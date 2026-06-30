#!/usr/bin/env python3
"""embeddings.py -- distributional sign embeddings (PPMI + TruncatedSVD).

For each script we build, per sign, a distributional vector in a shared ``d``-dim
space: PPMI (positive pointwise mutual information) co-occurrence within a sliding
window over sign sequences, then TruncatedSVD to ``d`` dimensions.  So E_A(sign)
and E_B(sign) live in a comparable ``d``-space, bridged only by the 55 anchor pairs
(the supervision is added later, in the alignment step -- NOT here).

This is the standard distributional-semantics recipe (Levy & Goldberg 2014,
"Neural Word Embedding as Implicit Matrix Factorization"; PPMI+SVD is the
linear-algebra equivalent of word2vec-skipgram-with-negative-sampling).  Applied
here to SIGNS (not words): a sign's meaning-as-distribution is the company it
keeps within a window, where the "company" is other signs in the same
inscription (A side) or word (B side).

Anti-circularity note: embeddings are built UNSUPERVISED from raw corpora. The
held-out anchors are withheld only from the ALIGNMENT fit, never from the
embedding construction -- exactly the MUSE evaluation protocol (Conneau 2017).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np
from sklearn.decomposition import TruncatedSVD


def build_vocab(seqs: List[List[str]]) -> Dict[str, int]:
    """sign -> column index (stable: sorted alphabetically for determinism)."""
    toks = sorted({t for s in seqs for t in s})
    return {t: i for i, t in enumerate(toks)}


def cooccurrence(
    seqs: List[List[str]], vocab: Dict[str, int], window: int = 2
) -> np.ndarray:
    """Symmetric within-window co-occurrence count matrix (focus x context).

    Weight 1/distance (Levy-Goldberg), symmetric: for focus at i, each context at
    i±d (d=1..window) contributes 1/d.  Window=2 (close phonotactic neighbours).
    """
    V = len(vocab)
    C = np.zeros((V, V), dtype=np.float64)
    for s in seqs:
        idx = [vocab[t] for t in s if t in vocab]
        n = len(idx)
        for i in range(n):
            for d in range(1, window + 1):
                w = 1.0 / d
                if i - d >= 0:
                    C[idx[i], idx[i - d]] += w
                if i + d < n:
                    C[idx[i], idx[i + d]] += w
    return C


def ppmi(C: np.ndarray, cds: float = 0.75, k: int = 1) -> np.ndarray:
    """Positive PMI with optional context-distributional smoothing (cds).

    cds<1 flattens the context marginal (Levy & Goldberg 2014 eq. 5 / shifted PMI
    with neg-k); ``k`` is the negative-sample shift subtracted from PMI.  All PMIs
    clipped at 0.  Pure numpy.
    """
    total = C.sum()
    row = C.sum(axis=1, keepdims=True)          # P(focus)
    col = C.sum(axis=0, keepdims=True)          # P(context)
    # context-distributional smoothing
    col_smooth = col ** cds
    col_smooth = col_smooth / col_smooth.sum() if col_smooth.sum() > 0 else col_smooth
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((C * total) / (row * col_smooth * total) + 1e-12) - np.log(k)
    pmi = np.nan_to_num(pmi, nan=0.0, posinf=0.0, neginf=0.0)
    return np.maximum(pmi, 0.0)


def embed(
    seqs: List[List[str]],
    d: int = 24,
    window: int = 2,
    cds: float = 0.75,
    seed: int = 0,
) -> Tuple[Dict[str, int], np.ndarray]:
    """Return (vocab, embeddings) with embeddings L2-row-normalised, shape (V, d).

    embeddings[i] is the d-vector for sign with vocab-index i.
    """
    vocab = build_vocab(seqs)
    C = cooccurrence(seqs, vocab, window=window)
    P = ppmi(C, cds=cds)
    # TruncatedSVD: keep min(d, rank) components. n_components must be < n_features.
    nc = min(d, P.shape[1] - 1, P.shape[0] - 1)
    nc = max(nc, 1)
    svd = TruncatedSVD(n_components=nc, random_state=seed)
    E = svd.fit_transform(P)  # U * S  (n_samples x nc)
    # zero-pad if nc < d so both scripts share the same column count
    if E.shape[1] < d:
        E = np.hstack([E, np.zeros((E.shape[0], d - E.shape[1]))])
    # L2 row-normalise (cosine geometry -- required for Procrustes / NN search)
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    E = E / norms
    return vocab, E


def embed_many(
    seqs: List[List[str]], dims=(16, 24, 32), window: int = 2, seed: int = 0
) -> Dict[int, Tuple[Dict[str, int], np.ndarray]]:
    """Embed at several d values (for the d-sweep)."""
    vocab = build_vocab(seqs)
    C = cooccurrence(seqs, vocab, window=window)
    P = ppmi(C)
    out = {}
    for d in dims:
        nc = min(d, P.shape[1] - 1, P.shape[0] - 1)
        nc = max(nc, 1)
        svd = TruncatedSVD(n_components=nc, random_state=seed)
        E = svd.fit_transform(P)
        if E.shape[1] < d:
            E = np.hstack([E, np.zeros((E.shape[0], d - E.shape[1]))])
        norms = np.linalg.norm(E, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        out[d] = (vocab, E / norms)
    return out


if __name__ == "__main__":
    from . import data as D

    a_inv, a_seqs, a_freq = D.load_a()
    b_seqs, b_freq, _ = D.load_b()
    for label, seqs in (("A", a_seqs), ("B", b_seqs)):
        vocab, E = embed(seqs, d=24)
        print(f"{label}: V={len(vocab)} E={E.shape} nnz-rows={int((E.sum(1)!=0).sum())}")
