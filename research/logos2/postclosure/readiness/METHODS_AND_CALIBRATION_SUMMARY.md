# Methods & calibration summary (LOGOS-2)

**Governance.** Constitution v2.3: preregistration frozen before execution (commit-hashed);
amendments are separate committed files distinguishing defect repair from result-driven
adaptation; append-only records; claim layers L0–L9 with wording capped at the earned
layer; all transfer licences NOT_EARNED.

**Determinism.** Master seed 1336530913; per-run seeds sha256(master|exp|cell|fold|rep);
no inherited global RNG. All counts script-generated.

**Instruments and their calibration status.**
- *Exact identifiability engine* (CP-SAT + component-decomposition exact counting): G1
  soundness gate 5/5 against reference backbones after one defect-repair amendment; UNSAT
  findings always adjudicated against 200 matched nulls before any wording.
- *Historical-replay harness* (E201): false-graduation calibration 0/200 with the full
  frozen pipeline including abstention; exact Clopper–Pearson 95% upper 1.49% ≤ 2% target.
  Dataset-inherent cognate-identity leakage measured (34.4% on Ugaritic–Hebrew) and
  adjudicated before scoring.
- *Dual-parser double-entry extraction* (E204R2): two independent parser architectures
  (HTML tree vs streaming FSM); conjunctive ≥98% agreement gate per field; measured .9995
  overall on 1,385 records; failed attempts preserved as blocked with named defect classes.
- *Selection-aware nulls everywhere*: metrology nulls re-run the ENTIRE soft pipeline per
  replicate; onomastic canaries are frequency-matched fabrications plus shuffled-name
  medians under Holm correction; detector power qualified by replay (0.905 ≥ 0.60) BEFORE
  reading any confirmatory result.
- *Verifier battery* (E214): banned-wording sweep, frozen status vocabulary, freeze-hash
  integrity with append-only errata, independence-graph shape, as-run preservation, seal
  verification WITHOUT opening. PASS required at closure; passing.

**Interpretation caps.** LLMs and retrieval are structurally excluded from verdicts
(capped signals; RAG classified NOT_A_CHANNEL); verdicts are computed mechanically from
artifacts; a hypothesis that fails never auto-resolves.
