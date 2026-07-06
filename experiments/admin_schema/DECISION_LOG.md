# DECISION LOG — Blinded Admin Schema Induction

Chronological record of decisions, commits, and manifest hashes (§XVII). Newest last.

## 2026-07-06

- **Programme opened.** External phonetic-anchor programme closed (last verdict:
  `research/egyptian-calibration-gate@dfa291e` — Cretan one-shot honest interpretation TRIVIAL/NULL).
  Pivot to structure-first semantic role/schema induction, blinded LB benchmark + LA transfer gate.
- **Isolation:** worktree `/home/claude-runner/gitlab/n8n/logos-admin-schema`, branch
  `research/blinded-admin-schema-induction`, forked from `main@f6a5682`. Completed research branches
  recorded in the charter and left untouched; `main`/`paper/`/`runtime/`(CSA) not modified.
- **Stage 1 — scaffold + ledger:** created directory scaffold + PROJECT_CHARTER / STATUS / DECISION_LOG
  / SOURCE_REGISTER. Commit: _(this commit)_.

- **Stage 2 — prior-art / novelty audit:** workflow `wf_dcb6a179-216` (3/4 clusters + synthesis; the
  novelty-boundary agent failed StructuredOutput → backfilled by hand). Audited 20 works. Verdict
  **`NOVELTY_SUPPORTED`** (combinatorial): 0/20 satisfy the defining conjunction (blinding-as-ablation on a
  *decipherable* script + structure-only role/schema + learned cross-script transfer gate + held-out by
  site/scribe/family). Nearest neighbour = Born, Monroe, Kelley & Sarkar 2025 (Proto-Elamite numeral
  disambiguation) — structure-only + uncertainty + held-out, but numeric, no cross-script gate, no blinding.
  Honest residual risk: primitives individually precedented; novelty is combinatorial and not a gate on the
  science. Artifacts: `reports/PRIOR_ART_MATRIX.md`, `reports/NOVELTY_BOUNDARY.md`,
  `data/prior_art/prior_art_register.csv` (20 rows), `data/prior_art/search_receipts/receipts.md`.
  Commit: _(this commit)_.

<!-- append: stage, commit sha, manifest hashes, key decision -->
