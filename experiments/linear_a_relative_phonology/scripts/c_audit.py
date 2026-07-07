#!/usr/bin/env python3
"""C_AUDIT — the load-bearing brutal audit of the C3 substitution consonant-axis result.

Mirrors, one-for-one, the WP-A battery that REFUTED the Foundry position channel, now aimed at
the C3 finding: "substitution neighbours share a CONSONANT (differ in vowel) — the vocalic-
alternation axis" (C3 same_consonant sign-pair AUC 0.633 / word-minimal-pair AUC 0.704,
morphophono 0.744, degree-preserving lift up to 2.5x, one-sided p ~0.003-0.006).

Battery (same bar position FAILED):
 (1) INDEPENDENT REPLICATION  >=3 genuinely distinct implementations of "substitution
     neighbours share a consonant": (A) slot-fill substitution-weight graph (raw frame count,
     the C3 method); (B) distributional neighbour-embedding cosine; (C) frequency-normalized
     slot co-fill Jaccard (set overlap of substitution environments); plus (D) PPMI slot
     association. Do they AGREE that the axis is same_consonant (> same_vowel, > 0.5)?
 (2) GROUPED CV  frequency-band-disjoint split (the test that killed position: within a freq
     band position-only -> 0.481 = chance) + leave-one-site-out + leave-one-series-out (rebuild
     the substitution graph on the complement corpus, re-test the enrichment).
 (3) MULTIPLICITY  over the relation-type family tried (same_C, same_V, spelling, morphophono
     word-final, same_C word-internal): Holm + BH-FDR + best-of-relation selection.
 (4) ADAPTIVE NULLS, ORIENTED (two-sided): degree-preserving Maslov-Sneppen AND a
     frequency-matched label null AND a best-of-relation selection null.
 (5) FREQUENCY ARTIFACT  explicit: does freq[a]*freq[b] alone recover it? does within-band
     survive? does residualizing ew on log frequency kill it?

NON-CIRCULAR: generation + all scorers use sign IDENTITY only; LB (C,V) values GRADE only.
Deterministic seed 20260708, stdlib + repo loader.
"""
from __future__ import annotations

import json
import math
import os
import random
import re
import sys
import bisect
from collections import Counter, defaultdict
from itertools import combinations

MAIN = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
DAMOS_ITEMS = os.path.join(MAIN, "corpus", "bronze", "linearb", "damos", "items.jsonl")

SEED = 20260708
N_NULL = 300
N_PERM = 300
VOW = set("AEIOU")
TOPK = (20, 40, 80, 160, 320)


# ------------------------------------------------------------------ value parse (GRADE ONLY)
def parse_cv(v):
    if v.startswith("*"):
        return None
    if v in VOW:
        return ("", v)
    if len(v) >= 2 and v[-1] in VOW and v[:-1].isalpha():
        return (v[:-1], v[-1])
    if len(v) >= 2 and v[-1].isdigit():
        core = v[:-1]
        if core in VOW:
            return ("", core)
        if len(core) >= 2 and core[-1] in VOW and core[:-1].isalpha():
            return (core[:-1], core[-1])
    return None


def core_value(v):
    if v.startswith("*"):
        return v
    return re.sub(r"\d+$", "", v)


def relation(a, b):
    pa, pb = parse_cv(a), parse_cv(b)
    if pa is None or pb is None:
        return None
    if core_value(a) == core_value(b):
        return "spelling_variant"
    ca, va = pa
    cb, vb = pb
    if va == vb:
        return "same_vowel"
    if ca and cb and ca == cb:
        return "same_consonant"
    return "cross"


