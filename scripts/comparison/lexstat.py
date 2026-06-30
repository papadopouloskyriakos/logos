#!/usr/bin/env python3
"""lexstat.py — minimal S_lex: deflated lexeme recall (logos comparison-layer §A.2, refinement F.1).

S_lex is the *Gordon failure-mode metric*: the fraction of held-out forms that fall within
regular-correspondence edit distance epsilon of SOME candidate lexeme. It is cheap to score and
easy to fool — exactly the statistic a Gordon/Di Mino-style match inflates by searching a huge
root x vowel x language space, which is why the design makes it the pragmatic primary (F.1) and
HAMMERS it with the null + the L_fake canary (§B.1, §C.3).

This module is the minimum needed to run L_fake (and any candidate) through a comparison statistic:

  - normalized_edit_distance(a, b)   = Levenshtein(a,b) / max(|a|,|b|)  in [0,1]
  - within_epsilon(form, lexicon, e) = any lexeme within normalized distance e of form
  - s_lex(heldout, lexicon, e)       = recall fraction (raw S_lex)
  - deflated_s_lex(...)              = recall deflated by the null expectation (recall - mean_null)

Normalized edit distance makes epsilon length-invariant (a 1-edit gap is not the same distance in a
2-char and an 8-char word). The DP is banded with early-exit: because NED <= e implies the absolute
edit distance <= e*max(|a|,|b|), the Wagner-Fischer row minimum can abandon once it exceeds that cap.

Pure stdlib (the DP); numpy only for the vectorized batch when callers want a full distance matrix.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

CITATION_DESIGN = (
    "logos comparison-layer §A.2 (S_lex = deflated lexeme recall, the Gordon failure-mode metric) "
    "and refinement F.1 (deflated S_lex is the pragmatic primary; S_morph is gold-standard-if-the-"
    "corpus-cooperates)."
)


# --------------------------------------------------------------------------- #
# Normalized edit distance with banded early-exit
# --------------------------------------------------------------------------- #
def edit_distance(a: str, b: str) -> int:
    """Plain Levenshtein distance (Wagner-Fischer). Pure Python."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        ai = a[i - 1]
        for j in range(1, lb + 1):
            cost = 0 if ai == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[lb]


def normalized_edit_distance(a: str, b: str) -> float:
    """Levenshtein(a,b) / max(|a|,|b|), in [0,1]. 0 iff equal; 1.0 for total mismatch.

    Length-normalized so epsilon is comparable across short and long forms (a 1-edit match on a
    2-char word is a 0.5 distance, on an 8-char word a 0.125 distance).
    """
    m = max(len(a), len(b))
    if m == 0:
        return 0.0
    return edit_distance(a, b) / m


def ned_capped(a: str, b: str, eps: float) -> bool:
    """True iff normalized_edit_distance(a,b) <= eps, with an early-exit DP.

    NED <= eps implies |edit_distance| <= eps * max(|a|,|b|); we compute the integer cap on
    admissible absolute edits, prune on the length gap, and abandon the Wagner-Fischer DP as soon
    as the running ROW MINIMUM exceeds the cap (no cell in a row can later recover once every cell
    is above cap, since edit distance is non-decreasing along a row's downward path). Correctness
    first (full DP), with the length + row-minimim exits giving the speed needed for multi-
    thousand-form lexicons.
    """
    if a == b:
        return True
    la, lb = len(a), len(b)
    m = max(la, lb)
    if m == 0:
        return True
    cap = int(np.floor(eps * m))            # max admissible absolute edits
    if abs(la - lb) > cap:                   # length gap alone exceeds cap -> cannot be within eps
        return False
    if cap == 0:
        return a == b
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        ai = a[i - 1]
        row_min = la + lb
        for j in range(1, lb + 1):
            cost = 0 if ai == b[j - 1] else 1
            v = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            cur[j] = v
            if v < row_min:
                row_min = v
        if row_min > cap:
            return False                    # every reachable cell this row > cap -> outside epsilon
        prev = cur
    return prev[lb] <= cap


# --------------------------------------------------------------------------- #
# S_lex — deflated lexeme recall
# --------------------------------------------------------------------------- #
def within_epsilon(form: str, lexicon: Sequence[str], eps: float,
                   length_index: Optional[Dict[int, List[str]]] = None) -> bool:
    """True if any lexeme is within normalized edit distance ``eps`` of ``form``."""
    if length_index is not None:
        m = len(form)
        cap = int(np.floor(eps * m))
        # only lexemes whose length is within cap of |form| can qualify
        for L in range(max(1, m - cap), m + cap + 1):
            for cand in length_index.get(L, ()):
                if ned_capped(form, cand, eps):
                    return True
        return False
    for cand in lexicon:
        if ned_capped(form, cand, eps):
            return True
    return False


