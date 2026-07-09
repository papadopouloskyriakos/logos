# EPOCH-101 — Global network-flow constrained decipherment benchmark

**Frontier:** F12 CROSS_DISCIPLINARY · **gate:** A · **layer:** L2
**plan_hash:** `6103a3682489f4be638dfa59e879a00558c30adc9dababa8c99ee32ece92d7a2`
**Verdict:** **GLOBAL_ASSIGNMENT_SELECTS_ARBITRARY_REPRESENTATIVE** · **LA touched:** yes · **licence:** none

## Question
Global-optimization re-decipherment (Ugaritic etc.) succeeded **with a known related-language target**. LA has none.
Does global assignment add information beyond the anchor-lattice null, or just pick an arbitrary representative?

## Method
Sign context embedding. **Stage A** (known target, blinded LB): anchored/unknown split; cost = distance to anchored
class centroids; **local** = argmin, **global** = capacity-Hungarian enforcing the class marginal, random. **Stage B**
(LA, target-free): equivalence classes; quantify class-label symmetry. **PC**: confusable + imbalanced synthetic
where the global marginal must beat local NN.

## Positive control — PASSED (after hardening to a genuinely hard case)
Confusable + strongly-imbalanced synthetic: global **0.662** vs local **0.553** (+0.11). Global assignment *can*
add information when a known target exists and classes are confusable — so the benchmark has power.

## Results
| | value |
|---|---|
| **Stage A blinded LB** — local NN | 0.466 |
| **Stage A blinded LB** — global assignment | **0.485** (+0.019, ≪ the +0.11 the PC shows) |
| Stage A random | 0.167 |
| **Stage B LA** — class-label symmetry | **S₅ = 120 equivalent relabelings** |

## Reading
- **Even with a known LB target**, global assignment barely beats local NN (+0.019, far below the +0.11 gain the PC
  demonstrates when global genuinely helps) — LB context similarity barely separates the classes, so the global
  marginal constraint adds almost nothing.
- **For LA there is no target:** global assignment produces equivalence classes whose labels are unidentifiable up
  to the full symmetric group S₅ (120 relabelings). Global optimization is a **representative-selector** — it cannot
  manufacture the constraints the anchor-lattice showed are absent (~10⁶³–10²⁷⁰ degeneracy).
- **The decisive distinction:** the Ugaritic-style successes had a *known cognate target*; LA does not. Global
  network-flow optimization therefore adds **no ambiguity reduction beyond the anchor-lattice null** on LA.

## Successors (5)
1. **E102 — cross-method synthesis + frozen-LA application (LAST F12 epoch, queued next).** Intersect the one F12
   positive (E099 invariant LB vowel structure, LA-untestable) against E097/E098/E100/E101 negatives under the
   independence audit + absolute-value gate.
2. **§12 map** — record GLOBAL_ASSIGNMENT_SELECTS_ARBITRARY_REPRESENTATIVE (bounded-neg 27→28) + the "needs a known
   target" distinction from Ugaritic.
3. **Optimal-transport / Sinkhorn variant** — low priority; the S₅ symmetry argument is solver-independent.
4. **anchor-lattice cross-reference** — E101 is the global-optimization view of the same degeneracy the
   anchor-lattice priced; note global optimization cannot break it without a target.
5. **E102 dependency register** — log network-flow as a non-contributing channel.

Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
