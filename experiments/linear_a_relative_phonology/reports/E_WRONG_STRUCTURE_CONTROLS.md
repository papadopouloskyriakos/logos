# E5 — Wrong-Structure Controls

**Constitution v2.2 · Art. III (falsification-first) / VII (search receipt) / VIII (multiplicity) / XII (no grading by the creating rule).**
Highest claim layer **L2/L3** (anonymous relative morphology). **No phonetic value assigned; no transfer licence earned.**
Deterministic seed `20260708`. Script `scripts/e5_wrong_structure.py` → data `data/E5_wrongstruct.json`.

## Question

Wave-2 characterised the Linear A signal as an anonymous relative-morphology structure (productive
word-**initial** A-/I- prefixation + a weak `-JA` final). A structure that only *describes* the
derivation set (overfit) will not beat its own corruptions **out of sample**. E5 asks the
falsification question directly:

> Does the REAL induced morphology carry **held-out predictive value** that WRONG structural
> hypotheses — shuffled affixes, shuffled stems, random cuts, site-shuffled / frequency-matched /
> wrong-typology corpora — do **not**?

## Metric — held-out predictive gain (bits/word)

Every word is segmented into a short morph sequence `[prefix?] stem [suffix?]` (single-sign affixes,
non-empty stem). A morph-**bigram** language model (add-α bigram → morph-unigram → sign-unigram base
measure `G0`, so every string is scorable) is trained on the training fold; a **no-morphology**
baseline is the same LM trained on whole-word (single-morph) segmentations. For a held-out word:

```
gain(word) = bits_baseline(word) − bits_morph(word)      (positive ⇒ morphology helps)
```

The **bigram** (not unigram) LM is what makes the corruptions bite: it is the `stem→suffix` /
`prefix→stem` **transitions** that a real paradigm predicts and a shuffle destroys. 5-fold CV on
`SEG_GORILA_WORD` (n=3147 words, 1369 multi-sign, V=259 signs). The productive-affix inventory is
learned **per fold** by the stem-recurrence criterion only (Art. XII — never graded by known values;
no phonetic input).

## Result — real morphology has genuine held-out gain

| quantity | mean (bits/word) | 95% CI | positive? |
|---|---|---|---|
| real gain, all words | **+2.812** | [2.58, 3.04] | yes |
| real gain, multi-sign words only | **+6.266** | [5.77, 6.74] | yes |
| real baseline-free advantage (learned vs random seg) | **+0.760** | [0.62, 0.91] | yes |

## Controls — the real morphology must beat all of them

### (A) Label corruptions of the real segmentation — paired, same held-out words, baseline fixed

Each corruption re-trains the morph LM on a corrupted **training** segmentation (25 permutations
averaged); held-out words keep their real segmentation. Paired bootstrap (2000 resamples).

| control | control gain | real − control | 95% CI | p(real ≤ ctrl) | real beats? |
|---|---|---|---|---|---|
| shuffled_suffixes (kills `stem→suffix`) | +2.091 | **+0.721** | [0.63, 0.82] | 0.0005 | **yes** |
| shuffled_stems (kills both transitions) | +1.157 | **+1.655** | [1.51, 1.81] | 0.0005 | **yes** |
| random_segmentation (random cuts, same #morphs) | +2.389 | **+0.423** | [0.31, 0.54] | 0.0005 | **yes** |

The **specific** learned segmentation carries predictive value beyond "having some segmentation":
real beats random-cut by +0.42 bits and beats stem-shuffle by +1.66 bits, both with CI excluding 0.

### (B) Corpus-level nulls — fresh pipeline on a null corpus (60 realizations each)

Two statistics are reported per null:

- **absolute whole-word-baseline gain** — **CONFOUNDED** across corpora and NOT used for the verdict.
  Destroying a corpus removes verbatim whole-word recurrence (real LA's dominant regularity), which
  *weakens the whole-word baseline* and thereby *inflates* apparent morph gain. This is why every
  null shows a **higher** absolute gain (≈4.4 bits) than real LA (2.8) — an artefact of the baseline,
  not evidence that noise is more morphological than LA.
- **baseline-free learned-vs-random advantage** (bits by which the learned segmentation beats a
  random segmentation of the *same* held-out words) — baseline-invariant, so **comparable across
  corpora**. This is the valid cross-corpus statistic and gates the verdict.

| null corpus | baseline-free null mean | 95% range | real (0.760) beats? | p(null ≥ real) |
|---|---|---|---|---|
| site_preserving_shuffle (within-site sign permutation) | 0.564 | [0.50, 0.63] | **yes** | 0.016 |
| frequency_matched_pseudo (i.i.d. global unigram) | 0.537 | [0.47, 0.63] | **yes** | 0.016 |
| synthetic_wrong_language (planted medial-infix grammar) | 0.782 | [0.66, 0.92] | no | 0.639 |

`synthetic_wrong_language` is **not** a no-structure null: it is a corpus with **densely planted**
morphology (recurrent stems + a closed medial-infix set) of the *wrong typology* for a prefix/suffix
segmenter. It is a **detector positive-control / upper reference**: the pipeline extracts *more*
learned-vs-random advantage from it (0.782) than from real LA (0.760), exactly as expected when more
morphology is present. Real LA is not required to beat a more morphologically-rich language; it is
required to beat corpora with **no** morphology, and it does (both genuine nulls, p = 0.016).

## Verdict — `REAL_STRUCTURE_BEATS_WRONG_STRUCTURE_CONTROLS`

| gate | result |
|---|---|
| real held-out gain positive | **PASS** (+2.81 all / +6.27 multi-sign, CI > 0) |
| beats all 3 label corruptions (paired) | **PASS** (all p = 0.0005, CI excludes 0) |
| beats both no-morphology corpus nulls (baseline-free) | **PASS** (both p = 0.016, real above 97.5-pctile) |
| beats planted-morphology reference | not a gate — **FALSE by design** (bounds LA richness from above) |

## Honest reading (what this does and does NOT license)

1. **The wave-2 structure is real, not an overfit artefact.** It generalises: the learned
   segmentation predicts held-out words better than every wrong-structure hypothesis with no
   morphology, and better than arbitrary corruptions of itself. This survives Art. VIII multiplicity
   (6 controls; real tops all falsification-relevant ones).
2. **The signal is modest, and repetition dominates it.** The absolute morph-over-whole-word gain
   is small (2.8 bits all words) precisely because LA's dominant compressible regularity is
   **verbatim whole-word repetition** (administrative recurrence), which the baseline already
   captures — morphology is a thin incremental layer on top. LA carries *less* morphological
   regularity than a densely-planted synthetic grammar (0.760 vs 0.782 bits advantage).
3. **No promotion.** This is still **anonymous relative structure**. No phonetic value, no lexical or
   semantic content, is assigned or implied. Highest layer **L2/L3**; SEMANTIC+ transfer remains
   `NOT_AUTHORIZED`. E5 raises confidence that there is *a* real morphological signal to read — it
   does not read it.

## Reproduce

```
python3 scripts/e5_wrong_structure.py     # seed 20260708; writes data/E5_wrongstruct.json
```
Config: 5-fold CV; α=0.5, β=1.0; prod_min=3; 25 permutations/label-control; 60 null-corpus
realizations; 2000 bootstrap resamples. Primitives `_residual_index`, `_recurrent` imported from
`scripts/e1_morphology_models.py` (audited).
