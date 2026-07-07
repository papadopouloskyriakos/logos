# B4 — Synthetic Segmentation Calibration (planted boundaries, dialed nuisances)

**Task:** B4 · **Branch:** research/linear-a-relative-phonology-seals · **Constitution:** v2.2
(Art. III guilty-until-proven · VII search-receipt · VIII effective-n · XII no-grading-by-the-rule-that-made-it)
· **Seed:** 20260708 · **Script:** `scripts/b4_synthetic_segmentation.py` · **Data:** `data/B4_synthetic.json`

## Question
B3 validated six unsupervised segmentation families on *opaque Linear B* (best held-out boundary F1 0.608)
and flagged that Linear A's short units will drive recovery lower — but *how much lower, and why?* B4 answers
mechanically: generate **controlled synthetic syllabic corpora with KNOWN word boundaries**, then run the
**exact B3 families** while dialing up, one at a time, the five nuisances that separate LA from LB. Report
boundary F1 **and the over/under-segmentation failure mode** vs the planted truth, and read off what boundary
accuracy to expect at LA's nuisance levels.

## Non-circularity (Art. XII)
The ground-truth boundaries are a property of the **synthetic generator only** and are used **only to grade**.
No model receives any boundary label: the B3 families are unsupervised (EM/cue rules trained on TRAIN sign
streams, frozen, predicted on held-out TEST). Every corpus is split 70/30 by tablet (seeded).

## Generator
A CV syllabary (5 pure-vowel + 16×5 CV signs = **85 types**, LA/LB scale), a Zipfian root lexicon (1,200
roots, len 1–3), a dedicated closed **suffix** class (morphology), and **8 site sub-lexicons** over a shared
core. A tablet = a sequence of gold words; word ends are the planted boundaries. Corpus ≈ **1,400 multi-word
tablets** per config (≈ B3's 2,202 LB tablets, same order). Five nuisance dials, each swept with the other
four held at the clean baseline:

| dial | meaning | how |
|---|---|---|
| **φ formulaic** | repeated administrative collocations | fraction of tablets = fixed multi-word templates |
| **hap hapax** | rare-word inflation | fraction of tokens replaced by freshly-minted never-repeated nonce words |
| **dmg damage** | broken tablets | per-sign deletion prob; emptied words drop out (boundaries merge) |
| **γ site imbalance** | corpus dominated by few sites | per-site token share ∼ Zipf(γ); rare-site vocab under-trained |
| **mix mixed convention** | scribes disagree where a word ends | fraction of tablets using the *fine* convention (stem \| suffix = two gold words) vs *coarse* (one word) — identical signs, convention-dependent gold |

## The metric trap (read this first)
**Absolute boundary F1 is not comparable across nuisance levels.** Damage and mixed-convention *shorten the
mean word* and thus raise the boundary rate; because every lexicon model **over-cuts**, a higher boundary rate
mechanically lifts its F1 — *and* lifts the cut-everywhere baseline in lock-step. The honest quantity is the
**margin over the strongest baseline** (`all-cut`, F1 = 2r/(1+r) at boundary rate r). All verdicts below use
**margin-vs-all-cut**; raw F1 is shown but is a decoy where the boundary rate moves.

## Result 1 — anchor configs (per model)

`ratio` = predicted boundaries ÷ gold boundaries (>1.15 OVER, <0.85 UNDER). `mBL` = F1 − best(random,fixed);
`mAll` = F1 − all-cut.

**CLEAN baseline** (boundary rate 0.357, mean word 2.44, word-hapax 0.49; best-BL 0.425, all-cut 0.527):

| model | F1 | P | R | ratio | mode | mBL | mAll |
|---|---|---|---|---|---|---|---|
| CUE_TP_min | 0.678 | 0.670 | 0.686 | 1.02 | balanced | +0.253 | +0.151 |
| CUE_BranchEntropy | 0.583 | 0.445 | 0.845 | 1.90 | OVER | +0.158 | +0.056 |
| **BAYESIAN_unigram** | **0.705** | 0.556 | 0.966 | 1.74 | OVER | **+0.280** | **+0.178** |
| MDL | 0.678 | 0.523 | 0.964 | 1.84 | OVER | +0.253 | +0.151 |
| FINITE_STATE_bigram | 0.635 | 0.477 | 0.948 | 1.99 | OVER | +0.209 | +0.107 |
| MULTISCALE_ENSEMBLE | 0.647 | 0.481 | 0.988 | 2.05 | OVER | +0.222 | +0.120 |

**LB-like reference** (longer words, low hapax; boundary rate 0.326, mean word 2.66) reproduces B3: Bayesian
F1 0.670, mAll +0.177 — same regime and order as the real opaque-LB result (B3 Bayesian 0.608). Upper anchor.

**LA-like combined** (mean word **1.62** ≈ GORILA 1.84; boundary rate **0.56**; word-hapax **0.79**; γ=1.6,
φ=0.20, hap=0.45, dmg=0.15, mix=0.25; best-BL 0.551, **all-cut 0.723**):

| model | F1 | P | R | ratio | mode | mBL | **mAll** |
|---|---|---|---|---|---|---|---|
| CUE_TP_min | 0.500 | 0.652 | 0.405 | 0.62 | **UNDER** | −0.051 | −0.223 |
| CUE_BranchEntropy | 0.640 | 0.582 | 0.711 | 1.22 | OVER | +0.089 | −0.083 |
| BAYESIAN_unigram | 0.709 | 0.614 | 0.839 | 1.37 | OVER | +0.158 | −0.014 |
| **MDL** | **0.727** | 0.607 | 0.907 | 1.49 | OVER | +0.176 | **+0.005** |
| FINITE_STATE_bigram | 0.683 | 0.580 | 0.829 | 1.43 | OVER | +0.132 | −0.040 |
| MULTISCALE_ENSEMBLE | 0.718 | 0.593 | 0.910 | 1.53 | OVER | +0.167 | −0.005 |

**Headline.** At LA nuisance levels the best raw F1 (0.727, MDL) *looks* higher than the clean baseline (0.705)
— but its **margin over the all-cut baseline is +0.005**, i.e. **zero real skill**. Every family clears the
random/fixed baselines (mBL +0.13…+0.18) yet **none clears cut-everywhere** (mAll ∈ [−0.22, +0.005]). LA's
short words make the all-cut ceiling (F1 0.72) essentially unbeatable; apparent accuracy is the short-word
artifact, not recovered boundaries. This corroborates B3's caveat and the published LA GORILA F1 0.436 (which
sits *below* its 0.577 all-boundaries ceiling — the same story).

