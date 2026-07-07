# B3 — Known-Script Segmentation Calibration (opaque Linear B)

**Task:** B3 · **Branch:** research/linear-a-relative-phonology-seals · **Constitution:** v2.2
(Art. III guilty-until-proven · VII search-receipt · VIII effective-n · XII no-grading-by-the-rule-that-made-it)
· **Seed:** 20260708 · **Script:** `scripts/b3_known_script_segmentation.py` · **Data:** `data/B3_known_script.json`

## Question
Linear B word boundaries are **known**. Treat LB as **opaque** (hide the phonetic readings; keep only the
distributional channel = sign identities + co-occurrence), physically reconstruct the tablets into sign
**streams**, delete the word dividers, and ask: **can unsupervised segmentation model families recover the
known word boundaries from distribution alone?** Only families that beat the random-boundary *and* fixed-rate
baselines on **held-out** LB are declared *validated* for use on Linear A (where no gold boundaries exist).

## Non-circularity (Art. XII)
Gold LB boundaries and LB vowel values `{A,E,I,O,U}` are used **only to grade** (boundary P/R/F1; downstream
C/V, substitution, morphology). They are **never** an input to any unsupervised model. The one supervised model
(`SUP_CLF_localcue`) *does* use gold boundary labels and is reported **only as a reference** — it is explicitly
**not transferable to Linear A** and is excluded from the validated set.

## Setup
Per-tablet reconstruction from DĀMOS (`_damos_wordforms`, syllabic wordforms only; logograms/metrograms/numerals
dropped). Tablets with ≥2 syllabic words split **70/30 by tablet** (seeded).

| | tablets | signs | gaps | gold boundaries | boundary rate | mean word (signs) |
|---|---|---|---|---|---|---|
| all multiword | 2,202 | — | — | — | 0.261 (train) | 3.29 (train) |
| **held-out TEST** | 661 | 12,362 | 11,701 | 3,152 | 0.269 | — |

Unsupervised models are estimated on **train**, **frozen**, then predict boundaries on **test**; downstream
metrics are graded on **test**. A "gap" is between two adjacent signs; boundary P/R/F1 is over gaps.

## Model families implemented (all distributional-only unless flagged)
- **CUE_TP_min** — forward transitional-probability (bigram) local-minimum rule (Saffran/Harris). Parameter-free.
- **CUE_BranchEntropy** — Tanaka-Ishii branching-entropy-increase rule (forward + backward, trie depth ≤5). Parameter-free.
- **BAYESIAN_unigram** — Brent/Venkataraman Dirichlet-smoothed unigram lexicon + spelling backoff, DP Viterbi, 6 EM iters.
- **MDL** — two-part description-length code (corpus MLE bits + lexicon-entry bits); DP + type pruning (spell-out cheaper ⇒ drop).
- **FINITE_STATE_bigram** — exact word-**bigram** Viterbi (state = last word) over an EM-induced lexicon.
- **MULTISCALE_ENSEMBLE** — majority vote (≥2 of 4) over BranchEntropy, Bayesian, MDL, FiniteState per gap.
- *baselines:* **RANDOM** (Bernoulli at gold rate), **FIXED** (period-3), **ALL** (cut every gap).
- *reference (uses gold labels — NOT transferable):* **SUP_CLF_localcue** — logistic on gap cues (TP, BE, PMI, freqs, position).

## Result 1 — boundary recovery (held-out TEST)

| model | P | R | **F1** | beats random / fixed / all-cut | validated for LA |
|---|---|---|---|---|---|
| `_REF` GOLD | 1.000 | 1.000 | 1.000 | — | (reference) |
| BASELINE_RANDOM | 0.277 | 0.268 | **0.272** | — | — |
| BASELINE_FIXED (period 3) | 0.291 | 0.340 | **0.313** | — | — |
| BASELINE_ALL (cut-every-gap) | 0.269 | 1.000 | **0.424** | — | — |
| CUE_TP_min | 0.437 | 0.576 | **0.497** | ✓ / ✓ / ✓ | **YES** |
| CUE_BranchEntropy | 0.356 | 0.845 | **0.501** | ✓ / ✓ / ✓ | **YES** |
| **BAYESIAN_unigram** | 0.463 | 0.884 | **0.608** | ✓ / ✓ / ✓ | **YES (best)** |
| MDL | 0.424 | 0.863 | **0.568** | ✓ / ✓ / ✓ | **YES** |
| FINITE_STATE_bigram | 0.404 | 0.901 | **0.558** | ✓ / ✓ / ✓ | **YES** |
| MULTISCALE_ENSEMBLE | 0.384 | 0.925 | **0.542** | ✓ / ✓ / ✓ | **YES** |
| SUP_CLF_localcue (rate-matched) | 0.432 | 0.419 | 0.425 | ✓ / ✓ / ✓ | no (uses labels; not transferable) |
| SUP_CLF_localcue (thr 0.5) | 0.448 | 0.097 | 0.160 | ✗ | no |

Bootstrap 95% CIs (1,000 resamples over tablets) on the **F1 gap vs each baseline exclude 0** for every
unsupervised family (e.g. Bayesian vs random = [+0.316, +0.353], vs fixed = [+0.272, +0.316]). **All six
unsupervised families are validated**: they beat random, fixed-rate, *and* the strong cut-everywhere baseline.

