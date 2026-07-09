# Cross-Epoch Evidence Synthesis (§7) — dependency-aware

Machine-readable backing: `CAMPAIGN_FINAL_STATE.json`, `METHOD_EXHAUSTION_MAP.json`,
`EPOCHS_001_TO_FINAL_MASTER_TABLE.csv`. All counts generated (invariant #12). Reflects the terminal audit
remediation (E103R/E104R).

## The one rule that governs this synthesis
**Dependent p-values are never combined as independent evidence.** The campaign's central risk was the
"English is a Semitic language" illusion — many lenses on one channel read as many channels. The E102 independence
audit is the antidote and its result is the spine of this synthesis.

## Evidence graph — node/edge summary
Nodes: 105 epochs · 34 method families · 5 durable relative claims · 1 graduated finding · 1 prospective seal ·
7 transfer licences (all NOT_EARNED) · N null families · the LB-analogue calibration anchor. Edge types realized:
`supports`, `contradicts`, `depends_on`, `shares_data_with`, `shares_assumption_with`, `replicates`,
`fails_to_replicate`, `confounded_by`, `held_out_by`, `null_adjudicated_by`, `reduces_equivalence_class_of`.

## Durable relative claim — A-initial positional enrichment (the only graduated finding)

| support metric | value |
|---|---|
| raw supporting epochs | 4 (E022, E023, E024, E103/E103R) |
| dependency-adjusted support | these are **not** independent replications — they share the silver corpus + the initial-position operationalization. They are independent along the **held-out axes tested**: adaptive-null (E022) ⟂ site (E023) ⟂ support-type & chronology (E024) ⟂ segmentation variant (E103/E103R). |
| segmentation axis, honestly stated | three **overlapping segmentation/selection variants from a single corpus lineage** (B shares 87.6% of unit realizations with A_editor; C is a subset of A_editor) — robustness, not replication; the materially distinct variants are two (editor-family, numeral-anchored). |
| independent *method-channel* count | **1** (positional profile). The A-initial enrichment is a positional-channel constraint. |
| effective evidence-lineage count | 1 corpus lineage (GORILA/silver), 4 orthogonal held-out partitions |

The claim graduates because it survives **held-out partitions the hypothesis did not see** (sites, support types,
chronological phases, segmentation variants) *and* a matched adaptive null — not because four correlated tests
agree. It stays at L2/L3 because it lives in a single method-channel and licenses no value. It is compatible with
a recurrent initial functional or morphological slot; prefixhood, productivity, sound, and meaning are not
established.

## The collapse (why nothing reaches L4+)
`shares_lineage` edges collapse the apparent multi-method vowel signal to one node:
eigenmap → ICA → morphogenesis(E091) → Potts(E098) → persistence(E100) all `share_data_with` the context
co-occurrence matrix (recorded pairwise agreement eigenmap|ICA ARI 0.979, E102; the other three methods recover
the same lineage's structure in their own epochs rather than an independent channel). The genuinely independent
positional channel `fails_to_replicate` the vowel signal (ARI 0.043–0.046 ≈ chance). → **n_independent_channels = 1** → absolute-value gate
`FAILS` → no phonetic value, translation, or language-ID node can be created.

## Contradictions resolved append-only (Art. XVII)
- E022 "A- sole survivor" → **QUALIFIED** by E103 and re-stated exactly by E103R under the corrected categorical
  null: A remains the dominant, rank-1 survivor in every variant (~2.4× the next sign); the corrected secondary
  survivor union (excl. A) is exactly **{*306, *411, DA, I, KU, PA, QA, U}**. Not a downgrade.
- The original E103 joint maxT null (comonotone shared-uniform draws) → **SUPERSEDED** by E103R's categorical
  construction; marginals unaffected; verdict class unchanged; the C-variant survivor set gains boundary sign DA.
- The original E104 point-estimate criterion → **SUPERSEDED** by E104R's blind-committed bound-based rule
  (`CAMPAIGN_NULL_GATES_CERTIFIED`: 1/400, CP95 upper 1.18%; the original run is a pilot).
- Foundry "position→C/V" and "reduced-seed" pillars → **REFUTED** as frequency artifacts by the relative-phonology
  campaign; this campaign inherits that correction and never rebuilds on them.

## Net
A single, weak, single-channel linguistic signal (E099, LB-only) + one graduated relative structural constraint
(A-initial enrichment, held-out-robust) + a wall of bounded negatives + a certified-honest gate (E104R). A
method-diverse re-confirmation of `ANCHOR_LATTICE_UNDERDETERMINED`.
