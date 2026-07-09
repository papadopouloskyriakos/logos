# EPOCH-099 — frozen prereg slice (causal source separation & confound disentanglement)

**Family:** F12 CROSS_DISCIPLINARY_DECIPHERMENT (E097–E102) · **priority:** NEXT_AFTER_MORPHOGENESIS · **layer:** L2 · **gate:** A
**Parent prereg:** `cross_disciplinary/PREREGISTRATION.md` (E099 slice frozen for the plan_hash).

## Question (frozen)
Is the blinded-LB sign-class (vowel) structure LINGUISTIC (invariant across nuisance) or CONFOUND-explained
(frequency)? The campaign's enemy is the frequency artifact (position→C/V, reduced-seed) — this epoch is the
causal-invariance adjudication of the weak vowel signal found in E091/E093.

## Method (frozen)
- Sign context embedding (left‖right neighbor counts, blinded LB). Source separation: **PCA + FastICA + NMF**
  (k=8); the ICA representation is the analysis embedding.
- **Target:** vowel class (5). **Nuisance:** log-frequency.
- **Two independent interventions (both must hold — the ≥2-intervention gate):**
  1. **leave-one-frequency-band-out (LOFO):** train a nearest-centroid vowel classifier on 2 frequency terciles,
     predict the held-out tercile. Vowel predictable for unseen-frequency signs ⇒ frequency-invariant.
  2. **deconfounding:** residualize every feature on log-frequency, re-embed, re-run LOFO.
- **Controls:** PC = synthetic linguistic factor INDEPENDENT of a confound factor (LOFO must survive). NEG =
  synthetic where the label IS the frequency band (LOFO must collapse to chance ⇒ CONFOUND_EXPLAINED). The test is
  validated iff PC stays invariant AND NEG collapses out-of-distribution.

## Verdicts (mechanical)
`CAUSAL_INVARIANT_STRUCTURE_SUPPORTED` (survives BOTH interventions above chance) · `PARTIAL_INVARIANCE` (one of
two) · `CONFOUND_EXPLAINED_SIGNAL` (in-distribution signal collapses OOD + under deconfounding) · `CAUSAL_NULL` (no
in-distribution structure) · `CAUSAL_NO_POWER` (controls fail).

## Scope
L2, opaque signs. **LA has no vowel ground truth** → invariance is validated on LB only; for LA the epoch exports a
confound-adjusted embedding to E102 and makes NO LA linguistic-recovery claim. No phonetic values, no translations.
A SUPPORTED verdict means the *blinded-LB* vowel signal is genuinely linguistic (not a frequency artifact) — it
does NOT license any LA reading.
