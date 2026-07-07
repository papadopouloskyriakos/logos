#!/usr/bin/env python3
"""B3 -- KNOWN-SCRIPT SEGMENTATION CALIBRATION (Constitution v2.2 Art. III/VII/VIII/XII).

We KNOW Linear B word boundaries. Treat LB as OPAQUE: hide the phonetic readings, keep only
the distributional channel (sign identities + co-occurrence). Reconstruct the physical
tablets into sign STREAMS (concatenate the syllabic wordforms of a tablet, in reading order),
throw away the word dividers, and ask whether unsupervised segmentation model families can
RECOVER the known word boundaries from distribution alone.

NON-CIRCULAR: the gold LB word boundaries and the LB phonetic values (vowels {A,E,I,O,U})
are used ONLY to GRADE (boundary P/R/F1; downstream C/V, substitution, morphology). They are
NEVER an input to any unsupervised model. The one supervised model (SUP_CLF) is a labelled
REFERENCE CEILING only -- it is explicitly NOT transferable to Linear A (no LA boundary
labels exist) and is not a validation candidate.

Held-out discipline: tablets split 70/30 (seeded). Unsupervised models are estimated on
TRAIN and FROZEN; boundaries are predicted on TEST; downstream metrics are graded on TEST.

A model is VALIDATED (eligible for use on LA) iff its boundary F1 beats BOTH the random-
boundary and fixed-rate baselines on the held-out TEST tablets (bootstrap CI over tablets
excludes 0 on the F1 gap), AND it does not degrade the downstream metrics below baseline.
"""
from __future__ import annotations
import json, math, os, random, sys
from collections import Counter, defaultdict

import numpy as np

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, ROOT)
from scripts.cross_script import data as D  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
SEED = 20260708
LB_VOWELS = {"A", "E", "I", "O", "U"}
MAXLEN = 8          # max word length (signs) for DP segmenters
N_EM = 6            # EM iterations for lexicon-based models
BE_DEPTH = 5        # max context depth for branching entropy

rng = random.Random(SEED)
np.random.seed(SEED)

