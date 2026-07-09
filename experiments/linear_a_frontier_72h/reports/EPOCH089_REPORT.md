# EPOCH-089 REPORT — Header writing WIDTH constrained?

**Task:** Is the header row's writing width (x-extent) constrained, explaining E087's heading-size ↔ header-length tradeoff (Spearman -0.189)? E088 REJECTED a fixed INK (area) budget; this epoch tests the better-motivated alternative: a fixed WRITING WIDTH.

**Layer:** L2 (geometry only, opaque IDs, positions/widths only, no values). **la_touched:** true.

## Verdict (FROZEN, mechanical)

**HEADER_WIDTH_CONSTRAINED**

PC PASSED (detect power_est=1.00, false-positive rate=0.100 ≤ 0.10) AND perm_p = 0.00050 ≤ 0.05.

## Numbers

| quantity | value |
|---|---|
| obs first-row x-extent CV | **0.4065** |
| assembly-null median CV | 0.5445 |
| ratio (obs/null) | 0.747 |
| **perm_p** | **0.00050** |
| n_docs (HT, ≥6 non-divider bbox glyphs, ≥2 rows) | 140 |
| extent / doc-x-extent (median) | **0.842** (~84% of document width) |
| pool sizes | 628 first-row widths, 488 inter-glyph gaps |
| count range (first row) | 1–16, median 4 |

## Positive control (synthetic, gates verdict) — PASSED
- **DETECT** (fixed target extent, independent of count): detect_p=0.0005, power_est=**1.00** over 30 reps.
- **FALSE-POSITIVE** (extent = random assembly at random count): fire-rate=**0.100** (≤0.10 gate; stable 0.067–0.100 across seeds 111/222/333/909090).

## Method
S_obs = CV (pstdev/mean) of first-row X-EXTENT (max glyph right − min glyph left) across HT docs. NULL: pool all first-row glyph WIDTHS and inter-glyph GAPS; for each doc rebuild synthetic extent = Σ(count random widths) + Σ((count−1) random gaps) at the doc's actual count; recompute CV; 2000 draws. perm_p = frac(null CV ≤ obs CV). Width-constrained ⟺ obs CV significantly BELOW null.

## Key findings
1. The real header writing extent (CV=0.41) is significantly more constant than random width+gap assembly (null median CV=0.54), perm_p=0.0005 — the extent is regularized.
2. The header occupies ~84% of the document writing width (near-full-width), consistent with a bounded writing area (E086).
3. PC confirms the machinery both detects a true fixed extent (power 1.0) and does not fire on random assembly (fire-rate ≤0.10).

## Honest bottom line
A bounded writing WIDTH explains E087's heading-size ↔ header-length tradeoff where the ink/area budget (E088) did not: within a near-fixed horizontal extent, bigger first-row glyphs mechanically leave room for fewer. **Caveat:** a constrained extent may reflect the physical TABLET dimension OR a scribal writing-area convention — the finding is "writing extent is constrained", NOT "scribes deliberately targeted a width". Resolving tablet-vs-convention is left to E090 (support-width comparison).

## Successor hypotheses
- E090: scale of constrained extent vs TABLET support width (Tablet vs other supports) — tablet-dimension vs convention.
- E091: is per-glyph width the free variable (count×width ≈ const) or is count fixed?
- E092: does the width constraint hold for body rows, or is it header-specific?
- E093: predict header count from (target_extent / mean_glyph_width); test residuals.
- E094: do inter-glyph gaps shrink as count rises (compression to fit)?
- E095: cross-site replication on non-HT Linear A.

## Deviations
- Doc x-extent computed from all non-divider glyph bboxes (no doc-level width field in source JSON); used for the extent/doc ratio only, not the verdict metric.
- PC used 30 reps/arm (protocol floor ≥15) for a stable fire-rate; independent RNG seeds per PC arm to avoid cross-arm RNG-state coupling (math unchanged).
