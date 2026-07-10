# E204R2 — residual canonicalization (separately preregistered; one pass)

**Relation:** E204 and E204R keep their verdicts and artifacts. E204R2 exists because the E204R
residual is restricted to 33 named rows in exactly two SOURCE-REPRESENTATION classes,
independent of the fraction-value hypotheses and of the already-perfect numeric agreement.
This is source canonicalization, NOT threshold movement: every E204R gate threshold is
retained unchanged.

## Frozen canonicalization rules (both parsers implement INDEPENDENTLY)

- **RC1 damaged-initial hyphen:** when a statement cell's text (after markup stripping) begins
  with a hyphen, that hyphen is EPIGRAPHIC (continuation from a lost/damaged sign): the
  canonical statement RETAINS exactly one leading "-", and the record's damaged flag is set
  to 1. Interior hyphen normalization is unchanged.
- **RC2 unterminated numeric entities:** an ampersand + '#' + 2-4 digits NOT followed by ';'
  decodes identically to its terminated form (numeric refs 149/183/8226 → "•", which then
  falls under the R2 bullet-punctuation rule and is stripped from statement/logogram fields).
- **RC3 genuinely malformed remainder:** a row that resists both rules is emitted with
  statement field verbatim + an `anomaly=1` flag; anomalous rows count as disagreements if
  the parsers differ (no silent exclusion).

## Freeze artifacts (committed BEFORE either parser runs)
- `residual_rows_frozen.json` — the 33 rows + sha256 (from statement_residuals.json @ 0600a5c).
- Canonical-source hashes: unchanged RAW_SOURCE_MANIFEST (E204R copy).
- Parser C2 spec: C-lineage tree parser + RC1-RC3 implemented in C2's own code; no D-lineage code.
- Parser D2 spec: D-lineage streaming FSM + RC1-RC3 implemented in D2's own code; no C-lineage code.
- Shared: raw sources, output schema, these semantic rules, non-answer-bearing fixtures only.

## Gate (identical to E204R; conjunctive; ONE pass)
overall ≥98% · statement ≥98% · fraction ≥98% · classification ≥98% · flags ≥98% ·
full-record ≥95% · ≥30 multi-fraction docs · ≥10 arithmetic-complete docs · 0 decimal
contamination · 0 duplicate inflation · no unresolved systematic rare-sign disagreement · no
proposed values in arithmetic-completeness. Reported per-field/per-sign/per-document as before.

Results: `E204R2_QUALITY_GATE_PASSED` | `E204R2_BLOCKED_DATA_QUALITY` | `E204R2_INVALID`.
Failure ⇒ preserved as-is; **no E204R3 is created automatically.** Pass ⇒ canonical dataset
frozen; E204 metrology proceeds under its own §4 stack freeze. The fraction seal remains
unopened either way (registered opening event has not occurred; E204R2 is not a substitute).
Implementation defects (crash/hang class): as-run preserved + committed amendment; residual
source ambiguity = a disagreement, not a defect.