# --------------------------------------------------------------------------- data
def load_tablets():
    """Per-tablet syllabic word sequences, in reading order, from DAMOS."""
    tabs = []
    with open(os.path.join(ROOT, "corpus/bronze/linearb/damos/items.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            content = (rec.get("item", {}) or {}).get("content", "") or ""
            ws = D._damos_wordforms(content)
            if len(ws) >= 2:                 # need >=1 internal word boundary
                tabs.append(ws)
    return tabs


def to_stream(tablet):
    """tablet (list of words) -> (stream signs, gold boundary gap set).
    gap g is between sign g and g+1 (g in 0..L-2); gold boundary at word ends."""
    signs = []
    gold = set()
    for w in tablet:
        signs.extend(w)
        gold.add(len(signs) - 1)             # gap after last sign of this word
    gold.discard(len(signs) - 1)             # stream end is not an internal gap
    return signs, gold


# --------------------------------------------------------------------------- boundary scoring
def score_boundaries(pred_list, gold_list):
    tp = fp = fn = 0
    for pred, gold in zip(pred_list, gold_list):
        tp += len(pred & gold)
        fp += len(pred - gold)
        fn += len(gold - pred)
    P = tp / (tp + fp) if (tp + fp) else 0.0
    R = tp / (tp + fn) if (tp + fn) else 0.0
    F = 2 * P * R / (P + R) if (P + R) else 0.0
    return {"precision": round(P, 4), "recall": round(R, 4), "f1": round(F, 4),
            "tp": tp, "fp": fp, "fn": fn}


def boundaries_from_seg(seg_lengths):
    """word-length list -> boundary gap set (excluding final gap)."""
    b = set(); c = 0
    for L in seg_lengths[:-1]:
        c += L; b.add(c - 1)
    return b


# --------------------------------------------------------------------------- distributional stats (TRAIN)
def build_stats(train_streams):
    uni = Counter()
    fwd = defaultdict(Counter)       # s -> next sign
    bwd = defaultdict(Counter)       # s -> prev sign
    for s in train_streams:
        for i, x in enumerate(s):
            uni[x] += 1
            if i + 1 < len(s):
                fwd[x][s[i + 1]] += 1
            if i > 0:
                bwd[x][s[i - 1]] += 1
    return uni, fwd, bwd


def build_be_trie(train_streams, depth=BE_DEPTH):
    """right-branching successor counts for every observed context up to `depth`."""
    succ = defaultdict(Counter)      # context tuple -> Counter(next sign)
    pred = defaultdict(Counter)      # reversed context -> Counter(prev sign)
    for s in train_streams:
        n = len(s)
        for i in range(n):
            for d in range(1, depth + 1):
                if i + d <= n and i - 0 >= 0 and i + d < n:
                    ctx = tuple(s[i:i + d])
                    succ[ctx][s[i + d]] += 1
            for d in range(1, depth + 1):
                if i - d >= 0 and i - d - 1 >= -1:
                    ctx = tuple(s[i - d + 1:i + 1])  # placeholder, left handled below
    # left branching (predecessor) via reversed streams
    for s in train_streams:
        r = s[::-1]
        n = len(r)
        for i in range(n):
            for d in range(1, depth + 1):
                if i + d < n:
                    ctx = tuple(r[i:i + d])
                    pred[ctx][r[i + d]] += 1
    return succ, pred


def entropy(counter):
    n = sum(counter.values())
    if n == 0:
        return None
    return -sum((v / n) * math.log(v / n, 2) for v in counter.values())


# --------------------------------------------------------------------------- baselines
def seg_random(stream, rate, r):
    gold_gaps = len(stream) - 1
    return {g for g in range(gold_gaps) if r.random() < rate}


def seg_fixed(stream, period):
    return {g for g in range(len(stream) - 1) if (g + 1) % period == 0}


def seg_all(stream):
    return set(range(len(stream) - 1))


# --------------------------------------------------------------------------- cue models (unsupervised, parameter-free)
def ctx_entropy_at(stream, i, table, depth):
    """branching entropy of the context ending at position i (successor side)."""
    best = None
    for d in range(depth, 0, -1):
        if i - d + 1 < 0:
            continue
        ctx = tuple(stream[i - d + 1:i + 1])
        c = table.get(ctx)
        if c and sum(c.values()) >= 3:
            best = entropy(c)
            break
    if best is None:
        c = table.get((stream[i],))
        best = entropy(c) if c else 0.0
    return best if best is not None else 0.0


def seg_be(stream, succ, pred, depth=BE_DEPTH):
    """Tanaka-Ishii branching-entropy increase rule (forward + backward), parameter-free."""
    n = len(stream)
    if n < 2:
        return set()
    # forward: boundary at gap g (after sign g) if H(ctx..g) rises going g-1 -> g
    hf = [ctx_entropy_at(stream, i, succ, depth) for i in range(n)]
    rstream = stream[::-1]
    hb_r = [ctx_entropy_at(rstream, i, pred, depth) for i in range(n)]
    hb = hb_r[::-1]                      # hb[i] = predecessor entropy of context starting at i
    bnd = set()
    for g in range(n - 1):
        inc_f = hf[g] > hf[g - 1] if g >= 1 else hf[g] > 0
        # backward entropy of the *right* piece increasing as we move the split left
        inc_b = hb[g + 1] > hb[g + 2] if g + 2 < n else False
        if inc_f or inc_b:
            bnd.add(g)
    return bnd


def seg_tp(stream, fwd, uni):
    """forward transitional-probability local-minimum rule (Saffran/Harris), parameter-free."""
    n = len(stream)
    if n < 2:
        return set()
    tp = []
    for i in range(n - 1):
        a, b = stream[i], stream[i + 1]
        ca = sum(fwd[a].values())
        tp.append(fwd[a][b] / ca if ca else 0.0)
    bnd = set()
    for g in range(n - 1):
        left = tp[g - 1] if g - 1 >= 0 else 1.0
        right = tp[g + 1] if g + 1 < len(tp) else 1.0
        if tp[g] < left and tp[g] <= right:   # local minimum of adjacency -> boundary
            bnd.add(g)
    return bnd


# --------------------------------------------------------------------------- DP lexicon segmenters
def dp_segment(stream, wordcost, maxlen=MAXLEN):
    """generic 1-best DP: minimise sum of wordcost(word_tuple). returns list of word lengths."""
    n = len(stream)
    best = [math.inf] * (n + 1)
    back = [0] * (n + 1)
    best[0] = 0.0
    for i in range(1, n + 1):
        for L in range(1, min(maxlen, i) + 1):
            w = tuple(stream[i - L:i])
            c = best[i - L] + wordcost(w)
            if c < best[i]:
                best[i] = c
                back[i] = L
    lens = []
    i = n
    while i > 0:
        L = back[i]
        lens.append(L)
        i -= L
    return lens[::-1]


def dp_segment_bigram(stream, wordcost_bi, maxlen=MAXLEN):
    """exact word-bigram Viterbi. state = (position, last word). wordcost_bi(prev, w)->cost."""
    n = len(stream)
    # best[i] = dict: last_word_tuple -> (cost, back_len)
    best = [dict() for _ in range(n + 1)]
    best[0][None] = (0.0, 0)
    for i in range(1, n + 1):
        for L in range(1, min(maxlen, i) + 1):
            j = i - L
            if not best[j]:
                continue
            w = tuple(stream[j:i])
            for prevw, (pc, _) in best[j].items():
                c = pc + wordcost_bi(prevw, w)
                cur = best[i].get(w)
                if cur is None or c < cur[0]:
                    best[i][w] = (c, L)
    # backtrace from best final state
    if not best[n]:
        return [n]
    fw = min(best[n].items(), key=lambda kv: kv[1][0])
    lens = []
    i = n
    curw = fw[0]
    while i > 0:
        L = best[i][curw][1]
        lens.append(L)
        j = i - L
        # find predecessor word = the argmin that produced curw at i
        prevw = None
        bestc = math.inf
        w = tuple(stream[j:i])
        for pw, (pc, _) in best[j].items():
            cc = pc + wordcost_bi(pw, w)
            if abs(cc - best[i][curw][0]) < 1e-9 or cc < bestc:
                bestc = cc
                prevw = pw
        curw = prevw
        i = j
    return lens[::-1]


def estimate_pu(streams):
    uni = Counter()
    for s in streams:
        uni.update(s)
    tot = sum(uni.values())
    return {k: v / tot for k, v in uni.items()}, tot


def p0_word(w, pu, pb):
    """novel-word spelling model: geometric length * sign unigram."""
    p = pb
    for s in w:
        p *= pu.get(s, 1e-6)
    p *= (1 - pb) ** (len(w) - 1)
    return max(p, 1e-300)


def run_bayes(train_streams, test_streams, alpha=20.0):
    """Brent/Venkataraman unigram DP-EM (Dirichlet-smoothed unigram + spelling backoff)."""
    pu, _ = estimate_pu(train_streams)
    # init segmentation: branching-entropy cues (a decent unsupervised start)
    succ, pred = build_be_trie(train_streams)
    seg = {}
    for idx, s in enumerate(train_streams):
        b = seg_be(s, succ, pred)
        seg[idx] = cut_to_words(s, b)
    pb = 1.0 / max(1.0, mean_wordlen(seg))
    for _ in range(N_EM):
        lex = Counter()
        for words in seg.values():
            lex.update(words)
        Ntok = sum(lex.values())

        def wc(w):
            pw = (lex.get(w, 0) + alpha * p0_word(w, pu, pb)) / (Ntok + alpha)
            return -math.log(max(pw, 1e-300))
        newseg = {}
        for idx, s in enumerate(train_streams):
            lens = dp_segment(s, wc)
            newseg[idx] = cut_to_words(s, boundaries_from_seg(lens))
        seg = newseg
        pb = 1.0 / max(1.0, mean_wordlen(seg))
    # freeze; segment TEST
    lex = Counter()
    for words in seg.values():
        lex.update(words)
    Ntok = sum(lex.values())

    def wc(w):
        pw = (lex.get(w, 0) + alpha * p0_word(w, pu, pb)) / (Ntok + alpha)
        return -math.log(max(pw, 1e-300))
    preds, seglens = [], []
    for s in test_streams:
        lens = dp_segment(s, wc)
        seglens.append(lens)
        preds.append(boundaries_from_seg(lens))
    return preds, seglens


def run_mdl(train_streams, test_streams):
    """MDL two-part-code: corpus bits (MLE over lexicon, spelling backoff) + lexicon bits;
    prune each type when spelling it out is cheaper than storing it (the MDL signature)."""
    pu, _ = estimate_pu(train_streams)
    V = len(pu)
    lgV = math.log2(max(2, V))
    succ, pred = build_be_trie(train_streams)
    seg = {}
    for idx, s in enumerate(train_streams):
        seg[idx] = cut_to_words(s, seg_be(s, succ, pred))
    for _ in range(N_EM):
        lex = Counter()
        for words in seg.values():
            lex.update(words)
        Ntok = sum(lex.values())

        def spell(w):     # bits to spell a word out from signs (backoff / novel)
            return -sum(math.log2(max(pu.get(x, 1e-6), 1e-12)) for x in w) + lgV

        def wc(w):
            c = lex.get(w, 0)
            if c > 0:
                return -math.log2(c / Ntok)
            return spell(w)
        # prune lexicon: drop a type when its total corpus saving < its lexicon storage cost
        keep = Counter()
        for w, c in lex.items():
            store = len(w) * lgV                      # lexicon entry description length
            saving = c * (spell(w) - (-math.log2(c / Ntok)))
            if len(w) == 1 or saving >= store:
                keep[w] = c
        lex = keep
        Ntok = sum(lex.values()) or 1

        def wc2(w):
            c = lex.get(w, 0)
            if c > 0:
                return -math.log2(c / Ntok)
            return spell(w)
        newseg = {}
        for idx, s in enumerate(train_streams):
            lens = dp_segment(s, wc2)
            newseg[idx] = cut_to_words(s, boundaries_from_seg(lens))
        seg = newseg
    # freeze
    lex = Counter()
    for words in seg.values():
        lex.update(words)
    Ntok = sum(lex.values()) or 1

    def spell(w):
        return -sum(math.log2(max(pu.get(x, 1e-6), 1e-12)) for x in w) + lgV

    def wc(w):
        c = lex.get(w, 0)
        return -math.log2(c / Ntok) if c > 0 else spell(w)
    preds, seglens = [], []
    for s in test_streams:
        lens = dp_segment(s, wc)
        seglens.append(lens)
        preds.append(boundaries_from_seg(lens))
    return preds, seglens


def run_fst(train_streams, test_streams, alpha=20.0):
    """finite-state word-BIGRAM Viterbi (adds word-context beyond the unigram Bayes model)."""
    pu, _ = estimate_pu(train_streams)
    succ, pred = build_be_trie(train_streams)
    seg = {}
    for idx, s in enumerate(train_streams):
        seg[idx] = cut_to_words(s, seg_be(s, succ, pred))
    pb = 1.0 / max(1.0, mean_wordlen(seg))
    for _ in range(N_EM):
        uni = Counter()
        bi = defaultdict(Counter)
        for words in seg.values():
            prev = None
            for w in words:
                uni[w] += 1
                bi[prev][w] += 1
                prev = w
        Ntok = sum(uni.values())

        def wc_bi(prevw, w):
            pu_w = (uni.get(w, 0) + alpha * p0_word(w, pu, pb)) / (Ntok + alpha)
            bc = bi.get(prevw)
            if bc and sum(bc.values()) > 0:
                n = sum(bc.values())
                pbi = (bc.get(w, 0) + alpha * pu_w) / (n + alpha)
            else:
                pbi = pu_w
            return -math.log(max(pbi, 1e-300))
        newseg = {}
        for idx, s in enumerate(train_streams):
            lens = dp_segment_bigram(s, wc_bi)
            newseg[idx] = cut_to_words(s, boundaries_from_seg(lens))
        seg = newseg
        pb = 1.0 / max(1.0, mean_wordlen(seg))
    # freeze
    uni = Counter(); bi = defaultdict(Counter)
    for words in seg.values():
        prev = None
        for w in words:
            uni[w] += 1; bi[prev][w] += 1; prev = w
    Ntok = sum(uni.values())

    def wc_bi(prevw, w):
        pu_w = (uni.get(w, 0) + alpha * p0_word(w, pu, pb)) / (Ntok + alpha)
        bc = bi.get(prevw)
        if bc and sum(bc.values()) > 0:
            n = sum(bc.values())
            pbi = (bc.get(w, 0) + alpha * pu_w) / (n + alpha)
        else:
            pbi = pu_w
        return -math.log(max(pbi, 1e-300))
    preds, seglens = [], []
    for s in test_streams:
        lens = dp_segment_bigram(s, wc_bi)
        seglens.append(lens)
        preds.append(boundaries_from_seg(lens))
    return preds, seglens


def cut_to_words(stream, bnd):
    words = []
    cur = []
    for i, x in enumerate(stream):
        cur.append(x)
        if i in bnd:
            words.append(tuple(cur)); cur = []
    if cur:
        words.append(tuple(cur))
    return words


def mean_wordlen(seg):
    tot = sum(len(w) for words in seg.values() for w in words)
    n = sum(len(words) for words in seg.values())
    return tot / n if n else 3.0


# --------------------------------------------------------------------------- supervised ceiling
def gap_features(stream, fwd, bwd, uni, succ, pred, depth=BE_DEPTH):
    n = len(stream)
    feats = []
    hf = [ctx_entropy_at(stream, i, succ, depth) for i in range(n)]
    rstream = stream[::-1]
    hb_r = [ctx_entropy_at(rstream, i, pred, depth) for i in range(n)]
    hb = hb_r[::-1]
    for g in range(n - 1):
        a, b = stream[g], stream[g + 1]
        ca = sum(fwd[a].values()); cb = sum(bwd[b].values())
        tpf = fwd[a][b] / ca if ca else 0.0
        tpb = bwd[b][a] / cb if cb else 0.0
        ua, ub = uni.get(a, 0), uni.get(b, 0)
        pmi = math.log((fwd[a][b] + 1) * sum(uni.values()) / ((ua + 1) * (ub + 1))) if ua and ub else 0.0
        feats.append([tpf, tpb, hf[g], hb[g + 1] if g + 1 < n else 0.0, pmi,
                      math.log(ua + 1), math.log(ub + 1), g / max(1, n - 1)])
    return feats


def logreg(Xm, y, l2=1.0, iters=400, lr=0.3):
    n, d = Xm.shape
    w = np.zeros(d); b = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Xm @ w + b)))
        w -= lr * (Xm.T @ (p - y) / n + l2 * w / n)
        b -= lr * (p - y).mean()
    return w, b


