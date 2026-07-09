# EPOCH-084 REPORT — Is E080's vertical line-spacing regularity DELIBERATE, or a line-HEIGHT artifact?

**Layer:** L2 (geometry-only, opaque IDs, positions/heights only)
**Verdict:** `LINE_SPACING_DELIBERATE_CROSS_SITE`
**Tests/Confirms:** E080 (vertical row-to-row pitch regularity)
**Symmetric partner of:** E083 (horizontal WIDTH-DRIVEN finding)

## Question
E080 found vertical row-to-row PITCH is regular. But line-pitch = inter-line GAP + row HEIGHT, and
glyph/row heights are fairly uniform, so uniform heights alone regularize line-pitch even with random
gaps. E084 runs the vertical analog of E083 with a HEIGHT-PRESERVING random-gap null: keep each row's
height and the column span, randomize ONLY the inter-line gaps; recompute line-pitch-CV. If observed
line-pitch-CV << null, the GAPS carry deliberate regularity (real deliberate line spacing) → CONFIRMS
E080. If observed ≥ null, the regularity is HEIGHT-driven → qualifies E080 (as E083 did E079).

## Method
- Data: `experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json`. Exclude `is_divider`. Docs with
  ≥6 non-divider bbox glyphs AND ≥3 rows. Sites with ≥15 usable docs: Haghia Triada (121), Khania (25),
  Zakros (21).
- Observed: per-doc line-pitch-CV (CV of consecutive row-center differences); S_obs = median across docs.
- Null (height-preserving random-gap): keep row heights + span, randomize ONLY inter-line gaps;
  null_median = median across docs over 500 draws.
- Deliberate = observed line-pitch-CV significantly BELOW null (perm_p ≤ 0.05).
- Positive control: (a) DETECT — 40 synthetic docs, EQUAL gaps + variable heights Uniform[6,12];
  (b) FALSE-POSITIVE — 40 docs, RANDOM gaps + same heights. 15 reps each.

## Results

### Global (n_docs = 193)
| metric | value |
|---|---|
| S_obs (observed line-pitch-CV) | **0.1105** |
| null_median (height-preserving) | **0.1603** |
| perm_p | **0.0020** |
| ratio (S_obs / null) | **0.690** |

Observed line-pitch-CV is **31% below** the height-preserving random-gap null → the inter-line GAPS
themselves carry regularity beyond what uniform row heights alone would produce.

### Per-site
| site | n_docs | S_obs | null_median | perm_p | deliberate |
|---|---|---|---|---|---|
| Haghia Triada | 121 | 0.1193 | 0.1732 | 0.0020 | **YES** |
| Khania | 25 | 0.1105 | 0.1304 | 0.1816 | no |
| Zakros | 21 | 0.1081 | 0.1425 | 0.0319 | **YES** |

2/3 usable sites significant → CROSS_SITE.

### Positive Control
| metric | value |
|---|---|
| pc_verdict | **PASSED** |
| detect_p (median) | 0.0020 |
| power_est | 1.00 |
| false_pos_rate | 0.067 (≤ 0.10 gate) |

Machinery detects deliberate equal-gap spacing with full power and does not fire on height-only-random
gaps above the 0.10 false-positive gate.

## Verdict logic
PC PASSED ∧ global perm_p=0.0020 ≤ 0.05 ∧ 2/3 sites significant → **LINE_SPACING_DELIBERATE_CROSS_SITE**.

## Bottom line
E080's vertical line-spacing regularity is **DELIBERATE** — it survives a height-preserving random-gap
null, meaning the observed gap arrangement yields lower line-pitch-CV than random gaps would under preserved row heights (observed 0.1105 vs null 0.1603); this indicates the gap arrangement is non-random with respect to pitch regularity, not that the gaps are independently uniform or that gaps additively 'contribute' a separable regularity component. This is the
**opposite** of E083's horizontal finding (where E079's pitch-regularity was WIDTH-DRIVEN and dissolved
under a width-preserving null). The Linear A scribes controlled vertical line spacing deliberately
(cross-site, strongest at Haghia Triada and Zakros) while horizontal column spacing appears to be a
by-product of glyph-width uniformity. The vertical/horizontal asymmetry is itself a finding worth
follow-up (E086).

## Non-circularity
Opaque IDs; geometry only (positions, heights); the null preserves the very feature (row heights) that
could spuriously regularize pitch, so any deliberate signal must come from the gaps themselves. No
semantic/phonetic content used.

## Successor hypotheses
- E085: test whether inter-line gaps follow a fixed module (integer multiple of a base unit) cross-site.
- E086: contrast vertical (E084 deliberate) vs horizontal (E083 width-driven) spacing within the same docs.
- E087: test correlation of deliberate line-spacing with support type / period.
- E088: decompose pitch variance into height-variance vs gap-variance contributions per site.
- E089: test whether row-height uniformity itself is deliberate (row-height-CV vs glyph-height null).

## Deviations
None. (PC ndraw set to 500 to match the main permutation draw count for calibration stability; this is
consistent with the protocol's 500-draw specification.)
