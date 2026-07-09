# EPOCH-101 — frozen prereg slice (global graph/network-flow constrained decipherment benchmark)

**Family:** F12 CROSS_DISCIPLINARY_DECIPHERMENT · **priority:** NEXT_AFTER_MORPHOGENESIS · **layer:** L2 · **gate:** A
**Parent prereg:** `cross_disciplinary/PREREGISTRATION.md` (E101 slice frozen for the plan_hash).

## Question (frozen)
Global-optimization re-decipherment (Ugaritic etc.) succeeded WITH a known related-language target. LA has none.
- **Stage A (known-target calibration, blinded LB):** does GLOBAL assignment (capacity-constrained Hungarian
  enforcing the class-size marginal) recover held-out sign classes better than LOCAL nearest-neighbor / random?
- **Stage B (TARGET-FREE, LA):** with no cognate target, does global assignment ADD information beyond the
  anchor-lattice null, or merely SELECT one arbitrary representative of a huge equivalence class?

## Method (frozen)
Sign context embedding. Stage A: split signs anchored/unknown (50/50); cost[i,c] = distance to anchored class-c
centroid; local = argmin_c; global = capacity-Hungarian with the oracle class marginal; random. Metric = held-out
class accuracy (vowel). Stage B (LA): target-free → equivalence classes; quantify the class-label symmetry (S_q).
**Positive control:** confusable + strongly-imbalanced synthetic where the global marginal MUST beat local NN
(local over-assigns the majority).

## Verdicts (mechanical)
`GLOBAL_ASSIGNMENT_ADDS_INFORMATION` (global beats local on LB by > the PC-demonstrated margin) ·
`GLOBAL_ASSIGNMENT_SELECTS_ARBITRARY_REPRESENTATIVE` (global ≈ local; LA target-free → representative-selector) ·
`GLOBAL_ASSIGNMENT_NULL` (nothing beats random) · `GLOBAL_ASSIGNMENT_NO_POWER` (PC fails: global can't beat local
even when it should).

## Scope
L2, opaque signs. Stage B for LA outputs equivalence CLASSES, not a lexicon. No claim that global optimization can
manufacture constraints absent from the data (the anchor-lattice priced LA degeneracy at ~10^63–10^270). No
phonetic values, no reading.
