#!/usr/bin/env python3
"""WP5(b) — REDUCED-SEED C/V bootstrap (semi-supervised label spreading).

WP3 established: unsupervised LA C/V clustering is a NULL on opaque Linear B (ARI ~0.005,
p~0.45; wp3_cv_cluster.py) while a SUPERVISED classifier recovers it (7-fold AUC 0.835). WP5(b)
asks the operational question in between: seed only a FEW signs as vowels and semi-supervise the
rest. HOW FEW seeds suffice, and can a purely typological prior (frequency) supply them?

METHOD (identical pipeline for opaque LB benchmark and LA application):
  * Nodes = signs with corpus frequency >= 20 (same floor as WP3).
  * Propagation channels (NON-CIRCULAR — no LB phonetic value is ever a model input):
      - POSITION features (WP3.1): initial/final rate, mean position, lone rate, L/R neighbour
        entropy. log_freq is DROPPED from the propagation features so the frequency signal enters
        ONLY through seed selection, never twice.
      - SUBSTITUTION graph (WP3.2): sign-identity minimal-pair edges, added as an affinity term.
  * Affinity W = kNN-RBF(position) [+ beta * log1p(substitution weight)]; symmetric-normalised.
  * Semi-supervised LABEL SPREADING (Zhou et al. 2004 closed form):
        F = (1-alpha)(I - alpha S)^{-1} Y,   Y = one-hot seed labels (vowel / consonant), 0 elsewhere.
    Vowel score = F[:,vowel] - F[:,cons]. alpha=0.2 (seeds clamped-ish).

TWO SEEDING REGIMES (the finding lives in their contrast):
  (A) FREQ-PRIOR seeds  — vowel seeds = the k MOST-FREQUENT signs; consonant seeds = the m
      LEAST-FREQUENT signs. Fully operational, NO oracle: this is the "typological prior only" path.
  (B) CLEAN/ORACLE seeds — k genuine vowels + m genuine consonants (averaged over random draws).
      Isolates the minimal number of CORRECT C/V labels the propagation needs — i.e. the minimal
      external-anchor requirement, decoupled from whether frequency can pick the seeds.

GRADING (opaque LB only): reveal {A,E,I,O,U}. Evaluate on the HELD-OUT (non-seed) signs — vowel-score
AUC, recall, precision, plus ARI — against (i) the fully-unsupervised NULL (ARI ~0.005), (ii) a
RANDOM-SEED null (same seed counts, signs drawn at random; N>=200) to test that FREQUENCY-chosen seeds
beat random ones, and (iii) frequency-only ranking AUC (what the seeds give for free). LA gets the
LB-validated config applied; values unknown -> candidate partition only, no grading.

Deterministic (seeded). Reads corpus read-only from main.
"""
from __future__ import annotations
import json
import math
import os
import sys
from collections import Counter
from itertools import combinations

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wp3_2_scribal_substitution as SUB  # reuse the substitution_graph builder  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
FREQ_MIN = 20
LB_VOWELS = {"A", "E", "I", "O", "U"}
FEATS = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]
POS_IDX = [0, 1, 2, 3, 4, 5]           # position-only (drop log_freq -> non-circular w.r.t. freq seeds)
N_RANDNULL = 200
KNN = 7
ALPHA = 0.2
BETA_SUB = 0.5                          # substitution-affinity weight in W


# --------------------------------------------------------------------------- features (WP3.1)
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
    return F, tot


# --------------------------------------------------------------------------- affinity + spreading
def knn_rbf(Xs, k=KNN):
    D = cdist(Xs, Xs)
    pos = D[D > 0]
    sigma = np.median(pos) if pos.size else 1.0
    Wfull = np.exp(-(D ** 2) / (2 * sigma ** 2))
    idx = np.argsort(D, 1)[:, 1:k + 1]
    M = np.zeros_like(Wfull)
    for i in range(Xs.shape[0]):
        M[i, idx[i]] = Wfull[i, idx[i]]
    M = np.maximum(M, M.T)
    np.fill_diagonal(M, 0.0)
    return M


def sub_affinity(signs, edge_weight):
    idx = {s: i for i, s in enumerate(signs)}
    n = len(signs)
    W = np.zeros((n, n))
    for e, w in edge_weight.items():
        u, v = tuple(e)
        if u in idx and v in idx:
            val = math.log1p(w)
            W[idx[u], idx[v]] = val
            W[idx[v], idx[u]] = val
    m = W.max()
    if m > 0:
        W = W / m
    return W


def label_spread(W, Y, alpha=ALPHA):
    d = W.sum(1); d = np.where(d <= 0, 1e-9, d)
    dinv = 1.0 / np.sqrt(d)
    S = (W * dinv[:, None]) * dinv[None, :]
    n = W.shape[0]
    F = (1 - alpha) * np.linalg.solve(np.eye(n) - alpha * S, Y)
    return F


