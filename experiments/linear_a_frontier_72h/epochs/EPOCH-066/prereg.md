# EPOCH-066 PREREGISTRATION (FROZEN)

## Task
EPOCH-066 — Within the TABLET class (physical support), does NUMERAL MAGNITUDE
(accounting scale, the corpus `num` token value `v`) vary by SITE, and is the
effect GENERAL across sites (a site register) or DRIVEN BY ONE outlier site
(collapses under leave-one-site-out)?

## Layer
L2 — pure structural quantity. The numeral VALUE is a magnitude. NO sign values,
NO commodity identities, NO reading, NO metrological arithmetic. Only the
number's magnitude by site.

## Scope (honest)
SINGLE-CLASS test. Only the Tablet class has >=2 sites with >=30 numerals, so
the test is run within Tablet only. The functional (document-class) axis was
handled in E028/E055; the site register on word-length in E065. This epoch is
the SITE axis for the QUANTITY channel within the single class that has numeral
power.

## Data
- corpus: `corpus/silver/inscriptions_structured.json`
- magnitude = integer `v` of `num` tokens (given by corpus)
- site = `site` field
- class fixed = Tablet (`support == "Tablet"`)
- eligible sites: those with >=30 Tablet numerals
  (verified: Haghia Triada, Khania, Phaistos, Tylissos, Arkhalkhori — 5 sites,
   n_total = 1047)

## Metric (frozen)
`obs_H` = tie-corrected Kruskal-Wallis H on numeral magnitude `v` grouped by
SITE, over Tablet numerals from sites with >=30. Rank-based, robust to heavy
right skew.

## Null (frozen)
Permute SITE labels among the Tablet numerals (preserving per-site n AND the
Tablet magnitude multiset); recompute H; >=2000 draws.
`perm_p = frac(null H >= obs H)`, one-sided.

## Robustness (frozen)
Leave-one-site-out: recompute `obs_H` + `perm_p` after dropping EACH eligible
site in turn. Effect is GENERAL iff perm_p<=0.05 under ALL single-site drops
(especially dropping the magnitude-outlier Tylissos and the largest site HT).
ONE-SITE-DRIVEN iff any single drop makes it non-significant.

## Positive Control (synthetic — gates verdict)
PC is SYNTHETIC. Two arms:
- (a) DETECT: plant a per-site magnitude shift (multiply one site's magnitudes)
  into a Tablet-like corpus; confirm site test flags it (perm_p<=0.05).
- (b) FALSE-POSITIVE: plant magnitudes with site labels assigned at RANDOM
  (no site effect); confirm NOT flagged (rejection rate <=0.10 across >=20 draws).
If miscalibrated -> MACHINERY_UNINFORMATIVE.

## Frozen Mechanical Verdict
- ACCOUNTING_SCALE_SITE_LOCAL iff PC passed AND within-Tablet site effect
  significant (perm_p<=0.05) AND survives ALL LOO drops (perm_p<=0.05 every
  single-site removal) — a GENERAL site register on accounting scale.
- ACCOUNTING_SCALE_SINGLE_SITE_DRIVEN iff global site effect significant BUT
  at least one single-site drop makes it non-significant.
- ACCOUNTING_SCALE_INVARIANT iff within-Tablet site effect NOT significant.
- ACCOUNTING_SCALE_UNDERPOWERED iff <2 sites have >=30 Tablet numerals.
- MACHINERY_UNINFORMATIVE iff PC failed.

## Non-circularity
magnitude = corpus `num` token `v` (given); site = `site` field; class fixed =
Tablet (`support`); null permutes SITE labels among Tablet numerals. L2 only.
No reading, no sign values, no commodity identities, no metrology.
