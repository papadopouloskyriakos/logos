# Labeling-function audit (Stage 4)

## Coverage / conflict / abstention
- 4,759 content forms; **abstain 29%** (no LF fires); **conflict 4.4%** (LFs disagree); mean 0.76 LFs/form.
- WS0–WS3 coverage 0.71 (60/66 gold covered); WS4 (intersection) coverage 0.66 (23 gold).

## The circularity caveat (load-bearing)
The WS "est_precision_on_gold = 1.0" is **NOT a generalization result**: the index LFs
(LF_TOPONYM_INDEX/TITLE) and the REFERENCE_GOLD_A gold are derived from the **same cited index**, so an index
LF trivially reproduces its own source. Precision here is a **consistency/coverage** check only.

The honest generalization proxy is the **EDITION_INDEPENDENT (structural) LFs' agreement with the gold role**:
**0.026** at 0.576 coverage (`power_gate.json`). Structure alone essentially does NOT recover the content
role (PLACE vs HUMAN) — toponyms structurally resemble recipients/counted heads. This is the core evidence
feeding the pre-Stage-5 power gate.

## Dependency handling
`LF_CROSS_SOURCE_CONCORDANCE` counts agreement as independent ONLY across independence classes; WS3 collapses
all `SHARED_DECIPHERMENT` LF votes to a single vote (dependency sensitivity WS1−WS3 = 0.0, since the index
LFs already agree). No false "independent consensus".
