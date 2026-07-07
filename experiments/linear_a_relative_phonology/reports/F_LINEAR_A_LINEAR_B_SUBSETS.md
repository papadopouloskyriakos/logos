# F_LINEAR_A_LINEAR_B_SUBSETS — evidence-graded LA↔LB correspondence subsets

**Task F4-A** · Constitution v2.2 (Art. XII no-grade-by-creating-rule, Art. XV transfer licences) ·
seed 20260708 · source `crossscript_gate/anchors.csv` (59 shared-AB correspondences) ·
script `scripts/f4_loso_relative_class.py` → `data/F4_loso.json`.

Articles triggered: XII (LB values grade only, never an input), XV (no licence earned; SEMANTIC+
NOT_AUTHORIZED). Non-circular gate: `conventional_value` is used ONLY to define subset membership by
the *evidence channel* and to grade held-out predictions — never as a distributional model input.

## Purpose

Partition the 59 LA↔LB correspondences by which **evidence channel** is strongest, so F4-B (leave-one-
sign-out) can ask whether a *distributional* correspondence recovers anything the strong channel does
not already assume. **LB values are HYPOTHESES here**, not facts: each subset is "the signs on which
channel X is confident", and the whole point of F4-B/D is to test those hypotheses against held-out and
value-free structure.

## Channels and thresholds

| channel | field in `anchors.csv` | "high" criterion |
|---|---|---|
| shape | `homomorphy_grade` (Salgarella 2020) | grade = **homophone** (dark-blue cell) |
| paleography / scholarly | `cypriot_stable` (Steele & Meissner 2017) | = **true** (the high-certainty eleven) |
| function / admin | `la_attestations` | ≥ **100** LA attestations (well-attested admin sign) |
| multi-channel | the three above | high on **≥ 2** of {shape, paleography, function} |
| contested | `cypriot_stable`=candidate ∨ `disagreement_notes` ∨ Cypriot value-conflict ∨ `sm2017_tier` "?" | any tension flag |
| Cypro-Minoan | `cypriot_detail` contains "CM sign N" | CM number present |

## The subsets (mechanically generated)

| subset | n | signs |
|---|---|---|
| all | 59 | A AU DA DE DI DU E I JA JE JU KA KE KI KO KU MA ME MI MU NA NE NI NU NWA O PA PA3 PI PO PU PU2 QA QE QI RA RA2 RE RI RO RU SA SE SI SU TA TA2 TE TI TO TU TWE U WA WI ZA ZE ZO ZU |
| shape_high (homophone) | 25 | A DA DI I KI MA ME MI MU NA NI PA PO RI RO RU SA SE SI SU TA TE TI TO TU |
| paleography_high (Cypriot-stable) | 11 | A DA I NA PA PO RO SA SE TI TO |
| function_high (≥100 attest.) | 19 | A DA DI I JA KA KI KU MA NA NI PA RA RE SA SI TA TE TI |
| multi_channel_high (≥2 channels) | 18 | A DA DI I KI MA NA NI PA PO RO SA SE SI TA TE TI TO |
| contested | 5 | DA JU MU RO SI |
| cypro_minoan | 10 | A DA I NA PA RO SA SE TI TO |

## Structural observations (before any prediction)

1. **The channels are heavily nested, not independent.** `multi_channel_high` (18) is essentially
   `shape_high ∩ (paleography ∪ function)`; `cypro_minoan` (10) ⊂ `paleography_high` (11) ⊂
   `shape_high`-adjacent. The Cypriot-stable set has exactly one member (**PO**) that is not CM.
   This nesting is itself the F4-C finding: the "independent" cross-script channels largely re-flag
   the *same* signs.

2. **`contested` is tiny (n=5)** and value-heterogeneous (DA "= ta in Cypriot", RO "= lo in Cypriot",
   JU Salgarella-internal tension, MU/SI Cypriot placename uncertainty). No test on it can be powered;
   it is reported for completeness and explicitly flagged UNDERPOWERED downstream.

3. **Every subset is drawn from the GORILA/Ventris transliteration lineage** (Art. XI single-
   dependency cluster `L_GORILA_VENTRIS`, per C4 caveats). "shape" and "paleography/Cypriot" are both
   expert value-judgments on the *same latent LB-identity fact* (F1: both CIRCULAR, capped ≤0.75). So
   a subset being "high" on shape or Cypriot does **not** supply an independent value witness — it
   supplies a stronger prior that the sign's LB value is its transliterated value.

## What these subsets are for

- **F4-B** treats each subset's LB values as held-out hypotheses and asks: does a distributional
  correspondence (LA profile → nearest LB sign, twin excluded) recover the value-family, or does the
  only thing that "works" remain the circular shape=identity assumption?
- **F4-C** asks whether the Cypro-Minoan channel adds an independent axis or multiplies the
  shape/Cypriot flags (the nesting above already foreshadows the answer).
- **F4-D** asks whether the *anonymous* C4/C5 substitution classes agree with these value hypotheses
  more than a size- and frequency-matched null.

**Compliance:** no combined evidence score computed; subset membership uses evidence-channel fields
only; `conventional_value` reserved for grading (Art. XII). Licence unchanged: NONE earned (Art. XV).
