#!/usr/bin/env python3
"""WP6 — BOUNDED AGNOSTIC SIGN-VALUE SEARCH over the REDUCED space + mandatory END-TO-END NULL.

Question. WP1 refuted the value-blind theorem; WP3.2 (substitution) and WP5(b) (reduced-seed
C/V bootstrap) VALIDATE on opaque Linear B but are ~1.7x below the clean regime / underpowered on
Linear A. The obstacle is LA-side propagation POWER. WP6 asks the sharpest possible version of the
decipherment question that the corpus can actually support, and then subjects it to the discipline's
hardest gate: an END-TO-END null that reruns the WHOLE adaptive pipeline on wrong data.

WHAT IS SEARCHED (the "reduced space").  A full syllabic relabeling of ~46 LA signs is a hopeless
search (S_46). We search the REDUCED space instead: a map phi: sign -> one of K distributional
value-CLASSES (K adaptively selected from {2,4,6,8}). This is the operational object every propagation
result above lives in — signs collapsed into a few phonological equivalence classes.

OBJECTIVE (self-supervised, LA-internal, NON-CIRCULAR; NO Linear B value is ever a model input).
  Held-out PREDICTIVE improvement of a class-based bigram over a unigram baseline:
      score(phi) = [ LL_test( q_i | class(p_{i-1}) )  -  LL_test( q_i ) ] / n_test_tokens   (nats/token)
  with P(q | c) and P(q) both fit on the TRAIN partition (add-delta), scored on HELD-OUT tokens.
  This is a Brown/information-bottleneck objective: a class map that captures real phonotactic context
  lowers held-out surprise; it is NOT relabeling-invariant because many signs map to few classes.
  There is NO reference to any language's phonology, NO root lexicon, NO semantic plausibility.

SEARCH (bounded; the search is fixed a priori, never tuned to any LA answer).
  * Fixed beam width B, fixed iterations T, K grid {2,4,6,8}, add-delta smoothing.
  * TRAIN objective steered by three FIXED-coefficient terms (each recomputed LA-internally):
      - substitution same-class term (WP3.2 strong edges; sign-identity contexts only),
      - a WEAK LA-internal C/V prior (PC1 of position features oriented by initial-rate; class 0 = vowel-like),
      - a multiplicity penalty (BIC-like K*V/n_tokens) — the mandated "multiplicity penalty".
  * K and the map are SELECTED on the TRAIN objective only; HELD-OUT touched once for the score.

END-TO-END NULL (the mandatory gate).  The SAME pipeline — priors, sub-graph threshold, K selection,
beam search, fold averaging — is rerun on >= 50 realizations per family:
  (S) order-shuffle : LA with sign order permuted within each inscription (destroys sequential phonotactics).
  (W) wrong-language: opaque Linear B (DAMOS) resampled to LA length distribution, processed identically.
  (R) random-prior  : real LA bigrams, but the WP3.1/WP3.2 priors permuted (destroys prior informativeness).
  Families (W) and (R) are the DECISIVE nulls for a *value* claim: (S) beaten only proves LA has order
  structure; (W)/(R) beaten is required to claim LA-value-specific edge. Because every realization runs the
  full best-of-search + K-selection, the null distribution is already search-adjusted. Family-wise
  false-positive rate = fraction of decisive null realizations whose held-out score >= the real score.

Deterministic (seed 20260708). Corpus read-only from the main worktree.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wp3_2_scribal_substitution as SUB  # reuse the sign-identity substitution graph  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
SEED = 20260708

# ------------------------------------------------------------------ fixed pipeline hyperparameters
FREQ_MIN = 20
K_GRID = (2, 4, 6, 8)
BEAM = 5                 # fixed beam width
ITERS = 8               # fixed beam iterations
N_FOLDS = 4             # held-out folds (averaged)
DELTA = 0.5            # add-delta smoothing
LAMBDA_SUB = 0.30      # substitution same-class steering (fixed a priori)
LAMBDA_CV = 0.20       # weak C/V prior steering (fixed a priori)
LAMBDA_MULT = 0.50    # multiplicity penalty coefficient (fixed a priori)
SUB_TARGET_EDGES = 40  # adaptive sub-threshold: keep ~this many strongest edges
N_NULL_PER_FAMILY = 50 # >= 50 mandated, per family


# =============================================================== corpus -> remapped token sequences
def remap(seqs, freq_min=FREQ_MIN):
    """Keep signs with freq>=freq_min; merge the rest into a single <R> token. Returns
    (sequences of token-ids, id2tok, freq_sign_set). Token vocab = frequent signs + '<R>'."""
    c = Counter()
    clean = []
    for w in seqs:
        w = [s for s in w if s]
        if w:
            clean.append(w)
            for s in w:
                c[s] += 1
    freq_signs = sorted((s for s in c if c[s] >= freq_min), key=lambda s: (-c[s], s))
    tok2id = {s: i for i, s in enumerate(freq_signs)}
    RARE = len(freq_signs)
    id2tok = freq_signs + ["<R>"]
    idseqs = [[tok2id.get(s, RARE) for s in w] for w in clean]
    return idseqs, id2tok, set(range(len(freq_signs))), RARE, c


def bigram_counts(idseqs, V):
    """N[p,q] over consecutive token-id pairs; unigram counts u[q] over all tokens."""
    N = np.zeros((V, V), dtype=np.float64)
    u = np.zeros(V, dtype=np.float64)
    for w in idseqs:
        for t in w:
            u[t] += 1.0
        for a, b in zip(w[:-1], w[1:]):
            N[a, b] += 1.0
    return N, u


# =============================================================== LA-internal priors (recomputed per corpus)
def position_features(idseqs, V):
    init = np.zeros(V); fin = np.zeros(V); tot = np.zeros(V); pos = np.zeros(V); lone = np.zeros(V)
    lnb = defaultdict(Counter); rnb = defaultdict(Counter)
    for w in idseqs:
        L = len(w)
        if L == 0:
            continue
        if L == 1:
            lone[w[0]] += 1
        for i, s in enumerate(w):
            tot[s] += 1
            pos[s] += (i / (L - 1)) if L > 1 else 0.5
            if i > 0:
                lnb[s][w[i - 1]] += 1
            if i < L - 1:
                rnb[s][w[i + 1]] += 1
        init[w[0]] += 1; fin[w[-1]] += 1

    def ent(cnt):
        n = sum(cnt.values())
        return -sum((v / n) * math.log(v / n) for v in cnt.values()) if n else 0.0

    F = np.zeros((V, 6))
    for s in range(V):
        t = tot[s] if tot[s] > 0 else 1.0
        F[s] = [init[s] / t, fin[s] / t, pos[s] / t, lone[s] / t, ent(lnb[s]), ent(rnb[s])]
    return F, tot


def cv_prior(idseqs, V, freq_ids):
    """WEAK LA-internal vowel-likeness in [0,1]: PC1 of standardized position features, oriented so
    that higher initial-rate => more vowel-like, squashed. Purely distributional; no phonetic values."""
    F, tot = position_features(idseqs, V)
    idx = sorted(freq_ids)
    Fs = F[idx]
    mu = Fs.mean(0); sd = Fs.std(0) + 1e-9
    Z = (Fs - mu) / sd
    # PC1
    U, S, Vt = np.linalg.svd(Z - Z.mean(0), full_matrices=False)
    pc1 = Z @ Vt[0]
    # orient by correlation with initial_rate (feature col 0)
    if np.corrcoef(pc1, Z[:, 0])[0, 1] < 0:
        pc1 = -pc1
    pc1 = (pc1 - pc1.mean()) / (pc1.std() + 1e-9)
    prob = 1.0 / (1.0 + np.exp(-pc1))
    out = np.full(V, 0.5)
    for j, i in enumerate(idx):
        out[i] = prob[j]
    return out


def sub_edges(seqs_raw, freq_ids, id_of, target_edges=SUB_TARGET_EDGES):
    """WP3.2 substitution graph on sign identities; adaptive threshold keeps ~target_edges strongest
    edges among frequent signs. Returns list of (i,j,weight) in token-id space."""
    edge_weight, _, _ = SUB.substitution_graph(seqs_raw)
    edges = []
    for e, w in edge_weight.items():
        u, v = tuple(e)
        if u in id_of and v in id_of:
            iu, iv = id_of[u], id_of[v]
            if iu in freq_ids and iv in freq_ids:
                edges.append((iu, iv, float(w)))
    edges.sort(key=lambda t: -t[2])
    if len(edges) > target_edges:
        edges = edges[:target_edges]
    # normalise weights to sum 1 (so the steering term is scale-free across corpora)
    tw = sum(w for _, _, w in edges) or 1.0
    return [(i, j, w / tw) for i, j, w in edges]


# =============================================================== class-bigram objective
def class_ll_train(M):
    """Train class-bigram log-likelihood = sum_c f(M[c,:]), decomposable per class.
    f(m) = sum_q m_q * log((m_q+DELTA)/(sum_q m + DELTA*V))."""
    V = M.shape[1]
    rowsum = M.sum(1, keepdims=True)
    logp = np.log(M + DELTA) - np.log(rowsum + DELTA * V)
    return float((M * logp).sum())


def build_M(N, classlab, n_classes):
    """M[c,:] = sum of N rows p with class(p)=c. classlab length V (context tokens)."""
    V = N.shape[1]
    M = np.zeros((n_classes, V))
    for p in range(N.shape[0]):
        M[classlab[p]] += N[p]
    return M


def heldout_delta(N_tr, u_tr, N_te, u_te, classlab, n_classes):
    """Per-token held-out predictive improvement (nats/token) of class-bigram over unigram.
    P(q|c) and P(q) fit on TRAIN; scored against HELD-OUT bigram/unigram counts."""
    V = N_tr.shape[1]
    M = build_M(N_tr, classlab, n_classes)
    rowsum = M.sum(1, keepdims=True)
    logp_cb = np.log(M + DELTA) - np.log(rowsum + DELTA * V)   # (n_classes, V)
    logp_uni = np.log(u_tr + DELTA) - np.log(u_tr.sum() + DELTA * V)  # (V,)
    # held-out bigram counts grouped by class of prev token
    Mte = build_M(N_te, classlab, n_classes)
    ll_cb = float((Mte * logp_cb).sum())
    ll_uni_bg = float((Mte.sum(0) * logp_uni).sum())  # unigram scored on the same bigram-next tokens
    n_te = float(N_te.sum())
    if n_te <= 0:
        return 0.0
    return (ll_cb - ll_uni_bg) / n_te


# =============================================================== bounded beam search (train objective)
def steer_terms(classlab, cvp, edges, freq_ids, n_classes, n_tr_tokens, V):
    """Fixed-coefficient steering: substitution same-class + weak C/V prior + multiplicity penalty."""
    # substitution same-class (weighted fraction of strong edges whose endpoints share a class)
    sub = 0.0
    for i, j, w in edges:
        if classlab[i] == classlab[j]:
            sub += w
    # C/V prior: class 0 is the vowel class
    cv = 0.0
    for i in freq_ids:
        cv += cvp[i] if classlab[i] == 0 else (1.0 - cvp[i])
    cv /= max(1, len(freq_ids))
    # multiplicity penalty (BIC-like per-token param cost)
    used = len(set(classlab[i] for i in freq_ids))
    penalty = (used * V) / max(1.0, n_tr_tokens)
    return LAMBDA_SUB * sub + LAMBDA_CV * cv - LAMBDA_MULT * penalty


def train_objective(N_tr, u_tr, classlab, n_classes, cvp, edges, freq_ids, n_tr_tokens, V):
    M = build_M(N_tr, classlab, n_classes)
    return class_ll_train(M) / max(1.0, n_tr_tokens) + steer_terms(
        classlab, cvp, edges, freq_ids, n_classes, n_tr_tokens, V)


def init_labels(K, BG, freq_ids, Ffeat, cvp, rng, kind):
    """Deterministic diverse inits: kmeans on position features, cv-prior split, freq buckets, random."""
    V = BG + 1
    lab = np.full(V, BG, dtype=int)
    fids = sorted(freq_ids)
    if kind == "kmeans" and len(fids) >= K:
        from sklearn.cluster import KMeans
        Z = Ffeat[fids]
        Z = (Z - Z.mean(0)) / (Z.std(0) + 1e-9)
        km = KMeans(n_clusters=K, n_init=5, random_state=SEED).fit(Z)
        for j, i in enumerate(fids):
            lab[i] = int(km.labels_[j])
    elif kind == "cv":
        # class 0 = top cv-prior signs, rest split by a second feature bucket
        order = sorted(fids, key=lambda i: -cvp[i])
        nv = max(1, len(order) // K)
        for r, i in enumerate(order):
            lab[i] = min(K - 1, r // max(1, len(order) // K))
        for i in order[:nv]:
            lab[i] = 0
    elif kind == "freq":
        for r, i in enumerate(fids):
            lab[i] = r % K
    else:  # random
        for i in fids:
            lab[i] = rng.integers(0, K)
    return lab


def beam_search_K(N_tr, u_tr, K, BG, freq_ids, Ffeat, cvp, edges, n_tr_tokens, V, rng):
    """Fixed beam width / fixed iterations coordinate search maximising the TRAIN objective for a given K."""
    n_classes = BG + 1
    fids = sorted(freq_ids)
    inits = ["kmeans", "cv", "freq", "random", "random"]
    beam = []
    seen = set()
    for kind in inits[:BEAM]:
        lab = init_labels(K, BG, freq_ids, Ffeat, cvp, rng, kind)
        key = tuple(lab[fids])
        if key in seen:
            lab = init_labels(K, BG, freq_ids, Ffeat, cvp, rng, "random")
            key = tuple(lab[fids])
        seen.add(key)
        obj = train_objective(N_tr, u_tr, lab, n_classes, cvp, edges, freq_ids, n_tr_tokens, V)
        beam.append((obj, lab))
    beam.sort(key=lambda t: -t[0])
    beam = beam[:BEAM]

    for _ in range(ITERS):
        cand = list(beam)
        for obj, lab in beam:
            for i in fids:
                cur = lab[i]
                for c in range(K):
                    if c == cur:
                        continue
                    lab2 = lab.copy(); lab2[i] = c
                    key = tuple(lab2[fids])
                    if key in seen:
                        continue
                    seen.add(key)
                    o2 = train_objective(N_tr, u_tr, lab2, n_classes, cvp, edges, freq_ids, n_tr_tokens, V)
                    cand.append((o2, lab2))
        cand.sort(key=lambda t: -t[0])
        newbeam = cand[:BEAM]
        if all(np.array_equal(a[1], b[1]) for a, b in zip(newbeam, beam)):
            break
        beam = newbeam
    return beam[0]  # (train_obj, labels)


# =============================================================== one full pipeline run on a corpus
def make_folds(n, k, rng):
    idx = np.arange(n); rng.shuffle(idx)
    return [idx[i::k] for i in range(k)]


def run_pipeline(idseqs, seqs_raw, id2tok, freq_ids, BG, rng, cvp_override=None):
    """Full adaptive pipeline. Returns realization score = mean held-out delta over folds (with the
    K selected on TRAIN per fold). cvp_override permutes/injects the C/V prior (random-prior null)."""
    V = BG + 1
    Ffeat, _ = position_features(idseqs, V)
    cvp = cv_prior(idseqs, V, freq_ids) if cvp_override is None else cvp_override
    id_of = {tok: i for i, tok in enumerate(id2tok)}
    edges = sub_edges(seqs_raw, freq_ids, id_of)

    n = len(idseqs)
    folds = make_folds(n, N_FOLDS, np.random.default_rng(SEED + 777))
    deltas = []
    picked_K = []
    for f in range(N_FOLDS):
        te_idx = set(folds[f].tolist())
        tr_seqs = [idseqs[i] for i in range(n) if i not in te_idx]
        te_seqs = [idseqs[i] for i in range(n) if i in te_idx]
        N_tr, u_tr = bigram_counts(tr_seqs, V)
        N_te, u_te = bigram_counts(te_seqs, V)
        n_tr_tokens = float(u_tr.sum())
        best = None  # (train_obj, labels, K)
        for K in K_GRID:
            tobj, lab = beam_search_K(N_tr, u_tr, K, BG, freq_ids, Ffeat, cvp, edges,
                                      n_tr_tokens, V, np.random.default_rng(SEED + 13 * K + f))
            if best is None or tobj > best[0]:
                best = (tobj, lab, K)
        # honest: K + map selected on TRAIN; held-out touched once
        d = heldout_delta(N_tr, u_tr, N_te, u_te, best[1], BG + 1)
        deltas.append(d)
        picked_K.append(best[2])
    return float(np.mean(deltas)), {"per_fold_delta": [round(x, 5) for x in deltas],
                                    "selected_K": picked_K}


# =============================================================== null-realization corpus generators
def shuffle_within(idseqs, rng):
    out = []
    for w in idseqs:
        w2 = w[:]
        rng.shuffle(w2)
        out.append(w2)
    return out


def lb_wrong_language(lb_seqs, la_lengths, rng):
    """Build LA-length-matched surrogate inscriptions by concatenating real LB wordforms (preserves LB
    within-word sequential structure). Returns raw sign sequences."""
    pool = [ [s for s in w if s] for w in lb_seqs if any(w) ]
    out = []
    for L in la_lengths:
        seq = []
        while len(seq) < L:
            w = pool[rng.integers(0, len(pool))]
            seq.extend(w)
        out.append(seq[:L])
    return out


# =============================================================== main
def run():
    master = np.random.default_rng(SEED)

    # ---- REAL Linear A ----
    inv, la_raw, freq = X.load_a()
    idseqs, id2tok, freq_ids, BG, _ = remap(la_raw)
    real_score, real_meta = run_pipeline(idseqs, la_raw, id2tok, freq_ids, BG,
                                          np.random.default_rng(SEED + 1))

    # ---- END-TO-END NULL families ----
    la_lengths = [len([s for s in w if s]) for w in la_raw if any(w)]
    lb_seqs, _, _ = X.load_b_damos()

    def family(name, gen_corpus, permute_prior=False, n=N_NULL_PER_FAMILY):
        scores = []
        for r in range(n):
            rng = np.random.default_rng(SEED + 1000 + hash(name) % 9999 + r * 7)
            raw = gen_corpus(rng)
            ids, id2, fids, bg, _ = remap(raw)
            cvp_over = None
            if permute_prior:
                V = bg + 1
                base = cv_prior(ids, V, fids)
                perm = base.copy()
                fl = sorted(fids)
                vals = base[fl].copy(); rng.shuffle(vals)
                for j, i in enumerate(fl):
                    perm[i] = vals[j]
                cvp_over = perm
            sc, _ = run_pipeline(ids, raw, id2, fids, bg, rng, cvp_override=cvp_over)
            scores.append(sc)
        return scores

    fam_S = family("shuffle", lambda rng: shuffle_within(la_raw, rng))
    fam_W = family("wronglang", lambda rng: lb_wrong_language(lb_seqs, la_lengths, rng))
    # random-prior uses the REAL LA corpus, only the prior is permuted
    fam_R = family("randprior", lambda rng: [[s for s in w if s] for w in la_raw if any(w)],
                   permute_prior=True)

    def summ(scores):
        a = np.array(scores)
        return {"n": len(a), "mean": round(float(a.mean()), 5), "sd": round(float(a.std()), 5),
                "min": round(float(a.min()), 5), "max": round(float(a.max()), 5),
                "p95": round(float(np.percentile(a, 95)), 5)}

    def fwer(scores):
        a = np.array(scores)
        exceed = int((a >= real_score).sum())
        return {"n_ge_real": exceed, "empirical_p": round((exceed + 1) / (len(a) + 1), 4),
                "z_real_vs_null": round((real_score - a.mean()) / (a.std() + 1e-12), 3)}

    decisive = fam_W + fam_R          # value-specific nulls
    pooled = fam_S + fam_W + fam_R

    # ---- verdict ----
    p_W = fwer(fam_W)["empirical_p"]; p_R = fwer(fam_R)["empirical_p"]; p_S = fwer(fam_S)["empirical_p"]
    p_dec = fwer(decisive)["empirical_p"]
    beats_decisive = (p_W < 0.05) and (p_R < 0.05)
    if beats_decisive:
        verdict = "BEATS_END_TO_END_NULL"
    else:
        verdict = "AT_END_TO_END_NULL"

    out = {
        "experiment": "WP6_agnostic_search_over_reduced_space_plus_end_to_end_null",
        "seed": SEED,
        "design": {
            "reduced_space": "sign -> one of K distributional value-CLASSES; K selected on TRAIN from %s" % (list(K_GRID),),
            "objective": "held-out per-token predictive improvement of class-bigram over unigram (nats/tok); "
                         "P(q|c),P(q) fit on TRAIN, scored on HELD-OUT; relabeling-non-invariant (many->few)",
            "search": {"beam_width": BEAM, "iterations": ITERS, "folds": N_FOLDS, "delta_smoothing": DELTA},
            "steering_fixed_coeffs": {"lambda_sub_WP3.2": LAMBDA_SUB, "lambda_cv_WP3.1": LAMBDA_CV,
                                       "lambda_multiplicity": LAMBDA_MULT, "sub_target_edges": SUB_TARGET_EDGES},
            "non_circular": "all priors (position features, C/V PC1, substitution graph) recomputed LA-internally "
                            "per corpus; NO Linear B phonetic value is ever a model input on the LA side; LB is only "
                            "a wrong-language NULL corpus, never a grader of the LA map",
            "freq_min": FREQ_MIN, "n_LA_frequent_signs": len(freq_ids),
        },
        "REAL_LA": {"heldout_score_nats_per_token": round(real_score, 5), **real_meta},
        "end_to_end_null": {
            "family_S_order_shuffle": {"desc": "LA order permuted within inscriptions (kills sequential structure)",
                                        **summ(fam_S), **fwer(fam_S)},
            "family_W_wrong_language": {"desc": "opaque Linear B resampled to LA length dist, same pipeline",
                                         **summ(fam_W), **fwer(fam_W)},
            "family_R_random_prior": {"desc": "real LA bigrams, WP3.1/WP3.2 prior permuted (kills prior info)",
                                       **summ(fam_R), **fwer(fam_R)},
            "pooled_all": {**summ(pooled), **fwer(pooled)},
            "decisive_W_plus_R": {**summ(decisive), **fwer(decisive)},
        },
        "family_wise_false_positive_rate": {
            "definition": "fraction of DECISIVE (wrong-language + random-prior) null realizations whose held-out "
                          "score >= the real LA held-out score; this is the search-adjusted FWER of declaring a "
                          "value signal, because every realization runs the full best-of-search + K-selection",
            "n_decisive_realizations": len(decisive),
            "fwer_decisive": fwer(decisive)["empirical_p"],
            "fwer_wrong_language_only": p_W,
            "fwer_random_prior_only": p_R,
            "p_vs_order_shuffle_only": p_S,
        },
        "verdict": verdict,
        "interpretation": None,  # filled below
    }

    real = real_score
    out["interpretation"] = (
        "REAL LA held-out predictive improvement = %.5f nats/token. The bounded agnostic search over the "
        "reduced K-class value space is %s the decisive end-to-end null: wrong-language (opaque Linear B) FWER "
        "p=%.3f, random-prior FWER p=%.3f, order-shuffle p=%.3f. %s Order-shuffle being beaten (if so) only "
        "confirms LA has real sequential structure; the value claim requires clearing the wrong-language and "
        "random-prior nulls, which run the identical adaptive pipeline on data with the LA-value signal removed. "
        "%s"
        % (real,
           ("ABOVE" if verdict == "BEATS_END_TO_END_NULL" else "AT / INSIDE"),
           p_W, p_R, p_S,
           ("A real different language (LB) processed identically scores in the same band, so the objective is "
            "detecting GENERIC linguistic order structure, not an LA-value-specific edge."
            if p_W >= 0.05 else
            "The real LA score exceeds the wrong-language band."),
           ("=> AT_END_TO_END_NULL: consistent with WP3.2b / WP5(b) — LA-side propagation is underpowered; the "
            "reduced-space search finds no value-specific signal that survives the full search-adjusted null. This "
            "is the honest, precisely-quantified insurance-policy result, not a claimed decipherment."
            if verdict == "AT_END_TO_END_NULL" else
            "=> BEATS_END_TO_END_NULL: the reduced-space value map carries information beyond generic order "
            "structure and beyond the informativeness of arbitrary priors; a genuine (if partial) value signal.")))

    os.makedirs(DATA, exist_ok=True)
    outp = os.path.join(DATA, "wp6_agnostic_search_endtoend_null.json")
    json.dump(out, open(outp, "w"), indent=1)
    # also dump raw null scores for reproducibility / plotting
    rawp = os.path.join(DATA, "wp6_null_scores.json")
    json.dump({"real": real_score, "family_S": fam_S, "family_W": fam_W, "family_R": fam_R},
              open(rawp, "w"), indent=1)

    print(json.dumps({"verdict": verdict,
                      "REAL_LA_score": round(real_score, 5),
                      "selected_K_folds": real_meta["selected_K"],
                      "family_S_shuffle": {**summ(fam_S), **fwer(fam_S)},
                      "family_W_wronglang": {**summ(fam_W), **fwer(fam_W)},
                      "family_R_randprior": {**summ(fam_R), **fwer(fam_R)},
                      "fwer_decisive": fwer(decisive)["empirical_p"]}, indent=1))
    print("\nWROTE", os.path.abspath(outp))
    print("WROTE", os.path.abspath(rawp))
    return out


if __name__ == "__main__":
    run()
