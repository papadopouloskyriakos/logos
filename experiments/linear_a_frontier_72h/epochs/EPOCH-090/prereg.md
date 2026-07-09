# EPOCH-090 PREREGISTRATION (FROZEN)

## Task
Is E089's header width-constraint HEADER-SPECIFIC or DOC-WIDE? (spatial confound-check; L2; within-HT).

E089 found the first (header) row's x-extent is width-CONSTRAINED (CV below an assembly null).
CONFOUND: if ALL rows fit the same bounded writing width, then E089 is a whole-document property
(rows fit the page), NOT a header design feature.

## Design (opaque IDs, positions/widths only, no values)
- Population: Haghia Triada docs with >=6 non-divider bbox glyphs AND >=2 rows.
- Header row = first (top) row of each doc. Body rows = all rows after the first.
- For each group (header, body) separately:
  - ratio = CV(row x-extent) / (median assembly-null CV)
  - assembly null rebuilds each row's extent from that group's pooled glyph WIDTHS + inter-glyph
    GAPS at the row's actual count (1000 draws).
- D = ratio_header - ratio_body.
- Bootstrap 95% CI of D: resample docs with replacement, recompute observed CVs; keep the two
  assembly-null medians FIXED from full data. 2000 resamples.

## Verdict (FROZEN, mechanical)
- WIDTH_CONSTRAINT_DOC_WIDE iff PC passed AND bootstrap 95% CI of D INCLUDES 0
  (header not more constrained than body -> E089's width constraint is whole-document, not header-specific).
- WIDTH_CONSTRAINT_HEADER_SPECIFIC iff PC passed AND CI EXCLUDES 0 AND D<0
  (header ratio significantly lower -> header specifically more width-constrained).
- WIDTH_CONSTRAINT_DIFF_UNDERPOWERED iff <60 header rows OR <60 body rows OR PC power<0.5.
- MACHINERY_UNINFORMATIVE iff PC calibration fails.

## Positive Control (synthetic, gates verdict)
- (a) DETECT: ~140 synthetic docs, header rows FIXED extent (constrained), body rows random-assembly (free).
  Confirm D_obs significantly <0 with CI excluding 0; power_est over >=15 reps.
- (b) FALSE-POSITIVE: docs where header AND body rows BOTH constrained to same degree.
  Confirm CI INCLUDES 0; fire-rate <=0.10 over >=15 reps.
- If can't DETECT header-specific constraint OR fires on equal-constraint docs -> MACHINERY_UNINFORMATIVE.

## Layer / Scope
- Layer: L2 (geometry only, opaque IDs, positions/widths only, no values).
- la_touched: true (reads Linear A glyph bboxes).
- non_circular: uses only spatial geometry (bbox positions/widths); no semantic/phonetic values;
  no reuse of E089 outputs as inputs.

## Seed
Fixed seed (90210) for reproducibility.
