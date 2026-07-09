# EPOCH-090 — Coordinator note: PC adjudication (anti-conservative difference-CI) + robust DOC_WIDE via reconstruction

**Verdict banked:** `WIDTH_CONSTRAINT_DOC_WIDE` — but the epoch's stated positive control is MISCALIBRATED, and the
DOC_WIDE conclusion is banked on the coordinator's independent reconstruction, NOT on the worker's PC. This is an
E080-style adjudication (the worker's statistical construction had a flaw; the coordinator reconstructs the correct
analysis; the conclusion stands).

## What the worker reported
Verdict DOC_WIDE (ratio_header 0.747, ratio_body 0.755, D_obs −0.008, row-resampled bootstrap 95% CI
[−0.124, +0.110] includes 0), PC `false_pos_rate: 0.0`, `detect_power: 1.0`, gate `passed:true, repairs:0`.

## The problem the coordinator found (independent PC reconstruction)
The epoch's difference statistic D = ratio_header − ratio_body is tested with a bootstrap that resamples ROWS
independently while holding the two assembly-null medians FIXED. The coordinator reconstructed the PC with a
GENUINELY-equal no-FP arm (header and body rows drawn from the SAME distribution): the 95% CI EXCLUDES 0 in
**24/40 = 0.60** of cases (worker reported 0.0). The row-resampling bootstrap is **anti-conservative** — it ignores
(a) within-doc row clustering and (b) uncertainty in the null medians, so the CI is too narrow and over-excludes 0.
The worker's `false_pos_rate: 0.0` came from a no-FP synthetic that (like the coordinator's first crude attempt) did
not actually impose equal ratios, so it never exercised the anti-conservatism.

## Why DOC_WIDE nonetheless stands (coordinator reconstruction)
DOC_WIDE does NOT depend on the miscalibrated difference-CI:
1. **Near-identical individual ratios.** ratio_header = 0.747 and ratio_body = 0.757 — both groups are ~25% more
   width-regular than random assembly, to the same degree. Each ratio is individually significant vs its own
   assembly null (header p=0.0005 in E089; body p=0.001 in the coordinator pre-check). Both rows are equally
   constrained; the header is not special.
2. **Anti-conservative test still includes 0.** A difference-test biased TOWARD excluding 0 (toward HEADER_SPECIFIC)
   nevertheless returns D≈0 with a CI including 0 → strong evidence FOR equality (DOC_WIDE). An anti-conservative
   test failing to find a difference is conservative for the null.
3. **Proper doc-level clustered bootstrap.** Resampling DOCS (preserving within-doc clustering) gives D_obs=−0.010,
   95% CI **[−0.102, +0.088]**, which INCLUDES 0. DOC_WIDE holds under the correct (clustered) resampling.

## Consequence for the record
- The FINDING (E089's width constraint is DOC-WIDE, not header-specific) is banked as robust and correctly qualifies
  E089. E089's own verdict (HEADER_WIDTH_CONSTRAINED) STANDS but its *scope* is refined: the bounded writing width
  is a whole-document property (all rows fit the writing area), not a header design feature. Append-only (Art. XVII):
  E089's ledger entry is unchanged.
- The epoch's difference-CI MACHINERY is flagged as anti-conservative; future difference-of-ratio tests must use a
  DOC-LEVEL bootstrap with nulls recomputed per resample (or a permutation of row-position labels), not row-level
  resampling with fixed nulls. This is the third PC-calibration lesson (E080 conditional null, E082 uncalibratable
  metric, E090 anti-conservative bootstrap).
- This is NOT a MACHINERY_UNINFORMATIVE case (contrast E082): unlike E082, the target conclusion (DOC_WIDE) is
  supported by calibration-INDEPENDENT facts (the near-identical individual ratios), so a definite, honest verdict
  is available — it is just not the worker's PC that certifies it.
