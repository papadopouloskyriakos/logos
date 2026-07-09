# E205 — Palaeographic measurement channel (milestone-2 scope)

**Classification (PRECHECK §4):** A/B EXTENSION, C BLOCKED_DATA, D NEW. Salgarella-2020
homomorphy grades are used as **palaeographic evidence only** — sign-shape continuity, never
phonetic-value identity. Level ceiling: L1 (measurement) / L2 (only if a palaeographic
correction changes a reproducible textual pattern). Governed additionally by
MILESTONE2_CONTROL_ADDENDUM @ 5deec1e.

## Sub-experiments this milestone

### E205-I (identifiability impact of the palaeographic prior; runs on the validated E203 engine)

Three conditions, frozen:
1. **NO_HOMOMORPHY_PRIOR** — baseline systems: {no unary} and {PINS4} on the WP-H domain.
2. **GRADED_PALAEOGRAPHIC_PRIOR** — Salgarella grades as SOFT weights (homomorphic-and-likely-
   homophone base 2.0; homomorphic-only base 1.0 where parseable), CP-SAT soft formulation;
   report near-optimal violation structure, marginals, contracting domains.
3. **HARD_IDENTITY_SENSITIVITY_ONLY** — grades as hard equalities. Explicitly an AGGRESSIVE
   SENSITIVITY arm, never the default model; its pilot outcome (UNSAT_GENERIC 200/200) already
   bounds it.

Compare across conditions: per-sign domain contraction, satisfiability, exact component-wise
model counts, backbones, and downstream structural stability (does any relative/structural
result change under condition 2 vs 1 — checked against the graduated A-initial statistic
recomputed under sign-merge proposals, see E205-A3).

Distinguished vocabulary (binding): sign-shape continuity ≠ sign identity ≠ allography ≠
script genealogy ≠ phonetic-value continuity. The first four never imply the fifth.

### E205-A (allograph/merge-split, bbox + grades; confound-controlled)

- A1: cluster-stability of SigLA bbox geometry per sign class (visual-only), vs context-only
  (co-occurrence) groupings, vs fused — with sign-disjoint and object-disjoint evaluation and
  label-permutation tests (100 permutations, plus-one p).
- A2: agreement of Salgarella grade classes with (i) bbox-geometry clusters, (ii) silver
  editorial sign classes; edition/illustrator sensitivity NOT testable (single drawing source)
  — recorded as a limitation, not silently.
- A3: for the top-k (k=5) most homomorphy-ambiguous signs, MERGE/SPLIT counterfactuals: does
  merging/splitting change (a) the A-initial enrichment statistic, (b) entry-template
  structure? Only a REPRODUCIBLE textual-pattern change graduates E205 to L2.

### E205-B (site/medium attribution; sign-identity-controlled)
Predict site (HT/Khania/Zakros where n≥30 docs with bboxes) from bbox geometry with sign
identity CONTROLLED (per-sign standardization; a model that only sees sign identity must drop
to chance — that null is part of the design). Label-permutation test; site-balanced folds.

### E205-C — remains **BLOCKED_DATA** (stroke/contour/hand imagery absent). BLOCKED.json emitted.
### E205-D (transcription-uncertainty propagation) — deferred to its own prereg if milestone
time allows; otherwise recorded OPEN with design sketch in NEXT steps.

## Decision rules (mechanical)
- E205-I verdicts: PRIOR_CONTRACTS_DOMAINS(non-generic)/PRIOR_GENERIC/PRIOR_INERT, decided by
  comparing contraction under condition 2 vs 200 grade-permutation nulls (permute grades over
  the graded sign set; plus-one p; α=.05 Holm over the two baseline systems).
- E205-A3: L2 graduation ONLY if a merge/split changes a pre-registered statistic (A-initial
  enrichment z, or entry-template rate) by more than its 95% bootstrap band under the original
  inventory, reproducibly across sites (≥2/3).
- E205-B: attribution claim only if accuracy > permutation null (α=.05) AFTER sign-identity
  control; otherwise SITE_SIGNAL_IS_VOCABULARY.

Seeds: master scheme, prefix "E205". Resources: ≤4 nice-15 workers. Data: silver + SigLA bbox
JSONs (decoded, gitignored) + salgarella_2020_grades.json (hashes in data_manifest.sha256).
