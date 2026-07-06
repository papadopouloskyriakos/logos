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

<!-- D3 SigLA reconcile / D4 A↔B equivalence freeze / … append below with input sha256s -->