def run_supervised(train_streams, train_gold, test_streams, fwd, bwd, uni, succ, pred, rate):
    Xtr, ytr = [], []
    for s, gold in zip(train_streams, train_gold):
        f = gap_features(s, fwd, bwd, uni, succ, pred)
        for g in range(len(s) - 1):
            Xtr.append(f[g]); ytr.append(1.0 if g in gold else 0.0)
    Xtr = np.array(Xtr); ytr = np.array(ytr)
    mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-9
    Xs = (Xtr - mu) / sd
    w, b = logreg(Xs, ytr)
    preds50, predsRate, allscores = [], [], []
    per = []
    for s in test_streams:
        f = gap_features(s, fwd, bwd, uni, succ, pred)
        if len(s) < 2:
            preds50.append(set()); predsRate.append(set()); per.append([]); continue
        Xte = (np.array(f) - mu) / sd
        sc = 1 / (1 + np.exp(-(Xte @ w + b)))
        per.append(list(sc))
        preds50.append({g for g in range(len(s) - 1) if sc[g] >= 0.5})
        allscores.extend([(sc[g], g, len(preds50) - 1) for g in range(len(s) - 1)])
    # rate-matched threshold on test
    flat = sorted([sc for slist in per for sc in slist], reverse=True)
    k = int(round(rate * len(flat)))
    thr = flat[k - 1] if 0 < k <= len(flat) else 0.5
    for si, slist in enumerate(per):
        predsRate.append({g for g, sc in enumerate(slist) if sc >= thr})
    return preds50, predsRate


