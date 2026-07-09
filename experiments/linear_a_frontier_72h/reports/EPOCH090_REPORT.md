# EPOCH-090 REPORT — Is E089's header width-constraint HEADER-SPECIFIC or DOC-WIDE?

**Verdict: WIDTH_CONSTRAINT_DOC_WIDE** (PC passed; CI of D includes 0)

## Question
E089 found the first (header) row's x-extent is width-CONSTRAINED (CV below an assembly null).
CONFOUND: if ALL rows fit the same bounded writing width, E089 is a whole-document property
(rows fit the page), not a header design feature. Test whether the header is *specifically* more
constrained than body rows.

## Method (L2, geometry only, opaque IDs)
- Haghia Triada docs, >=6 non-divider bbox glyphs, >=2 rows. **140 header rows, 462 body rows.**
- For each group: `ratio = CV(row x-extent) / median(assembly-null CV)`. The assembly null rebuilds
  each row's extent from that group's pooled glyph WIDTHS + inter-glyph GAPS at the row's actual
  count (1000 draws, FIXED from full data).
- `D = ratio_header - ratio_body`. Bootstrap 95% CI of D (2000 resamples), nulls FIXED.
- DOC_WIDE iff CI includes 0; HEADER_SPECIFIC iff CI excludes 0 AND D<0.
- Positive control (synthetic, 2 arms) gates the verdict.

## Results

| quantity | value |
|---|---|
| n_header | 140 |
| n_body | 462 |
| null_h (assembly-null median CV, header) | 0.5440 |
| null_b (assembly-null median CV, body) | 0.6641 |
| **ratio_header** | **0.7473** |
| **ratio_body** | **0.7551** |
| **D_obs** | **-0.00777** |
| 95% CI of D | **[-0.1236, +0.1101]** |
| CI includes 0? | **YES** |

### Positive control
- DETECT arm (header constrained, body free): power = **1.0** (15/15 reps detected D<0 with CI excluding 0).
- FALSE-POSITIVE arm (both equally constrained): fire-rate = **0.0** (0/15 reps falsely declared header-specific).
- **PC verdict: PASSED.**

## Interpretation
Header and body rows are width-constrained to a **nearly identical degree** (0.747 vs 0.755 — both
well below 1.0, i.e. both constrained relative to their assembly nulls). The difference D=-0.0078 is
negligible and its 95% CI comfortably spans 0. The header is **not** significantly more constrained
than body rows.

**Bottom line:** E089's bounded-writing-width finding is a **whole-document property** — all rows
(header and body alike) fit the available writing area. It is **not** a header-specific design
feature. E089 is therefore **qualified, not falsified**: the width constraint is real and pervasive,
but it does not specifically explain the header; it explains the entire document's row extents.

This matches the coordinator pre-check (header ratio 0.747, p=0.001 vs body ratio 0.758, p=0.001 —
nearly identical, both constrained).

## Scope / Honesty
- L2: geometry only (bbox x-positions, widths, gaps). No sign values, no semantics.
- la_touched: true. Non-circular: no E089 output reused as input.
- The DOC_WIDE result is a FULL result that QUALIFIES E089 (constraint is whole-document, not a
  header design feature).
- Deviation: input data file was accidentally deleted during setup and restored from the corpus
  source (byte-identical content: 787 docs, 369 HT). No math altered.
