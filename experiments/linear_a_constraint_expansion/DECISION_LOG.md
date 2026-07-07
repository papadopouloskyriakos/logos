# DECISION LOG

## 2026-07-07
- Campaign opened from main@6fd4f20 under Constitution v2.2. Isolation + append-only ledger verified; test
  baseline 411 passed. Offensive mandate: seek value-informative constraints, not re-run closed nulls.
- **Stage A `A_REOPENED`.** Recomputed the identifiability budget from signs_ontology + the corpus's own
  inventories. Prior `259>212` is a category error (259 = all diplomatic stream tokens; a reading needs the
  syllabary = 88-92 / 123 families / 72 A-only). Corrected: 92 params < 212 STRUCTURAL constraints (ratio
  0.43, favourable) but only ~2 VALUE-INFORMATIVE constraints (46× deficit). Underdetermination cause =
  constraint informativeness at the value layer, not count. Reopen target = value-informative constraints for
  ~92 syllabic parameters. Commit: _(this)_.
- **Stage B `ADVANCES` (representation), no value gain.** 5-agent forensics (wf_da6d35c8). Confirms syllabary=92
  (259 = 108 ligatures + 13 damage + logograms). SigLA not independent (same GORILA lineage); AB value-class
  CONTESTED (10 signs flip → value channel weaker than assumed). effective_n: 1242 objects / 565 usable lexical.
  Cleaned phonetic channel (scripts/stage_b_clean_representation.py): 819/3147 word tokens non-phonetic → 944
  clean wordform types for Stage D. Recovered channels: support-invariance (H(support|site)=1.23), accounting
  (blocked on notation typing), findspot (Younger bronze). Data-hygiene: subscript key normalization fixed.
  Commit: _(this)_. Checkpoint 1 written.
