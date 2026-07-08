# EPOCH-003 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F3** (substitution-neighborhood bridges v2)
**Epoch question:** SEED-POVERTY + CORPUS-POWER SURFACE for the trigram-frame motif bridge.
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Substantive gate:** A/E.
**Articles triggered:** V (claim layers), VII (search receipt), VIII (effective_n + multiplicity),
IX (info budget), XI/XII (non-circularity), XV (transfer licences: nothing here earns a value),
XXII (stage header).
**Claim layer of ANY result here: L2 (relative/structural), calibrated on KNOWN scripts
(LB, Cypriot). No Linear A value claim can emerge from this epoch.**

## Question

EPOCH-002 produced the first Holm-surviving KNOWN LB↔Cypriot cross-script recovery
(MF_A trigram-frame, M1 NN-transfer LOO: 7/47 exact = 0.149, p = 0.001) — but M1-LOO uses
**46 anchors**. Linear A has **~5 firm toponym equations**. Decisive question: does the bridge
survive LA's seed budget and LA's corpus power? Measured entirely on the KNOWN pair
(+ the CTRL identity pair), where ground truth exists.

## Non-circular contract (Art. XI/XII)

Identical to EPOCH-002: all similarities built from sign IDENTITY + word co-occurrence only
(MF_A trigram frames); known values are read AFTERWARD to define GT pairs and GRADE.
Alignment operates on opaque per-script sign lists with target order shuffled (seeded).
The LA operating point is LOCATED on the measured surface; no LA alignment is run in this
epoch (that would be a consistency test, already done as E002-LA; here we calibrate power).

## Data / units (frozen; measured pre-freeze, descriptive only)

- KNOWN pair = LB-cog (919 word types) ↔ Cypriot-cog (693), `f_bridge_common.load_lb_cog /
  load_cyp_cog`. Full-corpus alignable (MIN_SUP=3 both sides, parse_cv shared value): n=47.
  Min-side (Cypriot) median word-type support of alignable signs at full corpus: 56.
- CTRL pair = LB-DĀMOS split-half (seeded, 6,781 word tokens per half), identity GT,
  full-corpus alignable n=71.
- LA reference (descriptive, for locating the operating point ONLY): LA silver 3,147 word
  tokens / 1,165 types; E002 LA-leg alignable n=51; LA-side median support 47;
  LB-DĀMOS-side median support 245 → LA min-side median support = **47**.
- Machinery reused read-only: `scripts/e002_motif_common.py` (MF_A `inc_trigram` +
  `jaccard_lookup`), `f2_cross_script_bridge.py` (M1 `method_M1_nn`, GT builders,
  `half_split`), seed 20260708.

## Design (frozen)

**Axes.** Pairs P = {KNOWN, CTRL}; corpus fractions F = {0.05, 0.1, 0.25, 0.5, 0.75, 1.0}
(subsample the word-token list of BOTH sides without replacement, seeded); seed budgets
B = {3, 4, 5, 7, 10, 15, 20, 30, LOO} where LOO = all-but-one aggregate (E002 convention;
at full KNOWN corpus LOO ≡ 46 anchors). Surface = 2 × 6 × 9 = 108 cells, + 5 adversarial
cells (below) = **113 cells** (≥100 required).

**Replicates.** R = 20 per non-LOO cell: frac = 1.0 → 20 independent seed-subset draws on
the fixed corpus; frac < 1.0 → 5 corpus draws × 4 seed-subset draws. LOO cells: 1 replicate
per corpus draw (deterministic given corpus): frac = 1.0 → 1, frac < 1.0 → 5.
All RNG streams derived deterministically from (20260708, pair, frac, draw, rep).

