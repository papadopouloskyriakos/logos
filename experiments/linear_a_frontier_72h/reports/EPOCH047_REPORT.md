# EPOCH-047 REPORT — Held-Out Predictability of the Document Token-Type Grammar

**Campaign:** Linear A frontier-72h · **Epoch:** 047 · **Layer:** L2/L3 (document token-type grammar)
**Operator:** logos z.ai research worker (GLM-5.2) · **Discipline:** STRICT LOGOS (proposer/operator; mechanical verdict)

## Question
Does the Linear A **document TOKEN-TYPE stream** (the ordered sequence of token TYPES —
`word` / `num` / `nl` / `div` / `other` — within each inscription) have a **PREDICTABLE
grammar** that **GENERALIZES to HELD-OUT inscriptions**? Concretely: does a **first-order
Markov model** of token-TYPE transitions achieve **lower held-out cross-entropy** (bits/token)
than a **unigram baseline**, and does that generalization **hold across a site-blocked split**?

Pure token-TYPE sequence structure (L2/L3): **NO sign identities, NO numeral values, NO
phonetics, NO meaning.** This consolidates the certified ledger/document findings (E031
word→numeral, E037 numeral-line-final) into a single PREDICTIVE held-out test.

## Verdict (mechanical, frozen rule)
### **`DOC_GRAMMAR_PREDICTIVE_HELDOUT`**

Frozen rule: `DOC_GRAMMAR_PREDICTIVE_HELDOUT` iff PC passed AND global CV improvement > 0
significant (p ≤ 0.05) AND site-blocked held-out improvement > 0 (AND order-shuffle p ≤ 0.05)
in ≥ 3 sites. **All conditions met** (PC PASSED; CV +1.014 bits/token, p=0.005; 9/9 sites
improve).

## Positive Control (gates the verdict) — **PASSED**
The machinery must (a) DETECT a planted grammar and (b) produce NO false positives on
order-shuffled streams.

| gate | result |
|---|---|
| (a) DETECT planted `word→num→nl` grammar | mean improvement **+1.501 bits/token**, mean perm p **0.005** ✓ |
| (b) FALSE-POSITIVE on order-shuffled streams | mean improvement **+0.089 bits/token**, **0/20** sets significant ✓ |

Both gates pass → **PC PASSED**. The ~1 bit/token LA improvement (below) is far above the
shuffled null (+0.089), so it is not a machinery artifact.

## Global LA result — RANDOM 5-fold CV
| statistic | value |
|---|---|
| n inscriptions | 1,341 |
| Markov xent (held-out) | **~1.53 bits/token** |
| Unigram xent (held-out) | ~2.56 bits/token |
| **mean IMPROVEMENT** | **+1.014 bits/token** |
| mean order-shuffle perm p | **0.005** (significant) |

Per-fold (Markov xent / Unigram xent / improvement / perm p):

| fold | n_test | Markov | Unigram | improvement | perm p |
|---|---|---|---|---|---|
| 0 | 269 | 1.531 | 2.564 | +1.033 | 0.005 |
| 1 | 268 | 1.530 | 2.544 | +1.014 | 0.005 |
| 2 | 268 | 1.532 | 2.553 | +1.022 | 0.005 |
| 3 | 268 | 1.586 | 2.581 | +0.995 | 0.005 |
| 4 | 268 | 1.582 | 2.589 | +1.007 | 0.005 |

The Markov model cuts per-token uncertainty by ~1 bit (~40%) relative to the context-free
unigram baseline, on inscriptions it never saw in training. Shuffling the interior token order
destroys the gain (perm p=0.005), confirming the predictability is genuinely sequential.

## Site-Blocked Generalization (cross-site)
Train on all-but-one site, test on the held-out site, for each site with ≥ 15 inscriptions.
**9 sites qualify; ALL 9/9 generalize** (improvement > 0 AND perm p ≤ 0.05):

