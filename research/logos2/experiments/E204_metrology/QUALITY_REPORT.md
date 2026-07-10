# E204 dual-parser quality report — GATE FAILED (E204_BLOCKED_DATA_QUALITY)

Aligned pairs 782 (keys only-A 316, only-B 461). Frozen gate: overall field agreement >=98%.
**Measured: 86.2% raw / 86.3% post-adjudication -> FAIL.** No seal opened; no enumeration run.

Passing criteria (for the record): multi-fraction docs 39>=30 OK; arithmetic-complete 12>=10 OK;
decimal-gloss contamination 0 OK; within-parser duplicates 0 OK; rare-sign agreement K 11/11,
F 7/7, H 8/8, X 1/1, Y 1/1; L 3/4 and W 3/4 unresolved (small-n, logged).

Failure localization (the useful engineering fact):
- **context_word agreement 27.4%** even under comparison-normalization (space/hyphen/subscript
  unification): the two parsers extract genuinely different statement fields — Parser A's
  whitespace tokenizer over the wrap-mangled .txt fragments statements differently than
  Parser B's author-table cells. This channel feeds commodity/word association; unreliable.
- integer 95.0% (5 subscript reattachments adjudicated by rule I1), fraction_seq 97.6%,
  flags 98-99.9%, fraction-vs-integer classification 98.2% — the NUMERIC core is close to
  gate quality; the STATEMENT channel is not.
- Coverage asymmetry (316/461 unmatched keys) driven by locus-notation variants between
  renderings; uncharacterized remainder logged for the next pass.

Preserved: parser_a_output.csv, parser_b_output.csv (+ the invalid B-R0), quality_comparison
.json, adjudication_log.json, FRACTION_APPARATUS.csv (212 fully-agreed records — NOT gate-
qualified; usable only as a conservative descriptive subset, never for arithmetic constraints).

Unblock path (specific): redesign BOTH parsers' statement-field extraction against the author's
column semantics (A must reconstruct the statement column from the .txt layout; the .txt
rendering wraps table columns unpredictably — consider A' = a second, independent TABLE parser
over the HTML with different cell-walk logic), then rerun this gate unchanged.
