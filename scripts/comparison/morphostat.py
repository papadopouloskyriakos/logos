#!/usr/bin/env python3
"""morphostat.py — S_morph: deflated recurring-morphology score (logos comparison-layer §A.2, F.1).

S_morph is the *Kober statistic* of the comparison layer — the STRONG test (design §A.2):

    "do the held-out forms exhibit the SAME L affix / template inventory at above-null frequency,
     consistently, across INDEPENDENT inscriptions?"

Truth produces SYSTEM: a real affix (Semitic plural ``-m`` / ``-ym``, a prefixing ``m-``) recurs in
*many independent texts* AND attaches to *many distinct stems*. Coincidence — or a copied formula word
— produces SCATTER/REPETITION: a chance match clusters inside one inscription, and a repeated whole
word bears its "affix" on a single stem. So the statistic credits an affix only when it (a) spans
DISTINCT inscriptions (breadth, not raw occurrence count) AND (b) attaches to ≥ ``min_stems`` DISTINCT
STEMS (productivity — the residual after stripping the affix must vary). Requirement (b) is what stops
a single libation-formula word copied across five tablets from scoring like genuine affixation; the
within-form null alone does NOT neutralise that repetition, so the productivity gate carries it. That
productivity-gated breadth, deflated against the positional-structure-destroying null, is the score.
Independence across inscriptions is the crux, which is why the held-out forms arrive grouped per
inscription (a LIST OF LISTS); a flat list cannot test consistency and is pushed to ``no_power`` honestly.

THE NO-POWER ESCAPE (refinement F.1 — the whole point of THIS module). Linear A is short,
administrative, heavily formulaic; there may be too little morphology to recur, so S_morph can be
near-powerless *regardless of truth* — a "no power" verdict that reflects the corpus, not the
hypothesis. Mirroring the §C.3 ``S ≈ L_fake → report no power`` rule, when the observed recurrence is
indistinguishable from the null (or the corpus is too thin to test), this returns a structured result
with ``is_powered = False`` and an explicit ``reason``. A no-power result is VISIBLY DISTINCT from a
real low score — the two are never collapsed (a misleading 0 that looks like a real null is the bug
this module exists to avoid).

The null recurrence baseline reuses the Nair within-inscription permutation from ``nulls.py``
(``within_form_permutation``): it preserves each held-out form's exact character multiset and length
while destroying the positional affix/template structure, so it isolates "do L's affixes recur in
held-out POSITIONS beyond what the held-out character content alone would give." (The Packard banded
permutation in ``nulls.py`` is an alternative relabelling null; within-form is the tightest same-forms
control for a positional statistic and is what the consistency tests exercise.)

Pure numpy/stdlib, deterministic (seeded). The LLM never grades; this is arithmetic (invariant 4).
"""
from __future__ import annotations

import os
import sys
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

# make `scripts.comparison` importable when run as a plain script (cron-style)
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.comparison.nulls import within_form_permutation  # noqa: E402

CITATION_DESIGN = (
    "logos comparison-layer §A.2 (S_morph = recurring-morphology score, the STRONG/Kober statistic: "
    "same L affix/template inventory at above-null frequency, consistently, across INDEPENDENT "
    "inscriptions) and refinement F.1 (the no-power escape: a short formulaic corpus can leave "
    "S_morph near-powerless regardless of truth — report no power, never a misleading low score)."
)
CITATION_NAIR = (
    "Nair 2026, arXiv:2604.17828 (via nulls.within_form_permutation) — within-inscription fixed-seed "
    "permutation supplies the null recurrence baseline: each held-out form keeps its character "
    "multiset and length while its positional affix structure is destroyed."
)

# An affix is one of these two kinds; the value is the prefix/suffix string (1-2 transcription units).
Affix = Tuple[str, str]                       # (kind, string), kind in {"prefix", "suffix"}
# Held-out may arrive grouped per inscription (list of lists) or as a flat fallback (list of strings).
HeldOut = Union[Sequence[Sequence[str]], Sequence[str]]


