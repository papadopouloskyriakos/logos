# DECISION LOG — LA↔LB Toponym-Continuity Feasibility Pass

Append-only. Every freeze records the input hashes.

## 2026-07-06 — D1: adopt Channel B as next primary experiment (isolated)
- **Decision (user):** proceed with the LA→LB internal toponym-persistence channel first; preserve
  the Egyptian channel unchanged; do not fit/merge/delete it; return to it only after LA↔LB gets a
  mechanical power + circularity verdict. Objective: does the channel have power after removing
  projected phonetic readings, post-hoc pair selection, and free mapping search.
- **Fork point:** `research/external-minoan-anchors` @ `6d2e926e28325952313d300a5317112ae501681f`
  ("docs(anchors): correct 'acquire SigLA' — it was already in the repo, now decoded").
- **Preconditions verified (read-only):** external-anchor worktree clean (only untracked
  `experiments/external_anchors/results/`); `main` @ `f6a5682` with `paper/` + `runtime/` clean;
  target worktree path absent; new branch name free.
- **Isolation created:** `git worktree add -b research/la-lb-toponym-continuity
  /home/claude-runner/gitlab/n8n/logos-la-lb-continuity research/external-minoan-anchors` →
  new worktree HEAD `6d2e926`; parent + main verified unchanged after add.

## 2026-07-06 — D2: scaffold (commit chunk 1)
- Created `experiments/la_lb_continuity/{data/{manifests,silver,gold,bronze},src/sigla_reconcile,tests,reports}`.
- Wrote PROJECT_CHARTER.md, STATUS.md, DECISION_LOG.md, SOURCE_REGISTER.csv.
- Commit hash: _(recorded on commit)_

## 2026-07-06 — D3: SigLA↔silver reconciliation (commit chunk 2, §IV)
- **Inputs pinned** (`data/manifests/reconcile_inputs.sha256`), referenced read-only from `main`:
  - `sigla_documents.json` sha256 `218ae55b…002e`
  - `sigla_signs.json` sha256 `e2ebebc0…0bae`
  - `silver/inscriptions_structured.json` sha256 `aaee1aeb…b500` (matches external-anchors pin)
  - `silver/signs_ontology.json` sha256 `246f63f1…a80d` (matches external-anchors pin)
- **Code:** `src/sigla_reconcile/{config,reconcile}.py`; deterministic (summary sha stable across runs);
  tests `tests/test_sigla_reconcile_{normalization,crosswalk}.py` → 9 passed.
- **Result (generated):** matched 575; only-silver 766 (730 genuinely absent); only-SigLA 227 (143
  genuinely absent); site agree 546/29; period 416/14/145na; support 488/87; segmentation equal 365 /
  SigLA-more 150 / silver-more 60; learned AB→value aid 74 signs (45 ≥98%) reproduces the LB syllabary
  (firewalled from the model); A###↔*### overlap 49/298.
- **Ruling:** silver remains the LA transcription baseline; SigLA supplies sign-identity/palaeography
  and a 143-doc coverage extension. `ARKH` site ambiguity + transcription-variant uncertainty carried
  forward to §VII/§VIII. Derived data JSON kept gitignored; checksums + counts + code committed.
- Commit hash: _(recorded on commit)_

## 2026-07-06 — D4: freeze A↔B sign-equivalence layer (commit chunk 3, §V)
- **Basis (pair-blind, phonetic-blind):** SigLA's AB-vs-A classification = the conventional homomorphy
  (repertoire property; no toponym/sound input). Builder reads only the SigLA sign catalogue + LA
  attestation; blindness enforced by tests (source + content level).
- **Frozen artifact:** `data/gold/ab_sign_equivalence.json` sha256
  `77de6684a37cd4efa118bbc3e46bdc27fac86822762fa15964e814dc297f6b20` (rule `ab-equiv-v1-2026-07-06`),
  checksum in `data/manifests/ab_sign_equivalence.sha256`. Deterministic.
- **Contents:** 77 tier-A AB homomorphs (LEVEL_1 shared GORILA id, la AB## ≡ lb *##; 63 high-attestation
  ≥10 tokens), 299 tier-X A-only excluded. LEVEL_3 phonetic values firewalled to §IX ablation.
- **Declared limitation:** per-graph palaeographic B/C sub-tiering deferred to a Salgarella-2020
  collation (held locally); `high_attestation` used as the interim non-fabricated robustness handle.
- **Tests:** `tests/test_ab_equivalence_{blindness,structure}.py`; full suite 17 passed.
- Commit hash: _(recorded on commit)_

## 2026-07-06 — D5: known-pair source-critical audit (commit chunk 4, §VI)
- **Ledger (quarantined):** `data/quarantine/known_persistence_pairs.jsonl` sha256
  `9e832800386a0ef4db389482de404d09218d0a106a18c7905923c9429dd9bc8c`. Built from pinned silver (LA
  attestation) + LB scholarship. Common util `src/common/syllabary.py` (public Ventris grid, verified
  53/54 vs the learned concordance; the 1 diff = a learned-aid artifact AB188→I, grid correct).
- **Findings (recorded, not scored):** only PA-I-TO is administrative; TU-RU-SA/I-DA/SE-TO-I-JA are
  ritual-context (stone vessels), DI-KI-TA absent in silver. → 4 DEVELOPMENT_BENCHMARK, 1
  CONFIRMATORY_INELIGIBLE (di-ki-ta), 2 SPECULATIVE_MORPHOLOGICAL (di-de-ru, pa-je-re). Genre-mismatch
  (LA-ritual → LB-administrative) is a strong a-priori power concern flagged for §XIII.
- **Discipline:** all five post-hoc HIGH, `la_candidate_selected_without_lb_reading=false`; never
  confirmatory. Ledger quarantined; §VII/§VIII must not read it (leakage tests). Tests 5/5.
- Commit hash: _(recorded on commit)_

<!-- D6 LA candidate freeze §VII / D7 LB target freeze §VIII / … append below -->