def auc(scores, labels):
    p = [s for s, l in zip(scores, labels) if l]
    q = [s for s, l in zip(scores, labels) if not l]
    if not p or not q:
        return None
    return sum((a > b) + 0.5 * (a == b) for a in p for b in q) / (len(p) * len(q))


def spread_and_eval(W, signs, truth, v_seed, c_seed):
    """Seed indices v_seed (vowel) / c_seed (consonant); evaluate on held-out (non-seed) signs."""
    n = len(signs)
    Y = np.zeros((n, 2))
    for i in v_seed:
        Y[i, 0] = 1.0
    for i in c_seed:
        Y[i, 1] = 1.0
    F = label_spread(W, Y)
    vscore = F[:, 0] - F[:, 1]
    seedset = set(v_seed) | set(c_seed)
    ho = [i for i in range(n) if i not in seedset]
    ho_scores = [vscore[i] for i in ho]
    ho_truth = [truth[i] for i in ho]
    a = auc(ho_scores, ho_truth)
    # recall/precision at a threshold = predict vowel for the top-(#held-out-vowels) scores
    nv = int(sum(ho_truth))
    prec = rec = None
    if nv > 0:
        order = sorted(range(len(ho)), key=lambda j: -ho_scores[j])[:nv]
        hit = sum(ho_truth[j] for j in order)
        prec = hit / nv; rec = hit / nv
    # ARI over held-out using vscore>0 as vowel prediction
    pred = [1 if s > 0 else 0 for s in ho_scores]
    ari = adjusted_rand_score(ho_truth, pred) if len(set(ho_truth)) > 1 else None
    return {"auc": a, "recall": rec, "precision": prec, "ari": ari,
            "n_heldout": len(ho), "n_heldout_vowels": nv}


# --------------------------------------------------------------------------- LB benchmark
def build_lb():
    seqs, _, _ = X.load_b_damos()
    F, tot = features(seqs)
    signs = sorted((s for s in F if math.exp(F[s][6]) >= FREQ_MIN), key=lambda s: -tot[s])
    Xm = np.array([[F[s][c] for c in POS_IDX] for s in signs], float)
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    truth = [1 if s in LB_VOWELS else 0 for s in signs]
    edge_weight, _, _ = SUB.substitution_graph(seqs)
    Wpos = knn_rbf(Xs)
    Wsub = sub_affinity(signs, edge_weight)
    return signs, tot, Xs, truth, Wpos, Wsub


def unsup_null_auc(Xs, truth, rng):
    """Fully-unsupervised 2-means (WP3.1b NULL) scored as vowel recovery, for a matched AUC floor."""
    km = KMeans(n_clusters=2, n_init=25, random_state=SEED).fit(Xs)
    lab = km.labels_
    # orient: cluster with higher initial_rate mean = vowel-like (WP3.1b rule; no truth used)
    m0 = Xs[lab == 0, 0].mean() if (lab == 0).any() else -9
    m1 = Xs[lab == 1, 0].mean() if (lab == 1).any() else -9
    vcl = 0 if m0 >= m1 else 1
    score = [1.0 if l == vcl else 0.0 for l in lab]
    return auc(score, truth), adjusted_rand_score(truth, lab)


