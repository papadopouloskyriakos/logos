# CROSS_DISCIPLINARY_DECIPHERMENT — PREREGISTRATION (E097–E102)

**Frontier:** F12 · **family:** `CROSS_DISCIPLINARY_DECIPHERMENT` · **priority:** NEXT_AFTER_MORPHOGENESIS
**Reserved epochs:** E097 · E098 · E099 · E100 · E101 · E102 (first available after MORPH_END=E096)
**Status:** `WAITING_ON_MORPHOGENESIS` → `ACTIVE` when the F11 block is terminal (E094+E095 banked/terminated; E096
de-authorized). **Registered:** 2026-07-09, live inside the 72h campaign; **finalization gate remains BLOCKED**
(clock 2026-07-11T03:20Z governs, not epoch count).
**Layer ceiling:** L2/L3. **Absolute phonetic values remain NOT authorized** unless the §12 absolute-value gate is
met (≥2 independent channels + leave-one-anchor-out + leave-one-method-out + held-out-form prediction + full
adaptive null). Constitution Art. V (claim layers), Art. VIII (effective_n), Art. XI (source-dependency),
Art. XV (transfer licences — none earned), Art. XVIII (assumption register), Art. XXII (per-stage articles).

## Central hypothesis
Mathematical frameworks imported from other disciplines (error-correcting codes / belief propagation; spin-glass /
Potts energy landscapes; causal source separation; topological data analysis; global network-flow assignment),
implemented as **falsifiable computational models**, can (a) recover hidden script structure under **blinded
known-script** conditions and (b) **reduce Linear A ambiguity** — OR they cannot, in which case the null (a
rigorous map of what the corpus does/does not support) is the banked result. Metaphorical resemblance is not a
result; each method is calibrated on known truth, compared to simpler baselines, and subjected to adaptive nulls.

**Prior of record (do not re-derive):** the campaign has repeatedly found that (i) generic/simple methods tie or
beat fancy ones on this corpus (EPOCH-016 SBI; EPOCH-091/092 morphogenesis), (ii) apparent positives are often
frequency or site artifacts (position→C/V, reduced-seed, E074 genre↔site), and (iii) LA is data-sufficient for the
weak structural signal that exists (E093) but has **no licensed LB→LA phonetic transfer**. The modal expected
outcome for E097–E101 is therefore NULL / GENERIC / CONFOUND_EXPLAINED / UNDERDETERMINED; a genuine method-specific
positive would be the surprise and must clear the adaptive null.

## Shared 5-stage evaluation ladder (frozen; every method)
1. **Synthetic planted script** — known values/morphology/formulae/damage/site+scribe variation/false anchors.
2. **Blinded Linear B** — phonetic values + Greek readings hidden; opaque sign IDs; truth used only for evaluation.
3. **LB degraded to LA-like conditions** — corpus size, formula repetition, damage, short-form rate, anchor count,
   site imbalance, boundary uncertainty (reuse the E093 degradation harness where applicable).
4. **Frozen Linear A application** — only if Stages 1–3 pass the preregistered criteria for that method.
5. **Adaptive null + held-out adjudication** — §13 null programme; mechanical verdict.
A method reaches Stage 4 **only** if it passes Stages 1–3. A calibration failure is recorded and does **not** force
a Linear A result (Art. XVII append-only; an amendment may not turn a failed result into a success).

## Morphogenesis import rule (F11 → F12)
Import from F11 as **optional, ablatable channels only — never ground truth**: validated/invalidated graph views
(POSITION/SUBSTITUTION/FORMULA/MULTILAYER), the finding that the Turing mechanism is not needed (E091/E092), the
degradation thresholds + frequency-artifact guard (E093), the stable-vs-unstable anonymous classes, the confounds,
and the held-out partitions. Every method must **ablate** the morphogenesis-derived channel and report performance
with and without it (so no result depends on an unvalidated import).

## Per-epoch frozen commitments

### E097 — Error-correcting-code & belief-propagation decoding · gate A
Factor graph over sign / word-form / formula-slot / morphological-relation / ledger-constraint / anchor / damage
variables. Implement **sum-product BP, max-product BP, damped loopy BP** (survey/expectation propagation optional).
Stage-1 synthetic admin corpora with tunable redundancy; measure recovery as redundancy ↓. Stage-2 blinded LB:
recover missing signs, sign classes, morphological relations, formula roles, same-vowel/same-consonant constraints,
damaged-token reconstruction. Baselines: independent marginals, majority/frequency, plain factor graph (no
redundancy constraints), Bayesian morphology, MDL segmentation, random. Authorized LA outputs: posterior sign-role
classes, boundary/morphology relations, missing-sign predictions, equivalence-class reduction, uncertainty.
Forbidden: absolute readings w/o anchors, translations, language-family ID. Verdicts: `ECC_BP_SUPPORTED /
_PARTIAL / _NULL / _NO_POWER / _MODEL_INVALID`.

### E098 — Spin-glass / Potts energy-landscape identifiability · gate A
Potts variable per unresolved sign over candidate states (phonetic-class / relative-class / unknown). Couplings
from substitution / morphology / formula-slot / cross-script hypotheses / anchors / admin / site-genre (dependency
lineage explicit). Compute: energy landscape, ground-state degeneracy, near-ground-state count, overlap
distribution, replica stability, frustration index, anchor susceptibility, **phase transition under anchor
injection**, robustness to wrong anchors. Solvers: simulated annealing + parallel tempering + BP/cavity
(replica-exchange MCMC if feasible). Calibrate on blinded LB + synthetic: does the model detect the transition
many-minima → one-recoverable-system as anchors are added? LA question: is current evidence paramagnetic
(underdetermined) / glassy (frustrated) / ferromagnetic (identifiable)? Analogy only — report exact operational
metrics. No value assigned solely because it appears in one low-energy state. Verdicts:
`POTTS_IDENTIFIABILITY_SUPPORTED / POTTS_GLASSY_UNDERDETERMINED / POTTS_PHASE_TRANSITION_FOUND / POTTS_NULL /
POTTS_MODEL_INVALID`.

