# EPOCH-084 prereg — Is E080's vertical line-spacing regularity DELIBERATE, or a line-HEIGHT artifact?

## Layer
L2 (geometry-only, opaque IDs, positions/heights only).

## Question
E080 found vertical row-to-row PITCH is regular. But line-pitch = inter-line GAP + row HEIGHT, and
glyph/row heights are fairly uniform, so uniform heights alone regularize line-pitch even with random
gaps. E083 ran the horizontal analog and found E079's pitch-regularity is WIDTH-DRIVEN (not deliberate).
E084 runs the vertical analog with a HEIGHT-PRESERVING random-gap null.

## Design
- DATA: BASE/data/sigla_glyphs_bbox.json. Exclude is_divider. Docs with >=6 non-divider bbox glyphs AND
  >=3 rows. Sites with >=15 usable docs: Haghia Triada, Khania, Zakros.
- OBSERVED: per-doc line-pitch-CV (CV of consecutive row-center differences); S_obs = median across docs.
- NULL (height-preserving random-gap): keep each row's height (median glyph height in row) and the
  column span, randomize ONLY the inter-line gaps; recompute line-pitch-CV. null_median = median across
  docs and 500 draws.
- DELIBERATE = observed line-pitch-CV significantly BELOW the height-preserving null (perm_p<=0.05).
- Permutation: deliberate = observed BELOW null; p = (#{null_median <= S_obs}+1)/(500+1).

## Hypothesis (pre-data)
A coordinator pre-check found observed 0.111 vs height-preserving null 0.154 (ratio 0.716) -> prior is
DELIBERATE. Test mechanically with per-site + PC.

## Positive Control (synthetic, gates verdict)
- (a) DETECT: ~40 docs with EQUAL inter-line gaps (deliberate) + variable row heights (~Uniform[6,12]);
  confirm observed line-pitch-CV << null (perm_p<=0.05), power_est over >=15 reps.
- (b) FALSE-POSITIVE (height-only): ~40 docs with RANDOM inter-line gaps + SAME variable heights;
  confirm observed NOT below null (rate<=0.10).
- If can't detect deliberate OR fires on height-only-random -> MACHINERY_UNINFORMATIVE.

## Frozen Verdict
- LINE_SPACING_DELIBERATE_CROSS_SITE iff PC passed AND global perm_p<=0.05 AND significant in >=2 sites.
- LINE_SPACING_DELIBERATE_SITE_LOCAL iff global significant BUT <2 sites.
- LINE_REGULARITY_HEIGHT_DRIVEN iff global observed NOT significantly below null (perm_p>0.05).
- LINE_SPACING_UNDERPOWERED iff <2 sites with >=15 usable docs OR PC power<0.5.
- MACHINERY_UNINFORMATIVE iff PC calibration fails.

## Relation to priors
- Tests/CONFIRMS E080 (vertical line-pitch regularity).
- Symmetric partner of E083 (horizontal WIDTH-DRIVEN finding).

## Non-circularity
Opaque IDs; geometry only (positions, heights); no semantic/phonetic content; null preserves the very
feature (row heights) that could spuriously regularize pitch, so any deliberate signal must come from
the gaps themselves.
