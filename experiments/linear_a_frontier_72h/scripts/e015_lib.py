#!/usr/bin/env python3
"""EPOCH-015 shared machinery — segmentation-marginalized morphology (prereg d35828be).

Boundary-probability model: 3 parameter-free unsupervised cue features per gap
(forward/backward branching-entropy increase, forward TP local minimum; B3-validated
families re-implemented self-contained), calibrated P(boundary|cell) on gold gaps.
Affix induction: relphono-E1 recurrent-stem productivity + frequency-matched i.i.d. null.
Marginalization: K independent-Bernoulli boundary samples; statistic = mean over samples;
nulls PAIRED (each null replicate averages one fresh matched synthetic corpus per sample).
Pure stdlib. Seed discipline: every stochastic step takes an explicit seed.
"""
from __future__ import annotations
import json, math, os, random, sys
from collections import Counter, defaultdict

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
sys.path.insert(0, ROOT)
CAMP = os.path.join(ROOT, "experiments", "linear_a_frontier_72h")
DATA = os.path.join(CAMP, "data", "marginalized_morph")
SEED = 20260708
BE_DEPTH = 5
MIN_CTX = 3
MIN_ATT = 10
K_SAMPLES = 20
P_INV = 0.01          # inventory rule threshold
N_NULL_INV = 200      # inventory-rule null size
P_MARK = 0.9


