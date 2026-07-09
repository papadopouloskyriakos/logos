# EPOCH-094 — frozen prereg slice (sequence/segmentation morphogenesis)

**Family:** TURING_MORPHOGENESIS (E091–E096) · **priority:** IMMEDIATE · **layer:** L2 · **gate:** A
**Parent prereg:** `morphogenesis/PREREGISTRATION.md` (E094 slice frozen for the plan_hash).

## Question (frozen)
Distinct from E091–093 (class recovery): given an UNSEGMENTED blinded-LB sign stream, does an RD/morphogenesis
boundary cue (activator-domain boundaries over a sign-type graph) recover WORD BOUNDARIES better than generic
unsupervised segmentation cues (transition surprisal, forward branching entropy) and random?

## Design (frozen)
- **Task:** concatenate LB words (each ~3.23 signs) into sign streams (15 words/stream); truth = word boundaries.
- **Held-out:** bigram / branching-entropy stats estimated on a 70% TRAIN word split; boundary-F1 evaluated on
  30% TEST streams (5 stream seeds averaged).
- **Boundary prediction:** top-k gaps at the TRUE boundary rate (precision=recall → fair cross-cue comparison).
- **Cues:** random (floor) · transition surprisal −log P(s_{i+1}|s_i) · forward branching entropy H(next|s_i) ·
  **morphogenesis** = |u(s_i) − u(s_{i+1})| where u is the RD (Schnakenberg, unsupervised coarsest-mode) activator
  field over the G_POSITION sign-type graph.
- **Positive control:** synthetic lexicon-generated corpus with planted boundaries; the generic cues must beat
  random by >0.10 (else NO_POWER).

## Verdicts (mechanical)
- **SEGMENTATION_MORPHOGENESIS_SUPPORTED** — morphogenesis beats random AND the best generic cue (+0.02).
- **SEGMENTATION_MORPHOGENESIS_GENERIC** — beats random but not the generic cues.
- **SEGMENTATION_MORPHOGENESIS_NULL** — does not beat random (≤ +0.02).
- **SEGMENTATION_MORPHOGENESIS_NO_POWER** — PC fails (task undetectable by the harness).
- **SEGMENTATION_MORPHOGENESIS_MODEL_INVALID** — no valid Turing regime for the field.

## Prior / scope
E091/E092 established morphogenesis ties/loses to generic methods. A _GENERIC or _NULL is the expected outcome.
L2, opaque IDs, LA not touched (calibration on blinded LB; frozen-LA application deferred and only if SUPPORTED).
No sound values, no translations.
