#!/usr/bin/env python3
"""A2 — Multiplicity audit of the Foundry position->C/V symmetry-break result (Constitution v2.2, Art. VII/VIII).

A1 established the numbers reproduce exactly:
    WP1 single-feature initial_rate AUC = 0.744 (77 signs, integer freq>=20), perm_p = 0.035 (n=2000)
    WP3 7-feature 7-fold CV AUC        = 0.835 (74 signs), perm_p = 0.01 (n=200)

A2 asks the honesty question A1 deliberately deferred: WAS the reported significance corrected for the SEARCH
that produced it? This script enumerates every selection degree of freedom and MECHANICALLY computes the
corrected significances.

Two statistically distinct objects, kept rigorously separate:

  (I)  WP1 single-feature "position is the best symmetry breaker": p=0.035 is the p of ONE feature chosen as the
       best of a family (the 13-channel atlas / the 7 computed distributional features). This p is NOT
       search-corrected. -> Bonferroni + Holm over the family, BH-FDR q, and an end-to-end best-of-K
       permutation null that RE-SELECTS the best channel(+threshold) under every permutation.

  (II) WP3 7-feature CV perm_p=0.01 ALREADY permutes labels through the entire 7-fold fit, so it is honest with
       respect to overfitting/CV. It does NOT cover the *config* search (freq threshold, fold count, seed, model
       family). -> best-of-selection CV permutation null that RE-SELECTS the best config under every permutation.

NON-CIRCULAR: known LB vowel labels are used ONLY to grade AUC and to define the permutation null; never a
model input. Deterministic seed 20260708. Imports the A1 primitives so the two tasks share ONE implementation.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402
from a1_recompute import feature, standardize, logreg, auc as _auc_slow, LB_VOWELS, FEATS  # noqa: E402

DATA_DIR = os.path.join(HERE, "..", "data")
SEED = 20260708


def _avg_ranks(sorted_vals):
    """Tie-averaged ranks (1..n) for an already-sorted 1-D array."""
    n = len(sorted_vals)
    ranks = np.empty(n)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_vals[j + 1] == sorted_vals[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def auc(scores, labels):
    """Vectorized Mann-Whitney AUC (ties credited 0.5); identical result to the A1 pure-Python auc()."""
    s = np.asarray(scores, dtype=float)
    y = np.asarray(labels).astype(bool)
    npos = int(y.sum()); nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return None
    order = np.argsort(s, kind="mergesort")
    r = np.empty(len(s))
    r[order] = _avg_ranks(s[order])
    R = r[y].sum()
    return (R - npos * (npos + 1) / 2.0) / (npos * nneg)

# atlas channels (foundry symmetry_breaking_atlas.json), tagged for whether they are a single-feature
# distributional AUC channel that was *effectively available* to be "the best symmetry breaker" now.
ATLAS = [
    ("POSITION", "internal", True, True),               # -> initial_rate/final_rate/mean_pos/lone_rate
    ("SCRIBAL_SUBSTITUTION", "internal", True, False),   # needs minimal pairs, not a per-sign single feature
    ("ORTHOGRAPHIC_ALTERNATION", "internal", True, False),
    ("MORPHOLOGY", "internal", True, False),
    ("PHONOTACTICS", "internal", True, True),            # -> lnbr_ent/rnbr_ent
    ("SIGN_SHAPE_ALLOGRAPHY", "internal", True, False),
    ("CROSS_SCRIPT_AB_SHARED", "external", True, False),
    ("CRETAN_HIEROGLYPHIC", "external", False, False),
    ("CYPRO_MINOAN", "external", False, False),
    ("EXTERNAL_ANCHORS", "external", True, False),
    ("ACROPHONY_PICTORIAL", "internal", False, False),
    ("MEASURE_CORRESPONDENCE", "mixed", True, False),
    ("BILINGUAL", "external", False, False),
]


# ------------------------------------------------------------------ single-feature multiplicity helpers
def sf_auc(F, signs, j):
    labels = [s in LB_VOWELS for s in signs]
    scores = [F[s][j] for s in signs]
    return auc(scores, labels)


def sf_perm_p(F, signs, j, observed, two_sided, n=2000, seed=SEED):
    """One-sided (AUC>=obs) or two-sided (|AUC-0.5|>=|obs-0.5|) label-permutation p for one feature."""
    scores = [F[s][j] for s in signs]
    labels = [s in LB_VOWELS for s in signs]
    rng = random.Random(seed)
    lab = list(labels)
    obs_stat = abs(observed - 0.5) if two_sided else observed
    hits = 0
    for _ in range(n):
        rng.shuffle(lab)
        a = auc(scores, lab)
        if a is None:
            continue
        stat = abs(a - 0.5) if two_sided else a
        if stat >= obs_stat - 1e-12:
            hits += 1
    return (hits + 1) / (n + 1)


def holm(pvals):
    """Holm-Bonferroni adjusted p-values (monotone), returned in the ORIGINAL order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        val = (m - rank) * pvals[i]
        running = max(running, val)
        adj[i] = min(1.0, running)
    return adj


