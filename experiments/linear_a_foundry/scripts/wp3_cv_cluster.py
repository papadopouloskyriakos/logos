#!/usr/bin/env python3
"""WP3.1-followup — LA-internal C/V clustering (calibrated partition, no cross-script transfer).

WP3.1 trained a SUPERVISED C/V classifier on known-truth Linear B and applied the LB-fit decision
boundary to Linear A. That transfer failed to calibrate: on LA every sign scored prob<0.5 (0 vowel-like)
because the LB-learned intercept/scale does not port across scripts. This followup removes the cross-script
calibration entirely: it clusters signs into 2 classes UNSUPERVISED (k-means / GMM on standardized
position/distribution features), so the decision boundary is found WITHIN each script.

MANDATORY known-truth benchmark: the identical unsupervised pipeline is first run on OPAQUE Linear B
(vowel identities {A,E,I,O,U} hidden from the algorithm), and the recovered 2-class partition is scored
against the true vowel/consonant labels by Adjusted Rand Index vs a >=200-realization label-permutation
null. Only a pipeline that beats its LB null is applied to LA. Non-circular: features are pure
distributional/position statistics over sign identities; no Linear B phonetic values are ever model inputs
on the LA side. The LA output is a candidate C/V partition (relative structure), NOT an absolute reading.
Deterministic; reads corpus read-only from main.
"""
import json
import math
import os
import sys
from collections import Counter

import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260708
N_NULL = 500
LB_VOWELS = {"A", "E", "I", "O", "U"}
FEATS = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]
# position/distribution-only subset (drops log_freq; WP3.1 found freq dominated the supervised signal)
POS_IDX = [0, 1, 2, 3, 4, 5]
FREQ_MIN = 20


def features(seqs):
    """Identical feature extraction to WP3.1 wp3_cv_recovery.features()."""
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


def build_matrix(F, cols):
    signs = sorted(s for s in F if math.exp(F[s][6]) >= FREQ_MIN)
    Xm = np.array([[F[s][c] for c in cols] for s in signs], dtype=float)
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9
    return signs, (Xm - mu) / sd


def cluster2(Xs, method):
    if method == "kmeans":
        m = KMeans(n_clusters=2, n_init=25, random_state=SEED)
        lab = m.fit_predict(Xs)
    else:  # gmm
        m = GaussianMixture(n_components=2, covariance_type="full", n_init=10, random_state=SEED)
        lab = m.fit_predict(Xs)
    return np.asarray(lab)


def enriched_cluster(labels, truth):
    """Return (vowel_cluster_id, recall, purity, vowel_rate_by_cluster)."""
    rates = {}
    for c in (0, 1):
        idx = labels == c
        rates[c] = float(truth[idx].mean()) if idx.any() else 0.0
    vc = max(rates, key=rates.get)
    inc = labels == vc
    n_vow = int(truth.sum())
    recall = float(truth[inc].sum()) / n_vow if n_vow else 0.0     # frac of true vowels in enriched cluster
    purity = float(truth[inc].mean()) if inc.any() else 0.0         # frac of enriched cluster that is vowels
    return vc, recall, purity, rates


def eval_lb(Xs, truth, method, rng):
    labels = cluster2(Xs, method)
    ari = adjusted_rand_score(truth, labels)
    vc, recall, purity, rates = enriched_cluster(labels, truth)
    # label-permutation null: clustering FIXED, permute the true C/V labels among signs
    nulls = []
    for _ in range(N_NULL):
        tp = truth.copy(); rng.shuffle(tp)
        nulls.append(adjusted_rand_score(tp, labels))
    nulls = np.array(nulls)
    p = float((int((nulls >= ari).sum()) + 1) / (N_NULL + 1))
    return {
        "method": method, "ari": round(float(ari), 4),
        "vowel_recall": round(recall, 3), "vowel_purity": round(purity, 3),
        "n_vowels_captured": int(round(recall * int(truth.sum()))), "n_vowels_total": int(truth.sum()),
        "enriched_cluster_size": int((labels == vc).sum()),
        "vowel_rate_by_cluster": {str(k): round(v, 3) for k, v in rates.items()},
        "perm_null_mean_ari": round(float(nulls.mean()), 4),
        "perm_null_p95_ari": round(float(np.quantile(nulls, 0.95)), 4),
        "perm_p": round(p, 4), "n_null": N_NULL,
        "passes": bool(ari > 0 and p < 0.05 and recall >= 0.6),
    }, labels


