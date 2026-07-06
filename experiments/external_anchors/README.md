# External Minoan Anchors — logos parallel subproject

Falsification-first investigation of whether **external** Bronze Age evidence (Egyptian/Near-Eastern
attestations of Cretan names, places, goods, and speech; administrative archives; aDNA priors) can
supply **independently verifiable** constraints for partial interpretation or phonetic anchoring of
Linear A. **A rigorous null is a success.** No candidate-language tournament, and no confirmatory
claim, before the anchor + calibration + null layers are frozen and externally timestamped.

- **Governance:** `PROJECT_CHARTER.md` (mission, isolation contract, RQs, verdict ontology),
  `ROADMAP.md` (stages + experiment ledger), `DATA_DICTIONARY.md` (schemas), `STATUS.md`,
  `DECISION_LOG.md`.
- **Sources:** `SOURCE_REGISTER.csv`; blocked items in `MATERIAL_REQUESTS.md`.
- **Data:** `data/{bronze,silver,gold}` (immutable raw → normalized → frozen inputs); `anchors/`,
  `calibration/`, `population_priors/`, `candidate_languages/`, `nulls/`.
- **Read-only Linear A corpus:** referenced in place at `/home/claude-runner/gitlab/n8n/logos/corpus/silver/`
  (licensed/gitignored — **never copied or committed**); checksums in
  `data/manifests/linear_a_inputs.sha256`. Forked from `main@762f48d`.

## Isolation
Runs on branch `research/external-minoan-anchors` in a separate worktree. Does not touch the live
CSA sweep, `runtime/`, `paper/`, the TACL manuscript, existing preregistrations, or Zenodo. Compute
is light through Stage 2; Stage 3+ uses idle/separate resources or waits for the sweep.

## Central discipline
The Egyptian→foreign phonological-correspondence model is estimated on an **independent** calibration
corpus and **frozen before** any Cretan match; the Linear A slot classifier is frozen before
confirmatory testing; a Linear-B **positive control** gates sensitivity; **end-to-end null
calibration** (not naïve hypothesis counting) sets significance; verdicts are **mechanical** from
frozen criteria. Toponyms lead (continuity across the Minoan→Mycenaean shift); temporal overlap is a
hard, evidence-class-sensitive filter; transcription uncertainty is propagated.
