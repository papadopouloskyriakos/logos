# EPOCH-008 ADDENDUM-1 — held-out confirmation of the amended (v2) pipeline

**Frozen:** 2026-07-08, AFTER the main run and BEFORE any fresh-sign data is touched.
**Context:** Under the main prereg (sha256 67ea9ac4…e6a2) the frozen v1 pipeline returned
STROKE_RECOVERY_INFEASIBLE (extraction 3/10; anti-aliasing specks in the alpha-channel trace
renders blow the n_components ≤ 3 rule). A documented post-hoc amendment (AMENDMENT-A:
despeckle = drop components < max(4 px, 2% of largest) + 3×3 binary closing) reached
FEASIBLE-grade numbers (8/10; epig MRR 0.307, p 0.0105; aspect 0.018). Because AMENDMENT-A
was adopted after seeing v1 failures, it is hypothesis-generating (Art. XII). This addendum
confirms or refutes it on signs never used during debugging.

## Frozen procedure

- Frame: identical eligibility frame as the main run (57 AB-shared, 20 A-only eligible).
- Fresh sample: `random.Random(20260708 + 2).sample(sorted(eligible − main_picks), 5)`
  for each group → 10 fresh signs (zero overlap with DA,U,RA,PI,DE,*321,*333,*310,*301,*309B).
- Attestation choice, download etiquette, bbox-mode rule (geometric-validity first),
  alpha-ink decoding: identical to the main run's final script
  (`scripts/epoch008_stroke_pilot.py` at the state that produced result.json).
- Pipeline: **v2 exactly** (binarize → despeckle → skeleton_graph). No further changes of
  any kind after this freeze; any failure is reported as-is (fail closed).
- Calibration: the 5 fresh AB-shared signs vs the same 74-sign LB font gallery, stroke
  features vs aspect baseline, 20,000-draw permutation null (rng seed 20260708+3).

## Frozen mechanical outcome

- **AMENDMENT_CONFIRMED** iff extraction_ok_v2 ≥ 8/10 ∧ epig stroke MRR p < 0.05 ∧
  epig stroke MRR > epig aspect MRR.
- **AMENDMENT_PARTIAL** iff extraction_ok_v2 ≥ 6/10 ∧ ¬CONFIRMED.
- **AMENDMENT_REFUTED** otherwise.
- Epoch verdict mapping: CONFIRMED ⇒ epoch verdict STROKE_RECOVERY_FEASIBLE
  (route: SigLA trace renders; v1 INFEASIBLE + AMENDMENT-A confirmed held-out, both recorded);
  PARTIAL ⇒ STROKE_RECOVERY_PARTIAL; REFUTED ⇒ STROKE_RECOVERY_INFEASIBLE stands.
