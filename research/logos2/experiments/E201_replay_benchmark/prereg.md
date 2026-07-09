# E201 — Historical decipherment replay benchmark

**Classification (PRECHECK §4):** EXTENSION — (i) fills the named open defect in the published
sufficiency record (the LB/Cypriot 600–700-word cells were endpoint clamps, never measured; the
RUNNING CSA sweep delivers the measurements ~2026-07-13 and this experiment consumes them, it does
NOT re-run them); (ii) adds the genuinely-new **process-replay** leg (would this programme's own
graduation gate have accepted the historical decipherments at their actual evidence levels, and
rejected the famous failures?). A bare re-run of known-answer recovery would be DUPLICATE of the
LIN-14 instruments and is excluded. **Level ceiling:** L0 (benchmark tooling + calibration).
**Status at prereg:** committed before any execution.

## Datasets (feasibility-classified at preflight)

Available in-repo (licence-tracked, `DATA_INVENTORY.csv`): Linear B→Greek (+names variant),
Cypriot→Greek, Ugaritic→Hebrew (noiseless + noisy), Phoenician→Ugaritic, Luvian→Hittite (.cog
files; Tamburini/NeuroDecipher lineages). **Old Persian, Carian, Meroitic, Iberian: BLOCKED_DATA**
at prereg (no in-repo dataset; any later acquisition requires a licence-checked, citable source
and an amendment). Faithfulness caveat recorded per dataset: these are cognate-pair lists, not
full corpora — every result is explicitly "on this dataset's approximation of the historical
situation" and never "historical reconstruction".

## Design (frozen)

**Harness.** One driver (`harness.py`) exposing, per dataset: (a) value-hiding + label-hiding;
(b) corpus-size regimes matched to LA scale (distinct-unit counts bracketing 600–700, subject to
each dataset's n_full ceiling — datasets whose FULL size is below LA scale, e.g. Luvian–Hittite
n=59 and Phoenician–Ugaritic n=105, are labelled SCALE_UNREACHABLE and used only for full-size
calibration, never extrapolated: the E200-audited clamping defect is the anti-pattern);
(c) segmentation-quality degradation (oracle / noisy p∈{0.1,0.2} boundary flips / none);
(d) incremental evidence ladders: distribution-only → +formula boundaries → +semantic classes →
+1 name → +k names (k∈{3,5,10}) → +related-language corpus → +bilingual fragment.

**Recovery model under test (pilot):** the anchor-constrained assignment solver family already
validated in-repo (deterministic Hungarian-EM known-answer machinery, LIN-14 lineage) PLUS the
E203 engine as a second, independent formalism where feasible. New models enter only via this
harness's gate (below).

**Metrics per cell:** sign-value recovery (exact + value-class ARI), name/cognate retrieval
(MRR), calibration (reliability of the model's own confidence), abstention correctness on
insufficient evidence, number of surviving equivalent solutions (via E203 where wired), false
graduation on controls.

**Negative controls (every dataset, every ladder rung):** shuffled sign inventory; unrelated
target language (wrong .cog pairing); synthetic isolate matched for length+frequency (generator
seeded per cell); corrupted anchors (f_wrong ∈ {0.1, 0.3}); duplicated/leaked names (leak
detector must fire).

**Process-replay leg (new):** encode the EVIDENCE LEVEL available to (a) Ventris 1952 (Linear B:
~5 toponym anchors + internal grids + Kober triplets analogue), (b) the Ugaritic decipherment
(bilingual-adjacent + tiny alphabet), and (c) two known failure cases (Gordon's Eteocretan-Semitic
analogue; a random-map "decipherment") as evidence-ladder configurations of THIS harness, then ask
mechanically: does the programme's graduation gate (two channels + held-out prediction + canaries
+ multiplicity) GRADUATE the true cases and REFUSE the failures? Output is a calibration statement
about the GATE, not about history; dataset approximation caveats attach.

**Seeds:** master 1336530913, per-cell as in RESOURCE_BUDGET.json. **Resources:** pilot ≤4
workers nice-15; per-cell timeout 600 s; checkpoint per cell; failed cells never kill the harness.

## Gate (mechanical; decision_rule.json)

A decipherment model is PROMOTED to any Linear A confirmatory use only if, on ≥2 datasets:
recovery at full evidence ≥ the dataset's preregistered threshold (LB→Greek ≥0.5 exact at
full-size; Ugaritic→Hebrew ≥0.6) AND abstention/no-graduation on ALL negative controls (0/40
false graduations across the control battery; CP95 upper bound reported). Otherwise
NOT_PROMOTED. The harness itself graduates at L0 regardless.

## Pilot (exploratory) vs confirmatory

Pilot P1: Ugaritic→Hebrew (noiseless) + Cypriot→Greek small-regime ladder + full control battery
at reduced replication (n=5/control) + the process-replay ENCODING (no scoring). Confirmatory F1
(after the CSA sweep lands the at-scale LB/Cypriot cells): full ladders at LA scale + process-
replay scoring + promotion decisions.

## Forbidden

No claim that any historical situation is "reconstructed"; no promotion of any model that has not
passed the gate; no LA data loaded by this experiment at all (LA enters only via E203's separate
prereg); no reuse of a control's data in its matched real cell (leakage tests in tests/).
