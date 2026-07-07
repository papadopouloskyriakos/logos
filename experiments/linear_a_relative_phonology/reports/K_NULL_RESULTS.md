# K1 — Adaptive Null Battery: RESULTS

**Seed** `20260708` · R_full 500, R_cheap 1000, R_anchor 500 · runtime 130 s · data `data/K1_nulls.json`.
Constitution v2.2 · L2/L3 · no phonetic value. All numbers RUN, not hand-written.

## Headline

The **selection matters enormously**. The published per-affix null put A-'s single-affix chance
productivity at ≈24; the *best-of-195-affixes* null puts it at **≈37**. Correcting for selection
raises the null bar by ~13 productivity units. Even so, three of the four L2/L3 positives clear their
own best-of-selection null; the **cross-site nominal significance does not**.

## 1. Adaptive best-of-affix × segmentation null (target: A- = 47)

| statistic | value |
|---|---|
| observed A- prefix productivity (GORILA_WORD) | **47** = the campaign's best-of-selection |
| observed global max per segmentation | GORILA 47, ROW 38, FORMULA 23, PROB_BOUNDARY 19, ENTRY 11, DIPLOMATIC/MULTI_SCALE/INSCR_CONTEXT 10 |
| null best-of-affix (GORILA) mean | 36.77 |
| null best-of-affix 95th pctile | 43 |
| null best-of-affix max (500 draws) | 48 |
| null best-of-(affix × 8 segmentations) mean | 36.98 |
| **adaptive p (best-of affix × seg ≥ 47)** | **0.008** |

The best-of-affix null routinely reaches 36–43 by frequency alone (the price of searching ≈195
candidates). A- = 47 still sits at the ~99.2nd percentile → **adaptive p 0.008**, *below* the naïve
p_holm 0.050. A- survives the selection correction.

## 2. Cross-site both-direction null (target: min(29,16) = 16)

| statistic | value |
|---|---|
| observed A- non-HT / HT productivity | 29 / 16 (min = 16) |
| null best-of-affix min(nonHT, HT) mean | 15.19 |
| null best-of-affix min max (500 draws) | 22 |
| **adaptive p (some affix clears BOTH ≥ 16)** | **0.42** |

Under best-of-affix selection, *some* affix reaches min-both-direction ≥ 16 in **42 %** of null
corpora. The E3 "both directions p = 0.0099" is a **selection artifact**: the min-16 bar is
unremarkable once affix choice is credited. (A- as an *entity* is still established by test 1; what
fails is the *independent significance* of the cross-site generalization.)

## 3. Random anchor-system null — libation rigid order (target: 10 pairs, all consistent)

| statistic | value |
|---|---|
| observed | 10 co-occurring anchor pairs, all direction-consistent, perm-p 5e-5 |
| candidate recurring substrings | 42 · valid random 5-anchor systems 493 |
| random systems with *all pairs perfect* (any # pairs) | 302 / 493 = **61 %** |
| random systems reaching ≥ 10 pairs AND all perfect | **14 / 493** |
| **adaptive p (as strong as observed)** | **0.030** |

**"Zero inversions" alone is cheap** — 61 % of random anchor systems achieve it, because most have
only 2–6 co-occurring pairs where a rigid order is trivial. The *observed strength* is 10
co-occurring pairs all consistent; only 2.8 % of random systems reach it → **adaptive p ≈ 0.030**.
Survives, but far weaker than the nominal 5e-5.

## 4. Random ledger-anchor null — KU-RO terminal (target: 0.69 / 0.79)

| statistic | value |
|---|---|
| observed KU-RO frac-last-third / foll-by-numeral | 0.692 / 0.795 (39 occurrences) |
| random ledger-word mean frac-last-third / foll-rate | 0.283 / 0.483 |
| random anchors matching BOTH criteria | **0 / 500** |
| **adaptive p** | **0.002** |

KU-RO is a strong positional + adjacency outlier; no random recurring ledger word imitates it. The
arithmetic sum-consistency (E2: 7/31 exact) is a separate relative-structure corroboration untouched
by this positional null. Survives cleanly.

## 5. Corruption battery (target: best-of-affix ≥ 47)

| null family | null mean | null max | discover rate ≥ 47 |
|---|---|---|---|
| frequency-matched i.i.d. | 36.82 | 54 | 0.006 |
| shuffled morphology (within-word permute) | **28.04** | 36 | 0.001 |
| shuffled segmentation (random cuts) | 36.46 | 50 | 0.006 |
| shuffled sign labels (global relabel) | 47.00 | 47 | 1.0 (invariant control) |

- **shuffled morphology** collapses the best-of-affix to ~28 and *never* reaches 47 → destroying
  within-word sign order kills the signal: **there is genuine word-position structure** (independent
  of which sign). Corroborates E5's held-out predictive-gain result.
- **shuffled segmentation / frequency-matched** both hold at ~36 (the selection floor) — matching
  test 1's null bar and confirming 47 is a real excess, not a segmentation artifact.
- **shuffled sign labels** leaves the max at exactly 47 → the structure is **relabeling-invariant
  (value-blind)**; a positive control, not a null.

## 6. Value-layer relabeling-invariance (folds families 9–10)

| statistic | value |
|---|---|
| base held-out structural read-count | 1005 |
| read-count mean over 200 consistent value relabelings | 1005.0 |
| **read-count std** | **0.0** |
| value bits from selection | **0.0** |
| verdict | `RELABELING_INVARIANT_0_BITS` |

Reproduces H3/I1: held-out read-count is **exactly invariant** under every value relabeling → the
value layer carries **0 selection-exploitable bits** (≥10²⁷ relabeling-equivalent twins). The
wrong-seed / random-seed-subset / wrong-language-lexicon / random-cross-script / shuffled-substitution
families are all value-layer channels already audited to null in waves 2 & 4; they fold into this
mechanical zero. **No value positive exists to be a false positive.**

## Net

| positive | nominal p | adaptive-null p | verdict |
|---|---|---|---|
| A- prefixation | 0.050 (Holm) | **0.008** | **SURVIVES** |
| A- cross-site *significance* | 0.0099 | **0.42** | **ARTIFACT** |
| libation rigid order | 5e-5 | **0.030** | **SURVIVES** |
| ledger KU-RO terminal | — | **0.002** | **SURVIVES** |
| value layer (all claims) | null | 0 bits | **chance — nulls confirm nulls** |

See `K_ADAPTIVE_FALSE_POSITIVE_RATE.md` for the campaign-wide false-positive rate and per-positive
reasoning.
