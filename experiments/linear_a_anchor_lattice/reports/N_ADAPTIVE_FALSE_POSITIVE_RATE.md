# TASK N — ADAPTIVE FALSE-POSITIVE RATE (family-wise, per selection layer)

**Campaign:** research/linear-a-anchor-lattice · **Seed:** 20260708 · **Constitution:** v2.2
**Source:** `scripts/n_adaptive_null_programme.py` → `data/controls/n_adaptive_null.json`
(120 full-adaptive replicates + 20 planted; definitions frozen in `reports/N_NULL_SPEC.md` §4).
Companion: `reports/N_NULL_RESULTS.md` (tiers, UNSAT adjudication, FDR).

## 1. Headline

| pipeline | family-wise false-positive rate | 95% bound |
|---|---|---|
| **DISCIPLINED** (Art. XI collapse + retention gate + licensed accounting) — licence-gated legs d1+d3 | **0 / 120 = 0.0%** | CP95 upper **2.46%** |
| DISCIPLINED including the conditional-S2 leg d2 (frozen spec definition) | 10 / 120 = **8.3%** | CP95 upper 13.7% |
| **NAIVE-ADAPTIVE** (citation-stacking + best-of-everything) | **120 / 120 = 100%** | — |

The naive arm is the calibration that the instruments have power: the same search that returns
0 on real data returns an apparent "decipherment" in **every** null replicate when discipline is
removed. The disciplined licence-gated verdict fires never — matching its real-data output
(0 retained, 0 licensed bits) and the repo-level gate calibration (best-of-100 random maps:
3/500 = 0.6%).

## 2. Where the naive false positives come from (per selection layer, 120 reps)

| naive leg (frozen) | fires | mechanism under null |
|---|---|---|
| n1: naive retained ≥ 1 (raw-lineage / stacked accounting, no adaptive band, gC without held-out leg) | **120/120**, mean **20.7 signs/rep** | 148 re-targeted pin slots spread over ~90 signs; any ≥4-slot edge "confirms" its target |
| n2: ≥3 stacked "channels" on some sign | **120/120**, mean **17.8 signs/rep** | counting citations (L+H+C) instead of collapsed lineages — the real-data equivalent "fires" on **23 signs** (the C §4 inventory artifact) |
| n3: min nominal p < 0.10 across layers | **117/120**, median min-p **0.00141** | best-of: greedy anchor-subset (binomial vs 0.2615 chance), top-3 value selection, best of 4 bridge methods, 12 stroke features, 8 lexica, 5 seed restarts, 3 grains, loosest threshold |
| n4: naive MDL ΔDL < 0 | **120/120** (≈ −656 bits every rep) | clone slots counted as independent data — the H naive_raw −660.2 reproduced under pure noise |
| n5: best-of-language nominal p < 0.05 | 8/120 | random-lexicon matches on the few fully-pinned forms; the corpus-scale version is G's wrong-language bench: 0.836–0.895 "recovered" at FP ≈ 1.0 |

Adaptive selection alone (n3) converts pure noise into a median nominal p of ~1.4 × 10⁻³ —
a ~35× significance exaggeration at the median before any dependency error is added. This is a
measured, mechanical demonstration of why the campaign's Art. VII search receipt and Art. VIII
effective-n deflation are load-bearing, not ornamental.

## 3. The disciplined breakdown, honestly

- **d1 (retained ≥ 1): 0/120.** Also 0 in all 400 Tier-2 lattice nulls and the 200 cited
  hyperedge nulls. With CN4/LN2 (dependency-cloned nulls faithful to the real evidence
  structure), max independent anchors never exceeds 2 (< 3 = branch A) in 1,300 replicates.
- **d3 (rel channel at Bonferroni 0.05/648): 0/120** (min observed rel p under null = 0.0191,
  never < 7.7 × 10⁻⁵).
- **d2 (conditional-S2 A-only ≥ 0.1 bits): 10/120.** All ten sit at 0.100–0.106 bits — the
  conditional statistic is anticonservative under adaptive search because null re-targeting
  pins ~20 A-only signs (real data pins 0 parseable A-only signs; observed value 0.000 bits,
  below all 120 nulls). Standing lesson (already implicit in Art. XV, now measured): a
  conditional entropy reduction from a single unearned lineage must never be a reporting
  criterion; only the licence-gated legs are calibrated.

## 4. Gate power (the zero is informative)

**Planted-positive control: 20/20 retained** — a single A-only sign given 3 value-consistent
edges on genuinely distinct collapsed lineages (META_CONTINUITY + LIN_EG + synthetic bilingual),
2 concrete sites, 1 non-vacuous held-out edge, inside an otherwise-null world, is retained every
time. Combined with 0 disciplined retentions across 980 gate-level null evaluations (360 =
120 adaptive reps × 3 grains, 400 new lattice nulls, 200 cited hyperedge nulls, 20 planted
worlds' non-planted signs) — and branch A never openable in 1,000 further CN4 replicates —
the programme brackets the gate:
**specificity ≈ 100% under the fullest adaptive search this campaign performed; sensitivity 100%
on the minimal genuinely-independent configuration.** The campaign's `ZERO_RETAINED` is therefore
a statement about the evidence (one collapsed value-bearing meta-lineage, Task C), not about an
unopenable gate.

## 5. Search-adjusted significance of the campaign's one nontrivial positive finding

The UNSAT (15/24 continuity × substitution violations) adjudicates as **`UNSAT_GENERIC`**
(N_NULL_RESULTS §5): P(UNSAT | matched null) = 1.000 in all three matched families; P(viol ≥ 15)
= 0.77–0.93; the real pin-set violates *less* than chance, ns in both directions after the ×2
direction correction. No selection-adjusted test in the campaign survives BH at q = 0.05
(0 discoveries over the 6 recorded p-values; smallest q = 0.455).

## 6. Bottom line for Task O

Under the complete adaptive search this campaign actually performed — sources, anchors,
lineage assignments, stroke features, 4 bridge methods, 3 inventories, 3 solvers, a 65-slot
value grid, thresholds, restarts, subgroups, and best-result reporting — the disciplined
pipeline's licence-gated false-positive rate is **0/120 (CP95 ≤ 2.46%)**, the gate provably
opens on genuine independence (20/20), the naive counterpart fabricates ~20 sign "readings" per
replicate at FWER 100%, and the campaign's sole positive-flavoured finding is a generic property
of random pin-sets. Nothing in the null programme perturbs any prior verdict: C/G/H/I/J stand as
issued. No licence changes; SEMANTIC+ remains NOT_AUTHORIZED.
