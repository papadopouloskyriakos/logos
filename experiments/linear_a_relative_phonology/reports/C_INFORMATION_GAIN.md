# C5 — Information Gain of the Linear A Substitution Graph

**Task C5 (information-gain half).** Estimate how many **sign-value equivalence classes** the C4
anonymous relations would reduce **IF they are true**, with uncertainty, and deflated for what the
evidence actually supports.

- Engine / data: `scripts/c5_stability_infogain.py` → `data/C5_stability.json`. Seed 20260708.
- **Non-circular** (Art. XII): equivalence-class counting uses only the anonymous graph; GORILA/LB
  (C,V) values enter *afterward* to grade the deflation and earn **no licence** (the homomorphy is the
  channel this campaign disputes).

## The model

The 57 clean Linear A syllabograms begin as **57 singleton value-equivalence classes** (each sign an
independent unknown). If an anonymous `REL_CLASS` of *k* signs is **one true shared-feature series**
(a single consonant-series or single vowel-series), it merges *k* signs into 1 class and removes
(*k*−1) unknowns. Total:

> **ΔEqClasses = n_signs_covered − n_classes.**

## Point estimates (two graph thresholds)

| threshold | signs covered | classes | ΔEqClasses (if true) | remaining classes (57 −Δ) |
|---|--:|--:|--:|--:|
| **strong (≥2 long frames)** | 17 | 5 | **12** | 45 |
| loose (≥1 long frame) | 49 | 1 | 48 | 9 |

**The loose figure (48) is not usable.** At ≥1 long frame the graph collapses 49 of 57 signs into a
**single** connected blob — the trivial consequence of near-universal one-sign minimal-pairing on a
small alphabet, not phonological structure. Only the **strong** graph is interpretable, and its
headline ΔEqClasses = 12 (57 → 45).

## Uncertainty (bootstrap, ×500 documents)

The point estimate 12 is a small-sample artifact. Resampling documents gives:

- ΔEqClasses **mean 3.3**, **95% CI [1, 7]**.
- Mean strong-edge recurrence 0.28; only 1/12 edges recur in ≥50% of resamples (see companion nulls
  report). Most of the "12" does not reproduce.

## Deflation (what the evidence supports) — FLAGGED benchmark

On the disputed GORILA homomorphy, the strong edges grade **1 same_consonant + 3 same_vowel + 8 cross**
→ feature-sharing precision **0.33**; all 130 clean edges grade **11 + 35 + 84 cross** → precision
**0.35**. Both are **at/near the chance rate**, and C4 showed the graph's word-final enrichment does
**not** beat its own within-graph null. Deflating ΔEqClasses by feature precision:

| basis | ΔEqClasses | ×precision | deflated expected Δ |
|---|--:|--:|--:|
| strong (point) | 12 | 0.33 | **4.0** |
| strong (bootstrap mean) | 3.3 | 0.33 | **~1.1** |
| loose | 48 | 0.35 | 17.0 *(uninterpretable, see above)* |

## Bottom line

| figure | value | status |
|---|--:|---|
| ΔEqClasses, strong graph, **if every relation is a true series** | **12** (57 → 45) | optimistic upper bound |
| ΔEqClasses, **bootstrap 95% CI** | **[1, 7]** | honest range |
| ΔEqClasses, **deflated by benchmark precision** | **~4** (point) / **~1** (bootstrap) | honest expectation |
| toy bits, optimistic (Δ·log₂92 − within-series vowel residual) | ~50 bits | flagged; assumes full typing |

**The honest information gain of the substitution channel at this corpus scale is ≈1–4 sign-value
equivalence classes reduced — and even that is not enrichment-verified** (the axis it would exploit,
consonant-held vocalic alternation, was not recovered above chance in C4). The "if-true" 12 is a
ceiling contingent on relations that the C5 stability audit shows are non-generalizing (bootstrap-
fragile, segmentation-fragile, Haghia-Triada-dominated) and that grade at chance on the only known-value
check available. All edges descend from the single **L_GORILA_VENTRIS** transliteration lineage, so the
gain is **not independently corroborated** (Art. XI single dependency cluster).

**Status: INFORMATION_GAIN_MARGINAL_AND_UNVERIFIED** — the substitution channel does not, on the
current corpus, buy enough equivalence-class reduction to license a "not value-blind" claim; the binding
constraint remains an independent long-context or bilingual anchor, not more short administrative words.
