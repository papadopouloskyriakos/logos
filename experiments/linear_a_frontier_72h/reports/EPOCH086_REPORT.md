# EPOCH-086 REPORT — Top-Row Glyph-Count / Density (Header Line?)

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-086 · **Layer:** L2 (spatial; opaque IDs; counts/positions only)
**Axis (DISTINCT):** row GLYPH-COUNT and DENSITY by row position. (E085=row SIZE; E079-084=spacing/pitch; E077=size×word-initial.)

## Question
Does the TOP (first) spatial row carry MORE glyphs than lower rows (a "full/header line")?
Width/geometry effect, or a deliberately packed header?

## Method
- Per-doc `R_count = log(count(first row) / mean count(rest))`; global `S_obs = median(R_count)`.
- Secondary confound `R_density = log(density(first)/mean density(rest))`, `density = count/(x-span+1)`.
- Null: random-row-as-heading (directional, top LONGER); `perm_p = frac(null median-R >= S_obs)`, 1000 draws.
- Per-site: Haghia Triada, Khania, Zakros (sites with >=15 usable docs).
- Synthetic positive control: DETECT 1.7x header (power over 20 reps) + uniform FALSE-POSITIVE (fire-rate over 20 reps).

## Positive Control — PASSED
- DETECT: median perm_p = 0.0348, power_est = 0.95 (>=0.5 required).
- FALSE-POSITIVE (uniform): fire-rate = 0.00 (<=0.10 required).
- => Machinery is informative.

## Results — COUNT (primary)
| Scope | S_obs | null_median | perm_p | n_docs | SIG? |
|---|---|---|---|---|---|
| Global | +0.0645 | 0.0 | 0.00999 | 240 | **YES** |
| Haghia Triada | +0.1383 | 0.0 | 0.003996 | 140 | **YES** |
| Khania | 0.0000 | 0.0 | 0.9091 | 36 | no |
| Zakros | +0.0834 | 0.0 | 0.1189 | 23 | no (marginal) |

Top row carries MORE glyphs than lower rows globally and at HT; null at Khania; marginal at Zakros.

## Results — DENSITY (confound)
| Scope | S_obs | perm_p | SIG? |
|---|---|---|---|
| Global | -0.0471 | 0.1079 | no |
| Haghia Triada | -0.1260 | 0.6364 | no |
| Khania | +0.0617 | 0.0260 | yes (but COUNT null here) |
| Zakros | +0.0119 | 0.0979 | no |

Global DENSITY is NOT significant and S_obs <= 0. => The longer top row is **WIDTH/GEOMETRY-driven** (a full-width header line), NOT a deliberately packed header. Parallels E083 WIDTH-DRIVEN.

## Verdict (FROZEN, mechanical)
**HEADER_ROW_LONGER_SITE_LOCAL**

PC passed; global COUNT significant (S_obs>0, perm_p<=0.05); but only 1 of 3 sites (Haghia Triada) significant => site-local, not cross-site.

## Interpretation
- The top spatial row is a longer "header line" — but only robustly at Haghia Triada.
- The extra length is GEOMETRY (the top row spans wider), not packing: density is not elevated globally or at HT (in fact slightly negative at HT).
- This is consistent with a full-width top register at HT, adding to E081+E085's HT layout registers (a distinct axis: row glyph-COUNT, not row SIZE).

## Bottom line
The top row IS a longer header line, but it is an **HT register effect** (site-local), and it is **width/geometry-driven** (a full-width top line), not a deliberately packed header. Khania shows no top-row length structure; Zakros is marginal. A full, expected SITE_LOCAL + WIDTH-DRIVEN result.

## Files
- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-086/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-086/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-086/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-086/result.json`
