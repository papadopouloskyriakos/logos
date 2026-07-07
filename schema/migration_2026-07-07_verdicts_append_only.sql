-- Migration 2026-07-07 — make `verdicts` APPEND-ONLY (Constitution v2.0 Art. XVII).
--
-- Prior behaviour VIOLATED Art. XVII: UNIQUE(plan_hash) forced verdict.py's `ON DUPLICATE KEY UPDATE`
-- to overwrite a prior verdict in place (and re-grade "deleted prior first") — a silent rewrite of a
-- graded, held-out result. Under v2.0 the record is immutable; corrections are APPENDED. This converts
-- verdicts to a slowly-changing append-only ledger: many rows per plan_hash, at most one
-- status='current' (enforced by a virtual UNIQUE key), prior grades preserved as status='superseded'
-- with a lineage pointer; plus a general correction_ledger.
--
-- Apply ONCE on an existing DB (fresh installs get this from schema.sql):
--   ssh -i ~/.ssh/one_key root@nllei01cl01mariadb01 mariadb logos < schema/migration_2026-07-07_verdicts_append_only.sql
-- Requires MariaDB (indexed VIRTUAL generated column). After applying, re-run scripts/verdict.py so any
-- legacy row gets a content hash on its next genuine re-grade, then scripts/family_scores.py.

ALTER TABLE verdicts
  DROP INDEX uq_verdicts_plan,
  ADD COLUMN status ENUM('current','superseded') NOT NULL DEFAULT 'current' AFTER result,
  ADD COLUMN verdict_hash      CHAR(64) NULL AFTER provenance,
  ADD COLUMN supersedes_id     BIGINT UNSIGNED NULL AFTER verdict_hash,
  ADD COLUMN superseded_by_id  BIGINT UNSIGNED NULL AFTER supersedes_id,
  ADD COLUMN correction_type   ENUM('ERRATUM','SUPERSEDING_ANALYSIS','INVALIDATION_NOTICE',
                                    'DEPENDENCY_DISCOVERY','PROTOCOL_DEVIATION','RETRACTION') NULL
             AFTER superseded_by_id,
  ADD COLUMN correction_reason VARCHAR(255) NOT NULL DEFAULT '' AFTER correction_type,
  -- current_key = plan_hash while current, NULL once superseded (write_verdict maintains it). The
  -- UNIQUE index enforces at most ONE current row per plan_hash; NULLs (superseded) are distinct.
  ADD COLUMN current_key CHAR(64) NULL,
  ADD UNIQUE KEY uq_verdicts_current (current_key),
  ADD UNIQUE KEY uq_verdicts_hash (verdict_hash),
  ADD KEY ix_verdicts_plan (plan_hash);

-- Legacy rows are already one-per-plan_hash; ADD COLUMN ... DEFAULT 'current' marks them current and
-- leaves verdict_hash NULL, so the next genuine re-grade APPENDS a superseding row (Art. XVII) rather
-- than matching a placeholder hash. (NULL verdict_hash values coexist under uq_verdicts_hash.)
-- Backfill current_key so the single-current UNIQUE holds for pre-existing rows too:
UPDATE verdicts SET current_key = plan_hash WHERE status = 'current';

CREATE TABLE IF NOT EXISTS correction_ledger (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_type   VARCHAR(32)  NOT NULL,              -- 'verdict' | 'prereg' | 'assumption' | ...
  record_ref    VARCHAR(128) NOT NULL,             -- plan_hash / assumption_id / ...
  correction_type ENUM('ERRATUM','SUPERSEDING_ANALYSIS','INVALIDATION_NOTICE',
                       'DEPENDENCY_DISCOVERY','PROTOCOL_DEVIATION','RETRACTION') NOT NULL,
  original_status VARCHAR(64)  NOT NULL DEFAULT '',
  current_status  VARCHAR(64)  NOT NULL DEFAULT '',
  superseded_by   VARCHAR(128) NOT NULL DEFAULT '',
  reason        VARCHAR(512) NOT NULL DEFAULT '',
  artifact_hash CHAR(64)     NOT NULL DEFAULT '',
  commit_sha    VARCHAR(64)  NOT NULL DEFAULT '',
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_ledger_ref (record_type, record_ref)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
