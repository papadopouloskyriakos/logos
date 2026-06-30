#!/usr/bin/env python3
"""validate.py -- the held-out-shared-sign recovery test (the falsifiable crux).

THE TEST (anti-circularity)
---------------------------
The 55 anchor signs are SHARED between Linear A and B and carry INHERITED B-values.
If the alignment has learned anything real, it must recover those values for signs
it was NOT trained on:

  * Split the 55 anchors into TRAIN (80%) and HELD-OUT (20%).
  * Fit each alignment on the TRAIN anchor pairs ONLY.  The held-out signs' B-values
    are NOT used in fitting -- an inherited value cannot be BOTH the anchor that
    teaches the mapping AND the proof that the mapping works.  (This is the
    MUSE/Conneau-2017 held-out-translation protocol.)
  * For each held-out anchor s: map E_A(s) into B-space, take its nearest neighbour
    among ALL B signs.  A HIT iff that neighbour is s's true B counterpart.
  * Bootstrap over >=200 random splits -> mean held-out recovery + 95% CI, vs a
    random-alignment CHANCE baseline (1 / |B signs|, confirmed empirically by a
    uniform-random predictor run through the identical harness).

If recovery is clearly above chance (lower CI > chance), the bet is supported and we
impute A-only values.  Otherwise we do NOT impute and say so -- likely the thin
919-row Linear-B side + the fact that the two scripts write different languages
(Minoan vs Greek), so sign co-occurrence geometries are not guaranteed to be
isomorphic across scripts.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# A seeded uniform-random "alignment" -> empirical chance floor through the same
# harness (so its CI is directly comparable to the real methods).
# ---------------------------------------------------------------------------

class RandomAlign:
    name = "random_chance"

    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)

    def fit(self, EA, EB, pairs):
        return self

    def similarity(self, EA, EB):
        # uniform random score matrix (each A row votes uniformly at random for one B)
        nA, nB = EA.shape[0], EB.shape[0]
        S = np.full((nA, nB), 0.0)
        cols = self.rng.integers(0, nB, size=nA)
        S[np.arange(nA), cols] = 1.0
        return S


# ---------------------------------------------------------------------------
# bootstrap held-out recovery
# ---------------------------------------------------------------------------

def _make_method(factory, aux):
    """Construct a method, feeding structural aux (adjacency/freqs/seqs) if used."""
    try:
        return factory(aux) if aux is not None else factory()
    except TypeError:
        return factory()


def bootstrap_recovery(
    factory: Callable,
    EA: np.ndarray,
    vocabA: Dict[str, int],
    EB: np.ndarray,
    vocabB: Dict[str, int],
    anchors: List[Tuple[str, str]],
    n_splits: int = 200,
    held_frac: float = 0.2,
    seed: int = 0,
    aux=None,
) -> Dict:
    """Return mean / 95% CI held-out recovery for one method factory.

    ``factory`` is a closure taking a single ``seed`` int and returning a method
    object with ``.fit(EA, EB, pairs)`` and ``.similarity(EA, EB) -> S (nA x nB)``.
    """
    rng = np.random.default_rng(seed)
    invB = {i: t for t, i in vocabB.items()}
    idx_pairs = [(vocabA[a], vocabB[b]) for (a, b) in anchors]
    n = len(idx_pairs)
    n_hold = max(1, int(round(n * held_frac)))
    per_split = []
    per_split_hits = []  # (n_hold_this_split, n_hits)
    nB = EB.shape[0]
    for s in range(n_splits):
        perm = rng.permutation(n)
        hold = perm[:n_hold]
        train = perm[n_hold:]
        train_pairs = [idx_pairs[i] for i in train]
        hold_pairs = [idx_pairs[i] for i in hold]
        # fresh seeded method each split (deterministic given seed+s)
        m = factory(seed + s)
        m.fit(EA, EB, train_pairs)
        S = m.similarity(EA, EB)
        hits = 0
        for (ai, bi) in hold_pairs:
            pred_j = int(np.argmax(S[ai]))
            if pred_j == bi:
                hits += 1
        acc = hits / len(hold_pairs)
        per_split.append(acc)
        per_split_hits.append((len(hold_pairs), hits))
    per_split = np.array(per_split)
    # bootstrap CI over per-split accuracies (percentile)
    lo, hi = np.percentile(per_split, [2.5, 97.5])
    return {
        "method": getattr(m, "name", factory.__name__),
        "mean": float(per_split.mean()),
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "per_split": per_split,
        "n_splits": n_splits,
        "n_hold_per_split": n_hold,
        "n_anchors": n,
        "nB": nB,
        "chance_analytic": 1.0 / nB,
    }


# ---------------------------------------------------------------------------
# A-only imputation under the best method (only call if recovery > chance)
# ---------------------------------------------------------------------------

def impute_aonly(
    factory: Callable,
    EA: np.ndarray,
    vocabA: Dict[str, int],
    EB: np.ndarray,
    vocabB: Dict[str, int],
    anchors: List[Tuple[str, str]],
    a_only: List[str],
    a_freq=None,
    n_splits: int = 200,
    seed: int = 0,
) -> List[Dict]:
    """For each A-only sign: modal predicted B-value, bootstrap stability, NN margin.

    Each split fits on a RANDOM train subset of the anchors (same protocol as the
    held-out test) and predicts every A-only sign. Stability = fraction of splits
    whose top-1 prediction equals the modal prediction.  Margin = mean over splits
    of d(nn1)/d(nn2) in cosine space (1.0 = tied, lower = more confident).
    """
    rng = np.random.default_rng(seed)
    invB = {i: t for t, i in vocabB.items()}
    idx_pairs = [(vocabA[a], vocabB[b]) for (a, b) in anchors]
    n = len(idx_pairs)
    n_hold = max(1, int(round(n * 0.2)))
    # predictions[p] = list of predicted B tokens over splits
    preds: Dict[str, List[str]] = {t: [] for t in a_only}
    margins: Dict[str, List[float]] = {t: [] for t in a_only}
    for s in range(n_splits):
        perm = rng.permutation(n)
        train_pairs = [idx_pairs[i] for i in perm[n_hold:]]
        m = factory(seed + s)
        m.fit(EA, EB, train_pairs)
        S = m.similarity(EA, EB)
        for t in a_only:
            ai = vocabA[t]
            row = S[ai]
            order = np.argsort(-row)
            j1, j2 = int(order[0]), int(order[1])
            preds[t].append(invB[j1])
            d1, d2 = float(row[j1]), float(row[j2])
            # margin via "1 - normalised similarity"; smaller ratio = more confident
            denom = abs(d1) + abs(d2) + 1e-12
            margins[t].append((1.0 - d1) / (1.0 - d2 + 1e-12))
    out = []
    for t in a_only:
        pl = preds[t]
        from collections import Counter as _C

        c = _C(pl)
        modal_val, modal_n = c.most_common(1)[0]
        stability = modal_n / len(pl)
        # diversity: how many distinct B values proposed
        out.append(
            {
                "a_only_sign": t,
                "imputed_value": modal_val,
                "stability": round(stability, 3),
                "n_distinct_proposed": len(c),
                "margin_ratio_mean": round(float(np.mean(margins[t])), 3),
                "a_freq_in_corpus": int(a_freq.get(t, 0)) if a_freq else None,
                "top3": [(v, round(cn / len(pl), 2)) for v, cn in c.most_common(3)],
            }
        )
    return out
