# WP-G — Counterfactual Identifiability: the Anchor-Threshold Surface

**Branch** `research/linear-a-anchor-lattice` · **v2.2** · **Seed** 20260708 · **Date** 2026-07-08
**Articles:** VII (search receipt), VIII (power/effective_n), IX (info budget), XI (dependency), XII
(non-circularity: known values grade benchmarks only), XV (relative ≠ absolute), XXII (stage header).
**Truth-layer:** design/power analysis on KNOWN + synthetic scripts (≤ 0.75). NOT a Linear A reading.
**Script:** `scripts/g_anchor_threshold_lab.py` → `data/controls/anchor_threshold/{surface.json, surface_opaque_LB.csv}`
(re-run verified byte-identical, md5 `e19d4fee…`; 80 reps/cell, 200 at the LA points).

## Question

How many **independent** anchors, of what **quality** (slots, lineages, correctness, site spread), does the
full lattice need before a KNOWN syllabic script's absolute values come back — and where does Linear A sit
on that surface?

## Engine (mechanical, non-circular)

A syllabary is a C×V grid (opaque LB: 66 syllabic signs, 18C × 5V, built from DĀMOS; 13,436 real wordforms
for anchor words + 400 held-out words). Two strictly separated evidence types (Art. XV):

- **Value-free relative channel** — same-row / same-C and same-column / same-V pair observations at density
  `coverage`, propagated by union-find. This is what LA's substitution/morphology channels deliver. It never
  names a value.