# ----------------------------------------------------------------------- data
def load_lb_tablets():
    from scripts.cross_script import data as D
    tabs = []
    with open(os.path.join(ROOT, "corpus/bronze/linearb/damos/items.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            content = (rec.get("item", {}) or {}).get("content", "") or ""
            ws = D._damos_wordforms(content)
            if len(ws) >= 2:
                tabs.append([tuple(w) for w in ws])
    return tabs


def load_la_docs():
    recs = json.load(open(os.path.join(ROOT, "corpus/silver/inscriptions_structured.json"),
                          encoding="utf-8"))
    out = []
    for r in recs:
        if len(r["signs"]) < 2:
            continue
        signs = list(r["signs"])
        # GORILA word-boundary gaps + physical-mark flags
        st = r["stream"]
        wpos = [i for i, t in enumerate(st) if t["t"] == "word"]
        cum, cc = [], 0
        for i in wpos:
            cc += len(st[i]["signs"])
            cum.append(cc)
        gorila_gaps, marked_gaps = set(), set()
        for k in range(len(wpos) - 1):
            g = cum[k] - 1
            gorila_gaps.add(g)
            between = {st[j]["t"] for j in range(wpos[k] + 1, wpos[k + 1])}
            if between & {"div", "num", "nl", "other"}:
                marked_gaps.add(g)
        out.append({"id": r["id"], "site": r["site"], "signs": signs,
                    "words": [tuple(w) for w in r["words"]],
                    "gorila_gaps": gorila_gaps, "marked_gaps": marked_gaps})
    return out


def to_stream(words):
    """word list -> (signs, gold internal gap set). gap g sits between sign g and g+1."""
    signs, gold = [], set()
    for w in words:
        signs.extend(w)
        gold.add(len(signs) - 1)
    gold.discard(len(signs) - 1)
    return signs, gold


def words_from_gaps(signs, gaps):
    out, start = [], 0
    for g in sorted(gaps):
        out.append(tuple(signs[start:g + 1]))
        start = g + 1
    out.append(tuple(signs[start:]))
    return [w for w in out if w]


# ------------------------------------------------------- cue features (unsupervised)
class CueModel:
    """Forward/backward branching-entropy tries + forward transitional probabilities,
    estimated on a list of sign streams (no boundary information used)."""

    def __init__(self, streams, depth=BE_DEPTH):
        self.depth = depth
        succ = defaultdict(Counter)
        pred = defaultdict(Counter)
        fwd = defaultdict(Counter)
        for s in streams:
            n = len(s)
            for i in range(n - 1):
                fwd[s[i]][s[i + 1]] += 1
            for i in range(n):
                for d in range(1, depth + 1):
                    if i - d + 1 >= 0 and i + 1 < n:
                        succ[tuple(s[i - d + 1:i + 1])][s[i + 1]] += 1
            r = s[::-1]
            for i in range(n):
                for d in range(1, depth + 1):
                    if i - d + 1 >= 0 and i + 1 < n:
                        pred[tuple(r[i - d + 1:i + 1])][r[i + 1]] += 1
        self.succ, self.pred, self.fwd = succ, pred, fwd

    @staticmethod
    def _entropy(counter):
        n = sum(counter.values())
        if n == 0:
            return 0.0
        return -sum((v / n) * math.log(v / n, 2) for v in counter.values())

    def _ctx_h(self, stream, i, table):
        for d in range(self.depth, 0, -1):
            if i - d + 1 < 0:
                continue
            c = table.get(tuple(stream[i - d + 1:i + 1]))
            if c and sum(c.values()) >= MIN_CTX:
                return self._entropy(c)
        c = table.get((stream[i],))
        return self._entropy(c) if c else 0.0

    def features(self, stream):
        """per internal gap g in 0..n-2: (f1 fwd-BE-increase, f2 bwd-BE-increase, f3 TP local min)."""
        n = len(stream)
        if n < 2:
            return []
        hf = [self._ctx_h(stream, i, self.succ) for i in range(n)]
        r = stream[::-1]
        hb_r = [self._ctx_h(r, i, self.pred) for i in range(n)]
        hb = hb_r[::-1]
        tp = []
        for i in range(n - 1):
            ca = sum(self.fwd[stream[i]].values())
            tp.append(self.fwd[stream[i]][stream[i + 1]] / ca if ca else 0.0)
        feats = []
        for g in range(n - 1):
            f1 = int(hf[g] > hf[g - 1]) if g >= 1 else int(hf[g] > 0)
            f2 = int(hb[g + 1] > hb[g + 2]) if g + 2 < n else 0
            left = tp[g - 1] if g >= 1 else 1.0
            right = tp[g + 1] if g + 1 < len(tp) else 1.0
            f3 = int(tp[g] < left and tp[g] <= right)
            feats.append((f1, f2, f3))
        return feats


def calibrate(cue, streams_with_gold):
    """P(boundary | cell) with add-1 smoothing, from (stream, gold gap set) pairs."""
    nb, nt = Counter(), Counter()
    for signs, gold in streams_with_gold:
        for g, cell in enumerate(cue.features(signs)):
            nt[cell] += 1
            if g in gold:
                nb[cell] += 1
    return {cell: (nb[cell] + 1) / (nt[cell] + 2) for cell in
            [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]}, \
           {"".join(map(str, cell)): {"n": nt[cell], "n_boundary": nb[cell],
                                      "p": round((nb[cell] + 1) / (nt[cell] + 2), 4)}
            for cell in sorted(nt)}


def gap_probs(cue, calib, signs, marked_gaps=None, p_mark=P_MARK):
    ps = [calib[cell] for cell in cue.features(signs)]
    if marked_gaps:
        for g in marked_gaps:
            if 0 <= g < len(ps):
                ps[g] = max(ps[g], p_mark)
    return ps


# ------------------------------------------------------------ segmentation arms
def frozen_gaps(probs_per_doc, rule):
    """rule 'MAP' (p>0.5) or 'MEAN' (p>global mean over all gaps)."""
    if rule == "MAP":
        thr = [0.5] * len(probs_per_doc)
    else:
        allp = [p for ps in probs_per_doc for p in ps]
        m = sum(allp) / len(allp) if allp else 0.5
        thr = [m] * len(probs_per_doc)
    return [{g for g, p in enumerate(ps) if p > t} for ps, t in zip(probs_per_doc, thr)]


def sample_gaps(probs_per_doc, seed):
    rng = random.Random(seed)
    return [{g for g, p in enumerate(ps) if rng.random() < p} for ps in probs_per_doc]


def boundary_f1(pred_list, gold_list):
    tp = fp = fn = 0
    for pred, gold in zip(pred_list, gold_list):
        tp += len(pred & gold); fp += len(pred - gold); fn += len(gold - pred)
    P = tp / (tp + fp) if tp + fp else 0.0
    R = tp / (tp + fn) if tp + fn else 0.0
    F = 2 * P * R / (P + R) if P + R else 0.0
    return {"precision": round(P, 4), "recall": round(R, 4), "f1": round(F, 4)}


def cut_rate(gap_sets, streams):
    tot = sum(max(0, len(s) - 1) for s in streams)
    cut = sum(len(g) for g in gap_sets)
    return round(cut / tot, 4) if tot else 0.0


# ---------------------------------------------------- affix machinery (E1 paradigm)
def _residual_index(wset):
    rc = Counter()
    for w in wset:
        if len(w) >= 2:
            rc[w[1:]] += 1
            rc[w[:-1]] += 1
    return rc


def productivities(words, targets):
    """targets: list of (sign, 'PRE'|'SUF'). One pass. Returns {target: n_recurrent_stems}."""
    wset = set(w for w in words if len(w) >= 1)
    rc = _residual_index(wset)
    pre_t = {s for s, pos in targets if pos == "PRE"}
    suf_t = {s for s, pos in targets if pos == "SUF"}
    pre_stems = defaultdict(set); suf_stems = defaultdict(set)
    for w in wset:
        if len(w) < 2:
            continue
        if w[0] in pre_t:
            t = w[1:]
            if (t in wset) or rc[t] >= 2:
                pre_stems[w[0]].add(t)
        if w[-1] in suf_t:
            t = w[:-1]
            if (t in wset) or rc[t] >= 2:
                suf_stems[w[-1]].add(t)
    out = {}
    for s, pos in targets:
        out[(s, pos)] = len(pre_stems[s]) if pos == "PRE" else len(suf_stems[s])
    return out


def synth_corpus(words, rng):
    """frequency-matched i.i.d. null corpus: same word-length profile, same sign-unigram."""
    uni = Counter(s for w in words for s in w)
    signs = list(uni.keys()); wts = [uni[s] for s in signs]
    return [tuple(rng.choices(signs, weights=wts, k=len(w))) for w in words]


def null_pvals(words, targets, n_null, seed):
    """one-sided p per target: P(null productivity >= observed). Single word list."""
    obs = productivities(words, targets)
    rng = random.Random(seed)
    ge = {t: 0 for t in targets}
    null_sum = {t: 0.0 for t in targets}
    for _ in range(n_null):
        prod = productivities(synth_corpus(words, rng), targets)
        for t in targets:
            null_sum[t] += prod[t]
            if prod[t] >= obs[t]:
                ge[t] += 1
    return {t: {"obs": obs[t], "p": (1 + ge[t]) / (1 + n_null),
                "null_mean": round(null_sum[t] / n_null, 3)} for t in targets}


def marg_null_pvals(word_lists, targets, n_null, seed):
    """marginalized: obs = mean_k prod on sample k; null replicate j = mean_k prod on a fresh
    matched synthetic corpus per sample (paired). One-sided p."""
    K = len(word_lists)
    obs_k = [productivities(ws, targets) for ws in word_lists]
    obs = {t: sum(o[t] for o in obs_k) / K for t in targets}
    rng = random.Random(seed)
    ge = {t: 0 for t in targets}
    null_sum = {t: 0.0 for t in targets}
    for _ in range(n_null):
        acc = {t: 0.0 for t in targets}
        for ws in word_lists:
            prod = productivities(synth_corpus(ws, rng), targets)
            for t in targets:
                acc[t] += prod[t]
        for t in targets:
            m = acc[t] / K
            null_sum[t] += m
            if m >= obs[t]:
                ge[t] += 1
    return {t: {"obs": round(obs[t], 3), "p": (1 + ge[t]) / (1 + n_null),
                "null_mean": round(null_sum[t] / n_null, 3)} for t in targets}


def candidate_universe(ref_words, min_att=MIN_ATT):
    """(sign,POS) candidates with >= min_att attestations on the REFERENCE word list."""
    ini = Counter(w[0] for w in ref_words if len(w) >= 2)
    fin = Counter(w[-1] for w in ref_words if len(w) >= 2)
    U = [(s, "PRE") for s, c in sorted(ini.items()) if c >= min_att]
    U += [(s, "SUF") for s, c in sorted(fin.items()) if c >= min_att]
    return U


def inventory(words, U, seed, n_null=N_NULL_INV, p_thr=P_INV):
    pv = null_pvals(words, U, n_null, seed)
    return {t for t in U if pv[t]["p"] <= p_thr}, pv


def marg_inventory(word_lists, U, seed, n_null=N_NULL_INV, p_thr=P_INV):
    pv = marg_null_pvals(word_lists, U, n_null, seed)
    return {t for t in U if pv[t]["p"] <= p_thr}, pv


# ----------------------------------------------------------------- scoring
def set_f1(pred, gold, U):
    tp = len(pred & gold); fp = len(pred - gold); fn = len(gold - pred)
    P = tp / (tp + fp) if tp + fp else 0.0
    R = tp / (tp + fn) if tp + fn else 0.0
    F = 2 * P * R / (P + R) if P + R else 0.0
    return {"precision": round(P, 4), "recall": round(R, 4), "f1": round(F, 4),
            "tp": tp, "fp": fp, "fn": fn, "n_universe": len(U), "n_gold": len(gold)}


def mcnemar_exact(pred_a, pred_b, gold, U):
    """exact two-sided binomial on candidates where arms disagree in correctness vs gold."""
    b = c = 0
    for u in U:
        ok_a = (u in pred_a) == (u in gold)
        ok_b = (u in pred_b) == (u in gold)
        if ok_a and not ok_b:
            b += 1
        elif ok_b and not ok_a:
            c += 1
    n = b + c
    if n == 0:
        return {"n_discordant": 0, "a_only_correct": 0, "b_only_correct": 0, "p": 1.0}
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n * 2
    return {"n_discordant": n, "a_only_correct": b, "b_only_correct": c, "p": round(min(1.0, p), 6)}


def holm(pvals):
    """pvals: {key: p} -> {key: p_holm} (step-down)."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        adj = min(1.0, (m - i) * p)
        running = max(running, adj)
        out[k] = round(running, 6)
    return out


def tkey(t):
    return f"{t[0]}|{t[1]}"


# ------------------------------------------------- D2 stream-level marginalized null
def marg_null_pvals_stream(streams, gapsets_by_k, targets, n_null, seed):
    """D2 (deviation log): correlation-preserving marginalized null.

    streams: list of real sign streams (documents). gapsets_by_k: [K][n_docs] gap sets sampled
    from the boundary distribution on the REAL streams. obs = mean_k productivity(words(real, G_k)).
    Null replicate j: synthesize each document's stream ONCE (i.i.d. from the pooled real sign
    unigram, lengths preserved), apply the SAME K gap-sets, mean productivity over k.
    One-sided p = (1 + #{null >= obs}) / (1 + n_null).
    """
    K = len(gapsets_by_k)
    uni = Counter(s for st in streams for s in st)
    signs = list(uni.keys()); wts = [uni[s] for s in signs]
    lens = [len(st) for st in streams]

    def words_for(docs, gapsets):
        return [w for st, g in zip(docs, gapsets) for w in words_from_gaps(st, g)]

    obs_k = [productivities(words_for(streams, gapsets_by_k[k]), targets) for k in range(K)]
    obs = {t: sum(o[t] for o in obs_k) / K for t in targets}
    rng = random.Random(seed)
    ge = {t: 0 for t in targets}
    null_sum = {t: 0.0 for t in targets}
    for _ in range(n_null):
        synth_docs = [rng.choices(signs, weights=wts, k=n) for n in lens]
        acc = {t: 0.0 for t in targets}
        for k in range(K):
            prod = productivities(words_for(synth_docs, gapsets_by_k[k]), targets)
            for t in targets:
                acc[t] += prod[t]
        for t in targets:
            m = acc[t] / K
            null_sum[t] += m
            if m >= obs[t]:
                ge[t] += 1
    return {t: {"obs": round(obs[t], 3), "p": (1 + ge[t]) / (1 + n_null),
                "null_mean": round(null_sum[t] / n_null, 3)} for t in targets}


def marg_inventory_stream(streams, gapsets_by_k, U, seed, n_null=N_NULL_INV, p_thr=P_INV):
    pv = marg_null_pvals_stream(streams, gapsets_by_k, U, n_null, seed)
    return {t for t in U if pv[t]["p"] <= p_thr}, pv