# --------------------------------------------------------------------------- #
# L affix / template inventory — the "expected morphology" of the candidate
# --------------------------------------------------------------------------- #
def derive_affix_inventory(candidate_lexicon: Sequence[str],
                           max_affix_len: int = 2,
                           min_affix_count: Optional[int] = None,
                           min_affix_frac: float = 0.05) -> List[Affix]:
    """Derive L's recurring prefix/suffix inventory from the candidate lexicon (the "expected" L
    morphology).

    For affix length 1..``max_affix_len`` we count how many DISTINCT lexemes carry each prefix and
    each suffix, and keep those occurring in at least ``floor`` lexemes, where

        floor = min_affix_count   if given,   else   max(2, ceil(min_affix_frac * |lexicon|)).

    The ``max(2, …)`` ensures an affix must recur in at least two lexemes to count as morphology
    (a hapax is not an affix). An affix shorter than the form is required (a 2-unit suffix on a
    2-unit form would be the whole word, not an affix), so affixes are only counted on lexemes
    strictly longer than the affix.

    The inventory is deterministic and sorted (kind, string) for reproducibility.
    """
    lex = [w for w in candidate_lexicon if w]
    n = len(lex)
    if n == 0:
        return []
    floor = min_affix_count if min_affix_count is not None else max(2, int(np.ceil(min_affix_frac * n)))
    pre_counts: Counter = Counter()
    suf_counts: Counter = Counter()
    for w in lex:
        for k in range(1, max_affix_len + 1):
            if len(w) > k:                          # affix must be a PROPER prefix/suffix
                pre_counts[w[:k]] += 1
                suf_counts[w[-k:]] += 1
    inv: List[Affix] = []
    for s, c in pre_counts.items():
        if c >= floor:
            inv.append(("prefix", s))
    for s, c in suf_counts.items():
        if c >= floor:
            inv.append(("suffix", s))
    inv.sort()
    return inv


def _affix_in_form(form: str, affix: Affix) -> bool:
    """True iff ``form`` bears ``affix`` (a proper prefix/suffix — not the whole word)."""
    kind, s = affix
    if len(form) <= len(s):
        return False
    return form.startswith(s) if kind == "prefix" else form.endswith(s)


def _affix_stem(form: str, affix: Affix) -> Optional[str]:
    """The residual STEM after stripping ``affix`` from ``form``; None iff ``form`` does not bear it
    (as a PROPER prefix/suffix, not the whole word). ``("prefix","ma")`` on ``"matabu"`` -> ``"tabu"``.
    """
    kind, s = affix
    if len(form) <= len(s):
        return None
    if kind == "prefix":
        return form[len(s):] if form.startswith(s) else None
    return form[:-len(s)] if form.endswith(s) else None


# --------------------------------------------------------------------------- #
# Cross-inscription recurrence — breadth across INDEPENDENT inscriptions
# --------------------------------------------------------------------------- #
def cross_inscription_recurrence(inscriptions: Sequence[Sequence[str]],
                                 inventory: Sequence[Affix],
                                 min_stems: int = 2) -> float:
    """Mean over the L affix inventory of (# inscriptions bearing the affix PRODUCTIVELY / # inscriptions).

    Two requirements separate SYSTEM (recurring morphology) from SCATTER/REPETITION — the Kober logic
    (design §A.2):

      (1) *breadth*: count DISTINCT inscriptions, not raw occurrences — an affix clustered inside one
          inscription (chance) scores breadth 1, a systematic affix recurring across many independent
          inscriptions scores high; and
      (2) *productivity*: the affix must attach to at least ``min_stems`` DISTINCT STEMS (the residual
          after stripping it). A single formula word copied across many inscriptions bears its "affix"
          with only ONE stem — that is lexical REPETITION, not productive morphology — so it
          contributes 0.

    Requirement (2) is essential on a short, formulaic corpus (F.1): without it the statistic AND the
    within-form null (which cannot neutralise a repeated whole word — shuffling each copy independently
    still leaves the affix edge intact often enough) would fire IDENTICALLY on a copied formula word as
    on genuine affixation — the dominant false positive. In [0, 1]; 0.0 if no inscriptions / empty inventory.
    """
    m = len(inscriptions)
    if m == 0 or not inventory:
        return 0.0
    total = 0.0
    for affix in inventory:
        n_insc = 0
        stems: set = set()
        for insc in inscriptions:
            bears = False
            for f in insc:
                stem = _affix_stem(f, affix)
                if stem is not None:
                    stems.add(stem)
                    bears = True
            if bears:
                n_insc += 1
        if len(stems) < min_stems:           # repetition, not productive morphology -> no credit
            continue
        total += n_insc / m
    return total / len(inventory)