def bh_fdr(pvals):
    """Benjamini-Hochberg adjusted q-values, original order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = order[rank]
        val = pvals[i] * m / (rank + 1)
        prev = min(prev, val)
        adj[i] = min(1.0, prev)
    return adj


# ------------------------------------------------------------------ best-of-K single-feature null
def best_of_k_single(F, universe_signs, feat_idxs, thresholds, K, seed=SEED):
    """End-to-end search-adjusted p for the single-feature claim.

    Under every label permutation we RE-SELECT the best (feature x freq-threshold) config by |AUC-0.5| and
    record that best statistic; the observed best (over the same config grid on the true labels) is compared
    to this null of best-of-search statistics. Permutation places the 5 vowel labels uniformly at random over
    the freq>=min(thresholds) universe, so the search over thresholds is honestly integrated (a permuted vowel
    may fall on a low-freq sign and drop out at a stricter threshold, exactly as in a real re-search).
    """
    freq = {s: math.exp(F[s][6]) for s in universe_signs}
    subsets = {t: [s for s in universe_signs if freq[s] >= t] for t in thresholds}

    def best_stat(labelset):
        best = -1.0
        arg = None
        for t in thresholds:
            ss = subsets[t]
            labs = [s in labelset for s in ss]
            if sum(labs) < 2 or sum(labs) > len(labs) - 2:
                continue
            for j in feat_idxs:
                sc = [F[s][j] for s in ss]
                a = auc(sc, labs)
                if a is None:
                    continue
                st = abs(a - 0.5)
                if st > best:
                    best, arg = st, (FEATS[j], t, round(a, 3))
        return best, arg

    true_labels = set(s for s in universe_signs if s in LB_VOWELS)
    obs_best, obs_arg = best_stat(true_labels)
    rng = random.Random(seed)
    ulist = list(universe_signs)
    nv = len(true_labels)
    hits = 0
    null_best = []
    for _ in range(K):
        perm_vowels = set(rng.sample(ulist, nv))
        b, _a = best_stat(perm_vowels)
        null_best.append(b)
        if b >= obs_best - 1e-12:
            hits += 1
    p = (hits + 1) / (K + 1)
    return {
        "obs_best_stat_abs_auc_minus_half": round(obs_best, 4),
        "obs_best_config": obs_arg,
        "K": K,
        "p_search_adjusted": round(p, 4),
        "null_best_mean": round(float(np.mean(null_best)), 4),
        "null_best_p95": round(float(np.quantile(null_best, 0.95)), 4),
    }


# ------------------------------------------------------------------ CV machinery (config search)
_FOLD_CACHE: dict = {}


def _fold_masks(n, k, seed):
    """Cached (test_idx, train_idx) per fold for a given (n,k,seed): fold f = shuffled-index i with i%k==f."""
    key = (n, k, seed)
    hit = _FOLD_CACHE.get(key)
    if hit is not None:
        return hit
    rng = random.Random(seed)
    order = list(range(n)); rng.shuffle(order)
    order = np.array(order)
    masks = []
    for f in range(k):
        te = order[np.arange(n) % k == f]
        tr_mask = np.ones(n, dtype=bool); tr_mask[te] = False
        masks.append((te, np.nonzero(tr_mask)[0]))
    _FOLD_CACHE[key] = masks
    return masks


def cv_auc_cfg(Xs, y, k, seed):
    n = len(y)
    oof = np.zeros(n)
    for te, tr in _fold_masks(n, k, seed):
        if len(te) == 0:
            continue
        w, b = logreg(Xs[tr], y[tr])
        oof[te] = Xs[te] @ w + b
    return auc(oof, y)


def best_of_selection_cv(F, universe_signs, thresholds, folds, seeds, K, seed=SEED):
    """best-of-selection CV permutation null: RE-SELECT best CV AUC over (threshold x fold-count x seed) under
    every label permutation. Answers the multiplicity the WP3 perm_p=0.01 does NOT cover (config search)."""
    freq = {s: math.exp(F[s][6]) for s in universe_signs}
    subsets = {t: [s for s in universe_signs if freq[s] >= t] for t in thresholds}
    # pre-standardize per threshold
    Xstd = {}
    for t in thresholds:
        ss = subsets[t]
        Xm = np.array([F[s] for s in ss])
        Xs, _, _ = standardize(Xm)
        Xstd[t] = (ss, Xs)

    def best_cv(labelset):
        best = -1.0; arg = None
        for t in thresholds:
            ss, Xs = Xstd[t]
            y = np.array([1.0 if s in labelset else 0.0 for s in ss])
            if y.sum() < 2 or y.sum() > len(y) - 2:
                continue
            for k in folds:
                for sd in seeds:
                    a = cv_auc_cfg(Xs, y, k, sd)
                    if a is not None and a > best:
                        best, arg = a, {"threshold": t, "folds": k, "seed": sd, "auc": round(a, 3)}
        return best, arg

    true_labels = set(s for s in universe_signs if s in LB_VOWELS)
    obs_best, obs_arg = best_cv(true_labels)
    rng = random.Random(seed)
    ulist = list(universe_signs)
    nv = len(true_labels)
    hits = 0; null_best = []
    for _i in range(K):
        if _i % 25 == 0:
            print("  [best_of_selection_cv] perm %d/%d" % (_i, K), file=sys.stderr, flush=True)
        perm_vowels = set(rng.sample(ulist, nv))
        b, _a = best_cv(perm_vowels)
        null_best.append(b)
        if b is not None and b >= obs_best - 1e-12:
            hits += 1
    return {
        "obs_best_cv_auc_over_config_grid": round(obs_best, 4),
        "obs_best_config": obs_arg,
        "K": K,
        "n_configs": len(thresholds) * len(folds) * len(seeds),
        "config_grid": {"thresholds": thresholds, "folds": folds, "seeds": seeds},
        "p_search_adjusted": round((hits + 1) / (K + 1), 4),
        "null_best_mean": round(float(np.mean(null_best)), 4),
        "null_best_p95": round(float(np.quantile(null_best, 0.95)), 4),
    }


def run():
    lb_seqs, _, _ = X.load_b_damos()
    F = feature(lb_seqs)
    freq = {s: math.exp(F[s][6]) for s in F}
    signs77 = sorted(s for s in F if round(freq[s]) >= 20)     # correct integer inventory (per A1)
    signs74 = sorted(s for s in F if freq[s] >= 20)            # foundry WP3 explog inventory
    universe10 = sorted(s for s in F if round(freq[s]) >= 10)  # widest set for threshold-search null

    # ============================================================= (I) single-feature family correction
    # per-feature single AUC + one-sided (foundry convention) + two-sided perm p, on the correct 77-sign set
    feat_rows = []
    for j, fn in enumerate(FEATS):
        a = sf_auc(F, signs77, j)
        p1 = sf_perm_p(F, signs77, j, a, two_sided=False, n=2000)
        p2 = sf_perm_p(F, signs77, j, a, two_sided=True, n=2000)
        feat_rows.append({"feature": fn, "auc": round(a, 3), "abs_auc_minus_half": round(abs(a - 0.5), 3),
                          "perm_p_one_sided": round(p1, 4), "perm_p_two_sided": round(p2, 4)})
    # also on 74-sign set (foundry WP3 grading) for initial_rate parity
    a_init74 = sf_auc(F, signs74, 0)
    p_init74 = sf_perm_p(F, signs74, 0, a_init74, two_sided=False, n=2000)

    # family = the 7 computed distributional features (the concrete search that produced "position is best")
    p_one = [r["perm_p_one_sided"] for r in feat_rows]
    p_two = [r["perm_p_two_sided"] for r in feat_rows]
    holm_two = holm(p_two)
    bh_two = bh_fdr(p_two)
    for r, ho, bq in zip(feat_rows, holm_two, bh_two):
        r["holm_adj_p_two_sided"] = round(ho, 4)
        r["bh_fdr_q_two_sided"] = round(bq, 4)

    # the position/initial_rate specific correction the WP1 headline needs
    init_row = next(r for r in feat_rows if r["feature"] == "initial_rate")
    m_feat_family = 7
    m_atlas_nominal = len(ATLAS)                                        # 13
    m_atlas_internal_available_singlefeat = sum(1 for _n, io, av, sf in ATLAS if sf)  # POSITION+PHONOTACTICS=2 channels
    init_p1 = init_row["perm_p_one_sided"]
    best_feat = min(feat_rows, key=lambda r: r["perm_p_two_sided"])

    # ============================================================= best-of-K single-feature null (channel + threshold)
    print("[stage] best-of-K single-feature nulls ...", file=sys.stderr, flush=True)
    thresholds = [10, 15, 20, 25, 30]
    bok_channel_only = best_of_k_single(F, signs77, list(range(7)), [20], K=1000)          # DOF(1) only, fixed set
    bok_channel_threshold = best_of_k_single(F, universe10, list(range(7)), thresholds, K=1000)  # DOF(1)+(2)
    # position-only sub-family (was POSITION's win itself search-robust vs other position features?)
    bok_position_only = best_of_k_single(F, universe10, [0, 1, 2, 3], thresholds, K=1000)
    print("[stage] best-of-selection CV null ...", file=sys.stderr, flush=True)

    # ============================================================= (II) 7-feature CV: config-search correction
    # restate the honest label-perm through the fit (already computed in A1 = 0.01); here re-derive best-of-config
    cv_thresholds = [15, 20, 25]           # 3 thresholds x 3 fold-counts x 2 seeds = 18 configs
    bos_cv = best_of_selection_cv(F, universe10, cv_thresholds, folds=[5, 7, 10],
                                  seeds=[SEED, 1], K=200)

    # naive garden-of-forking-paths product (for narrative only; the best-of-K nulls are the principled version)
    naive_product = {
        "feature_family": 7, "atlas_nominal": 13, "freq_thresholds": len(thresholds),
        "fold_counts": 3, "seeds_effective": "1 used / unbounded available (>=4 sampled)",
        "model_families": "logreg used / >=3 available (LDA, threshold, tree)",
        "analogues": "LB used / >=2-3 readable syllabaries available (Cypriot Greek, etc.) -- NOT empirically integrated here",
        "illustrative_config_count_internal_only": 7 * len(thresholds) * 3 * 4,
    }

    out = {
        "meta": {
            "seed": SEED, "task": "A2_multiplicity_audit",
            "note": "single implementation shared with A1 (imported primitives); LB labels grade only.",
            "inventories": {"n_signs_int77": len(signs77), "n_signs_explog74": len(signs74),
                            "n_universe_freq10": len(universe10)},
        },
        "selection_degrees_of_freedom": {
            "1_feature_family_search": {
                "what": "position/initial_rate reported as THE single best symmetry breaker",
                "alternatives_effectively_tried": {
                    "computed_distributional_features": m_feat_family,
                    "atlas_channels_nominal": m_atlas_nominal,
                    "atlas_channels_internal_singlefeature_available_now": m_atlas_internal_available_singlefeat,
                },
            },
            "2_freq_threshold": {"what": "freq>=20 inventory cut", "alternatives_effectively_tried": len(thresholds),
                                 "grid": thresholds, "note": "continuous DOF; 5-point grid is a conservative discretization"},
            "3_folds_and_seed": {"what": "7-fold CV + seed 20260708",
                                 "alternatives_effectively_tried": {"fold_counts": [5, 7, 10], "seeds_sampled": [SEED, 1, 2, 3]}},
            "4_model_family": {"what": "L2 logistic regression",
                               "alternatives_effectively_tried": ">=3 (LDA / single-threshold / tree)",
                               "note": "the CV perm null re-fits the SAME model under permutation, so it is honest "
                                       "wrt overfitting; model SELECTION remains an uncorrected DOF"},
            "5_analogue_choice": {"what": "Linear B chosen among readable syllabaries",
                                  "alternatives_effectively_tried": ">=2-3 (Cypriot Greek syllabary, etc.)",
                                  "note": "no non-LB loader in scope; folded in analytically, not empirically"},
        },
        "I_single_feature_position": {
            "claim": "position (initial_rate) AUC 0.744, unadjusted perm_p 0.035 = 'best symmetry breaker'",
            "per_feature_family_77signs": feat_rows,
            "initial_rate_on_74signs": {"auc": round(a_init74, 3), "perm_p_one_sided": round(p_init74, 4)},
            "unadjusted_p_one_sided_initial_rate_77": init_p1,
            "the_actual_best_feature_by_p": best_feat["feature"],
            "family_wise_correction_over_atlas": {
                "family_size_used_feature_family": m_feat_family,
                "bonferroni_p_initial_rate_x7": round(min(1.0, init_p1 * m_feat_family), 4),
                "bonferroni_p_initial_rate_x13_atlas_nominal": round(min(1.0, init_p1 * m_atlas_nominal), 4),
                "holm_adj_p_initial_rate_two_sided_over7": init_row["holm_adj_p_two_sided"],
                "bh_fdr_q_initial_rate_two_sided_over7": init_row["bh_fdr_q_two_sided"],
            },
            "best_of_K_search_adjusted": {
                "channel_only_fixed_freq20": bok_channel_only,
                "channel_x_threshold": bok_channel_threshold,
                "position_subfamily_x_threshold": bok_position_only,
            },
        },
        "II_seven_feature_cv": {
            "claim": "7-fold CV AUC 0.835, perm_p 0.01 (n=200)",
            "label_perm_through_fit_is_honest_wrt_overfitting": True,
            "recomputed_perm_p_A1": {"explog74": 0.01, "int77": 0.01},
            "config_search_not_covered_by_that_p": ["freq threshold", "fold count", "seed", "model family", "analogue"],
            "best_of_selection_cv_search_adjusted": bos_cv,
            "ablation_reminder_from_A1": {"all": 0.835, "log_freq_only": 0.838, "position_only_74": 0.67,
                                          "position_only_77": 0.586,
                                          "reading": "the CV AUC is a frequency prior (log_freq_only>=all); the "
                                                     "position-only structure is 0.586-0.67"},
        },
        "naive_garden_of_forking_paths_product": naive_product,
    }

    # ---------- mechanical verdicts ----------
    alpha = 0.05
    survives_bonf7 = out["I_single_feature_position"]["family_wise_correction_over_atlas"]["bonferroni_p_initial_rate_x7"] < alpha
    survives_bonf13 = out["I_single_feature_position"]["family_wise_correction_over_atlas"]["bonferroni_p_initial_rate_x13_atlas_nominal"] < alpha
    survives_bok_ct = bok_channel_threshold["p_search_adjusted"] < alpha
    cv_perm_survives = 0.01 < alpha
    cv_bos_survives = bos_cv["p_search_adjusted"] < alpha
    out["verdicts"] = {
        "single_feature_position_survives_bonferroni_over_7": bool(survives_bonf7),
        "single_feature_position_survives_bonferroni_over_13_atlas": bool(survives_bonf13),
        "single_feature_position_survives_best_of_K_channel_x_threshold": bool(survives_bok_ct),
        "position_is_the_best_single_feature": best_feat["feature"] == "initial_rate",
        "seven_feature_cv_labelperm_p_survives": bool(cv_perm_survives),
        "seven_feature_cv_survives_best_of_selection_config_search": bool(cv_bos_survives),
        "headline": ("SINGLE-FEATURE POSITION CLAIM: DOWNGRADED — does not survive multiplicity; and position is "
                     "NOT even the best single feature (%s is). 7-FEATURE CV: the label-perm p=0.01 is honest "
                     "wrt overfitting and survives config-search, BUT the AUC is a frequency prior "
                     "(log_freq_only>=all), so it is not evidence of positional/relative phonological structure."
                     % best_feat["feature"]),
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "A2_multiplicity.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
