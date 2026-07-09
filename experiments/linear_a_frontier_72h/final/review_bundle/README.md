# LOGOS 72-Hour Linear A Frontier Campaign — External Review Bundle

**This is an AUDIT PACKAGE**: the closure layer plus the key adjudication epochs of the closed
`research/linear-a-frontier-72h` campaign (105 epochs). It is *not* a self-contained reproduction package — the
reproduction environment is the branch repository itself (see "How to reproduce"). Rebuilt under the terminal
audit remediation pass (E103R/E104R, corrected closure generator).

## Where to start
1. **`CAMPAIGN_FINAL_REPORT.md`** — the authoritative executive summary, verdicts, and one graduated finding.
2. **`GRADUATED_FINDINGS.md`** — the single graduated result (A-initial positional enrichment, relative
   structural, no value).
3. **`CROSS_EPOCH_EVIDENCE_SYNTHESIS.md`** — the dependency-aware synthesis (why nothing reaches L4+).
4. **`STRONG_LEADS_AND_FAILED_REPLICATIONS.md`** — every lead and its adjudication.

## Which reports are authoritative
`CAMPAIGN_FINAL_REPORT.md` + the machine-readable `*.json` closure files are authoritative. **Counts are
generated** (by `generate_closure.py` from the append-only ledger, Constitution invariant #12); **narrative
fields are curated** and are labelled `"source": "curated"` in the JSON. Bucket classification follows a
documented headline-keyword rule (`bucket_source` per row); per-epoch **verdicts** are verbatim and untruncated
from the append-only ledger. Note: ledger text is append-only history — superseded wording inside quoted ledger
records is corrected by later SUPERSEDING/QUALIFICATION records, never edited in place.

## Contents
- **Reports (§12.1–12.10):** CAMPAIGN_FINAL_REPORT, CROSS_EPOCH_EVIDENCE_SYNTHESIS, GRADUATED_FINDINGS,
  STRONG_LEADS_AND_FAILED_REPLICATIONS, METHOD_EXHAUSTION_MAP, INFORMATION_GAIN_AND_BOTTLENECKS,
  PROSPECTIVE_SEALS_AND_FUTURE_TESTS, NEXT_STEPS_AFTER_CAMPAIGN, INTEGRITY_AND_REPRODUCIBILITY.
- **Machine-readable (§13):** CAMPAIGN_FINAL_STATE.json, FINAL_VERDICTS.json, GRADUATED_FINDINGS.json,
  STRONG_LEADS.json, METHOD_EXHAUSTION_MAP.json, PROSPECTIVE_SEALS.json, ARTIFACT_MANIFEST.json.
- **Tables:** EPOCHS_001_TO_FINAL_MASTER_TABLE.csv (one row per epoch), RECONCILIATION_TABLE.csv (leading `#`
  line states exactly what the table does and does not audit).
- **Key adjudication machinery + preregs:** EPOCH-103 (strong-lead), EPOCH-104 (campaign-wide null),
  EPOCH-105 (synthesis) — each with the frozen prereg.md, plan_hash.txt, machinery.py, result.json, AND (for
  E103/E104) the append-only remediation files: prereg_addendum_R.md, plan_hash_R.txt, machinery_R.py,
  result_R.json.
- **Prospective-seal verification:** `seals/FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256` plus the five files it
  references (licence-clean, campaign-derived), laid out at the manifest's relative paths under
  `experiments/linear_a_frontier_72h/`.

## How to verify hashes
- **Whole bundle:** `sha256sum -c BUNDLE_MANIFEST.sha256` from the bundle root (covers every file in the bundle
  except the manifest itself).
- **Closure layer:** `ARTIFACT_MANIFEST.json` holds sha256 of every generated closure file (self-excluded); paths
  are relative to `experiments/linear_a_frontier_72h/` in the branch.
- **Seal:** `sha256sum -c seals/FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256` from the bundle root — the five
  referenced files ship in this bundle at the manifest's paths.

## How to reproduce key results (from the BRANCH repo root, not from this bundle)
- **A-initial adjudication, corrected null (E103R):**
  `python3 experiments/linear_a_frontier_72h/epochs/EPOCH-103/machinery_R.py`
  → REPLICATED_RELATIVE_CONSTRAINT, byte-identical scientific content (fixed seeds). The original E103 run:
  `.../machinery.py` (frozen; its joint maxT null carries the comonotone defect corrected by E103R).
- **Campaign-wide null, bound-based (E104R):**
  `python3 experiments/linear_a_frontier_72h/epochs/EPOCH-104/machinery_R.py`
  → CAMPAIGN_NULL_GATES_CERTIFIED: 1/400 false graduation (CP95 upper 1.18%), ablation 121/400, planted 40/40.
  ~9 min.
- **Closure regeneration (E105):** `python3 experiments/linear_a_frontier_72h/final/generate_closure.py`
  → regenerates all JSON + CSV from the append-only ledger and emits `epochs/EPOCH-105/result.json`.

## Large artifacts outside the bundle
Licensed source material (DĀMOS Linear B, GORILA, SigLA — CC BY-NC-SA / vendor terms) is **excluded** and cannot be
redistributed. The silver corpus derivatives the epochs consume live in the branch under `corpus/silver/` where
licence permits. Per-epoch `data/` outputs and full `reports/` are in the branch (gitignored → committed with
`git add -f`); this audit package carries the closure layer + key epochs, not every intermediate.

## One-line result
No decipherment. One graduated *relative structural* finding (A-initial positional enrichment). Corpus exhausted
within scope; bottleneck = anchor independence. The discipline is certified (E104R, bound-based). This is the
intended insurance outcome.