- **Anchors** — a q-slot anchor is a **word equation over q signs** (EA-13's La = skeleton length); if
  correct it pins the true (C,V) of its q signs, each of which labels its whole row/col component; if wrong
  (prob `f_wrong`) it seeds **wrong** labels that propagate identically. Anchor words are sampled from
  **real LB wordforms**, so anchors are frequency-biased toward common signs — tail signs can stay dark,
  exactly the LA situation. Only `min(n_anchors, lineages)` anchors are independent (Art. XI); clones are
  re-citations and carry zero new information by construction. Ground-truth values are used only to build
  the known grid and to grade (Art. XII).

Metrics per cell: absolute-value recovery, relative-class recovery, equivalence-class reduction (log₁₀ of
consistent label-assignments removed), residual ambiguity, held-out word recovery, FP rate
(wrong-value / recovered = 1 − calibration precision), recovered fraction.

## 1. The main surface (opaque LB, coverage 0.55, f_wrong 0, full site spread)

`n_anchors ∈ {0..10} × slots ∈ {1,2,4,8} × lineages ∈ {1,2,3,5}` (144 cells; full grid in
`surface_opaque_LB.csv`). Slice at lineages=5, slots=8:

| n_anchors | 0 | 1 | 2 | 3 | 4 | 5 | 8 | 10 |
|---|---|---|---|---|---|---|---|---|
| abs recovery | 0.000 | 0.338 | 0.597 | 0.758 | 0.820 | 0.863 | 0.871 | 0.866 |
| held-out word | 0.000 | 0.073 | 0.303 | 0.543 | 0.669 | 0.746 | 0.768 | 0.756 |
| eq-reduction (log₁₀) | 0.0 | 10.9 | 15.6 | 18.7 | 20.1 | 21.1 | 21.3 | 21.4 |

- **0 anchors ⇒ 0.000 absolute recovery and 0.0 equivalence-class reduction, at every coverage.** The
  relative channel alone relabels freely (confirms the campaign's relabeling-invariance findings from the
  identifiability side).
- **Slots dominate**: at n=5, lineages=5: slots 1→2→4→8 gives abs 0.168 → 0.361 → 0.617 → 0.863. A 1-slot
  pin is nearly worthless even ×5.
- **Lineages bind hard** (Art. XI is not bookkeeping): at n=10, slots=4, lineages 1→2→3→5 gives abs
  0.138 → 0.311 → 0.449 → 0.610. Ten citations from one lineage ≈ one anchor.
- **Plateau inside the prescribed range**: best cell in-range = (8 anchors, 8 slots, 5 lineages) →
  abs 0.871. **abs ≥ 0.90 is UNREACHABLE within n_anchors ≤ 10 / lineages ≤ 5.**

### Minimum configurations (frontier located by an extended sweep, lineages = n_anchors)

| target | minimum (n_anchors, slots, lineages) | abs | held-out word | FP |
|---|---|---|---|---|
| abs ≥ 0.90, FP ≤ 0.05 | **(12, 8, 12)** | 0.972 | 0.952 | 0.000 |
| abs ≥ 0.75, FP ≤ 0.10 | **(3, 8, ≥3 lineage-distinct)** | 0.731–0.758* | 0.543 | 0.000 |
| abs ≥ 0.50, FP ≤ 0.10 | **(2, 8, 2)** | 0.593 | 0.280 | 0.000 |

\* (3,8,3) and (3,8,5) are the same effective configuration (n_indep = 3); their 0.731 / 0.758 spread is
Monte-Carlo noise at 80 reps — the 0.75 frontier sits *at* 3 independent 8-slot anchors, not safely above it.

So on a real 18-consonant syllabary, *script-level* recovery needs **≈ a dozen independent, correct,
long (≥8-slot) anchors**; the first *foothold* (half the values) needs **2–3 independent multi-slot
anchors**. Smaller grids need fewer: synth 8C×5V → (3, 8); synth 15C×5V → (5, 8) — the threshold scales
with the number of consonant rows.

## 2. Sensitivity (holding a nominally-powered set: n=5, slots=4, lineages=5)

- **Coverage** (relative-channel density): abs 0.283 @0.1 → 0.617 @0.55 → **saturates ≈ 0.65 by 0.7–1.0**.
  Once the relative grid is connected, *anchors are the binding constraint, not more relative structure* —
  more corpus-internal pattern cannot substitute for anchors.
- **Incorrect-anchor fraction is the killer axis**: f_wrong 0 → 0.1 → 0.2 → 0.5 gives FP
  0.00 → **0.306** → 0.559 → 0.906 (abs 0.617 → 0.435 → 0.262 → 0.059). Wrong anchors don't just fail —
  they *poison components*: per-anchor error is amplified ≈3× downstream. Note eq-reduction stays ~15
  throughout: **ambiguity reduction is blind to correctness** — a lattice can look maximally "constraining"
  while being mostly wrong. Never cite eq-reduction as evidence of truth.
- **Site coverage**: mild (abs 0.463 @0.2 → 0.617 @1.0); regional anchor bias costs ~15 points, mostly on
  held-out words (0.156 vs 0.483).
- **Dependency clones**: flat at abs ≈ 0.32 for 0/2/4/8 clones on a 2-anchor 2-lineage base — measured
  confirmation that re-citations add nothing (the model enforces Art. XI by construction; the sweep
  demonstrates invariance, it does not independently discover it).

## 3. Adversarial benches

- **Degraded LB matched to LA** (coverage 0.20 ≈ LA's value-free channel: 32/131 subst + 22/131 morph signs
  ⇒ pair-coverage ≈ 0.4² ≈ 0.17–0.20; slots ≤ 2, the LA pin depth): even **10 anchors × 2 slots → abs
  0.215, held-out word 0.045**. At LA-like sparsity the response surface is flat and low: no anchor count
  in the prescribed range recovers the script.
- **Synthetic admin (Zipf, tail-dark, f_wrong 0.05)**: abs ≤ 0.39 with FP up to 0.25 — admin corpora
  concentrate anchors on common signs and the tail never labels; FP grows with anchor count because more
  anchors = more chances to poison.
- **Wrong-language / misspecified grid** (relative edges cross true classes): the lattice **"recovers"
  84–90% of signs with FP ≈ 1.000** at any anchor count ≥ 2. This is the decipherment-delusion generator in
  one row: **volume of recovered values is zero evidence of correctness**; only held-out grading separates
  this bench from the honest ones (Invariant 3).

## 4. Linear A's operating point (measured, not assumed)

Inputs from WP-B/C/D (Art. XI collapse): **DEPENDENCY_COLLAPSED_INDEPENDENT_ANCHORS = 0**; 3 one-toponym-deep
pins (*49, *79, ZU) in ONE value-bearing meta-lineage at 1 slot; SEED_A = 0; value-free coverage ≈ 0.20
(generous: among the 69 A-only signs the measured relative channel is 1/69 — the grant is favourable, the
conclusion holds a fortiori); site_coverage 0.4.

| LA scenario | abs recovery | eq-reduction (log₁₀) | residual ambiguity | held-out word | FP |
|---|---|---|---|---|---|
| **collapsed (honest, SEED_A=0)** | **0.000** | **0.0** | **10^63.4** | 0.000 | 0.000 |
| 3 pins at face value (1 lineage, 1-slot, f_wrong 0.25 ≈ EA-13 La<4) | 0.012 | 2.7 | 10^60.9 | 0.000 | **0.230** |
| inflated: ignore Art.-XI collapse (10 anchors, 2 slots, 5 lineages) | 0.198 | 16.8 | 10^47.0 | 0.035 | 0.000 |

Linear A sits at the surface's **zero point**. Even the deliberately inflated reading of its anchor
inventory (pretending the 26 citation-stacked "multi-channel" signs were 10 independent 2-slot anchors
across 5 lineages) reaches < 20% of sign values and 3.5% of held-out words — an order of magnitude short of
the (12, 8, 12) script-recovery frontier and still short of the (3, 8, 3) foothold. Taking the 3 real pins
at face value buys 1% of signs at 23% FP — worse than silence.

The relative-class rows (rel recovery ≈ 0.97 at the LA points) are an artifact of granting coverage 0.20
with error-free edges; they echo the real LA situation only qualitatively (relative/L2-L3 structure IS
recoverable — the campaign's positive controls — while values are not; morphology-pair recovery hits 0.74
at coverage 0.2 in this engine with **zero** value implication).

## Verdict (mechanical)

- `SURFACE_MEASURED`. Minimum for absolute-value recovery of an LB-scale syllabary (abs ≥ 0.90, FP ≤ 0.05):
  **(n_anchors 12, slots 8, lineages 12)**; first foothold (abs ≥ 0.5): **(2–3 anchors, ≥8 slots,
  lineage-distinct, f_wrong ≲ 0.05)**. Unreachable inside n ≤ 10 × lineages ≤ 5 on an 18-row grid.
- **Linear A operating point: (0, –, –) — `LA_AT_IDENTIFIABILITY_ZERO`**. 0 independent anchors ⇒ 0.000
  absolute recovery, 0.0 bits of equivalence-class reduction, residual ambiguity ~10^63; no coverage
  increase can substitute (saturation ≤ 0.65 even at coverage 1.0 with 5 anchors).
- Quality gates: anchors below ~4 slots or above ~5–10% wrongness are net-poisonous (FP amplification ≈3×);
  clones and re-citations are worthless; misspecified lattices produce near-total false recovery with high
  apparent yield.
- **No transfer licence earned or approached** (this is a design study on known/synthetic scripts;
  SEMANTIC+ remains NOT_AUTHORIZED). What would move LA off the zero point is exactly WP-D's unlock:
  newly-excavated multi-slot, lineage-distinct anchors — not re-analysis of the present corpus.

**Compliance line:** WP-G COMPLETE · surface + benches + LA point from `g_anchor_threshold_lab.py` (seed
20260708, reproducible byte-identical) · known values grade only (Art. XII) · independence = lineage-distinct
(Art. XI) · relative ≠ absolute maintained (Art. XV) · truth-layer ≤ 0.75 · SEED_A = 0 unchanged.