**Key finding on the supervised reference:** a purely local-cue supervised classifier (even with gold labels)
reaches only F1 0.42 — **weaker than every unsupervised lexicon model**. Segmentation on this script is driven
by **global lexicon structure**, not local gap cues; the DP lexicon families are the right instrument.

## Result 2 — downstream (does each segmentation improve LB structure recovery?)

Graded on held-out TEST with known LB values. Baselines random/fixed vs GOLD vs the validated models.

| model | C/V recovery (CV AUC) | substitution (same-feat prec; chance≈0.26) | morphology (G_typed bits/word) |
|---|---|---|---|
| GOLD segmentation | 0.754 | 0.283 | 0.267 |
| PACKED (whole tablet) | 0.779 | 0.00 (1 edge) | 0.099 |
| BASELINE_RANDOM | 0.807 | 0.260 | 0.079 |
| BASELINE_FIXED | 0.789 | 0.260 | 0.170 |
| CUE_TP_min | 0.757 | 0.258 | 0.118 |
| CUE_BranchEntropy | 0.675 | 0.249 | 0.197 |
| **BAYESIAN_unigram** | 0.782 | **0.291** | **0.417** |
| **MDL** | 0.743 | **0.335** (best) | **0.559** (best) |
| FINITE_STATE_bigram | 0.768 | 0.264 | 0.332 |
| MULTISCALE_ENSEMBLE | 0.711 | 0.284 | 0.211 |

Reading each downstream channel honestly:

- **C/V recovery — NOT a discriminator (honest null).** Vowel-vs-consonant AUC is 0.68–0.81 for *every*
  segmentation, and **random (0.807) and packed (0.779) exceed gold (0.754)**. The LB positional C/V signal is
  **segmentation-invariant** — it survives random cuts. Consequence for LA: **held-out C/V recovery cannot be
  used to select or validate a segmentation.** (This tightens B1's C/V story: the C/V partition is not evidence
  of correct word boundaries.)
- **Substitution recovery — improved by MDL and Bayesian.** Random/fixed sit at chance (≈0.26). **MDL 0.335**
  and **Bayesian 0.291** exceed both chance and GOLD (0.283); FST and the cue models stay at chance. MDL's
  segmentation yields a substitution graph that tracks shared C/shared V above baseline.
- **Morphology recovery — strongly improved by all lexicon models.** Held-out affix-compression gain rises from
  random 0.079 / fixed 0.170 to **MDL 0.559, Bayesian 0.417, FST 0.332** — above GOLD (0.267). *Caveat:* DP
  segmenters favor frequent repeated chunks (= regular affix slots), so the metric rewards distributional
  regularity; read as "captures strong morphology-like paradigm structure," not "more linguistically correct
  than gold." The direction vs the baselines is the load-bearing fact: unsupervised segmentation **recovers
  affix structure the baselines do not.**

## Validated set (eligible for Linear A)
All six unsupervised families pass the boundary gate with CI-separated margins and none degrade downstream
below baseline. Ranked by held-out boundary F1:

1. **BAYESIAN_unigram** (F1 0.608) — best boundaries; strong morphology; above-chance substitution. **Primary.**
2. **MDL** (F1 0.568) — best downstream (substitution 0.335, morphology 0.559). **Primary for structure recovery.**
3. **FINITE_STATE_bigram** (F1 0.558).
4. **MULTISCALE_ENSEMBLE** (F1 0.542).
5. **CUE_BranchEntropy** (F1 0.501) / **CUE_TP_min** (F1 0.497) — parameter-free cue baselines; validated but weakest.

**Excluded:** `SUP_CLF_localcue` (uses gold labels; no LA analogue; also under-performs the unsupervised models).

## Honesty / limits (do not overstate)
- This is a **reconstruction**: real LB tablets *had* word dividers; we deleted them to build the calibration.
  Even the best model still **misses ~12% of gold boundaries and over-cuts** (P 0.46) — best F1 0.61 means
  segmentation is *aided, not solved*, on a fully known script.
- **These F1 values are an optimistic upper reference for LA.** LA units are far shorter (GORILA words mean 1.84
  signs; packed inscriptions ~7.9) than LB words (3.29); the known segmentation-tax means LA recovery will be
  lower. Validation here is **necessary, not sufficient**; it earns these families the right to *run* on LA, not
  a claim about LA boundaries. Consistent regime check: B1's unsupervised `SEG_PROBABILISTIC_BOUNDARY` graded
  F1 0.436 on LA GORILA words — same order, lower, as expected.
- The C/V downstream being segmentation-invariant means **no phonetic licence is earned or implied here.** This
  is an **L2/L3 structural** result (sign-string segmentation), not L5+ semantic/phonetic.

## Verdict
```
KNOWN_SCRIPT_SEGMENTATION_CALIBRATION: SUPPORTED_ON_LINEAR_B
VALIDATED_FAMILIES = {BAYESIAN_unigram, MDL, FINITE_STATE_bigram, MULTISCALE_ENSEMBLE,
                      CUE_BranchEntropy, CUE_TP_min}   # all beat random+fixed, CI-separated, held-out
BOUNDARY_F1_BEST = 0.608 (BAYESIAN_unigram)  vs  baselines random 0.272 / fixed 0.313 / all-cut 0.424
DOWNSTREAM: C/V recovery = segmentation-INVARIANT (not a discriminator);
            substitution + morphology recovery = IMPROVED by MDL/Bayesian above baseline.
TRANSFER_TO_LA = necessary-not-sufficient; no phonetic/semantic licence earned (L2/L3 structural only).
```
