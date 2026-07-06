# Annotation guidelines — DRAFT (NOT FROZEN / NOT COMMITTED)

## Principle

Annotate the **role/relation ground truth** from the standard deciphered Linear B literature (EVALUATION
layer). Annotators MAY use transliteration, lemma, Greek, and glosses — these are ground-truth sources and
live in the evaluation layer. The **model** never sees them; annotations do.

## Per-token procedure

1. Identify the token (word-form / logogram / numeral / …) by its `token_or_form_id` in the Stage-4 graph.
2. Assign **TOKEN_ROLE** (coarse first, then fine if secure) — the token's entity class.
3. Assign **ENTRY_RELATION** independently — its contextual admin relation (DESTINATION, RECIPIENT, …), or
   NONE. Do **not** collapse role and relation.
4. Assign **DOCUMENT_SCHEMA** (once per document) and **TRANSACTION_TYPE** (per entry) where determinable.
5. Set `gold_tier` per `gold_tier_rules_draft.md`; record `confidence`, `source_citation`,
   `annotation_rationale`.
6. If scholarship is divided: record ALL plausible labels in `alternative_labels`, set `dispute_flag`, tier
   GOLD_B/GOLD_C — never force one label.

## Calibration examples (illustrative)

- word-form immediately before `LOGOGRAM + NUMERAL` and recurring across sites → often
  HUMAN_OR_INSTITUTION (recipient) or PLACE (destination) — decide by recurrence + destination structure,
  cite source.
- `to-so` / totalling form at document end → DOCUMENT_STRUCTURE / TOTAL_OR_SUBTOTAL (structural, GOLD_A).
- logogram → COMMODITY_OR_CATEGORY (structural control, not gate-load-bearing).

## Do NOT

Do not assign roles from sign shape alone; do not let damage force a confident label; do not annotate the
opaque model-visible IDs (annotate the underlying evaluation-layer token); do not produce Linear A
annotations (out of scope for this programme).
