# EPOCH-066 REPORT — Accounting-scale site register within the Tablet class

**Layer:** L2 (pure structural quantity — numeral magnitude only; no sign values, no commodity identities, no reading, no metrology)
**Scope:** SINGLE-CLASS (Tablet). Only the Tablet class has >=2 sites with >=30 numerals, so this is a within-class site test, honestly scoped.
**Verdict (frozen, mechanical):** `ACCOUNTING_SCALE_SITE_LOCAL`

## Question
Within the Tablet class (the dominant LA administrative document type), does
numeral MAGNITUDE (accounting scale, the corpus `num` token value `v`) vary by
SITE — and is the effect GENERAL across sites (a site register) or DRIVEN BY
ONE outlier site (collapses under leave-one-site-out)?

## Data (verified)
Corpus `corpus/silver/inscriptions_structured.json`; Tablet (`support=="Tablet"`)
`num` tokens with integer `v`, grouped by `site`. Sites with >=30 Tablet numerals:

| Site | n | median | mean |
|---|---:|---:|---:|
| Haghia Triada | 829 | 5 | 28.50 |
| Khania | 121 | 2 | 15.76 |
| Phaistos | 33 | 1 | 7.70 |
| Arkhalkhori | 33 | 4 | 6.91 |
| Tylissos | 31 | 10 | 60.90 |

n_sites = 5, n_numerals = 1047. Per-site medians span an order of magnitude
(1..10), matching the contract.

## Metric & null (frozen)
- `obs_H` = tie-corrected Kruskal-Wallis H on magnitude `v` grouped by SITE
  (rank-based, robust to heavy right skew).
- Null: permute SITE labels among Tablet numerals (preserve per-site n AND the
  Tablet magnitude multiset); recompute H; 5000 draws; one-sided
  `perm_p = frac(null H >= obs H)`.

## Positive control (synthetic — gates verdict)
PC is SYNTHETIC. Two arms:
- DETECT: planted per-site magnitude shift (one site's magnitudes x8) -> flagged,
  detect_p = 0.0005 (<=0.05). PASS.
- FALSE-POSITIVE: random site labels (no effect), 20 draws -> 0/20 rejected
  (false_pos_rate = 0.00 <= 0.10). PASS.

**PC verdict: PASSED.** Machinery is informative. (Self-check also confirmed
the tie-corrected KW matches scipy exactly, and the null is calibrated at
~4% rejection under no-effect.)

## Global result (within Tablet)
- obs_H = **45.07**
- null mean H = 4.09
- perm_p = **0.0002** (5000 draws)

The within-Tablet site effect on accounting scale is overwhelmingly significant.

## Robustness — leave-one-site-out
Recompute obs_H + perm_p after dropping each site in turn:

| Dropped site | obs_H (remaining 4) | perm_p | sig |
|---|---:|---:|:---|
| Arkhalkhori | 44.12 | 0.0002 | yes |
| Haghia Triada | 33.74 | 0.0002 | yes |
| Khania | 26.81 | 0.0002 | yes |
| Phaistos | 28.46 | 0.0002 | yes |
| Tylissos | 35.38 | 0.0002 | yes |

**LOO_ALL_SIG = true.** The effect stays significant under every single-site
drop. Critically:
- Dropping the **magnitude-outlier Tylissos** (median 10, mean 60.9) leaves
  obs_H = 35.38, p = 0.0002 — not a Tylissos artefact.
- Dropping the **dominant Haghia Triada** (829/1047 = 79% of numerals) leaves
  obs_H = 33.74, p = 0.0002 over the remaining 4 sites — not an HT-dominance
  artefact.

The effect is GENERAL across sites, not one-site-driven.

## Frozen mechanical verdict
PC passed AND global site effect significant (perm_p=0.0002 <= 0.05) AND
survives ALL leave-one-site-out drops (perm_p=0.0002 for every single-site
removal) -> **ACCOUNTING_SCALE_SITE_LOCAL**.

## Bottom line
Within the Tablet class, accounting scale (numeral magnitude) carries a
**general SITE register**: it differs strongly by site and the difference is
not driven by any single site — it survives dropping both the magnitude
outlier (Tylissos) and the dominant site (Haghia Triada, 79% of numerals).
This is a genuine cross-site structural register on the quantity channel,
distinct from the document-class magnitude effect (E028/E055) and the
word-length site register (E065). Single-class (Tablet) scope is explicit.

## Non-circularity
magnitude = corpus `num` token integer `v` (given); site = `site` field;
class fixed = Tablet (`support`); null permutes SITE labels among Tablet
numerals preserving per-site n and the Tablet magnitude multiset. L2 only:
no sign values, no commodity identities, no reading, no metrological arithmetic.

## Outputs
- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-066/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-066/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-066/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-066/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_066/`
