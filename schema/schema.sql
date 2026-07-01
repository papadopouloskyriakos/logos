-- logos schema — foundational (v0). Galera-safe: every table has an explicit PRIMARY KEY.
-- Apply via: ssh -i ~/.ssh/one_key root@nllei01cl01mariadb01 mariadb logos < schema.sql
-- (the runner has no mysql client; ProxySQL's cert is untrusted from lab hosts — agora pattern)

SET NAMES utf8mb4;

-- the corpus index (provenance + stats per inscription; raw signs live in DuckDB silver/gold)
CREATE TABLE IF NOT EXISTS inscriptions (
  id            VARCHAR(32) NOT NULL,
  site          VARCHAR(128) NOT NULL DEFAULT '',
  context       VARCHAR(32)  NOT NULL DEFAULT '',   -- e.g. LMIB (dating band)
  support       VARCHAR(64)  NOT NULL DEFAULT '',   -- Tablet / Seal / etc.
  n_signs       INT UNSIGNED NOT NULL DEFAULT 0,
  source        VARCHAR(64)  NOT NULL DEFAULT 'lineara',  -- bronze provenance
  as_of         DATE NOT NULL DEFAULT (CURRENT_DATE),
  PRIMARY KEY (id),
  KEY ix_inscriptions_site (site)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- sign inventory (the V in the unicity equation) + observed frequency
CREATE TABLE IF NOT EXISTS signs (
  sign          VARCHAR(16) NOT NULL,
  frequency     INT UNSIGNED NOT NULL DEFAULT 0,
  is_logogram   TINYINT(1) NOT NULL DEFAULT 0,
  phonetic_value VARCHAR(32) DEFAULT NULL,          -- proposed (always a hypothesis)
  notes         VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (sign)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- the PREDICT output: a hash-keyed, falsifiable hypothesis (invariant 1). The LLM/model
-- never grades itself (invariant 2); verdicts live in `verdicts`.
CREATE TABLE IF NOT EXISTS hypotheses (
  plan_hash     CHAR(64) NOT NULL,                  -- sha256(canonical body)
  family        VARCHAR(48) NOT NULL,               -- semitic / anatolian / tyrrenian / ie / isolate
  claim_type    VARCHAR(32) NOT NULL,               -- sign_map / lexeme / grammar / reading
  body          JSON NOT NULL,                      -- the canonical, hashed prediction
  prediction    JSON NOT NULL,                      -- falsifiable held-out implication
  confidence    DECIMAL(4,3) NOT NULL DEFAULT 0.000, -- <=0.750 if model-assisted (invariant 5)
  as_of         DATE NOT NULL DEFAULT (CURRENT_DATE),
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (plan_hash),
  KEY ix_hypotheses_family (family)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- the SOLE writer is scripts/verdict.py (invariant 2). Mechanical, held-out.
CREATE TABLE IF NOT EXISTS verdicts (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  plan_hash     CHAR(64) NOT NULL,
  result        ENUM('match','partial','deviation','pending') NOT NULL DEFAULT 'pending',
  -- P0.1: the §E gate outcome, persisted STRUCTURED (not only inside `notes`). A family win is
  -- gate_verdict='GRADUATE'; result='match' means only the local L_fake bar was cleared.
  gate_verdict      ENUM('GRADUATE','REJECT','NULL_PUBLISHED','INCOMPLETE') NULL,
  gate_version      VARCHAR(16) NOT NULL DEFAULT '',   -- §E gate semantics version
  gate_clauses_json JSON NULL,                         -- per-clause §E gate booleans
  search_log_id     BIGINT UNSIGNED NULL,              -- the instrumented SearchLog behind N_eff
  held_out_site VARCHAR(128) NOT NULL DEFAULT '',
  accuracy      DECIMAL(6,3) NULL,                  -- held-out read accuracy
  brier         DECIMAL(6,3) NULL,
  bench_return  DECIMAL(8,3) NULL,                  -- not used in v0; reserved
  notes         VARCHAR(255) NOT NULL DEFAULT '',
  provenance    VARCHAR(64) NOT NULL DEFAULT '',    -- code SHA
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_verdicts_plan (plan_hash),
  KEY ix_verdicts_result (result),
  KEY ix_verdicts_gate (gate_verdict)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- capped signals (JEPA / LLM / cognate-matchers) feeding the hypothesis layer (invariant 5)
CREATE TABLE IF NOT EXISTS signals (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  source        VARCHAR(48) NOT NULL,               -- jepa-seq / jepa-cross / llm-thesis / cognate
  ref           VARCHAR(64) NOT NULL,               -- sign / sign-sequence id
  payload       JSON NOT NULL,
  confidence    DECIMAL(4,3) NOT NULL,              -- <=0.750 enforced by convention
  as_of         DATE NOT NULL DEFAULT (CURRENT_DATE),
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_signals_source (source, as_of)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- per-family scorecard with the López de Prado corrections (reused from agora_stats)
CREATE TABLE IF NOT EXISTS family_scores (
  family        VARCHAR(48) NOT NULL,
  n_predictions INT UNSIGNED NOT NULL DEFAULT 0,
  win_rate      DECIMAL(5,3) NULL,
  held_out_acc  DECIMAL(6,3) NULL,
  calibration_gap DECIMAL(5,3) NULL,
  dsr           DECIMAL(5,3) NULL,                  -- Deflated Sharpe on effective-n
  n_trials      INT UNSIGNED NOT NULL DEFAULT 0,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (family)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- graduation gates: a family graduates only if DSR>=0.95 AND params <= info floor (invariant 3/7)
CREATE TABLE IF NOT EXISTS graduation_state (
  family        VARCHAR(48) NOT NULL,
  gate          VARCHAR(8) NOT NULL DEFAULT 'G0',   -- G0..G4
  frozen        TINYINT(1) NOT NULL DEFAULT 0,
  reason        VARCHAR(255) NOT NULL DEFAULT '',
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (family)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
