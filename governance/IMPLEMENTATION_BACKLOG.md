# Implementation backlog — machine-readable obligations v2.0 creates

Append-only (Art. XVII). What adopting v2.0 obligates us to build, and what already exists. Produced by
audit run `wf_4c40bcc4-428` (repo inventory of `logos` + reusable `../finops-agora` machinery). Adoption
does **not** require these before ratification — they gate *future graduating claims*, not the constitution.

## Already satisfied (reuse, don't rebuild)

- **Multiplicity / selection-bias deflation** (Art. VII, VI) — `scripts/logos_stats.py`: order-statistic
  E[max], Deflated Sharpe, PSR, PBO, CPCV, `dsr_trial_count` (ported from the finops-agora López de Prado
  lineage). The operative deflation engine.
- **Machine-search trial counter / N_eff with deterministic dedup** (Art. VII, XIX) —
  `scripts/comparison/searchlog.py` (`SearchLog.log_candidate/.n_eff`, canonical assignment×lexeme×
  segmentation key, per-dimension tripwire); consumed by `scripts/verdict.py`, pinned via
  `verdicts.search_log_id`. Covers "count the trials, don't estimate" for one scanner.
- **Gate false-graduation / null power sim** (Art. VIII, IV) — `scripts/gate_null_calibration.py`
  (best-of-N_eff random readings through the full gate → 3/500 = 0.6%).
- **Information-floor component** (Art. IX, partial) — `scripts/corpus_info.py`, `scripts/inventory/
  floor_cleaned.py` (unicity distance U=H(K)/D, bigram entropy, redundancy) — ~3–4 of the 13 panel fields.
- **Content-addressed hypotheses + committed prediction + sole-writer verdict** (Art. II, III, XIX) —
  `schema/schema.sql` (`hypotheses` PK=`plan_hash`, `prediction` NOT NULL; verdicts sole-writer) +
  `scripts/verdict.py`.
- **L_fake canary + held-out §E acceptance gate** (Art. IV) — `scripts/comparison/lfake.py`, `lexstat.py`.
- **Assumption register** (Art. XVIII) — `governance/assumption_register.json` (schema v2, 9 premises).
- **Transfer-licence state** (Art. XV) — `governance/transfer_licences.json`.

## Missing — prioritized

| P | item | article | note |
|---|---|---|---|
| ~~P0~~ **DONE** | ~~Append-only correction ledger~~ **BUILT** (2026-07-07) — `verdicts` is now append-only (`status`/`current_key`/`supersedes_id`/`superseded_by_id`/`correction_type`) + a general `correction_ledger` table; `write_verdict` appends a superseding row (content-idempotent via `verdict_hash`), never overwrites. Migration applied to the live DB; `tests/test_verdict_append_only.py` locks it. | XVII | Fixed the live anti-pattern: `ON DUPLICATE KEY UPDATE` / delete-then-reinsert removed from the sole writer; `family_scores` reads `status='current'`. |
| ~~P0~~ **DONE** | ~~source-dependency graph~~ **BUILT** (2026-07-07) — `governance/source_dependency_graph.json` (13 sources, 6 evidentiary lineages) + `scripts/source_dependency.py` lineage-collapse checker (DAMOS+V-C+DMic → 1 vote; fail-loud on unknown source) + `tests/test_source_dependency.py`. Promotes the A04 SHARED_DECIPHERMENT finding to an enforceable artifact; `effective_sources()` feeds Art. VIII. | XI | Done. Next: wire `effective_sources()` into the Art. VIII evidence-unit effective_n primitive. |
| ~~P0~~ **DONE** | ~~effective_n over EVIDENCE UNITS~~ **BUILT** (2026-07-07) — `scripts/effective_n.py`: bottleneck (min independent-unit count across required dims) + Art. XI source-lineage fold + `dependency_components` union-find. | VIII | Distinct from the finance time-overlap primitive; graduation keys off it. |
| ~~P0~~ **DONE** | ~~information-budget panel~~ **BUILT** (2026-07-07) — `scripts/info_budget.py`: all 13 fields (missing → UNKNOWN), `certify()` fails closed on UNKNOWN load-bearing fields or underdetermination (params > evidence), B7-scoped. Validated on the no-human 19-vs-57 case. | IX | Composes effective_n + corpus_info unicity component; unicity alone insufficient. |
| **P1** | **Program-level search receipt** — candidate languages, feature/MODEL families, alignment methods, thresholds, seeds, restarts, subgroups, exclusions, failed branches + the 4-way preregistered/cross-model/exploratory/confirmatory partition. | VII | `searchlog.py` counts only one scanner's triples; program-level dimensions captured nowhere. Build `governance/search_receipt.json`. |
| **P1** | **Per-stage constitutional headers** (`articles_consulted/triggered`, gates, assumptions checked, authorized/forbidden outputs) at open + a compliance/deviations/violations block at close. | XXII | Nothing emits these. Template + JSON schema + a linter that blocks a stage without a header. |
| **P2** | **Assumption-register enforcement hook** — a loader that BLOCKS downstream execution when a load-bearing premise is FALSE (A04/A08/A09 already are) or STALE past expiry. | XVIII | Register is currently a static file with no consumer. Add `assumption_gate.py` imported at stage entry. |
| **P2** | **Transfer-licence enforcement checker** — gate experiments on current licence state; mechanically enforce "a lower licence never implies a higher one" + layer-capping. | XV, V | State file has no consumer. Ties into the Art. XXII forbidden-outputs field. |

## Top priorities to build next

1. ~~**Art. XVII correction ledger**~~ — **DONE 2026-07-07** (append-only verdicts + `correction_ledger`;
   live migration applied; in-place mutation removed from the sole writer).
2. ~~**Art. XI source-dependency graph**~~ — **DONE 2026-07-07** (`governance/source_dependency_graph.json`
   + `scripts/source_dependency.py`; A04 now an enforceable lineage-collapse gate).
3. ~~**Art. VIII evidence-unit effective_n**~~ — **DONE 2026-07-07** (`scripts/effective_n.py`; composes
   `source_dependency.effective_sources`).
4. ~~**Art. IX information-budget panel**~~ — **DONE 2026-07-07** (`scripts/info_budget.py`; fail-closed).
5. **Art. VII program-level search receipt** — beyond the single-scanner triple.