def profile_cluster(Xraw_by_sign, signs, labels, cols):
    """Descriptive per-cluster centroid in RAW (interpretable) feature units."""
    prof = {}
    for c in (0, 1):
        members = [signs[i] for i in range(len(signs)) if labels[i] == c]
        if not members:
            prof[c] = {}; continue
        arr = np.array([[Xraw_by_sign[s][j] for j in cols] for s in members], dtype=float)
        prof[c] = {FEATS[cols[j]]: round(float(arr[:, j].mean()), 3) for j in range(len(cols))}
        prof[c]["size"] = len(members)
    return prof


def run():
    rng = np.random.default_rng(SEED)

    # ---- known-truth LB benchmark ----
    lb_seqs, _, _ = X.load_b_damos()
    FB = features(lb_seqs)
    lb_bench = {}
    lb_best = None
    for tag, cols in (("all_feats", list(range(7))), ("pos_only", POS_IDX)):
        signs, Xs = build_matrix(FB, cols)
        truth = np.array([1.0 if s in LB_VOWELS else 0.0 for s in signs])
        lb_bench[tag] = {}
        for method in ("kmeans", "gmm"):
            res, labels = eval_lb(Xs, truth, method, np.random.default_rng(SEED))
            lb_bench[tag][method] = res
            cand = (res["ari"], res["vowel_recall"], tag, cols, method, res["passes"])
            if res["passes"] and (lb_best is None or res["ari"] > lb_best[0]):
                lb_best = cand
    lb_bench["n_signs"] = len(np.array([s for s in FB if math.exp(FB[s][6]) >= FREQ_MIN]))

    # ---- apply the LB-validated pipeline to LA (unsupervised, no transfer) ----
    la_out = {"applied": False,
              "reason": "no LB config beat its label-permutation null (passes=True); pipeline not applied to LA"}
    if lb_best is not None:
        _, _, tag, cols, method, _ = lb_best
        la_seqs = X.load_a()[1]
        FA = features(la_seqs)
        la_signs, LXs = build_matrix(FA, cols)
        la_labels = cluster2(LXs, method)
        prof = profile_cluster(FA, la_signs, la_labels, cols)
        # identify the vowel-like cluster PURELY from LA-internal profile:
        # vowels are disproportionately word-initial and stand alone -> higher initial_rate + lone_rate.
        score = {c: prof[c].get("initial_rate", 0) + prof[c].get("lone_rate", 0) for c in (0, 1)}
        v_cluster = max(score, key=score.get)
        vowel_like = sorted(la_signs[i] for i in range(len(la_signs)) if la_labels[i] == v_cluster)
        cons_like = sorted(la_signs[i] for i in range(len(la_signs)) if la_labels[i] != v_cluster)
        la_out = {
            "applied": True,
            "config": {"feature_set": tag, "method": method, "n_signs": len(la_signs)},
            "vowel_like_cluster_id": int(v_cluster),
            "vowel_like_identification_basis": "LA-internal profile: cluster with higher mean(initial_rate)+mean(lone_rate); "
                                               "vowels are disproportionately word-initial / standalone. No LB values used.",
            "cluster_profiles_raw": {str(k): v for k, v in prof.items()},
            "n_vowel_like": len(vowel_like), "n_consonant_like": len(cons_like),
            "vowel_like_signs": vowel_like,
            "consonant_like_signs": cons_like,
            "note": "candidate C/V partition from LA-internal distribution only; relative structure, NOT an absolute reading",
        }

    verdict = ("CV_CLUSTER_RECOVERED" if lb_best is not None else "NULL")
    out = {
        "experiment": "WP3.1-followup — unsupervised LA-internal C/V clustering",
        "method": "2-class k-means/GMM on standardized WP3.1 features; ARI vs label-permutation null; "
                  "known-truth LB benchmark GATES application to LA",
        "seed": SEED, "freq_min": FREQ_MIN,
        "LB_benchmark": lb_bench,
        "LB_best_config": (None if lb_best is None else
                           {"feature_set": lb_best[2], "method": lb_best[4],
                            "ari": lb_best[0], "vowel_recall": lb_best[1]}),
        "LA_partition": la_out,
        "verdict": verdict,
        "reduces_equivalence_classes": bool(lb_best is not None and la_out.get("applied")),
        "contrast_with_WP3.1": "WP3.1 supervised LB->LA transfer put 0 signs in the vowel class (calibration "
                               "collapse); unsupervised within-script clustering finds the boundary per script "
                               "and yields a non-degenerate LA partition.",
    }
    os.makedirs(os.path.join(HERE, "..", "data"), exist_ok=True)
    outp = os.path.join(HERE, "..", "data", "wp3_cv_cluster.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "LA_partition"}, indent=1))
    print("\nLA:", json.dumps({k: la_out.get(k) for k in ("applied", "config", "n_vowel_like",
          "n_consonant_like", "cluster_profiles_raw")}, indent=1))
    print("wrote", outp)
    return out


if __name__ == "__main__":
    run()