def _null_recurrence(inscriptions: Sequence[Sequence[str]],
                     inventory: Sequence[Affix],
                     n_null: int,
                     seed: int,
                     min_stems: int = 2) -> List[float]:
    """Null distribution of the recurrence statistic under the Nair within-form permutation.

    Each draw independently shuffles the characters WITHIN every held-out form (per inscription,
    deterministic per-inscription seed), preserving every form's character multiset and length while
    destroying the positional affix/template structure, then recomputes the recurrence against the
    SAME fixed L inventory with the SAME productivity gate. The spread of these draws is the σ0 the
    observed score must beat. The composite per-inscription seed is reduced mod 2**32 so a negative or
    large ``seed`` never reaches ``default_rng`` (which rejects negatives) while staying deterministic.
    """
    draws: List[float] = []
    for d in range(n_null):
        shuffled = [
            within_form_permutation(list(insc), seed=((seed + d) * 100003 + k) % (2 ** 32))
            for k, insc in enumerate(inscriptions)
        ]
        draws.append(cross_inscription_recurrence(shuffled, inventory, min_stems=min_stems))
    return draws


# --------------------------------------------------------------------------- #
# Normalization: list-of-lists (per inscription) vs flat fallback
# --------------------------------------------------------------------------- #
def _normalize_groups(heldout: HeldOut) -> Tuple[List[List[str]], bool]:
    """Return (groups, was_flat). A flat list of strings is wrapped as a SINGLE group (documented
    fallback): with one group, cross-inscription consistency cannot be tested, which forces no_power.
    Empty forms and empty groups are dropped."""
    seq = list(heldout)
    if not seq:
        return [], False
    if isinstance(seq[0], str):                      # flat list of forms -> one group, flagged
        forms = [f for f in seq if isinstance(f, str) and f]
        return ([forms] if forms else []), True
    groups = [[f for f in g if f] for g in seq]      # type: ignore[union-attr]
    groups = [g for g in groups if g]
    return groups, False