# ------------------------------------------------------------------ LB load with metadata
def load_lb():
    """Per-tablet ordered wordform streams + doc-level site/series meta."""
    occ = []
    type_occ = defaultdict(list)
    doc_words = defaultdict(list)      # doc -> list of wordform tuples (for LOSO rebuilds)
    doc_meta = {}
    with open(DAMOS_ITEMS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            it = rec.get("item", {}) or {}
            did = rec.get("_id")
            content = it.get("content", "") or ""
            site = it.get("ishort")
            series = it.get("seriessicura") or it.get("series")
            doc_meta[did] = {"site": site, "series": series}
            words = [tuple(w) for w in X._damos_wordforms(content)]
            doc_words[did] = words
            for i, w in enumerate(words):
                prev = words[i - 1] if i > 0 else None
                nxt = words[i + 1] if i + 1 < len(words) else None
                occ.append({"type": w, "doc": did, "pos": i, "prev": prev, "next": nxt})
                type_occ[w].append(len(occ) - 1)
    return occ, type_occ, doc_words, doc_meta


# ------------------------------------------------------------------ frames / graph (IMPL-A + co-fill sets)
def build_frames(types):
    slots = defaultdict(set)
    long_slots = defaultdict(set)
    for t in types:
        L = len(t)
        if L < 2:
            continue
        for p in range(L):
            ctx = t[:p] + ("\x00",) + t[p + 1:]
            slots[(L, p, ctx)].add(t[p])
            if L >= 3:
                long_slots[(L, p, ctx)].add(t[p])
    return slots, long_slots


def edge_weights(slots):
    """IMPL-A: edge{a,b} -> number of DISTINCT frames licensing the a/b substitution."""
    ew = Counter()
    for fills in slots.values():
        if len(fills) < 2:
            continue
        for a, b in combinations(sorted(fills), 2):
            ew[frozenset((a, b))] += 1
    return ew


def cofill_sets(slots):
    """sign -> set of multi-filler slot-keys it participates in (for Jaccard/PPMI)."""
    fset = defaultdict(set)
    for key, fills in slots.items():
        if len(fills) < 2:
            continue
        for s in fills:
            fset[s].add(key)
    return fset


def sign_neighbour_vectors(type_occ):
    vec = defaultdict(Counter)
    for t, idxs in type_occ.items():
        n = len(idxs)
        for k in range(len(t)):
            s = t[k]
            if k > 0:
                vec[s][t[k - 1]] += n
            if k + 1 < len(t):
                vec[s][t[k + 1]] += n
    norm = {s: math.sqrt(sum(v * v for v in c.values())) for s, c in vec.items()}
    return vec, norm


def cosine(vec, norm, a, b):
    if a not in vec or b not in vec or norm.get(a, 0) == 0 or norm.get(b, 0) == 0:
        return 0.0
    ca, cb = vec[a], vec[b]
    small, big = (ca, cb) if len(ca) <= len(cb) else (cb, ca)
    dot = sum(v * big.get(k, 0) for k, v in small.items())
    return dot / (norm[a] * norm[b])


# ------------------------------------------------------------------ AUC
def auc(pos_scores, neg_scores):
    if not pos_scores or not neg_scores:
        return None
    neg_sorted = sorted(neg_scores)
    m = len(neg_scores)
    tot = 0.0
    for s in pos_scores:
        lo = bisect.bisect_left(neg_sorted, s)
        hi = bisect.bisect_right(neg_sorted, s)
        tot += lo + 0.5 * (hi - lo)
    return tot / (len(pos_scores) * m)


# ------------------------------------------------------------------ Maslov-Sneppen rewire
def rewire(edge_list, rng, mult=8):
    edges = [list(e) for e in edge_list]
    eset = set(frozenset(e) for e in edges)
    E = len(edges)
    if E < 2:
        return eset
    target = mult * E
    swaps = attempts = 0
    while swaps < target and attempts < target * 12:
        attempts += 1
        i = rng.randrange(E); j = rng.randrange(E)
        if i == j:
            continue
        a, b = edges[i]; c, d = edges[j]
        if rng.random() < 0.5:
            c, d = d, c
        if len({a, b, c, d}) < 4:
            continue
        if frozenset((a, d)) in eset or frozenset((c, b)) in eset:
            continue
        eset.discard(frozenset((a, b))); eset.discard(frozenset((c, d)))
        edges[i] = [a, d]; edges[j] = [c, b]
        eset.add(frozenset((a, d))); eset.add(frozenset((c, b)))
        swaps += 1
    return eset


def rel_rate(edge_set, rel_of, target):
    hit = tot = 0
    for e in edge_set:
        r = rel_of.get(e)
        if r is None:
            continue
        tot += 1
        if target == "any_phon":
            hit += (r in ("same_vowel", "same_consonant", "spelling_variant"))
        else:
            hit += (r == target)
    return (hit / tot if tot else 0.0), tot


# ------------------------------------------------------------------ multiplicity helpers
def holm(pvals):
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals)
    running = 0.0
    m = len(pvals)
    for rank, i in enumerate(idx):
        val = (m - rank) * pvals[i]
        running = max(running, val)
        adj[i] = min(1.0, running)
    return adj


