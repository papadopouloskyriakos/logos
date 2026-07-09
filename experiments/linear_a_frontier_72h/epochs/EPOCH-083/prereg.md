# EPOCH-083 PREREGISTRATION (FROZEN)

## Task
E079 found horizontal center-to-center PITCH regularity (pitch-CV 0.329 vs random-composition null 0.743).
But pitch = inter-glyph GAP + glyph WIDTH, and glyph widths are fairly uniform (E076), so uniform widths
alone regularize pitch even with random gaps. E082 surfaced this and returned MACHINERY_UNINFORMATIVE.

E083 QUALIFIES/TESTS E079: is the horizontal pitch-regularity DELIBERATE even spacing, or a glyph-WIDTH
artifact? We separate them with a WIDTH-PRESERVING random-gap null.

## Hypothesis (H1)
The horizontal pitch regularity is DELIBERATE even spacing: the inter-glyph GAPS themselves are regular,
beyond what uniform glyph widths would impose.

## Null (H0, width-preserving random-gap)
Keep each glyph's ACTUAL width and the row's center-span; randomize ONLY the gap allocation; recompute
pitch-CV. Under H0, observed pitch-CV is NOT below this null.

## Test
deliberate spacing = observed pitch-CV SIGNIFICANTLY BELOW the width-preserving random-gap null
(one-sided permutation, perm_p = frac(null_median <= S_obs), LOW => observed is low => deliberate).

## Data
- BASE: experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json
- Exclude is_divider glyphs; docs with >=6 non-divider bbox glyphs.
- Sites with >=15 usable docs: Haghia Triada, Khania, Zakros.

## Discipline
- L2 (geometry only, no semantics).
- OPAQUE IDs: no sign identities used; only bbox geometry (left, width, y-center, height).
- Positions only.

## Positive Control (synthetic, gates verdict)
- (a) DETECT: ~40 docs, EQUAL gaps (deliberate even spacing) + variable widths ~ Uniform[4,9].
      Expect perm_p<=0.05, power_est>=0.5 over >=15 reps.
- (b) FALSE-POSITIVE: ~40 docs, RANDOM gaps + SAME variable widths. Expect perm_p NOT <=0.05
      (false-positive rate <=0.10).
- If PC cannot detect deliberate spacing OR fires on width-only-random-gap -> MACHINERY_UNINFORMATIVE.

## Frozen Verdict (mechanical)
- HORIZONTAL_SPACING_DELIBERATE_CROSS_SITE iff PC passed AND global perm_p<=0.05 AND significant in >=2 sites.
- HORIZONTAL_SPACING_DELIBERATE_SITE_LOCAL iff global significant BUT <2 sites.
- HORIZONTAL_REGULARITY_WIDTH_DRIVEN iff global observed pitch-CV NOT significantly below null (perm_p>0.05).
- HORIZONTAL_SPACING_UNDERPOWERED iff <2 sites with >=15 usable docs OR PC power<0.5.
- MACHINERY_UNINFORMATIVE iff PC calibration fails.

"Significant in a site" = site perm_p<=0.05.

## Non-circularity
The width-preserving null uses the SAME widths and span as observed; only gap allocation is randomized.
This isolates gap-regularity from width-regularity. E079's original null (random composition) is replaced
by a stricter, width-matched null, so any signal here is NOT explainable by E079's mechanism.
