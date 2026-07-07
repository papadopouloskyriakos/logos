# Human-pilot sampling plan (frozen BEFORE sampling)

Deterministic sample for later annotation by **two genuine human experts**. Plan frozen in
`src/human_pilot/draw_human_pilot.py` (PLAN dict) and echoed in `data/human_pilot/human_pilot_manifest.json`.

| parameter | value |
|---|---|
| target size | 160 (floor 120; if <120 eligible → `NO_POWER / INSUFFICIENT_INDEPENDENT_SAMPLE`) |
| random seed | 20260708 |
| replacement | without replacement (distinct form-types) |
| site quota | KN 80 / non-KN 80 |
| recurrent/hapax | 80 / 80 (40 per site×balance cell) |
| series / support spread | ≥8 series, ≥3 supports |
| context-type proxy | before_logogram / before_numeral / standalone / other — **coverage device only, never a label** |
| role coverage | context-type spread ensures candidate HUMAN/PLACE/COMMODITY/OPERATOR/QUALIFIER forms are present; **roles are NOT assigned here** |
| cluster exclusion | auto-pilot form-families + all forms in auto-pilot documents + stem-siblings + formula-cluster siblings |

**Eligible independent pool: 2,454** content forms (after excluding 2,305: 160 auto-pilot + 1,715
in-pilot-docs + 1,095 stem-siblings). Drew **160** (strata KN/hapax 40 · KN/recurrent 40 · nonKN/hapax 40 ·
nonKN/recurrent 40). Nothing is reserved for a sealed holdout yet (holdout not chosen).

Outputs: `data/human_pilot/pilot_sample.{jsonl,csv}` (reading-bearing → gitignored),
`data/manifests/human_pilot_sample.sha256`, `data/human_pilot/human_pilot_manifest.json` (plan + strata +
hashes, committed).