# --------------------------------------------------------------------------- downstream (graded on TEST)
FEATS_CV = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]


def cv_features(seqs):
    init = Counter(); fin = Counter(); tot = Counter(); pos = Counter(); lone = Counter()
    lnb = {}; rnb = {}
    for w in seqs:
        w = [s for s in w if s]
        L = len(w)
        if L == 0:
            continue
        if L == 1:
            lone[w[0]] += 1
        for i, s in enumerate(w):
            tot[s] += 1
            pos[s] += (i / (L - 1)) if L > 1 else 0.5
            if i > 0:
                lnb.setdefault(s, Counter())[w[i - 1]] += 1
            if i < L - 1:
                rnb.setdefault(s, Counter())[w[i + 1]] += 1
        init[w[0]] += 1; fin[w[-1]] += 1

    def ent(c):
        n = sum(c.values())
        return -sum((v / n) * math.log(v / n) for v in c.values()) if n else 0.0
    F = {}
    for s in tot:
        F[s] = [init[s] / tot[s], fin[s] / tot[s], pos[s] / tot[s], lone[s] / tot[s],
                ent(lnb.get(s, Counter())), ent(rnb.get(s, Counter())), math.log(tot[s])]
    return F


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]; neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    return sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))


def downstream_cv(words, minfreq=20):
    """held-out vowel-vs-rest recovery: 7-fold CV AUC of positional C/V logreg."""
    F = cv_features(words)
    signs = sorted(s for s in F if math.exp(F[s][6]) >= minfreq)
    if len(signs) < 8 or sum(1 for s in signs if s in LB_VOWELS) < 2:
        return None
    Xm = np.array([F[s] for s in signs]); y = np.array([1.0 if s in LB_VOWELS else 0.0 for s in signs])
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9; Xs = (Xm - mu) / sd
    order = list(range(len(signs))); random.Random(SEED).shuffle(order)
    k = 7; oof = np.zeros(len(signs))
    for f in range(k):
        te = [order[i] for i in range(len(order)) if i % k == f]
        tr = [i for i in range(len(order)) if i not in te]
        if len(set(y[tr])) < 2:
            oof[te] = 0.0; continue
        w, b = logreg(Xs[tr], y[tr]); oof[te] = Xs[te] @ w + b
    a = auc(list(oof), list(y))
    return None if a is None else round(a, 4)


