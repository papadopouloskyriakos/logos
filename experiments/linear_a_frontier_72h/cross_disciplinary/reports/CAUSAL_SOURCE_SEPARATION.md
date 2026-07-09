# EPOCH-099 — Causal source separation & confound disentanglement

**Frontier:** F12 CROSS_DISCIPLINARY · **gate:** A · **layer:** L2
**plan_hash:** `71c147b73a5daed8aaf2ef9104ccf3c2e182d58ea926ba6a20264377060b155e`
**Verdict:** **CAUSAL_INVARIANT_STRUCTURE_SUPPORTED** (blinded LB; LB-calibration positive, NOT an LA claim) · **LA touched:** yes · **licence:** none

## Question
Is the blinded-LB vowel-class signal (E091/E093) genuinely **linguistic** (frequency-invariant) or a **frequency
artifact** (the enemy that sank position→C/V and reduced-seed)?

## Method
Sign context embedding → source separation (PCA + FastICA + NMF, k=8). Target = vowel; nuisance = log-frequency.
Two independent interventions, **both** required:
1. **leave-one-frequency-band-out (LOFO):** predict vowel for signs whose frequency band was never in training.
2. **deconfounding:** residualize features on log-frequency, re-embed, re-run LOFO.

## Controls — validate the test both directions
| control | within-band F1 | LOFO F1 | reads as |
|---|---|---|---|
| PC (linguistic ⟂ confound) | 1.000 | **0.996** | invariant survives ✓ |
| NEG (label = frequency band) | 1.000 | **0.218** (≈ chance) | confound collapses OOD ✓ |

The test detects both an invariant signal and a pure confound → the LB verdict is meaningful.

## Result (blinded LB)
| quantity | value |
|---|---|
| within-band vowel F1 (in-distribution) | 0.388 |
| **leave-one-frequency-band-out F1** | **0.437** |
| **deconfounded LOFO F1** | **0.467** |
| max component–log-freq correlation | 0.429 (separable frequency component) |
| chance (1/q) | 0.200 |

## Reading
- The vowel signal **survives both interventions**: it is predictable for signs whose frequency band was held out
  (0.437 > within-band 0.388, ≫ chance 0.20), and it survives frequency-residualization (0.467). A frequency
  component exists but is **separable** (corr 0.429).
- ⇒ the weak vowel co-occurrence structure is **frequency-invariant linguistic structure, not a frequency
  artifact.** This **corroborates and strengthens E093** (vowel beats a frequency-only baseline) by adding
  out-of-frequency-distribution generalization + deconfounding.
- **Scope (critical):** this is **blinded Linear B**, which *has* vowel truth. **Linear A has no vowel ground
  truth**, so LA invariance is **not** tested — the epoch exports a confound-adjusted LA embedding to E102 and makes
  **no** LA linguistic-recovery claim. Weak in absolute terms (F1 ~0.44). No phonetic values, no reading.

## Place in F12
First F12 non-negative. Contrast E097/E098 (LB-calibration-positive but LA-transfer/identify NEGATIVE): E099's
positive is that the **readable script's signal is genuinely linguistic**, and it hands E102 the strongest confound
guard the campaign has built (the invariance test) plus a validated deconfounding tool.

## Successors (5)
1. **E100 — topological data analysis (queued next).** Persistent structure across representations; nulls include
   degree-rewiring + label-shuffle; the invariance lesson carries over.
2. **E101 — global network-flow** (target-free for LA).
3. **E102 — synthesis:** weigh E099's invariant LB vowel structure (a real but weak, LA-untestable signal) against
   the E097/E098 LA-transfer failures; log E099's deconfounded embedding as a channel.
4. **Second independent nuisance** — add a position/damage intervention to the invariance gate (frequency alone was
   decisive here; a fully-orthogonal second nuisance would harden the ≥2-intervention claim).
5. **§12 map** — record the invariant-vowel qualification (bucket 5→6): the weak signal is genuinely linguistic.

Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
