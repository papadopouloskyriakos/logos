# E204R quality report — GATE FAILED on one criterion (E204R_BLOCKED_DATA_QUALITY)

1392 aligned pairs (only-C 40, only-D 36). Post-R2 measurements vs the frozen conjunctive gate:
- overall 0.9972 ≥ .98 ✓ · **statement 0.9763 < .98 ✗ (33 rows)** · fraction 1.000 ✓ ·
  classification 1.000 ✓ · flags 1.000 ✓ · full-record 0.9756 ≥ .95 ✓ · multi-fraction docs
  72 ≥ 30 ✓ · arithmetic-complete 23 ≥ 10 ✓ · decimal contamination 0 ✓ · rare signs all
  perfect (L 4/4, H 15/15, F 14/14, W 5/5, X 3/3, Y 1/1) ✓ · duplicates logged (7+7) ✓.
- doc_id / locus / integer: 1.000 — **the numeric apparatus is at complete dual-parse
  agreement** (326 fraction records, 72 multi-fraction docs, 23 arithmetic-complete docs).

The 33 residual statement disagreements (statement_residuals.json) fall in two named classes:
(a) damaged-initial hyphen semantics ("-DI-NA" vs "DI-NA": whether the initial hyphen marking a
lost sign is statement content); (b) unterminated numeric entities ("&#149" without ';'), which
stdlib decoding accepts and the independent decoder leaves literal. Amendment R2 pre-committed
that post-R2 residuals are a REPRESENTATION RESULT, not grounds for further parser rewriting.

**Verdict: E204R_BLOCKED_DATA_QUALITY** (gate conjunctive; not moved). E204 metrology does NOT
run. The fraction seal remains unopened and unread. Unblock for a future preregistered pass:
freeze the two residual-class semantics (damaged-initial hyphen; unterminated entities) in a
revised spec and re-gate — 33 rows are also individually listed for scholarly adjudication.
