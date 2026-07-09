# EPOCH-098 — Spin-glass / Potts energy-landscape identifiability

**Frontier:** F12 CROSS_DISCIPLINARY · **gate:** A · **layer:** L2
**plan_hash:** `217d1217af299cc6e9fbc41e25e0e3b790b11fe23be65eba6f1da3da762da15f`
**Verdict:** **POTTS_NULL** (evidence landscape orthogonal to the linguistic target) · **LA touched:** yes · **licence:** none

## Question
Does the sign-class constraint system have a near-unique ground state (identifiable) or many frustrated minima
(glassy)? Does anchor injection drive an identifiability phase transition?

## Model
Potts spin per sign over q=5 class states; **signed** couplings J = S − mean(S) from the blinded SUBSTITUTION
context-similarity graph (attract/repel → frustration; a purely ferromagnetic J collapses trivially). Energy
E = −Σ J_ij·[s_i==s_j]. Simulated annealing, 12 restarts, permutation-invariant overlap. Anchor sweep fixes a
fraction f of spins to truth and measures free-spin recovery + inter-run overlap.

## Positive control — PASSED
Planted **signed**-block couplings (attract within block, repel across): the solver recovers the unique planted
ground state from random starts (mean recovery 0.96; runs 0.96/0.96/0.91/1.0). Solver + overlap are valid.

## Results
| | inter-run overlap | states used | free-vowel recovery |
|---|---|---|---|
| blinded LB (f=0 anchors) | 0.997 | 5 / 5 | 0.288 |
| blinded LB (f=0.5 anchors) | 0.546 | — | 0.379 |
| Linear A (f=0) | 0.917 | 5 / 5 | (no truth) |

Anchor sweep (LB): f 0→0.5 → recovery 0.29→0.38 (chance = 1/q = 0.20); inter-run overlap **1.00→0.55**.

## Reading
- The context-similarity landscape is **near-unique** (overlap 0.997) and uses **all 5 states** — *not* a trivial
  single-cluster collapse. So it is **not classically glassy** (not many equal-energy minima).
- **But its minimum is orthogonal to the vowel classes:** free-vowel recovery sits near chance (0.29 vs 0.20), and
  injecting *true*-vowel anchors **drops** inter-run overlap 1.00→0.55 while barely lifting recovery — the
  truth-anchors **conflict** with the couplings (they add frustration rather than resolving it). This is a
  truth-independent structural fact proving the evidence is orthogonal to the target.
- **No identifiability phase transition.** ⇒ the available structural evidence does not make LA (or blinded LB)
  class assignment identifiable. A mechanism-level confirmation of underdetermination — sharper than "too little
  data": the evidence gives a *determined-but-wrong* landscape. Consistent with E091/E092 (context graph orthogonal
  to vowel) and complementary to the anchor-lattice degeneracy pricing (which counted many minima of the *full*
  constraint system). No value assigned from any minimum.

## Successors (5)
1. **E099 — causal source separation (queued next).** Separate linguistic from nuisance structure; LA-transfer bar.
2. **Multi-source couplings** — combine substitution + morphology + formula + anchors into one Potts and re-test the
   transition (an E102-synthesis question); low priority given single-source orthogonality.
3. **E100 — TDA**; **E101 — network-flow**; **E102 — synthesis** (Potts logged as non-contributing).
4. **§12 map** — record POTTS_NULL (determined-but-orthogonal) in the exhaustion map (bounded-neg 25→26).
5. **anchor-lattice cross-reference** — note E098 gives the single-evidence-source view of the same
   underdetermination the anchor-lattice priced at the full-system level.

Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