# --------------------------------------------------------------------------- #
# S_morph — the structured, no-power-aware result
# --------------------------------------------------------------------------- #
def s_morph(heldout_by_inscription: HeldOut,
            candidate_lexicon: Sequence[str],
            *,
            max_affix_len: int = 2,
            min_affix_count: Optional[int] = None,
            min_affix_frac: float = 0.05,
            min_inscriptions: int = 3,
            min_affixes: int = 2,
            min_stems: int = 2,
            n_null: int = 64,
            seed: int = 0,
            z_threshold: float = 2.0) -> Dict[str, object]:
    """S_morph — deflated recurring-morphology score with the F.1 no-power escape.

    Parameters
    ----------
    heldout_by_inscription : list of lists of forms (per INDEPENDENT inscription); a flat list of
        forms is accepted as a documented fallback (treated as one group -> consistency cannot be
        tested -> pushed to no_power).
    candidate_lexicon : L's known lexemes (same transcription space as the held-out forms), from
        which the affix/template inventory is derived.
    min_inscriptions : independence across at least this many inscriptions is required to test
        consistency (default 3 — two texts barely test recurrence).
    min_affixes : the L inventory must hold at least this many affixes above the frequency floor.
    min_stems : an affix must attach to at least this many DISTINCT stems to count as productive
        morphology rather than lexical repetition (default 2 — see ``cross_inscription_recurrence``).
    z_threshold : observed recurrence must beat the null by this many σ0 to be SIGNIFICANT.

    Returns a structured dict (NEVER a bare float — a no-power result must be visibly distinct from a
    real low score)::

        {score, null_mean, null_std, deflated, z, n_inscriptions, n_affixes, n_heldout_forms,
         has_power, is_significant, is_powered, reason}

    Two booleans, deliberately SEPARATE (the conflation of these was a real defect — a statistic that
    "has power" only when it also passes can never fail a gate clause):

      ``has_power``     — the CORPUS can support the test at all: enough independent inscriptions,
                          enough affixes above the floor, and a non-degenerate within-form null. This
                          is the F.1 no-power escape — it reflects the corpus, NOT the hypothesis.
      ``is_significant``— GIVEN power, the candidate's affixes productively recur above the null
                          (z ≥ ``z_threshold``). ``has_power and not is_significant`` is a REAL
                          negative (the strong test was available and the candidate FAILED it).

    ``is_powered = has_power and is_significant`` is retained as the headline "passed everything" flag.
    ``score`` is the productivity-gated cross-inscription recurrence in [0,1];
    ``deflated = max(0, score-null_mean)``. When not significant, ``reason`` says exactly why and the
    numbers are still reported for transparency (honesty: no misleading silent 0).
    """
    groups, was_flat = _normalize_groups(heldout_by_inscription)
    m = len(groups)
    n_forms = sum(len(g) for g in groups)
    inventory = derive_affix_inventory(candidate_lexicon, max_affix_len, min_affix_count, min_affix_frac)
    n_affixes = len(inventory)

    score = cross_inscription_recurrence(groups, inventory, min_stems=min_stems)

    # Null is only meaningful when there is something to score; otherwise it is a degenerate 0.
    if m >= 1 and n_affixes >= 1 and n_forms >= 1:
        null_scores = _null_recurrence(groups, inventory, n_null=n_null, seed=seed, min_stems=min_stems)
        null_mean = float(np.mean(null_scores))
        null_std = float(np.std(null_scores, ddof=1)) if len(null_scores) > 1 else 0.0
    else:
        null_mean = 0.0
        null_std = 0.0

    z = (score - null_mean) / null_std if null_std > 1e-12 else 0.0
    deflated = max(0.0, score - null_mean)

    result: Dict[str, object] = {
        "score": float(score),
        "null_mean": null_mean,
        "null_std": null_std,
        "deflated": float(deflated),
        "z": float(z),
        "n_inscriptions": m,
        "n_affixes": n_affixes,
        "n_heldout_forms": n_forms,
        "has_power": False,
        "is_significant": False,
        "is_powered": False,
        "reason": "",
    }

    # --- no-power gates (the CORPUS cannot support the test): has_power stays False --------------- #
    if n_forms == 0:
        result["reason"] = "no held-out forms: nothing to score (degenerate)."
        return result
    if n_affixes < min_affixes:
        result["reason"] = (f"too few L affixes above floor (n_affixes={n_affixes} < {min_affixes}): "
                            f"no recurring-morphology inventory to test.")
        return result
    if was_flat:
        result["reason"] = ("flat held-out list (single group): independence across inscriptions "
                            "cannot be tested — re-supply forms grouped per inscription.")
        return result
    if m < min_inscriptions:
        result["reason"] = (f"too few independent inscriptions (m={m} < {min_inscriptions}): "
                            f"cross-inscription consistency cannot be established (corpus too sparse).")
        return result
    if null_std <= 1e-12:
        result["reason"] = ("null recurrence has zero variance: the within-form baseline is "
                            "degenerate (forms too short to permute), so no power.")
        return result

    # The corpus CAN support the test -> has_power=True regardless of the candidate's outcome.
    result["has_power"] = True

    if z < z_threshold:
        # tested and NEGATIVE: the candidate's affixes do not productively recur above chance here.
        # This is a REAL low score (has_power is True), NOT the no-power escape — distinct on purpose.
        result["reason"] = (f"observed recurrence indistinguishable from null (z={z:.2f} < "
                            f"{z_threshold:.2f}): the candidate's affixes do not productively recur "
                            f"above chance — a real negative (has_power=True, is_significant=False).")
        return result

    result["is_significant"] = True
    result["is_powered"] = True
    result["reason"] = (f"powered: L affix inventory recurs productively across {m} independent "
                        f"inscriptions at z={z:.2f} ≥ {z_threshold:.2f} above the within-form null.")
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse, json
    p = argparse.ArgumentParser(
        description="S_morph — deflated recurring-morphology score (no-power-aware). "
                    "Group held-out forms per inscription with '++' separators; a single group "
                    "(no separator) is the flat fallback and reports no power by construction.")
    p.add_argument("--heldout", nargs="+", required=True,
                   help="held-out forms; separate independent inscriptions with a literal '++'")
    p.add_argument("--lexicon", nargs="+", required=True, help="candidate L lexemes")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-null", type=int, default=64)
    args = p.parse_args(argv)
    # split --heldout into inscription groups on the '++' sentinel
    groups: List[List[str]] = [[]]
    for tok in args.heldout:
        if tok == "++":
            groups.append([])
        else:
            groups[-1].append(tok)
    groups = [g for g in groups if g]
    heldout: HeldOut = groups if len(groups) > 1 else (groups[0] if groups else [])
    res = s_morph(heldout, args.lexicon, seed=args.seed, n_null=args.n_null)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
