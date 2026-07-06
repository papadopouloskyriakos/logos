# FINAL_EGYPTIAN_CHANNEL_VERDICT — §XI

Mechanically derived by `src/calibration/verdict.py` from `results/{model_validation,gate}.json`.

## Verdict
```
status                     = COMPLETE
egyptian_channel_readiness = READY_FOR_PREREG_DRAFT
```
**The first channel in the external-anchors programme to pass its gate.**

## Why READY (all criteria met, from the numbers)
| criterion | result |
|---|---|
| calibration corpus valid + provenance-complete | 152 tier-A/B, 156 roots, 0 Cretan leakage ✅ |
| model beats baselines out-of-sample | M2 top-1 0.691 vs 0.434 (M0/M1) ✅ |
| leave-one-family-out robust | NW 0.77 / South 0.67 / cross 0.60 (East → SUBGROUP_NO_POWER) ✅ |
| deterministic regeneration | ✅ |
| matched-scarcity control passes | short recovery 0.685; min detectable 2 anchors ✅ |
| end-to-end FP acceptable | real 0.691 vs random 0.0 / permuted 0.118 / permissive 0.007; specific ✅ |
| no load-bearing adaptive choice outside the null | frozen spec `3c56ed71`; selection covered by permissive null ✅ |
| held-out recovery adequate | top-1 0.691 ✅ |
| uncertainty does not reverse | HIGH-uncertainty recovery 0.342 ≫ null; no reversal ✅ |

## Contingency (important — this is DESIGN readiness, not a decipherment)
Future Cretan toponym anchors remain **CONFIRMATORY_INELIGIBLE** until **REQ-01** (the Kom el-Hetan
primary edition — Edel & Görg 2005 / Kitchen's full collation) is directly collated. The *calibration*
is ready; the confirmatory *target freeze* is not, pending REQ-01. READY_FOR_PREREG_DRAFT means "draft
the preregistration," not "the reading works."

## Recommendation
**Draft a preregistration** for a later one-shot Cretan-anchor test. The non-Cretan calibration is
valid, the frozen correspondence model beats baselines out-of-sample and per family, the matched-
scarcity control passes (min detectable 2 anchors), the nulls are specific, and the verdict survives
HIGH transcription uncertainty. Do **not** run real Cretan/Linear-A matching, preregister externally,
or claim any sign value in this pass; resolve REQ-01 before the confirmatory target freeze.

## Not claimed
No Linear A phonetic/lexical/language-family/decipherment verdict; no Cretan name correspondence. This
is a calibrated, powered DESIGN — the first anchor route that clears the gate.