**Per replicate.** Rebuild GT-alignable problem on the (sub)corpus (MIN_SUP=3 both sides);
MF_A trigram similarity matrices (target order shuffled per corpus draw); seeds drawn
uniformly from alignable pairs; M1 NN-transfer cost from seed columns; prediction for each
HELD-OUT sign = argmin over ALL target columns (E002 convention, unrestricted); endpoint =
exact-recovery count on held-out signs. **Null** = 1,000 seeded permutations of the true
partners among held-out signs, one-sided p on exact count. (LOO: held-out = all signs,
identical to E002's `perm_null_classes` exact leg.)
A replicate with < 10 gradeable held-out signs is INVALID; a cell with > R/2 invalid
replicates is **NO_POWER** (excluded from verdict scans, reported).

**Cell statistics.** mean + median exact accuracy, 95% percentile CI over replicates,
median p, survival_rate = frac(p ≤ 0.05/12). Cell verdict (mechanical):
- **SURVIVES_HOLM** if median p ≤ 0.05/12 = 0.0041667 (the per-test bar M1:exact had to
  clear inside E002's Holm-12 family — the bridge claim inherits that family, Art. VIII);
- **NOMINAL** if median p ≤ 0.05;
- else **FLOOR**.

**Minimum seed budget** (primary readout) = smallest b ∈ B on the KNOWN pair at frac = 1.0
such that b **and every larger budget** SURVIVES_HOLM (monotone closure — no isolated-cell
cherry-picking).

## Adversarial: wrong-seed injection (frozen; KNOWN pair, frac = 1.0)

Cells: (b=5, k_wrong=1), (b=5, k_wrong=2), (b=7, k_wrong=1), (b=7, k_wrong=2), and
(b=5, k_wrong=5) = full-scramble **negative control** (must be FLOOR; if it is not, the
grading harness is broken → epoch aborts with DETECTOR_BROKEN). R = 20 each. A wrong seed:
the seed's target partner is replaced by a uniformly random target sign ≠ its true partner.
Held-out grading unchanged (held-out = non-seed signs).
**POISONING verdict:** POISONS if the clean (b, 0-wrong) cell is ≥ NOMINAL and the 1-wrong
cell at the same b drops at least one tier (SURVIVES_HOLM→NOMINAL counts); quantified by
Δ mean exact accuracy.

## LA operating point (frozen mapping rule)

- Seed axis: **n_seeds = 5** (the ~5 firm toponym equations; sensitivity row b=4 and b=7
  reported, verdict uses b=5).
- Corpus axis: **f_LA** = the f ∈ F minimizing |realized min-side median alignable support
  at f (KNOWN pair, averaged over its 5 corpus draws; frac 1.0 uses the full-corpus value 56)
  − 47| (LA's min-side median support). Pre-freeze arithmetic expects f_LA ∈ {0.75, 1.0};
  the realized medians decide mechanically.
- Secondary descriptive mapping (reported, not verdict-bearing): token-ratio
  LA types / LB-cog types = 1165/919 > 1 → would clamp to f = 1.0.

## Mechanical epoch verdict (frozen)

Let CELL_LA = KNOWN cell (b=5, f_LA); let WRONG1 = KNOWN (b=5, k_wrong=1, frac 1.0).
1. CELL_LA = SURVIVES_HOLM **and** WRONG1 ≥ NOMINAL → **BRIDGE_VIABLE_AT_LA_SEED_BUDGET**
2. elif CELL_LA ≥ NOMINAL (i.e. NOMINAL, or SURVIVES_HOLM with WRONG1 = FLOOR) →
   **BRIDGE_MARGINAL_AT_LA_SEED_BUDGET**
3. else (CELL_LA = FLOOR or NO_POWER) → **BRIDGE_NOT_VIABLE_AT_LA_SEED_BUDGET**
Plus the measured **min_seed_budget** (or NONE_BELOW_LOO) reported alongside in all cases.

## Positive control (run FIRST, gate on it)

Reproduce EPOCH-002's frozen numbers with this epoch's code path (full corpus, LOO):
- KNOWN M1-LOO exact_count = **7**/47;
- CTRL M1-LOO exact_count = **55**/71 (0.775).
Any mismatch → **DETECTOR_BROKEN**, epoch aborts, no verdict.

## Search receipt (Art. VII)

Everything tried is listed above: 113 cells × ≤20 replicates, one method (M1/MF_A — the only
Holm survivor; sweeping M2–M4 too would be multiplicity farming on known nulls), one endpoint
(exact count; class metrics not swept), fixed grids, N_PERM=1000, MIN_SUP=3, seed 20260708.
No other budgets, fractions, kernels, thresholds, or restriction schemes will be tried;
any deviation = new preregistration.

## Falsifiable prediction (committed)

The bridge is anchor-hungry: M1's profile dimensionality equals n_seeds, so at 5 seeds the
profile space is too coarse for 40+ candidates. Committed prediction: min_seed_budget > 5
(confidence 0.70) and epoch verdict = BRIDGE_NOT_VIABLE or BRIDGE_MARGINAL at the LA point
(confidence 0.75). P(BRIDGE_VIABLE_AT_LA_SEED_BUDGET) = 0.15. Corpus axis is predicted to be
the WEAKER constraint at LA's operating point (f_LA ≥ 0.75) — the poverty is in seeds, not
corpus.
