# EPOCH-104 preregistration — campaign-wide adaptive null (§9)

**Reason:** RUN_CAMPAIGN_WIDE_NULL. **Frontier:** campaign-wide discipline validation. **Layer:** N/A (methodology). **Licence:** none.

## Objective
Reproduce the campaign's major adaptive choices as ONE meta-null and measure whether the discipline machinery
fabricates a graduated finding on signal-free data, plus which gate is load-bearing. Adaptive choices reproduced:
(1) sign selection (best-of ~51-sign initial universe), (2) segmentation choice (3 schemes + replication),
(3) threshold/report rule (E103: top maxT survivor p<=.01 under >=2/3 schemes), (4) multiplicity control
(correlation-aware best-of-universe maxT deflation).

## Design (frozen)
- Null corpora: real editor words with within-word sign order shuffled (preserves per-word multiset + length +
  per-inscription content; destroys positional signal). Rebuild all 3 segmentation schemes on each null.
- Run the ACTUAL E103 graduation machinery end-to-end on each null; count false REPLICATED_RELATIVE_CONSTRAINT.
- Ablation: same, but replace the maxT deflation with the naive raw single-permute p of the extreme sign.
- Power: plant a real prefix 'PX' at 12% into the null; confirm recovery.
- Absolute-value gate false-fire: structural 0 (a positional-only null cannot make >=2 independent channels).

## Committed prediction
Modal: full machinery false-graduation rate <= 2% AND naive ablation materially higher AND planted recovery >= 0.8
-> CAMPAIGN_NULL_GATES_LOAD_BEARING, identifying the maxT deflation as load-bearing. This also certifies E103's A-
graduation is outside the null band.

## Verdict rule (mechanical)
CAMPAIGN_NULL_GATES_LOAD_BEARING iff false-graduation(maxT) <= 0.02 AND planted_recovery >= 0.8; else
CAMPAIGN_NULL_GATE_WEAK. Load-bearing gate = maxT iff ablation raises the rate by > 0.05.

## Reuse note
Complements (does not replace) the existing calibrations: E022 in-epoch false-graduation 0/300; the anchor-lattice
gate calibration (naive pipeline fabricates decipherment 120/120 vs gated 0/120, planted 20/20). This epoch adds the
end-to-end adaptive-search null specific to the frontier-72h graduation rule.
