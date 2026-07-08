#!/usr/bin/env python3
"""EPOCH-016 — SBI pilot (frontier F9, gate A): simulation-based inference for
VALUE-CLASS recovery, KNOWN-script calibration ONLY.

Question: can an amortized SBI estimator (neural pair-posterior trained on a
generative admin-syllabary simulator) recover relative sign value-CLASS structure
(consonant rows / vowel columns of the CV grid — gauge-invariant, scored by ARI)
at LA-scale corpora and LA anchor budgets (0/3/5), where G-surface-style anchor
geometry failed (E003/E006)?

Calibration targets:
  - held-out in-distribution simulations (positive controls PC-A ample / PC-B LA-scale)
  - painted-label structure-free simulations (negative/leakage control)
  - wrong-prior misspecification test (must fail VISIBLY, via OOD flag)
  - VERDICT: opaque Linear B (DAMOS) degraded to LA token scale, vs baselines
    BASE_SPEC (raw-affinity spectral), BASE_M1 (anchor-profile geometry, the
    E003 G-surface estimator analogue), BASE_GW (entropic GW to a grid template,
    the E006-best estimator analogue), at anchor budgets b in {0,3,5}.

LINEAR A IS NEVER LOADED by this script. Claim layer L2. Licences unchanged.
Seed 20260708 (frozen). All hyperparameters frozen in prereg; zero tuning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import warnings
from collections import Counter, defaultdict

import numpy as np

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
OUT = os.path.join(CAMP, "data", "sbi_pilot")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

SEED = 20260708
LA_TOKEN_SCALE = 5792          # measured LA sign-token count (silver, words)
AMPLE_SCALE = 5 * LA_TOKEN_SCALE
CORE_RE = re.compile(r"^[DJKMNPQRSTWZ]?[AEIOU]$")
MIN_SIGN_FREQ = 3
N_TRAIN = 200                  # training sims per prior (true / wrong)
N_HELD = 20                    # held-out sims per control condition
R_LB = 20                      # LB degradation replicates
BUDGETS = [0, 3, 5]
ANCHOR_POOL_TOP = 30           # anchors drawn from top-30 frequent kept signs
N_PERM = 10000                 # sign-flip permutations for paired diffs
MARGIN = 0.05                  # material ARI margin for BEATS/UNDERPERFORMS
PC_A_BAR = 0.40                # PC-A (ample-scale) mean ARI_C bar
NEG_BAR = 0.05                 # negative-control |mean ARI| leak bar
MISSPEC_DROP = 0.10            # ARI drop defining a misspec "failure"
OOD_FLAG_FRAC = 0.50           # >= this fraction of corpora flagged => VISIBLE
MAX_TRAIN_PAIRS = 400000

FEATURE_NAMES = [
    "cos1", "cosL", "cosR", "cos2",
    "mp_final", "mp_nonfinal", "pos_sim",
    "freq_ratio", "logfreq_absdiff", "logfreq_sum",
    "final_share_absdiff", "init_share_absdiff",
]


def rng_for(*key) -> np.random.Generator:
    h = hashlib.sha256(("E016|" + "|".join(map(str, key)) + f"|{SEED}").encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "big"))


# ---------------------------------------------------------------------------
# 1. Generative simulator of admin-syllabary corpora
# ---------------------------------------------------------------------------

def draw_theta(rng: np.random.Generator, wrong: bool = False) -> dict:
    """Prior over simulator parameters. TRUE prior matched to LA/LB measured
    stats; WRONG prior = the preregistered misspecification (shifted Zipf, no
    harmony, near-no paradigms, too-short words)."""
    th = {
        "C": int(rng.integers(10, 15)),          # consonant rows incl. null row
        "V": int(rng.integers(4, 6)),            # vowel columns
        "zipf_c": float(rng.uniform(0.6, 1.0)),  # matched: LA .78 / LB .80
        "zipf_v": float(rng.uniform(0.4, 0.9)),
        "zipf_lex": float(rng.uniform(0.8, 1.2)),
        "wlen_mean": float(rng.uniform(1.6, 3.4)),  # spans LA 1.84 .. LB 3.23
        "harmony": float(rng.uniform(0.0, 0.5)),
        "paradigm": float(rng.uniform(0.25, 0.6)),
        "formula_rate": float(rng.uniform(0.05, 0.4)),
        "n_sites": int(rng.integers(3, 11)),
        "site_alpha": float(np.exp(rng.uniform(np.log(0.25), np.log(2.0)))),
        "n_lemmas": int(rng.integers(300, 901)),
        "words_per_doc": float(rng.uniform(1.5, 4.0)),  # LA mean 2.35
    }
    if wrong:
        th["zipf_c"] = float(rng.uniform(1.4, 1.8))
        th["harmony"] = 0.0
        th["paradigm"] = float(rng.uniform(0.0, 0.1))
        th["wlen_mean"] = float(rng.uniform(1.2, 1.6))
    return th


def simulate(theta: dict, token_budget: int, rng: np.random.Generator):
    """Generate a corpus: list of word tokens (tuples of opaque sign ids) plus
    ground-truth labels sign_id -> (row, col). Sign id = row*V + col (opaque to
    all estimators; labels are used ONLY for scoring)."""
    C, V = theta["C"], theta["V"]
    wc = (np.arange(1, C + 1, dtype=float) ** -theta["zipf_c"])
    wc /= wc.sum()
    wv = (np.arange(1, V + 1, dtype=float) ** -theta["zipf_v"])
    wv /= wv.sum()
    # random rank->identity permutations so frequency rank is not the label
    perm_c = rng.permutation(C)
    perm_v = rng.permutation(V)
    p_wlen = 1.0 / max(theta["wlen_mean"], 1.05)

    def new_stem():
        L = int(min(rng.geometric(p_wlen), 8))  # support >=1, mean = wlen_mean
        cs = perm_c[rng.choice(C, size=L, p=wc)]
        vs = np.empty(L, dtype=int)
        for t in range(L):
            if t > 0 and rng.random() < theta["harmony"]:
                vs[t] = vs[t - 1]
            else:
                vs[t] = perm_v[rng.choice(V, p=wv)]
        return list(zip(cs.tolist(), vs.tolist()))

    lemmas = []
    for _ in range(theta["n_lemmas"]):
        stem = new_stem()
        variants = [stem]
        if len(stem) >= 1 and rng.random() < theta["paradigm"]:
            # final-vowel alternation paradigm (plants the same-CONSONANT signal)
            c_last = stem[-1][0]
            n_alt = int(rng.integers(1, 3))
            alt_vs = rng.choice(V, size=min(n_alt, V), replace=False)
            for av in alt_vs:
                v2 = int(perm_v[av])
                if v2 != stem[-1][1]:
                    variants.append(stem[:-1] + [(c_last, v2)])
        lemmas.append(variants)
    lw = (np.arange(1, len(lemmas) + 1, dtype=float) ** -theta["zipf_lex"])
    lw /= lw.sum()
    lemma_order = rng.permutation(len(lemmas))

    n_sites = theta["n_sites"]
    site_w = rng.dirichlet(np.full(n_sites, theta["site_alpha"]))
    # per-site lemma re-weighting (site imbalance in vocabulary)
    site_boost = rng.dirichlet(np.full(len(lemmas), 50.0), size=n_sites)
    headers = rng.choice(len(lemmas), size=(n_sites, 2))

    words = []
    tokens = 0
    while tokens < token_budget:
        s = int(rng.choice(n_sites, p=site_w))
        pw = 0.5 * lw + 0.5 * site_boost[s]
        pw /= pw.sum()
        ndw = 1 + rng.poisson(max(theta["words_per_doc"] - 1.0, 0.1))
        doc = []
        if rng.random() < theta["formula_rate"]:
            doc.append(int(headers[s, rng.integers(0, 2)]))
        while len(doc) < ndw:
            doc.append(int(rng.choice(len(lemmas), p=pw)))
        for li in doc:
            var = lemmas[li]
            form = var[int(rng.integers(0, len(var)))]
            w = tuple(c * V + v for c, v in form)
            words.append(w)
            tokens += len(w)
    labels = {r * V + v: (r, v) for r in range(C) for v in range(V)}
    return words, labels


def simulate_painted(theta: dict, token_budget: int, rng: np.random.Generator):
    """NEGATIVE control: words are random sign strings (no grid generative
    process at all); (row,col) labels are painted on arbitrarily afterward.
    Any systematic ARI > 0 against painted labels = leakage in the pipeline."""
    C, V = theta["C"], theta["V"]
    n_signs = C * V
    sw = (np.arange(1, n_signs + 1, dtype=float) ** -0.8)
    sw /= sw.sum()
    sperm = rng.permutation(n_signs)
    p_wlen = 1.0 / max(theta["wlen_mean"], 1.05)
    n_types = theta["n_lemmas"]
    types = []
    for _ in range(n_types):
        L = int(min(rng.geometric(p_wlen), 8))
        types.append(tuple(int(sperm[i]) for i in rng.choice(n_signs, size=L, p=sw)))
    lw = (np.arange(1, n_types + 1, dtype=float) ** -theta["zipf_lex"])
    lw /= lw.sum()
    words = []
    tokens = 0
    while tokens < token_budget:
        w = types[int(rng.choice(n_types, p=lw))]
        words.append(w)
        tokens += len(w)
    paint = rng.permutation(n_signs)
    labels = {int(s): (int(paint[s]) // V, int(paint[s]) % V) for s in range(n_signs)}
    return words, labels


# ---------------------------------------------------------------------------
# 2. Feature extraction (identical code path for sims and opaque LB)
# ---------------------------------------------------------------------------

def extract(words):
    """words: list of tuples (token occurrences of sign ids / opaque strings).
    Returns dict with kept sign list, pairwise feature matrix X (P x F), pair
    index, and the raw first/second-order cosine matrices used by baselines."""
    tokfreq = Counter()
    for w in words:
        tokfreq.update(w)
    kept = sorted([s for s, c in tokfreq.items() if c >= MIN_SIGN_FREQ], key=str)
    idx = {s: i for i, s in enumerate(kept)}
    n = len(kept)
    typec = Counter(words)

    OTH, BOS, EOS = n, n + 1, n + 2
    Lm = np.zeros((n, n + 3))
    Rm = np.zeros((n, n + 3))
    pos = np.zeros((n, 4))  # init, medial, final, singleton
    fin_types = np.zeros(n)
    slot_types = np.zeros(n)
    mp_fin = np.zeros((n, n))
    mp_non = np.zeros((n, n))

    fin_groups = defaultdict(Counter)
    non_groups = defaultdict(Counter)
    for w, c in typec.items():
        u = np.sqrt(c)
        Lw = len(w)
        for t, s in enumerate(w):
            i = idx.get(s)
            if i is None:
                continue
            left = idx.get(w[t - 1], OTH) if t > 0 else BOS
            right = idx.get(w[t + 1], OTH) if t < Lw - 1 else EOS
            Lm[i, left] += u
            Rm[i, right] += u
            if Lw == 1:
                pos[i, 3] += u
            elif t == 0:
                pos[i, 0] += u
            elif t == Lw - 1:
                pos[i, 2] += u
            else:
                pos[i, 1] += u
        if Lw >= 2:
            i = idx.get(w[-1])
            if i is not None:
                fin_types[i] += 1
                fin_groups[w[:-1]][i] += 1
            for t in range(Lw - 1):
                i = idx.get(w[t])
                if i is not None:
                    slot_types[i] += 1
                    non_groups[(Lw, t, w[:t] + w[t + 1:])][i] += 1

    for grp, target in ((fin_groups, mp_fin), (non_groups, mp_non)):
        for _, cnt in grp.items():
            ks = list(cnt)
            for a in range(len(ks)):
                for b in range(a + 1, len(ks)):
                    i, j = ks[a], ks[b]
                    v = cnt[ks[a]] * cnt[ks[b]]
                    target[i, j] += v
                    target[j, i] += v

    def ppmi_cos(M):
        tot = M.sum()
        if tot <= 0:
            return np.zeros((n, n))
        P = M / tot
        pr = P.sum(1, keepdims=True)
        pc = P.sum(0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            pm = np.log(P / (pr @ pc))
        pm[~np.isfinite(pm)] = 0.0
        pm = np.maximum(pm, 0.0)
        nrm = np.linalg.norm(pm, axis=1, keepdims=True)
        nrm[nrm == 0] = 1.0
        U = pm / nrm
        return U @ U.T

    cosL = ppmi_cos(Lm)
    cosR = ppmi_cos(Rm)
    cos1 = ppmi_cos(np.hstack([Lm, Rm]))

    def rowcos(A):
        nrm = np.linalg.norm(A, axis=1, keepdims=True)
        nrm[nrm == 0] = 1.0
        U = A / nrm
        return U @ U.T

    cos2 = rowcos(cos1)

    freqs = np.array([tokfreq[s] for s in kept], dtype=float)
    lf = np.log10(freqs)
    pshare = pos / np.maximum(pos.sum(1, keepdims=True), 1e-9)

    iu = np.triu_indices(n, 1)
    P = len(iu[0])
    X = np.zeros((P, len(FEATURE_NAMES)))
    i, j = iu
    X[:, 0] = cos1[iu]
    X[:, 1] = cosL[iu]
    X[:, 2] = cosR[iu]
    X[:, 3] = cos2[iu]
    X[:, 4] = mp_fin[iu] / np.sqrt((1 + fin_types[i]) * (1 + fin_types[j]))
    X[:, 5] = mp_non[iu] / np.sqrt((1 + slot_types[i]) * (1 + slot_types[j]))
    X[:, 6] = 1.0 - 0.5 * np.abs(pshare[i] - pshare[j]).sum(1)
    X[:, 7] = np.minimum(freqs[i], freqs[j]) / np.maximum(freqs[i], freqs[j])
    X[:, 8] = np.abs(lf[i] - lf[j])
    X[:, 9] = lf[i] + lf[j]
    X[:, 10] = np.abs(pshare[i, 2] - pshare[j, 2])
    X[:, 11] = np.abs(pshare[i, 0] - pshare[j, 0])

    return {"kept": kept, "X": X, "pairs": iu, "cos1": cos1, "cos2": cos2,
            "freqs": freqs, "n": n}


def pair_labels(kept, labels):
    rows = np.array([labels[s][0] for s in kept])
    cols = np.array([labels[s][1] for s in kept])
    iu = np.triu_indices(len(kept), 1)
    return (rows[iu[0]] == rows[iu[1]]).astype(int), (cols[iu[0]] == cols[iu[1]]).astype(int), rows, cols


# ---------------------------------------------------------------------------
# 3. Estimators
# ---------------------------------------------------------------------------

def cluster_ari(A, k, true_lab, anchors, anchor_lab, seed_key):
    """Spectral clustering on affinity A (with anchor equality constraints),
    ARI scored on NON-anchor signs only."""
    from sklearn.cluster import SpectralClustering
    from sklearn.metrics import adjusted_rand_score
    n = A.shape[0]
    A = np.clip((A + A.T) / 2.0, 0.0, None)
    A = A / max(A.max(), 1e-9)
    if anchors is not None and len(anchors) > 0:
        for ai, a in enumerate(anchors):
            for bi in range(ai + 1, len(anchors)):
                b = anchors[bi]
                v = 1.0 if anchor_lab[ai] == anchor_lab[bi] else 0.0
                A[a, b] = A[b, a] = v
    np.fill_diagonal(A, 1.0)
    k = int(min(k, n - 1))
    r = rng_for(*seed_key)
    sc = SpectralClustering(n_clusters=k, affinity="precomputed",
                            assign_labels="kmeans", n_init=10,
                            random_state=int(r.integers(0, 2**31 - 1)))
    try:
        pred = sc.fit_predict(A)
    except Exception:
        return None
    mask = np.ones(n, bool)
    if anchors is not None and len(anchors) > 0:
        mask[list(anchors)] = False
    return float(adjusted_rand_score(true_lab[mask], pred[mask]))


def sbi_affinity(clf, scaler, X, n):
    iu = np.triu_indices(n, 1)
    p = clf.predict_proba(scaler.transform(X))[:, 1]
    A = np.zeros((n, n))
    A[iu] = p
    A = A + A.T
    return A


def base_m1_ari(cos1, anchors, anchor_lab_unused, k, true_lab, seed_key):
    """E003 G-surface estimator geometry analogue: each sign represented by its
    similarity profile to the b anchors; k-means; ARI on non-anchors."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score
    n = cos1.shape[0]
    Xp = cos1[:, list(anchors)]
    r = rng_for(*seed_key)
    km = KMeans(n_clusters=int(min(k, n - 1)), n_init=10,
                random_state=int(r.integers(0, 2**31 - 1)))
    pred = km.fit_predict(Xp)
    mask = np.ones(n, bool)
    mask[list(anchors)] = False
    return float(adjusted_rand_score(true_lab[mask], pred[mask]))


