# E204R — canonical-table extraction repair (separately preregistered remediation)

**Relation to E204:** the failed run KEEPS its verdict `E204_BLOCKED_DATA_QUALITY` and all its
artifacts; E204R is a new remediation experiment, not a relabel. **Frozen before execution.**

## Canonical source (frozen)

The Younger HTML files ONLY (HTtexts.html, misctexts.html, religioustexts.html; sha256 in
`RAW_SOURCE_MANIFEST.sha256`, identical to the E204 register): their `<TR>/<TD>` tables encode
the author's own record structure (locus | statement | logogram | number | fraction, per his
printed column headers). The .txt renderings are NOT sources here (their wrapping caused the
E204 statement-field failure).

## Frozen semantic specification (both parsers implement INDEPENDENTLY; no shared code)

- **Row selection:** a record row = a table row whose FIRST non-empty cell is a locus token
  (side.line shapes: optional a/b(+roman), dot, digits, optional -digits; or side./edge./lat.).
  Header rows ("side.line statement …"), separator rows, and rows outside a document scope are
  not records.
- **Document scope:** opens when inter-table/inter-row text contains a site-prefix token
  (frozen prefix table = SCHEMA.json of E204) + designation number, with a support keyword
  within 12 tokens; scope persists until the next document opens.
- **Cell text extraction:** inline tags (b, i, u, font, span, sub, sup) are TRANSPARENT;
  `<sub>n</sub>` and `<sup>n</sup>` render as the digit appended directly to the preceding
  token (subscript signs: PA<sub>3</sub> → "PA3"); entities decoded per the frozen map
  (&amp; &lt; &gt; &nbsp; &bull; &#8226; &quot;); all whitespace runs collapse to single
  spaces; leading/trailing space stripped.
- **Field mapping:** cells after the locus cell are classified per cell content: a cell whose
  tokens are all integers (1-4 digits) → integer zone; all fraction letters (frozen alphabet
  J E F K L B H D W X Y, tokens ≤2 chars) → fraction zone; else content cell. First content
  cell = statement; remaining content cells joined = logogram field. Statement normalization
  for OUTPUT: hyphen-join collapse ("PA - DE" → "PA-DE"), single spaces.
- **Flags:** '?' anywhere in row → uncertain=1; '[' or ']' → restored=1; '…'/'vest.' →
  damaged=1; sigla {…} kept in logogram field.
- **Continuation:** a following row whose only non-empty cells are fraction letters continues
  the previous record's fraction zone.
- **Duplicates:** same (doc_id, locus, statement, integer, fraction) seen twice in one file →
  one record + duplicate log entry; across files, precedence HTtexts > misctexts >
  religioustexts.
- **Exclusions:** unchanged from E204 EXCLUSION_RULES.md (decimal glosses = whole-row
  exclusion; prose rows; no-locus rows). NO arithmetic inference; NO value assignment.
- **Arithmetic-complete (data-side only, no proposed values):** a document with ≥2 unflagged
  integer-bearing entry records + an unflagged KU-RO record.

## Parsers (genuinely independent)

- **Parser C** — tree-based: python stdlib `html.parser.HTMLParser` subclass building an
  explicit element tree; table walk over the tree. Own entity/subscript/whitespace code.
- **Parser D** — streaming character/state-machine scanner: single pass, explicit states
  (TEXT/TAG/CELL/ROW), own tag-name reader, own entity decoder, own whitespace collapse; no
  tree is built; rows emitted as they close. No regexes for record assembly.
- Shared: raw files, this specification, SCHEMA fields, and regression FIXTURES (the 212
  E204-agreed records may be used ONLY as regression fixtures — they do not define
  adjudication and do not replace full-corpus evaluation).

## Frozen quality gate (at least as strict as E204's; per-field, no weighted hiding)

overall ≥98% AND statement ≥98% AND fraction-sequence ≥98% AND fraction/integer
classification ≥98% AND uncertainty/restoration ≥98% AND ≥30 multi-fraction documents AND
≥10 arithmetic-complete documents AND zero decimal contamination AND zero duplicate inflation
AND no unresolved systematic rare-sign disagreement. Additionally (stricter, justified by the
shared canonical source): **full-record exact agreement ≥95%.** Reported: structural row
identity, per-field, per-sign, per-document, rare-sign, duplicates.

Failure ⇒ `E204R_BLOCKED_DATA_QUALITY`, outputs preserved, gate NOT moved, no parser-rewriting
loop (an implementation defect needs an amendment; a representation disagreement is a result).
Pass ⇒ freeze adjudicated dataset; E204 metrology proceeds under its own §8 stack freeze.
The fraction seal stays unopened regardless (its registered event has not occurred; E204R
completion is NOT a substitute).
