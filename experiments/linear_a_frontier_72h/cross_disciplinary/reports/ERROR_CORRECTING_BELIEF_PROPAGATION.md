# EPOCH-097 — Error-correcting-code / belief-propagation decoding

**Frontier:** F12 CROSS_DISCIPLINARY_DECIPHERMENT (first epoch) · **gate:** A · **layer:** L2
**plan_hash:** `a6217b483f644221a003815d3b2cf4e7a0f8b969e1313edc052801ce88203809`
**Verdict:** **ECC_BP_SUPPORTED (LB calibration) · LA_TRANSFER_NEGATIVE (LA objective = NULL)** · **LA touched:** yes · **licence:** none

## Question
Treating the blinded corpus as a noisy code, does belief propagation over a sign factor graph (bidirectional +
skip-2 redundancy = message passing) reconstruct masked signs better than local/independent baselines — and does
that advantage transfer to Linear A?

## Method
Held-out masked-sign top-1 accuracy (70/30 word split). Methods: random · unigram · forward-bigram ·
backward-bigram · **bp_bidir** (sum-product left+right messages ÷ prior) · **bp_loopy** (add skip-2 factors,
damping 0.5). Ladder: synthetic HMM → blinded LB → LB degraded to LA token scale → blinded LA.

## Positive control — PASSED
Synthetic HMM: bp_bidir **0.490** ≫ unigram 0.065 on high redundancy, and recovery **rises with redundancy**
(0.490 high vs 0.105 low). The decoder genuinely recovers masked signs when a code is present.

## Results (masked-sign top-1 accuracy)
| stage | random | unigram | forward | backward | bp_bidir | bp_loopy |
|---|---|---|---|---|---|---|
| blinded LB | 0.003 | 0.044 | 0.152 | 0.158 | 0.279 | **0.307** |
| LB @ LA token scale | 0.004 | 0.057 | 0.153 | 0.157 | **0.214** | 0.197 |
| **real Linear A** | 0.016 | 0.058 | **0.121** | 0.104 | 0.087 | 0.038 |

## Reading
- **On blinded LB, belief propagation clearly wins:** bp_loopy 0.307 ≫ best-local 0.158 ≫ unigram 0.044. Combining
  bidirectional + higher-order redundancy recovers masked signs well beyond local context. The advantage even
  survives degrading LB to LA token scale (bp_bidir 0.214 vs local 0.157).
- **On real Linear A it reverses:** the **best method is a plain forward-bigram (0.121)**; bp_bidir underperforms it
  (0.087) and **loopy BP is actively harmful (0.038, below unigram 0.058)**. LA's longer (mean 7.88 vs LB 3.23),
  sparser words break the higher-order/bidirectional estimates — the "code redundancy" machinery does not transfer.
- **Net for the LA objective:** masked-sign prediction is best served by a plain forward-bigram at modest accuracy
  (top-1 0.121); belief propagation adds nothing and its higher-order form hurts. This is a **calibration-positive /
  transfer-negative** — the campaign's signature pattern (E016 SBI, F11 morphogenesis) — and exactly the failure
  mode §15 warns against ("do not treat LB success as LA evidence").

## Authorized LA output (L2, no phonetic values)
Missing-sign prediction via forward-bigram: top-1 accuracy 0.121 (with uncertainty). No sign values, no
translations, no language-family ID. Feeds E102 synthesis as a **non-contributing** channel (BP yields no
independent LA-supported relation).

## F12 discipline established
The real gate for imported frameworks is the **LA-transfer bar**, not the LB calibration. E098–E101 continue;
E102 records BP as non-contributing unless a later epoch finds an LA-transferring variant.

## Successors (5)
1. **E098 — Potts spin-glass identifiability (queued next).** Does the constraint system have a unique or
   exponentially-degenerate ground state? (Expected: glassy/underdetermined, per the anchor-lattice pricing.)
2. **E099 — causal source separation.** Separate linguistic from nuisance structure; the LA-transfer bar applies.
3. **BP-LA-variant** — if pursued, a sparsity-robust BP (backoff/shrinkage on LA bigrams) to test whether the
   transfer failure is fixable or intrinsic; low priority given forward-bigram already wins.
4. **§12 map** — record ECC/BP as an LA-transfer-negative in the exhaustion map (bounded-neg 24→25).
5. **E102 dependency register** — log BP's inputs (LB/LA token streams, bigram lineage) for the independence audit.

Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