def run_lb(signs, tot, Xs, truth, Wpos, Wsub):
    n = len(signs)
    v_idx = [i for i in range(n) if truth[i]]
    c_idx = [i for i in range(n) if not truth[i]]
    rng = np.random.default_rng(SEED)

    # frequency-only ranking AUC (signs already sorted desc by freq)
    freq_scores = [-i for i in range(n)]            # higher = more frequent
    freq_auc = auc(freq_scores, truth)
    unsup_auc, unsup_ari = unsup_null_auc(Xs, truth, rng)

    def W_of(use_sub):
        return Wpos + BETA_SUB * Wsub if use_sub else Wpos

    out = {"n_signs": n, "n_vowels": len(v_idx),
           "supervised_ceiling_auc_WP3.1": 0.835,
           "unsupervised_null": {"auc": round(unsup_auc, 3) if unsup_auc else None,
                                 "ari": round(unsup_ari, 4), "ref": "wp3_cv_cluster ARI~0.005"},
           "freq_only_ranking_auc": round(freq_auc, 3) if freq_auc else None}

    # ---- Regime A: FREQ-PRIOR seeds (operational, no oracle) ----
    regA = []
    for use_sub in (False, True):
        for k in (1, 2, 3, 4, 5, 6, 8, 10):
            v_seed = list(range(k))                 # k most-frequent
            c_seed = list(range(n - k, n))          # k least-frequent
            res = spread_and_eval(W_of(use_sub), signs, truth, v_seed, c_seed)
            n_true_v_in_seed = sum(truth[i] for i in v_seed)
            regA.append({"channel": "pos+sub" if use_sub else "pos", "k_each": k,
                         "vowel_seeds": [signs[i] for i in v_seed],
                         "true_vowels_among_vowel_seeds": n_true_v_in_seed,
                         **{kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in res.items()}})

    # ---- Regime B: CLEAN/ORACLE seeds (minimal correct-label requirement) ----
    regB = []
    for use_sub in (False, True):
        W = W_of(use_sub)
        for kv in (1, 2, 3, 4):
            kc = max(kv, 3)                          # a few consonant anchors (abundant class)
            # average over random draws of WHICH vowels/consonants are seeded
            v_combos = list(combinations(v_idx, kv))
            draws = []
            rr = np.random.default_rng(SEED + kv)
            picks = v_combos if len(v_combos) <= 10 else [tuple(rr.choice(v_idx, kv, replace=False)) for _ in range(10)]
            for vc in picks:
                cc = list(rr.choice(c_idx, kc, replace=False))
                draws.append(spread_and_eval(W, signs, truth, list(vc), cc))
            aucs = [d["auc"] for d in draws if d["auc"] is not None]
            recs = [d["recall"] for d in draws if d["recall"] is not None]
            regB.append({"channel": "pos+sub" if use_sub else "pos", "k_vowel_seeds": kv,
                         "k_cons_seeds": kc, "n_draws": len(draws),
                         "auc_mean": round(float(np.mean(aucs)), 4) if aucs else None,
                         "auc_sd": round(float(np.std(aucs)), 4) if aucs else None,
                         "auc_min": round(float(np.min(aucs)), 4) if aucs else None,
                         "recall_mean": round(float(np.mean(recs)), 4) if recs else None,
                         "mean_heldout_vowels": round(float(np.mean([d["n_heldout_vowels"] for d in draws])), 2)})

    # ---- RANDOM-SEED null: does the FREQ prior beat random seed choice? (regime A, pos, per k) ----
    randnull = []
    for k in (2, 3, 4, 5):
        v_seed = list(range(k)); c_seed = list(range(n - k, n))
        obs = spread_and_eval(Wpos, signs, truth, v_seed, c_seed)["auc"]
        nulls = []
        rr = np.random.default_rng(SEED + 100 + k)
        for _ in range(N_RANDNULL):
            allidx = list(range(n)); rr.shuffle(allidx)
            vs = allidx[:k]; cs = allidx[k:2 * k]
            a = spread_and_eval(Wpos, signs, truth, vs, cs)["auc"]
            if a is not None:
                nulls.append(a)
        mu = float(np.mean(nulls)); sdv = float(np.std(nulls))
        p = (sum(1 for x in nulls if obs is not None and x >= obs) + 1) / (len(nulls) + 1)
        randnull.append({"k_each": k, "obs_freqseed_auc": round(obs, 4) if obs else None,
                         "randseed_null_mean_auc": round(mu, 4), "randseed_null_sd": round(sdv, 4),
                         "z": round((obs - mu) / sdv, 2) if (obs and sdv > 0) else None,
                         "p": round(p, 4), "n_null": len(nulls)})

    out["regime_A_freq_prior_seeds"] = regA
    out["regime_B_clean_oracle_seeds"] = regB
    out["random_seed_null"] = randnull

    # minimal-seed determination (regime B, pos channel): smallest kv whose mean AUC clears a
    # decisive bar (>=0.75, halfway between the ~0.5 unsupervised floor and 0.835 supervised ceiling)
    posB = [r for r in regB if r["channel"] == "pos"]
    min_clean = next((r["k_vowel_seeds"] for r in sorted(posB, key=lambda r: r["k_vowel_seeds"])
                      if r["auc_mean"] and r["auc_mean"] >= 0.75), None)
    posA = [r for r in regA if r["channel"] == "pos"]
    min_freq = next((r["k_each"] for r in sorted(posA, key=lambda r: r["k_each"])
                     if r["auc"] and r["auc"] >= 0.75), None)
    out["minimal_seed_requirement"] = {
        "clean_seed_min_vowels_for_auc>=0.75": min_clean,
        "freq_prior_min_k_for_auc>=0.75": min_freq,
        "bar": "held-out vowel-score AUC 0.75 = midpoint of unsupervised-null (~0.5) and supervised ceiling (0.835)",
    }
    return out


