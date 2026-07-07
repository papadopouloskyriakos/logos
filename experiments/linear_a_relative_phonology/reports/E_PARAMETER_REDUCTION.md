# E4 — Parameter reduction: does the E1 morphology reduce independent hypotheses, or only re-describe training data?

**Constitution v2.2.** Articles III (guilty-until-proven), V (claim layers), VII (search receipt), VIII
(effective-n / multiplicity), IX (information budget), XII (no grading by the creating rule). **Highest
claim layer L2/L3. Licences NOT_EARNED. No phonetic value assigned.** Script
`scripts/e4_parameter_reduction.py`; data `data/E4_paramreduce.json`; seed 20260708; pure stdlib + the
read-only corpus loader. Every input is a distributional statistic over **anonymous** sign identities;
Linear B is used only as anonymous strings (its values are never read here).

## The question, and the honest rule stated up front

E1 induced a modest morphology (word = `[prefix?] stem [suffix?]`, single-sign affixes; one robust
anonymous prefix class **A-**). E4 asks whether that morphology **reduces the number of independent
sign/word hypotheses** — the thing a real grammar does. A morphology can do two very different things,
and they must not be conflated:

1. **Compress the training corpus** (fewer bits / fewer lexical units to describe the data it was fit on).
2. **Predict held-out words better** (generalize to material it never saw).

**A morphology that only compresses training data does NOT advance.** Compression is a statement about
the corpus you already have; only held-out predictive gain — *attributable to the learned structure* —
shows the morphology captures real generative units. E4 measures **both**, and gates the verdict on the
held-out axis with a rate-matched random-segmentation **null** and a **Linear B positive control**.

## Method

**Models (all proper distributions over sign-strings — a stop symbol makes the sign-unigram base
proper, so held-out negative log-likelihood in bits is directly comparable):**

| model | what it is |
|---|---|
| **P0** | sign-unigram-with-stop — no morphology, no lexicon. The floor. |
| **FLAT** | Witten-Bell( whole-word MLE lexicon , P0 ) — *memorise* every training word. |
| **MORPH** | `[prefix?] stem [suffix?]`, MAP-fit (E1 hard-EM); stem = Witten-Bell(stem-lex, P0), affixes add-0.5, gates = fitted π. Marginalises over the ≤4 analyses. |
| **MORPH_RANDNULL** | **null**: same PSS structure and *same* affixation rates (π_p, π_s) as MORPH, but cut locations are **random**. Isolates "did the *learned* structure help?" from "did *any* split help?". |

**(1) Compression** — two-part MDL (Rissanen/Morfessor form) on the full corpus:
`L_total = L(codebook) + L(corpus|codebook)`. FLAT's codebook = word types; MORPH's codebook =
morphemes (prefixes ∪ stems ∪ suffixes) shared across words. Reported as
`compression_improvement = (DL_flat − DL_morph)/DL_flat` and `param_reduction_ratio = #morphemes/#word-types`.

**(2) Held-out** — 5-fold CV over word tokens; bits/word and bits/sign; split by whether the test
word-**type** was **SEEN** or **UNSEEN** in the training fold. UNSEEN is the true generalization test —
FLAT can only back off to P0 there, so a genuine morphology must beat both P0 and the random null on UNSEEN.

## Results — measured

### (1) Compression: YES, clearly — a real training-data statement

| dataset | word types | morphemes (pre/stem/suf) | param ratio | ΔDL (bits) | compression |
|---|---|---|---|---|---|
| **LA GORILA_WORD** | 1165 | **709** (54 / 597 / 58) | **0.609** | 8 928 | **+14.2 %** |
| LA ENTRY | 633 | 495 (35 / 410 / 50) | 0.782 | 2 414 | +8.5 % |
| LA FORMULA | 662 | 500 (35 / 421 / 44) | 0.755 | 2 946 | +8.5 % |
| **LB DAMOS** (control) | 4946 | **2567** (68 / 2435 / 64) | **0.519** | 54 023 | **+16.5 %** |

The morphology genuinely shrinks the description: on the primary GORILA_WORD segmentation it replaces
1 165 independent word-units with **709** morphemes (**456 fewer lexical units**) and saves **14.2 %** of
the total code length. Robust across ENTRY/FORMULA and echoed by the LB control. **On the compression
axis, the morphology reduces the parameter count.**

### (2) Held-out predictive: the compression does NOT buy structural generalization

Overall 5-fold bits/word (lower = better), and the SEEN / UNSEEN decomposition:

