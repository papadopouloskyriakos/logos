#!/usr/bin/env python3
"""align_methods.py -- five cross-script alignment methods.

Each method learns, from TRAIN anchors only, a way to map an A-sign embedding into
B-space (or directly a similarity over B signs). Unified interface:

    m.fit(EA, EB, pairs)      # pairs: list of (a_index, b_index) TRAIN anchors
    S = m.similarity(EA, EB)  # S[i, j] = score that A-sign i maps to B-sign j

Prediction = argmax_j S[i, j]; the held-out test scores a hit when the argmax lands
on the true B counterpart.

Methods
-------
  (1) FreqPosition    -- frequency/positional baseline (match by Zipf rank +
                         positional distribution). NO embedding; the floor any
                         embedding method must beat to be meaningful.
  (2) GraphIsoRank    -- seeded graph matching of A/B sign-context networks
                         (IsoRank: R <- alpha A R B^T + (1-alpha) R0). Distinct
                         from Procrustes -- uses graph topology + seed propagation.
  (3) CCA             -- sklearn CCA fitted on the train anchors; project both
                         spaces into the shared canonical-correlation space.
  (4) Procrustes      -- orthogonal Procrustes, the MUSE / Mikolov-2013 method:
                         W = argmin ||W EA - EB|| via SVD, W orthogonal.
  (5) SinkhornOT      -- entropic optimal transport with anchors as soft
                         (cost-discounted) constraints.

References: Mikolov, Le, Sutskever 2013 (Procrustes bilingual alignment);
Conneau et al. 2017, MUSE (the unsupervised + anchor evaluation protocol we follow);
Bayati, Gleich, Saberi 2013 / Singh, Xu, Berger 2007 (IsoRank seeded graph matching);
Cuturi 2013 (Sinkhorn for OT). Bouchard-Cote et al. 2013 is the cognate-based
alternative we deliberately do NOT use (needs cognates; script-borrowing gives us
shared phonetic anchors without them).
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np
from scipy.linalg import svd as scipy_svd
from sklearn.cross_decomposition import CCA


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------

def _cosine_mat(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Row-vs-row cosine similarity matrix (nX x nY)."""
    xn = np.linalg.norm(X, axis=1, keepdims=True)
    yn = np.linalg.norm(Y, axis=1, keepdims=True)
    xn[xn == 0] = 1.0
    yn[yn == 0] = 1.0
    return (X / xn) @ (Y / yn).T


# ---------------------------------------------------------------------------
# (1) Frequency / positional baseline
# ---------------------------------------------------------------------------

class FreqPosition:
    """Match signs by (normalised log-frequency, mean rel. position, pos. spread).

    A pure-distributional floor: if embedding methods cannot beat this, their
    'geometry' adds nothing over Zipf + word-edge habits.
    """

    name = "freq_position"
    needs = ("a_seqs", "b_seqs", "vocabA", "vocabB")

    def __init__(self, a_seqs, b_seqs, vocabA, vocabB):
        self.fa = self._features(a_seqs, vocabA)
        self.fb = self._features(b_seqs, vocabB)

    @staticmethod
    def _features(seqs, vocab):
        V = len(vocab)
        cnt = np.zeros(V)
        pos_sum = np.zeros(V)
        pos_sq = np.zeros(V)
        for s in seqs:
            n = len(s)
            if n == 0:
                continue
            for k, t in enumerate(s):
                if t not in vocab:
                    continue
                i = vocab[t]
                r = k / max(n - 1, 1)  # relative position 0..1
                cnt[i] += 1
                pos_sum[i] += r
                pos_sq[i] += r * r
        freq = np.log1p(cnt)
        mean = np.where(cnt > 0, pos_sum / np.maximum(cnt, 1), 0.0)
        var = np.where(cnt > 0, pos_sq / np.maximum(cnt, 1) - mean**2, 0.0)
        var = np.clip(var, 0, None)
        std = np.sqrt(var)
        feat = np.stack([freq, mean, std], axis=1)
        feat = (feat - feat.mean(0, keepdims=True)) / (feat.std(0, keepdims=True) + 1e-9)
        return feat

    def fit(self, EA, EB, pairs):
        return self  # nothing to learn -- it is a static baseline

    def similarity(self, EA, EB):
        return _cosine_mat(self.fa, self.fb)


# ---------------------------------------------------------------------------
# (2) Seeded graph alignment (IsoRank)
# ---------------------------------------------------------------------------

class GraphIsoRank:
    """Seeded graph matching via similarity propagation on co-occurrence graphs.

    R_{t+1} = alpha * A_norm @ R_t @ B_norm^T + (1-alpha) * R_seed
    A_norm, B_norm are row-stochastic sign-sign co-occurrence adjacency matrices.
    Seed R_seed has mass 1/|anchors| on each TRAIN anchor pair, 0 elsewhere.
    """

    name = "graph_isorank"

    def __init__(self, A_adj, B_adj, alpha=0.7, iters=40):
        self.A = self._stochastic(A_adj)
        self.B = self._stochastic(B_adj)
        self.alpha = alpha
        self.iters = iters
        self.seed = None

    @staticmethod
    def _stochastic(M):
        rs = M.sum(axis=1, keepdims=True)
        rs[rs == 0] = 1.0
        return M / rs

    def fit(self, EA, EB, pairs):
        nA, nB = self.A.shape[0], self.B.shape[0]
        R0 = np.zeros((nA, nB))
        if pairs:
            w = 1.0 / len(pairs)
            for a, b in pairs:
                R0[a, b] = w
        self.seed = R0
        return self

    def similarity(self, EA, EB):
        R = self.seed.copy()
        Bt = self.B.T
        for _ in range(self.iters):
            R = self.alpha * (self.A @ R @ Bt) + (1.0 - self.alpha) * self.seed
            # row-normalise to keep it a distribution over B for each A node
            rs = R.sum(axis=1, keepdims=True)
            rs[rs == 0] = 1.0
            R = R / rs
        return R


