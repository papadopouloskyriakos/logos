# TASK J — Conditional Language-Family Gate

**Campaign:** research/linear-a-anchor-lattice · **Constitution:** v2.2 · **Date:** 2026-07-08
**Script:** `scripts/j_language_gate.py` (deterministic arithmetic over Task-H artifacts; all
numbers below are printed by the script — Invariant 12).
**Artifact:** `data/candidates/j_gate_decision.json`.

**Stage header (Art. XXII):** articles_triggered = V (claim layers), VII (search receipt: the
only search performed is the 3-criterion gate below; no language hypothesis was formed or
scored), VIII (effective_n), XI/XII (non-circularity), XV (transfer licences), XVII
(append-only). Gates consumed: H `JOINT_INFERENCE_NULL` (3/3 solvers), H random-anchor null
`REAL_BELOW_NULL`. Assumptions: none new; inherits C1 (lattice complete) and the recorded
circularity of META_CONTINUITY_LA_eq_LB for values.

## Verdict

**`J_NOT_AUTHORIZED`** — the language-family tournament is NOT run.

## The rule

Languages are tested only after the lattice produces **nontrivial sign constraints**, defined
mechanically as all of:

- **G1** — real A-only value-entropy reduction exceeds the random-anchor null (95th pct);
- **G2** — the reduction survives in the **licensed** state S0 (ρ_META = 0, i.e. without the
  unearned META_CONTINUITY licence), with ≥ 1 A-only sign above 0.1 bit;
- **G3** — at least one unconditional (non-continuity-derived) A-only pin exists.

Rationale: a language test scored against a lattice that constrains nothing is a pure
multiple-testing machine (Invariant 8 — the "English is Semitic" failure mode); a language test
scored against continuity-pinned values is not a Linear A test at all, it is a Linear B test
run through the unearned META_CONTINUITY licence (Art. XV; LANGUAGE_ID licence NOT_EARNED,
`governance/transfer_licences.json`).

## Mechanical evaluation (from `data/candidates/h_*.json`)

| Criterion | Value | Threshold | Pass |
|---|---|---|---|
| G1: real A-only mean reduction | **0.000 bits** | > null p95 = 0.0381 bits (null mean 0.0316, p5 0.0228) | **NO** |
| G1 tail probability | p(null ≤ real) = **0.000** — real is *strictly below* every null draw (`REAL_BELOW_NULL`) | — | **NO** |
| G2: S0 licensed-state A-only reduction | **0.00001 bits** (MC noise); signs > 0.1 bit = **0** | ≥ 1 sign > 0.1 bit | **NO** |
| G3: A-only signs with a parseable pin | **0** (the single A-only pin `*49` is vacuous — its "value" is its own label) | ≥ 1 | **NO** |

**0/3 criteria pass.** The only nonzero reduction anywhere in the system is 0.131 bits per
*pinned* (AB-shared/logogram) sign under S2 — conditional on META_CONTINUITY_LA_eq_LB, a
licence that is NOT_EARNED and whose lattice-internal Bayes factor is exactly 1 (the lattice
contains no evidence for its own value channel; H §1). Supporting negatives: joint solution
space ≥ 10^270 equivalence classes after gauge quotient; continuity-pins × LA-substitution
UNSAT (15/24 pairs); rel channel at chance (p = 0.252).

## Consequence

- **No language tournament is run in this campaign.** Any tournament outcome would be
  uninterpretable: with 0 bits of sign constraint, every candidate family fits the unconstrained
  system equally (≥ 10^270 ways), so any "match" is pure selection — parameters ≫ information
  (Invariant 7).
- **Prior results stand and are not re-litigated:** the Foundry campaign's 6 candidate families
  are `AT_END_TO_END_NULL` (branch `research/linear-a-decipherment-foundry`); the Di Mino
  Semitic chain is `REJECT` (branch `research/di-mino-301-exact-audit`). No do-not-repeat rerun
  (Art. XVII).
- **No preregistered tournament design is written** — the rule makes the design conditional on
  authorization, which was not granted. Re-opening J requires a lattice state where G1–G3 pass
  from artifacts (e.g. an *earned* continuity licence via held-out calibration, or new A-only
  anchors of distinct lineage — G surface says abs ≥ 0.90 needs 12×8-slot distinct-lineage
  anchors; current dependency-collapsed independent anchors = 0).

**Claim-layer statement (Art. V):** this stage makes no claim above L2/L3; L8 (language-id)
remains untested-by-design, not refuted-here.

**Compliance (Art. XXII):** verdict computed mechanically from committed H artifacts; no model
graded its own outcome; no licence changed; record appended, nothing deleted.
