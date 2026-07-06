# Linear A slot-classification specification (FROZEN — `slot-rules-v1-2026-07-06`)

Internal-only assignment of each distinct Linear A word-form to a document-role / semantic class,
using **evidence internal to the Linear A corpus only**. Frozen before any external anchor is allowed
to interact with Linear A. Implementation: `src/slot_classifier/slotlib.py`; driver
`build_manifest.py`; tests `tests/test_slot_classifier_{leakage,rules}.py`.

## Prohibition (leakage contract)
The classifier MUST NOT consult: external toponyms, Egyptian spellings, personal-name lists,
candidate-language lexica, projected/Linear-B phonetic values, any manually "promising" form, or any
anchor-match score. Enforced by tests: stdlib-only imports; opens only the checksum-pinned
`corpus/silver/{inscriptions_structured.json, signs_ontology.json}`; no `anchors/`, `calibration/`,
or `candidate_languages` path in code; every manifest row carries `leakage_exclusion_status =
internal_only_clean`; and the manifest must be built while **no matcher module exists**.

## Inputs (read-only, pinned)
`inscriptions_structured.json` (sha `aaee1aeb…`) and `signs_ontology.json` (sha `246f63f1…`),
verified at load (drift ⇒ hard error). The ontology is used **only** for sign *class*
(logogram/syllabogram) — never for any phonetic value.

## Classes
`TOPONYM_LIKE · PERSON_NAME_LIKE · COMMODITY · TITLE_OR_OFFICE · INSTITUTION · TRANSACTION_TERM ·
RITUAL_FORMULA · NUMERIC_OR_METROLOGICAL · UNKNOWN`. Strings are not forced into a meaningful class.

## Internal features (per distinct word-form, aggregated over occurrences)
Recurrence (`occ`, `n_sites`, `n_docs`), sign length, damage flag; position (`header_rate`,
`terminal_rate`, `pre_num_rate` = followed by a numeral, `post_logo` = followed by a logogram);
context (`adj_kuro`/`adj_kiro` = adjacent to total/deficit, `ritual_genre_rate` = share on
stone/clay/metal vessel supports); genre = support type. **No phonetic feature.**

## Rules (deterministic, tiered) — evaluated in order
1. **X (exclude)** — damaged/uncertain sign (`[ ] ? *`) or length ≤ 1.
2. **TRANSACTION_TERM / A** — form ∈ {KU-RO=total, KI-RO=deficit, PO-TO-KU-RO=grand total} (attested
   internally by recurring form + position, not by any external reading).
3. **COMMODITY / A** — the form is/contains a logogram (ontology class only).
4. **RITUAL_FORMULA / B|C** — `ritual_genre_rate ≥ 0.5` (predominantly on vessel supports); B if occ≥3.
5. **entry-leading** (`header_rate ≥ 0.5` OR `pre_num_rate ≥ 0.5` OR `post_logo ≥ 1`):
   - **TOPONYM_LIKE / B|C** — recurs across the network (`n_sites ≥ 2` OR `n_docs ≥ 3`); B if both.
   - **PERSON_NAME_LIKE / C** — entry-leading but localized/hapax (single site, few docs).
6. **TRANSACTION_TERM / C** — adjacent to a total/deficit but otherwise unclassified.
7. **UNKNOWN / C** — default.

Tiers: **A** strong structural · **B** moderate convergent · **C** weak/exploratory · **X** excluded
from confirmatory use.

## Held-out design
**Leave-one-site-out**, `heldout_group = primary site` (alphabetically-deterministic when a form
spans sites), split rule + `seed = 20260706` recorded in the manifest checksum file. Sites present:
Haghia Triada, Khania, Knossos, Phaistos, Zakros, Palaikastro, Malia, Thera, … The E3 confirmatory
test trains a mapping on some sites and predicts held-out-site TOPONYM_LIKE forms.

## Outputs
`data/silver/linear_a_slot_features.jsonl` (features), `data/gold/slot_candidate_manifest.jsonl`
(1165 candidates, schema in `DATA_DICTIONARY`-style fields), `data/manifests/
slot_candidate_manifest.sha256` (freeze hash + rule version + split rule/seed).

## Freeze
`rule_or_model_version = slot-rules-v1-2026-07-06`, `manifest_version = 1`. Any change to rules or
features bumps the version and re-freezes; the confirmatory anchor test binds to a specific manifest
hash.