# ---------------------------------------------------------------------------
# (3) CCA
# ---------------------------------------------------------------------------

class CCAAlign:
    """Canonical Correlation Alignment (sklearn CCA) on the train anchors."""

    name = "cca"

    def __init__(self, n_components=None):
        self.n_components = n_components
        self.cca = None

    def fit(self, EA, EB, pairs):
        a_idx = np.array([p[0] for p in pairs])
        b_idx = np.array([p[1] for p in pairs])
        X = EA[a_idx]
        Y = EB[b_idx]
        nc = self.n_components or min(len(pairs) - 1, X.shape[1], Y.shape[1])
        nc = max(min(nc, len(pairs) - 1), 1)
        self.cca = CCA(n_components=nc, scale=False, max_iter=2000)
        self.cca.fit(X, Y)
        return self

    def similarity(self, EA, EB):
        Xc, Yc = self.cca.transform(EA, EB)
        return _cosine_mat(Xc, Yc)


# ---------------------------------------------------------------------------
# (4) Orthogonal Procrustes (MUSE / Mikolov 2013)
# ---------------------------------------------------------------------------

class Procrustes:
    """W = argmin ||W EA - EB||_F  s.t. W^T W = I.  Mikolov 2013 / MUSE."""

    name = "procrustes"

    def __init__(self):
        self.W = None

    def fit(self, EA, EB, pairs):
        a_idx = np.array([p[0] for p in pairs])
        b_idx = np.array([p[1] for p in pairs])
        X = EA[a_idx]
        Y = EB[b_idx]
        # centre (MUSE mean-centres anchors) then solve
        mx, my = X.mean(0), Y.mean(0)
        Xc = X - mx
        Yc = Y - my
        M = Yc.T @ Xc  # (dB x dA)
        U, S, Vt = scipy_svd(M, full_matrices=False)
        self.W = U @ Vt  # (dB x dA) orthogonal
        self.mx = mx
        self.my = my
        return self

    def similarity(self, EA, EB):
        Xc = EA - self.mx
        mapped = Xc @ self.W.T  # -> B-space
        # re-normalise rows (cosine NN)
        return _cosine_mat(mapped, EB)


# ---------------------------------------------------------------------------
# (5) Sinkhorn optimal transport with soft anchors
# ---------------------------------------------------------------------------

class SinkhornOT:
    """Entropic OT. Anchors act as soft constraints via cost discounting.

    Source mass = A sign frequency, target mass = B sign frequency. The transport
    plan T assigns 'flow' from A signs to B signs; a high T[i,j] means i~j.
    Train anchor pairs get their cost heavily discounted so flow prefers them.
    """

    name = "sinkhorn_ot"

    def __init__(self, fa, fb, reg=0.10, anchor_discount=0.05, iters=200):
        self.fa = fa / (fa.sum() + 1e-12)
        self.fb = fb / (fb.sum() + 1e-12)
        self.reg = reg
        self.anchor_discount = anchor_discount
        self.iters = iters
        self.cost_mask = None  # multiplicative cost mask (1 default, discount on anchors)

    def fit(self, EA, EB, pairs):
        nA, nB = EA.shape[0], EB.shape[0]
        mask = np.ones((nA, nB))
        if pairs:
            for a, b in pairs:
                mask[a, b] = self.anchor_discount
        self.cost_mask = mask
        return self

    def similarity(self, EA, EB):
        # squared-euclidean cost on the (already L2-normalised) embeddings -> in [0,4]
        C = np.sum((EA[:, None, :] - EB[None, :, :]) ** 2, axis=2)
        C = C * self.cost_mask
        # Sinkhorn (log-domain stabilised)
        loga = np.log(self.fa + 1e-12)
        logb = np.log(self.fb + 1e-12)
        log_K = -C / self.reg
        log_u = np.zeros_like(self.fa)
        log_v = np.zeros_like(self.fb)
        for _ in range(self.iters):
            # log f = loga - logsumexp_j (log_K + log_v)
            log_u = loga - self._lse_rows(log_K + log_v[None, :])
            log_v = logb - self._lse_cols(log_K + log_u[:, None])
        log_T = log_K + log_u[:, None] + log_v[None, :]
        T = np.exp(log_T)
        return T / (T.sum(1, keepdims=True) + 1e-12)  # row-normalise -> P(B|A)

    @staticmethod
    def _lse_rows(M):
        """logsumexp over axis=1 (collapse columns) -> shape (nA,)."""
        m = M.max(axis=1)
        return m + np.log(np.exp(M - m[:, None]).sum(axis=1))

    @staticmethod
    def _lse_cols(M):
        """logsumexp over axis=0 (collapse rows) -> shape (nB,)."""
        m = M.max(axis=0)
        return m + np.log(np.exp(M - m[None, :]).sum(axis=0))
