> **DRAFT — NOT FROZEN · DRAFT — NOT USED FOR MODELING · DRAFT — NOT COMMITTED**
> Stage 5 review package. No final gold labels, splits, firewall, or models exist. Awaiting
> `STAGE5_ONTOLOGY_APPROVED` before anything here is frozen or committed.

# Ontology & Annotation Review Packet (Stage 5)

## 1. Coarse ontology (the transfer-gate load-bearer) — revised per §IX

8 classes, structurally inducible and Linear-A-representable:

```
HUMAN_OR_INSTITUTION   PLACE   COMMODITY_OR_COUNTED_CATEGORY   MEASURE_OR_QUANTITY
OPERATOR_OR_RELATION   QUALIFIER   DOCUMENT_STRUCTURE   UNKNOWN
```
(revised: `COMMODITY_OR_CATEGORY`→`COMMODITY_OR_COUNTED_CATEGORY`; `TRANSACTION_OR_OPERATOR`→`OPERATOR_OR_RELATION`.)

## 2. Fine ontology (secondary, may be sparse) — revised per §IX

PERSON · **HUMAN_GROUP** · INSTITUTION · TITLE_OR_OFFICE · TOPONYM · ETHNIC_OR_TOPONYMIC_ADJECTIVE ·
**ANIMAL_CATEGORY** · COMMODITY · **OTHER_COUNTED_ENTITY** · MEASURE_OR_UNIT · QUANTITY ·
TRANSACTION_OR_ALLOCATION_OPERATOR · QUALIFIER · TOTAL_OR_SUBTOTAL · HEADER_OR_SECTION_LABEL ·
FORMULA_OR_BOILERPLATE · UNKNOWN. **`ANIMAL_OR_HUMAN_CATEGORY` removed** (split into ANIMAL_CATEGORY vs
HUMAN_GROUP). Uncertainty labels at both levels: `UNKNOWN` · `AMBIGUOUS` · `MULTILABEL` · `EXCLUDED`.
Entity vs relation kept separate: `entry_relation ∈ {DESTINATION, ORIGIN, LOCATION, SOURCE, …}`.
`TITLE_OR_OFFICE` is fine + **secondary only** (not in the primary gate unless counts/agreement justify).

## 3. Separate prediction targets (never merged into one label)

```
TOKEN_ROLE        (lexical entity class of a word-form)      e.g. PLACE
ENTRY_RELATION    (contextual admin relation of the token)   e.g. DESTINATION
DOCUMENT_SCHEMA   (document-level template)                  e.g. ALLOCATION_LIST
TRANSACTION_TYPE  (operation)                                e.g. DELIVERY
```
A lexical entity class and its contextual administrative relation are **different tasks** — the schema
(`role_ontology_draft.schema.json`) represents them as four independent fields.

## 4. Trivial vs non-trivial evaluation (§VI)

- `ALL_ROLE_SCORE`, `LEXICAL_ROLE_SCORE`, `STRUCTURAL_NOTATION_SCORE` = reported but NOT the gate.
- **Load-bearing = `NONTRIVIAL_UNSEEN_FORM_SCORE`**, which EXCLUDES numerals, fractions, unambiguous
  logograms, explicit totals, section dividers, **and lexical forms seen in training** (+ close
  morphological siblings that would leak).

## 5. Gold tiers · grouping · QC

See `gold_tier_rules_draft.md` (GOLD_A/B/C/X), `grouping_and_leakage_rules_draft.md` (9 grouping keys),
`annotation_qc_plan_draft.md` (two independent passes + adjudication + κ / α). Primary eval = GOLD_A only.

## 6. Projected class counts (DRAFT estimates — `projected_class_counts_draft.csv`)

Grounded on the Stage-4 graph (15,777 word-form tokens / 4,843 distinct forms / 3,133 hapax; 6,738
logograms; 8,875 numerals; 2,699 measures; 23 series). **These are estimates, not labels.** Headline
imbalance warnings:
- **`MEASURE_OR_QUANTITY` and `COMMODITY_OR_CATEGORY` dominate** (numerals + logograms ≈ 18k structural
  tokens) — these are largely the *trivial* partition and must not dominate the gate.
- The **load-bearing non-trivial-unseen-form partition is SMALL at GOLD_A** — ~150–900 securely-labelable
  content-word test units. Central power risk for the whole programme.
- **NEW (post-4.1) — cross-site power is weak: KN dominates (71%, 4,146/5,799).** Only **6 sites have ≥30
  docs**, and 5 of them are small (PY 984, TH 426, MY 99, TI 67, KH 52). PC3/S3 (cross-site) is load-bearing
  yet effectively "KN vs the rest" → a genuine cross-site power concern (open decision #C).
- Better news post-4.1: **series stratification is good** (18/23 series ≥30 docs → S5 leave-one-series-out
  viable) and **scribe is now available** (293 hands; 23 with ≥30 docs → S4 viable for top hands).
- `OPERATOR_OR_RELATION`, `TITLE_OR_OFFICE`, `DOCUMENT_STRUCTURE` likely **too sparse** for the fine gate.

## 7. Transfer eligibility (`label_transferability_draft.csv`)

Coarse classes are mostly `TRANSFER_ELIGIBLE`; structural-notation classes are `STRUCTURAL_CONTROL`;
scribe-derived and Greek-morphology-dependent fine classes are `LB_ONLY_DIAGNOSTIC` /
`EXCLUDED_FROM_TRANSFER_GATE`. The transfer model must not depend on LB lexical identity, LB-specific sign
coefficients, transliteration, lemma, or AB-shared-as-sound.

## 8. Open decisions requiring approval

See `open_decisions.md` (12 §XIII decisions + 2 findings). The critical ones: **(A)** re-map `site` to the
heading prefix (KN/PY/…) before any leave-one-site-out split — currently `area_code`; **(#8)** whether the
GOLD_A non-trivial-unseen partition is large enough for a powered gate, or the programme is `NO_POWER` at
the outset.
