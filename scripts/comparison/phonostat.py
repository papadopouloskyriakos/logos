#!/usr/bin/env python3
"""phonostat.py — minimal S_phono: held-out phonotactic plausibility (logos comparison-layer §A.2).

S_phono is the *weakest* of the three held-out statistics (§A.2): "log-likelihood of held-out
word-forms under an L-phonotactic n-gram model built from L's known lexicon. (Weak: surface
plausibility.)" It asks only "do the committed-map outputs LOOK like L-shaped words?" — a necessary
but cheap-to-satisfy condition, reported beneath S_lex (the pragmatic primary, F.1) and S_morph.

This module is the minimum needed to score any candidate (and L_fake) through that surface filter:

  - fit(lexicon, order)              = an order-n character/sign-level add-k n-gram model over L's
                                       known lexemes, with begin/end sentinels.
  - logprob_form(model, form)        = total natural-log probability of one form under the model.
  - s_phono_per_form(heldout, L, ord)= per-form length-normalized (per-emitted-symbol) log-likelihood
                                       — the bootstrap/CI hook, mirroring lexstat.s_lex_per_form.
  - s_phono(heldout, L, order)       = MEAN per-form length-normalized log-likelihood. Higher = more
                                       L-phonotactically-plausible.

Smoothing — add-k (Lidstone), chosen over Kneser-Ney-lite for ONE reason that matters here: the
corpus is tiny and the alphabet is a closed romanization, so the robustness requirement ("no -inf on
an OOV n-gram") dominates the marginal ranking gain of a continuation-probability backoff. Add-k is
unconditionally defined: P(c|ctx) = (count(ctx,c)+k) / (count(ctx)+k*V) is strictly positive for any
context (an unseen context degenerates to the uniform 1/V — finite, never -inf) and for any target
(out-of-vocabulary held-out characters are folded onto a reserved UNK symbol that has count 0
everywhere, so they cost a bounded -log(V), never -inf). The price — an unseen context backs off to
uniform rather than to a lower-order model — is acceptable because S_phono is the explicitly WEAK
statistic; its job is a sanity floor, not the verdict.

Length normalization — per-form scores divide the total log-probability by the number of EMITTED
symbols (len(form)+1, counting the terminal end-sentinel), so word length does not dominate the mean
across L's heterogeneous lexemes. This is approximate, NOT exact length-invariance: for
phonotactically-IMPLAUSIBLE material (heavily UNK), the per-symbol score still drifts upward with
length because the heavy begin/UNK boundary penalty is diluted over more uniform interior emissions
(~1 nat across len 1→8 for all-OOV input). The bias CANCELS in the actual use — comparing two lexicons
on the SAME held-out set — but a caller must not read absolute per-symbol values across held-out sets
of different length composition.

Cross-lexicon comparison caveat (the C.3/F.2 use: candidate vs L_fake) — add-k's denominator
``total + k·V`` depends on the symbol-inventory size ``V``, so for two lexicons with identical
(count,total) structure the larger-alphabet one scores strictly lower. S_phono is therefore only
comparable across lexicons matched in INVENTORY, not merely in lexicon size; the F.2 calibration (which
builds L_fake from the candidate's own phoneme inventory + frequencies) supplies that matching, but a
caller comparing arbitrary lexicons must ensure inventory parity or the smaller alphabet wins on V
alone. This is acceptable for the explicitly WEAK statistic (never verdict-bearing); a promotion toward
a decision role would need inventory-normalized smoothing (stupid-backoff / interpolation).

Degenerate / no-power path (honesty, never a misleading finite number): an empty candidate lexicon
yields a model with no training evidence, and an empty held-out set has nothing to score. Either case
returns float('nan') (with a companion :func:`is_degenerate` predicate and the ``is_degenerate`` flag
on :func:`s_phono_report`) — a NaN that propagates honestly, NOT a 0.0 that an unwary caller could
read as a real, finite likelihood.

Pure stdlib (the counting + math.log); deterministic by construction — n-gram fitting has no RNG, so
the same lexicon and order yield byte-identical counts and an identical float every run.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

CITATION_DESIGN = (
    "logos comparison-layer §A.2 (S_phono = log-likelihood of held-out word-forms under an "
    "L-phonotactic n-gram model built from L's known lexicon; the WEAK, surface-plausibility "
    "statistic, reported beneath the deflated S_lex pragmatic primary of refinement F.1)."
)

# Sentinels — multi-character tokens so they can never collide with a single romanized sign.
BEGIN = "<s>"      # left padding; appears only in contexts, is never emitted/scored
END = "</s>"       # terminal symbol; emitted once per form so word length is itself modelled
UNK = "<unk>"      # reserved target for out-of-vocabulary held-out characters (count 0 everywhere)

DEFAULT_K = 0.1    # add-k pseudocount; < 1 (Laplace add-1 over-smooths a closed romanized alphabet)


# --------------------------------------------------------------------------- #
# The model
# --------------------------------------------------------------------------- #
@dataclass
class NgramModel:
    """An order-``order`` add-k character/sign n-gram model fit on L's known lexicon.

    ``context_counts[ctx][target]`` is the raw co-occurrence count and ``context_totals[ctx]`` its
    row sum; ``vocab`` is the set of emittable symbols (L's characters plus END plus the reserved
    UNK); ``vocab_size`` (= ``V``) is the add-k denominator term. A model fit on an empty lexicon has
    no training evidence and is flagged via :func:`is_degenerate`.
    """
    order: int
    k: float
    context_counts: Dict[Tuple[str, ...], Dict[str, int]]
    context_totals: Dict[Tuple[str, ...], int]
    vocab: frozenset
    n_forms: int

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)


def is_degenerate(model: NgramModel) -> bool:
    """True iff the model carries no PHONOTACTIC training evidence → S_phono has no meaning.

    Degenerate when there are no training forms, no contexts, OR the vocabulary holds no real
    character (``vocab ⊆ {END, UNK}``). The last case catches a lexicon of only empty / whitespace
    strings (e.g. ``['', '', '']``): it has ``n_forms > 0`` and a non-empty ``context_totals`` (the
    BEGIN→END emission of each empty form), yet zero character evidence — so a naive list-emptiness
    guard would wrongly return a finite likelihood. Folding it in here keeps the 'honest NaN, never a
    misleading finite number' guarantee airtight.
    """
    return (model.n_forms == 0
            or not model.context_totals
            or model.vocab <= frozenset({END, UNK}))


def _tokens(form: str) -> List[str]:
    """A form is a sequence of single-character/sign tokens, in lexstat's transcription space."""
    return list(form)


