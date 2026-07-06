# STATUS — LA↔LB Toponym-Continuity Feasibility Pass

_Single source of current state. Phases follow the commit plan (§XVIII)._

## Current phase: **2 → 3** (SigLA reconciliation done; A↔B equivalence next)

| # | Phase | State |
|---|-------|-------|
| 1 | Branch/worktree + project scaffold | ✅ DONE |
| 2 | SigLA source audit + silver crosswalk + corpus delta | ✅ DONE |
| 3 | Freeze A↔B sign-equivalence layer (blind to known pairs) | 🔄 NEXT |
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

## Key finding (phase 2)
SigLA 802 docs / 376 signs vs silver 1341 records: **575 matched**, but **730 silver + 143 SigLA docs
genuinely absent** from the other (corpus-composition difference, not normalization). AB signs agree
(learned map reproduces the LB syllabary); SigLA keeps ~249 A-series composites silver decomposes.
Site typos + the `ARKH` (Arkhanes/Arkalochori) ambiguity flagged for §VIII. **Silver stays the LA
baseline; SigLA supplies sign-identity/palaeography for §V.**

## Next concrete step (phase 3, §V)
Freeze the palaeographic A↔B sign-equivalence layer **blind to the five known pairs**: LEVEL_1 = shared
sign-ID identity; LEVEL_2 = the 77 SigLA AB-class signs as conventional A↔B homomorphs (confidence
tiers A/B/C/X), with `target_pair_used_in_selection=false` and `phonetic_value_used=false`. Checksum
and freeze before any sequence matching.
