#!/usr/bin/env python3
"""A3 — THREE independent replications of "does internal structure recover C/V on opaque LB".

Audits the Foundry WP1/WP3 claim (single-feature position AUC 0.744; 7-feature 7-fold CV AUC 0.835).
Three genuinely distinct implementations that do NOT share all decisive assumptions:

  A_MODEL_1  supervised position/distribution classifier (sklearn logistic, grouped-by-sign 7-fold CV,
             roc_auc, label-permutation null). Reimplemented cleanly; ablations expose the log_freq confound.
  A_MODEL_2  UNSUPERVISED Bayesian latent 2-class model (2-component Gaussian mixture, EM). Labels used
             ONLY to score the latent partition (AUC of vowel-component posterior + adjusted Rand).
  A_MODEL_3  UNSUPERVISED 2-state HMM over sign SEQUENCES (Baum-Welch, hand-implemented). Per-sign state
             posterior -> C/V alignment scored the same way (AUC + ARI).

Non-circular: known LB vowel labels grade the benchmark ONLY; they are never a model input.
Deterministic seed 20260708. Writes data/A3_replications.json.
"""
import json
import math
import os
import sys
from collections import Counter

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.mixture import GaussianMixture
from sklearn.metrics import roc_auc_score, adjusted_rand_score

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
LB_VOWELS = {"A", "E", "I", "O", "U"}
LA_PURE_VOWELS = {"A", "I", "U", "E", "O"}  # AB08/28/10/38/61 pure-vowel signs (benchmark only)
FEATS = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]
POS_FEATS = [f for f in FEATS if f != "log_freq"]  # position/distribution only (no frequency)
MIN_FREQ = 20


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
    """AUC after orienting the score toward the positive class (the unsupervised-scoring convention)."""
    a = roc_auc_score(labels, scores)
    return max(a, 1.0 - a)


# ---------------------------------------------------------------- A_MODEL_1: supervised discriminative
def model1(F, signs, y, feat_names, n_perm=1000, k=7, seed=SEED):
    Xm = matrix(F, signs, feat_names)
    mu, sd = Xm.mean(0), Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    rng = np.random.RandomState(seed)
    order = rng.permutation(len(signs))
    folds = [order[i::k] for i in range(k)]  # grouped by SIGN (each sign in exactly one held-out fold)

    def cv_oof(labels):
        oof = np.zeros(len(signs))
        for te in folds:
            tr = np.array([i for i in range(len(signs)) if i not in set(te.tolist())])
            clf = LogisticRegression(C=1.0, max_iter=2000)
            # need both classes in the training fold
            if len(set(labels[tr].tolist())) < 2:
                oof[te] = 0.0
                continue
            clf.fit(Xs[tr], labels[tr])
            oof[te] = clf.decision_function(Xs[te])
        return oof

    oof = cv_oof(y)
    cv_auc = float(roc_auc_score(y, oof))
    # label-permutation null (refit CV each shuffle) — oriented to match a two-sided detector
    rp = np.random.RandomState(seed + 1)
    nulls = []
    for _ in range(n_perm):
        yp = rp.permutation(y)
        nulls.append(oriented_auc(cv_oof(yp), yp))
    perm_p = float((sum(1 for a in nulls if a >= cv_auc) + 1) / (n_perm + 1)) if n_perm else None
    null_mean = round(float(np.mean(nulls)), 3) if nulls else None
    null_95 = round(float(np.percentile(nulls, 95)), 3) if nulls else None
    # full-fit weights + per-sign probability (reusable prediction)
    clf = LogisticRegression(C=1.0, max_iter=2000).fit(Xs, y)
    prob = clf.predict_proba(Xs)[:, 1]
    return {
        "cv_auc_7fold": round(cv_auc, 3), "perm_p": perm_p, "n_perm": n_perm,
        "null_auc_mean": null_mean, "null_auc_95pct": null_95,
        "weights": {f: round(float(w), 3) for f, w in zip(feat_names, clf.coef_[0])},
        "mu": mu.tolist(), "sd": sd.tolist(), "feat_names": feat_names,
        "per_sign_prob": {s: round(float(p), 4) for s, p in zip(signs, prob)},
        "per_sign_oof": {s: round(float(v), 4) for s, v in zip(signs, oof)},
    }


