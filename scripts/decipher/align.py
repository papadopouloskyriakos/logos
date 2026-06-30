"""align.py — the E-step: align each cipher word to its best plain candidate.

Given the current substitution map ``phi`` (cipher-token -> plain-token), every cipher word
is aligned (via :func:`editdist.align_pairs`) to the plain candidate that minimises the
*weighted* edit distance, subject to a length filter (and optionally a top-k pre-filter for
efficiency). The aligned (cipher-token, plain-token) columns are accumulated across the whole
vocabulary — these are the sufficient statistics for the M-step.

This is the hard-argmax E-step of the combinatorial decipherment EM
(Berg-Kirkpatrick & Klein, 2011). Luo, Cao & Barzilay (2019, "Neural Decipherment via
Minimum-Cost Flow") replace this hard alignment with a soft / neural one; the M-step here is
unchanged in spirit (a global assignment on the pair co-occurrences).

Determinism: candidate iteration order is fixed (plain words in their given order, grouped
by length); ties in minimum edit distance are broken by that order (first wins), so the
result is fully reproducible.
"""

from typing import Dict, List, Optional, Sequence, Tuple

from . import editdist

# A decoded alignment: best plain match, its aligned substitution pairs, and the score.
Alignment = Tuple[Tuple, Tuple[Tuple, ...], float]


def _to_tuple(w: Sequence) -> Tuple:
    return tuple(w)


def best_align(
    cipher_words: Sequence[Sequence],
    plain_words: Sequence[Sequence],
    phi: Optional[Dict] = None,
    sub_cost: float = 1.0,
    indel_cost: float = 1.0,
    max_len_delta: int = 2,
    top_k: Optional[int] = None,
) -> Dict[Tuple, Alignment]:
    """E-step. For each cipher word, pick the minimum-cost plain candidate.

    Parameters
    ----------
    cipher_words, plain_words
        Sequences of token-sequences (lists/tuples of strings). They are normalised to
        tuples internally so they can be used as dict keys.
    phi
        Current substitution map (cipher-token -> plain-token); ``None`` or empty on iter 0.
    max_len_delta
        Only plain words whose token-length is within ``+/- max_len_delta`` of the cipher
        word's length are considered. This is the standard cheap pruner (the B-K&K /
        Snyder line restricts by length and/or top-k).
    top_k
        Optional further pruner: after the length filter, keep only the ``top_k`` plain
        candidates closest in length to the cipher word (ties broken by plain order). Useful
        on very large vocabularies; ``None`` means use every length-filtered candidate.

    Returns
    -------
    dict mapping ``cipher_word_tuple -> (best_plain_tuple, ((c,p),...), score)``.
    Cipher words with no candidate within the length window are omitted.
    """
    phi = phi or {}

    # Index plain candidates by length, in input order (deterministic).
    by_len: Dict[int, List[Tuple]] = {}
    for w in plain_words:
        t = _to_tuple(w)
        by_len.setdefault(len(t), []).append(t)

    out: Dict[Tuple, Alignment] = {}
    for cw in cipher_words:
        c = _to_tuple(cw)
        L = len(c)
        # Gather length-windowed candidates, preserving plain input order across lengths.
        lo = max(0, L - max_len_delta)
        hi = L + max_len_delta
        cands: List[Tuple] = []
        for length in range(lo, hi + 1):
            cands.extend(by_len.get(length, ()))
        if not cands:
            continue
        if top_k is not None and len(cands) > top_k:
            # Keep the top_k closest in length; stable sort preserves plain order on ties.
            cands = sorted(cands, key=lambda p: (abs(len(p) - L),))[:top_k]

        best: Optional[Alignment] = None
        for p in cands:
            score, pairs = editdist.align_pairs(c, p, phi, sub_cost, indel_cost)
            if best is None or score < best[2]:
                best = (p, tuple(pairs), score)
        out[c] = best  # type: ignore[assignment]
    return out


def collect_pairs(alignments: Dict[Tuple, Alignment]) -> List[Tuple]:
    """Flatten the per-word aligned (cipher-token, plain-token) columns into one list.

    This is the input to :func:`maplearn.fit_map`. Only the substitution/match columns
    survive (indels were already dropped in :func:`editdist.align_pairs`).
    """
    pairs: List[Tuple] = []
    for _cw, (_plain, cols, _score) in alignments.items():
        pairs.extend(cols)
    return pairs