def bh_fdr(pvals):
    m = len(pvals)
    idx = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = idx[rank]
        val = pvals[i] * m / (rank + 1)
        prev = min(prev, val)
        adj[i] = min(1.0, prev)
    return adj


# ------------------------------------------------------------------ word minimal pairs
def word_minimal_pairs(types):
    by_key = defaultdict(list)
    for t in types:
        L = len(t)
        if L < 2:
            continue
        for p in range(L):
            ctx = t[:p] + ("\x00",) + t[p + 1:]
            by_key[(L, p, ctx)].append((t, t[p]))
    seen = set()
    out = []
    for (L, p, ctx), members in by_key.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                t1, f1 = members[i]; t2, f2 = members[j]
                if f1 == f2:
                    continue
                key = frozenset((t1, t2))
                if key in seen:
                    continue
                seen.add(key)
                out.append((t1, t2, p, f1, f2))
    return out


# =================================================================== run
def run():
    os.makedirs(DATA, exist_ok=True)
    rng = random.Random(SEED)
    occ, type_occ, doc_words, doc_meta = load_lb()
    types = list(type_occ)
    type_freq = {t: len(type_occ[t]) for t in types}
    sign_freq = Counter()
    for t in types:
        for s in set(t):
            sign_freq[s] += type_freq[t]

    slots, long_slots = build_frames(types)
    ew = edge_weights(slots)
    ew_long = edge_weights(long_slots)
    fset = cofill_sets(slots)
    vec, norm = sign_neighbour_vectors(type_occ)

    scorable = sorted(s for s in sign_freq if parse_cv(s) is not None)
    rel_of = {}
    for a, b in combinations(scorable, 2):
        r = relation(a, b)
        if r is not None:
            rel_of[frozenset((a, b))] = r
    counts_rel = Counter(rel_of.values())

    # ---- scorers over sign pairs (independent implementations) ----
    def s_weight(a, b):        # IMPL-A raw frame count
        return ew.get(frozenset((a, b)), 0)

    def s_cosine(a, b):        # IMPL-B distributional neighbour embedding
        return cosine(vec, norm, a, b)

    def s_jaccard(a, b):       # IMPL-C freq-normalized co-fill Jaccard
        A, B = fset.get(a, set()), fset.get(b, set())
        u = len(A | B)
        return len(A & B) / u if u else 0.0

    N_SLOTS = sum(1 for f in slots.values() if len(f) >= 2)
    def s_ppmi(a, b):          # IMPL-D PPMI over the sign x slot co-fill bipartite graph
        A, B = fset.get(a, set()), fset.get(b, set())
        co = len(A & B)
        if co == 0 or not A or not B:
            return 0.0
        # PMI(a,b) = log( P(co) / (P(a)P(b)) ) over slots
        p_co = co / N_SLOTS
        p_a = len(A) / N_SLOTS
        p_b = len(B) / N_SLOTS
        return max(0.0, math.log(p_co / (p_a * p_b)))

    def s_freq(a, b):          # frequency baseline (the confound)
        return sign_freq[a] * sign_freq[b]

    impls = {"A_substgraph_weight": s_weight, "B_neighbour_cosine": s_cosine,
             "C_cofill_jaccard": s_jaccard, "D_cofill_ppmi": s_ppmi,
             "FREQ_baseline": s_freq}

    # ================================================================ LEG 1: independent replication
    def pairs_pos_neg(target):
        pos, neg = [], []
        for e, r in rel_of.items():
            a, b = tuple(e)
            (pos if r == target else (neg if r == "cross" else None))
        return None
    # build once: lists of (a,b,rel)
    graded_pairs = [(tuple(e)[0], tuple(e)[1], r) for e, r in rel_of.items()]

    def auc_target(scorer, target, restrict=None):
        pos, neg = [], []
        for a, b, r in graded_pairs:
            if restrict is not None and not restrict(a, b):
                continue
            if r == target:
                pos.append(scorer(a, b))
            elif r == "cross":
                neg.append(scorer(a, b))
        a_ = auc(pos, neg)
        return (round(a_, 4) if a_ is not None else None, len(pos), len(neg))

    leg1 = {"targets": ["same_consonant", "same_vowel", "spelling_variant"], "by_impl": {}}
    for name, sc in impls.items():
        row = {}
        for tgt in ["same_consonant", "same_vowel", "spelling_variant"]:
            a_, npos, nneg = auc_target(sc, tgt)
            row[tgt] = {"auc": a_, "n_pos": npos, "n_neg": nneg}
        row["axis_is_consonant"] = (
            row["same_consonant"]["auc"] is not None and row["same_vowel"]["auc"] is not None
            and row["same_consonant"]["auc"] > row["same_vowel"]["auc"]
            and row["same_consonant"]["auc"] > 0.55)
        leg1["by_impl"][name] = row
    # agreement among the 4 genuine method implementations (exclude FREQ baseline)
    method_impls = ["A_substgraph_weight", "B_neighbour_cosine", "C_cofill_jaccard", "D_cofill_ppmi"]
    leg1["n_method_impls_axis_consonant"] = sum(leg1["by_impl"][m]["axis_is_consonant"] for m in method_impls)
    leg1["independent_replication_pass"] = leg1["n_method_impls_axis_consonant"] >= 2

    # ================================================================ LEG 5a: frequency artifact — within-band
    # quartile bands of scorable signs by log-frequency
    lf = {s: math.log(sign_freq[s]) for s in scorable}
    order = sorted(scorable, key=lambda s: lf[s])
    q = len(order) // 4
    band_of = {}
    bands = [order[:q], order[q:2 * q], order[2 * q:3 * q], order[3 * q:]]
    for bi, bnd in enumerate(bands):
        for s in bnd:
            band_of[s] = bi

    def within_band_auc(scorer, target):
        pooled_pos, pooled_neg = [], []
        per = []
        for bi in range(4):
            pos, neg = [], []
            for a, b, r in graded_pairs:
                if band_of.get(a) != bi or band_of.get(b) != bi:
                    continue
                if r == target:
                    pos.append(scorer(a, b))
                elif r == "cross":
                    neg.append(scorer(a, b))
            a_ = auc(pos, neg)
            per.append({"band": bi, "auc": round(a_, 4) if a_ is not None else None,
                        "n_pos": len(pos), "n_neg": len(neg),
                        "logfreq_range": [round(lf[bands[bi][0]], 2), round(lf[bands[bi][-1]], 2)]})
            pooled_pos += pos; pooled_neg += neg
        pa = auc(pooled_pos, pooled_neg)
        return {"pooled_within_band_auc": round(pa, 4) if pa is not None else None,
                "n_pos": len(pooled_pos), "n_neg": len(pooled_neg), "per_band": per}

    leg5 = {
        "freq_baseline_same_consonant_auc": leg1["by_impl"]["FREQ_baseline"]["same_consonant"]["auc"],
        "method_A_same_consonant_auc": leg1["by_impl"]["A_substgraph_weight"]["same_consonant"]["auc"],
        "within_band": {
            "A_substgraph_weight": within_band_auc(s_weight, "same_consonant"),
            "C_cofill_jaccard": within_band_auc(s_jaccard, "same_consonant"),
            "FREQ_baseline": within_band_auc(s_freq, "same_consonant"),
        },
    }
    # residualize ew on log(freq_a*freq_b): rank-regress out frequency, re-AUC
    fa_pairs = [(a, b, r, math.log(sign_freq[a] * sign_freq[b]), ew.get(frozenset((a, b)), 0))
                for a, b, r in graded_pairs]
    xs = [p[3] for p in fa_pairs]; ys = [p[4] for p in fa_pairs]
    mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    beta = sxy / sxx if sxx else 0.0
    resid = {}
    for a, b, r, x, y in fa_pairs:
        resid[(a, b)] = y - (my + beta * (x - mx))
    rpos = [resid[(a, b)] for a, b, r in graded_pairs if r == "same_consonant"]
    rneg = [resid[(a, b)] for a, b, r in graded_pairs if r == "cross"]
    ra = auc(rpos, rneg)
    leg5["ew_residualized_on_logfreq_same_consonant_auc"] = round(ra, 4) if ra is not None else None
    leg5["freq_beta"] = round(beta, 4)

    # ================================================================ LEG 2: grouped CV
    # (a) frequency-band-disjoint handled in leg5 within_band (train/test signs disjoint freq ranges);
    #     the DIRECT mirror of position's killer: pooled within-band AUC.
    # (b) leave-one-site-out / leave-one-series-out: rebuild ew on complement corpus, re-test.
    def rebuild_ew(exclude_key, meta_field):
        keep = [w for did, ws in doc_words.items()
                if doc_meta[did].get(meta_field) != exclude_key for w in ws]
        keep_types = set(keep)
        s2, _ = build_frames(keep_types)
        return edge_weights(s2)

    def loso(meta_field, min_docs=30):
        # groups with enough docs
        gcount = Counter(doc_meta[d].get(meta_field) for d in doc_words)
        groups = [g for g, c in gcount.items() if g is not None and c >= min_docs]
        res = []
        for g in sorted(groups, key=lambda x: -gcount[x]):
            ew_c = rebuild_ew(g, meta_field)
            sc = lambda a, b, _ew=ew_c: _ew.get(frozenset((a, b)), 0)
            asc, np_, nn_ = auc_target(sc, "same_consonant")
            asv, _, _ = auc_target(sc, "same_vowel")
            res.append({"held_out": g, "n_docs": gcount[g],
                        "same_consonant_auc": asc, "same_vowel_auc": asv,
                        "axis_consonant": (asc is not None and asv is not None and asc > asv and asc > 0.55)})
        aucs = [r["same_consonant_auc"] for r in res if r["same_consonant_auc"] is not None]
        return {"folds": res,
                "min_same_consonant_auc": round(min(aucs), 4) if aucs else None,
                "median_same_consonant_auc": round(sorted(aucs)[len(aucs) // 2], 4) if aucs else None,
                "all_folds_axis_consonant": all(r["axis_consonant"] for r in res) if res else False}

    leg2 = {
        "frequency_band_disjoint": {
            "pooled_within_band_same_consonant_auc":
                leg5["within_band"]["A_substgraph_weight"]["pooled_within_band_auc"],
            "note": "the exact test that collapsed position (position-only within-band 0.481=chance)",
            "detail_ref": "leg5.within_band",
        },
        "leave_one_site_out": loso("site"),
        "leave_one_series_out": loso("series"),
    }

    # ================================================================ LEG 3 + LEG 4: relation family, nulls
    # word-minimal-pair grading (Analysis-B mirror) for the relation family
    wmp = word_minimal_pairs(types)
    graded_wmp = []
    for (t1, t2, p, sa, sb) in wmp:
        r = relation(sa, sb)
        if r is None:
            continue
        final = (p == len(t1) - 1)
        graded_wmp.append({"t1": t1, "t2": t2, "sa": sa, "sb": sb, "rel": r, "final": final})

    def wclass(name):
        if name == "morphophono_final_sameC":
            return [g for g in graded_wmp if g["rel"] == "same_consonant" and g["final"]]
        if name == "same_consonant_word_internal":
            return [g for g in graded_wmp if g["rel"] == "same_consonant" and not g["final"]]
        return [g for g in graded_wmp if g["rel"] == name]

    RELFAM = ["same_consonant", "same_vowel", "spelling_variant",
              "morphophono_final_sameC", "same_consonant_word_internal"]
    cross_wmp = [g for g in graded_wmp if g["rel"] == "cross"]
    neg_scores = [ew.get(frozenset((g["sa"], g["sb"])), 0) for g in cross_wmp]

    # observed AUC per relation (method ew, class vs cross minimal pairs) + label-permutation p (two-sided)
    def perm_p_two_sided(pos_scores, obs_auc, pool_scores, npos, rng):
        # permute: draw npos scores from the pooled (class + cross) universe, recompute AUC vs cross-sized neg
        nulls = []
        for _ in range(N_PERM):
            samp = [pool_scores[rng.randrange(len(pool_scores))] for _ in range(npos)]
            a_ = auc(samp, neg_scores)
            if a_ is not None:
                nulls.append(a_)
        mu = sum(nulls) / len(nulls)
        # two-sided: fraction as-or-more extreme than obs on either side
        dev = abs(obs_auc - mu)
        cnt = sum(1 for a in nulls if abs(a - mu) >= dev)
        return (cnt + 1) / (len(nulls) + 1), round(mu, 4)

    leg3 = {"relation_family": {}, "note": "method=ew; positives=class minimal pairs, negatives=cross minimal pairs"}
    fam_pool = [ew.get(frozenset((g["sa"], g["sb"])), 0) for g in graded_wmp]  # all graded minimal-pair weights
    fam_pvals = []
    fam_aucs = []
    for name in RELFAM:
        members = wclass(name)
        pos = [ew.get(frozenset((g["sa"], g["sb"])), 0) for g in members]
        a_ = auc(pos, neg_scores)
        p2, mu = (None, None)
        if a_ is not None and members:
            p2, mu = perm_p_two_sided(pos, a_, fam_pool, len(pos),
                                      random.Random(SEED + hash(name) % 1000))
        leg3["relation_family"][name] = {"auc": round(a_, 4) if a_ is not None else None,
                                         "n_pos": len(pos), "perm_null_mean": mu,
                                         "perm_p_two_sided": round(p2, 4) if p2 is not None else None}
        fam_aucs.append(a_ if a_ is not None else 0.0)
        fam_pvals.append(p2 if p2 is not None else 1.0)
    holm_p = holm(fam_pvals)
    bh_p = bh_fdr(fam_pvals)
    for name, hp, bq in zip(RELFAM, holm_p, bh_p):
        leg3["relation_family"][name]["holm_adj_p"] = round(hp, 4)
        leg3["relation_family"][name]["bh_fdr_q"] = round(bq, 4)
    leg3["same_consonant_survives_holm_05"] = leg3["relation_family"]["same_consonant"]["holm_adj_p"] < 0.05
    leg3["morphophono_survives_holm_05"] = leg3["relation_family"]["morphophono_final_sameC"]["holm_adj_p"] < 0.05

    # best-of-relation selection null: max AUC over family vs null max
    obs_max = max(fam_aucs)
    rngb = random.Random(SEED + 4242)
    null_max = []
    for _ in range(N_PERM):
        ms = []
        for name in RELFAM:
            n = len(wclass(name))
            samp = [fam_pool[rngb.randrange(len(fam_pool))] for _ in range(n)] if n else []
            a_ = auc(samp, neg_scores)
            ms.append(a_ if a_ is not None else 0.0)
        null_max.append(max(ms))
    p_bestrel = (sum(1 for a in null_max if a >= obs_max) + 1) / (len(null_max) + 1)
    leg4 = {"best_of_relation_selection_null": {"obs_max_auc": round(obs_max, 4),
                                                "null_max_mean": round(sum(null_max) / len(null_max), 4),
                                                "p_one_sided": round(p_bestrel, 4)}}

    # degree-preserving Maslov-Sneppen null, TWO-SIDED, at top-k (same_consonant + any_phon)
    graded_edges = [tuple(e) for e in rel_of if frozenset(tuple(e)) in ew]
    ranked = sorted(graded_edges, key=lambda e: -ew[frozenset(e)])
    dp_sweep = []
    for k in TOPK:
        if k > len(ranked):
            continue
        top = set(frozenset(e) for e in ranked[:k])
        el = [tuple(e) for e in top]
        null_sets = [rewire(el, rng) for _ in range(N_NULL)]
        row = {"top_k_edges": k}
        for tgt in ["same_consonant", "same_vowel", "any_phon"]:
            obs, tot = rel_rate(top, rel_of, tgt)
            nulls = [rel_rate(ns, rel_of, tgt)[0] for ns in null_sets]
            mu = sum(nulls) / len(nulls)
            sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
            dev = abs(obs - mu)
            p_two = (sum(1 for x in nulls if abs(x - mu) >= dev) + 1) / (len(nulls) + 1)
            p_one = (sum(1 for x in nulls if x >= obs) + 1) / (len(nulls) + 1)
            row[tgt] = {"obs_rate": round(obs, 4), "null_mean": round(mu, 4),
                        "lift": round(obs / mu, 3) if mu else None,
                        "z": round((obs - mu) / sd, 2) if sd > 0 else None,
                        "p_one_sided": round(p_one, 4), "p_two_sided": round(p_two, 4),
                        "n_scored": tot}
        dp_sweep.append(row)
    leg4["degree_preserving_null_two_sided"] = dp_sweep

    # frequency-matched label null: permute same_consonant/cross labels within freq-product strata,
    # recompute the ew same_consonant-vs-cross sign-pair AUC. Kills freq confound.
    sc_pairs = [(a, b) for a, b, r in graded_pairs if r == "same_consonant"]
    cr_pairs = [(a, b) for a, b, r in graded_pairs if r == "cross"]
    def fp_stratum(a, b):
        return min(8, int(math.log2(sign_freq[a] * sign_freq[b])))
    obs_pos = [ew.get(frozenset(p), 0) for p in sc_pairs]
    obs_neg = [ew.get(frozenset(p), 0) for p in cr_pairs]
    obs_scv = auc(obs_pos, obs_neg)
    # pool by stratum
    strata = defaultdict(list)
    for a, b in sc_pairs + cr_pairs:
        strata[fp_stratum(a, b)].append((a, b))
    n_sc_by_stratum = Counter(fp_stratum(a, b) for a, b in sc_pairs)
    rngf = random.Random(SEED + 99)
    fm_nulls = []
    for _ in range(N_PERM):
        fake_pos = []
        fake_neg = []
        for st, members in strata.items():
            k = n_sc_by_stratum.get(st, 0)
            shuffled = members[:]
            rngf.shuffle(shuffled)
            for i, (a, b) in enumerate(shuffled):
                (fake_pos if i < k else fake_neg).append(ew.get(frozenset((a, b)), 0))
        a_ = auc(fake_pos, fake_neg)
        if a_ is not None:
            fm_nulls.append(a_)
    mu_fm = sum(fm_nulls) / len(fm_nulls)
    dev = abs(obs_scv - mu_fm)
    p_fm_two = (sum(1 for a in fm_nulls if abs(a - mu_fm) >= dev) + 1) / (len(fm_nulls) + 1)
    p_fm_one = (sum(1 for a in fm_nulls if a >= obs_scv) + 1) / (len(fm_nulls) + 1)
    leg4["frequency_matched_label_null"] = {
        "obs_same_consonant_vs_cross_auc": round(obs_scv, 4),
        "null_mean": round(mu_fm, 4), "p_one_sided": round(p_fm_one, 4),
        "p_two_sided": round(p_fm_two, 4),
        "note": "labels permuted within freq(a)*freq(b) strata; if signal is frequency it vanishes"}

    # ================================================================ VERDICT (mechanical)
    # decision components (mirrors the bar position FAILED)
    dp20 = dp_sweep[0]["same_consonant"] if dp_sweep else {}
    c_indep = leg1["independent_replication_pass"]
    band_auc = leg2["frequency_band_disjoint"]["pooled_within_band_same_consonant_auc"]
    c_band = (band_auc is not None and band_auc >= 0.55)   # position collapsed to 0.481; require materially > chance
    c_multiplicity = leg3["same_consonant_survives_holm_05"] or leg3["morphophono_survives_holm_05"]
    c_dp_two = (dp20.get("p_two_sided") is not None and dp20["p_two_sided"] < 0.05)
    c_fm = (p_fm_two < 0.05)
    c_bestrel = (p_bestrel < 0.05)
    c_nulls = c_dp_two and c_fm and c_bestrel
    c_loso = (leg2["leave_one_site_out"]["all_folds_axis_consonant"]
              and leg2["leave_one_series_out"]["all_folds_axis_consonant"])

    passed_all = c_indep and c_band and c_multiplicity and c_nulls and c_loso
    # EXPLORATORY if the core enrichment is real (nulls + multiplicity) but a robustness leg is weak
    core_ok = c_multiplicity and c_dp_two and c_bestrel
    if passed_all:
        verdict = "SUBSTITUTION_CONSONANT_AXIS_VALIDATED"
    elif (not c_band) or (not c_indep and leg1["n_method_impls_axis_consonant"] == 0) or (not core_ok):
        verdict = "SUBSTITUTION_CONSONANT_AXIS_REFUTED"
    else:
        verdict = "SUBSTITUTION_CONSONANT_AXIS_EXPLORATORY_ONLY"

    decision = {
        "components": {
            "independent_replication_ge2 (c_indep)": c_indep,
            "n_method_impls_axis_consonant": leg1["n_method_impls_axis_consonant"],
            "frequency_band_disjoint_survives (c_band)": c_band,
            "pooled_within_band_auc": band_auc,
            "multiplicity_holm_survives (c_multiplicity)": c_multiplicity,
            "degree_preserving_two_sided_p<.05 (c_dp_two)": c_dp_two,
            "frequency_matched_null_two_sided_p<.05 (c_fm)": c_fm,
            "best_of_relation_null_p<.05 (c_bestrel)": c_bestrel,
            "oriented_adaptive_nulls_all (c_nulls)": c_nulls,
            "loso_all_folds_axis_consonant (c_loso)": c_loso,
        },
        "decision_rule": ("VALIDATED requires ALL of: >=2 independent implementations agree AND the "
                          "frequency-band-disjoint split survives (>=0.55, position collapsed to 0.481) AND "
                          "multiplicity (Holm) survives AND oriented adaptive nulls (degree-preserving two-sided, "
                          "frequency-matched, best-of-relation) all p<.05 AND leave-one-site/series-out all folds "
                          "keep the consonant axis. Miss the freq-band OR the core nulls/multiplicity -> REFUTED; "
                          "core intact but a robustness leg weak -> EXPLORATORY_ONLY."),
    }

    out = {
        "experiment": "C_AUDIT_substitution_consonant_axis",
        "seed": SEED, "n_null": N_NULL, "n_perm": N_PERM,
        "non_circular": "generation + all scorers use sign IDENTITY only; LB (C,V) values GRADE only.",
        "corpus": {"wordform_tokens": sum(type_freq.values()), "wordform_types": len(types),
                   "scorable_signs": len(scorable), "sign_pairs_graded": len(rel_of),
                   "relation_counts": dict(counts_rel),
                   "n_word_minimal_pairs_graded": len(graded_wmp)},
        "leg1_independent_replication": leg1,
        "leg2_grouped_cv": leg2,
        "leg3_multiplicity_relation_family": leg3,
        "leg4_adaptive_nulls_oriented": leg4,
        "leg5_frequency_artifact": leg5,
        "decision": decision,
        "verdict": verdict,
    }
    outpath = os.path.join(DATA, "C_audit.json")
    json.dump(out, open(outpath, "w"), indent=1, ensure_ascii=False)
    print(json.dumps({"verdict": verdict, "decision": decision,
                      "leg1_axis": {m: leg1["by_impl"][m]["same_consonant"]["auc"] for m in method_impls},
                      "leg1_same_vowel": {m: leg1["by_impl"][m]["same_vowel"]["auc"] for m in method_impls},
                      "freq_baseline_same_consonant": leg5["freq_baseline_same_consonant_auc"],
                      "within_band_pooled": {k: v["pooled_within_band_auc"] for k, v in leg5["within_band"].items()},
                      "ew_resid_same_consonant": leg5["ew_residualized_on_logfreq_same_consonant_auc"],
                      "dp_top20_same_consonant": dp20,
                      "freq_matched_null": leg4["frequency_matched_label_null"],
                      "best_of_relation": leg4["best_of_relation_selection_null"],
                      "relation_family": {k: {"auc": v["auc"], "holm": v["holm_adj_p"]}
                                          for k, v in leg3["relation_family"].items()},
                      "loso_site_min": leg2["leave_one_site_out"]["min_same_consonant_auc"],
                      "loso_series_min": leg2["leave_one_series_out"]["min_same_consonant_auc"]},
                     indent=1))
    print("\nWROTE", outpath, os.path.getsize(outpath), "bytes")
    return out


if __name__ == "__main__":
    run()
