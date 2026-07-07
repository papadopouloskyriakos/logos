# C3 — Linear B Substitution Calibration

**Task C3.** Run the C1 candidate-generation (word-level one-sign minimal pairs) **plus a
substitution-graph weight** on **opaque Linear B** and measure, per relation type, how well it
recovers the KNOWN structure of the script — using Linear B phonetic **values only to grade**
(never as a detector input; Constitution v2.2 Art. XII). This tells us **which relation types the
method can trust when it is later pointed at Linear A**, where no values exist to grade.

- Engine: `experiments/linear_a_relative_phonology/scripts/c3_lb_calibration.py`
- Data: `experiments/linear_a_relative_phonology/data/C3_lb_calibration.json`
- Seed 20260708, deterministic, pure stdlib + repo loader. All counts script-generated (Inv. 12).

## Corpus & non-circularity

- **DĀMOS Mycenaean: 13,562 syllabic wordform tokens / 4,946 types** (`X.load_b_damos`, re-parsed
  per-tablet to keep neighbour order; token total verified byte-for-byte against the loader).
- Candidate generation and the substitution graph consume **sign IDENTITY only** (value tokens as
  opaque symbols). LB `(consonant, vowel)` parses are read **afterwards, to grade**. **73** distinct
  standard-value signs are attested and gradable; **2,628** scorable sign-pairs.

## Relation types (graded from LB values)

| type | definition | grading |
|---|---|---|
| **same_vowel** | differing signs share the VOWEL, differ in consonant (KA/TA, RO/TO) | consonantal contrast in a fixed vocalic slot |
| **same_consonant** | share the CONSONANT, differ in vowel (RO/RA, JA/JO) | the vocalic-alternation slot — Greek inflection |
| **spelling_variant** | allograph doublet, same value modulo a trailing digit (A/A2, RA/RA2) | known orthographic variant, not a new value |
| **morphophonological** | same_consonant **and word-FINAL** (-jo/-ja/-je, -to/-ta, -o/-a) | Mycenaean case/gender endings |
| **scribal_error / cross** | minimal pair sharing **no** feature, not an allograph | scribal slip **or** two unrelated lexemes (honesty control) |

**Baselines (rival scorers, same universe):** *frequency-matched random* (`freq[a]·freq[b]`),
*edit-distance* (unweighted candidate generation = does the pair substitute at all), *context-only*
(cosine of the two signs' in-word neighbour vectors), *formula-only* (substitution weight from
LONG ≥3-sign frames only). **Method** = substitution-graph context weight (# distinct word-frames
licensing the substitution). **Null** = degree-preserving (Maslov–Sneppen) rewiring of the sign
substitution graph, ×300.

## Headline: what the method can and cannot recover

The **decisive** measure is *within-minimal-pair discrimination* — given a one-sign minimal pair,
can the method say **which relation type** it is (positives = class, negatives = the 14,063
cross-class minimal pairs)? Edit-distance is flat here by construction (every minimal pair is
distance 1), so this isolates the graph-weight signal.

| relation type | method AUC (vs cross minimal pairs) | strong-edge lift vs degree-preserving null | verdict for LA |
|---|---:|---:|---|
| **morphophonological (final same-C)** | **0.744** | — (subset of same-C) | **TRUST** |
| **same_consonant** | **0.704** | **1.4–2.5×** (z ≈ 3.6–5.0, p≈0.003) | **TRUST** |
| **same_vowel** | 0.612 | 1.15–1.28× (z ≈ 0.7–4.0) | **SUGGESTIVE** (weak) |
| **spelling_variant (allograph)** | **0.363** (below chance) | — | **DO NOT** rank by weight — needs a context detector |
| **scribal_error / cross** | — (is the negative class; **69.2%** of all minimal pairs) | ≈1.0 | **IRREDUCIBLE NOISE** |

- **The method recovers the CONSONANT-held (vocalic-alternation) axis best**, and best of all when
  it is **word-final** — exactly where Greek inflection lives. Top same-consonant edges are the real
  Mycenaean paradigm swaps: **JA/JO (98 frames), TO/TA (60), RO/RA (49), KA/KO (46), WO/WE (42)**.
- **The vowel-held (consonantal) axis is only weakly recovered** (AUC 0.61; lift ~1.2, z marginal at
  small k). Top same-vowel edges KA/TA, KO/TO, RO/TO are real but far less repetition-concentrated.
- **Allographic spelling variants are anti-recovered by substitution WEIGHT** (AUC 0.36): A2/A,
  RA2/RA occur in only 5–16 frames, so weight ranks them *low*. They are instead best caught by the
  **context-only** baseline (sign-pair AUC **0.668**) — an allograph shares its base sign's
  distribution. **Lesson: on LA, do not rank candidate spelling variants by substitution frequency;
  use a distributional/context detector.**
