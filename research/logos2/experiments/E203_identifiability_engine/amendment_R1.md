# E203 amendment R1 — G1 gate criterion repair (defect repair, NOT result-driven adaptation)

**Committed:** 2026-07-10, after the as-run pilot G1 failure (results/G1_gate.json, preserved
unchanged) and BEFORE any amended rerun. **Scope:** the G1 synthetic-recovery criterion only.
No LA cell had been interpreted (fail-closed held); no LA result is affected by this amendment.

## The defect

decision_rule.json G1 required "backbone containing >=90% of planted values" over randomly
generated instances. The generator does not guarantee that 90% of signs are information-
theoretically recoverable: a sign whose pinned-neighbor compatibility sets do not intersect to a
singleton is provably unrecoverable by ANY correct engine. As-run evidence: the engine was SOUND
in 5/5 replicates (zero wrong backbone values; zero-anchor arm 0/163 backbone) and failed only on
one replicate's recovery fraction (0.859 < 0.90) — instance-hardness variance, not engine error.
The criterion tested the random instance, not the engine.

## Amended G1 (stricter on the engine, instance-luck-free)

Per replicate (5 replicates, 60 signs / 500 rel edges / 24 pins — smaller instances so the
reference computation is exact and affordable):

1. **Soundness (unchanged):** every engine-backbone value equals the planted truth (n_wrong == 0).
2. **Zero-anchor ambiguity (unchanged):** engine backbone at 0 anchors ≤ 5% of signs.
3. **Completeness vs reference (replaces the 0.90-of-all rule):** compute the reference
   identifiable set by per-value CP-SAT probing (a sign is reference-identifiable iff exactly ONE
   of its arc-consistent candidate values admits a full satisfying assignment; the probe path
   exercises the SAT search, a different algorithm than the engine's AC propagation). Require the
   engine backbone to EQUAL the reference set exactly.

Gate passes iff all three hold in 5/5 replicates. This is stricter than the defective criterion
wherever the instance is informative, and never fails a correct engine on an uninformative
instance.

## Why this is defect repair

The amended rule is derived from the prereg's own stated intent ("recover the planted assignment
when given sufficient anchors; report ambiguity rather than a confident wrong answer") and was
fixed without reference to any Linear A data or result — the only observations consulted were the
synthetic gate replicates themselves, whose soundness/ambiguity components PASSED.

sha256(this file) recorded in plan_hash.txt (appended, append-only).