def sinkhorn(K, p, q, iters=200):
    u = np.ones_like(p)
    v = np.ones_like(q)
    for _ in range(iters):
        u = p / np.maximum(K @ v, 1e-30)
        v = q / np.maximum(K.T @ u, 1e-30)
    return u[:, None] * K * v[None, :]


def base_gw_ari(cos2, C_true, V_true, anchors, anchor_rc, true_rows, true_cols,
                axis, eps=0.05, alpha=0.5, iters=50):
    """E006-best estimator analogue: entropic Gromov-Wasserstein coupling of the
    corpus dissimilarity graph to an idealized C x V grid template; anchors fused
    into the cost (alpha) when present. Graded axis-swap-best (generous)."""
    from sklearn.metrics import adjusted_rand_score
    n = cos2.shape[0]
    D1 = 1.0 - np.clip(cos2, 0.0, 1.0)
    m = C_true * V_true
    rr = np.arange(m) // V_true
    cc = np.arange(m) % V_true
    D2 = np.ones((m, m))
    D2[rr[:, None] == rr[None, :]] = 0.35
    D2[cc[:, None] == cc[None, :]] = np.minimum(
        D2[cc[:, None] == cc[None, :]], 0.65)
    np.fill_diagonal(D2, 0.0)
    p = np.full(n, 1.0 / n)
    q = np.full(m, 1.0 / m)
    M = None
    if anchors is not None and len(anchors) > 0:
        M = np.full((n, m), 0.5)
        for ai, a in enumerate(anchors):
            r_, c_ = anchor_rc[ai]
            M[a, :] = 1.0
            M[a, r_ * V_true + c_] = 0.0
    T = np.outer(p, q)
    for _ in range(iters):
        G = -2.0 * D1 @ T @ D2
        G = G / max(np.abs(G).max(), 1e-12)
        if M is not None:
            G = (1 - alpha) * G + alpha * M
        K = np.exp(-G / eps)
        T = sinkhorn(K, p, q)
        if not np.isfinite(T).all():
            return None
    cell = T.argmax(1)
    pred_r = cell // V_true
    pred_c = cell % V_true
    mask = np.ones(n, bool)
    if anchors is not None and len(anchors) > 0:
        mask[list(anchors)] = False
    tl = true_rows if axis == "C" else true_cols
    a1 = adjusted_rand_score(tl[mask], pred_r[mask])
    a2 = adjusted_rand_score(tl[mask], pred_c[mask])
    return float(max(a1, a2))


