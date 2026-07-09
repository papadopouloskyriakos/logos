# DEPENDENCY REGISTER — F12 (Art. XI source-dependency graph; E102 independence audit)

Every candidate relation produced by E097–E101 is logged here with its full input lineage, so E102 can count
**genuinely independent** method families (dependency-adjusted), not naive votes. Two methods that share a graph
construction, label set, embedding, or hyperparameter tuning are NOT independent channels.

## Per-relation record (append at each epoch)
```
relation_id:
claim:                    [e.g. "signs X,Y share a relative vowel class" — L2, anonymous]
produced_by:              [method family + epoch]
inputs:
  corpus_version:
  sign_inventory:
  segmentation_variant:
  graph_construction:     [POSITION/SUBSTITUTION/FORMULA/MULTILAYER/other + params]
  embedding:
  labels_used:            [evaluation-only truth vs any used in construction]
  anchors_used:
  morphogenesis_channel:  [imported? which? — must be ablatable]
  hyperparameters:
shared_lineage_with:      [other relation_ids sharing >=1 input above]
independent_channel_count: [after collapsing shared lineages]
held_out_result:
null_result:
stability_across_inventories:
```

## Independence-collapse rule (E102)
Build the source-dependency graph over relations; relations in the same connected component of "shared input"
collapse to **one** channel. A relation is retained only if its independent_channel_count >= 2 AND each channel
independently passes held-out + adaptive null. This prevents an apparent multi-method consensus that is really one
signal seen through five correlated lenses.

## Known shared lineages to watch (pre-registered)
- POSITION / SUBSTITUTION / FORMULA / MULTILAYER graphs all derive from the SAME token stream → co-occurrence-based
  methods (morphogenesis, TDA-on-context, BP-context-factors) share this lineage and are NOT automatically independent.
- Any method seeded by morphogenesis classes inherits the F11 lineage (E091 NULL / E092 GENERIC) → must ablate.
- Frequency is an input to almost everything → a "consensus" that is really a shared frequency prior collapses to
  one channel (the position→C/V lesson).

## Logged relations
(none yet — F12 WAITING_ON_MORPHOGENESIS)
