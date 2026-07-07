# E3 — Cross-Site / Cross-Genre Generalization of the E1 Affixation Paradigm

**Branch** `research/linear-a-relative-phonology-seals` · **Seed** 20260708 · **Null** freq-matched
i.i.d. (unigram + length preserved), N=300, Holm-corrected · Data `data/E3_crosssite.json`
Claim layer **L2/L3**, anonymous relative structure only, **no phonetic value assigned**; pure-vowel
{A,I} and -JA names are read AFTERWARD to grade recovery, never a model input (Art. XII).

## Question
C5 flagged **severe Haghia-Triada dependency** (HT = 1891/3147 words = 60.1% of the GORILA-word
corpus). Is the wave-2 / E1 headline paradigm — productive word-**initial A-/I-** prefixation +
word-**final -JA** suffixation, scored by recurrent-stem productivity — a property of the Linear A
administrative *language*, or is it **HT-bound**? The only thing transferred across any split is the
anonymous affix identity {A-, I-, -JA}; productivity and its null are recomputed entirely on the
held-out partition's own sign statistics.

## Headline result — the paradigm does NOT generalize as a whole; it collapses to **A- only**

| Test (held-out partition) | n_words | recur. stems | **A- pre** | **I- pre** | **-JA suf** |
|---|--:|--:|---|---|---|
| Full corpus (reference) | 3147 | 305 | **obs 47, p=0.0099 ✅** | 28, p=0.159 ✗ | 26, p=0.116 ✗ |
| **T2 train HT → test non-HT** | 1256 | 171 | **29 vs 15.1, p=0.0099 ✅** | 17 vs 11.0, p=0.066 ✗ | 14 vs 12.7, **p=0.402 ✗** |
| **T3 train non-HT → test HT** | 1891 | 147 | **16 vs 6.6, p=0.0099 ✅** | 9 vs 10.9, p=0.754 ✗ | 11 vs 5.8, p=0.066 ✗ |

`p` = Holm-corrected one-sided p vs the partition's own frequency-matched null (3 affixes tested).
✅ = clears p<0.05.

**Only word-initial A- prefixation is a robust, cross-HT relative-structural regularity.** It fires
both directions of the HT / non-HT split at the same p=0.0099 — i.e. it is present *and detectable*
in HT alone, in the pooled 51 other sites, and in the whole corpus.

- **-JA suffix does NOT generalize.** On the pooled non-HT test set (well-powered, 171 recurrent
  stems) it sits **at chance** (obs 14 vs null 12.7, p=0.40). It reaches significance only when
  Haghia-Triada tablets are in the partition (T3 p=0.066; T5-tablet p=0.040 below). -JA is a
  **HT/tablet-admin-register artifact**, not a language-wide suffix. This *downgrades* the E1
  "A-/I- + -JA" headline.
- **I- prefix never clears multiplicity** anywhere (best is non-HT pool p=0.066). UNDERDETERMINED.

## T5 — Leave-one-formula-family-out (family = document genre / support)

| Genre held out | n_words | recur. stems | n sig | A- | I- | -JA |
|---|--:|--:|:--:|---|---|---|
| Tablet (admin core) | 1775 | 195 | **2** | obs 30, **p=0.0099 ✅** | 11, p=0.498 | obs 14, **p=0.040 ✅** |
| Stone vessel (**libation**) | 370 | 69 | **0** | 7, p=0.153 | 10, p=0.090 | 7, p=0.339 |
| Clay vessel | 84 | 18 | 0 | 4, p=0.259 | 0, p=1.0 | 2, p=0.571 |
| Nodule | 640 | **6** | 0 | 0 | 0 | 0 — *no power* |
| Roundel | 119 | **7** | 0 | 0 | 0 | 0 — *no power* |

- The paradigm is **administrative-tablet-associated**, NOT a libation-formula phenomenon. The
  libation register (stone vessels, 69 recurrent stems — the second-best-powered partition) shows
  **no affix productivity above its own null** (A-/I-/-JA all p>0.09). So the A-/-JA signal is *not*
  driven by the famous A-TA-I-…-WA-JA / I-DA-MA-TE libation strings; it lives in the tablet ledger
  register. -JA's significance is entirely a tablet effect.
- **Nodules & roundels are single-word documents** (6–7 recurrent stems out of 640/119 words) →
  structurally **zero power**; they cannot test morphology and their nulls are uninformative.

## T4 — Leave-one-site-out (sites with ≥40 words)

| Held-out site | n_words | recur. stems | n sig | best affix |
|---|--:|--:|:--:|---|
| Haghia Triada | 1891 | 147 | **1** | A- (16 vs 6.6, p=0.0099 ✅) |
| Khania | 368 | 41 | 0 | A- (5 vs 3.6, p=0.90) |
| Zakros | 218 | 39 | 0 | A- (5 vs 2.5, p=0.21) |
| Phaistos | 110 | 19 | 0 | — |
| Knossos | 98 | 15 | 0 | — |
| Palaikastro / Arkhalkhori / Tylissos / Malia | 77–41 | 4–18 | 0 | — |

**No individual non-HT site reaches significance** for any affix — but every non-HT site is
**underpowered** (≤41 recurrent stems; Tylissos/Malia have 4). This confirms C5 mechanically: only
Haghia Triada and the *pooled* non-HT set carry enough recurrent-stem support to run the test.

### Power vs signal caveat (important, non-obvious)
Raw word-**initial-A rate is higher OFF Haghia Triada**, not lower — HT 2.5%, Khania 7.1%, Zakros
9.2%, Knossos 10.2% (T1). The A- *prefix presence* is corpus-wide; what is HT-limited is the
*statistical power* to certify it via stem-recurrence, because the small sites have too few
recurrent stems. The pooled non-HT test (T2) recovers the power and confirms A- generalizes.

## Inventory overlap (independent induction, HT vs non-HT)
Jaccard@15 prefixes **0.43**, suffixes **0.36**; Spearman on the shared set 0.32 (pre) / 0.52 (suf).
Shared prefixes {A, DA, I, KA, KU, MI, PA, SA, SI}; shared suffixes {JA, KI, NA, RA, RE, SA, TA, TI}.
Moderate — the induced affix *inventory* partially replicates across the split (A, I, JA all appear
in both), but rank agreement is weak; the two registers do not induce the same paradigm.

## Verdict
**PARTIAL / AFFIX-SPECIFIC GENERALIZATION.** The E1 paradigm is **not** uniformly cross-site.
Mechanically, cross-HT it collapses to a single regularity: **word-initial A- prefixation** (the only
affix significant on a partition disjoint from Haghia Triada, both split directions, p=0.0099). The
**-JA suffix is HT/tablet-admin-bound** (at chance off HT). The **I- prefix is UNDERDETERMINED**
(never clears multiplicity). Genre-wise the paradigm is **tablet-administrative**, not libation. Most
individual non-HT sites and all seal/roundel genres are **structurally underpowered** (C5 confirmed).
No phonetic licence earned; this remains anonymous relative structure at L2/L3.