# ---------------------------------------------------------------------------
# 4. Training the SBI estimator
# ---------------------------------------------------------------------------

def gen_training(prior: str, n_sims: int, tag: str):
    rows = []
    yc_all, yv_all = [], []
    metas = []
    for s in range(n_sims):
        rng = rng_for("train", prior, tag, s)
        th = draw_theta(rng, wrong=(prior == "wrong"))
        budget = int(np.exp(rng.uniform(np.log(4000), np.log(30000))))
        words, labels = simulate(th, budget, rng)
        ex = extract(words)
        yc, yv, _, _ = pair_labels(ex["kept"], labels)
        rows.append(ex["X"])
        yc_all.append(yc)
        yv_all.append(yv)
        metas.append({"theta": th, "budget": budget, "n_signs": ex["n"],
                      "n_pairs": len(yc)})
    X = np.vstack(rows)
    yc = np.concatenate(yc_all)
    yv = np.concatenate(yv_all)
    if len(yc) > MAX_TRAIN_PAIRS:
        r = rng_for("train_sub", prior, tag)
        sel = r.choice(len(yc), MAX_TRAIN_PAIRS, replace=False)
        X, yc, yv = X[sel], yc[sel], yv[sel]
    return X, yc, yv, metas


def train_sbi(X, yc, yv, tag):
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    r = rng_for("mlp", tag)
    clfC = MLPClassifier(hidden_layer_sizes=(64, 32), alpha=1e-4, max_iter=200,
                         early_stopping=True,
                         random_state=int(r.integers(0, 2**31 - 1)))
    clfC.fit(Xs, yc)
    r2 = rng_for("mlp_v", tag)
    clfV = MLPClassifier(hidden_layer_sizes=(64, 32), alpha=1e-4, max_iter=200,
                         early_stopping=True,
                         random_state=int(r2.integers(0, 2**31 - 1)))
    clfV.fit(Xs, yv)
    return scaler, clfC, clfV


