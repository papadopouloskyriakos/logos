# Stages E & F — method validation + external-anchor re-audit

## Stage E — `METHOD_VALID_LA_NULL_IS_CORPUS`
The value-recovery machineries demonstrably FIRE on known-script / planted truth while returning null on LA
(verified from committed artifacts) — so the LA null is a property of the corpus's information budget, not a
dead detector:
- **LB morphology** positive control: 0.5625 (9/16 V&C affixes) vs bigram floor 0.3125, `has_morphology_power`=
  true, on DĀMOS 13,562 wordforms → the *same* test is NO_POWER on LA's short words.
- **Metrology / KU-RO**: planted control recovers 0.9 vs 0.22 null (p=0.003); KU-RO=total confirmed by integer
  balance; real LA held-out **fraction** balance = 0.0 (p=1.0). *(Distinct from the campaign's KU-RO integer
  reconciliation control, `kuro_reconciliation.json`: 25% vs 1.47% null = 17×, p=0.0005 — a different test on
  real integer sections. Both valid; both HT-locked.)*
- **Opaque-Linear-B** value recovery works: LB-internal self-persistence 11/11 (0 FP); planted power → 1.0
  (top-1 0.997) at strength 13 — while the real LA→LB distributional channel = **0.0000** held-out hits.
- **Gate calibration**: best-of-100 random-map null false-graduates 3/500 = **0.6%** (CP 95% upper 1.54%).

## Stage F — `NO_NONCIRCULAR_ANCHOR`
Salgarella 2020 (now available) does **not** supply a new non-circular anchor set. Her entire A–B scheme is
the **shape/homomorphy channel** with LB sound values projected backward onto LA — the ≤0.75-capped
circularity the frozen paper already flags (she flags it herself, p.34, p.374 n.2, and does not test values
held-out). Her lexical identifications are the **same** anchors already tested (toponyms pa-i-to / se-to-i-ja
/ su-ki-ri-ta; anthroponyms qa-qa-ru→qa-qa-ro, di-de-ru→di-de-ro, …), deferred to Steele & Meissner 2017
Table 6.3 — the very source behind the Phase-2 census that returned REFUTE. **No anchor class yields ≥3
independent, held-out, non-circular anchors** capable of surviving leave-one-anchor-out. The two preregistered
one-shots (DOIs 21168887, 21173639) are immutable and were not re-run. Salgarella "moves rows, not verdicts."

## Consequence — Stage H is a provable null
Stage D2 established that the corpus's internal distributional/morphological structure is **invariant under
any bijective sign relabeling**. A sign-**value** assignment *is* a relabeling, so **no agnostic search over
internal evidence can inform sign values** — the internal channel is value-blind by construction. Values can
enter only via external anchors (Stage F), which are absent/circular. Therefore an agnostic decipherment
search (Stage H) cannot exceed the end-to-end null; the gate calibration (0.6% false-graduation) bounds any
apparent "system" as noise. Confirmed concretely in `scripts/stage_hj_agnostic_null.py`.