### E099 — Causal source separation & confound disentanglement · gate A
Separate linguistic signal from nuisance (site / genre / scribe-tracer / modern rendering / edition / frequency /
damage / document-series / chronology). ≥3 methods: ICA + NMF + causal/invariant-risk representation (multi-view
latent / domain-adversarial / SCM optional). LB labels for evaluation only. Interventions: leave-one-site-out,
leave-one-genre-out, leave-one-renderer/tracer-out, leave-one-edition-out, frequency balancing, damage balancing.
**Critical gate:** a relation advances only if it survives ≥2 independent nuisance interventions. LA outputs:
confound-adjusted embeddings, invariant relations, relations that disappear under deconfounding, residual
site/genre structure. Verdicts: `CAUSAL_INVARIANT_STRUCTURE_SUPPORTED / CONFOUND_EXPLAINED_SIGNAL /
PARTIAL_INVARIANCE / CAUSAL_NULL / CAUSAL_NO_POWER`.

### E100 — Topological data analysis & persistent structure · gate A
Filtrations over sign-context / substitution / morphology / formula-slot / cross-site / morphogenesis-field /
confound-adjusted distances. Compute persistent connected components, persistent loops, barcode stability,
persistence diagrams, bottleneck + Wasserstein distances (Mapper / persistent cohomology / multiparameter
optional). Calibrate: do persistent structures match same-vowel / same-consonant families, morphological paradigms,
formula classes, site/scribe communities? Nulls: degree-preserving rewiring, metric permutation, random
embeddings, frequency-matched graphs, site-label shuffle, genre-label shuffle. LA outputs: persistent anonymous
communities / formula structures / morphological families stable across inventories + segmentations. No semantics
on a topological feature without independent evidence. Verdicts: `PERSISTENT_STRUCTURE_SUPPORTED /
PERSISTENT_STRUCTURE_GENERIC / TDA_NULL / TDA_NO_POWER`.

### E101 — Global graph/network-flow constrained decipherment benchmark · gate A
Stage-A (known-target calibration): min-cost flow / bipartite matching / optimal transport / global assignment on
blinded LB + known-script benchmarks, using known related-language targets **for calibration only**. Stage-B
(TARGET-FREE for LA): remove cognate-target supervision; allow only relative classes / formula structure /
morphology / admin roles / independent anchors / confound-adjusted similarities / persistent structures; output
**equivalence classes, not a lexicon**. Baselines: local nearest-neighbor, greedy assignment, random, Bayesian
factor graph, MDL beam search, existing anchor-lattice solvers. Critical question: does global assignment reduce
ambiguity **beyond the anchor-lattice null**, or merely pick one arbitrary representative of an equivalence class?
Verdicts: `GLOBAL_ASSIGNMENT_ADDS_INFORMATION / GLOBAL_ASSIGNMENT_SELECTS_ARBITRARY_REPRESENTATIVE /
GLOBAL_ASSIGNMENT_NULL / GLOBAL_ASSIGNMENT_NO_POWER`.

### E102 — Cross-method synthesis & frozen LA application · gate A/C
Intersect ONLY independently-validated outputs of E097–E101 + morphogenesis. Do not average weak signals.
Independence audit per candidate relation: methods supporting it, shared inputs / source lineages / graph
construction / labels / hyperparameters, **dependency-adjusted independent-channel count** (Art. XI). Retain a
relation only if: survives held-out AND appears in ≥2 genuinely independent method families AND beats adaptive
nulls AND is stable across ≥2 sign inventories or segmentations. Possible retained outputs: anonymous sign classes,
relative phonological classes, morphological relations, formula roles, confound-invariant relations, persistent
communities, per-sign entropy reduction, ranked evidence-acquisition targets, prospective predictions.
**Absolute-value gate (all required):** ≥2 independent external/structural channels constrain the value AND it
survives leave-one-anchor-out AND leave-one-method-out AND it predicts held-out forms AND the complete adaptive
null rejects chance. Otherwise report relative constraints only. Verdicts:
`SYNTHESIS_ABSOLUTE_VALUE_SUPPORTED / SYNTHESIS_RELATIVE_CONSTRAINTS_ONLY / SYNTHESIS_NULL /
SYNTHESIS_NO_INDEPENDENT_CHANNELS`.

## Shared adaptive-null programme (frozen; §13)
The null reproduces every adaptive choice across the batch: method / representation / graph / factor / anchor /
parameter / threshold / solver / initialization / restart / baseline selection + best-result reporting +
cross-method intersection. Null families: random value assignments, frequency-matched value assignments, random
factor graphs, shuffled redundancy constraints, random anchors, dependency-cloned anchors, wrong-language targets,
degree-preserving rewiring, random embeddings, shuffled confounds, random filtrations, best-of-method/parameter/
representation/ensemble nulls. Draws: cheap component nulls ≥1000, moderate method nulls ≥300, full adaptive batch
nulls ≥100.

## Substantive-epoch gate (each epoch, §15)
implemented method · positive control · negative controls · held-out test · mechanical verdict · persisted
machine-readable artifacts · successor decision. A quick negative is a valid epoch iff it has all of these. No
runtime padding. Synthetic/LB success is NOT LA evidence. A physical metaphor is NOT a scientific result.

## Content hash
`plan_hash` per epoch = sha256 of that epoch's frozen prereg slice + code manifest, written to the epoch dir at run
time (as in F11 E091–E093).
