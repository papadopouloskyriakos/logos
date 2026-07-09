# EPOCH-100 — Topological data analysis & persistent structure

**Frontier:** F12 CROSS_DISCIPLINARY · **gate:** A · **layer:** L2
**plan_hash:** `ba2f9021b0a1f36fdea488a40cc04f7dd15ae721c365623f2f60df63cd65e41e`
**Verdict:** **PERSISTENT_STRUCTURE_GENERIC** · **LA touched:** yes (anonymous communities) · **licence:** none

## Question
Do blinded-LB sign structures persist across thresholds (genuine topology), and do persistent structures align with
linguistic classes?

## Method
H0 persistence (persistent connected components) via single-linkage over the cosine-distance filtration of the sign
context embedding. Persistent partitions scored vs vowel/consonant (ARI). Nulls: metric permutation + frequency-
matched. PC: planted-cluster distance matrix. LA: persistent-community stability across two sign inventories.

## Positive control — PASSED
Planted-cluster distance matrices recovered at ARI **1.0** (mean best over 4 seeds). Machinery valid.

## Results (blinded LB)
| quantity | value |
|---|---|
| vowel best persistent-partition ARI | **−0.002** (≈ 0) |
| consonant best ARI | 0.019 |
| metric-permutation null p95 | 0.023 |
| frequency-matched null p95 | 0.024 |
| **LA persistent-community stability (inventory ARI)** | **0.729** |

## Reading
- Persistent H0 communities **exist and are inventory-stable** (LA 0.729) — but they do **not align with linguistic
  classes** on blinded LB (vowel ARI ≈ 0, *below* both nulls). ⇒ the persistent topology is **generic** (degree /
  single-linkage chaining), not linguistic.
- **Sharpens E099:** the vowel signal is real and frequency-invariant (E099, F1 ~0.44) but is **not a
  topological-cluster signal** — it is centroid-separable while single-linkage *chains through* it. So the weak
  linguistic signal has **diffuse geometry**, not separated clusters. This is a genuinely informative negative: it
  tells us *what kind* of structure the signal is (and isn't).
- LA persistent communities are exported to E102 as **anonymous + inventory-stable**, with no semantics.

## Successors (5)
1. **E101 — global network-flow (queued next).** Target-free constrained assignment for LA; does global
   optimization add information beyond the anchor-lattice null?
2. **E102 — synthesis:** log TDA as a non-linguistic-contributing channel (LA communities available as anonymous
   structure only); reconcile with E099's centroid-separable-but-not-clustered vowel signal.
3. **Higher homology** (H1 loops / Mapper) if a persistence library becomes available — low priority given H0 null.
4. **Density-based filtration** (average/complete linkage) to test whether the chaining is the culprit vs a true
   absence of cluster topology.
5. **§12 map** — record TDA_GENERIC (bounded-neg 26→27) + the "diffuse not clustered" geometry note.

Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