def build_length_index(lexicon: Sequence[str]) -> Dict[int, List[str]]:
    """Bucket lexemes by length so within_epsilon only scans length-plausible candidates."""
    idx: Dict[int, List[str]] = {}
    for w in lexicon:
        idx.setdefault(len(w), []).append(w)
    return idx


def s_lex(heldout_forms: Sequence[str], candidate_lexicon: Sequence[str],
          eps: float = 0.25) -> float:
    """Raw S_lex: fraction of held-out forms within normalized edit distance ``eps`` of a lexeme.

    This is the un-deflated recall — high for BOTH real cognates and well-shaped chance matches,
    which is precisely why it must be deflated (see :func:`deflated_s_lex`) and beaten against the
    L_fake canary distribution.
    """
    if not heldout_forms:
        return 0.0
    idx = build_length_index(candidate_lexicon)
    hits = sum(1 for w in heldout_forms if within_epsilon(w, candidate_lexicon, eps, idx))
    return hits / len(heldout_forms)


def s_lex_per_form(heldout_forms: Sequence[str], candidate_lexicon: Sequence[str],
                   eps: float = 0.25) -> List[int]:
    """Per-form hit indicators (1/0) — useful for bootstrap CIs and per-form analysis."""
    idx = build_length_index(candidate_lexicon)
    return [1 if within_epsilon(w, candidate_lexicon, eps, idx) else 0 for w in heldout_forms]


def deflated_s_lex(heldout_forms: Sequence[str], candidate_lexicon: Sequence[str],
                   eps: float, null_recalls: Sequence[float]) -> float:
    """Deflated S_lex = raw recall - mean(null recall), clipped at 0.

    The deflation subtracts the expected recall under the null generators (Packard / random-lexeme /
    within-form; see nulls.py). A real correspondence registers only to the extent it BEATS that
    null expectation — the core of the §B.3 deflated bar at the statistic level.

    A negative raw-minus-null is reported as 0 (no evidence above chance); the raw and null means
    should still be reported separately for honesty (a synthetic baseline is not ground truth).
    """
    raw = s_lex(heldout_forms, candidate_lexicon, eps)
    if not null_recalls:
        return raw
    mu0 = float(np.mean(null_recalls))
    return max(0.0, raw - mu0)


def expected_chance_recall(heldout_forms: Sequence[str], alphabet: Sequence[str],
                            eps: float = 0.25, n_mc: int = 200, seed: int = 0,
                            length_dist: Optional[Dict[int, float]] = None) -> float:
    """Monte-Carlo estimate of the S_lex expected under random strings of the given alphabet.

    Draws ``n_mc`` random-form lexicons (same size + length distribution as heldout) and averages
    S_lex(heldout, random_lexicon). This is an INDEPENDENT chance baseline — a cross-check on the
    null generators (which permute real forms). It is not a substitute for the L_fake floor.
    """
    rng = np.random.default_rng(seed)
    alph = list(alphabet)
    if not alph:
        return 0.0
    lens = sorted(length_dist) if length_dist else sorted({len(w) for w in heldout_forms})
    if not lens:
        return 0.0
    if length_dist:
        lp = np.array([length_dist[L] for L in lens], dtype=float)
        lp /= lp.sum()
    else:
        lp = None
    n_lex = max(len(heldout_forms), 1)
    recalls = []
    for _ in range(n_mc):
        lex = []
        for _ in range(n_lex):
            if lp is not None:
                L = int(rng.choice(lens, p=lp))
            else:
                L = int(rng.choice(lens))
            lex.append("".join(rng.choice(alph, size=L).tolist()))
        recalls.append(s_lex(heldout_forms, lex, eps))
    return float(np.mean(recalls))


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse, json
    p = argparse.ArgumentParser(description="S_lex — deflated lexeme recall")
    p.add_argument("--heldout", nargs="+", required=True)
    p.add_argument("--lexicon", nargs="+", required=True)
    p.add_argument("--eps", type=float, default=0.25)
    args = p.parse_args(argv)
    raw = s_lex(args.heldout, args.lexicon, args.eps)
    print(json.dumps({"eps": args.eps, "s_lex": raw, "n_heldout": len(args.heldout),
                      "n_lexicon": len(args.lexicon)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