def _emissions(tokens: Sequence[str], order: int):
    """Yield (context, target) pairs for one padded form.

    Left-pad with ``order-1`` BEGIN sentinels and append one END; for each emitted symbol the context
    is the preceding ``order-1`` tokens. BEGIN is never a target (not scored/emitted); END is, so the
    model learns where words stop (length is part of the phonotactics).
    """
    padded = [BEGIN] * (order - 1) + list(tokens) + [END]
    for i in range(order - 1, len(padded)):
        ctx = tuple(padded[i - (order - 1):i])
        yield ctx, padded[i]


# --------------------------------------------------------------------------- #
# fit
# --------------------------------------------------------------------------- #
def fit(lexicon: Sequence[str], order: int = 3, k: float = DEFAULT_K) -> NgramModel:
    """Train an order-``order`` add-k n-gram model over L's known lexemes.

    ``order`` 3 (default) or 2 are the supported / tested settings; any order >= 1 works. ``k`` is the
    Lidstone pseudocount. The returned model is fully determined by (lexicon, order, k) — no RNG.
    An empty lexicon returns a degenerate model (see :func:`is_degenerate`); it does not raise.
    """
    if order < 1:
        raise ValueError(f"order must be >= 1, got {order}")
    if k <= 0:
        raise ValueError(f"k must be > 0 for add-k smoothing (no -inf), got {k}")

    context_counts: Dict[Tuple[str, ...], Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    context_totals: Dict[Tuple[str, ...], int] = defaultdict(int)
    chars: set = set()
    n_forms = 0
    for form in lexicon:
        n_forms += 1
        toks = _tokens(form)
        chars.update(toks)
        for ctx, target in _emissions(toks, order):
            context_counts[ctx][target] += 1
            context_totals[ctx] += 1

    # Emittable symbols: L's characters + END (a real target) + the reserved UNK. BEGIN is excluded
    # (padding only). UNK guarantees a finite cost for held-out characters unseen in training.
    vocab = frozenset(chars | {END, UNK})
    # Freeze the defaultdicts into plain dicts so the model is hashably deterministic / side-effect-free.
    return NgramModel(
        order=order,
        k=k,
        context_counts={ctx: dict(d) for ctx, d in context_counts.items()},
        context_totals=dict(context_totals),
        vocab=vocab,
        n_forms=n_forms,
    )


# --------------------------------------------------------------------------- #
# scoring
# --------------------------------------------------------------------------- #
def _cond_logprob(model: NgramModel, ctx: Tuple[str, ...], target: str) -> float:
    """log P(target | ctx) under add-k. Strictly finite for ALL (ctx, target).

    Unseen context  -> total 0  -> P = k / (k*V) = 1/V         (uniform; finite, never -inf).
    OOV target      -> folded to UNK, count 0 -> P = k/(total+k*V) (bounded; never -inf).
    """
    V = model.vocab_size
    tgt = target if target in model.vocab else UNK
    num = model.context_counts.get(ctx, {}).get(tgt, 0) + model.k
    den = model.context_totals.get(ctx, 0) + model.k * V
    return math.log(num / den)


def _emitted_len(form: str) -> int:
    """Number of scored emissions for a form = len(form) + 1 (the terminal END). >= 1 always."""
    return len(form) + 1


def logprob_form(model: NgramModel, form: str) -> float:
    """Total natural-log probability of one form under the model (sum over its emissions).

    Finite for any input (add-k); an empty-string form scores its single END emission. Returns
    float('nan') if the model is degenerate (no training evidence) — never a misleading finite value.
    """
    if is_degenerate(model):
        return float("nan")
    total = 0.0
    for ctx, target in _emissions(_tokens(form), model.order):
        total += _cond_logprob(model, ctx, target)
    return total


def s_phono_per_form(heldout_forms: Sequence[str], candidate_lexicon: Sequence[str],
                     order: int = 3, k: float = DEFAULT_K) -> List[float]:
    """Per-form length-normalized (per-emitted-symbol) log-likelihoods — the bootstrap/CI hook.

    Mirrors :func:`lexstat.s_lex_per_form`: returns one score per held-out form, each the total
    log-probability divided by the number of emitted symbols (len(form)+1), so short and long forms
    are comparable. A degenerate model (empty candidate lexicon) yields a list of NaNs of the right
    length; an empty held-out set yields an empty list.
    """
    model = fit(candidate_lexicon, order=order, k=k)
    if is_degenerate(model):
        return [float("nan")] * len(heldout_forms)
    return [logprob_form(model, w) / _emitted_len(w) for w in heldout_forms]


def s_phono(heldout_forms: Sequence[str], candidate_lexicon: Sequence[str],
            order: int = 3, k: float = DEFAULT_K) -> float:
    """Mean per-form length-normalized held-out log-likelihood under L's phonotactic model.

    Higher (less negative) = the held-out forms are more L-phonotactically-plausible. Degenerate
    inputs (empty held-out set OR empty candidate lexicon) return float('nan') — the honest no-power
    sentinel (§A.2 is the WEAK statistic; a 0.0 here would masquerade as a real, finite likelihood).
    """
    if not heldout_forms or not candidate_lexicon:
        return float("nan")
    per = s_phono_per_form(heldout_forms, candidate_lexicon, order=order, k=k)
    # per is all-NaN only if the model is degenerate, which the candidate_lexicon guard above rules
    # out; defend anyway so a stray NaN never silently averages into a finite-looking number.
    if any(math.isnan(x) for x in per):
        return float("nan")
    return math.fsum(per) / len(per)


def s_phono_report(heldout_forms: Sequence[str], candidate_lexicon: Sequence[str],
                   order: int = 3, k: float = DEFAULT_K) -> Dict[str, object]:
    """S_phono plus its honesty companions: the ``is_degenerate`` flag and the input sizes.

    The degenerate flag lets a caller distinguish a real, finite mean from the NaN no-power sentinel
    without re-deriving the guard, satisfying the §A.2 / invariant-honesty 'never a misleading 0' rule.
    The flag is derived from the ACTUAL fitted model (not just list-emptiness) so a lexicon carrying no
    character evidence (e.g. ``['', '', '']``) is reported degenerate, consistent with its NaN s_phono.
    """
    degen = (not heldout_forms) or (not candidate_lexicon)
    if not degen:
        degen = is_degenerate(fit(candidate_lexicon, order=order, k=k))
    return {
        "s_phono": s_phono(heldout_forms, candidate_lexicon, order=order, k=k),
        "is_degenerate": degen,
        "order": order,
        "k": k,
        "n_heldout": len(heldout_forms),
        "n_lexicon": len(candidate_lexicon),
        "note": ("degenerate: empty held-out set or empty candidate lexicon -> NaN (no power), "
                 "NOT a finite likelihood") if degen else "finite per-symbol mean log-likelihood",
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse, json
    p = argparse.ArgumentParser(description="S_phono — held-out phonotactic plausibility (§A.2)")
    p.add_argument("--heldout", nargs="+", required=True)
    p.add_argument("--lexicon", nargs="+", required=True)
    p.add_argument("--order", type=int, default=3)
    p.add_argument("--k", type=float, default=DEFAULT_K)
    args = p.parse_args(argv)
    print(json.dumps(s_phono_report(args.heldout, args.lexicon, order=args.order, k=args.k),
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
