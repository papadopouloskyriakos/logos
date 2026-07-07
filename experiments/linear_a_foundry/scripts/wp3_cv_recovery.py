#!/usr/bin/env python3
"""WP3.1 — vowel/consonant partition recovery (Constitution v2.2 Art. IV/VII/XII).

Extends the WP1 single-feature counterexample into a multi-feature C/V classifier, trained + cross-validated
on KNOWN-TRUTH Linear B (vowels = {A,E,I,O,U}), then applied to Linear A. Non-circular: features are pure
distributional/position statistics over sign identities; no phonetic values are used as inputs. A held-out
C/V partition on LB above chance proves internal evidence reduces the sign-value equivalence classes; the LA
output is a candidate partition (relative structure), NOT an absolute reading. 200 label-permutation nulls.
Deterministic; reads corpus read-only from main.
"""
import json
import math
import os
import random
import sys
from collections import Counter

import numpy as np

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260708
LB_VOWELS = {"A", "E", "I", "O", "U"}
FEATS = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]


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
        F[s] = [init[s] / tot[s], fin[s] / tot[s], pos[s] / tot[s], lone[s] / tot[s],
                ent(lnb.get(s, Counter())), ent(rnb.get(s, Counter())), math.log(tot[s])]
    return F


def standardize(Xm):
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9
    return (Xm - mu) / sd, mu, sd


def logreg(Xm, y, l2=1.0, iters=500, lr=0.3):
    n, d = Xm.shape
    w = np.zeros(d); b = 0.0
    for _ in range(iters):
        z = Xm @ w + b
        p = 1 / (1 + np.exp(-z))
        gw = Xm.T @ (p - y) / n + l2 * w / n
        gb = (p - y).mean()
        w -= lr * gw; b -= lr * gb
    return w, b


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]; neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    return round(sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg)), 3)


def run():
    lb_seqs, _, _ = X.load_b_damos()
    F = features(lb_seqs)
    signs = sorted(s for s in F if math.exp(F[s][6]) >= 20)      # freq>=20
    Xm = np.array([F[s] for s in signs]); y = np.array([1.0 if s in LB_VOWELS else 0.0 for s in signs])
    Xs, mu, sd = standardize(Xm)
    # 7-fold CV AUC on LB (held-out vowel recovery)
    rng = random.Random(SEED); order = list(range(len(signs))); rng.shuffle(order)
    k = 7; oof = np.zeros(len(signs))
    for f in range(k):
        te = [order[i] for i in range(len(order)) if i % k == f]
        tr = [i for i in range(len(order)) if i not in te]
        w, b = logreg(Xs[tr], y[tr])
        oof[te] = Xs[te] @ w + b
    cv_auc = auc(list(oof), list(y))
    # permutation null on the CV AUC
    nulls = []
    for _ in range(200):
        yp = y.copy(); rng.shuffle(yp)
        oofp = np.zeros(len(signs))
        for f in range(k):
            te = [order[i] for i in range(len(order)) if i % k == f]
            tr = [i for i in range(len(order)) if i not in te]
            w, b = logreg(Xs[tr], yp[tr]); oofp[te] = Xs[te] @ w + b
        nulls.append(auc(list(oofp), list(yp)))
    p = round((sum(1 for a in nulls if a and a >= cv_auc) + 1) / (len(nulls) + 1), 4)

    # fit full LB model, apply to LA (values unknown)
    w, b = logreg(Xs, y)
    la_seqs = X.load_a()[1]
    LF = features(la_seqs)
    la_signs = sorted(s for s in LF if math.exp(LF[s][6]) >= 20)
    LXm = (np.array([LF[s] for s in la_signs]) - mu) / sd
    la_score = LXm @ w + b
    la_prob = 1 / (1 + np.exp(-la_score))
    la_ranked = sorted(zip(la_signs, la_prob), key=lambda t: -t[1])
    top_vowel_candidates = [(s, round(float(pr), 3)) for s, pr in la_ranked[:8]]
    n_vowel_like = int((la_prob >= 0.5).sum())

    out = {
        "LB_cross_validated": {"n_signs": len(signs), "n_vowels": int(y.sum()),
                               "cv_auc_7fold": cv_auc, "permutation_p": p, "n_null": 200,
                               "single_feature_auc_WP1": 0.744},
        "feature_weights": {f: round(float(wi), 3) for f, wi in zip(FEATS, w)},
        "LA_partition": {"n_signs": len(la_signs), "n_vowel_like_prob_ge0.5": n_vowel_like,
                         "top8_vowel_candidates": top_vowel_candidates,
                         "note": "candidate C/V partition from LA-internal distribution only; relative structure, NOT an absolute reading"},
        "verdict": "CV_PARTITION_RECOVERED" if (cv_auc and cv_auc >= 0.8 and p < 0.05) else ("CV_SIGNAL_WEAK" if (cv_auc and p < 0.05) else "NULL"),
        "equivalence_class_reduction": "the ~92-sign value space partitions into vowel-like vs consonant-like classes; external anchors now need to fix representatives per class, not per sign",
    }
    os.makedirs(os.path.join(HERE, "..", "data"), exist_ok=True)
    json.dump({**out, "LA_full_partition": [(s, round(float(pr), 3)) for s, pr in la_ranked]},
              open(os.path.join(HERE, "..", "data", "wp3_cv_recovery.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
