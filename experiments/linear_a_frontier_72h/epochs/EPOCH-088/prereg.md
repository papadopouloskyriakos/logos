# EPOCH-088 PREREGISTRATION (FROZEN)

## Task
Is E087's heading-size <-> header-length tradeoff (Spearman -0.189 at Haghia Triada) a
FIXED first-row INK BUDGET, or a SOFT tendency?

## Hypothesis (mechanism)
If scribes allocate a roughly CONSTANT total glyph-AREA to the header row, then larger
glyphs mechanically leave room for fewer of them -> the size<->length tradeoff is a
byproduct of a fixed area budget.

## Test (L2, opaque IDs, geometry only; no sign values used)
- Population: HT docs with >=6 non-divider bbox glyphs AND >=2 detected rows.
- Per doc: first row total ink = sum of glyph areas; first_count = #glyphs in first row;
  first_med_area = median glyph area in first row.
- S_obs = CV (pstdev/mean) of first-row TOTAL INK across docs.
- NULL (tradeoff broken): pair a UNIFORMLY RANDOM first-row median-area with a UNIFORMLY
  RANDOM first-row count (independent draws from the two marginals); total_ink ~
  median_area * count; recompute CV; 2000 draws.
- perm_p = (#{null CV <= obs CV} + 1) / (2000 + 1).
- Budget holds iff obs CV significantly BELOW null (perm_p <= 0.05).

## Positive control (synthetic, gates verdict)
- DETECT arm: ~140 docs with fixed total header ink C0 (small noise); count random;
  median_area = C0/count (perfect size<->count anti-correlation). Expect perm_p<=0.05.
  power_est over >=15 reps.
- FALSE-POSITIVE arm: ~140 docs with INDEPENDENT random median-area and count (no budget).
  Expect fire-rate <=0.10 over >=15 reps.
- PC fails -> MACHINERY_UNINFORMATIVE.

## Frozen verdict rule
- HEADER_INK_BUDGET_CONSTRAINED  iff PC passed AND perm_p <= 0.05.
- HEADER_INK_NOT_BUDGETED        iff PC passed AND perm_p > 0.05.
- HEADER_INK_BUDGET_UNDERPOWERED iff n_docs < 60 OR PC power_est < 0.5.
- MACHINERY_UNINFORMATIVE        iff PC calibration fails.

## Coordinator pre-check (advisory, not binding)
obs first-ink CV=0.639 vs independence-null median 0.717, perm_p=0.134 -> expected
HEADER_INK_NOT_BUDGETED.

## Discipline
L2, opaque IDs, areas/counts only, no sign values. la_touched=true. Non-circular: this
epoch does not consume E087's correlation as evidence; it tests a mechanism on raw geometry.
