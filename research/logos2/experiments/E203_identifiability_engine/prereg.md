# E203 — Exact Linear A identifiability engine (CP-SAT / SMT / counting)

**Classification (PRECHECK §4):** NEW formalism (first industrial-solver formalization in this
programme; all prior solvers were custom numpy), EXTENSION of the priced identifiability question.
**Level ceiling:** L0–L2 (the primary scientific result is an identifiability MAP, not a
decipherment). **Status at prereg:** committed before any execution.

## Question

Under explicitly-modularized evidence, how large is the space of surviving sign-value solution
families for Linear A, which constraints actually shrink it, what (if anything) is unsatisfiable,
and what is the smallest hypothetical observation that would distinguish the leading families?

## Inherited acceptance bar (from E200; binding)

1. **Comparability:** on the shared 67-cell CV domain used by anchor-lattice WP-H, the engine's
   residual-ambiguity estimate must be reported side-by-side with WP-H's (~10^63.4 operational;
   ≥10^270 gauge-quotient lower bound). Divergence is a finding to explain, not to hide.
2. **UNSAT adjudication:** any UNSAT discovery must be adjudicated against ≥200 matched random
   pin-sets (the WP-N protocol). If matched random constraint-sets are also UNSAT at comparable
   rates, the verdict is UNSAT_GENERIC, not a discovery.
3. **Synthetic recovery gate (fail-closed):** on planted ground truth the engine must (a) recover
   the planted assignment when given sufficient anchors, (b) report ambiguity (NOT a confident
   wrong answer) at zero anchors. Engine failing this gate ⇒ ENGINE_NOT_VALIDATED and no LA
   results are interpreted.

## Design (frozen)

**Variables.** One integer variable per sign in the working inventory, ranging over a value domain
of CV cells (pilot: the WP-H-comparable domain of 13 consonants × 5 vowels + 2 series cells = 67
values; full: the 92-sign conservative syllabary inventory mapped to the same cell domain).
One-to-one is NOT assumed: homophony (two signs, one value) is permitted by default; polyphony is
modelled as an optional relaxation module (a second value slot for a declared subset); null
correspondences via an explicit NONE value.

**Constraint modules** (each ON/OFF; every run records the active set; provenance per module):
- `M_HOMOMORPHY` — A–B sign-shape correspondence with uncertainty, weighted by the Salgarella-2020
  grade file (57 signs; soft constraints: grade-weighted penalties, NOT hard equalities).
- `M_CONTINUITY_HYP` — LB value import as an explicitly UNLICENSED HYPOTHESIS module (used only for
  conditional maps "IF LA≈LB values THEN …"; never asserted; licence state NOT_EARNED recorded in
  every output that uses it).
- `M_STRUCTURE` — the graduated relative constraints (A-initial enrichment; KU-RO ledger-terminal;
  libation order) encoded as positional co-occurrence constraints. Prior work says these are
  value-blind (relabeling-invariant); their measured contribution here TESTS that result and is
  expected ≈ 0 bits.
- `M_NUMERAL` — numeral/fraction adjacency and document-grammar constraints (value-blind expected).
- `M_PINS` — the four cross-script pins (I, RI, SU, TO), each one-toponym-deep, as individually
  toggleable anchor modules with a declared error probability (pin-wrong scenarios are part of the
  sensitivity grid).
- `M_PHONOTACTICS` — candidate-language phonotactic templates as OPTIONAL modules, off by default
  (they import unproven assumptions; used only in clearly-labelled conditional maps).

**Computations** (in order):
1. Exact satisfiability + unsat cores (CP-SAT primary; Z3 for core extraction cross-check).
2. Solution counting: exact enumeration when the projected count < 10^6; otherwise (a) analytic
   domain-product upper bound, (b) sequential importance sampling lower/upper (WP-H-comparable),
   (c) XOR-hash approximate counting with CP-SAT as oracle (ApproxMC-style, m XOR constraints,
   repetition r=10, δ-band reported). All three reported when run; disagreement >2 orders of
   magnitude is a defect to investigate.
3. Backbone extraction (assignments common to all solutions) + equivalence-class structure
   (value-permutation gauge group; classes reported modulo the gauge, matching WP-H's quotient).
4. Sensitivity: leave-one-module-out and leave-one-constraint-out ambiguity deltas (in log10).
5. Distinguishing observation: over a declared family of hypothetical observations (a new
   inscription containing sign s at slot k of a known formula; a new pin of type t), rank by
   expected log10 ambiguity reduction — the acquisition ranking that feeds E202-recast.

**Seeds.** master 1336530913; per-run seed = sha256(master ‖ 'E203' ‖ cell ‖ replicate) low 31 bits.
SIS and XOR draws use per-replicate generators; no global RNG.

**Resources.** Pilot ≤2 workers nice-15, ≤2 GiB, per-solve timeout 300 s, cells checkpointed.
Full grid deferred until the CSA sweep completes unless pilot cost measurements show ≤6-worker
feasibility.

## Committed pilot (exploratory) vs full run (confirmatory)

- **Pilot P1 (exploratory):** synthetic-recovery gate + WP-H-domain comparability + the marginal
  module path ∅ → +M_STRUCTURE → +M_NUMERAL → +M_HOMOMORPHY → +M_PINS (5 runs) with counting
  method (a)+(b), XOR method on the two smallest.
- **Full F1 (confirmatory, own amendment if design changes):** the 2^6 module grid × pin-error
  scenarios × polyphony on/off, all three counters where feasible, full sensitivity + acquisition
  ranking.

## Verdict vocabulary (mechanical; see decision_rule.json)

ENGINE_VALIDATED / ENGINE_NOT_VALIDATED · IDENTIFIABILITY_MAP_{COMPLETE,PARTIAL} ·
UNSAT_GENERIC / UNSAT_SPECIFIC(module-set) · AMBIGUITY_CONSISTENT_WITH_PRIOR /
AMBIGUITY_DIVERGES(explained|unexplained). No verdict asserts any phonetic value; outputs using
M_CONTINUITY_HYP or M_PHONOTACTICS are conditional maps and are labelled as such in every artifact.

## Forbidden

No phonetic value, reading, language identification, or translation claim at any outcome. No
one-to-one mapping assumption without a justification module. No seal inspection. No unlabelled
use of unlicensed value-transfer assumptions.