- **69.2%** of opaque LB minimal pairs (14,063 / 20,311) are cross-class — share no phonological
  feature. This is the multiple-testing base rate the method must fight, and it correctly does **not**
  promote them. On LA the same majority of minimal pairs will be noise.

## Sign-pair recovery AUC — method vs each baseline

Positives = sign-pairs of the relation; negatives = all other scorable sign-pairs.
(relation_counts: same_vowel 512, same_consonant 122, spelling_variant 9, cross 1,985)

| scorer | same_vowel | same_consonant | spelling_variant | any_phon |
|---|---:|---:|---:|---:|
| **method (subst-graph weight)** | 0.536 | 0.633 | 0.526 | 0.563 |
| frequency-matched random | 0.507 | 0.568 | 0.327 | 0.519 |
| edit-distance (exist) | 0.505 | 0.552 | 0.515 | 0.517 |
| context-only (cosine) | 0.558 | **0.659** | **0.668** | 0.591 |
| formula-only (long frame) | **0.561** | **0.672** | 0.663 | **0.596** |

- **The method beats frequency and edit-distance everywhere** → it is *not* a frequency artifact,
  and unweighted candidate-generation alone carries almost no relation-type information (AUC ≈ 0.5).
- **Restricting to long/formulaic frames sharpens recovery** (formula-only is the best single scorer
  for same_consonant and any_phon): multi-sign fixed contexts are the cleanest substitution
  evidence. **Recommendation: weight LA candidates by long-frame support, not raw pair count.**
- **Context-only is the right tool for allographs / spelling variants** (0.668 vs method 0.526).

## Word-pair recovery vs frequency-matched random negatives

Against **60,933** frequency-matched random word pairs, both the method and edit-distance separate
*every* relation class at **AUC = 1.00** (minimal pairs differ by one sign; random pairs do not) —
i.e. **candidate generation reliably retrieves minimal pairs, but retrieval alone cannot type
them.** Neighbour-word context / formula baselines are near-useless at the word level here
(AUC ≈ 0.50–0.53): DĀMOS wordforms sit in short administrative lists, so external neighbour context
is too sparse to license a "formula" the way it does inside a word. **The usable signal is
intra-word (the substitution graph), not inter-word context** — which matches LA, where word
segmentation itself is uncertain.

## Degree-preserving null sweep (strong edges)

| top-k edges | any_phon lift (z, p) | same_vowel lift (z) | same_consonant lift (z) |
|---:|---|---|---|
| 20 | 1.54 (3.28, 0.007) | 1.15 (0.72) | **2.52 (3.82)** |
| 40 | 1.40 (3.57, 0.003) | 1.18 (1.36) | **2.09 (3.59)** |
| 80 | 1.40 (4.74, 0.003) | 1.22 (2.23) | **1.94 (4.84)** |
| 160 | 1.36 (6.42, 0.003) | 1.28 (3.94) | 1.67 (4.99) |
| 320 | 1.23 (5.99, 0.003) | 1.19 (4.03) | 1.39 (4.16) |

Strong substitution edges are significantly enriched for feature-sharing above a degree-preserving
null at every cutoff (any_phon p ≈ 0.003 throughout) — the enrichment is **not** hubbiness. The
enrichment is **carried by same_consonant** (lift up to 2.5×); same_vowel is only marginal at the
very top and grows as k widens.

## Calibration verdict — trust map for Linear A

**CALIBRATED.** On known-truth Linear B the C1-generation + substitution-graph method:

1. **TRUSTS same-consonant / morphophonological (word-final vocalic) alternations** — AUC 0.70–0.74,
   degree-preserving lift up to 2.5× (z≈5). These recover real inflectional paradigms. → On LA,
   the strong-weight, consonant-held / word-final substitution families are the ones to promote.
2. **Treats same-vowel (consonantal) contrasts as SUGGESTIVE only** — real but weak (AUC 0.61,
   lift ~1.2). → On LA, do not over-read consonant-swap families without corroboration.
3. **Must NOT rank spelling variants (allographs) by substitution weight** (AUC 0.36) — use the
   **context/distributional** detector instead (0.668).
4. **Cannot separate scribal-error/unrelated cross-pairs from noise** (69% of minimal pairs) — and
   correctly does not try. → On LA, expect the majority of raw minimal pairs to be this bucket; the
   tiering must down-weight them, exactly as C1 does.
5. **Method-quality rule for LA:** weight by **long-frame (formulaic) support**, not raw pair count
   (formula-only was the best single sign-pair scorer); the method beats both a frequency baseline
   and unweighted candidate generation, so its edges are genuine relative structure, **not** a
   frequency or edit-distance artifact — but nothing above L2/L3 is licensed (no value transfers).

Guilty-until-proven-innocent: this calibration says the machine *can* recover consonant-held /
morphophonological structure **where the truth is known**; it does **not** assign any value on LA,
and the LA corpus is far smaller, so even the TRUSTED relation types remain candidates until a
held-out, non-GORILA-dependent check confirms them.
