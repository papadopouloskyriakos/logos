"""eval.py — decipherment evaluation metrics.

Three orthogonal measures (the standard decipherment scoreboard):

  (a) :func:`mapping_accuracy` — fraction of cipher tokens whose learned ``phi`` value
      matches the ground-truth substitution map. The "did we recover the alphabet?" metric.
  (b) :func:`cognate_accuracy` — fraction of cipher words whose best plain match is the
      TRUE cognate. The "can we read the words?" metric.
  (c) :func:`mean_edit_distance` — mean weighted edit distance of the chosen alignments;
      a model-fit / residual measure (low is better, but it is not accuracy).

All functions are pure and deterministic.
"""

from typing import Dict, Sequence, Tuple

from . import editdist


def mapping_accuracy(phi: Dict, truth_map: Dict) -> Tuple[float, int, int]:
    """ ``(accuracy, n_correct, n_evaluated)`` for the learned vs true substitution map.

    Only cipher tokens present in ``truth_map`` are evaluated. A token counts as correct iff
    ``phi.get(c) == truth_map[c]`` (unmapped tokens are wrong). ``n_evaluated`` is
    ``len(truth_map)``; ``n_correct / n_evaluated`` is the accuracy.
    """
    n_eval = len(truth_map)
    if n_eval == 0:
        return 0.0, 0, 0
    correct = sum(1 for c in truth_map if phi.get(c) == truth_map[c])
    return correct / n_eval, correct, n_eval


def cognate_accuracy(best_matches: Dict[Tuple, Tuple], true_pairs: Dict[Tuple, Tuple]) -> Tuple[float, int, int]:
    """ ``(accuracy, n_correct, n_evaluated)`` for word-level cognate recovery.

    ``best_matches`` is ``{cipher_word_tuple: chosen_plain_tuple}`` (from the E-step);
    ``true_pairs`` is ``{cipher_word_tuple: true_plain_tuple}``. Only cipher words present
    in ``true_pairs`` are evaluated. A correct read requires an EXACT plain-token-sequence
    match.
    """
    n_eval = len(true_pairs)
    if n_eval == 0:
        return 0.0, 0, 0
    correct = 0
    for cw, tp in true_pairs.items():
        if best_matches.get(cw) == tp:
            correct += 1
    return correct / n_eval, correct, n_eval


def mean_edit_distance(
    alignments: Dict[Tuple, Tuple], phi: Dict, sub_cost: float = 1.0, indel_cost: float = 1.0
) -> float:
    """Mean weighted edit distance of the E-step's chosen alignments under ``phi``.

    ``alignments`` is the output of :func:`align.best_align`
    (``{cipher_word: (best_plain, pairs, score)}``). Recomputes the distance with the FINAL
    ``phi`` so the number reflects the converged map (the stored score used whatever phi was
    current when the alignment was made).
    """
    if not alignments:
        return 0.0
    total = 0.0
    for cw, (plain, _pairs, _score) in alignments.items():
        total += editdist.weighted_edit_distance(cw, plain, phi, sub_cost, indel_cost)
    return total / len(alignments)


def chance_cognate_accuracy(
    cipher_words: Sequence[Sequence],
    plain_words: Sequence[Sequence],
    true_pairs: Dict[Tuple, Tuple],
    max_len_delta: int = 2,
) -> float:
    """Expected cognate accuracy of a length-only random guesser (the null baseline).

    For each cipher word the chance of guessing its true cognate by picking uniformly among
    the plain candidates within the length window is ``1 / (#candidates)``. We average this
    over the cipher words that have a known true pair AND at least one candidate. This is the
    honest "no skill" floor against which :func:`cognate_accuracy` is judged — and the number
    the Linear-A null (``null_linear_a.py``) is expected to land on.
    """
    from collections import Counter

    plain_by_len = Counter(len(tuple(p)) for p in plain_words)
    weighted = 0.0
    n = 0
    for cw, tp in true_pairs.items():
        L = len(tuple(cw))
        cands = sum(
            plain_by_len.get(length, 0)
            for length in range(max(0, L - max_len_delta), L + max_len_delta + 1)
        )
        if cands > 0:
            weighted += 1.0 / cands
            n += 1
    return (weighted / n) if n else 0.0