def ood_stat(scaler, X):
    """Median (over pairs) mean-|z| distance under the training scaler."""
    Z = np.abs(scaler.transform(X))
    return float(np.median(Z.mean(1)))


# ---------------------------------------------------------------------------
# 5. Evaluation of one corpus with all estimators at one budget
# ---------------------------------------------------------------------------

def eval_corpus(ex, labels, models, budget, seed_key, methods=("SBI", "SPEC", "M1", "GW")):
    scaler, clfC, clfV = models
    kept, n = ex["kept"], ex["n"]
    yc, yv, rows, cols = pair_labels(kept, labels)
    kC = len(set(rows.tolist()))
    kV = len(set(cols.tolist()))
    r = rng_for("anchors", *seed_key, budget)
    anchors = []
    if budget > 0:
        order = np.argsort(-ex["freqs"])
        pool = order[:min(ANCHOR_POOL_TOP, n)]
        anchors = list(map(int, r.choice(pool, size=min(budget, len(pool)),
                                         replace=False)))
    a_rows = [int(rows[a]) for a in anchors]
    a_cols = [int(cols[a]) for a in anchors]
    a_rc = list(zip(a_rows, a_cols))
    out = {"n_signs": n, "kC": kC, "kV": kV, "anchors": anchors}
    A_sbi_C = sbi_affinity(clfC, scaler, ex["X"], n)
    A_sbi_V = sbi_affinity(clfV, scaler, ex["X"], n)
    A_raw = np.clip(ex["cos2"], 0.0, 1.0)
    for axis, k, tl, alab, A_s in (("C", kC, rows, a_rows, A_sbi_C),
                                   ("V", kV, cols, a_cols, A_sbi_V)):
        res = {}
        if "SBI" in methods:
            res["SBI"] = cluster_ari(A_s.copy(), k, tl, anchors, alab,
                                     ("sbi", axis, *seed_key, budget))
        if "SPEC" in methods:
            res["SPEC"] = cluster_ari(A_raw.copy(), k, tl, anchors, alab,
                                      ("spec", axis, *seed_key, budget))
        if "M1" in methods and budget > 0:
            res["M1"] = base_m1_ari(ex["cos1"], anchors, alab, k, tl,
                                    ("m1", axis, *seed_key, budget))
        if "GW" in methods:
            res["GW"] = base_gw_ari(ex["cos2"], kC, kV, anchors, a_rc,
                                    rows, cols, axis,
                                    alpha=(0.5 if budget > 0 else 0.0))
        out[axis] = res
    return out


