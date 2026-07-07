# F_LEAVE_ONE_SIGN_OUT — distributional cross-script correspondence vs shape / frequency

**Task F4-B** · Constitution v2.2 (Art. XII, Art. XV) · seed 20260708 ·
script `scripts/f4_loso_relative_class.py` → `data/F4_loso.json`.

## Protocol

For every sign `s` in a subset (that parses to a canonical LB value-cell):

1. **Hold out `s`'s value.** Build the candidate pool = all LB syllabogram signs that parse to a
   `(consonant, vowel)` cell, **excluding the same-named LB twin of `s`** (this is the leave-one-sign-
   out step: the model may not see the identity answer it is being graded on).
2. **Infer the correspondence from Linear A distribution alone.** `s` has a 7-feature distributional
   profile (word-initial / -final rate, mean position, lone rate, L/R-neighbour entropy, log-freq),
   computed over sign *identities* only and z-standardized within Linear A. Rank the LB pool by profile
   cosine; the **top-1 LB sign** is the predicted correspondence. Read off its `(C,V)` as the predicted
   value-family. A second, more robust estimator predicts the **nearest LB value-class centroid**
   (vowel / consonant) directly.
3. **Grade** the predicted vowel and consonant against `s`'s held-out truth.

**Three reference lines** on the identical prediction:
- **shape-only ceiling (circular)** — assume the homomorphic twin ⇒ predict `s`'s true value exactly.
  Vowel/consonant accuracy = **1.0 by construction**. This is the circular identity baseline (F1: shape
  = an LB-homophony judgment, capped ≤0.75); it is a *ceiling that measures the assumption*, not a result.
- **frequency baseline** — predict the value-family of the LB sign whose corpus frequency-*rank* is
  closest to `s`'s (rank-matched, corpus-size agnostic). The "did distribution just recover frequency?"
  control.
- **chance (modal)** — always predict the subset's most common vowel / consonant. The floor a
  distributional method must beat to carry any information.

Non-circular (Art. XII): no phonetic value is ever a model input; values grade the truth and define the
circular shape ceiling only.

## Result — vowel-family recovery

| subset | n | dist top-1 | dist centroid | frequency | **chance (modal)** | shape ceiling |
|---|---|---|---|---|---|---|
| all | 56 | 0.232 | 0.214 | 0.179 | **0.286** | 1.0 (circular) |
| shape_high | 25 | 0.280 | 0.200 | 0.200 | **0.320** | 1.0 |
| paleography_high | 11 | 0.273 | 0.091 | 0.182 | **0.455** | 1.0 |
| function_high | 19 | 0.263 | 0.053 | 0.263 | **0.526** | 1.0 |
| multi_channel_high | 18 | 0.333 | 0.056 | 0.222 | **0.389** | 1.0 |
| cypro_minoan | 10 | 0.300 | 0.100 | 0.200 | **0.500** | 1.0 |
| contested | 5 | 0.800 | 0.400 | 0.600 | **0.400** | 1.0 |

## Result — consonant-family recovery (and exact cell)

| subset | n_cons | dist top-1 | dist centroid | frequency | chance | exact-cell (dist) |
|---|---|---|---|---|---|---|
| all | 51 | 0.098 | 0.078 | 0.020 | 0.118 | **0.000** |
| shape_high | 23 | 0.130 | 0.043 | 0.000 | 0.217 | 0.000 |
| paleography_high | 9 | 0.000 | 0.000 | 0.000 | 0.222 | 0.000 |
| function_high | 17 | 0.176 | 0.059 | 0.000 | 0.176 | 0.000 |
| multi_channel_high | 16 | 0.062 | 0.062 | 0.000 | 0.250 | 0.000 |
| cypro_minoan | 8 | 0.000 | 0.000 | 0.000 | 0.250 | 0.000 |

**Exact `(C,V)` cell accuracy is 0.000 in every subset.**

## Significance

Label-permutation null on the full anchor set (shuffle true vowels 5,000×, recompute distributional
top-1 vowel accuracy):

- observed vowel accuracy 0.232 · null mean 0.208 · null p95 0.304 · **p = 0.377** → **NOT significant.**

## Reading

1. **The distributional cross-script correspondence recovers value-family at or below chance.** In
   every powered subset the top-1 estimator sits *below the trivial "always predict the modal vowel"
   floor* (e.g. function_high 0.263 vs 0.526; paleography_high 0.273 vs 0.455). The centroid estimator
   is *worse still* (0.05–0.21), so the null is not an artefact of a noisy top-1 rule. The permutation
   test confirms the small apparent lift on `all` is noise (p = 0.377). Exact-cell recovery is a flat
   zero. This concords with F2-Q2 (cross-script retrieval MRR 0.164, top-1 0.059) and F2-Q3 (within-LB
   same-vowel function-lift p = 0.365, null): even inside a single readable script the vowel axis is
   not distributionally recoverable, so the cross-script leg cannot be either.

2. **The only line that "reads" the value is the shape ceiling — and it reads it by circular
   assumption.** Its 1.0 is definitional: it *assumes* the transliterated identity it is scored on
   (F1: shape channel is CIRCULAR, capped ≤0.75; source-dependency = 0/59 primary value witnesses). It
   is a measure of the prior's strength, not evidence of a recovered correspondence.

3. **The apparent `contested` win (0.80, n = 5) is underpowered noise.** No permutation significance is
   attainable at n = 5; the five signs are value-heterogeneous by construction (DA/RO carry documented
   Cypriot value-conflicts). Per-sign: DA→KA, MU→DU, RO→MO, SI→I all share the *true vowel* only because
   `a`/`u`/`o`/`i` happen to be the corpus-modal vowels among those signs — the frequency floor, not a
   correspondence. It must not be read as a positive.

## Verdict

```
CROSS_SCRIPT_VALUE_FAMILY_RECOVERY: NULL (distributional correspondence at/below chance; perm-p 0.377;
                                    exact-cell 0.000; consonant recovery at/below chance in all subsets)
ONLY_NON_NULL_LINE:                 shape-identity ceiling = 1.0, CIRCULAR (assumes the graded value;
                                    F1 capped <=0.75; 0/59 primary value witnesses)
```

Leave-one-sign-out finds **no distributional cross-script channel that recovers an LA sign's LB value-
family beyond chance**, on any evidence-graded subset. Cross-script "correspondence" carries value
information *only* through the circular shape=identity assumption; the internal distribution does not
corroborate it. Highest earned layer L2 (relative structure). **Licence unchanged: NONE (Art. XV).**

**Compliance:** LB values graded only; distributional profiles value-free; append-only. No licence
bypass; no absolute value assigned or transferred.
