-- Migration 2026-07-01 — persist the §E gate outcome as structured columns (P0.1/P0.5).
-- Idempotent-ish: run once on an existing DB created before the gate_verdict columns existed.
-- (Fresh installs get these from schema.sql directly.)
--
-- Rationale: family_scores previously read a family "win" off verdicts.result=='match' (the local
-- L_fake-bar signal), because gate_verdict survived only inside the free-text notes. These columns
-- let the roll-up read the §E outcome directly, so a win is provably gate_verdict='GRADUATE'.

ALTER TABLE verdicts
  ADD COLUMN gate_verdict      ENUM('GRADUATE','REJECT','NULL_PUBLISHED','INCOMPLETE') NULL AFTER result,
  ADD COLUMN gate_version      VARCHAR(16) NOT NULL DEFAULT '' AFTER gate_verdict,
  ADD COLUMN gate_clauses_json JSON NULL AFTER gate_version,
  ADD COLUMN search_log_id     BIGINT UNSIGNED NULL AFTER gate_clauses_json,
  ADD KEY ix_verdicts_gate (gate_verdict);

-- After migrating, regenerate verdicts (verdict.py re-grades from persisted hypotheses) so the new
-- columns are populated under gate-e2 semantics, then re-run family_scores.py.
