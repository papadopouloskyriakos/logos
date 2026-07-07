#!/usr/bin/env python3
"""A1 — Independent reconstruction of the Foundry position->C/V symmetry-break result.

Audit task A1 (Constitution v2.2). This script re-derives, FROM SCRATCH and WITHOUT importing any
Foundry code (experiments/linear_a_foundry/), the three headline numbers:

    * WP1 single-feature (word-initial-rate) AUC separating the 5 known Linear B vowel signs   -> claimed 0.744
    * WP3 7-feature logistic-regression 7-fold cross-validated AUC on Linear B                  -> claimed 0.835
    * WP3 label-permutation p-value for that CV AUC (n_null=200)                                -> claimed 0.01

Independence: the feature extractor, the logistic-regression solver, the AUC (Mann-Whitney) and the
cross-validation / permutation machinery are all re-implemented here. A bug in the Foundry scripts
therefore cannot silently reproduce itself. Where a numerical choice is load-bearing (freq>=20 threshold,
7-fold split logic, standardization, l2/lr/iters, seed) it is reproduced EXACTLY so the comparison is
apples-to-apples, and any residual gap is a genuine finding, not a config drift.

NON-CIRCULAR: known LB vowel/consonant values are used ONLY as grading labels (the y vector). They are
never a model INPUT feature — every one of the 7 features is a pure distributional statistic over sign
identities.

The clean helpers feature(), logreg(), auc(), cv_auc() are exported for downstream audit tasks to import.
Deterministic seed 20260708.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from collections import Counter

import numpy as np

# --- data access (read-only) ----------------------------------------------------------------------
# The DAMOS/GORILA corpora are gitignored and only materialized in the main worktree, so the data
# LOADERS are imported from there (identical code to this worktree's scripts/cross_script/data.py).
# This is a read-only data source; all analysis code below is reimplemented locally.
MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")
SEED = 20260708
LB_VOWELS = {"A", "E", "I", "O", "U"}                       # known-truth grading labels ONLY
FEATS = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]


# ======================================================================================================
# reusable primitives (exported)
# ======================================================================================================
def feature(seqs):
    """Per-sign 7-feature distributional profile computed from a list of word/inscription sign-lists.

    Returns {sign: [initial_rate, final_rate, mean_pos, lone_rate, lnbr_ent, rnbr_ent, log_freq]}.
      initial_rate : P(sign is word-initial | sign occurs)
      final_rate   : P(sign is word-final   | sign occurs)
      mean_pos     : mean normalized position i/(L-1) over occurrences (0.5 for length-1 words)
      lone_rate    : (# length-1 words that are this sign) / freq
      lnbr_ent     : Shannon entropy (nats) of the left-neighbour distribution
      rnbr_ent     : Shannon entropy (nats) of the right-neighbour distribution
      log_freq     : natural log of total occurrence count
    """
    init = Counter(); fin = Counter(); tot = Counter(); pos = Counter(); lone = Counter()
    lnb: dict = {}; rnb: dict = {}
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
        init[w[0]] += 1
        fin[w[-1]] += 1

    def ent(c):
        n = sum(c.values())
        return -sum((v / n) * math.log(v / n) for v in c.values()) if n else 0.0

    F = {}
    for s in tot:
        F[s] = [init[s] / tot[s], fin[s] / tot[s], pos[s] / tot[s], lone[s] / tot[s],
                ent(lnb.get(s, Counter())), ent(rnb.get(s, Counter())), math.log(tot[s])]
    return F


def standardize(Xm):
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9
    return (Xm - mu) / sd, mu, sd


def logreg(Xm, y, l2=1.0, iters=500, lr=0.3):
    """L2-regularized logistic regression via full-batch gradient descent (independent solver)."""
    n, d = Xm.shape
    w = np.zeros(d); b = 0.0
    for _ in range(iters):
        z = Xm @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        gw = Xm.T @ (p - y) / n + l2 * w / n
        gb = float((p - y).mean())
        w -= lr * gw
        b -= lr * gb
    return w, b


def auc(scores, labels):
    """Mann-Whitney AUC of a scalar score vs binary labels (ties -> 0.5)."""
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    wins = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
    return wins / (len(pos) * len(neg))


def cv_auc(Xs, y, k=7, seed=SEED, return_oof=False, l2=1.0, iters=500, lr=0.3):
    """k-fold out-of-fold AUC. Folds by shuffled index modulo k (matches Foundry split logic)."""
    n = len(y)
    rng = random.Random(seed)
    order = list(range(n)); rng.shuffle(order)
    oof = np.zeros(n)
    for f in range(k):
        te = [order[i] for i in range(n) if i % k == f]
        tr = [i for i in range(n) if i not in te]
        w, b = logreg(Xs[tr], y[tr], l2=l2, iters=iters, lr=lr)
        oof[te] = Xs[te] @ w + b
    a = auc(list(oof), list(y))
    return (a, oof, order) if return_oof else a


# ======================================================================================================
# reconstruction runs
# ======================================================================================================
def signs_at_threshold(F, mode):
    """Sign set with freq>=20. mode='int' uses integer freq; mode='explog' uses exp(log_freq) (Foundry WP3)."""
    if mode == "int":
        return sorted(s for s in F if round(math.exp(F[s][6])) >= 20)
    return sorted(s for s in F if math.exp(F[s][6]) >= 20)


def single_feature_auc(F, signs, feat_idx=0):
    labels = [s in LB_VOWELS for s in signs]
    scores = [F[s][feat_idx] for s in signs]
    return auc(scores, labels), labels


def perm_p_single(F, signs, observed, feat_idx=0, n=2000, seed=SEED):
    scores = [F[s][feat_idx] for s in signs]
    labels = [s in LB_VOWELS for s in signs]
    rng = random.Random(seed)
    lab = list(labels)
    hits = 0
    for _ in range(n):
        rng.shuffle(lab)
        a = auc(scores, lab)
        if a is not None and a >= observed:
            hits += 1
    return (hits + 1) / (n + 1)


def cv_and_perm(F, signs, n_null=200, seed=SEED):
    Xm = np.array([F[s] for s in signs])
    y = np.array([1.0 if s in LB_VOWELS else 0.0 for s in signs])
    Xs, mu, sd = standardize(Xm)
    observed, oof, order = cv_auc(Xs, y, k=7, seed=seed, return_oof=True)
    # permutation null: reshuffle labels, recompute full 7-fold oof AUC, SAME fold structure
    rng = random.Random(seed)
    _ = list(range(len(signs))); rng.shuffle(_)   # burn the same shuffle the observed run used (order)
    nulls = []
    for _i in range(n_null):
        yp = y.copy(); rng.shuffle(yp)
        oofp = np.zeros(len(signs))
        for f in range(7):
            te = [order[i] for i in range(len(order)) if i % 7 == f]
            tr = [i for i in range(len(order)) if i not in te]
            w, b = logreg(Xs[tr], yp[tr])
            oofp[te] = Xs[te] @ w + b
        nulls.append(auc(list(oofp), list(yp)))
    p = (sum(1 for a in nulls if a is not None and a >= observed) + 1) / (len(nulls) + 1)
    return observed, p, y, Xs, mu, sd, nulls


def ablation(F, signs, seed=SEED):
    """CV AUC for feature subsets (matches Foundry ablation columns)."""
    y = np.array([1.0 if s in LB_VOWELS else 0.0 for s in signs])
    out = {}
    subsets = {
        "all": list(range(7)),
        "log_freq_only": [6],
        "minus_log_freq": [0, 1, 2, 3, 4, 5],
        "position_only": [0, 1, 2],          # initial, final, mean_pos
    }
    for name, idx in subsets.items():
        Xm = np.array([[F[s][j] for j in idx] for s in signs])
        Xs, _, _ = standardize(Xm)
        out[name] = round(cv_auc(Xs, y, k=7, seed=seed), 3)
    return out


def run():
    lb_seqs, lb_freq_loader, _ = X.load_b_damos()
    F = feature(lb_seqs)

    # --- sign inventory reconciliation: integer vs exp(log) freq>=20 threshold -------------------
    signs_int = signs_at_threshold(F, "int")
    signs_explog = signs_at_threshold(F, "explog")
    dropped = sorted(set(signs_int) - set(signs_explog))
    dropped_detail = [{"sign": s, "int_freq": round(math.exp(F[s][6])), "explog": math.exp(F[s][6])}
                      for s in dropped]

    # === WP1 reconstruction: single-feature initial_rate AUC ======================================
    # Foundry WP1 used the integer-freq sign set (77 signs).
    a_init_int, _ = single_feature_auc(F, signs_int, feat_idx=0)
    p_init_int = perm_p_single(F, signs_int, a_init_int, feat_idx=0, n=2000)
    a_init_explog, _ = single_feature_auc(F, signs_explog, feat_idx=0)

    # === WP3 reconstruction: 7-feature 7-fold CV AUC + permutation p ===============================
    # Foundry WP3 used the exp(log)-freq sign set (74 signs). Recompute on BOTH for full reconciliation.
    cv_explog, p_explog, y_e, *_ = cv_and_perm(F, signs_explog, n_null=200)
    cv_int, p_int, y_i, *_ = cv_and_perm(F, signs_int, n_null=200)

    abl_explog = ablation(F, signs_explog)
    abl_int = ablation(F, signs_int)

    def match(recomputed, published, tol):
        return abs(recomputed - published) <= tol

    out = {
        "meta": {
            "seed": SEED, "features": FEATS, "lb_vowels": sorted(LB_VOWELS),
            "n_lb_wordforms": len(lb_seqs), "logreg": {"l2": 1.0, "iters": 500, "lr": 0.3},
            "cv": {"folds": 7, "split": "shuffled index % k", "standardize": "z-score on full sign set"},
            "perm_null": {"single_feature_n": 2000, "cv_n": 200, "stat": ">= observed", "p": "(hits+1)/(n+1)"},
            "note": "independent reimplementation; no Foundry import. Known LB values used ONLY as grading labels.",
        },
        "sign_inventory": {
            "threshold": "freq>=20",
            "n_signs_int_freq": len(signs_int),
            "n_signs_explog_freq": len(signs_explog),
            "n_true_vowels_present_int": sum(s in LB_VOWELS for s in signs_int),
            "n_true_vowels_present_explog": sum(s in LB_VOWELS for s in signs_explog),
            "signs_dropped_by_explog_threshold": dropped_detail,
            "explog_threshold_bug": ("Foundry WP3 filters with math.exp(math.log(freq))>=20; floating-point "
                                     "rounding drops signs whose freq is EXACTLY 20, so WP3 grades on 74 signs "
                                     "while WP1 grades on 77. A clean integer freq>=20 keeps all 77."),
        },
        "WP1_single_feature": {
            "published_auc": 0.744, "published_perm_p": 0.035,
            "recomputed_auc_int77": round(a_init_int, 3),
            "recomputed_perm_p_int77": round(p_init_int, 4),
            "recomputed_auc_explog74": round(a_init_explog, 3),
            "matches_published_auc_within_0.01": match(a_init_int, 0.744, 0.01),
        },
        "WP3_cv": {
            "published_cv_auc": 0.835, "published_perm_p": 0.01, "published_n_signs": 74,
            "recomputed_cv_auc_explog74": round(cv_explog, 3),
            "recomputed_perm_p_explog74": round(p_explog, 4),
            "recomputed_cv_auc_int77": round(cv_int, 3),
            "recomputed_perm_p_int77": round(p_int, 4),
            "matches_published_cv_within_0.01": match(cv_explog, 0.835, 0.01),
            "matches_published_p_within_0.02": match(p_explog, 0.01, 0.02),
        },
        "ablation_explog74": abl_explog,
        "ablation_int77": abl_int,
        "verdict_reconstruction": (
            "REPRODUCED" if (match(a_init_int, 0.744, 0.01) and match(cv_explog, 0.835, 0.01)
                             and match(p_explog, 0.01, 0.02)) else "DISCREPANCY"),
    }
    def _ser(o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        raise TypeError(str(type(o)))

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "A1_recompute.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=_ser)
    print(json.dumps(out, indent=1, default=_ser))
    return out


if __name__ == "__main__":
    run()