## Result 2 — nuisance sensitivity (margin-vs-all-cut of the best model, BAYESIAN_unigram)

| dial | 0 (clean) | low | mid | high | top | verdict |
|---|---|---|---|---|---|---|
| **φ formulaic** | +0.178 | +0.178 | +0.142 | +0.087 | **+0.054** | erodes skill (repeated collocations get merged) |
| **hap hapax** | +0.178 | +0.143 | +0.121 | +0.082 | **+0.029** | **worst degrader** — no lexicon to learn from |
| **dmg damage** | +0.178 | +0.144 | +0.112 | +0.103 | **+0.064** | erodes skill (raw F1 *rises* — pure baseline artifact) |
| **γ site imbalance** | +0.178 | +0.182 | +0.182 | +0.168 | +0.175 | **no effect** (honest null) at this corpus scale |
| **mix mixed convention** | +0.178 | +0.180 | +0.182 | +0.181 | +0.179 | **no effect on over-cutters** (see below) |

(Levels: φ/mix {.15,.30,.50,.75}; hap {.15,.30,.50,.70}; dmg {.10,.20,.35,.50}; γ {.6,1.0,1.6,2.4}.)

- **Hapax is the dominant killer of genuine skill**: at 82% word-hapax the DP lexicon models retain only
  +0.03 over all-cut. Lexicon-based segmentation needs *repeated* words; LA's high hapax rate is why B3's
  families lose most of their edge there — independent of word length.
- **Formulaic and damage** both halve the skill margin, but for different reasons: formulaic sequences create
  high-frequency multi-word chunks the DP models absorb as single "words" (under-cutting the internal
  boundary); damage shortens words and inflates raw F1 while the *real* margin shrinks.
- **Site imbalance is a null** here — a shared common core keeps the held-out vocabulary trainable even when
  one site dominates. Imbalance alone does not degrade boundary recovery at this scale.
- **Mixed convention is a null *for the over-cutters***: because Bayesian/MDL/FST/ensemble already cut ~1.7×
  too often, the *extra* fine-convention boundaries (which are distributionally real — the closed suffix class
  is highly marked) are "free" recall, so the margin holds flat while raw F1 climbs. The one **precision-
  oriented** model, `CUE_TP_min`, *does* erode under mixing (mAll +0.151 → −0.026): inconsistent gold hurts a
  balanced segmenter but not an over-segmenting one.

## Result 3 — failure-mode characterization
- **Over-segmentation is universal** for the five distributional/lexicon models across *every* config: ratio
  1.5–2.2, recall 0.85–0.99, precision 0.44–0.61. They plant far too many cuts and win F1 on recall. This is
  the same signature B3 saw on real LB (P≈0.46, R≈0.88).
- **`CUE_TP_min` is the lone precision-balanced model** (ratio ≈1.0 at clean/LB) — and the only one whose
  failure mode is *regime-dependent*: in the LA-like short-word regime it flips to **under-segmentation**
  (ratio 0.62, recall 0.40) and drops below baseline. A transitional-probability local-minimum rule has too
  few gaps to find a minimum in 1.6-sign words.
- **Consequence for LA:** any LA boundary set from these families should be read as an **over-segmentation**
  (a superset of the true boundaries) — never as precise word edges. Downstream analyses must be robust to
  ~1.5–2× spurious cuts.

## Verdict
```
SYNTHETIC_SEGMENTATION_CALIBRATION: QUANTIFIED
- Clean/LB-like regime reproduces B3 (Bayesian raw F1 ~0.67-0.71, +0.18 over the all-cut baseline).
- At LA nuisance levels (mean word 1.62, boundary rate 0.56, word-hapax 0.79): raw F1 <= 0.727 BUT
  skill over the strongest (all-cut) baseline collapses to ~0 (best mAll +0.005, MDL; all others <=0).
- NUISANCE RANKING (erosion of genuine skill): hapax > formulaic ~ damage >> site-imbalance ~ mixed-
  convention(~null). High hapax, not damage or mixing, is the binding constraint.
- FAILURE MODE: over-segmentation is universal (ratio 1.5-2.2, recall ~0.95, precision ~0.5);
  CUE_TP_min alone is precision-balanced and flips to UNDER-segmentation on LA-short words.
- CAUTION: raw boundary F1 is CONFOUNDED by boundary rate; damage/mixing raise F1 while eroding skill.
  Report margin-over-all-cut, never bare F1, when comparing across nuisance levels.
TRANSFER_TO_LA: expect ~0 net boundary skill over cut-everywhere at LA's regime; treat any LA
  segmentation as an over-cut superset. L2/L3 structural only; no phonetic/semantic licence earned.
```