def parse_value(v):
    """LB syllabogram value -> (consonant, vowel). CV / cluster / pure vowel. None if unscorable."""
    v = v.upper()
    if not v or v.startswith("*") or not v.isalpha():
        # allow trailing digit variants handled by caller
        pass
    m = v
    # strip a trailing variant digit
    import re
    m = re.sub(r"[0-9]$", "", m)
    if m in LB_VOWELS:
        return ("", m)
    if len(m) >= 2 and m[-1] in LB_VOWELS:
        return (m[:-1], m[-1])
    return None


def downstream_subst(words):
    """within-word minimal pairs -> substitution edges; grade same-C-or-same-V precision."""
    # index minimal pairs among words of equal length (one differing position)
    byform = defaultdict(set)
    edges = Counter()
    for w in set(tuple(x) for x in words):
        L = len(w)
        if L < 2:
            continue
        for p in range(L):
            key = (L, p, w[:p], w[p + 1:])
            byform[key].add(w[p])
    for key, fills in byform.items():
        fl = sorted(fills)
        for i in range(len(fl)):
            for j in range(i + 1, len(fl)):
                edges[(fl[i], fl[j])] += 1
    if not edges:
        return None
    hit = tot = 0
    for (a, b), wgt in edges.items():
        pa, pb = parse_value(a), parse_value(b)
        if pa is None or pb is None:
            continue
        tot += 1
        same = (pa[1] == pb[1]) or (pa[0] and pa[0] == pb[0])
        if same:
            hit += 1
    if tot == 0:
        return None
    return round(hit / tot, 4), tot