| dataset | P0 | FLAT | MORPH | RANDNULL | MORPH−P0 (overall) | MORPH−RANDNULL (overall) |
|---|---|---|---|---|---|---|
| LA GORILA_WORD | 24.78 | 15.61 | 14.02 | **13.67** | −10.76 | **+0.35 ± 0.10** |
| LA ENTRY | 26.59 | 20.60 | 18.60 | **18.13** | −7.99 | **+0.47 ± 0.22** |
| LA FORMULA | 24.79 | 17.22 | 15.87 | **15.55** | −8.93 | **+0.32 ± 0.13** |
| LB DAMOS | 34.47 | 17.83 | 16.69 | **15.87** | −17.78 | **+0.82 ± 0.11** |

**UNSEEN word-types only (the true generalization test):**

| dataset | P0 | MORPH | RANDNULL | MORPH−P0 | MORPH−RANDNULL |
|---|---|---|---|---|---|
| LA GORILA_WORD | 32.23 | 26.75 | **26.22** | −5.48 | +0.53 |
| LA ENTRY | 31.49 | 27.37 | **26.91** | −4.11 | +0.46 |
| LA FORMULA | 35.84 | 32.81 | **32.15** | −3.02 | +0.66 |
| LB DAMOS | 36.57 | 27.86 | **26.55** | −8.71 | +1.31 |

Two things to read carefully, because the naive numbers are a trap:

- **The big MORPH−P0 gap (−10.8 bits/word overall) is NOT the advance.** It is dominated by the
  **SEEN** words: MORPH's stem lexicon memorises them (SEEN MORPH−P0 ≈ −13). On SEEN words FLAT
  (pure memorisation) actually *beats* MORPH (GORILA: FLAT 7.79 vs MORPH 8.63) — decomposing a word you
  already hold as an atom costs a little. Memorisation is not generalization.

- **The learned morphology does NOT beat the random-segmentation null — it is consistently, significantly
  *worse*.** MORPH−RANDNULL is **positive on all four datasets** (GORILA +0.35 ± 0.10 ≈ 3.6 σ; ENTRY
  +0.47 ± 0.22; FORMULA +0.32 ± 0.13; DAMOS +0.82 ± 0.11 ≈ 7.6 σ), overall and on UNSEEN. A segmentation
  that cuts words at **random positions**, at the same affixation rate, predicts held-out words *at least
  as well as* the E1-induced A-/-JA morphology. The held-out gain over the raw floor P0 is therefore a
  **generic "any subword lexicon smooths held-out prediction better" effect** — not the specific learned
  structure.

### The Linear B positive control is what makes this bulletproof

Linear B's `-JO/-JA/-O/-A` inflection is real, productive, and generalizing (E1 recovers it). Yet on the
per-word held-out predictive test **the very same non-result appears**: RANDNULL beats the learned MORPH
by **+0.82 bits/word overall (+1.31 on UNSEEN)**. Because a script with *known* real morphology also
fails to show a learned-structure edge over random cuts, the conclusion is not "Linear A has no
morphology." It is that **per-word held-out likelihood, at this model class / corpus scale / short-word
regime, cannot certify a morphology** — the compression it produces is real but does not, by itself,
license a claim that the induced units are the true generative units.

## Verdict — `COMPRESSES_TRAINING__HELDOUT_GAIN_NOT_STRUCTURAL` (all four datasets)

- **Parameter/description-length reduction on training: SUPPORTED.** −14.2 % code length, 1165→709
  lexical units (param ratio 0.61) on LA GORILA_WORD; robust across segmentations and the LB control.
- **Held-out predictive reduction attributable to the learned morphology: NOT SUPPORTED.** MORPH beats the
  raw floor P0 out-of-sample, but so does a rate-matched **random** segmentation — and the learned
  morphology is significantly *worse* than that null (+0.35…+0.82 bits/word, incl. on unseen types). The
  identical outcome on Linear B, whose morphology is genuinely real, shows the predictive test — not
  Linear A — is the limiting factor.

**Net:** the E1 morphology **reduces the count of parameters and compresses the corpus, but that
compression does not translate into held-out predictive power attributable to the specific induced
structure.** By the honest rule stated up front, a morphology that compresses training without a
*structural* held-out advance **does not advance the decipherment**. This stays at L2/L3 anonymous
relative structure — **no values, no licences.** The result is recorded as a bounded negative on the
predictive axis alongside a genuine (but non-load-bearing) compression result.
