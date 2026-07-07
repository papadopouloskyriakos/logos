#!/usr/bin/env python3
"""A6 — complete null battery on the BEST surviving configuration + mechanical WP-A verdict.

BEST surviving configuration (from A1-A5): the M1 supervised 7-feature, sign-grouped 7-fold
logistic CV on the full DAMOS Linear B analogue (observed directed CV AUC ~0.828; Foundry 0.835).
This is the only configuration that survived the naive label-permutation test; A2/A3/A4/A5 already
showed it is a frequency prior that (a) fails Bonferroni at the single-feature level, (b) is not
replicated by two independent unsupervised models, (c) collapses under frequency-band grouped CV,
and (d) degrades below the chance band at the measured Linear-A operating point. A6 runs the full
null battery to nail down what the surviving AUC actually is.

Nulls (statistic = sign-grouped 7-fold logistic CV AUC of the surviving config unless noted):
  LABEL nulls (true features fixed, permute the C/V label; oriented null vs directed obs):
    1. random_cv_labels          uniform permutation of the 5 positives among 77 signs
    2. frequency_matched_labels  stratified permutation within log-freq quartiles (freq profile held)
  DATA nulls (TRUE labels fixed, destroy structure in the corpus, recompute features):
    3. shuffled_sign_positions   within-word order shuffle (kills position/order; keeps word bag+freq)
    4. shuffled_documents        global length-matched token reshuffle (document-blind; keeps freq)
    5. site_preserving_shuffle   token reshuffle within each site (keeps site-conditional freq)
    6. series_preserving_shuffle token reshuffle within each series
  ADAPTIVE selection nulls (permute label, RE-RUN the full selection, take the best AUC; corrects
                            the researcher's selection DOF):
    7. best_of_model            selection over {logistic-CV, GMM-unsup, best-single-feature-threshold}
    8. best_of_segmentation     selection over freq-threshold/inventory resolutions {15,20,25}
    9. best_of_seed             selection over CV seeds {20260708,1,2,3,4}

Non-circular: known LB vowel values grade the benchmark ONLY, never a model input.
Deterministic seed 20260708. Writes data/A6_nulls.json.
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.mixture import GaussianMixture
from sklearn.metrics import roc_auc_score

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
DAMOS_ITEMS = os.path.join(MAIN, "corpus", "bronze", "linearb", "damos", "items.jsonl")
SEED = 20260708
LB_VOWELS = {"A", "E", "I", "O", "U"}
FEATS = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]
POS_FEATS = [f for f in FEATS if f != "log_freq"]
MIN_FREQ = 20


# ---------------------------------------------------------------- data
def load_b_damos_meta():
    rows = []
    with open(DAMOS_ITEMS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            it = rec.get("item", {}) or {}
            content = it.get("content", "") or ""
            site = it.get("ishort")
            series = it.get("seriessicura") or it.get("series")
            for w in X._damos_wordforms(content):
                rows.append((tuple(w), {"site": site, "series": series}))
    return rows


# ---------------------------------------------------------------- features
def features(seqs):
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
        F[s] = {
            "initial_rate": init[s] / tot[s], "final_rate": fin[s] / tot[s],
            "mean_pos": pos[s] / tot[s], "lone_rate": lone[s] / tot[s],
            "lnbr_ent": ent(lnb.get(s, Counter())), "rnbr_ent": ent(rnb.get(s, Counter())),
            "log_freq": math.log(tot[s]), "freq": tot[s],
        }
    return F


def matrix(F, signs, feat_names):
    return np.array([[F[s][f] for f in feat_names] for s in signs], dtype=float)


def oriented_auc(scores, labels):
    a = roc_auc_score(labels, scores)
    return max(a, 1.0 - a)


def grouped_cv_oof(F, signs, y, feat_names, k=7, seed=SEED):
    """Sign-grouped k-fold OOF decision scores (each sign held out exactly once)."""
    Xm = matrix(F, signs, feat_names)
    mu, sd = Xm.mean(0), Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    rng = np.random.RandomState(seed)
    order = rng.permutation(len(signs))
    folds = [order[i::k] for i in range(k)]
    oof = np.zeros(len(signs))
    for te in folds:
        te_set = set(te.tolist())
        tr = np.array([i for i in range(len(signs)) if i not in te_set])
        if len(set(y[tr].tolist())) < 2:
            oof[te] = 0.0
            continue
        clf = LogisticRegression(C=1.0, max_iter=2000).fit(Xs[tr], y[tr])
        oof[te] = clf.decision_function(Xs[te])
    return oof


def grouped_cv_auc_directed(F, signs, y, feat_names, k=7, seed=SEED):
    return float(roc_auc_score(y, grouped_cv_oof(F, signs, y, feat_names, k, seed)))


def grouped_cv_auc_oriented(F, signs, y, feat_names, k=7, seed=SEED):
    return float(oriented_auc(grouped_cv_oof(F, signs, y, feat_names, k, seed), y))


def gmm_oriented_auc(Xs, y, seed=SEED, n_init=3):
    gm = GaussianMixture(n_components=2, covariance_type="full", n_init=n_init,
                         random_state=seed).fit(Xs)
    post = gm.predict_proba(Xs)
    return float(oriented_auc(post[:, 1], y))


def best_single_feature_threshold_auc(F, signs, y, feat_names):
    """Best oriented single-feature AUC (threshold classifier) over the feature family."""
    best = 0.0
    for f in feat_names:
        v = np.array([F[s][f] for s in signs])
        best = max(best, float(oriented_auc(v, y)))
    return best


# ---------------------------------------------------------------- structure-destroying corpus shuffles
def shuffle_positions(rows, rng):
    out = []
    for w, _ in rows:
        w = list(w)
        rng.shuffle(w)
        out.append(w)
    return out


def _length_matched_redistribute(words, tokens, rng):
    """Redistribute a shuffled token pool back into words preserving each word's length."""
    tokens = list(tokens)
    rng.shuffle(tokens)
    out = []
    idx = 0
    for w in words:
        L = len(w)
        out.append(tokens[idx:idx + L])
        idx += L
    return out