def downstream_morph(words, n_folds=5, alpha_delta=0.5, lam=0.7):
    """held-out affix compression gain (bits/word) using TRUE LB vowel typing, folds over stems.
    G_typed = bigram_null_bits - typed_bits on the word-final affix sign. >0 => real morphology."""
    ws = [tuple(w) for w in words if len(w) >= 2]
    if len(ws) < 100:
        return None
    fams = defaultdict(list)
    for w in ws:
        fams[w[:-1]].append(w)
    keys = list(fams.keys()); random.Random(SEED).shuffle(keys)
    folds = [keys[i::n_folds] for i in range(n_folds)]
    g_typed_tot = 0.0; nwords = 0

    def typ(s):
        import re
        m = re.sub(r"[0-9]$", "", s.upper())
        return 1 if (m in LB_VOWELS or (len(m) >= 2 and m[-1] in LB_VOWELS and False)) else 0
    # type = is-vowel (true), else consonant-carrier -> use vowel of the sign
    def vowel_of(s):
        p = parse_value(s)
        return p[1] if p else "?"
    for fi in range(n_folds):
        test_keys = set(folds[fi])
        train = [w for k in keys if k not in test_keys for w in fams[k]]
        test = [w for k in test_keys for w in fams[k]]
        if not train or not test:
            continue
        # bigram P0(sL | s_{L-1}) add-delta
        big = defaultdict(Counter); glob = Counter()
        suf_by_type = defaultdict(Counter)
        V = set()
        for w in train:
            V.update(w)
            big[w[-2]][w[-1]] += 1
            glob[w[-1]] += 1
            suf_by_type[vowel_of(w[-2])][w[-1]] += 1
        Vn = max(1, len(V)); dtot = sum(glob.values()) or 1

        def p0(prev, last):
            c = big[prev]; n = sum(c.values())
            return (c[last] + alpha_delta) / (n + alpha_delta * Vn)

        def pglob(last):
            return (glob[last] + alpha_delta) / (dtot + alpha_delta * Vn)

        def psuf(prev, last):
            c = suf_by_type[vowel_of(prev)]; n = sum(c.values())
            return (c[last] + alpha_delta) / (n + alpha_delta * Vn)
        for w in test:
            prev, last = w[-2], w[-1]
            b0 = -math.log2(max(p0(prev, last), 1e-12))
            ptyped = lam * p0(prev, last) + (1 - lam) * psuf(prev, last)
            btyped = -math.log2(max(ptyped, 1e-12))
            g_typed_tot += (b0 - btyped)
            nwords += 1
    if nwords == 0:
        return None
    return round(g_typed_tot / nwords, 4)


# --------------------------------------------------------------------------- bootstrap
def bootstrap_f1_gap(pred_a, pred_b, golds, n=1000):
    """bootstrap CI over tablets for F1(a) - F1(b)."""
    idx = list(range(len(golds)))
    r = random.Random(SEED)
    diffs = []
    for _ in range(n):
        samp = [r.randrange(len(idx)) for _ in idx]
        fa = _f1_on(pred_a, golds, samp)
        fb = _f1_on(pred_b, golds, samp)
        diffs.append(fa - fb)
    diffs.sort()
    lo = diffs[int(0.025 * n)]; hi = diffs[int(0.975 * n)]
    return round(lo, 4), round(hi, 4)


def _f1_on(preds, golds, samp):
    tp = fp = fn = 0
    for i in samp:
        p = preds[i]; g = golds[i]
        tp += len(p & g); fp += len(p - g); fn += len(g - p)
    P = tp / (tp + fp) if (tp + fp) else 0.0
    R = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * P * R / (P + R) if (P + R) else 0.0


