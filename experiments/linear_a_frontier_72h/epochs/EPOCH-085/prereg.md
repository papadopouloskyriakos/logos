# EPOCH-085 PREREGISTRATION (FROZEN)

## Task
DO SCRIBES MARK THE DOCUMENT HEADING (TOP SPATIAL ROW) WITH LARGER GLYPHS THAN THE BODY?

## Layer
L2 — opaque IDs, AREAS and positions only. No phonetic/semantic values used.

## Axis (DISTINCT from prior epochs)
Size x document REGION (top spatial row vs body rows).
- E077 = size x word-INITIAL
- E078 = size x FREQUENCY
- E079-084 = SPACING/pitch
This is a NEW axis: spatial row position.

## Hypothesis
Administrative docs may use a visual hierarchy — a title/heading row drawn LARGER for salience.
HEADING HIERARCHY = top row glyphs LARGER than a random row would be.

## Metric (per doc)
R = log( median glyph AREA in the FIRST (top) row / median glyph AREA in ALL remaining rows ).
R > 0 = heading larger.

## Global statistic
S_obs = median of R over docs.

## Null model
Random-row-as-pseudo-heading: within each doc, pick a UNIFORMLY RANDOM row to be the pseudo-heading
and recompute R. The null median answers: "is the ACTUAL top row larger than a RANDOM row would be?"

## Direction
DIRECTIONAL (heading LARGER): perm_p = fraction of null draws with median-R >= S_obs.

## Data
BASE/data/sigla_glyphs_bbox.json (located at experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json).
Exclude is_divider. Docs need >=6 non-divider bbox glyphs AND >=2 rows AND first row >=2 glyphs AND rest >=3 glyphs.
Sites with >=15 usable docs: Haghia Triada, Khania, Zakros.

## Verdict rule (FROZEN, mechanical)
- HEADING_SIZE_HIERARCHY_CROSS_SITE iff PC passed AND global perm_p<=0.05 AND S_obs>0 AND significant in >=2 sites.
- HEADING_SIZE_HIERARCHY_SITE_LOCAL iff PC passed AND (global OR any site) significant BUT <2 sites significant.
- NO_HEADING_SIZE_HIERARCHY iff PC passed AND global NOT significant (perm_p>0.05 or S_obs<=0) AND 0 sites significant.
- HEADING_SIZE_UNDERPOWERED iff <2 sites with >=15 usable docs OR PC power<0.5.
- MACHINERY_UNINFORMATIVE iff PC calibration fails (can't detect inflated OR fires on uniform).

Significant (per site) = perm_p<=0.05 AND S_obs>0.

## Positive control (gates verdict)
(a) DETECT: ~40 synthetic docs, first row areas INFLATED x1.7 vs body; confirm S_obs sig > 0; power over >=15 reps.
(b) FALSE-POSITIVE: ~40 synthetic docs, all rows SAME distribution; confirm fire-rate <=0.10 over >=15 reps.

## Non-circularity
Geometry (bbox areas, row positions) only. No sign/phonetic/semantic labels. Verdict is mechanically
derived from a frozen rule applied to S_obs and perm_p.
