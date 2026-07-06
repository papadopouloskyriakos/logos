# PROJECT CHARTER — Egyptian External-Anchor CALIBRATION GATE

**Branch:** `research/egyptian-calibration-gate` · **Worktree:** `/home/claude-runner/gitlab/n8n/logos-egyptian-calibration`
**Forked from:** `research/external-minoan-anchors` @ `6d2e926` (preserved Egyptian channel).

## Purpose (calibration gate, NOT a discovery run)
Determine whether an Egyptian→foreign correspondence model, estimated ONLY from independent **non-Cretan**
material, has enough independently-calibrated sensitivity + false-positive control to justify a later
preregistered one-shot Cretan-anchor test. **No real Linear A↔Egyptian matching. No Cretan/LA similarity
inspection. No phonetic/lexical/language-family claim. No external preregistration.**

## Valid final outcomes
`READY_FOR_PREREG_DRAFT` · `NO_POWER` · `REJECT_SEARCH_ARCHITECTURE` · `INCOMPLETE`. A rigorous null /
NO_POWER / blocked-INCOMPLETE is a successful, honest outcome.

## Isolation (forbidden)
Do not touch `runtime/csa_sweep/`, signal CSA processes, modify `paper/` or the TACL correction, alter
the closed LA↔LB channel artifacts, perform real LA↔Egyptian matching, inspect Cretan/LA resemblance,
run candidate-language testing, externally preregister, or use fenced compute. Light local CPU only.

## Verdict ontology
`status ∈ {INCOMPLETE, COMPLETE}` · `egyptian_channel_readiness ∈ {NOT_READY, READY_FOR_PREREG_DRAFT,
NO_POWER, REJECT_SEARCH_ARCHITECTURE}`. `INCOMPLETE` must not be used to dodge a warranted negative — but
it IS the correct verdict when the load-bearing calibration corpus cannot be built to standard.
