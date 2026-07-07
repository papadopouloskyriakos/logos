# Stage D — constraint mining (no semantic claims)

**Articles:** VII, VIII, XII, XIII, XVI, XXII. **Claim layer:** L2–L3 (structure/function). 5-agent mining
(`wf_b5d7fd20`) on the Stage-B cleaned phonetic material (944 wordform types, 878 multi-sign, subscript-
normalized, logograms removed), all held-out. **No value-informative constraint; no novel structure.**

| sub | verdict | held-out result |
|---|---|---|
| **D1 formula grammar** | `CONFIRMS_KNOWN` | Nothing beyond the known libation chain (genre-locked, 7 stone vessels) + the KU-RO/KI-RO word→number admin marker. Template coverage 0% under site- and support-holdout; recurring-frame count at chance (p=0.53); only libation beats the order-shuffle null. Corpus too shallow (mean 2.3 words/inscription). |
| **D2 morphology** | `NULL` | Clean material does **not** change the prior morphology null. The stem+affix paradigm model does not beat a properly-smoothed bigram on unseen-stem families (λ=0.9: plain bigram *beats* morph, CI excludes 0). No multi-sign morphemes (k=1 reproduces the score). The "affixes" are the known positional sign-frequency skew. **The naive unigram comparison would have been a FALSE POSITIVE — the honest control (interpolated bigram) erased it.** Has power → NULL, not NO_POWER. Value-free (relabeling-invariant). |
| **D4 accounting closure** | `CONFIRMS_KNOWN` | Typing fractions does **not** raise closure: 8/31 exact both integer-only and with fractions (25.8%). Typing fixes HT104 and breaks a spurious HT13 coincidence (net zero) — improves *fidelity*, adds no counting power. The Bennett A700 glyph-fraction hypothesis is **inert** (0 of the closure problems use raw A700 glyphs). Re-derives KU-RO=total (Bennett 1950s); opaque tokens; zero value constraint. |
| **D5 cross-site/support invariance** | `CONFIRMS_KNOWN` | **A genuine held-out positive:** word-**initial** positional grammar survives simultaneous site+support removal AND held-out third-genre validation (cross-genre r=0.607 p=0.001; held-out r up to 0.931 p=0.0005), beating a metadata-preserving null. Residual consonantal structure persists beyond the pure vowel-initial rule. **But it is the known CV-syllabary phonotactics — value-free, not a new constraint.** Word-final grammar cleanly localizes the libation genre. |
| **D7 compression** | `CONFIRMS_KNOWN` | **A genuine held-out positive:** the induced grammar compresses held-out documents (series-disjoint) at **1.42 bits/tok vs 1.77 best baseline (positional-bigram), 2.57 unigram** — +0.33 over all six baselines + both shuffled controls. **But the compressed structure is the known LA administrative list format** (word→numeral→line-break, totals penultimate, support-conditioned layout). Reads token categories, not values. |

## Synthesis

The cleaned corpus contains **real, held-out, generalizable structure** — word-initial phonotactics invariant
across genres, and an administrative document grammar that beats every baseline on unseen documents. This is
scientifically solid (and the D2 false-positive-erasure shows the gates work). **But every bit of it is
already-known epigraphy** (the CV syllabary, the admin list format, the libation formula, KU-RO = total),
**value-free, and adds no constraint on the ~92 syllabic values.** Morphology is a confirmed NULL even on
clean material. The value layer is now **empty across every internal channel** — distributional, formula,
morphology, accounting, invariance, compression.

The only remaining value lever is **external anchors (Stage F)**. Per Stage A's diagnosis and the two prior
preregistered cross-script negatives, that is where the campaign stands or falls.
