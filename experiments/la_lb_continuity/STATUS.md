# STATUS — LA↔LB Toponym-Continuity Feasibility Pass

_Single source of current state. Phases follow the commit plan (§XVIII)._

## Current phase: **§IX–§XV ANALYSIS (INPUT_FREEZE_APPROVED 2026-07-06). Membership frozen; mechanical verdict pending.**

| # | Phase | State |
|---|-------|-------|
| 1 | Branch/worktree + project scaffold | ✅ DONE |
| 2 | SigLA source audit + silver crosswalk + corpus delta | ✅ DONE |
| 3 | Freeze A↔B sign-equivalence layer (blind to known pairs) | ✅ DONE (77 tier-A, `77de6684`) |
| 4 | Known-pair source-critical audit (five = DEVELOPMENT_BENCHMARK) | ✅ DONE (4 benchmark, 1 ineligible, 2 speculative) |
| 5a | Freeze internal-only LA candidate manifest (§VII, packet A) | ✅ DONE (11 PRIMARY, I-DA quarantined, `eb2bb293`) |
| 5b | Independent LB toponym target manifest (§VIII, packet B) | ✅ DONE (33 targets, `29e25d49`) |
| — | **STOPPED — awaiting INPUT_FREEZE_APPROVED before §IX–§XV** | ⛔ HERE |
| §II | metadata freeze clarifications (partitions/ARKH/unit) | ✅ DONE |
| §IX–§XV | model+ablations / controls / nulls / heldout / power / circularity / verdict | 🔄 IN PROGRESS |
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

## Next concrete step (phase 4, §VI)
Source-critical audit of the five known pairs (`pa-i-to · tu-ru-sa · di-ki-ta · i-da · se-to-i-ja`) →
default class **DEVELOPMENT_BENCHMARK** (already observed ⇒ not confirmatory). Record for each: LA raw
sign sequence + docs/site/date/context/slot-class, LB form + independent entity identification +
docs/site/date, selection history, post-hoc risk, same-source dependency, confirmatory eligibility.
Store `di-de-ru~di-de-ro`, `pa-je-re~pa-je-ro` separately as SPECULATIVE_MORPHOLOGICAL_CONTINUITY.
