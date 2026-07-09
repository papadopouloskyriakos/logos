# EPOCH-100 — frozen prereg slice (topological data analysis & persistent structure)

**Family:** F12 CROSS_DISCIPLINARY_DECIPHERMENT · **priority:** NEXT_AFTER_MORPHOGENESIS · **layer:** L2 · **gate:** A
**Parent prereg:** `cross_disciplinary/PREREGISTRATION.md` (E100 slice frozen for the plan_hash).

## Question (frozen)
Do blinded-LB sign structures PERSIST across thresholds/representations (genuine topology) rather than appear only
at one arbitrary clustering choice — and do persistent structures align with linguistic classes?

## Method (frozen)
- H0 persistence (persistent connected components) via single-linkage over the cosine-distance filtration of the
  sign context embedding. Barcode = component lifetimes. Persistent-cluster partitions (fcluster over the
  dendrogram) scored vs vowel + consonant truth (ARI); most-persistent k = largest merge-height gap.
- **Nulls:** metric permutation (shuffle distances) + frequency-matched embedding (distance = |Δ log-freq|).
- **Positive control:** planted-cluster distance matrix (persistence must recover it, ARI > 0.4).
- **LA:** persistent communities exported as anonymous; stability = ARI of persistent partitions across two sign
  inventories (min_count 2 vs 3). No semantics assigned.

## Verdicts (mechanical)
`PERSISTENT_STRUCTURE_SUPPORTED` (vowel ARI beats BOTH nulls and > 0.15) · `PERSISTENT_STRUCTURE_GENERIC`
(persistent communities exist/stable but do not align with linguistic classes) · `TDA_NULL` (no persistent
structure at all) · `TDA_NO_POWER` (PC fails).

## Scope
L2, opaque signs. No semantics on any topological feature without independent evidence. LA persistent communities
are anonymous + inventory-stability-checked; no phonetic values, no reading.
