# EPOCH-089 PREREGISTRATION (FROZEN)

## Task
Is the header row's writing width (x-extent) constrained, explaining E087's heading-size <-> header-length tradeoff (Spearman -0.189)? E088 REJECTED a fixed INK (total-area) budget. This epoch tests the better-motivated alternative: a fixed WRITING WIDTH.

## Hypothesis (L2, within-HT, geometry only)
If the header row occupies a roughly fixed horizontal extent (bounded writing area / near-full document width, per E086), then bigger glyphs mechanically leave room for fewer -> the E087 size<->count tradeoff is a byproduct of a bounded writing width.

## Data
- Source: experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json
- Filter: site == "Haghia Triada"; docs with >=6 non-divider bbox glyphs AND >=2 rows (rows_of). Opaque IDs only.
- Expected n ~ 140.

## Metric
S_obs = CV (pstdev/mean) of first-row X-EXTENT (max glyph right - min glyph left) across HT docs.

## Null (break target-width regularization)
Pool ALL first-row glyph WIDTHS and ALL first-row inter-glyph GAPS across HT. For each doc rebuild a synthetic extent = sum(count random widths) + sum((count-1) random gaps) at the doc's ACTUAL count; recompute CV; 2000 draws.

## Decision rule (FROZEN, mechanical)
- WIDTH-CONSTRAINED iff PC passed AND perm_p <= 0.05 (obs x-extent CV significantly BELOW assembly null -> extent regularized to ~fixed width).
- WIDTH-NOT-CONSTRAINED iff PC passed AND perm_p > 0.05 (obs CV ~ null -> extent NOT more constant than random assembly).
- WIDTH-UNDERPOWERED iff n < 60 usable HT docs OR PC power < 0.5.
- MACHINERY_UNINFORMATIVE iff PC calibration fails.

perm_p = frac(null CV <= obs CV), small => constrained. Seed fixed.

## Positive Control (synthetic, gates verdict)
(a) DETECT: ~140 synthetic docs with FIXED target extent (extent ~ E0 + small noise, independent of count); confirm perm_p <= 0.05 over >=15 reps (power_est).
(b) FALSE-POSITIVE: ~140 docs whose extent IS random assembly (sum of pooled widths+gaps at random count); confirm fire-rate <= 0.10 over >=15 reps.
Fail either -> MACHINERY_UNINFORMATIVE.

## Honest caveat (to be reported verbatim in spirit)
A constrained extent may reflect the TABLET dimension OR a scribal writing-area convention. Report the finding as "writing extent is constrained", NOT "scribes deliberately targeted a width".

## Layer / scope
L2; opaque IDs; positions/widths only; no values; la_touched=true; non-circular (geometry-only, no semantic labels).