def jackknife_vowels(F, signs, y, feat_names, k=7, seed=SEED):
    """Fragility of the 5-positive CV-AUC: drop each true vowel in turn, recompute CV-AUC."""
    vw = [s for s in signs if s in LB_VOWELS]
    out = {}
    for drop in vw:
        keep = [s for s in signs if s != drop]
        yk = np.array([1.0 if s in LB_VOWELS else 0.0 for s in keep])
        out[drop] = model1(F, keep, yk, feat_names, n_perm=0, k=k, seed=seed)["cv_auc_7fold"]
    vals = list(out.values())
    return {"drop_one_vowel_cv_auc": out, "min": min(vals), "max": max(vals),
            "range": round(max(vals) - min(vals), 3)}


# ---------------------------------------------------------------- A_MODEL_2: unsupervised GMM
def model2(F, signs, y, feat_names, n_perm=5000, seed=SEED):
    Xm = matrix(F, signs, feat_names)
    Xs = (Xm - Xm.mean(0)) / (Xm.std(0) + 1e-9)
    gm = GaussianMixture(n_components=2, covariance_type="full", n_init=20, random_state=seed).fit(Xs)
    post = gm.predict_proba(Xs)          # (n,2)
    hard = gm.predict(Xs)
    # orient: component with the higher TRUE-vowel fraction = the 'vowel' component (scoring only)
    v0 = y[hard == 0].mean() if (hard == 0).any() else 0.0
    v1 = y[hard == 1].mean() if (hard == 1).any() else 0.0
    vcomp = 1 if v1 >= v0 else 0
    vscore = post[:, vcomp]
    auc = oriented_auc(vscore, y)
    ari = adjusted_rand_score(y.astype(int), hard)
    # nulls (model fixed, shuffle labels — replicate orientation freedom)
    rp = np.random.RandomState(seed + 2)
    null_auc = []; null_ari = []
    for _ in range(n_perm):
        yp = rp.permutation(y)
        null_auc.append(oriented_auc(post[:, vcomp], yp))
        null_ari.append(adjusted_rand_score(yp.astype(int), hard))
    p_auc = float((sum(1 for a in null_auc if a >= auc) + 1) / (n_perm + 1))
    p_ari = float((sum(1 for a in null_ari if a >= ari) + 1) / (n_perm + 1))
    comp_sizes = [int((hard == 0).sum()), int((hard == 1).sum())]
    return {
        "auc": round(float(auc), 3), "perm_p_auc": round(p_auc, 4),
        "ari": round(float(ari), 3), "perm_p_ari": round(p_ari, 4),
        "component_sizes": comp_sizes, "vowel_component": int(vcomp),
        "vowels_in_vowel_component": int((y[hard == vcomp]).sum()),
        "null_auc_95pct": round(float(np.percentile(null_auc, 95)), 3),
        "per_sign_vscore": {s: round(float(v), 4) for s, v in zip(signs, vscore)},
        "per_sign_hard": {s: int(h) for s, h in zip(signs, hard)},
    }


