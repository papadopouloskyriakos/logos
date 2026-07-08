#!/usr/bin/env python3
"""TASK F1 — OPAQUE-LB CALIBRATION of the substitution-neighborhood channel.

Question: with LB values BLIND (graph built from sign identity only; values GRADE only),
do substitution neighborhoods recover the same_consonant / same_vowel / spelling_variant /
morphophonological (word-final same_consonant) equivalence classes under
  (a) FREQUENCY-DISJOINT holdout  (only within-frequency-band sign pairs — the split that
      collapsed the position channel to chance), and
  (b) FORMULA-DISJOINT holdout    (leave-one-SERIES-out: rebuild the neighborhood graph on the
      complement corpus, re-test the class enrichment)?

This re-earns, under stricter holdouts, the C_AUDIT consonant-axis precondition the cross-script
bridge (F2) relies on. Two independent neighborhood implementations (cofill-Jaccard, adjacency
cosine) must AGREE the axis is consonant. Permutation null = shuffle value labels among signs.

NON-CIRCULAR: neighborhoods use identity only; relation() reads values to GRADE.
Seed 20260708.
"""
from __future__ import annotations
import os, random, sys
from collections import Counter, defaultdict
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f_bridge_common as C

SEED = C.SEED
N_PERM = 300


def scorable_signs(seqs):
    sup = C.sign_support(seqs)
    return sorted(s for s in sup if C.parse_cv(s) is not None and sup[s] >= 2)


def pair_relations(signs):
    rel = {}
    for a, b in __import__("itertools").combinations(signs, 2):
        r = C.relation(a, b)
        if r:
            rel[frozenset((a, b))] = r
    return rel


def class_aucs(sim_lookup, signs, rel, restrict=None):
    """AUC of each class's pair-similarity vs the `cross` pool. restrict = set of allowed pairs."""
    pools = defaultdict(list)
    for e, r in rel.items():
        if restrict is not None and e not in restrict:
            continue
        a, b = tuple(e)
        pools[r].append(sim_lookup(a, b))
    neg = pools.get("cross", [])
    out = {}
    for cls in ("same_consonant", "same_vowel", "spelling_variant"):
        out[cls] = {"auc": C.auc(pools.get(cls, []), neg),
                    "n_pos": len(pools.get(cls, [])), "n_neg": len(neg)}
    return out


def make_sim_lookup(seqs, signs, kind):
    S = C.similarity_matrix(seqs, signs, kind=kind)
    idx = {s: i for i, s in enumerate(signs)}
    return lambda a, b: S[idx[a], idx[b]] if a in idx and b in idx else 0.0


