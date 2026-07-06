# STATUS — LA↔LB Toponym-Continuity Feasibility Pass

_Single source of current state. Phases follow the commit plan (§XVIII)._

## Current phase: **1 → 2** (scaffold done; SigLA reconciliation in progress)

| # | Phase | State |
|---|-------|-------|
| 1 | Branch/worktree + project scaffold | ✅ DONE |
| 2 | SigLA source audit + silver crosswalk + corpus delta | 🔄 IN PROGRESS |
| 3 | Freeze A↔B sign-equivalence layer (blind to known pairs) | ⬜ |
| 4 | Known-pair source-critical audit (five = DEVELOPMENT_BENCHMARK) | ⬜ |
| 5 | Freeze internal-only LA candidate set + independent LB target set | ⬜ |
| 6 | Primary matching model + ablations A1–A5 (no free mapping search) | ⬜ |
| 7 | Positive controls | ⬜ |
| 8 | End-to-end null framework (≥10 families) | ⬜ |
| 9 | Power pass + risk-adjusted channel comparison | ⬜ |
| 10 | Circularity + design-readiness verdict | ⬜ |

## Verdicts (not yet issued)
- `status`: **INCOMPLETE**
- `channel_readiness`: **NOT_READY** (pending frozen inputs + power)
- `circularity`: **not yet evaluated**

## Isolation invariants held
- Forked from `research/external-minoan-anchors` @ `6d2e926`; parent worktree unchanged.
- `main`, `paper/`, `runtime/csa_sweep/`, live CSA processes: **not touched**.
- Egyptian channel: **preserved, not fitted, not merged**.

## Next concrete step
Compute the deterministic SigLA↔silver crosswalk + corpus delta from canonical main-repo inputs
(read-only), write the three SIGLA_* reports + tests + input checksums, commit as chunk 2.