# ---------------------------------------------------------------- A_MODEL_3: unsupervised 2-state HMM
def hmm_baum_welch(seqs, sym2i, n_states=2, n_iter=60, n_init=6, seed=SEED):
    V = len(sym2i)
    seqs_i = [[sym2i[s] for s in w if s in sym2i] for w in seqs]
    seqs_i = [w for w in seqs_i if len(w) >= 1]
    best = None
    for init in range(n_init):
        rng = np.random.RandomState(seed + init)
        pi = rng.dirichlet(np.ones(n_states))
        A = rng.dirichlet(np.ones(n_states), size=n_states)
        B = rng.dirichlet(np.ones(V) * 0.5, size=n_states)
        ll_prev = -np.inf
        for _ in range(n_iter):
            pi_num = np.zeros(n_states); A_num = np.zeros((n_states, n_states))
            A_den = np.zeros(n_states); B_num = np.zeros((n_states, V)); B_den = np.zeros(n_states)
            ll = 0.0
            for w in seqs_i:
                T = len(w)
                # forward with scaling
                alpha = np.zeros((T, n_states)); c = np.zeros(T)
                alpha[0] = pi * B[:, w[0]]; c[0] = alpha[0].sum() + 1e-300; alpha[0] /= c[0]
                for t in range(1, T):
                    alpha[t] = (alpha[t - 1] @ A) * B[:, w[t]]
                    c[t] = alpha[t].sum() + 1e-300; alpha[t] /= c[t]
                ll += np.log(c).sum()
                # backward
                beta = np.zeros((T, n_states)); beta[T - 1] = 1.0 / c[T - 1]
                for t in range(T - 2, -1, -1):
                    beta[t] = (A @ (B[:, w[t + 1]] * beta[t + 1])) / c[t]
                gamma = alpha * beta; gamma /= (gamma.sum(1, keepdims=True) + 1e-300)
                pi_num += gamma[0]
                for t in range(T):
                    B_num[:, w[t]] += gamma[t]; B_den += gamma[t]
                for t in range(T - 1):
                    xi = (alpha[t][:, None] * A * (B[:, w[t + 1]] * beta[t + 1])[None, :])
                    xi /= (xi.sum() + 1e-300)
                    A_num += xi; A_den += gamma[t]
            pi = pi_num / (pi_num.sum() + 1e-300)
            A = A_num / (A_den[:, None] + 1e-300)
            B = B_num / (B_den[:, None] + 1e-300)
            if ll - ll_prev < 1e-3:
                ll_prev = ll; break
            ll_prev = ll
        if best is None or ll_prev > best[0]:
            best = (ll_prev, pi, A, B)
    return best  # (loglik, pi, A, B)


def model3(seqs, signs, y, n_perm=5000, seed=SEED):
    # emission vocabulary = ALL signs seen (rare signs kept as their own symbol)
    allsyms = sorted({s for w in seqs for s in w})
    sym2i = {s: i for i, s in enumerate(allsyms)}
    ll, pi, A, B = hmm_baum_welch(seqs, sym2i, n_states=2, seed=seed)
    # per-sign state posterior via expected emission counts already in B, but we want P(state|sign):
    # P(state|sign) proportional to freq_state_emits_sign = colcount. Use B (P(sign|state)) * state occupancy.
    # occupancy = stationary-ish weight = average gamma per state, approx via B row sums weighting.
    # Compute expected state occupancy from a forward pass aggregate:
    occ = np.zeros(2); symstate = np.zeros((2, len(allsyms)))
    for w in seqs:
        wi = [sym2i[s] for s in w]
        T = len(wi)
        alpha = np.zeros((T, 2)); c = np.zeros(T)
        alpha[0] = pi * B[:, wi[0]]; c[0] = alpha[0].sum() + 1e-300; alpha[0] /= c[0]
        for t in range(1, T):
            alpha[t] = (alpha[t - 1] @ A) * B[:, wi[t]]; c[t] = alpha[t].sum() + 1e-300; alpha[t] /= c[t]
        beta = np.zeros((T, 2)); beta[T - 1] = 1.0 / c[T - 1]
        for t in range(T - 2, -1, -1):
            beta[t] = (A @ (B[:, wi[t + 1]] * beta[t + 1])) / c[t]
        gamma = alpha * beta; gamma /= (gamma.sum(1, keepdims=True) + 1e-300)
        for t in range(T):
            symstate[:, wi[t]] += gamma[t]; occ += gamma[t]
    # P(state|sign)
    pstate_sign = symstate / (symstate.sum(0, keepdims=True) + 1e-300)  # (2, V)
    idx = [sym2i[s] for s in signs]
    p1 = pstate_sign[1, idx]  # P(state1 | sign)
    # orient state->vowel by true-vowel fraction (scoring only)
    hard = (p1 >= 0.5).astype(int)
    v0 = y[hard == 0].mean() if (hard == 0).any() else 0.0
    v1 = y[hard == 1].mean() if (hard == 1).any() else 0.0
    vstate = 1 if v1 >= v0 else 0
    vscore = p1 if vstate == 1 else (1 - p1)
    auc = oriented_auc(vscore, y)
    hardv = (vscore >= 0.5).astype(int)
    ari = adjusted_rand_score(y.astype(int), hardv)
    rp = np.random.RandomState(seed + 3)
    null_auc = []; null_ari = []
    for _ in range(n_perm):
        yp = rp.permutation(y)
        null_auc.append(oriented_auc(vscore, yp))
        null_ari.append(adjusted_rand_score(yp.astype(int), hardv))
    p_auc = float((sum(1 for a in null_auc if a >= auc) + 1) / (n_perm + 1))
    p_ari = float((sum(1 for a in null_ari if a >= ari) + 1) / (n_perm + 1))
    return {
        "loglik": round(float(ll), 1), "auc": round(float(auc), 3), "perm_p_auc": round(p_auc, 4),
        "ari": round(float(ari), 3), "perm_p_ari": round(p_ari, 4),
        "state_sizes": [int((hardv == 0).sum()), int((hardv == 1).sum())],
        "vowels_in_vowel_state": int(y[hardv == 1].sum()),
        "null_auc_95pct": round(float(np.percentile(null_auc, 95)), 3),
        "per_sign_vscore": {s: round(float(v), 4) for s, v in zip(signs, vscore)},
    }


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    return float((ra @ rb) / (np.sqrt((ra @ ra) * (rb @ rb)) + 1e-12))