# ---------------------------------------------------------------------------
# 6. Linear B degraded benchmark
# ---------------------------------------------------------------------------

def lb_replicate(seqs_core, rep):
    r = rng_for("lb", rep)
    order = r.permutation(len(seqs_core))
    words = []
    tok = 0
    for k in order:
        w = seqs_core[k]
        words.append(w)
        tok += len(w)
        if tok >= LA_TOKEN_SCALE:
            break
    return words


def load_lb():
    from cross_script.data import load_b_damos
    seqs, freq, _ = load_b_damos()
    core_words = [tuple(w) for w in seqs
                  if len(w) >= 1 and all(CORE_RE.match(s) for s in w)]
    labels = {}
    rowmap = {}
    for w in core_words:
        for s in w:
            if s in labels:
                continue
            c = s[:-1] or "-"
            v = s[-1]
            rowmap.setdefault(c, len(rowmap))
            labels[s] = (rowmap[c], "AEIOU".index(v))
    return core_words, labels


# ---------------------------------------------------------------------------
# 7. Stages
# ---------------------------------------------------------------------------

def perm_p(diffs, n_perm=N_PERM, key=("perm",)):
    """Two-sided sign-flip permutation p for mean(diffs) != 0."""
    diffs = np.asarray(diffs, float)
    obs = abs(diffs.mean())
    r = rng_for(*key)
    signs = r.choice([-1.0, 1.0], size=(n_perm, len(diffs)))
    null = np.abs((signs * diffs[None, :]).mean(1))
    return float((1 + (null >= obs - 1e-12).sum()) / (1 + n_perm))


