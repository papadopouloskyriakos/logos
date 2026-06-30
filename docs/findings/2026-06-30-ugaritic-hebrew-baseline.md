# Finding 2026-06-30 — Ugaritic→Hebrew known-answer recovery (the credibility milestone)

The known-answer recovery the expert audits demanded. Run via
`python3 scripts/decipher/run_ugaritic.py` on the gold 2,214 cognate pairs
(`corpus/bronze/ugaritic/uga-heb.gold.cog` — the Luo 2019 / Snyder 2010 / B-K&K benchmark).

**Why Ugaritic→Hebrew (not Linear-B→Greek):** the engine is a 1-1 char map. Ugaritic and Old
Hebrew are both consonantal **abjads**, so a 1-1 consonant map is well-posed. Linear B is a
**syllabary** (sign = CV), where a 1-1 sign→letter map is the wrong granularity — that needs a
syllable-aware / variable-length alignment (the neural upgrade), deferred.

## Result

```
cipher words (Ugaritic, unique) : 2,182
plain candidates (Hebrew vocab) : 2,767
converged in 2 iteration(s)
cognate_accuracy   : 0.0055   (12 / 2,182)
chance (null floor): 0.0004
mean_edit_distance : 1.4707
```

The learned Ugaritic→Hebrew consonant map is visibly **scrambled** (e.g. `a→H`, `b→m`, `d→k`,
`n→t`) rather than the near-identity expected for closely-related Semitic consonants.

## Interpretation (honest)

- **The engine is correct, not buggy.** The synthetic self-test recovers a known 13-sign map at
  **100%** (13/13 signs, 72/72 words); the Linear-A null lands at chance. So the E-step +
  `linear_sum_assignment` + EM loop are right.
- **But the simplified heuristic is too weak for the real benchmark.** 0.55% cognate accuracy is
  ~14× the chance floor (real signal, not noise) yet far below Luo 2019's neural **~67%**. The
  gap is exactly the documented limitations biting on real noisy data:
  - **hard-argmax E-step** (not soft/expected counts) → fragile;
  - **1-1 assignment only** (no many-to-one / polyphony);
  - **no random restarts** → fast convergence (2 iters) into a poor local optimum;
  - **non-neural** (no differentiable alignment / true min-cost flow).
- **This quantifies the upgrade headroom.** To get *credible* decipherment numbers on
  Ugaritic→Hebrew we need (a) faithful **Berg-Kirkpatrick & Klein 2011** (word-level bipartite
  matching + many-to-many alphabet + **random restarts**) and/or (b) the **Luo/NeuroCipher
  neural upgrade**. Both are documented paths; this is the non-neural floor they start from.

## Takeaway

This is the **honest baseline number** — above chance (the machinery finds signal), well below
the published neural result (the simplification costs real performance). It does NOT constitute
a decipherment claim; it calibrates the harness and measures the distance to SOTA. Recorded per
logos invariant (guilty until proven innocent) and the audit's demand for a known-answer
milestone. Next: faithful-B-K&K-with-restarts to close the gap, and the pseudo-decipherment
learning curves (#16) as the real information-sufficiency test.
