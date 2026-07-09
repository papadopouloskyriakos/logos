# EPOCH-059 REPORT — CROSS-SITE SUB-LEXICAL SHARING (shared morphology; L2)

**Campaign:** Linear A frontier-72h
**Layer:** L2 (pure distributional n-gram statistics; anonymous sign IDs)
**Verdict (mechanical):** `SHARED_SUBLEXICAL_INVENTORY_CROSS_SITE`
**PC:** PASSED

---

## 1. Question

At the intermediate granularity — sign **bigrams/trigrams** (sub-word sequences = candidate
shared affixes/formulae) — is there a **shared sub-lexical inventory** that recurs across
sites **beyond what shared single-sign frequencies alone predict**?

- E036: single-sign *frequencies* are shared cross-site (shared script).
- E032: whole *word-forms* do NOT recur cross-site (site-local vocabulary).
- E039: a single A-prefix is shared.

A YES ⇒ the "shared grammar" includes shared **morphology** (recurrent multi-sign elements)
beyond the single A-prefix. A NO ⇒ shared structure bounded to signs + positional grammar.

## 2. Discipline (non-circular)

- Anonymous sign IDs only. No sign values, readings, phonetics, or meanings. L2 only.
- **The crux of the null:** it preserves each site's single-sign (unigram) frequencies by
  construction (per-site independent draws from each site's *own* unigram distribution).
  Therefore any detected cross-site bigram sharing is **beyond shared signs**. The shared-signs
  confound (E036) is explicitly absorbed: the null S is substantial (~61) precisely because
  shared signs produce shared bigrams; the **signal is the observed excess**.

## 3. Data

- `corpus/silver/inscriptions_structured.json` — word tokens (`t=='word','signs'`).
- Word-internal sign bigrams = adjacent sign pairs within a word (len≥2).
- **9 sites qualify** (≥50 word-internal bigrams): Haghia Triada, Zakros, Khania, Knossos,
  Palaikastro, Phaistos, Iouktas, Arkhalkhori, Syme.

## 4. Metric (frozen)

- **Observed S** = number of distinct bigram TYPES recurring across ≥3 qualifying sites.
- **Null:** for each site, regenerate its bigram multiset by sampling the SAME number of
  sign-pairs, each pair = two INDEPENDENT draws from THAT SITE'S OWN unigram frequency
  distribution. ≥500 realizations; permutation p = frac(null S ≥ observed S).

## 5. Positive Control (gates verdict) — PASSED

| Arm | Result | Target |
|-----|--------|--------|
| (a) DETECT (planted shared sub-lexical inventory) | detection rate **1.000** (20/20 trials), median p=0.000 | ≥0.80 |
| (b) FALSE-POSITIVE (shared unigrams, independent bigrams) | rejection rate **0.040** (1/25) | ≤0.10 |

The machinery detects planted shared morphology and does **not** fire on shared-unigrams-only
— proving the unigram-preserving null removes the shared-signs confound.

## 6. Global Result

| Quantity | Value |
|----------|-------|
| Qualifying sites | **9** |
| Distinct bigram types (union) | **1045** |
| Observed S (≥3 sites) | **96** |
| Observed S (≥2 sites) | 255 |
| Null mean S (500 realizations) | **61.078** (range 41–82) |
| Permutation p | **0.0000** |
| Observed / null ratio | **1.572** |
| Mean pairwise Jaccard | **0.0597** |

Observed S (96) exceeds the maximum of the null distribution (82) across 500 realizations.
The excess is **beyond shared signs** (the null preserves per-site unigram frequencies).

### Trigram robustness

| Quantity | Value |
|----------|-------|
| Qualifying sites (trigram) | 7 |
| Observed trigram S (≥3 sites) | **6** |
| Null mean | **0.010** (max=1) |
| Permutation p | **0.0000** |

The trigram signal points the same direction as the bigram result, though it rests on a small absolute count (6 types).

## 7. Frozen Mechanical Verdict

PC passed AND observed S exceeds the unigram-null (perm p ≤ 0.05) ⇒

### `SHARED_SUBLEXICAL_INVENTORY_CROSS_SITE`

Sign sequences (bigrams recur; trigrams point the same direction but on a small count) recur cross-site **beyond** what shared
single-sign frequencies predict. There is a **shared sub-lexical inventory** — recurrent
multi-sign elements (candidate shared affixes/formulae) — beneath the site-local word-forms
(E032). The cross-site bigram overlap is **not** just shared signs.

## 8. Bottom line

There **is** shared sub-lexical structure beyond shared signs. The observed cross-site bigram
recurrence (96 types across ≥3 sites) is 1.57× the unigram-preserving null (p=0.0000), and the
null already absorbs the shared-signs confound (it preserves each site's sign frequencies and
still produces ~61 shared bigrams). The trigram robustness check (6 observed types vs 0.01 null mean, across 7 qualifying sites) is consistent in direction, though small in absolute count. This means
the "shared grammar" extends from shared signs (E036) + positional grammar into shared
**morphology** — recurrent multi-sign sequences — even though whole word-forms remain
site-local (E032). Anonymous sequences; no readings.

## 9. Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-059/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-059/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-059/machinery.py`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-059/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_059/run_analysis.py`
- `experiments/linear_a_frontier_72h/data/epoch_059/analysis_raw.json`
- `experiments/linear_a_frontier_72h/reports/EPOCH059_REPORT.md`
