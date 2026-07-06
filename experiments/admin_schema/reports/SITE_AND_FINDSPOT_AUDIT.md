# Site & findspot audit (Stage 4.1 Correction 1)

**Problem:** Stage 4 mapped DĀMOS `area_code` (room/area findspot codes like "Room 8", "J1", "-") into
`meta.site`. Leave-one-site-out is load-bearing (PC3), so this is corrected before splits.

**Fix:** canonical `site_code` = DĀMOS heading PREFIX via `data/reference/site_crosswalk.csv`
(`site_mapping.py`, `site_mapping_version = site-crosswalk-v1-2026-07-07`).

| site_code | site_name | docs |
|---|---|---|
| KN | Knossos | 4146 | PY | Pylos | 984 | TH | Thebes | 426 | MY | Mycenae | 99 | TI | Tiryns | 67 | KH | Khania | 52 |

Plus ~13 minor/single-doc prefixes (MI/MA/EL/OR/KR/GL/IK/VOL/ARM/DIM/MAM/MED, and HV = internal id, flagged
NON_SITE → exclude from leave-one-site-out). **19 canonical site groups** total (was ~295 findspots).

**Preserved separately:** `findspot_code` + `area_code_raw` (exact old value); `document_identifier_prefix`;
`current_document_identifier`. Site never inferred from lexical content. Joined fragments inherit the
heading-prefix site deterministically. Mapping confidence recorded (SECURE/PROBABLE/DISPUTED/NON_SITE).

**Acceptance:** `site_code` canonical + versioned ✅; findspot/area preserved separately ✅; no
leave-one-site-out logic reads `area_code_raw` as site ✅ (`test_site_findspot_separation`); deterministic ✅.
Crosswalk sha in `stage4_1_graph_freeze.json`.
