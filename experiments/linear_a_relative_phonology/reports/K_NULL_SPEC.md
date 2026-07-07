# K1 — Adaptive Null Battery: SPECIFICATION

**Constitution v2.2** · Art. III (falsification-first) / VII (search receipt) / VIII (effective-n,
multiplicity) / XII (no grading by the creating rule). Highest claim layer **L2/L3**; no phonetic
value assigned; no transfer licence. Seed `20260708`. Script `scripts/k1_adaptive_null.py`; data
`data/K1_nulls.json`; primitives imported from the audited `e1_morphology_models.py` / `e2_formula_grammar.py`.

## Why an adaptive null

The campaign ran ~40 tasks. Each carried **selection degrees of freedom**: *which* segmentation (8
available), *which* morphology family (MDL / Bayesian / paradigm), *which* affix (≈195 candidate
word-initial + word-final signs), *which* site split (full / HT-in / HT-out / LOSO / genre-LOFO),
*which* anchor system (the 5 libation anchors; KU-RO as total-anchor), *which* threshold. A single
"p = 0.0099" is only trustworthy if it survives a null that **reproduces the same selection pipeline**
— a *best-of-selection* null. The published per-affix nulls (e.g. E1 `freq_matched_null`) corrected
for only the 10 *named* tests; they did **not** correct for the full best-of-everything search that
actually chose A-, KU-RO and the libation anchor set.

**Design principle (fail-closed).** The observed statistic is always the campaign's *selected best*
(e.g. A- = the single most productive affix = 47). The null statistic is the *same max* over the same
selection grid, computed on a corpus stripped of the structure under test. Adaptive
p = P(null best-of ≥ observed best). Where a choice makes the null larger (treating correlated
segmentations as independent), we keep it — a **conservative** (harder-to-pass) null.

## Null families and the strength target each must reach

Primary strength target for the morphology track = **A- prefix recurrent-stem productivity = 47**
(global max affix on `SEG_GORILA_WORD`). For the formula track: libation **10 co-occurring anchor
pairs all direction-consistent** (perm-p 5e-5); ledger **KU-RO terminal frac_last_third 0.69 +
followed-by-numeral 0.79**.

| # | null family | how realized | strength target / statistic | min R |
|---|---|---|---|---|
| 1 | **frequency-matched relative classes** | i.i.d. corpus, sign-unigram + word-length preserved; recompute best-of-affix max | best-of-affix ≥ 47 | 1000 |
| 2 | **random relative classes** | every single sign is a singleton relative class; the best-of-affix max IS the max over all singleton classes | best-of-affix ≥ 47 | (=1) |
| 3 | **shuffled morphology** | permute sign order *within* each word (destroys prefix/suffix slots) | best-of-affix ≥ 47 | 1000 |
| 4 | **shuffled segmentations** | re-cut the concatenated sign stream at random boundaries, same length distribution | best-of-affix ≥ 47 | 1000 |
| 5 | **shuffled sign labels (relabel)** | global bijective relabeling of the alphabet | best-of-affix ≥ 47 (invariant control) | 100 |
| 6 | **shuffled sites** | permute site labels, re-run the cross-site both-direction test | best-of-affix clears BOTH HT splits ≥ 16 | 500 |
| 7 | **shuffled formula families / random anchor systems** | pick 5 random recurring sign-substrings (freq-matched to OP/SSR/UNK/IPN/SIR) as anchors; induce order; perm-null | ≥ 10 co-occurring pairs, all consistent | 500 |
| 8 | **random anchors (ledger)** | random recurring ledger word as total-anchor | frac_last_third ≥ 0.69 AND foll-by-num ≥ 0.79 | 500 |
| 9 | **wrong seed labels / random seed subsets** | value-layer: SEED_A = 0 (no secure seed); reproduced as relabeling-invariance | value read-count variance = 0 | 200 |
| 10 | **wrong-language lexica / random cross-script correspondences / shuffled substitutions** | value-layer channels already audited to null in waves 2/4; folded into the relabeling-invariance proof (0 bits) | value bits ≤ 0 | (exact) |

### Adaptive best-of-selection nulls (the decisive tests)

| test | selection DOF reproduced | statistic |
|---|---|---|
| **A. best-of-affix × segmentation × slot** | affix (≈195) × segmentation (8) × {prefix,suffix} | max recurrent-stem productivity, obs 47 |
| **B. cross-site both-direction** | affix (≈195) × {train-HT→test-nonHT, train-nonHT→test-HT} | max over affixes of min(nonHT prod, HT prod), obs 16 |
| **C. random anchor system** | choice of the 5 libation anchors | # co-occurring anchor pairs all-consistent, obs 10 |
| **D. random ledger anchor** | choice of KU-RO as total-anchor | terminal-position + numeral-adjacency, obs (0.69, 0.79) |
| **F. value relabeling** | any consistent value map (bilingual absent, SEED_A=0) | held-out structural read-count variance across relabelings |

## Non-circularity

Every input is a distributional statistic over **anonymous sign identities**. Known values
(pure-vowel {A,E,I,O,U}; the glosses KU-RO='total', libation names) are read **afterward to grade
only** (Art. XII) — never a model input, never a gate. The relabeling-invariance test (F) is the
mechanical proof that the value layer carries 0 selection-exploitable information.

## Statistic conventions

- Empirical one-sided p = (#{null ≥ observed} + 1)/(R + 1).
- Best-of-affix productivity computed one-pass via the exact e1 recurrent-stem criterion
  (`_recurrent`: free word OR residual of ≥2 words).
- Libation perm-null: 20 000 shuffles for the observed; 4 000 per random anchor system (resolution
  floor 2.5e-4 — so the honest "as-strong-as-observed" count uses *≥10 all-consistent pairs*, not the
  resolution-limited perm-p threshold).
