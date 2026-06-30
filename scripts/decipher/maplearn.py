"""maplearn.py — the M-step: learn the global substitution map from aligned pairs.

From the E-step's aligned ``(cipher_token, plain_token)`` columns we build a cipher-x-plain
co-occurrence COUNT matrix, convert it to a COST matrix (``cost = -count``), and solve the
global 1-1 assignment with ``scipy.optimize.linear_sum_assignment``. The minimum-cost
matching on ``-count`` IS the maximum-co-occurrence assignment — i.e. the bipartite
min-cost flow under a 1-1 policy (Luo, Cao & Barzilay, 2019, "Neural Decipherment via
Minimum-Cost Flow", use a true min-cost flow that permits many-to-one; the 1-1 Hungarian
matching here is the clean numpy baseline, see LIMITATION below).

Citation: this M-step is the combinatorial core of Berg-Kirkpatrick & Klein (2011) and the
non-neural half of Luo et al. (2019).

Determinism: ``linear_sum_assignment`` is the Jonker-Volgenant algorithm and is fully
deterministic given the cost matrix; the row/col orderings are fixed (sorted token strings),
so the learned ``phi`` is reproducible.

LIMITATION (1-1 policy): a 1-1 assignment forces each cipher token onto exactly one plain
token. Real scripts can be polyphonic (one sign, several sounds) or homophonic (several
signs, one sound) — B-K&K allow a cipher char to map to a small SET. To represent
many-to-one / set-valued maps one needs a genuine min-cost flow (or a small per-cipher
allowance) instead of a matching; this baseline deliberately does not, and the docstrings
flag it. On clean monophonic synthetic data (the self-test) 1-1 is exact.
"""

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import linear_sum_assignment


def build_count_matrix(
    aligned_pairs: Iterable[Tuple],
    cipher_chars: Optional[List] = None,
    plain_chars: Optional[List] = None,
    smoothing: float = 0.0,
) -> Tuple[np.ndarray, List, List]:
    """Build the cipher-x-plain co-occurrence count matrix from aligned pairs.

    Parameters
    ----------
    aligned_pairs
        Iterable of ``(cipher_token, plain_token)`` columns from the E-step.
    cipher_chars, plain_chars
        Optional fixed row/column orderings. If ``None`` they are derived (sorted) from the
        pairs actually observed. Tokens unseen in ``aligned_pairs`` never appear, so by
        construction every row/column has a real count (smoothing notwithstanding).
    smoothing
        Value added to EVERY cell of the count matrix (Laplace-style). Useful if a later
        variant divides by the count; with ``cost = -count`` smoothing does not move the
        argmin but keeps the matrix dense and non-degenerate. Default 0.

    Returns
    ``(count_matrix, cipher_chars, plain_chars)`` where the matrix rows are indexed by
    ``cipher_chars`` and columns by ``plain_chars``.
    """
    observed_cipher = set()
    observed_plain = set()
    tallies: Dict[Tuple, float] = {}
    for c, p in aligned_pairs:
        observed_cipher.add(c)
        observed_plain.add(p)
        tallies[(c, p)] = tallies.get((c, p), 0.0) + 1.0

    if cipher_chars is None:
        cipher_chars = sorted(observed_cipher)
    if plain_chars is None:
        plain_chars = sorted(observed_plain)

    ci = {c: i for i, c in enumerate(cipher_chars)}
    pj = {p: j for j, p in enumerate(plain_chars)}
    M = np.full((len(cipher_chars), len(plain_chars)), float(smoothing), dtype=float)
    for (c, p), n in tallies.items():
        i, j = ci.get(c), pj.get(p)
        if i is not None and j is not None:
            M[i, j] += n
    return M, cipher_chars, plain_chars


def fit_map(
    aligned_pairs: Iterable[Tuple],
    cipher_chars: Optional[List] = None,
    plain_chars: Optional[List] = None,
    smoothing: float = 0.0,
) -> Dict:
    """M-step. Solve the global 1-1 substitution map from aligned pairs.

    Constructs the count matrix (:func:`build_count_matrix`), forms ``cost = -count`` and
    runs :func:`scipy.optimize.linear_sum_assignment`. Returns ``phi`` (cipher-token ->
    plain-token) for the matched pairs.

    Cipher tokens absent from ``aligned_pairs`` are *not* in ``cipher_chars`` and therefore
    absent from ``phi`` (they are left UNMAPPED, per the spec); callers treat a missing key
    as a full-cost substitution.

    On a rectangular inventory (e.g. 259 Linear-A signs vs 26 Latin letters) only
    ``min(|cipher|, |plain|`` tokens get mapped — the 1-1 limitation noted above.
    """
    M, cipher_chars, plain_chars = build_count_matrix(
        aligned_pairs, cipher_chars, plain_chars, smoothing
    )
    if M.size == 0 or len(cipher_chars) == 0 or len(plain_chars) == 0:
        return {}

    # Min-cost 1-1 matching on -count  ==  max-co-occurrence assignment.
    cost = -M
    row_ind, col_ind = linear_sum_assignment(cost)
    phi: Dict = {}
    for i, j in zip(row_ind, col_ind):
        phi[cipher_chars[i]] = plain_chars[j]
    return phi


def frequency_init(
    cipher_words: Iterable[Sequence], plain_words: Iterable[Sequence]
) -> Dict:
    """Deterministic frequency-rank cold start (Snyder et al. 2010 / standard in this line).

    Maps the k-th most frequent cipher token to the k-th most frequent plain token.
    Frequency is preserved under a monophonic substitution (encoding is a relabelling, so the
    cipher token that is the image of plain token p inherits p's count), so on clean
    monophonic data this is already the correct map modulo frequency ties — it is the
    principled way to avoid the E-step's length-only cold-start degeneracy on disjoint
    alphabets. Ties are broken by token sort order (deterministic).

    Used by :func:`decipher.run_em` when ``init="frequency"``.
    """
    from collections import Counter

    def rank(words):
        cnt = Counter()
        for w in words:
            cnt.update(w)
        # Sort by (count desc, token asc) for a deterministic total order.
        return [tok for tok, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]

    c_rank = rank(cipher_words)
    p_rank = rank(plain_words)
    phi: Dict = {}
    for c, p in zip(c_rank, p_rank):
        phi[c] = p
    return phi