| site | n_test | Markov | Unigram | improvement | perm p | improves |
|---|---|---|---|---|---|---|
| Haghia Triada | 845 | 1.521 | 2.551 | **+1.030** | 0.005 | ✓ |
| Khania | 159 | 1.759 | 2.639 | +0.880 | 0.005 | ✓ |
| Knossos | 51 | 1.952 | 2.721 | +0.769 | 0.005 | ✓ |
| Malia | 21 | 1.435 | 2.562 | **+1.127** | 0.005 | ✓ |
| Palaikastro | 25 | 1.609 | 2.634 | +1.024 | 0.005 | ✓ |
| Phaistos | 48 | 1.780 | 2.551 | +0.771 | 0.005 | ✓ |
| Thera | 17 | 1.797 | 2.504 | +0.707 | 0.005 | ✓ |
| Zakros | 46 | 1.597 | 2.559 | +0.961 | 0.005 | ✓ |
| Iouktas | 16 | 1.942 | 2.912 | +0.970 | 0.005 | ✓ |

The token-TYPE transition grammar is **shared across the Linear A scribal tradition**, not
site-local: a model trained on every other site predicts the held-out site's token-type
ordering significantly better than a unigram baseline. The frozen gate required ≥ 3 sites; 9
achieved.

## Key findings
1. **Predictive held-out grammar.** Random 5-fold CV gives +1.014 bits/token improvement of
   Markov over unigram (1.53 vs 2.56 bits/token), significant by the order-shuffle null
   (p=0.005). Shuffling the interior token order destroys the gain — the predictability is
   genuinely sequential.
2. **Cross-site generalization.** All 9 qualifying sites generalize in the site-blocked split
   (improvement 0.71–1.13 bits/token, all perm p=0.005). The token-type transition structure is
   a property of the tradition, not of individual sites.
3. **PC validated both directions.** The machinery detects a planted word→num→nl grammar
   (+1.501 bits/token, p=0.005) and produces zero false positives on order-shuffled streams
   (+0.089 bits/token, 0/20 significant). The LA result is far above the shuffled null.
4. **Large, stable magnitude.** ~1 bit/token (~40% uncertainty reduction), remarkably uniform
   across folds and sites — a strong, stable document-level regularity in token-TYPE ordering,
   consistent with the certified E031 (word→numeral) and E037 (numeral-line-final) findings,
   now consolidated into a single predictive held-out test.
5. **Closest L2/L3 analog to "predicts held-out material."** A model trained on one set of
   inscriptions predicts the token-TYPE ordering of unseen inscriptions and unseen sites
   significantly better than a context-free baseline — using only token TYPE labels and
   positions, no sign identities, numeral values, phonetics, or meaning.

## Non-circularity / discipline
Pure L2/L3 token-TYPE sequence statistics on the ORDERED per-inscription stream of token TYPES
(`word`/`num`/`nl`/`div`/`other`). NO sign identities, NO numeral values, NO phonetics, NO
sound, NO meaning, NO reading. Only the TYPE label of each token and its position. LB has no
native token-type stream; a synthetic LB control is specified in the machinery but the verdict
rests entirely on LA held-out cross-entropy. Verdict is mechanical from the frozen rule. L2/L3
only.

## Successor hypotheses
- **H1 (L2/L3):** Fit a SECOND-ORDER Markov model over token types; test whether it beats
  first-order on held-out cross-entropy (quantifies 2-step structure beyond first-order
  transitions; token TYPES only).
- **H2 (L2/L3):** Extract and rank the highest-information token-TYPE transitions from the
  trained matrix and characterize the implied document "skeleton" (token-type grammar only).
- **H3 (L2/L3):** Test whether the token-type grammar differs by inscription class/support
  (tablet vs seal vs other) via per-class Markov vs pooled held-out comparison (token types
  only).
- **H4 (L2/L3):** Build the synthetic LB token-type control stream and compare its
  Markov-vs-unigram improvement to LA's, to test whether the grammar strength is distinctive to
  LA or a generic administrative-text property (LB control-only, synthetic stream labelled).
- **H5 (L2/L3):** Leave-one-type-out ablation — collapse one type into `other`, retrain,
  re-evaluate held-out xent — to identify which token classes carry the sequential structure.
- **H6 (L2/L3):** Test predictability as a function of inscription LENGTH (length-binned
  held-out evaluation; token types only).

## Deviations
No deviations from the frozen prereg/plan. The machinery was run exactly as specified (frozen
seeds, Laplace add-1 smoothing, 5-fold CV, site-blocked with MIN_SITE_N=15, order-shuffle
permutation null with 200 shuffles, 20 false-positive control sets). `result.json` and this
`EPOCH047_REPORT.md` were generated in this repair pass because they were missing from the
initial epoch output; `prereg.md` and `plan_hash.txt` were NOT modified.
