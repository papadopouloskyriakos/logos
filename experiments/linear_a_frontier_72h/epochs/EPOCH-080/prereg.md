# EPOCH-080 PREREGISTERED PROTOCOL — Vertical Row-to-Row Spacing (line pitch) Regularity (ruled horizontal lines / page grid), cross-site

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-080 (fifth SigLA spatial epoch; ORTHOGONAL PARTNER to E079).
  - E079 established HORIZONTAL glyph spacing WITHIN a line is regular (pitch-CV 0.329 vs random null 0.743, cross-site 3/3).
  - E080 asks the PERPENDICULAR question: are the LINES themselves evenly spaced DOWN the document — i.e., is the
    VERTICAL distance between consecutive rows uniform (like ruled horizontal lines on a page), more so than a random
    partition of the column height, and consistent cross-site? A scribe could have even glyph spacing but uneven line
    spacing (or vice versa); the two are independent layout properties, and together (if both regular) they establish
    a full 2D ruled GRID.
**Layer:** L2 (pure structural graphic / layout property)
**Operator:** logos z.ai research worker (GLM-5.2), proposer/operator only — MECHANICAL verdict from a FROZEN rule.
**Status:** FROZEN before any null-model run.

## 1. QUESTION
Is the VERTICAL SPACING of rows (lines) REGULAR — a deliberate ruled-horizontal-lines / page-grid layout — i.e., are
the center-to-center VERTICAL PITCHES between consecutive rows MORE UNIFORM than a random allocation of the same
total column span (same number of rows, same top-to-bottom extent) would give? And is that regularity CONSISTENT
CROSS-SITE? Pure structural layout property: signs are OPAQUE IDs; NO value, NO reading, NO meaning; only glyph
POSITIONS (specifically ROW y-positions) matter.

## 2. NON-CIRCULAR / DISCIPLINE (hard)
- Positions from `bbox=[x,y,w,h]` (y = top edge; y-center = y + h/2).
- A ROW = a y-band: cluster glyphs by y-center within ~0.6 × median glyph-height of the doc.
- Each row's y-position = MEDIAN y-center of that row's glyphs.
- Sort rows top-to-bottom; VERTICAL PITCH = consecutive row-position difference.
- Use docs with >=3 rows (>=2 vertical pitches).
- Doc line-pitch-CV = CV (sd/mean) of the doc's vertical pitches.
- The RANDOM ROW-ALLOCATION null replaces the doc's vertical pitches with a random composition of (n_rows-1) positive
  pitches summing to the SAME total row-span (same number of rows, same top-to-bottom extent), so it preserves row
  count + column height and destroys ONLY the REGULARITY of line spacing. Uniform Dirichlet / random breakpoints on
  the column height.
- Regular ruled layout => observed line-pitch-CV << null line-pitch-CV. L2 ONLY.
- DISTINCT from E079: E079 was HORIZONTAL within-row glyph pitch (x-direction, within a single row); E080 is VERTICAL
  between-row line pitch (y-direction, across rows). The two metrics share the row-clustering primitive but measure
  orthogonal layout regularities.

## 3. DATA (verified, pre-decoded)
- `BASE/data/sigla_glyphs_bbox.json` — list of docs; each doc has
  `glyphs[{sign, bbox:[x,y,w,h], is_divider}]`, plus `site`.
- EXCLUDE `is_divider` glyphs. Use docs with >=6 non-divider bbox glyphs AND >=3 rows (>=2 vertical pitches).
- Sites with >=15 usable docs: Haghia Triada (~124), Khania (~26), Zakros (~21). Read the JSON directly.

## 4. METRIC (frozen)
- Per doc: y-cluster into rows (within 0.6 × median glyph-height); row y-position = median y-center of the row's
  glyphs; sort rows top-to-bottom; VERTICAL PITCHES = consecutive row-position differences; doc line-pitch-CV =
  sd/mean of those pitches.
- CORPUS statistic S_obs = MEDIAN doc line-pitch-CV over usable docs. (Low = regular ruled lines.)

## 5. NULL MODEL (frozen)
- For each doc: draw a random composition of (n_rows-1) positive pitches summing to that doc's OBSERVED total
  row-span (uniform Dirichlet = random breakpoints on the column height), recompute the doc line-pitch-CV; recompute
  S = median doc line-pitch-CV; >=1000 draws.
- One-sided perm p = frac(null S <= S_obs) (regular = observed MORE uniform / LOWER CV than random).
- Report S_obs, null-median, perm p, normalized effect S_obs / null_median.

## 6. CROSS-SITE
For each site with >=15 usable docs, recompute S_site (median doc line-pitch-CV) + its own random row-allocation
null + perm p + direction; count sites significant regular (perm p<=0.05, S_site<null).

## 7. POSITIVE CONTROL FIRST (synthetic, gates verdict)
- (a) DETECT: build synthetic docs with EVENLY-SPACED rows (low vertical pitch CV); confirm S flagged below null
  (perm p<=0.05); power_est over >=20 replicates.
- (b) FALSE-POSITIVE: build synthetic docs with RANDOM-composition row spacings; confirm S NOT flagged as regular
  (rejection <=0.10 across >=20 draws).
- If it can't detect ruled rows OR fires on random spacing => MACHINERY_UNINFORMATIVE.

## 8. FROZEN MECHANICAL VERDICT
- LINE_SPACING_REGULAR_CROSS_SITE iff PC passed (power_est>=0.5) AND global S_obs significantly < null
  (perm p<=0.05) AND significant regular in >=2 sites — vertical line spacing is a deliberate ruled/regular layout
  cross-site (which, WITH E079, means a 2D ruled grid).
- LINE_SPACING_REGULAR_SITE_LOCAL iff global significant BUT <2 sites significant.
- LINE_SPACING_NOT_REGULAR iff S_obs NOT significantly below null.
- LINE_SPACING_UNDERPOWERED iff <2 sites with >=15 usable docs OR PC power_est<0.5.
- MACHINERY_UNINFORMATIVE iff PC detect/false-positive calibration fails.

## 9. SCOPE / OPAQUE
L2 only. Signs are opaque catalog IDs. No reading, no value, no meaning. Only POSITIONS (row y-positions) matter.
