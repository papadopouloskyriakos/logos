# DOCUMENT REPRESENTATION SPEC (Stage 4)

A deterministic, script-internal, **de-phoneticised** heterogeneous graph for Linear B administrative
documents, instantiable for Linear A without phonetic readings, Greek, translations, or semantics.

## Artifacts

| file | role |
|---|---|
| `data/schema/admin_document_graph.schema.json` (`628f49fb`) | JSON Schema — node/edge/provenance contract |
| `data/schema/admin_document_graph.example.json` | worked example (KN Fp(1) 1) |
| `data/schema/feature_transferability.csv` | every feature → transferability class |
| `src/corpus/graph_common.py` | node/edge types, opaque vocab, forbidden-field list |
| `src/corpus/build_linear_b_graph.py` | DĀMOS → LB graph (de-phoneticising) |
| `src/corpus/build_linear_a_compatible_graph.py` | silver LA → same schema (dry-run) |
| `src/corpus/validate_admin_graph.py` | schema + leakage validator |
| `data/model_visible/lb_graph.jsonl` (`f040720e`) · `la_graph.jsonl` (`d79b3fe4`) · `lb_reference.json` | outputs |
| `data/evaluation_only/lb_dephon_vocab.json` · `lb_source_transliteration.jsonl` · `la_dephon_vocab.json` | **the de-phon key — never model-visible** |
| `data/manifests/stage4_graph_freeze.{json,sha256}` | frozen hashes + counts |

## De-phoneticisation (the blinding core)

Every Linear B syllabogram / logogram / metrogram / qualifier is mapped to an **opaque graphic ID**
(`B_SIGN_017`, `B_LOGO_125`, `B_MEAS_012`, `B_QUAL_002`) by a deterministic vocabulary sorted over the
distinct token set. The id↔sound maps live in `data/evaluation_only/lb_dephon_vocab.json` and are **never
read by model code**. Worked example (`de-u-ki-jo-jo → di-we OLE S 1`):

```
WORD_FORM  B_SIGN_007+B_SIGN_081+B_SIGN_023+B_SIGN_020+B_SIGN_020   (de-u-ki-jo-jo, blinded)
WORD_FORM  B_SIGN_008+B_SIGN_084                                     (di-we)
LOGOGRAM   B_LOGO_125     MEASURE_MARKER B_MEAS_012     NUMERAL 1    (OLE / S / 1)
```

Linear A uses a **separate** `A_SIGN` vocab (58 signs), never merged with Linear B (§II-E).

## Node / edge model

20 node types, 30 edge types (see schema). Per-document graphs carry the intra-document hierarchy
(`DOCUMENT ▸ ROW ▸ ENTRY ▸ {WORD_FORM ▸ SIGN | LOGOGRAM | NUMERAL | FRACTION | MEASURE_MARKER | TOKEN}`)
with `NEXT/PREVIOUS_TOKEN`, `NEXT/PREVIOUS_ENTRY`, `PRECEDES/FOLLOWS_{NUMERAL,LOGOGRAM}`, and per-entry
`FORMULA_CLUSTER` membership. **Document-level entities** (`SITE`, `DOCUMENT_SERIES`, `SCRIBE`,
`OBJECT_OR_SUPPORT`, `CHRONOLOGICAL_PHASE`, `JOINED_FRAGMENT_CLUSTER`) are recorded as `meta` attributes
and materialised as **reference clusters** in `lb_reference.json` — the efficient (linear) representation
of `SAME_SITE`/`SAME_SERIES`/… and `REPEATS_FORM` (shared membership, not O(n²) pairwise edges).

## Counts (frozen)

- **LB graphs 5,799** (docs with content) · **LA graphs 1,341**.
- Node types: SIGN 44,974 · ENTRY 16,042 · WORD_FORM 15,777 · ROW 14,841 · TOKEN 10,425 · FORMULA_CLUSTER
  9,432 · NUMERAL 8,875 · LOGOGRAM 6,738 · DOCUMENT 5,799 · MEASURE_MARKER 2,699.
- Edge types: CONTAINS 120,371 · NEXT/PREVIOUS_TOKEN 31,263×2 · SAME_DOCUMENT 16,042 · NEXT/PREVIOUS_ENTRY
  10,243×2 · SAME_FORMULA_CLUSTER 9,432 · PRECEDES/FOLLOWS_NUMERAL 8,377×2 · PRECEDES/FOLLOWS_LOGOGRAM 6,164×2.
- Vocab: 89 syllabograms · 155 logograms · 17 metrograms · 2 qualifiers (LB); 58 signs (LA).
- **Reference clusters:** 295 sites · 23 series · 55 phases · **1,162 joined-fragment clusters** · **1,606
  word-forms repeated across ≥2 documents** (grouped — not counted independent).
- **Uncertainty preserved:** 12,751 nodes carry `uncertain_flag`; damage marks → `damage_flag`; broken
  boundaries → `uncertain_boundary_flag`. No silent normalisation.

## Acceptance (§II-H) — all pass

1. validates against schema ✅ (lb 0 invalid / la 0 invalid) · 2. deterministic rebuild ✅ (hash-stable) ·
3. no forbidden semantic/phonetic field OR sound-value in model-visible ✅ · 4. every feature classified ✅ ·
5. same schema instantiates LA with no semantic output ✅ · 6. provenance retained (source id/version/hash/
builder/timestamp) ✅ · 7. uncertainty explicit ✅ · 8. joins + repeated formulae grouped, not independent ✅.

## Scribe availability caveat

DĀMOS `vasewriter` is populated for **0** documents in this dump → the `SCRIBE`/`SAME_SCRIBE` channel is
present in the schema but empty here; scribe stays `LB_ONLY_DIAGNOSTIC` and the `S4` leave-one-scribe-out
split (§VIII) will need an alternative DĀMOS scribe field or is declared `NO_POWER` for scribes. Flagged for
the source audit follow-up.
