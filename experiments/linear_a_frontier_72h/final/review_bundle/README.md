# LOGOS 72-Hour Linear A Frontier Campaign — External Review Bundle

Self-contained audit package for the closed `research/linear-a-frontier-72h` campaign (105 epochs).

## Where to start
1. **`CAMPAIGN_FINAL_REPORT.md`** — the authoritative executive summary, verdicts, and one graduated finding.
2. **`GRADUATED_FINDINGS.md`** — the single graduated result (A- prefixation, relative structural, no value).
3. **`CROSS_EPOCH_EVIDENCE_SYNTHESIS.md`** — the dependency-aware synthesis (why nothing reaches L4+).
4. **`STRONG_LEADS_AND_FAILED_REPLICATIONS.md`** — every lead and its adjudication.

## Which reports are authoritative
`CAMPAIGN_FINAL_REPORT.md` + the machine-readable `*.json` closure files are authoritative. The narrative reports
cite generated numbers. Where a bucket tally is heuristic it is labelled; per-epoch **verdicts** are verbatim from
the append-only ledger and are exact.

## Contents
- **Reports (§12.1–12.10):** CAMPAIGN_FINAL_REPORT, CROSS_EPOCH_EVIDENCE_SYNTHESIS, GRADUATED_FINDINGS,
  STRONG_LEADS_AND_FAILED_REPLICATIONS, METHOD_EXHAUSTION_MAP, INFORMATION_GAIN_AND_BOTTLENECKS,
  PROSPECTIVE_SEALS_AND_FUTURE_TESTS, NEXT_STEPS_AFTER_CAMPAIGN, INTEGRITY_AND_REPRODUCIBILITY.
- **Machine-readable (§13):** CAMPAIGN_FINAL_STATE.json, FINAL_VERDICTS.json, GRADUATED_FINDINGS.json,
  STRONG_LEADS.json, METHOD_EXHAUSTION_MAP.json, PROSPECTIVE_SEALS.json, ARTIFACT_MANIFEST.json.
- **Tables:** EPOCHS_001_TO_FINAL_MASTER_TABLE.csv (one row per epoch), RECONCILIATION_TABLE.csv.
- **Key adjudication machinery + preregs:** EPOCH-103 (strong-lead), EPOCH-104 (campaign-wide null),
  EPOCH-105 (synthesis) — each with prereg.md, plan_hash.txt, machinery.py, result.json.
- **Prospective-seal hashes:** FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256.

## How to verify hashes
`ARTIFACT_MANIFEST.json` holds sha256 of every closure file. Re-hash with
`sha256sum <file>` and compare. Seal integrity: `sha256sum -c FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256`.

## How to reproduce key results
From the branch repo root:
- **A- adjudication (E103):** `python3 experiments/linear_a_frontier_72h/epochs/EPOCH-103/machinery.py`
  → REPLICATED_RELATIVE_CONSTRAINT, byte-identical scientific content (fixed seeds).
- **Campaign-wide null (E104):** `python3 experiments/linear_a_frontier_72h/epochs/EPOCH-104/machinery.py`
  → false-graduation 0.5% (full) vs 30.5% (maxT ablated), planted 40/40. ~3.5 min.
- **Closure regeneration (E105):** `python3 experiments/linear_a_frontier_72h/final/generate_closure.py`
  → regenerates all JSON + CSV from the append-only ledger.

## Large artifacts outside the bundle
Licensed source material (DĀMOS Linear B, GORILA, SigLA — CC BY-NC-SA / vendor terms) is **excluded** and cannot be
redistributed. The silver corpus derivatives the epochs consume live in the branch under `corpus/silver/` where
licence permits. Per-epoch `data/` outputs and full `reports/` are in the branch (gitignored → committed with
`git add -f`); the bundle carries the closure layer, not every intermediate.

## One-line result
No decipherment. One graduated *relative structural* finding (A- prefixation). Corpus exhausted within scope;
bottleneck = anchor independence. The discipline is certified load-bearing. This is the intended insurance outcome.
