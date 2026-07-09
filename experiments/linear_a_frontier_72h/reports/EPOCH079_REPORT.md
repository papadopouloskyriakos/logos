# EPOCH-079 REPORT — Inter-Glyph Spacing Regularity (ruled / monospaced-like), cross-site

**Campaign:** Linear A frontier-72h  |  **Epoch:** EPOCH-079 (fourth SigLA spatial epoch)
**Layer:** L2 (pure structural layout property — opaque sign IDs, positions only)
**Operator:** logos z.ai research worker (GLM-5.2), proposer/operator — MECHANICAL verdict from a FROZEN rule.
**Verdict:** `SPACING_REGULAR_CROSS_SITE`

## Question
Is the horizontal SPACING of glyphs within a line REGULAR (a deliberate ruled / columnar /
monospaced-like layout) — are the center-to-center PITCHES between consecutive glyphs in a row
MORE UNIFORM than a random allocation of the same total row width would give — and is that
regularity consistent CROSS-SITE? (Follows E076 shared per-sign size, E077 size not positional,
E078 size-frequency economy.)

## Method (frozen in prereg.md, hash `aa0120a2…`)
- ROW = y-band: cluster non-divider glyphs by y-center within 0.6 × median glyph-height.
- Within a row (>=3 glyphs): sort by x-center; PITCH = consecutive center-to-center distance.
- Doc pitch-CV = sd/mean of pooled within-row pitches. **S_obs = MEDIAN doc pitch-CV** over usable docs.
- Usable doc: >=6 non-divider bbox glyphs AND >=1 row of >=3 glyphs → **246 docs**.
- **NULL (random-composition):** for each row, replace its pitches with a uniform-Dirichlet /
  random-breakpoint composition summing to the SAME row pitch-total (preserves row span + glyph
  count, destroys only regularity); recompute S = median doc pitch-CV; 2000 draws;
  one-sided perm p = frac(null S <= S_obs).

## Positive Control (synthetic — gates verdict) — PASSED
- Self-check: on REGULAR synthetic, S_obs=0.024 vs null-median=0.704 (obs << null, OK);
  on RANDOM synthetic, S_obs=0.756 vs null-median=0.729 (~null, OK).
- DETECT: power_est = **1.0** (regular-pitch synthetics flagged in 25/25 reps, median perm p=0.0).
- FALSE-POSITIVE: fp_rate = **0.0** (random-composition synthetics flagged in 0/25 reps).
- → machinery is informative; PC gates the verdict.

## Global result
| stat | value |
|---|---|
| n_docs | 246 |
| **S_obs** (median doc pitch-CV) | **0.3287** |
| null-median | 0.7429 |
| perm p (2000 draws) | **0.0** |
| ratio S_obs / null_median | **0.4425** |

Observed within-row pitches are roughly **half as variable** as a random allocation of the same
row spans. Spacing is regular.

## Cross-site (sites with >=15 usable docs)
| site | n_docs | S_site | null_median | perm_p | sig_regular |
|---|---|---|---|---|---|
| Haghia Triada | 143 | 0.3541 | 0.7565 | 0.0 | **yes** |
| Khania | 33 | 0.2677 | 0.6850 | 0.0 | **yes** |
| Zakros | 21 | 0.3456 | 0.7540 | 0.0 | **yes** |

Not testable (<15 docs): Knossos (12), Phaistos (12), Arkhanes (8), Mallia (5), others ≤3.
**n_sites_testable = 3, n_sites_sig_regular = 3.** Khania is the most regular; all three sit far
below their site-specific nulls (~0.69–0.76).

## Frozen mechanical verdict
PC passed (power_est=1.0 ≥ 0.5) AND global S_obs significantly < null (perm p=0.0 ≤ 0.05) AND
significant regular in >=2 sites (3/3) → **`SPACING_REGULAR_CROSS_SITE`**.

## Bottom line
Inter-glyph horizontal spacing within a line is a **deliberate ruled / regular (monospaced-like)
layout, cross-site** — not a random gap allocation. Median doc pitch-CV ≈ 0.33 vs a
random-composition null ≈ 0.74 (perm p=0.0, ratio 0.44), replicated in all three testable sites
(Haghia Triada, Khania, Zakros). Combined with E076–E078, the Linear A writing surface carries a
shared cross-site graphic convention in BOTH glyph SIZE and glyph PLACEMENT: signs sit on an
implicit columnar grid. L2 only — opaque IDs, positions only, no reading.

## Outputs
- `prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json` (this epoch dir)
- `data/epoch_079/per_doc_pitch_cv.json` (per-doc pitch-CV table, 246 docs)
