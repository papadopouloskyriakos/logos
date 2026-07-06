# DATA DICTIONARY

Schemas for the versioned, machine-readable datasets. Raw source records are **immutable**;
corrections are new `record_version`s with provenance, never silent overwrites.

## External Minoan Anchor Corpus — `anchors/**/*.jsonl` (one record per line)

| field | type | notes |
|---|---|---|
| `anchor_id` | str | stable id, e.g. `TOP-KNOSSOS-KOMELHETAN` |
| `source_id` | str | FK → `SOURCE_REGISTER.csv` |
| `source_type` | enum | `primary` \| `edition` \| `catalogue` \| `secondary` |
| `original_script` | enum | `egyptian_hieroglyphic` \| `egyptian_hieratic` \| `akkadian_cuneiform` \| `ugaritic` \| `linear_a` \| … |
| `original_text` | str | as published (unicode/translit of the source script); `null` if only a reference is held |
| `scholarly_transliteration` | str | editor's transliteration |
| `alternative_transliterations` | list[str] | editorial variants / competing readings |
| `normalized_form` | str | project-normalized comparison form |
| `translation_or_gloss` | str | |
| `semantic_class` | enum | `toponym` \| `personal_name` \| `ethnonym` \| `title` \| `commodity` \| `metal` \| `vessel` \| `textile` \| `role` \| `transaction` \| `ritual_string` \| `measure` \| `other` |
| `entity_type` | enum | `place` \| `person` \| `good` \| `institution` \| `formula` \| … |
| `candidate_modern_identification` | str | e.g. "Knossos"; `null` if none |
| `identification_confidence` | float [0,1] | that the modern id is correct |
| `refers_to_crete_confidence` | float [0,1] | that the entity is Cretan/Minoan-sphere |
| `minoan_vs_greek_confidence` | float [0,1] | **P(Minoan-speaking rather than Greek)** — load-bearing for names |
| `date_start_bce` / `date_end_bce` | int | attestation window |
| `date_confidence` | float [0,1] | |
| `linear_a_overlap_tier` | enum | `A` \| `B` \| `C` \| `D` (see below) |
| `findspot` | str | archaeological provenance of the attestation |
| `source_provenance` | str | how the record was obtained (edition/catalogue/URL) |
| `editorial_notes` | str | scholarly disagreements, recarving, damage |
| `phonetic_uncertainty` | str/float | how lossy the source script is for this form |
| `segmentation_uncertainty` | str/float | |
| `transmission_language` | str | language of the recording script (Egyptian, Akkadian…) |
| `possible_intermediary_language` | str | if the form passed through an intermediary |
| `heldout_status` | enum | `train` \| `heldout` \| `unassigned` |
| `exploratory_or_confirmatory` | enum | `exploratory` \| `confirmatory` (frozen sets only) |
| `license` | str | redistribution status of the underlying source |
| `citation` | str | full citation |
| `retrieved_at` | iso8601 | |
| `as_of_date` | iso8601 | PIT: evidence-availability date used for leakage control |
| `record_version` | int | monotonic; corrections append, never overwrite |

## Temporal tiers (`linear_a_overlap_tier`) — evidence-class-sensitive

- **A** — directly contemporary with the relevant Linear A stratum (MM III–LM IB).
- **B** — near-contemporary.
- **C** — later, admissible **only** for demonstrably persistent toponyms with an explicit persistence assumption.
- **D** — postdating / politically or linguistically ambiguous → **exploratory only**.

Mismatch handling differs by class: **personal names & ordinary vocabulary** → strong exclusion /
severe downweight for C/D; **toponyms** → C admissible with stated persistence; **administrative
semantics** → informative but never as direct phonetic evidence; **ritual strings** → exploratory
unless independently secured.

## Egyptian foreign-name calibration record — `calibration/egyptian_foreign_names/*.jsonl`

`cal_id · source_id · egyptian_spelling · egyptian_translit · source_language ·
known_source_form · gloss · date_bce · scribal_school · genre · confidence_source_form ·
notes`. **Constraint:** the calibration set must NOT contain any Cretan target anchor used in E3/E4.
The estimated Egyptian→foreign correspondence model (consonant substitution/omission/merger, cluster
handling, vowel-indicator reliability, epenthesis, metathesis, syllable restructuring, period/school
variation) is fit **only** here, versioned, and **frozen** before confirmatory matching.

## SOURCE_REGISTER.csv columns

`source_id, title, author_editor, year, identifier (DOI/catalogue/archive/URL), institution,
date_accessed, license, obtained (full|metadata|none), source_kind (primary|edition|catalogue|secondary),
refs (pages/tables/lines), disagreements, checksum, rq (RQ1..RQ6), temporal_tier, priority, notes`.

## Verdict / status — see `PROJECT_CHARTER.md`
`status ∈ {INCOMPLETE, COMPLETE}`; `verdict ∈ {NO_POWER, NULL_PUBLISHED, REJECT, GRADUATE}`.
Generated **mechanically** from frozen criteria by a verdict script (Stage 4+), never from prose.