def main(dev=False, simonly=False):
    t0 = time.time()
    global N_TRAIN, N_HELD, R_LB, N_PERM
    if dev:
        N_TRAIN, N_HELD, R_LB, N_PERM = 12, 4, 3, 500
    res = {"epoch": "EPOCH-016", "seed": SEED, "dev": dev,
           "feature_names": FEATURE_NAMES,
           "config": {"N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "R_LB": R_LB,
                      "BUDGETS": BUDGETS, "LA_TOKEN_SCALE": LA_TOKEN_SCALE,
                      "AMPLE_SCALE": AMPLE_SCALE, "MIN_SIGN_FREQ": MIN_SIGN_FREQ,
                      "ANCHOR_POOL_TOP": ANCHOR_POOL_TOP, "MARGIN": MARGIN,
                      "PC_A_BAR": PC_A_BAR, "NEG_BAR": NEG_BAR,
                      "MISSPEC_DROP": MISSPEC_DROP,
                      "OOD_FLAG_FRAC": OOD_FLAG_FRAC}}

    # --- train true-prior SBI ------------------------------------------------
    print("[stage T] training true-prior SBI ...", flush=True)
    Xt, yct, yvt, meta_t = gen_training("true", N_TRAIN, "v1")
    models_true = train_sbi(Xt, yct, yvt, "true_v1")
    from sklearn.metrics import roc_auc_score
    # in-sample sanity AUC (diagnostic only)
    auc_c = roc_auc_score(yct, models_true[1].predict_proba(
        models_true[0].transform(Xt))[:, 1])
    auc_v = roc_auc_score(yvt, models_true[2].predict_proba(
        models_true[0].transform(Xt))[:, 1])
    res["train"] = {"n_sims": N_TRAIN, "n_pairs": int(len(yct)),
                    "insample_auc_C": round(float(auc_c), 4),
                    "insample_auc_V": round(float(auc_v), 4),
                    "base_rate_sameC": round(float(yct.mean()), 4),
                    "base_rate_sameV": round(float(yvt.mean()), 4)}
    print(f"  trained: pairs={len(yct)} aucC={auc_c:.3f} aucV={auc_v:.3f}", flush=True)

    # --- PC-A / PC-B: held-out in-distribution sims (b=0) --------------------
    print("[stage PC] positive controls ...", flush=True)
    pc = {}
    heldout_true = []
    for name, scale in (("PC_A_ample", AMPLE_SCALE), ("PC_B_lascale", LA_TOKEN_SCALE)):
        aris_C, aris_V, aucs = [], [], []
        for s in range(N_HELD):
            rng = rng_for("held", name, s)
            th = draw_theta(rng)
            words, labels = simulate(th, scale, rng)
            ex = extract(words)
            if name == "PC_B_lascale":
                heldout_true.append((ex, labels))
            yc, yv, _, _ = pair_labels(ex["kept"], labels)
            try:
                aucs.append(float(roc_auc_score(yc, models_true[1].predict_proba(
                    models_true[0].transform(ex["X"]))[:, 1])))
            except Exception:
                pass
            ev = eval_corpus(ex, labels, models_true, 0, (name, s),
                             methods=("SBI", "SPEC"))
            if ev["C"]["SBI"] is not None:
                aris_C.append(ev["C"]["SBI"])
                aris_V.append(ev["V"]["SBI"])
        pc[name] = {"mean_ARI_C": round(float(np.mean(aris_C)), 4),
                    "mean_ARI_V": round(float(np.mean(aris_V)), 4),
                    "mean_pair_auc_C": round(float(np.mean(aucs)), 4),
                    "per_sim_ARI_C": [round(a, 3) for a in aris_C]}
        print(f"  {name}: ARI_C={pc[name]['mean_ARI_C']} ARI_V={pc[name]['mean_ARI_V']} auc={pc[name]['mean_pair_auc_C']}", flush=True)
    pc["PC_A_pass"] = bool(pc["PC_A_ample"]["mean_ARI_C"] >= PC_A_BAR)
    res["positive_controls"] = pc

    # --- NEG: painted-label structure-free sims ------------------------------
    print("[stage NEG] negative control ...", flush=True)
    negs_C, negs_V = [], []
    for s in range(N_HELD):
        rng = rng_for("neg", s)
        th = draw_theta(rng)
        words, labels = simulate_painted(th, LA_TOKEN_SCALE, rng)
        ex = extract(words)
        ev = eval_corpus(ex, labels, models_true, 5, ("neg", s),
                         methods=("SBI",))
        if ev["C"]["SBI"] is not None:
            negs_C.append(ev["C"]["SBI"])
            negs_V.append(ev["V"]["SBI"])
    neg_p = perm_p(negs_C, key=("negperm",))
    res["negative_control"] = {
        "mean_ARI_C": round(float(np.mean(negs_C)), 4),
        "mean_ARI_V": round(float(np.mean(negs_V)), 4),
        "perm_p_C": neg_p,
        "leak": bool(abs(np.mean(negs_C)) >= NEG_BAR and neg_p < 0.05)}
    print(f"  NEG: ARI_C={res['negative_control']['mean_ARI_C']} p={neg_p} leak={res['negative_control']['leak']}", flush=True)

    # --- MISSPEC: wrong-prior SBI + OOD visibility ---------------------------
    print("[stage MIS] misspecification test ...", flush=True)
    Xw, ycw, yvw, meta_w = gen_training("wrong", N_TRAIN, "v1")
    models_wrong = train_sbi(Xw, ycw, yvw, "wrong_v1")
    # in-dist OOD reference: wrong-prior held-out sims under wrong scaler
    ref_stats = []
    for s in range(N_HELD):
        rng = rng_for("held_wrong", s)
        th = draw_theta(rng, wrong=True)
        words, labels = simulate(th, LA_TOKEN_SCALE, rng)
        ex = extract(words)
        ref_stats.append(ood_stat(models_wrong[0], ex["X"]))
    thresh = float(np.percentile(ref_stats, 95))
    mis_aris, mis_flags = [], []
    for s, (ex, labels) in enumerate(heldout_true):
        st = ood_stat(models_wrong[0], ex["X"])
        mis_flags.append(bool(st > thresh))
        ev = eval_corpus(ex, labels, models_wrong, 0, ("mis", s),
                         methods=("SBI",))
        if ev["C"]["SBI"] is not None:
            mis_aris.append(ev["C"]["SBI"])
    drop = float(pc["PC_B_lascale"]["mean_ARI_C"] - np.mean(mis_aris))
    flag_frac = float(np.mean(mis_flags))
    if drop >= MISSPEC_DROP:
        mis_verdict = "VISIBLE_FAILURE" if flag_frac >= OOD_FLAG_FRAC else "SILENT_FAILURE"
    else:
        mis_verdict = "ROBUST"
    res["misspec"] = {"wrong_train_pairs": int(len(ycw)),
                      "ood_threshold": round(thresh, 4),
                      "ood_ref_stats": [round(x, 4) for x in ref_stats],
                      "mean_ARI_C_wrongSBI_on_true": round(float(np.mean(mis_aris)), 4),
                      "ari_drop": round(drop, 4),
                      "flag_frac": round(flag_frac, 3),
                      "verdict": mis_verdict}
    print(f"  MIS: drop={drop:.3f} flags={flag_frac:.2f} -> {mis_verdict}", flush=True)

    if simonly:
        # pre-freeze smoke mode: LB is NEVER loaded
        res["runtime_s"] = round(time.time() - t0, 1)
        out = os.path.join(OUT, "E016_smoke_simonly.json")
        with open(out, "w") as fh:
            json.dump(res, fh, indent=1)
        print("SIMONLY smoke complete; LB untouched. wrote", out)
        return

    # --- LB verdict cells -----------------------------------------------------
    print("[stage LB] Linear B degraded benchmark ...", flush=True)
    core_words, lb_labels = load_lb()
    res["lb_meta"] = {"core_word_occurrences": len(core_words),
                      "core_sign_types": len(lb_labels)}
    cells = {str(b): [] for b in BUDGETS}
    lb_ood = []
    for rep in range(R_LB):
        words = lb_replicate(core_words, rep)
        ex = extract(words)
        lb_ood.append(ood_stat(models_true[0], ex["X"]))
        for b in BUDGETS:
            ev = eval_corpus(ex, lb_labels, models_true, b, ("lbrep", rep))
            cells[str(b)].append(ev)
    # true-prior OOD view of LB (descriptive)
    ref_true = []
    for s, (ex, _) in enumerate(heldout_true):
        ref_true.append(ood_stat(models_true[0], ex["X"]))
    thresh_true = float(np.percentile(ref_true, 95))
    res["lb_ood_under_true_prior"] = {
        "threshold": round(thresh_true, 4),
        "lb_stats": [round(x, 4) for x in lb_ood],
        "flag_frac": round(float(np.mean([x > thresh_true for x in lb_ood])), 3)}

    # --- verdict mechanics ----------------------------------------------------
    summary = {}
    raw_ps = {}
    for b in BUDGETS:
        rows_ = cells[str(b)]
        per = {"SBI": [], "SPEC": [], "M1": [], "GW": []}
        dV = []
        diffs = []
        for r_i, ev in enumerate(rows_):
            sbi = ev["C"]["SBI"]
            bases = [ev["C"].get(m) for m in ("SPEC", "M1", "GW")]
            bases = [x for x in bases if x is not None]
            if sbi is None or not bases:
                continue
            diffs.append(sbi - max(bases))
            for m in per:
                if ev["C"].get(m) is not None:
                    per[m].append(ev["C"][m])
            if ev["V"]["SBI"] is not None:
                vb = [ev["V"].get(m) for m in ("SPEC", "M1", "GW")]
                vb = [x for x in vb if x is not None]
                if vb:
                    dV.append(ev["V"]["SBI"] - max(vb))
        p = perm_p(diffs, key=("lbperm", b))
        raw_ps[b] = p
        summary[str(b)] = {
            "mean_ARI_C": {m: round(float(np.mean(v)), 4) for m, v in per.items() if v},
            "mean_diff_C_SBI_vs_bestbase": round(float(np.mean(diffs)), 4),
            "sd_diff_C": round(float(np.std(diffs)), 4),
            "raw_p": p,
            "mean_diff_V": round(float(np.mean(dV)), 4) if dV else None,
            "n_replicates": len(diffs)}
    # Holm over the 3 budgets (primary endpoint = ARI_C diff)
    order = sorted(BUDGETS, key=lambda b: raw_ps[b])
    holm = {}
    for rank, b in enumerate(order):
        holm[b] = min(1.0, raw_ps[b] * (len(BUDGETS) - rank))
    for i in range(1, len(order)):
        holm[order[i]] = max(holm[order[i]], holm[order[i - 1]])
    miscal = (not pc["PC_A_pass"]) or res["negative_control"]["leak"] or \
        (mis_verdict == "SILENT_FAILURE")
    verdicts = {}
    for b in BUDGETS:
        d = summary[str(b)]["mean_diff_C_SBI_vs_bestbase"]
        hp = holm[b]
        summary[str(b)]["holm_p"] = round(hp, 5)
        if miscal:
            v = "SBI_MISCALIBRATED"
        elif d >= MARGIN and hp < 0.05:
            v = "SBI_BEATS_SURFACE"
        elif d <= -MARGIN and hp < 0.05:
            v = "SBI_UNDERPERFORMS"
        else:
            v = "SBI_MATCHES"
        verdicts[str(b)] = v
    res["lb_cells"] = cells
    res["summary"] = summary
    res["verdicts_per_budget"] = verdicts
    res["miscalibration_gate"] = {
        "PC_A_pass": pc["PC_A_pass"],
        "neg_leak": res["negative_control"]["leak"],
        "misspec_verdict": mis_verdict,
        "SBI_MISCALIBRATED": bool(miscal)}
    res["runtime_s"] = round(time.time() - t0, 1)
    out = os.path.join(OUT, "E016_result_dev.json" if dev else "E016_result.json")
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({"verdicts": verdicts, "miscal": miscal,
                      "summary": {k: {kk: vv for kk, vv in v.items() if kk != 'mean_ARI_C'}
                                  for k, v in summary.items()},
                      "runtime_s": res["runtime_s"]}, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--simonly", action="store_true")
    args = ap.parse_args()
    main(dev=args.dev, simonly=args.simonly)