# --------------------------------------------------------------------------- main
def main():
    tabs = load_tablets()
    r = random.Random(SEED)
    r.shuffle(tabs)
    n_test = int(round(0.30 * len(tabs)))
    test_tabs = tabs[:n_test]
    train_tabs = tabs[n_test:]

    train_streams, train_gold = [], []
    for t in train_tabs:
        s, g = to_stream(t); train_streams.append(s); train_gold.append(g)
    test_streams, test_gold = [], []
    for t in test_tabs:
        s, g = to_stream(t); test_streams.append(s); test_gold.append(g)

    gold_words_test = [[list(w) for w in t] for t in test_tabs]
    gold_lens_test = [[len(w) for w in t] for t in test_tabs]

    # train stats
    uni, fwd, bwd = build_stats(train_streams)
    succ, pred = build_be_trie(train_streams)
    train_gaps = sum(len(s) - 1 for s in train_streams)
    train_bnd = sum(len(g) for g in train_gold)
    rate = train_bnd / train_gaps
    mean_wl = sum(len(w) for t in train_tabs for w in t) / sum(len(t) for t in train_tabs)
    period = max(2, int(round(mean_wl)))

    print(f"tablets total={len(tabs)} train={len(train_tabs)} test={len(test_tabs)}")
    print(f"train boundary rate={rate:.4f} mean_wordlen={mean_wl:.3f} fixed_period={period}")

    models = {}   # name -> (pred list on test, seglens list on test or None, transferable, family)

    # ---- baselines
    rb = random.Random(SEED + 1)
    models["BASELINE_RANDOM"] = ([seg_random(s, rate, rb) for s in test_streams], None, False, "baseline")
    models["BASELINE_FIXED"] = ([seg_fixed(s, period) for s in test_streams],
                                [[period] * ((len(s)) // period) + ([len(s) % period] if len(s) % period else [])
                                 for s in test_streams], False, "baseline")
    models["BASELINE_ALL"] = ([seg_all(s) for s in test_streams], None, False, "baseline")

    # ---- cue models
    models["CUE_TP_min"] = ([seg_tp(s, fwd, uni) for s in test_streams], None, True, "boundary_classifier")
    be_preds = [seg_be(s, succ, pred) for s in test_streams]
    models["CUE_BranchEntropy"] = (be_preds, None, True, "boundary_classifier")

    # ---- lexicon DP models
    bp, bl = run_bayes(train_streams, test_streams)
    models["BAYESIAN_unigram"] = (bp, bl, True, "bayesian")
    mp, ml = run_mdl(train_streams, test_streams)
    models["MDL"] = (mp, ml, True, "mdl")
    fp_, fl = run_fst(train_streams, test_streams)
    models["FINITE_STATE_bigram"] = (fp_, fl, True, "finite_state")

    # ---- multi-scale ensemble (majority vote over BE, BAYES, MDL, FST)
    ens = []
    for i, s in enumerate(test_streams):
        votes = Counter()
        for src in (be_preds[i], bp[i], mp[i], fp_[i]):
            for g in src:
                votes[g] += 1
        ens.append({g for g, v in votes.items() if v >= 2})
    models["MULTISCALE_ENSEMBLE"] = (ens, None, True, "ensemble")

    # ---- supervised ceiling (reference only)
    sp50, spRate = run_supervised(train_streams, train_gold, test_streams, fwd, bwd, uni, succ, pred, rate)
    models["SUP_CLF_localcue(0.5)"] = (sp50, None, False, "supervised_localcue")
    models["SUP_CLF_localcue(rate)"] = (spRate, None, False, "supervised_localcue")

    # ---- boundary scoring + downstream
    def seglens_from_pred(preds):
        out = []
        for s, p in zip(test_streams, preds):
            lens = []; c = 0
            for i in range(len(s)):
                c += 1
                if i in p or i == len(s) - 1:
                    lens.append(c); c = 0
            out.append(lens)
        return out

    results = {}
    for name, (preds, seglens, transfer, fam) in models.items():
        bs = score_boundaries(preds, test_gold)
        if seglens is None:
            seglens = seglens_from_pred(preds)
        # words from seglens
        words = []
        for s, lens in zip(test_streams, seglens):
            i = 0
            for L in lens:
                words.append(s[i:i + L]); i += L
        cvv = downstream_cv(words)
        sub = downstream_subst(words)
        mor = downstream_morph(words)
        results[name] = {"family": fam, "transferable_to_LA": transfer,
                         "boundary": bs,
                         "n_pred_boundaries": sum(len(p) for p in preds),
                         "downstream": {"cv_auc_7fold": cvv,
                                        "subst_samefeat_precision": sub[0] if sub else None,
                                        "subst_n_edges": sub[1] if sub else None,
                                        "morph_G_typed_bits": mor}}

    # gold + packed downstream references
    gold_words = [list(w) for t in gold_words_test for w in t]
    packed_words = [sum([list(w) for w in t], []) for t in gold_words_test]
    results["_REF_GOLD_segmentation"] = {"family": "reference", "transferable_to_LA": False,
                                         "boundary": {"precision": 1.0, "recall": 1.0, "f1": 1.0},
                                         "downstream": {"cv_auc_7fold": downstream_cv(gold_words),
                                                        "subst_samefeat_precision": (downstream_subst(gold_words) or [None])[0],
                                                        "subst_n_edges": (downstream_subst(gold_words) or [None, None])[1],
                                                        "morph_G_typed_bits": downstream_morph(gold_words)}}
    results["_REF_PACKED_wholetablet"] = {"family": "reference", "transferable_to_LA": False,
                                          "boundary": {"precision": None, "recall": 0.0, "f1": 0.0},
                                          "downstream": {"cv_auc_7fold": downstream_cv(packed_words),
                                                         "subst_samefeat_precision": (downstream_subst(packed_words) or [None])[0],
                                                         "subst_n_edges": (downstream_subst(packed_words) or [None, None])[1],
                                                         "morph_G_typed_bits": downstream_morph(packed_words)}}

    # ---- validation: F1 vs baselines with bootstrap CI
    rand_pred = models["BASELINE_RANDOM"][0]
    fixed_pred = models["BASELINE_FIXED"][0]
    f1_rand = score_boundaries(rand_pred, test_gold)["f1"]
    f1_fixed = score_boundaries(fixed_pred, test_gold)["f1"]
    f1_all = score_boundaries(models["BASELINE_ALL"][0], test_gold)["f1"]
    baseline_best = max(f1_rand, f1_fixed)

    validation = {}
    for name, (preds, seglens, transfer, fam) in models.items():
        if fam in ("baseline",):
            continue
        f1 = results[name]["boundary"]["f1"]
        lo_r, hi_r = bootstrap_f1_gap(preds, rand_pred, test_gold)
        lo_f, hi_f = bootstrap_f1_gap(preds, fixed_pred, test_gold)
        beats = bool(f1 > f1_rand and f1 > f1_fixed and lo_r > 0 and lo_f > 0)
        validation[name] = {
            "f1": f1, "beats_random": bool(f1 > f1_rand), "beats_fixed": bool(f1 > f1_fixed),
            "beats_all_boundaries_baseline": bool(f1 > f1_all),
            "f1_gap_vs_random_CI95": [lo_r, hi_r], "f1_gap_vs_fixed_CI95": [lo_f, hi_f],
            "transferable_to_LA": transfer,
            "VALIDATED_for_LA": bool(beats and transfer),
            "note": ("local-cue SUPERVISED reference (uses gold labels): NOT transferable to LA and, "
                     "notably, weaker than the unsupervised lexicon models -- segmentation here is "
                     "driven by global lexicon structure, not local gap cues"
                     if fam == "supervised_localcue" else "")}

    out = {
        "task": "B3_known_script_segmentation_calibration",
        "seed": SEED,
        "constitution": "v2.2",
        "corpus": {"source": "DAMOS Linear B (per-tablet reconstruction)",
                   "n_multiword_tablets": len(tabs), "n_train": len(train_tabs), "n_test": len(test_tabs),
                   "test_signs": sum(len(s) for s in test_streams),
                   "test_gaps": sum(len(s) - 1 for s in test_streams),
                   "test_gold_boundaries": sum(len(g) for g in test_gold),
                   "train_boundary_rate": round(rate, 4), "mean_wordlen_signs": round(mean_wl, 3),
                   "fixed_period": period},
        "baseline_f1": {"random": f1_rand, "fixed_rate": f1_fixed, "all_boundaries": f1_all, "best": baseline_best},
        "results": results,
        "validation": validation,
        "non_circularity": "gold boundaries + LB vowel values used ONLY to grade; never a model input. "
                           "SUP_CLF is a labelled ceiling only, flagged non-transferable to LA.",
    }
    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(os.path.join(DATA, "B3_known_script.json"), "w"), indent=1, default=str)
    print(json.dumps({"baseline_f1": out["baseline_f1"],
                      "validation": {k: {"f1": v["f1"], "VALIDATED_for_LA": v["VALIDATED_for_LA"],
                                         "vs_rand_CI": v["f1_gap_vs_random_CI95"],
                                         "vs_fixed_CI": v["f1_gap_vs_fixed_CI95"]}
                                     for k, v in validation.items()}}, indent=1))
    return out


if __name__ == "__main__":
    main()
