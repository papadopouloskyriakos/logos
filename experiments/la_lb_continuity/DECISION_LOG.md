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

<!-- D4 A↔B equivalence freeze / … append below with input sha256s -->
