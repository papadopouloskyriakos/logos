# THEORY & PRIOR ART — cross-disciplinary decipherment (E097–E102)

Each imported framework is stated as a **falsifiable computational model on this corpus**, with the operational
metric that decides it and the honest prior on whether it will work here. Metaphor is explicitly not the claim.

## E097 — Error-correcting codes & belief propagation
**Source.** Gallager LDPC codes; Pearl belief propagation; the sum-product algorithm on factor graphs (Kschischang,
Frey, Loeliger 2001); loopy BP and survey propagation from statistical physics of inference.
**Falsifiable model here.** Signs/forms/formula-slots/morphology/ledger-totals/anchors/damage as a factor graph;
redundancy (repeated formulae, accounting identities, morphological alternations) acts as parity structure. If the
corpus carries recoverable redundancy, BP marginals should reconstruct held-out masked signs above the
independent-marginal baseline; recovery should degrade as redundancy is removed.
**Prior/honesty.** Real administrative syllabaries are weakly redundant and loopy; loopy BP can fail to converge or
converge to wrong fixed points. A plain frequency/marginal baseline is strong. Expected modal outcome: PARTIAL on
LB (damaged-token reconstruction), NULL/NO_POWER at LA scale. Danger: "recovery" that is just the frequency prior —
guarded by the plain-FG and frequency baselines.

## E098 — Spin-glass / Potts energy landscapes
**Source.** Sherrington–Kirkpatrick / Potts models; the cavity method and replica theory (Mézard–Parisi); the
statistical-physics view of constraint satisfaction (SAT/coloring phase transitions).
**Falsifiable model here.** Each unresolved sign = a Potts spin; compatibility constraints = couplings. The
identifiability question becomes: does the constraint system have a near-unique ground state (ferromagnetic /
identifiable) or exponentially many equal-energy minima (glassy / underdetermined)? Anchor injection = a field;
identifiability = a phase transition as field strength grows.
**Prior/honesty.** The anchor-lattice campaign already PRICED LA's ambiguity as astronomically degenerate
(~10^63–10^270). So POTTS_GLASSY_UNDERDETERMINED is the strongly expected outcome; the value of the epoch is a
*calibrated, mechanism-level* restatement (degeneracy count + the anchor threshold at which a phase transition would
occur) — NOT a new positive. Must verify the model is a genuine spin system (real couplings, real frustration), not
generic clustering relabeled.

## E099 — Causal source separation & confound disentanglement
**Source.** ICA (Hyvärinen); NMF (Lee–Seung); invariant risk minimization / causal representation learning
(Arjovsky et al.; Schölkopf et al.); domain-adversarial learning (Ganin).
**Falsifiable model here.** Sign embeddings are a mixture of linguistic signal + nuisance sources (site, genre,
scribe, rendering, edition, frequency, damage). A method that separates them should yield a component that is
*invariant* across held-out nuisance interventions (LOSO/LOGO/LO-renderer) and predicts held-out linguistic labels;
confounded structure should vanish under deconfounding.
**Prior/honesty.** The campaign has repeatedly shown apparent structure is site/genre/frequency-confounded (E074
genre↔site ~83%; position→C/V frequency artifact). So CONFOUND_EXPLAINED_SIGNAL / PARTIAL_INVARIANCE are the modal
outcomes. The critical gate (survive ≥2 independent interventions) is precisely to prevent a confound from passing
as signal. Small effective-n (≈88 signs) limits power — NO_POWER is a live outcome.

## E100 — Topological data analysis & persistence
**Source.** Persistent homology (Edelsbrunner–Harer; Carlsson); barcodes; bottleneck/Wasserstein stability
(Cohen-Steiner et al.); Mapper.
**Falsifiable model here.** Build filtrations over sign-relation distances; genuine structure (same-vowel families,
paradigms, formula classes, communities) should appear as topological features that PERSIST across scales and
across representation choices, unlike features that exist only at one arbitrary clustering threshold.
**Prior/honesty.** Persistence controls the "one arbitrary clustering" failure mode, which is real here. But with
~88 nodes and weak signal, persistent features may be indistinguishable from degree-preserving-rewiring nulls →
PERSISTENT_STRUCTURE_GENERIC / TDA_NULL are the modal outcomes. Persistence ≠ meaning: no semantics without
independent evidence.

## E101 — Global network-flow assignment
**Source.** Successful computational re-decipherment via global optimization (Knight, Nair, Rathod, Yamada 2006 on
Ugaritic; Snyder, Barzilay, Knight 2010; Luo, Cao, Barzilay 2019 neural decipherment) — all of which used a
**known related-language target**. Min-cost flow / optimal transport / Hungarian assignment.
**Falsifiable model here.** Stage A calibrates global assignment where a known target exists (blinded LB → Greek /
benchmark pairs). Stage B is the honest hard case: **LA has no known cognate target**, so the target-free mode may
only output equivalence classes. The decisive test is whether global optimization ADDS information over the
anchor-lattice null or merely selects one arbitrary representative from a large equivalence class.
**Prior/honesty.** The anchor-lattice work established that without ≥12 distinct-lineage multi-slot anchors LA
assignment is underdetermined; global optimization cannot manufacture constraints that are not in the data. Modal
outcome: GLOBAL_ASSIGNMENT_SELECTS_ARBITRARY_REPRESENTATIVE / _NULL. This epoch exists partly to make that
limitation *quantitative and mechanical*, and to refuse the classic overclaim (a re-decipherment method that
"works" only because it invented a target).

## E102 — Cross-method synthesis
**Source.** Ensemble/consensus theory, but with a strict independence audit (dependency-adjusted channel counting,
Art. XI) rather than naive voting.
**Falsifiable model here.** A relation is retained only if independently corroborated by ≥2 genuinely independent
method families (not shared inputs/lineages) AND held-out AND null-beating AND stable across inventories. The
absolute-value gate is deliberately near-unreachable given the current evidence — it is the honesty backstop, not
an expected pass.
**Prior/honesty.** Given E097–E101's expected nulls, the modal synthesis outcome is
SYNTHESIS_RELATIVE_CONSTRAINTS_ONLY or SYNTHESIS_NO_INDEPENDENT_CHANNELS. The deliverable is a defensible map of
what is jointly supported (likely: anonymous relative classes + entropy-reduction targets), NOT a decipherment.

## Common failure modes this batch is built to avoid
- **Metaphor-as-result** — every method has a mechanical verdict computed from held-out data.
- **Frequency/site/degree artifacts** — guarded by frequency-matched, site-shuffle, degree-rewiring nulls.
- **Best-of-search inflation** — the adaptive null reproduces method/param/representation/ensemble selection.
- **Shared-input pseudo-independence** — E102's dependency audit charges shared lineages before counting channels.
- **Inventing an LA target** — E101 Stage B is explicitly target-free; equivalence classes, not a lexicon.
- **Turning a physics analogy into a phonetic claim** — L2 ceiling; absolute-value gate near-unreachable by design.
