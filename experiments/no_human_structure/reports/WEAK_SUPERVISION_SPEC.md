# Weak-supervision spec (Stage 4)

13 deterministic labeling functions (`src/weak_supervision/labeling_functions.py`), each votes a coarse role
or ABSTAINs from a cited index OR an observable structural rule. **Structural (EDITION_INDEPENDENT) LFs are
kept separate from index (SHARED_DECIPHERMENT) LFs.** No eval-gold read for the vote; no Linear A; no model
predictions. Frozen: `configs/weak_supervision_freeze.json`.

| LF | class | rule |
|---|---|---|
| LF_TOPONYM_INDEX / LF_TITLE_INDEX / LF_OPERATOR_INDEX / LF_QUALIFIER_INDEX | SHARED_DECIPHERMENT | cited published index membership |
| LF_PERSON_NAME_INDEX | SHARED_DECIPHERMENT | **abstains** (no machine-readable PN index — never fabricate) |
| LF_LOGOGRAM_ADJACENCY / LF_NUMERAL_POSITION / LF_ENTRY_POSITION / LF_RECURRENCE_PATTERN / LF_HEADER_POSITION / LF_TOTAL_POSITION / LF_NEGATIVE_EXCLUSION | EDITION_INDEPENDENT | observable structure |
| LF_DOCUMENT_SERIES | EDITION_INDEPENDENT | **abstains** in WS (series is a shortcut — diagnostic only) |
| LF_CROSS_SOURCE_CONCORDANCE | CROSS_CLASS | independent evidence ONLY across independence classes (index ∧ structural agree) |

## Label models (WS0–WS4)
WS0 majority · WS1 source-weighted (index×2) · WS2 accuracy-weighted (dev precision) · WS3 dependency-aware
(collapse same-independence-class votes to one) · WS4 conservative intersection (unanimous only).

## Metrics (`data/source_labels/weak_supervision_metrics.json`)
Coverage 0.71 · abstain 0.29 · conflict 0.044 · mean LFs firing 0.76 · dependency-sensitivity (WS1−WS3) 0.0.
See `LABEL_FUNCTION_AUDIT.md` for the critical circularity caveat on "precision".
