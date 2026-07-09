# EPOCH-059 — COORDINATOR CORRECTION (SUPERSEDING, Art. XVII)

**GLM's `result.json` in this directory is RETAINED UNALTERED as the append-only record of what the worker
produced. Its verdict is SUPERSEDED by this correction. The authoritative verdict is in `EPOCH_LEDGER.yaml`.**

## What GLM reported
`verdict: SHARED_SUBLEXICAL_INVENTORY_CROSS_SITE` — cross-site sign-bigram recurrence S=96 vs null mean 61,
perm p=0, ratio 1.57; trigram 6 vs null 0.01, p=0. A cross-site *positive*.

## Why it is WRONG (null-construction bug)
`machinery.py` builds the null with:
```python
S_null = null_distribution_S({s: uni for s in sites}, site_n_pairs, sites, ...)   # line ~138
```
`{s: uni for s in sites}` maps **every site to one shared `uni` distribution** instead of each site's **own**
unigram distribution. The frozen prereg requires *per-site* unigrams ("two independent draws from THAT SITE'S
OWN unigram distribution"). The shared-distribution bug deflates the null, fabricating an excess.

## Corrected computation (machinery's OWN `statistic_S` + `null_distribution_S`, correct per-site unigrams)
| n-gram | observed S (≥3 sites) | correct per-site null mean | perm p | ratio |
|---|---|---|---|---|
| bigram | 96 | **86.6** | **0.093** | 1.11 |
| trigram | 11 | **28.1** | **1.00** | 0.39 (obs *below* null) |

Cross-checked by an independent from-scratch null: bigram null 87.4, p=0.13 — same conclusion.

## Corrected verdict
**`NO_SHARED_SUBLEXICAL_BEYOND_SIGNS`** — cross-site bigram/trigram overlap is fully explained by the shared
single-sign frequencies (E036); there is **no shared multi-sign morphology beyond signs + the A-prefix**.
Sub-lexical structure is **site-local**, like whole words (E032) and document typology (E058).

## Process lesson
The gate's `repro_check` verified only the *observed* statistic (S=96, correct), not the *null* — so it did not
catch the null bug. **Null-dependent positives must have the null independently recomputed in `repro_check`.**
This catch is invariant #2/#3 working as designed: the model never grades its own outcome; a positive is guilty
until independently proven.
