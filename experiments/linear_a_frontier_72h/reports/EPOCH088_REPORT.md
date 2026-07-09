# EPOCH-088 REPORT — Is E087's heading-size <-> header-length tradeoff a fixed ink budget?

**Campaign:** Linear A frontier-72h  |  **Layer:** L2 (opaque IDs, geometry only)  |  **la_touched:** true
**Population:** Haghia Triada docs with >=6 non-divider bbox glyphs AND >=2 detected rows. **n = 140.**

## Question
E087 found a heading-size <-> header-length tradeoff (Spearman -0.189) at Haghia Triada:
docs whose first row has larger glyphs have shorter first rows. Is this the byproduct of a
**fixed first-row ink budget** (scribes allocate a roughly constant total glyph-area to the
header row), or merely a **soft tendency**?

## Test
- Per doc: first-row total ink = sum of glyph areas; first_count; first_med_area.
- S_obs = CV (pstdev/mean) of first-row total ink across docs.
- NULL (tradeoff broken): independent random median-area * independent random count;
  recompute CV; 2000 draws. perm_p = (#{null CV <= obs CV} + 1) / 2001.
- Budget holds iff obs CV significantly BELOW null (perm_p <= 0.05).

## Positive control (synthetic, gates verdict) — PASSED
- DETECT arm (fixed-budget docs): power_est = **1.0**, median detect perm_p = 0.0005.
- FALSE-POSITIVE arm (independent size*count): fire-rate = **0.0**.
- Machinery is calibrated and informative.

## Result
| metric | value |
|---|---|
| obs CV (first-row total ink) | **0.639** |
| null median CV (independent size*count) | **0.714** |
| ratio (obs / null) | 0.896 |
| perm_p | **0.145** |
| n_docs | 140 |

## Verdict (frozen rule)
**HEADER_INK_NOT_BUDGETED** — PC passed AND perm_p = 0.145 > 0.05.

## Bottom line
The observed first-row total ink (CV 0.639) is only marginally more concentrated than the
independence null (0.714) and is **not** significantly below it. A fixed first-row ink
budget is rejected. **E087's heading-size <-> header-length tradeoff is a SOFT tendency,
not the byproduct of a fixed header ink budget** — total header ink varies freely across HT
documents. This is a full, expected result (matches the coordinator pre-check) and closes
the mechanism question honestly: the tradeoff must arise from some other constraint
(line-width, glyph-height preference, scribal habit) rather than a constant area budget.

## Discipline notes
- L2: opaque doc IDs; only bbox areas and counts used; no sign values.
- Non-circular: does not consume E087's correlation as evidence; tests a mechanism on raw
  geometry. Verdict produced mechanically by the frozen rule.
- Deviation: data file resolved to `experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json`
  (the `BASE/data/` path in the brief did not exist); same corpus.
