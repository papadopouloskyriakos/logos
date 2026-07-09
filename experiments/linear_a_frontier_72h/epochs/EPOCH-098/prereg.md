# EPOCH-098 — frozen prereg slice (spin-glass / Potts energy-landscape identifiability)

**Family:** F12 CROSS_DISCIPLINARY_DECIPHERMENT (E097–E102) · **priority:** NEXT_AFTER_MORPHOGENESIS · **layer:** L2 · **gate:** A
**Parent prereg:** `cross_disciplinary/PREREGISTRATION.md` (E098 slice frozen for the plan_hash).

## Question (frozen)
Does the sign-class constraint system have a near-unique ground state (identifiable) or many frustrated minima
(glassy/underdetermined) — and does anchor injection drive an identifiability phase transition? Ties to the
anchor-lattice degeneracy pricing (~10^63–10^270). A calibrated mechanism-level restatement, NOT a new positive.

## Model (frozen)
- Potts spin per sign over q=5 class states (vowel classes as the LB target). **SIGNED** couplings J = S − mean(S)
  from the blinded SUBSTITUTION context-similarity graph (similar signs attract J>0, dissimilar repel J<0 →
  frustration + nontrivial ground state; a purely ferromagnetic J collapses trivially). Energy E = −Σ_{i<j} J_ij·[s_i==s_j].
- Solver: simulated annealing, 12 restarts, permutation-invariant overlap. **Degeneracy** = mean pairwise overlap
  across restarts (high = identifiable / few minima; low = glassy). **Anchor sweep**: fix fraction f∈{0,.1,.2,.3,.5}
  of spins to truth; measure free-spin recovery + inter-run overlap → the identifiability transition curve.
- Diagnostic: n states used in the ground state (guards trivial single-cluster collapse).

## Ladder / calibration
Stage-1 positive control: planted signed-block couplings (attract within block, repel across) → the solver must
recover the planted identifiable ground state (mean recovery > 0.8). Stage-2 blinded LB (truth = vowel).
Stage-4 LA (no truth → intrinsic degeneracy + state-usage).

## Verdicts (mechanical)
`POTTS_IDENTIFIABILITY_SUPPORTED` (unique GS aligned with truth) · `POTTS_PHASE_TRANSITION_FOUND` (anchor injection
raises free recovery > 0.15) · `POTTS_GLASSY_UNDERDETERMINED` (low overlap = many minima) · `POTTS_NULL` (landscape
minimum orthogonal to the target; no transition; anchors conflict) · `POTTS_MODEL_INVALID` (PC fails).

## Scope
L2, opaque signs. No sign value is assigned from any single low-energy state (explicitly forbidden). Analogies
(paramagnetic/glassy/ferromagnetic) are labels for the exact operational metrics only. No phonetic values.
