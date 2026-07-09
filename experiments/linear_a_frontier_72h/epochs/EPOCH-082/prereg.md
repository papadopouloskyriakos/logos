# EPOCH-082 PREREGISTRATION — Linear A frontier-72h

## Task
EPOCH-082: Is the 2D-ruled-grid finding (E079 horizontal glyph spacing regular; E080 vertical line spacing
regular) ROBUST to the row-detection method? HARDENING / robustness epoch for E079 + E080.

## Layer / discipline
- Layer: L2 (geometry only, opaque IDs, positions only, NO value/reading).
- Operator: logos z.ai research worker (GLM-5.2). Proposer/operator, never adjudicator.
- Verdict: MECHANICAL, from a FROZEN rule (invariant #3 — robustness to method choice).

## Background (prior epochs, frozen findings)
- E079: horizontal glyph spacing regular. Median doc h-pitch-CV = 0.329 vs random-composition null 0.743,
  perm p = 0.
- E080: vertical line spacing regular. v-line-CV = 0.118 vs clustering-conditional null 0.354, perm p = 0.
- BOTH define "rows" via the SAME greedy y-band clustering at tol = 0.6 x median-glyph-height. That 0.6 is
  arbitrary. This epoch sweeps the threshold and adds an independent alt method.

## Data
- Source: experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json
- Each doc: glyphs[{sign, bbox:[x,y,w,h], is_divider}].
- EXCLUDE is_divider glyphs. Use docs with >=6 non-divider bbox glyphs.
- Sites with >=15 usable docs (frozen): Haghia Triada, Khania, Zakros.

## Row-detection settings (FROZEN, 4)
1. tol = 0.5 x median-glyph-height (greedy y-band clustering).
2. tol = 0.6 x median-glyph-height (CANONICAL — matches E079/E080).
3. tol = 0.7 x median-glyph-height (greedy y-band clustering).
4. ALT relative-gap splitter (independent method: tol = 1.5 x median consecutive-y-gap).

CORE = all 4 settings must hold for ROBUST.

## Metrics (reused VERBATIM from E079/E080, no re-derivation)
- h_pitch_cv(rows): per-doc CV of within-row horizontal pitches (rows with >=3 glyphs).
- v_line_cv(rows): per-doc CV of consecutive row-center y-spacings (>=3 rows).
- S_h / S_v: median over docs of h_pitch_cv / v_line_cv (corpus statistic).
- Nulls (VERBATIM):
  - E079 null_h_doc: random-composition (uniform breakpoints) of each row's observed pitches.
  - E080 null_v_doc: clustering-conditional random row-allocation via rand_comp_above (floor = merge tol).
- perm_p: 500 permutation draws, median over docs, p = (#{null <= obs}+1)/(ndraw+1).
- Regular direction: obs << null (smaller CV = more regular).

## Positive control (synthetic, calibration)
- DETECT arm (~40 docs): regular grid — evenly spaced rows (pitch ~10, jitter 5%) each with evenly spaced
  glyphs (pitch ~6, jitter 5%). Confirm BOTH S_h and S_v flag regular (perm_p <= 0.05) under tol=0.6 AND alt.
  power_est over >=15 reps.
- FALSE-POSITIVE arm (~40 docs): random placement — rows at random y via rand_comp of a column span; glyphs
  at random x via rand_comp of a row span (keep each row left-to-right). Confirm NEITHER metric flags regular
  (rate <= 0.10).
- If PC fails under tol=0.6 OR alt -> MACHINERY_UNINFORMATIVE.

## FROZEN VERDICT RULE (mechanical)
- GRID_REGULARITY_ROBUST_TO_ROW_DETECTION iff:
  PC passed AND global S_h and S_v both significant (perm_p <= 0.05, regular direction obs << null) at ALL 4
  settings AND each metric retains >=2/3 sites significant at tol=0.6.
- GRID_REGULARITY_PARTIALLY_SENSITIVE iff robust for at least one metric across all 4 but the other metric
  (or a site leg) loses significance at some setting (name which).
- GRID_REGULARITY_THRESHOLD_SENSITIVE iff either metric loses global significance / flips direction at any of
  the 4 settings.
- MACHINERY_UNINFORMATIVE iff PC calibration fails.

## Outputs
- result.json at PATH CONTRACT path.
- EPOCH082_REPORT.md at PATH CONTRACT path.
- Opaque IDs only; geometry only; no value/reading.
