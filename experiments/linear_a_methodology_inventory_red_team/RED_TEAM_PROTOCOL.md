# Red-team protocol — independent verification of the methodology inventory

Adversarial audit of `experiments/linear_a_methodology_inventory/` (Prompt 1, committed e800b63). Branch
`audit/linear-a-methodology-inventory-red-team` from e800b63 (read-only; P1 report preserved unchanged; not merged).

## Independence-first
1. Built INDEPENDENT_ARTIFACT_INDEX by CONTENT-HASH across ALL 12 worktrees (not P1's dir-ownership mapping):
   2,587 experiment files -> **986 distinct-content** (vs P1's 923). Denominator = the independent 986.
2. Delta = 75 distinct-content artifacts absent from P1's index (basename): 41 .pyc (irrelevant), 10 pdf + 1 srt
   (reference sources), 23 material -> OMITTED_ARTIFACTS.csv.
3. **KEY P1 DEFECT FOUND:** P1's "authoritative worktree" for external_anchors + la_lb_continuity was la-lb-ritual,
   but the OWNING branches (external-anchors 3310e4b 07-07, la-lb-continuity 87b4dea) are NEWER (external_anchors
   57->80 files, la_lb_continuity 67->77). P1 read STALE inherited copies -> candidate omitted method
   FROZEN_POWER_PASS (external anchors) + un-traced continuity result JSONs. Verification agents route to owning
   branches.
4. Fan-out: per-lineage verification agents (independent re-derivation + P1 row verification + numerical trace +
   omission/duplicate/semantics flags) + a cross-cutting verdict-semantics/branch-status pass.
5. Synthesis: ROW_VERIFICATION, OMITTED_METHODS, DUPLICATE_AND_NOVELTY, NUMERICAL_AUDIT, VERDICT_SEMANTICS,
   BRANCH_STATUS_RECONCILIATION, COVERAGE, verified tables, RED_TEAM_FINDINGS, REMAINING_UNCERTAINTIES,
   MASTER_REPORT_VERIFIED. Answer the 13 required questions.

NON-DESTRUCTIVE: no experiments; no verdict-ledger/paper/P1-report edits; read-only over research branches.
