# EPOCH-069 REPORT — Entry-initial words longer than entry-internal words? (L2)

**Verdict: `ENTRY_INITIAL_WORD_LONGER_CROSS_SITE`**

Within a line/entry, the FIRST word is systematically LONGER (more signs) than the
subsequent words — a name-then-modifiers length gradient — and this holds cross-site,
survives leave-one-site-out, and is **NOT** the A-prefix confound.

---

## Question

WITHIN a line/entry, is the FIRST word systematically longer than the subsequent words
(entry opens with a longer 'head' / item name, followed by shorter internal words /
qualifiers), BEYOND a within-line word-order shuffle null, and CROSS-SITE? Critical
confound to control: A-prefixed words are longer and over-represented in initial
positions, so a first-word-longer effect could be merely the A-prefix clustering
entry-initially. The verdict requires the effect to survive EXCLUDING A-initial words.

Layer L2: word-length = sign count; `A` = anonymous E022 slot; no sign values, readings,
or meanings.

## Data

- corpus/silver/inscriptions_structured.json — ordered `stream`.
- LINE = word tokens between consecutive `nl` (num/div/other ignored; words keep in-line
  order). TARGET = lines with >=2 word tokens.
- **n target lines = 363** (matches spec). Per-site first-words: Haghia Triada 177,
  Khania 40, Zakros 33 (3 sites testable at >=20).

## Metric & Null (frozen)

- diff = mean(len FIRST words) − mean(len LATER words), pooled over target lines.
- Null: within EACH line, uniformly shuffle the order of its word tokens; recompute diff;
  one-sided perm p = frac(null diff >= observed). Controls each line's word-length
  multiset + word count.

## Self-check (machinery validity)

The within-line shuffle null has E[diff] = −0.118, **not exactly 0**, because `diff`
pools an *unweighted* first-word mean against a *(len−1)-weighted* later-word mean; under
exchangeability these coincide only if line-mean is uncorrelated with line length. The
null is still valid (it is the true shuffle distribution). The self-check validates the
**empirical null mean (−0.116) against the closed-form analytical E[diff] (−0.118)** —
match to <0.03 confirms the shuffle machinery is correct. The observed diff sits ~11
null-SDs above the null mean.

## Positive Control (SYNTHETIC, gates verdict) — PASSED

- **DETECT** (planted first-longer lines): observed=3.49, perm_p=0.001 (≤0.05). ✓
- **FALSE-POSITIVE** (position-independent lengths): rejection rate=0.000 over 30 draws
  (≤0.10). ✓
- PC is synthetic. Machinery is informative.

## Global

| metric | value |
|---|---|
| n_lines | 363 |
| first_mean | 2.551 |
| later_mean | 1.762 |
| **diff** | **0.789** |
| null_mean | −0.121 (null_sd 0.086) |
| **perm_p** | **0.0002** |

First words are ~0.79 signs longer than later words; observed is ~11 SDs above the null
mean.

## Cross-site (>=20 first-words)

| site | n_first | diff | perm_p | sig |
|---|---|---|---|---|
| Haghia Triada | 177 | 1.108 | 0.0005 | ✓ longer |
| Khania | 40 | 1.227 | 0.0005 | ✓ longer |
| Zakros | 33 | 1.153 | 0.0005 | ✓ longer |

- n_sites_testable = 3; **n_sites_sig same direction = 3**; direction_consistent = TRUE.
- **Leave-one-site-out (excl. Haghia Triada)**: n=186, diff=0.542, perm_p=0.0002.
  Survives.

## A-prefix confound robustness (LOAD-BEARING)

Excluding ALL A-initial words (63 words dropped; 322/363 lines survive with >=2 non-A
words; each line's first word re-derived among the remaining words):

| metric | value |
|---|---|
| n_lines_noA | 322 |
| first_mean_noA | 2.391 |
| later_mean_noA | 1.675 |
| **diff_noA** | **0.716** |
| **perm_p_noA** | **0.0002** |

Per-site (noA): Haghia Triada diff=1.13 (p=0.0005); Khania diff=0.90 (p=0.0005);
Zakros diff=1.19 (p=0.0010) — all still significant.

Non-A first words (mean 2.39) remain far longer than non-A later words (mean 1.70).
A-initial first words are longer still (mean 3.75), so the A-prefix *amplifies* the
effect marginally, but **the effect is NOT A-driven** — it is a general length structure.

## Verdict gate check

| gate | condition | result |
|---|---|---|
| PC passed | detect p≤0.05, FP rate≤0.10 | ✓ PASSED |
| global diff>0 sig | perm_p≤0.05 | ✓ 0.0002 |
| ≥2 sites sig same dir | first longer | ✓ 3/3 |
| survives LOO | perm_p≤0.05 excl HT | ✓ 0.0002 |
| survives A-exclusion | diff_noA>0, perm_p_noA≤0.05 | ✓ 0.716, 0.0002 |

**→ `ENTRY_INITIAL_WORD_LONGER_CROSS_SITE`**

## Bottom line (honest)

Yes. Entries open with a longer word (the 'head') followed by shorter internal words, and
this is a genuine cross-site structural regularity — not an artifact of the A-prefix
clustering entry-initially, not driven by the dominant Haghia Triada corpus, and detected
by a calibrated (PC-passing) within-line shuffle test. The ledger entry has a
name-then-modifiers length gradient at L2.

## Non-circularity

word-length = len(signs); position = order within a line between consecutive `nl`; the
within-line word-order shuffle null makes first/later positions exchangeable while
controlling each line's word-length multiset and word count; A-word exclusion drops all
words whose first sign is `A` from both pools. No sign values, readings, or meanings. L2.

## Deviations

Self-check note (not a protocol deviation): the shuffle null mean is −0.118, not exactly
0, due to pooled-mean weighting (unweighted first vs (len−1)-weighted later). The null is
valid; the self-check validates the empirical null mean against the closed-form
analytical E[diff] (match <0.03). Does not affect perm p or any gate. Documented in
machinery.py and result.json.

## Outputs

- prereg.md, plan_hash.txt, machinery.py, result.json (EPOCH-069/)
- data/epoch_069/per_line.csv, data/epoch_069/summary_stats.json
- reports/EPOCH069_REPORT.md (this file)
