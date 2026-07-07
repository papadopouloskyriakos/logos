# Stage B — corpus forensics & representation recovery

**Claim layer:** L0–L2 (representation). **Articles:** VIII, IX, XI, XII, XVII, XXII. **Advancement gate: PASSED**
(false units removed + params clarified + channels recovered). No value-informative gain — consistent with
Stage A. Five parallel sub-audits (`wf_da6d35c8`); artifacts in `data/`, `scripts/stage_b_clean_representation.py`.

## What changed

| sub-audit | result |
|---|---|
| **B2 sign/allography** | Confirms the syllabary = **92** (conservative) — the "259" was 108 ligatures + 13 damage-tokens (only 121/258 word-tokens are pure inventory signs). Allography removes just **7** params total; distribution yields **no** new defensible merges; hapax already excluded by conservative-92. Site-specific allography inflates lexical diversity <1%. **Data-hygiene bug:** ontology uses ASCII `PA3`, corpus uses Unicode `PA₃` — naive join drops 133/258 tokens (fixed by subscript-normalization here). |
| **B1 cross-edition (SigLA)** | SigLA is a **second digitization of the same GORILA editions** → an ingest check, **not** independent corroboration (0 held-out weight). On 590 shared docs, 38% byte-identical, ~90% of residual is edition convention. **Key:** the AB-class that licenses a Linear B value is **contested** — 10 GORILA sign-numbers flip AB↔A-only across editions (34 tokens) → the value-bearing set is itself unstable. |
| **B4 joins/duplicates** | Raw 1341 overstates independence: physical-object collapse → **1242 objects**; only 618 records carry ≥2 signs → **565 distinct content signatures** (the usable lexical evidence base, ~2.4× smaller). 600 single-sign nodules = only 14 sign-types. 86 `HYPOTHESIZED_JOIN` candidates delivered (never merged). |
| **B5 notation** | **222 commodity logograms were mis-routed into the phonetic word channel**; the `other` bucket collapses ≥5 untyped channels (ASCII fractions 313, Bennett A700 LA fractions ~127, placeholder `U+1076B` 451, logograms, lacunae). Accounting closure is crippled by this (only 7/34 KU-RO lines sum). **Typing the channels cleans the wordform set and is the prerequisite to a usable accounting constraint (Stage D4).** |
| **B6 context** | The `context` field is **mislabelled** (holds chronology/phase, not archaeology); true findspot is collapsed into `site`. **Support/object-type is a genuine independent invariance axis** (H(support\|site)=1.23 bits, cross-cuts site) — "survives-medium-removal" is testable *now*. Finer findspot is recoverable from a bronze source (Younger `HTtexts.txt`). |

## Concrete deliverable — cleaned representation (`data/`)

`stage_b_clean_representation.py` → `clean_phonetic_wordforms.json` + `stage_b_representation.json`:
- word tokens 3147 → **2328 PHONETIC / 402 LIGATURE / 298 LOGOGRAM / 119 MIXED** — **26% of the word channel
  was non-phonetic contamination** the prior analyses ran on;
- clean phonetic wordform types **944** (was 1165), multi-sign **878** — the proper input for Stage D;
- effective denominators corrected: **1242 physical objects; 565 usable ≥2-sign lexical signatures**.

## Verdict

**Stage B ADVANCES the representation** (false units removed, phonetic channel cleaned, notation/context
channels identified for recovery, a real ingest bug fixed) but adds **no value-informative constraint** — as
Stage A predicted. It sharpens Stages D–F: D runs on clean phonetic material + the newly-identified accounting
and support-invariance channels; the AB-class instability (B1) further discounts the (circular) value channel.
