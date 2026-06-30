"""editdist.py — weighted edit distance + alignment, the E-step's local scorer.

Implements the Needleman-Wunsch / Wagner-Fischer dynamic program with a *phi-dependent*
substitution cost, as used by the unsupervised decipherment EM
(Berg-Kirkpatrick & Klein, 2011; Snyder, Barzilay & Knight, 2010; Luo, Cao & Barzilay,
2019 — "Neural Decipherment via Minimum-Cost Flow", whose non-neural core this is).

The substitution cost of writing cipher-token ``c`` as plain-token ``p`` is::

    sub_cost(c, p) = 0.0          if phi.get(c) == p        (the current map agrees)
                   = sub_cost     otherwise                (default 1.0)

and every insertion / deletion costs ``indel_cost`` (default 1.0). On iteration 0 phi is
empty/identity, so every substitution costs ``sub_cost`` and the distance reduces to plain
Levenshtein — the cold-start behaviour.

Tokens are elements of the input sequences; they may be single characters (a Latin cipher)
or multi-character sign strings (Linear A syllabograms). Pure Python (no numpy needed here)
so the DP works on arbitrary hashable tokens.
"""

from typing import Sequence, Tuple, List, Dict, Optional


def _sub_cost(c, p, phi: Dict, sub_cost: float) -> float:
    """0 if the current map phi sends c->p, else sub_cost. Missing key => mismatch."""
    return 0.0 if phi.get(c) == p else sub_cost


def weighted_edit_distance(
    a: Sequence,
    b: Sequence,
    phi: Optional[Dict] = None,
    sub_cost: float = 1.0,
    indel_cost: float = 1.0,
) -> float:
    """Minimum weighted edit distance turning cipher sequence ``a`` into plain sequence ``b``.

    Wagner-Fischer DP. ``phi`` (cipher-token -> plain-token) makes an agreeing substitution
    free; all other substitutions cost ``sub_cost``; indels cost ``indel_cost``.
    Returns a float (the minimal cost). O(len(a)*len(b)).
    """
    phi = phi or {}
    n, m = len(a), len(b)
    # dp[i][j] = min cost to convert a[:i] -> b[:j]
    # Use a 1-D rolling array for memory; we keep the full table only in align_pairs.
    prev = [j * indel_cost for j in range(m + 1)]
    cur = [0.0] * (m + 1)
    for i in range(1, n + 1):
        cur[0] = i * indel_cost
        ai = a[i - 1]
        for j in range(1, m + 1):
            diag = prev[j - 1] + _sub_cost(ai, b[j - 1], phi, sub_cost)
            up = prev[j] + indel_cost          # delete a[i-1]
            left = cur[j - 1] + indel_cost     # insert b[j-1]
            d = diag
            if up < d:
                d = up
            if left < d:
                d = left
            cur[j] = d
        prev, cur = cur, prev
    return float(prev[m])


def align_pairs(
    a: Sequence,
    b: Sequence,
    phi: Optional[Dict] = None,
    sub_cost: float = 1.0,
    indel_cost: float = 1.0,
) -> Tuple[float, List[Tuple]]:
    """Align ``a`` (cipher) to ``b`` (plain) and return ``(score, substitution_pairs)``.

    Performs the Needleman-Wunsch DP with the same phi-dependent costs as
    :func:`weighted_edit_distance`, then traces back. The returned list contains the
    aligned ``(cipher_token, plain_token)`` columns in left-to-right order — i.e. the
    positions where both sequences emit a token (substitutions / matches). Insertions and
    deletions (indels) are SKIPPED, exactly as the EM E-step requires (indels carry no
    character-correspondence information).

    Traceback tie-break is deterministic: prefer the diagonal (substitution/match), then the
    up move (deletion), then the left move (insertion). This fixed order makes the whole
    engine reproducible.
    """
    phi = phi or {}
    n, m = len(a), len(b)
    # Full DP table (we need it for traceback). dp[i][j] = min cost a[:i]->b[:j].
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i * indel_cost
    for j in range(1, m + 1):
        dp[0][j] = j * indel_cost
    for i in range(1, n + 1):
        ai = a[i - 1]
        row = dp[i]
        prow = dp[i - 1]
        for j in range(1, m + 1):
            diag = prow[j - 1] + _sub_cost(ai, b[j - 1], phi, sub_cost)
            up = prow[j] + indel_cost
            left = row[j - 1] + indel_cost
            d = diag
            if up < d:
                d = up
            if left < d:
                d = left
            row[j] = d

    # Traceback from (n, m). Tie-break order: diag > up > left.
    pairs: List[Tuple] = []
    i, j = n, m
    while i > 0 and j > 0:
        ai = a[i - 1]
        diag_cost = dp[i - 1][j - 1] + _sub_cost(ai, b[j - 1], phi, sub_cost)
        up_cost = dp[i - 1][j] + indel_cost
        left_cost = dp[i][j - 1] + indel_cost
        cur = dp[i][j]
        if cur == diag_cost:                      # substitution / match (preferred)
            pairs.append((ai, b[j - 1]))
            i -= 1
            j -= 1
        elif cur == up_cost:                      # deletion of a[i-1]
            i -= 1
        else:                                     # insertion of b[j-1]
            j -= 1
    pairs.reverse()
    return float(dp[n][m]), pairs
