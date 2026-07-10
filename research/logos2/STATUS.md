# LOGOS-2 campaign status

**Updated:** 2026-07-10 (milestone 2 in progress) · branch `research/logos2-anchor-identifiability` ·
governance: Constitution v2.3 + `CLAIM_LADDER.md` + `MILESTONE2_CONTROL_ADDENDUM.md` (@5deec1e,
frozen before any confirmatory inspection).

| item | state |
|---|---|
| PREFLIGHT + E200 | COMPLETE (L0) |
| M2 control addendum | FROZEN @5deec1e (E201-F1 rules, 200-null calibration, import boundary) |
| E201 pilot | COMPLETE — HARNESS_OPERATIONAL (UGA ladder 0.037→0.591@5names; CSYL flat at chance; 0/15) |
| **E201-F1a** | **SCORED: ALPHABETIC_REPLAY_ONLY_NOT_QUALIFIED_FOR_LINEAR_A** (LB 0.000/CSYL chance/UGA 0.486<0.60 discounted; calibration CERTIFIED 0/200, CP95 1.49%) |
| E201-F1b | PENDING CSA-sweep import (§2.3 boundary; sweep ETA ~2026-07-13) |
| E202 acquisition policy | **COMPLETE** — VOI measured off E203-F1; top actionable = GORILA fraction-apparatus ingestion; value-space max = bilingual (+17.95 log10) but fragility 0.20 |
| E203 pilot + F1 | **COMPLETE (confirmatory)** — ENGINE_VALIDATED; WPH38 exact count 10^224.83; MUS cores size-2 CORES_TYPICAL_OF_RANDOM; value-permutation nulls UNSAT 200/200; soft always-violated set band-stable |
| E204 metrology | **E204_BLOCKED_DATA_QUALITY** — Younger apparatus extracted by two independent parsers (1362/1446 records) but gate FAILED (86.3%<98%; statement-field divergence localized); numeric core near-gate; seal UNOPENED & unread; artifacts + adjudication log preserved; unblock path specified |
| E205 palaeography | **I COMPLETE: PRIOR_GENERIC** (grade prior ≡ pin-count; hard arm UNSAT_GENERIC); A/B deferred w/ reason; C BLOCKED_DATA |
| E206 onomastics | **Stage-1 SLOT FREEZE COMMITTED** (151 candidates, 4 contaminated-flagged, formula head derived internally; zero external contact); Stage 2 not started |
| E207 morphology | **COMPLETE: POSITIONAL_ONLY** (corrected battery after amendment R1; no predictive paradigm; A-initial enrichment stays exactly that) |
| E208 | DE_AUTHORIZED_PENDING_LICENSE_CLEAN_GATE |
| E209/E210/E211 | not started (gated/auxiliary) |
| M2 report | **DELIVERED** (reports/MILESTONE2_*) |
| E204R2 canonicalization | **QUALITY_GATE_PASSED** (single pass; overall .9995, statement .9957, full-record .995; canonical dataset frozen: 1385 dual-agreed records / 324 fraction-bearing) |
| E204 metrology | **UNLOCKED — stack frozen (bc5599f), engine RUNNING** (CP-SAT bases 60/120/240, relations + ablations + 200 matched-notation nulls; seal STILL closed) |
| E204R remediation | **E204R_BLOCKED_DATA_QUALITY** — gate failed on statement 0.9763<0.98 alone (33 rows, 2 named classes); NUMERIC apparatus at 1.000 dual-parse agreement (326 fraction records, 72 multi-frac, 23 arith-complete docs); 2 amendments (R1 hang/grammar/trap, R2 bullets/entities); seal untouched |
| Autopilot | **LIVE** — 15-min cron watchdog installed+tested (8/8), resumes this session when idle; STOP file + 8-failure breaker + final-state exit |
| E206 Stage-2 | NEXT (prereg freeze: DAMOS/toponym inventories, drift model, canary battery, hierarchy) |
| E212–E214 + final/ | queued after E206-S2; F1b import boundary armed for sweep (~07-13) |

**Amendment discipline exercised twice** (E203 G1 gate criterion; E207 probability sign error) —
both defect repairs with as-run artifacts preserved; no result-driven adaptation.

**Standing:** CSA sweep runs until ~2026-07-13 (its at-scale cells enter only via `imports/`);
paper/governance/corpus/72h campaign untouched; all seals unread; ledger.jsonl append-only.

---

## 2026-07-10 — CAMPAIGN CLOSED → POST-CLOSURE MAINTENANCE

Closure commit `8d67213` (branch `research/logos2-anchor-identifiability`). Verdicts final:
E204 `UNDERDETERMINED_AFTER_ABLATION` · E212 `NO_MULTI_CHANNEL_INDEPENDENT_CLAIM` · E213
`SEALED_PROSPECTIVE` (2 predictions, sha256 5b50f21d…) · E214 battery PASS · package 232
artifacts verified · review ZIP hash-verified · protected assets 33/33 · both seals closed
and unread. Cron autopilot removed (`automation/CRON_REMOVAL_TRANSCRIPT.md`); watchdog
scripts retained for audit. **No autonomous continuation is permitted without a registered
reopening event** (see `final/METHOD_EXHAUSTION_UPDATE.md` §reopening). Sole pending item:
the E201-F1b post-closure addendum via `imports/E201_F1B/` when the external CSA sweep
completes (~2026-07-13) — classified only as INDEPENDENT_REPLICATION / SCALE_EXTENSION /
NON_COMPARABLE / FAILED_IMPORT / INVALID; F1a remains the binding confirmatory result; E208
remains DE-AUTHORIZED.
