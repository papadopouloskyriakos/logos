# EPOCH-079 PREREGISTERED PROTOCOL — Inter-Glyph Spacing Regularity (ruled / monospaced-like), cross-site

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-079 (fourth SigLA spatial epoch; follows E076 shared per-sign size convention,
E077 size carries no positional info, E078 size-frequency economy of effort)
**Layer:** L2 (pure structural graphic / layout property)
**Operator:** logos z.ai research worker (GLM-5.2), proposer/operator only — MECHANICAL verdict from a FROZEN rule.
**Status:** FROZEN before any null-model run.

## 1. QUESTION
Is the horizontal SPACING of glyphs within a line REGULAR — a deliberate ruled / columnar /
monospaced-like layout — i.e., are the center-to-center PITCHES between consecutive glyphs in a row
MORE UNIFORM than a random allocation of the same total row width would give? And is that regularity
CONSISTENT CROSS-SITE? Pure structural layout property: signs are OPAQUE IDs; NO value, NO reading,
NO meaning; only glyph POSITIONS matter.

## 2. NON-CIRCULAR / DISCIPLINE (hard)
- Positions from `bbox=[x,y,w,h]` (x = left edge; glyph spans `[x, x+w]`).
- A ROW = a y-band: cluster glyphs by y-center within ~0.6 × median glyph-height of the doc.
- Within a row (>=3 glyphs): sort by x-center; PITCH = consecutive center-to-center distance.
- Doc pitch-CV = CV (sd/mean) of all the doc's within-row pitches (pooled across its >=3-glyph rows).
- The RANDOM-COMPOSITION null replaces each row's pitches with a random composition summing to the
  SAME row span (same number of glyphs, same total width), so it preserves row span + glyph count and
  destroys ONLY the regularity of spacing. Uniform Dirichlet / random breakpoints on the span.
- Regular layout => observed pitch-CV << null pitch-CV. L2 ONLY.

## 3. DATA (verified, pre-decoded)
- `BASE/data/sigla_glyphs_bbox.json` — list of docs; each doc has
  `glyphs[{sign, bbox:[x,y,w,h], is_divider}]`, plus `site`.
- EXCLUDE `is_divider` glyphs. Use docs with >=6 non-divider bbox glyphs AND >=1 row of >=3 glyphs
  (~246 docs). Sites with >=15 usable docs: Haghia Triada, Khania, Zakros (Phaistos/Knossos smaller —
  report n). Read the JSON directly.

## 4. METRIC (frozen)
- Per doc: y-cluster into rows (within 0.6 × median glyph-height); per row (>=3 glyphs) sort by
  x-center, compute consecutive center-to-center PITCHES; pool the doc's pitches; doc pitch-CV = sd/mean.
- CORPUS statistic S_obs = MEDIAN doc pitch-CV over usable docs. (Low = regular.)

## 5. NULL MODEL (frozen)
- For each doc, for each row: draw a random composition of (n_row − 1) positive pitches summing to
  that row's OBSERVED pitch-total (uniform Dirichlet = random breakpoints on the span), recompute the
  doc pitch-CV; recompute S = median doc pitch-CV; >=1000 draws.
- One-sided perm p = frac(null S <= S_obs) (regular = observed MORE uniform / LOWER CV than random).
- Report S_obs, null-median, perm p, normalized effect S_obs / null_median.

## 6. CROSS-SITE
For each site with >=15 usable docs, recompute S_site (median doc pitch-CV) + its own
random-composition null + perm p + direction; count sites significant regular (perm p<=0.05, S_site<null).

## 7. POSITIVE CONTROL FIRST (synthetic, gates verdict)
- (a) DETECT: build synthetic docs with REGULAR pitches (low CV); confirm S flagged below null
  (perm p<=0.05); power_est over >=20 replicates.
- (b) FALSE-POSITIVE: build synthetic docs with RANDOM-composition pitches; confirm S NOT flagged as
  regular (rejection <=0.10 across >=20 draws).
- If it can't detect regular spacing OR fires on random spacing => MACHINERY_UNINFORMATIVE.

## 8. FROZEN MECHANICAL VERDICT
- SPACING_REGULAR_CROSS_SITE iff PC passed (power_est>=0.5) AND global S_obs significantly < null
  (perm p<=0.05) AND significant regular in >=2 sites.
- SPACING_REGULAR_SITE_LOCAL iff global significant BUT <2 sites significant.
- SPACING_NOT_REGULAR iff S_obs NOT significantly below null.
- SPACING_UNDERPOWERED iff <2 sites with >=15 usable docs OR PC power_est<0.5.
- MACHINERY_UNINFORMATIVE iff PC detect/false-positive calibration fails.

## 9. SCOPE / OPAQUE
L2 only. Signs are opaque catalog IDs. No reading, no value, no meaning. Only POSITIONS matter.
