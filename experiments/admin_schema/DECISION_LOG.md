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

- **Stage 3 — source / license audit:** DĀMOS (LB, in repo) sufficient as backbone. **Key decision:** the
  blinding mechanism = de-phoneticise LB at ingest — map each syllabogram to its opaque graphic sign-ID
  (Unicode B-number, stripping the phonetic value like `QE`); transliteration/lemma/Greek/gloss → EVAL_ONLY.
  LA (silver + SigLA) is natively opaque (undeciphered). Transfer-critical primary feature set = opaque sign
  identity + structure/position + logograms + numerals/fractions + support + site + recurrence + damage.
  **Excluded (LB-only sensitivity):** scribal hand, fine chronology, fine layout. **Flagged top transfer
  risk:** LA↔LB sign-inventory non-homomorphy → represent signs within-script-opaque + AB-shared bridge only.
  No licensing/repro blocker (LiBER/PA-I-TO TO_AUDIT but LB-only enrichment). Artifacts:
  `reports/LINEAR_B_SOURCE_AUDIT.md`, `reports/LINEAR_A_FEATURE_COMPATIBILITY.md`,
  `reports/LICENSE_AND_REPRODUCIBILITY.md`. Commit: _(this commit)_.

## 2026-07-07

- **Stage 4 start.** Starting commit `4526c5c` (branch `research/blinded-admin-schema-induction`, clean;
  `main@f6a5682`, paper/runtime/CSA + completed branches untouched; 6 worktrees).
- **Stage 4 — canonical transferable document graph.** DĀMOS → de-phoneticised heterogeneous graph:
  every syllabogram/logogram/metrogram/qualifier → opaque graphic ID (`B_SIGN/B_LOGO/B_MEAS/B_QUAL_NNN`);
  id↔sound maps EVAL-ONLY. LA (silver) instantiated in the SAME schema (dry-run, separate `A_SIGN` vocab,
  no semantic output). **Hashes:** schema `628f49fb`, lb_graph `f040720e`, la_graph `d79b3fe4`,
  feature_transferability `<see manifest>`. Counts: LB 5,799 / LA 1,341 graphs; 89 syll / 155 logo / 17 meas
  vocab; 1,606 repeated forms + 1,162 joins grouped; 12,751 uncertain nodes. Transferability: 22
  TRANSFERABLE / 3 AB-shared / 1 LB-only / 3 EXCLUDED. **All 4 acceptance tests pass** (schema, determinism,
  no-semantic-fields incl. sound-value leak, feature-transferability). **Finding:** DĀMOS `vasewriter`
  empty in this dump → SCRIBE channel empty; S4 leave-one-scribe-out needs another field or is NO_POWER.
  Model-visible graphs + eval-only key gitignored (regenerable; eval-only never redistributed). Commit: _(this)_.
- **Stage 5 — ontology review DRAFT ONLY** generated under `reviews/stage5/` (UNCOMMITTED, NOT FROZEN).
  Awaiting `STAGE5_ONTOLOGY_APPROVED`.

<!-- append: stage, commit sha, manifest hashes, key decision -->