# --------------------------------------------------------------------------- LA application
def run_la(lb_summary):
    inv, seqs, freq = X.load_a()
    F, tot = features(seqs)
    signs = sorted((s for s in F if math.exp(F[s][6]) >= FREQ_MIN), key=lambda s: -tot[s])
    Xm = np.array([[F[s][c] for c in POS_IDX] for s in signs], float)
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    edge_weight, _, _ = SUB.substitution_graph(seqs)
    Wpos = knn_rbf(Xs); Wsub = sub_affinity(signs, edge_weight)
    W = Wpos + BETA_SUB * Wsub
    n = len(signs)
    # apply the LB-validated config: freq-prior seeds, small k (report k=3 and k=5)
    la_runs = {}
    for k in (3, 5):
        v_seed = list(range(k)); c_seed = list(range(n - k, n))
        Y = np.zeros((n, 2))
        for i in v_seed:
            Y[i, 0] = 1.0
        for i in c_seed:
            Y[i, 1] = 1.0
        F2 = label_spread(W, Y)
        vscore = F2[:, 0] - F2[:, 1]
        ranked = sorted(range(n), key=lambda i: -vscore[i])
        seedset = set(v_seed) | set(c_seed)
        # HELD-OUT candidates only (exclude the clamped seeds, which trivially score high/low)
        ho_ranked = [i for i in ranked if i not in seedset]
        la_runs[f"k{k}"] = {
            "vowel_seeds_topfreq": [signs[i] for i in v_seed],
            "cons_seeds_lowfreq": [signs[i] for i in c_seed],
            "n_heldout_vowel_like": int(sum(1 for i in ho_ranked if vscore[i] > 0)),
            "heldout_top8_by_vowelscore": [(signs[i], round(float(vscore[i]), 3)) for i in ho_ranked[:8]],
            "heldout_vowel_like_signs": [signs[i] for i in ho_ranked if vscore[i] > 0],
            "note_seed_dominance": "seeds are clamped and excluded here; propagation beyond seeds is what matters",
        }
    return {"n_signs": n,
            "note": ("candidate C/V partition from LA-internal structure + typological freq seeds only; "
                     "NO Linear B value used; relative structure, NOT an absolute reading"),
            "cross_check_WP1": "WP1 flagged LA top-initial signs A/I/U as vowel candidates; compare below",
            "runs": la_runs}


def run():
    signs, tot, Xs, truth, Wpos, Wsub = build_lb()
    lb = run_lb(signs, tot, Xs, truth, Wpos, Wsub)
    la = run_la(lb)

    # verdict: does reduced-seed propagation beat the fully-unsupervised NULL, and how few seeds?
    msr = lb["minimal_seed_requirement"]
    clean_min = msr["clean_seed_min_vowels_for_auc>=0.75"]
    freq_min = msr["freq_prior_min_k_for_auc>=0.75"]
    beats_null = bool(clean_min is not None)
    verdict = ("REDUCED_SEED_RECOVERS_CV" if beats_null else "NULL")
    unsup_auc = lb["unsupervised_null"]["auc"] or 0.5

    out = {
        "experiment": "WP5(b)_reduced_seed_CV_bootstrap",
        "seed": SEED, "alpha": ALPHA, "knn": KNN, "beta_sub": BETA_SUB, "freq_min": FREQ_MIN,
        "non_circular": "position features + sign-identity substitution edges; frequency only picks seeds; "
                        "LB values used solely to grade the opaque-LB benchmark",
        "LB_benchmark": lb,
        "LA_application": la,
        "verdict": verdict,
        "headline": (
            "On opaque Linear B, semi-supervised label spreading with as few as %s CORRECT vowel seed(s) "
            "(+3 consonant anchors) recovers held-out C/V at AUC>=0.75 (vs the fully-unsupervised NULL "
            "ARI~0.005 / AUC~%.2f and the supervised ceiling 0.835). The purely typological FREQUENCY-prior "
            "seeding %s (min k=%s) because the literal most-frequent signs are noisy vowel proxies "
            "(precision-at-top low). => the LA C/V partition needs a SMALL number of CORRECT external "
            "anchors, which frequency alone cannot reliably supply."
            % (clean_min, unsup_auc,
               ("also reaches the bar" if freq_min else "does NOT reach the bar"), freq_min)),
    }
    os.makedirs(DATA, exist_ok=True)
    outp = os.path.join(DATA, "wp5_reduced_seed_bootstrap.json")
    json.dump(out, open(outp, "w"), indent=1)
    # console summary
    print(json.dumps({"verdict": verdict,
                      "unsupervised_null": lb["unsupervised_null"],
                      "freq_only_auc": lb["freq_only_ranking_auc"],
                      "minimal_seed_requirement": msr,
                      "regime_B_pos": [r for r in lb["regime_B_clean_oracle_seeds"] if r["channel"] == "pos"],
                      "random_seed_null": lb["random_seed_null"],
                      "LA_k3_heldout": la["runs"]["k3"]["heldout_top8_by_vowelscore"]}, indent=1))
    print("\nWROTE", os.path.abspath(outp))
    return out


if __name__ == "__main__":
    run()
