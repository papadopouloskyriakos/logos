# L — INGESTION READINESS (parsers, schemas, validation)

**Campaign:** `research/linear-a-relative-phonology-seals` · **Constitution:** v2.2 · **Frozen:** 2026-07-07.
**Artifacts:** `scripts/l_ingest_parsers.py` (schema + parser stubs) · `tests/test_l_ingest_readiness.py`
(6/6 pass) · `scripts/l_source_watch_build.py` (measured baseline).

Goal: freeze the **target schema, validation contract, and parser wiring NOW** so that when a watched source
publishes, ingestion is a fill-in-the-transcription step, not a design task. No stub fabricates content — each
raises `NotImplementedError` until a real source file is supplied (append-only, Art. XVII).

## Target substrate (the silver schema, measured against the live corpus)

Every parser emits records matching `corpus/silver/inscriptions_structured.json`:

```json
{
  "id": "KNZg57", "site": "Knossos", "context": "LMIB", "support": "Sceptre",
  "words":  [["A","B"], ["C"]],
  "stream": [{"t":"word","signs":["A","B"]}, {"t":"nl"}, {"t":"word","signs":["C"]}],
  "signs":  ["A","B","C"]
}
```

Measured stream token vocabulary (from the held corpus): `word`(3,147) · `nl`(2,114) · `num`(1,276) ·
`other`(1,056) · `div`(463). Editorial types `logogram/erasure/vacat/damage` are pre-authorized for a new
editio-princeps parser.

## Validation contract (`validate_inscription`, pure, no I/O)

Enforced and tested against 200 real silver records (**0 failures**):

1. all seven required keys present;
2. every stream token is typed and of a known type;
3. every `word` token carries a `signs` list;
4. **fidelity:** `signs[]` == concatenation of `word`-token signs (catches dropped/edited signs);
5. **mirror:** `words[]` == the `word`-token sign lists.

Tests also confirm the contract *rejects* missing keys and a deliberately corrupted `signs[]`, and that the
editio-princeps parser refuses to fabricate (raises `NotImplementedError`).

## Parser stubs (one per source category)

| Function | Serves | Input when it lands | Output |
|----------|--------|---------------------|--------|
| `parse_editio_princeps(path, source_id)` | Anetaki II; new finds | hand-transcribed transliteration TSV/JSON with per-sign certainty flag | silver records → `corpus/derived/post_gorila_additions/` |
| `reconcile_signreadings(silver, corrigenda)` | GORILA corrigenda | `{insc_id:{pos:new_sign}}` | append-only diff report (no silent overwrite) |
| `update_signs_ontology(ontology, catalogue)` | sign-lists | new sign-class mapping | merged ontology + inventory-size delta → info-budget denominator |
| `parse_chic_sequences(path, source_id)` | Cretan Hieroglyphic / Cypro-Minoan | sister-script sequence dump | silver-schema records (`support`='Seal'/'Nodule') |

Already-in-repo, reused (no new stub needed): `scripts/sigla_decode.py` (SigLA `database.js` → JSON on hash
change), `sign_images/manifest` (museum rasters), `litindex.py` (onomastic/toponym → decontamination index).

## Editorial-mark fidelity (mandatory, per source rules)

Dots/brackets encode reading certainty and **must survive ingestion**. The parser attaches a per-word parallel
`certain: [bool,...]` alongside `signs`, mirroring the `post_gorila_additions` discipline (dot/bracket
preservation). Uncertain signs enter the substrate **masked**, never silently promoted to a firm reading —
otherwise a new source would leak overconfidence into effective_n.

## Source-specific readiness notes

- **Anetaki II (rank 1):** print monograph → human OCR/transcription is the only bottleneck; the pipeline
  downstream of a transcription is ready and tested. On arrival: transcribe → `parse_editio_princeps` →
  validate → **then and only then** open the sealed Anetaki predictions (never re-seal; never change
  segmentation after opening — CAMPAIGN.md prohibition).
- **Younger lexicon/texts (rank 9):** live host **withdrawn** (Kansas; confirmed BMCR 2026.01.17). Ingest from
  the held Wayback captures (`SRC-YOUNGER-LEXICON`, `SRC-YOUNGER-TEXTS`, `SRC-YOUNGER-BIBLIO`) — **do not**
  point the parser at a live URL. Value contaminated (Art. XII) → `litindex` decontamination use only.
- **SigLA (rank 5):** `sigla_decode.py` handles OCaml-Marshal `database.js`; trigger on a `database.js` hash
  change; if sign count changes, re-run the info-budget denominator before any significance figure.
- **Sign catalogues (rank 3):** ingestion changes **N** (inventory size). Gate: re-run `effective_n` /
  info-budget scripts on merge; a denominator change with no re-run is an Invariant-7 violation.

## Readiness status

| Category | Schema | Validation | Parser | State |
|----------|:------:|:----------:|:------:|-------|
| Editio princeps (Anetaki II / finds) | ✅ | ✅ | stub (transcription-gated) | READY-ON-ARRIVAL |
| GORILA corrigenda | ✅ | ✅ | stub | READY-ON-ARRIVAL |
| Sign catalogue | ✅ | ✅ | stub | READY-ON-ARRIVAL |
| Sister script (CH/CM) | ✅ | ✅ | stub | READY-ON-ARRIVAL |
| SigLA bump | ✅ | ✅ | `sigla_decode.py` | LIVE |
| Onomastic index | ✅ | ✅ | `litindex.py` (capped) | LIVE (archived src) |

## Compliance line

WP-L INGESTION: articles_triggered {IX info-budget, XI source-dependency, XVII append-only, XXII stage-header};
gates {schema validated vs 200 real records 0-fail; no stub fabricates; editorial-mark fidelity enforced;
denominator-change requires info-budget re-run}. Status: **READY**; no corpus mutated this stage.
