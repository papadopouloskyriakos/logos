# EPOCH-097 — frozen prereg slice (error-correcting-code / belief-propagation decoding)

**Family:** F12 CROSS_DISCIPLINARY_DECIPHERMENT (E097–E102) · **priority:** NEXT_AFTER_MORPHOGENESIS · **layer:** L2 · **gate:** A
**Parent prereg:** `cross_disciplinary/PREREGISTRATION.md` (E097 slice frozen for the plan_hash). First F12 epoch.

## Question (frozen)
Treating the blinded corpus as a noisy code: does belief propagation over a sign factor graph that exploits
REDUNDANCY (bidirectional context + higher-order/skip factors = message passing) reconstruct MASKED signs better
than independent/local baselines — and does that advantage TRANSFER to Linear A?

## Design (frozen)
- **Task:** held-out masked-sign top-1 accuracy. 70/30 word split; estimate factors on train, mask each sign in
  each test word, reconstruct.
- **Methods:** random · unigram (independent marginal) · forward-bigram · backward-bigram · **bp_bidir**
  (sum-product: product of left+right messages ÷ prior) · **bp_loopy** (add skip-2 factors, damping 0.5).
- **Ladder:** Stage-1 synthetic HMM corpus with tunable redundancy (BP must beat unigram AND rise with redundancy)
  → Stage-2 blinded LB → Stage-3 LB degraded to LA token scale (~4245) → Stage-4 blinded LA (missing-sign
  prediction is an authorized L2 output — sign identity, NOT phonetic value).
- **Positive control:** the Stage-1 synthetic HMM (detects iff bp_bidir > unigram+0.05 on high-redundancy AND
  high > low redundancy).

## Verdicts (mechanical, computed on the LB calibration)
`ECC_BP_SUPPORTED` (BP beats unigram AND local single-direction) · `_PARTIAL` (beats unigram, not local) ·
`_NULL` (does not beat unigram) · `_NO_POWER` (PC fails) · `_MODEL_INVALID`.
**Transfer rule (frozen, §15):** LB success is NOT LA evidence. The banked headline must report the LA-transfer
outcome separately — an ECC_BP_SUPPORTED calibration with a failed LA transfer is a NEGATIVE for the LA objective.

## Prior / scope
E016/E091/E092 established local/simple structure carries the signal and fancy methods tie/lose. Modal expectation:
BP works on LB but does not reduce LA ambiguity beyond a simple local model. L2, opaque signs, no phonetic values,
no translations, no language-family ID. Authorized LA output: missing-sign predictions + uncertainty only.