def freq_bands(seqs, signs, nb=4):
    sup = C.sign_support(seqs)
    order = sorted(signs, key=lambda s: sup[s])
    band = {}
    for i, s in enumerate(order):
        band[s] = min(nb - 1, i * nb // len(order))
    return band


def within_band_pairs(signs, rel, band):
    return {e for e in rel if band[tuple(e)[0]] == band[tuple(e)[1]]}


def final_frame_sim(seqs, signs):
    """Morphophonological axis: cofill-Jaccard restricted to WORD-FINAL substitution frames."""
    slots = defaultdict(set)
    for t in set(seqs):
        L = len(t)
        if L < 2:
            continue
        p = L - 1
        ctx = t[:p] + ("\x00",)
        slots[(L, p, ctx)].add(t[p])
    fset = defaultdict(set)
    for key, fills in slots.items():
        if len(fills) < 2:
            continue
        for s in fills:
            fset[s].add(key)

    def look(a, b):
        fa, fb = fset.get(a, set()), fset.get(b, set())
        u = len(fa | fb)
        return len(fa & fb) / u if u else 0.0
    return look


def perm_null_consonant(sim_lookup, signs, rel, n=N_PERM, seed=SEED):
    """Shuffle value labels among signs, recompute same_consonant-vs-cross AUC."""
    rng = random.Random(seed)
    obs = class_aucs(sim_lookup, signs, rel)["same_consonant"]["auc"]
    vals = list(signs)
    null = []
    for _ in range(n):
        perm = vals[:]
        rng.shuffle(perm)
        relabel = dict(zip(signs, perm))
        rel2 = {}
        for e in rel:
            a, b = tuple(e)
            r = C.relation(relabel[a], relabel[b])
            if r:
                rel2[e] = r
        a = class_aucs(sim_lookup, signs, rel2)["same_consonant"]["auc"]
        if a is not None:
            null.append(a)
    null.sort()
    ge = sum(1 for x in null if x >= obs)
    p = (ge + 1) / (len(null) + 1)
    return {"obs_auc": obs, "null_mean": float(np.mean(null)),
            "null_p95": float(np.quantile(null, 0.95)), "p_one_sided": p, "n_null": len(null)}


def run():
    rng = random.Random(SEED)
    seqs, doc_words, doc_meta = C.load_lb_damos()
    signs = scorable_signs(seqs)
    rel = pair_relations(signs)
    counts = Counter(rel.values())
    print("LB scorable signs", len(signs), "graded pairs", dict(counts))

    out = {"experiment": "F1_opaque_lb_calibration", "seed": SEED,
           "corpus": {"lb_wordform_tokens": len(seqs), "scorable_signs": len(signs),
                      "relation_counts": dict(counts)},
           "non_circular": "neighborhoods use sign identity only; values GRADE only"}

    # ---- (0) full-corpus baseline, two independent implementations ----
    impls = {}
    for kind in ("jaccard", "cosine"):
        look = make_sim_lookup(seqs, signs, kind)
        a = class_aucs(look, signs, rel)
        a["axis_is_consonant"] = (a["same_consonant"]["auc"] or 0) > (a["same_vowel"]["auc"] or 0) \
            and (a["same_consonant"]["auc"] or 0) > 0.5
        impls[kind] = a
    # morphophono word-final axis
    finlook = final_frame_sim(seqs, signs)
    morph = class_aucs(finlook, signs, rel)
    impls["jaccard_wordfinal_morphophono"] = morph
    out["full_corpus"] = impls
    out["independent_replication_axis_consonant"] = sum(
        1 for k in ("jaccard", "cosine") if impls[k]["axis_is_consonant"])

    # ---- (a) FREQUENCY-DISJOINT ----
    band = freq_bands(seqs, signs, nb=4)
    wb = within_band_pairs(signs, rel, band)
    fd = {}
    for kind in ("jaccard", "cosine"):
        look = make_sim_lookup(seqs, signs, kind)
        fd[kind] = class_aucs(look, signs, rel, restrict=wb)
    out["frequency_disjoint"] = {"n_within_band_pairs": len(wb), "by_impl": fd}

    # ---- (b) FORMULA-DISJOINT (leave-one-series-out) ----
    series_docs = defaultdict(list)
    for did, m in doc_meta.items():
        series_docs[m.get("series") or "NA"].append(did)
    big = sorted(series_docs, key=lambda s: -sum(len(doc_words[d]) for d in series_docs[s]))
    folds = []
    for held in big[:6]:
        train = []
        for did, ws in doc_words.items():
            if doc_meta[did].get("series") != held:
                train.extend(ws)
        tsigns = [s for s in signs if s in set().union(*[set(w) for w in train]) if True]
        look = make_sim_lookup(train, signs, "jaccard")
        a = class_aucs(look, signs, rel)
        folds.append({"held_series": held, "n_train_words": len(train),
                      "same_consonant_auc": a["same_consonant"]["auc"],
                      "same_vowel_auc": a["same_vowel"]["auc"],
                      "axis_consonant": (a["same_consonant"]["auc"] or 0) > (a["same_vowel"]["auc"] or 0)})
    scA = [f["same_consonant_auc"] for f in folds if f["same_consonant_auc"] is not None]
    out["formula_disjoint_loso"] = {
        "folds": folds,
        "min_same_consonant_auc": min(scA) if scA else None,
        "median_same_consonant_auc": float(np.median(scA)) if scA else None,
        "all_folds_axis_consonant": all(f["axis_consonant"] for f in folds)}

    # ---- permutation null (label shuffle) on the primary Jaccard impl ----
    look = make_sim_lookup(seqs, signs, "jaccard")
    out["perm_null_label_shuffle"] = perm_null_consonant(look, signs, rel)

    # ---- verdict ----
    fj = out["frequency_disjoint"]["by_impl"]["jaccard"]
    out["decision"] = {
        "independent_replication_ge2": out["independent_replication_axis_consonant"] >= 2,
        "freq_disjoint_consonant_auc": fj["same_consonant"]["auc"],
        "freq_disjoint_axis_consonant": (fj["same_consonant"]["auc"] or 0) > (fj["same_vowel"]["auc"] or 0),
        "loso_all_axis_consonant": out["formula_disjoint_loso"]["all_folds_axis_consonant"],
        "perm_p": out["perm_null_label_shuffle"]["p_one_sided"],
        "morphophono_final_consonant_auc": morph["same_consonant"]["auc"],
    }
    cond = (out["decision"]["independent_replication_ge2"]
            and out["decision"]["freq_disjoint_axis_consonant"]
            and out["decision"]["loso_all_axis_consonant"]
            and out["decision"]["perm_p"] < 0.05)
    out["verdict"] = "OPAQUE_LB_CONSONANT_AXIS_RECOVERED_UNDER_HOLDOUTS" if cond \
        else "CALIBRATION_WEAK_OR_FAILED"
    p = C.dump("F1_opaque_lb_calibration.json", out)
    print("wrote", p, "| verdict", out["verdict"])
    print("full jaccard same_C AUC", impls["jaccard"]["same_consonant"]["auc"])
    print("freq-disjoint jaccard same_C AUC", fj["same_consonant"]["auc"])
    print("LOSO min same_C AUC", out["formula_disjoint_loso"]["min_same_consonant_auc"])
    print("perm p", out["perm_null_label_shuffle"]["p_one_sided"])
    return out


if __name__ == "__main__":
    run()