def shuffle_global(rows, rng):
    words = [list(w) for w, _ in rows]
    pool = [s for w in words for s in w]
    return _length_matched_redistribute(words, pool, rng)


def shuffle_within_key(rows, key, rng):
    by = defaultdict(list)
    for i, (w, m) in enumerate(rows):
        by[m.get(key)].append(i)
    out = [None] * len(rows)
    for g, idxs in by.items():
        words = [list(rows[i][0]) for i in idxs]
        pool = [s for w in words for s in w]
        red = _length_matched_redistribute(words, pool, rng)
        for i, w in zip(idxs, red):
            out[i] = w
    return out


# ---------------------------------------------------------------- run
def run():
    rows = load_b_damos_meta()
    seqs = [list(w) for w, _ in rows]
    F = features(seqs)
    signs = sorted(s for s in F if F[s]["freq"] >= MIN_FREQ)   # honest integer freq>=20 -> 77
    y = np.array([1.0 if s in LB_VOWELS else 0.0 for s in signs])
    n_pos = int(y.sum())
    print(f"[data] LB wordforms={len(seqs)} signs(freq>={MIN_FREQ})={len(signs)} vowels={n_pos}")

    # ---- observed statistic of the BEST surviving configuration ----
    obs_all = grouped_cv_auc_directed(F, signs, y, FEATS)
    obs_pos = grouped_cv_auc_directed(F, signs, y, POS_FEATS)
    print(f"[obs] grouped-CV directed AUC  all={obs_all:.3f}  position-only={obs_pos:.3f}")

    results = {}

    # ================================================================ 1. random C/V labels
    N1 = 2000
    rng = np.random.RandomState(SEED + 1)
    nulls = []
    for _ in range(N1):
        yp = rng.permutation(y)
        nulls.append(grouped_cv_auc_oriented(F, signs, yp, FEATS))
    nulls = np.array(nulls)
    p1 = float((np.sum(nulls >= obs_all) + 1) / (N1 + 1))
    results["random_cv_labels"] = {
        "statistic": "grouped-CV directed AUC (all 7 feats)", "obs": round(obs_all, 3),
        "n_null": N1, "null_mean": round(float(nulls.mean()), 3),
        "null_p95": round(float(np.percentile(nulls, 95)), 3),
        "p": round(p1, 4), "note": "uniform label permutation; oriented null vs directed obs"}
    print(f"[1] random_cv_labels p={p1:.4f} null_mean={nulls.mean():.3f} null95={np.percentile(nulls,95):.3f}")

    # ================================================================ 2. frequency-matched labels
    # stratified permutation within log-freq quartiles: the fake positive set keeps the same
    # freq-quartile membership counts as the true vowels -> isolates the frequency confound.
    logf = np.array([F[s]["log_freq"] for s in signs])
    q = np.quantile(logf, [0.25, 0.5, 0.75])
    strat = np.digitize(logf, q)               # 0..3
    N2 = 2000
    rng = np.random.RandomState(SEED + 2)
    true_quart = Counter(strat[y == 1].tolist())
    nulls2 = []
    for _ in range(N2):
        yp = np.zeros(len(signs))
        for band, cnt in true_quart.items():
            idx = np.where(strat == band)[0]
            chosen = rng.choice(idx, size=cnt, replace=False)
            yp[chosen] = 1.0
        nulls2.append(grouped_cv_auc_oriented(F, signs, yp, FEATS))
    nulls2 = np.array(nulls2)
    p2 = float((np.sum(nulls2 >= obs_all) + 1) / (N2 + 1))
    results["frequency_matched_labels"] = {
        "statistic": "grouped-CV directed AUC (all 7 feats)", "obs": round(obs_all, 3),
        "n_null": N2, "null_mean": round(float(nulls2.mean()), 3),
        "null_p95": round(float(np.percentile(nulls2, 95)), 3),
        "p": round(p2, 4),
        "true_vowel_freq_quartiles": dict(true_quart),
        "note": "labels permuted WITHIN log-freq quartiles (freq profile of positives preserved); "
                "high p => the AUC is explained by the frequency location of the vowels"}
    print(f"[2] frequency_matched_labels p={p2:.4f} null_mean={nulls2.mean():.3f} null95={np.percentile(nulls2,95):.3f}")

    # ================================================================ DATA nulls 3-6
    def data_null(name, shuffler, n_real=40, seed0=1000):
        aa = []; ap = []
        for r in range(n_real):
            rng_ = np.random.RandomState(SEED + seed0 + r)
            sh = shuffler(rows, rng_)
            Fs = features(sh)
            # sign set is invariant (multiset of tokens preserved) -> same 77 signs
            sg = [s for s in signs if s in Fs and Fs[s]["freq"] >= MIN_FREQ]
            ys = np.array([1.0 if s in LB_VOWELS else 0.0 for s in sg])
            aa.append(grouped_cv_auc_directed(Fs, sg, ys, FEATS))
            ap.append(grouped_cv_auc_directed(Fs, sg, ys, POS_FEATS))
        aa = np.array(aa); ap = np.array(ap)
        # p = fraction of structure-destroyed realizations that still reach the observed AUC
        p_all = float((np.sum(aa >= obs_all) + 1) / (n_real + 1))
        p_pos = float((np.sum(ap >= obs_pos) + 1) / (n_real + 1))
        d = {"statistic": "grouped-CV directed AUC", "n_real": n_real,
             "auc_all_mean": round(float(aa.mean()), 3), "auc_all_sd": round(float(aa.std()), 3),
             "auc_pos_mean": round(float(ap.mean()), 3), "auc_pos_sd": round(float(ap.std()), 3),
             "obs_all": round(obs_all, 3), "obs_pos": round(obs_pos, 3),
             "p_all_ge_obs": round(p_all, 4), "p_pos_ge_obs": round(p_pos, 4)}
        results[name] = d
        print(f"[{name}] all={aa.mean():.3f}+-{aa.std():.3f} (p_all={p_all:.3f})  "
              f"pos={ap.mean():.3f}+-{ap.std():.3f} (p_pos={p_pos:.3f})")
        return d

    data_null("shuffled_sign_positions", shuffle_positions, n_real=40, seed0=3000)
    data_null("shuffled_documents", shuffle_global, n_real=40, seed0=4000)
    data_null("site_preserving_shuffle", lambda rw, rg: shuffle_within_key(rw, "site", rg),
              n_real=40, seed0=5000)
    data_null("series_preserving_shuffle", lambda rw, rg: shuffle_within_key(rw, "series", rg),
              n_real=40, seed0=6000)

    # precompute standardized matrix for GMM in adaptive nulls
    Xm = matrix(F, signs, FEATS)
    Xs_full = (Xm - Xm.mean(0)) / (Xm.std(0) + 1e-9)

    # ================================================================ 7. best_of_model (adaptive)
    def model_family_best_oriented(yy):
        a_log = grouped_cv_auc_oriented(F, signs, yy, FEATS)
        a_gmm = gmm_oriented_auc(Xs_full, yy)
        a_thr = best_single_feature_threshold_auc(F, signs, yy, FEATS)
        return max(a_log, a_gmm, a_thr), {"logistic_cv": a_log, "gmm": a_gmm, "single_feat_thr": a_thr}
    obs_bm, obs_bm_parts = model_family_best_oriented(y)
    N7 = 200
    rng = np.random.RandomState(SEED + 7)
    nb = []
    for _ in range(N7):
        nb.append(model_family_best_oriented(rng.permutation(y))[0])
    nb = np.array(nb)
    p7 = float((np.sum(nb >= obs_bm) + 1) / (N7 + 1))
    results["best_of_model"] = {
        "statistic": "max oriented AUC over {logistic-CV, GMM, best-single-feature}",
        "obs_best": round(float(obs_bm), 3),
        "obs_parts": {k: round(float(v), 3) for k, v in obs_bm_parts.items()},
        "n_null": N7, "null_best_mean": round(float(nb.mean()), 3),
        "null_best_p95": round(float(np.percentile(nb, 95)), 3), "p": round(p7, 4),
        "note": "each null re-runs the full model selection under a permuted label"}
    print(f"[7] best_of_model obs={obs_bm:.3f} p={p7:.4f} null95={np.percentile(nb,95):.3f} parts={results['best_of_model']['obs_parts']}")

    # ================================================================ 8. best_of_segmentation (adaptive)
    seg_thresholds = [15, 20, 25]
    seg_signsets = {}
    for t in seg_thresholds:
        ss = sorted(s for s in F if F[s]["freq"] >= t)
        seg_signsets[t] = (ss, np.array([1.0 if s in LB_VOWELS else 0.0 for s in ss]))

    def seg_family_best_directed(perm_seed=None):
        best = 0.0; parts = {}
        for t in seg_thresholds:
            ss, yt = seg_signsets[t]
            if perm_seed is None:
                yy = yt
            else:
                rr = np.random.RandomState(perm_seed + t)
                yy = rr.permutation(yt)
            a = grouped_cv_auc_directed(F, ss, yy, FEATS)
            parts[t] = a
            best = max(best, a)
        return best, parts
    obs_bs, obs_bs_parts = seg_family_best_directed(None)
    N8 = 200
    nb8 = []
    for i in range(N8):
        nb8.append(seg_family_best_directed(perm_seed=SEED + 80000 + i * 7)[0])
    nb8 = np.array(nb8)
    p8 = float((np.sum(nb8 >= obs_bs) + 1) / (N8 + 1))
    results["best_of_segmentation"] = {
        "statistic": "max directed grouped-CV AUC over freq-threshold inventories {15,20,25}",
        "obs_best": round(float(obs_bs), 3),
        "obs_parts": {str(k): round(float(v), 3) for k, v in obs_bs_parts.items()},
        "n_null": N8, "null_best_mean": round(float(nb8.mean()), 3),
        "null_best_p95": round(float(np.percentile(nb8, 95)), 3), "p": round(p8, 4),
        "note": "each null re-runs selection over the inventory/segmentation-resolution grid"}
    print(f"[8] best_of_segmentation obs={obs_bs:.3f} p={p8:.4f} null95={np.percentile(nb8,95):.3f} parts={results['best_of_segmentation']['obs_parts']}")

    # ================================================================ 9. best_of_seed (adaptive)
    seeds = [20260708, 1, 2, 3, 4]

    def seed_family_best_directed(y_use):
        vals = [grouped_cv_auc_directed(F, signs, y_use, FEATS, seed=s) for s in seeds]
        return max(vals), vals
    obs_bd, obs_bd_parts = seed_family_best_directed(y)
    N9 = 500
    rng = np.random.RandomState(SEED + 9)
    nb9 = []
    for _ in range(N9):
        yp = rng.permutation(y)
        nb9.append(seed_family_best_directed(yp)[0])
    nb9 = np.array(nb9)
    p9 = float((np.sum(nb9 >= obs_bd) + 1) / (N9 + 1))
    results["best_of_seed"] = {
        "statistic": "max directed grouped-CV AUC over CV seeds {20260708,1,2,3,4}",
        "obs_best": round(float(obs_bd), 3),
        "obs_parts": {str(s): round(float(v), 3) for s, v in zip(seeds, obs_bd_parts)},
        "n_null": N9, "null_best_mean": round(float(nb9.mean()), 3),
        "null_best_p95": round(float(np.percentile(nb9, 95)), 3), "p": round(p9, 4),
        "note": "each null re-runs selection over CV seeds under a permuted label"}
    print(f"[9] best_of_seed obs={obs_bd:.3f} p={p9:.4f} null95={np.percentile(nb9,95):.3f} parts={results['best_of_seed']['obs_parts']}")

    # ================================================================ VERDICT (mechanical)
    ALPHA = 0.05
    # survival flags used by the decision rule -----------------------------------------
    survives_naive_labelperm = results["random_cv_labels"]["p"] < ALPHA
    survives_freq_matched = results["frequency_matched_labels"]["p"] < ALPHA  # BEYOND frequency
    # position structure survives destroying order? (obs_pos beyond the position-destroyed dist)
    pos_beyond_shuffle = results["shuffled_sign_positions"]["p_pos_ge_obs"] < ALPHA
    # all-feature AUC explained by frequency? (survives if it CANNOT be reproduced by freq-only shuffles)
    all_beyond_global_shuffle = results["shuffled_documents"]["p_all_ge_obs"] < ALPHA
    survives_best_of_model = results["best_of_model"]["p"] < ALPHA
    survives_best_of_seg = results["best_of_segmentation"]["p"] < ALPHA
    survives_best_of_seed = results["best_of_seed"]["p"] < ALPHA

    # pull the cross-work facts from A2-A5 (mechanical, read from disk) -----------------
    def _load(name):
        return json.load(open(os.path.join(DATA, name)))
    a3 = _load("A3_replications.json")
    a4 = _load("A4_grouped.json")
    a5 = _load("A5_surface.json")
    m2_auc = a3["A_MODEL_2_gmm_unsupervised"]["all_features"]["auc"]
    m2_null95 = a3["A_MODEL_2_gmm_unsupervised"]["all_features"]["null_auc_95pct"]
    m3_auc = a3["A_MODEL_3_hmm_unsupervised"]["auc"]
    m3_null95 = a3["A_MODEL_3_hmm_unsupervised"]["null_auc_95pct"]
    independent_models_replicate = (m2_auc > m2_null95) and (m3_auc > m3_null95)
    freqband = a4["sign_unit_frequency_band_leaveout"]
    freqband_grouped_survives = freqband["all_feats"]["perm_p"] < ALPHA
    la_op = a5["linear_a_operating_point_measured"]
    la_survives = la_op["auc_all"] > la_op["null95_all"]

    # per-model grouped AUCs (from A4) for the numbers field ---------------------------
    per_model_grouped = {
        "M1_logistic_sign_grouped_7fold_all": a4["baselines"]["sign_grouped_7fold_all_feats"],
        "M1_logistic_sign_grouped_7fold_position_only": a4["baselines"]["sign_grouped_7fold_position_only"],
        "M1_logistic_leave_one_site_out_pooled": a4["feature_domain_grouped"]["leave_one_site_out"]["all_feats"]["pooled_auc"],
        "M1_logistic_leave_one_series_out_pooled": a4["feature_domain_grouped"]["leave_one_series_out"]["all_feats"]["pooled_auc"],
        "M1_logistic_frequency_band_grouped_all": freqband["all_feats"]["oof_auc"],
        "M1_logistic_frequency_band_grouped_position_only": freqband["position_only"]["oof_auc"],
        "M2_gmm_unsupervised_auc": m2_auc,
        "M2_gmm_null95": m2_null95,
        "M3_hmm_unsupervised_auc": m3_auc,
        "M3_hmm_null95": m3_null95,
    }

    # DECISION RULE (stated explicitly) ------------------------------------------------
    # REPLICATED requires: (a) survives >=2 INDEPENDENT models (M2 GMM AND M3 HMM above their
    #   own nulls) AND (b) grouped CV that controls the frequency confound (frequency-band LOGO)
    #   AND (c) end-to-end multiplicity/adaptive correction (all best-of-* nulls) AND (d) survives
    #   the frequency-matched label null (structure BEYOND frequency).
    # EXPLORATORY_ONLY: survives the naive label permutation but fails the adaptive/grouped/
    #   frequency-confound controls (i.e. it is real in-sample but is a frequency prior / not
    #   independently replicated).
    # REFUTED: fails independent replication AND the frequency-confound grouped CV (the positive
    #   signal is fully attributable to frequency and does not generalise off the confound), OR
    #   degrades below the chance band at the measured Linear-A operating point.
    replicated = (independent_models_replicate and freqband_grouped_survives
                  and survives_best_of_model and survives_best_of_seg and survives_best_of_seed
                  and survives_freq_matched and pos_beyond_shuffle)
    refuted = ((not independent_models_replicate and not freqband_grouped_survives)
               or not la_survives or not survives_freq_matched)
    if replicated:
        verdict = "CV_ANALOGUE_REPLICATED"
    elif refuted:
        verdict = "CV_ANALOGUE_REFUTED"
    elif survives_naive_labelperm:
        verdict = "CV_ANALOGUE_EXPLORATORY_ONLY"
    else:
        verdict = "CV_ANALOGUE_INCOMPLETE"

    decision = {
        "alpha": ALPHA,
        "flags": {
            "survives_naive_labelperm": survives_naive_labelperm,
            "survives_frequency_matched_label_null (structure beyond frequency)": survives_freq_matched,
            "position_structure_beyond_order_shuffle": pos_beyond_shuffle,
            "all_feat_AUC_beyond_global_freq_shuffle": all_beyond_global_shuffle,
            "survives_best_of_model": survives_best_of_model,
            "survives_best_of_segmentation": survives_best_of_seg,
            "survives_best_of_seed": survives_best_of_seed,
            "independent_unsupervised_models_replicate (M2 AND M3 > null95)": independent_models_replicate,
            "frequency_band_grouped_CV_survives (A4)": freqband_grouped_survives,
            "survives_at_measured_LinearA_operating_point (A5)": la_survives,
        },
        "cross_work_numbers": {
            "M2_gmm_auc": m2_auc, "M2_gmm_null95": m2_null95,
            "M3_hmm_auc": m3_auc, "M3_hmm_null95": m3_null95,
            "freqband_grouped_all_auc": freqband["all_feats"]["oof_auc"],
            "freqband_grouped_all_perm_p": freqband["all_feats"]["perm_p"],
            "freqband_grouped_position_only_auc": freqband["position_only"]["oof_auc"],
            "LA_operating_point_auc_all": la_op["auc_all"],
            "LA_operating_point_null95": la_op["null95_all"],
        },
        "decision_rule": (
            "REPLICATED := independent_models_replicate AND frequency_band_grouped_CV_survives "
            "AND all best-of-{model,segmentation,seed} adaptive nulls p<0.05 AND "
            "frequency_matched_label_null p<0.05 AND position_structure_beyond_order_shuffle. "
            "REFUTED := (NOT independent_models_replicate AND NOT frequency_band_grouped_CV_survives) "
            "OR NOT survives_at_measured_LinearA_operating_point OR NOT frequency_matched (freq fully "
            "explains it). EXPLORATORY_ONLY := survives naive label permutation but not the "
            "adaptive/grouped/frequency-confound controls. INCOMPLETE otherwise."),
        "verdict": verdict,
    }

    # final adjusted p-values + per-model grouped AUCs (the required 'numbers') ---------
    adjusted_p = {
        "random_cv_labels": results["random_cv_labels"]["p"],
        "frequency_matched_labels": results["frequency_matched_labels"]["p"],
        "shuffled_sign_positions_p_pos_ge_obs": results["shuffled_sign_positions"]["p_pos_ge_obs"],
        "shuffled_sign_positions_p_all_ge_obs": results["shuffled_sign_positions"]["p_all_ge_obs"],
        "shuffled_documents_p_all_ge_obs": results["shuffled_documents"]["p_all_ge_obs"],
        "site_preserving_p_all_ge_obs": results["site_preserving_shuffle"]["p_all_ge_obs"],
        "series_preserving_p_all_ge_obs": results["series_preserving_shuffle"]["p_all_ge_obs"],
        "best_of_model": results["best_of_model"]["p"],
        "best_of_segmentation": results["best_of_segmentation"]["p"],
        "best_of_seed": results["best_of_seed"]["p"],
    }

    out = {
        "meta": {
            "seed": SEED, "task": "A6_complete_nulls_and_WP_A_verdict",
            "best_surviving_config": "M1 supervised 7-feature sign-grouped 7-fold logistic CV on full DAMOS LB",
            "obs_grouped_cv_auc_all": round(obs_all, 3),
            "obs_grouped_cv_auc_position_only": round(obs_pos, 3),
            "foundry_reported_cv_auc": 0.835, "foundry_reported_single_feature_auc": 0.744,
            "n_lb_wordforms": len(seqs), "n_signs": len(signs), "n_vowels": n_pos,
            "note": "known LB vowel values grade benchmark ONLY, never a model input",
        },
        "null_battery": results,
        "decision": decision,
        "adjusted_p_values": adjusted_p,
        "per_model_grouped_auc": per_model_grouped,
        "WP_A_VERDICT": verdict,
    }
    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(os.path.join(DATA, "A6_nulls.json"), "w"), indent=1)
    print("\n==== WP-A VERDICT:", verdict, "====")
    print(json.dumps(decision["flags"], indent=1))
    return out


if __name__ == "__main__":
    run()
