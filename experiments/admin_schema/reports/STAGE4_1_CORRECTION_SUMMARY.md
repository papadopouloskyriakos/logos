# Stage 4.1 correction summary

Five corrections to the Stage-4 graph, re-frozen as `stage4_1_graph_freeze.json`. All 13 tests pass.

## Before → after

| dimension | Stage 4 (original) | Stage 4.1 (corrected) |
|---|---|---|
| lb_graph sha | `f040720e` | **`81a5d6de`** |
| la_graph sha | `d79b3fe4` | **`3c417034`** |
| **site** | DĀMOS `area_code` mis-mapped (~295 findspots as "site") | **19 canonical sites** (heading prefix: KN 4146, PY 984, TH 426, MY 99, TI 67, KH 52, …) |
| findspot | conflated into site | `findspot_code` + `area_code_raw` preserved separately |
| **scribe** | 0 (used empty `vasewriter`) | **293 hands, 3,944/5,799 docs** (`hand_easy`); `S4_LEAVE_ONE_SCRIBE_OUT = AVAILABLE` |
| **LA numerals** | 0 (reported "absent") | **1,276** (silver `stream` `num` with value) |
| LA rows/entries | absent | ROW 3,435 / ENTRY 3,738 recovered |
| LA logograms | absent | 1,056 opaque `A_LOGO_UNRESOLVED` (`PRESENT_BUT_NOT_PARSED`) |
| LA sign vocab | 58 (words only) | 259 (full stream) |

## Corrections

1. **Site vs findspot** — canonical `site_code` from the DĀMOS heading prefix via `site_crosswalk.csv`;
   `area_code_raw`/`findspot_code` preserved; deterministic; joins inherit site from the heading. Leave-one-
   site-out now groups on `site_code` (19 groups), not findspots. Tests: `test_site_mapping`,
   `test_site_findspot_separation`.
2. **Scribal hand** — `vasewriter` is empty, but `hand_easy`/`handpreptt3` carry the DĀMOS hand
   classification (293 hands). Not inferred from vocabulary/layout/model. **S4 available.** Test:
   `test_scribe_crosswalk`. Audit: `SCRIBAL_METADATA_AUDIT.md`.
3. **LA structural channels** — recovered from `inscriptions_structured.json` `stream`: NUMERAL (value),
   ROW, ENTRY, WORD_FORM, SIGN parsed; LOGOGRAM/FRACTION opaque (`PRESENT_BUT_NOT_PARSED`); MEASURE
   `UNKNOWN`; DOCUMENT_SERIES `GENUINELY_ABSENT` (LA has no named series). No LB meaning imported; A_SIGN
   vocab disjoint from B_SIGN. Tests: `test_linear_a_structural_channels`, `test_linear_a_no_semantic_mapping`.
4. **Cardinality** — SIGN/WORD_FORM/ENTRY are OCCURRENCE nodes (unique ids); `opaque_id` is the shared TYPE
   key. Invariants tested: each SIGN has exactly one WORD_FORM parent; each WORD_FORM one ENTRY; no orphans;
   no duplicate ids. Audit: `GRAPH_CARDINALITY_AUDIT.md`.
5. **Formula clusters** — extracted to `formula_clustering.py`; blind by construction (input = opaque form
   ids only; rejects any non-opaque input); classified `GROUPING_ONLY`; same id ⇔ same sequence (no
   collisions). Audit: `FORMULA_CLUSTER_AUDIT.md`.

## Unchanged / carried

Transferability classes (22 TRANSFERABLE / 3 AB / 1 LB-only / 3 EXCLUDED); de-phoneticisation; blinding
firewall (no forbidden field or sound value in model-visible); determinism. LB node/edge counts essentially
unchanged (structure identical; only metadata corrected).