def run():
    lb_seqs, _, _ = X.load_b_damos()
    F = features(lb_seqs)
    signs = sorted(s for s in F if F[s]["freq"] >= MIN_FREQ)          # honest integer threshold -> 77
    y = np.array([1.0 if s in LB_VOWELS else 0.0 for s in signs])
    print(f"[data] LB wordforms={len(lb_seqs)} signs(freq>={MIN_FREQ})={len(signs)} vowels={int(y.sum())}")

    # ---- A_MODEL_1 (+ ablations exposing the log_freq confound) ----
    print("[M1] supervised classifier + ablations ...")
    m1_all = model1(F, signs, y, FEATS)
    m1_pos = model1(F, signs, y, POS_FEATS)                            # position-only (no frequency)
    m1_freq = model1(F, signs, y, ["log_freq"])                        # frequency-only typological prior
    m1_jack = jackknife_vowels(F, signs, y, FEATS)

    # ---- A_MODEL_2 (unsupervised GMM) ----
    print("[M2] unsupervised GMM (EM) ...")
    m2_all = model2(F, signs, y, FEATS)
    m2_pos = model2(F, signs, y, POS_FEATS)

    # ---- A_MODEL_3 (unsupervised HMM over sequences) ----
    print("[M3] unsupervised 2-state HMM (Baum-Welch) ...")
    m3 = model3(lb_seqs, signs, y)

    # ---- agreement across models (per-sign vowel scores) ----
    s1 = np.array([m1_all["per_sign_prob"][s] for s in signs])
    s2 = np.array([m2_all["per_sign_vscore"][s] for s in signs])
    s3 = np.array([m3["per_sign_vscore"][s] for s in signs])
    agree = {
        "spearman_M1_M2": round(spearman(s1, s2), 3),
        "spearman_M1_M3": round(spearman(s1, s3), 3),
        "spearman_M2_M3": round(spearman(s2, s3), 3),
    }
    # do the 5 true vowels rank in top-K of each model?
    def vowel_ranks(scores):
        order = sorted(range(len(signs)), key=lambda i: -scores[i])
        rank = {signs[order.index(i)] if False else s: order.index(i) + 1
                for i, s in enumerate(signs)}
        return {s: rank[s] for s in signs if s in LB_VOWELS}
    vr = {"M1": vowel_ranks(s1), "M2": vowel_ranks(s2), "M3": vowel_ranks(s3)}

    # ---- apply each model to Linear A (candidate partition; reusable, no LA ground truth used) ----
    la_seqs = X.load_a()[1]
    LF = features(la_seqs)
    la_signs = sorted(s for s in LF if LF[s]["freq"] >= MIN_FREQ)
    # M1: standardize LA with LB stats, apply LB-fit weights (reuse full-fit)
    clf_scores = {}
    Xla = matrix(LF, la_signs, FEATS)
    Xla_s = (Xla - np.array(m1_all["mu"])) / np.array(m1_all["sd"])
    w = np.array([m1_all["weights"][f] for f in FEATS])
    # recover intercept by refit (weights already from full fit); use logistic on LB to get intercept
    Xlb = matrix(F, signs, FEATS); Xlb_s = (Xlb - np.array(m1_all["mu"])) / np.array(m1_all["sd"])
    clf = LogisticRegression(C=1.0, max_iter=2000).fit(Xlb_s, y)
    la_prob = clf.predict_proba(Xla_s)[:, 1]
    m1_la = {s: round(float(p), 4) for s, p in zip(la_signs, la_prob)}
    la_bench = {s: (s in LA_PURE_VOWELS) for s in la_signs}
    m1_la_auc = None
    if any(la_bench.values()) and not all(la_bench.values()):
        yl = np.array([1.0 if la_bench[s] else 0.0 for s in la_signs])
        m1_la_auc = round(float(oriented_auc(la_prob, yl)), 3)

    out = {
        "meta": {"seed": SEED, "lb_wordforms": len(lb_seqs), "n_signs": len(signs),
                 "n_vowels": int(y.sum()), "min_freq": MIN_FREQ, "feats": FEATS,
                 "note": "known LB/LA vowel values used for SCORING ONLY, never as model input"},
        "A_MODEL_1_supervised": {
            "all_features": m1_all, "position_only_no_freq": m1_pos, "log_freq_only": m1_freq,
            "vowel_jackknife_fragility": m1_jack,
            "ablation_summary_auc": {"all": m1_all["cv_auc_7fold"],
                                     "position_only": m1_pos["cv_auc_7fold"],
                                     "log_freq_only": m1_freq["cv_auc_7fold"]},
        },
        "A_MODEL_2_gmm_unsupervised": {"all_features": m2_all, "position_only_no_freq": m2_pos},
        "A_MODEL_3_hmm_unsupervised": m3,
        "agreement": {"spearman": agree, "true_vowel_ranks": vr,
                      "n_signs_ranked": len(signs)},
        "LA_application": {"n_signs": len(la_signs), "m1_probs": m1_la,
                           "m1_vs_ABvowel_benchmark_auc": m1_la_auc,
                           "note": "relative-structure candidate partition; LA benchmark AUC is a circular check, not training"},
    }
    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(os.path.join(DATA, "A3_replications.json"), "w"), indent=1)
    print(json.dumps({
        "M1_all_auc": m1_all["cv_auc_7fold"], "M1_all_p": m1_all["perm_p"],
        "M1_pos_auc": m1_pos["cv_auc_7fold"], "M1_pos_p": m1_pos["perm_p"],
        "M1_freq_auc": m1_freq["cv_auc_7fold"], "M1_freq_p": m1_freq["perm_p"],
        "M1_jack_range": m1_jack["range"], "M1_jack_min": m1_jack["min"],
        "M2_all_auc": m2_all["auc"], "M2_all_p_auc": m2_all["perm_p_auc"], "M2_all_ari": m2_all["ari"],
        "M2_all_p_ari": m2_all["perm_p_ari"], "M2_comp_sizes": m2_all["component_sizes"],
        "M2_pos_auc": m2_pos["auc"], "M2_pos_p_auc": m2_pos["perm_p_auc"], "M2_pos_ari": m2_pos["ari"],
        "M3_auc": m3["auc"], "M3_p_auc": m3["perm_p_auc"], "M3_ari": m3["ari"], "M3_p_ari": m3["perm_p_ari"],
        "M3_state_sizes": m3["state_sizes"],
        "agree_spearman": agree, "true_vowel_ranks": vr, "M1_LA_bench_auc": m1_la_auc,
    }, indent=1))
    return out


if __name__ == "__main__":
    run()
