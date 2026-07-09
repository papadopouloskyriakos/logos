# Prospective Seals and Future Tests (§8.4 / §12.8)

Machine-readable: `PROSPECTIVE_SEALS.json`. A prospective seal is a *frozen, hashed* prediction that can only be
scored against evidence not available at freeze time — the Linear-B-new-tablet standard.

## SEAL-1 — FRACTION_ORDER_ANETAKI_SEAL (E004) · **FROZEN, UNOPENED**
- **seal_id:** FRACTION_ORDER_ANETAKI_SEAL · **plan_hash:** da6e0248… · **manifest:**
  `data/seals/FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256`
- **frozen_prediction:** a 25-claim pairwise fraction-value ordering, Corpus-derived (Corazza-independent), plus the
  Corazza-2021 comparator. Sharpest committed content: **H > K** and **A > B** — both anti-frequency and both
  contradicting Corazza's uncertain-tier values. Honest p_desc = 0.727 (ZA8 violates descending convention).
- **opening_event:** publication of the (currently unpublished) Anetaki II face-delta six-fraction sequence.
- **contamination_conditions:** any pre-opening access to the Anetaki II fraction readings voids the seal.
- **success_criterion:** the mechanical scorer beats the Corazza comparator on the held-out ordering.
- **failure_criterion:** scorer ties or loses to Corazza, or the sharp H>K / A>B calls are contradicted.
- **status:** PASS on PC/NC/contamination at freeze; awaiting the opening event.

## SEAL-2 — cross-branch imported seals · **FROZEN ELSEWHERE (referenced, not re-frozen)**
- `M_ANETAKI_LATTICE_DELTA_SEAL` (research/linear-a-anchor-lattice) and the relative-phonology seals
  `SEAL_2` / `SEAL_3` (research/linear-a-relative-phonology-seals) are frozen on their own branches. They share the
  Ariadne-2025 opening event with SEAL-1; listed here for the reviewer's completeness, not duplicated.

## Future tests defined but not yet runnable
| test | opening condition | expected equivalence-class reduction |
|---|---|---|
| A- slot vs newly-excavated inscriptions | any new LA admin inscription | confirms/refutes the graduated finding prospectively (highest-value) |
| second-channel independence (stroke/palaeography) | GORILA-plate contour acquisition | could raise n_independent_channels 1→2 → re-opens the absolute-value gate |
| FRACTION_ORDER scoring | Anetaki II publication | tests a committed relative fraction ordering against unseen data |

## Verification for reviewers
All seal hashes are in `data/seals/*.manifest.sha256` and are reproduced in `INTEGRITY_AND_REPRODUCIBILITY.md`.
None may be opened by the campaign; opening is an external event.
