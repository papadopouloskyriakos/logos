# EPOCH-071 PREREGISTRATION (FROZEN)

**Task:** EPOCH-071 — Does the libation (stone-vessel / religious) corpus have a
cross-site-recurring FORMULA, unlike the site-local administrative vocabulary?
(genre-dependent lexicon sharing; L2/L3)

**Status:** FROZEN before any global computation. PC is synthetic (stated).

## Question (mechanical, value-blind)

Do anonymous word-FORMS (sign tuples, len>=2) recur ACROSS SITES in the
stone-vessel (libation) corpus BEYOND what word-form frequencies + per-site
token counts predict — i.e. a genuine cross-site formula — and does this
CONTRAST with the administrative corpus (Tablet+Nodule+Roundel)?

Pure structural word-form recurrence (L2/L3). Word-forms are anonymous
sign-sequences. NO reading, NO phonetic value, NO meaning. We do NOT claim what
the formula says, only whether a fixed sequence recurs cross-site beyond
frequency+site-size confounds.

## Data

- Corpus: `corpus/silver/inscriptions_structured.json`
- LIBATION corpus = inscriptions with `support == "Stone vessel"` (99 inscriptions).
- ADMIN corpus = inscriptions with `support in {Tablet, Nodule, Roundel}`.
- Word-TOKEN = a word with signs; Word-TYPE = tuple of signs, len>=2.
- Genre = the physical `support` field (given, not inferred).

## Metric (FROZEN)

S = sum over multi-sign word-TYPES of max(0, n_distinct_sites - 1)
= total cross-site recurrence mass. A type at 5 sites contributes 4; a
site-local type contributes 0.

Computed separately:
- S_lib over the stone-vessel corpus (its own inscriptions/sites).
- S_admin over the admin corpus (its own inscriptions/sites).

## Null (FROZEN, per corpus)

Token->site reassignment null: reassign each word-TOKEN to a site, preserving
BOTH marginals exactly:
  - each word-form keeps its total count (form frequency preserved)
  - each site keeps its total token count (site size preserved)
This breaks the form<->site association but holds frequency + site-size fixed,
so any cross-site recurrence in S is BEYOND frequency + site-size.

Implementation: sequential hypergeometric sample of the form x site
contingency table with fixed margins (exact marginal-preserving; equivalent in
distribution to Patefield/AS159). Validated by self-check to preserve both
marginals exactly over many draws.

- >=1000 draws (using 2000).
- perm p = frac(null S >= observed S), one-sided (cross-site recurrence beyond
  frequency+site-size). Add-one smoothing.
- Normalized effect = S_obs / null_mean.

## Positive Control (SYNTHETIC — stated)

PC is fully synthetic (no real data in PC).

(a) DETECT: plant a synthetic corpus with a genuine formula (several forms each
    at ALL sites, count = n_sites, one token per site; rest singletons —
    matching real corpus structure where most forms are singletons). Confirm S
    is enriched (perm p <= 0.05). Estimate power over >=20 draws.
(b) FALSE-POSITIVE: plant a synthetic corpus with NO formula, where each form's
    tokens are assigned to sites proportional to site size (pure
    frequency-driven overlap). Confirm S is NOT enriched (rejection rate
    <= 0.10 over >=20 draws).

PC gates the verdict: if power < 0.5 OR false-positive rate > 0.10 ->
MACHINERY_UNINFORMATIVE.

## Frozen Mechanical Verdict

- LIBATION_FORMULA_CROSS_SITE iff PC passed AND S_lib enriched beyond its
  reassignment null (perm p <= 0.05 AND ratio > 1).
- LIBATION_FORMULA_SITE_LOCAL_LIKE_ADMIN iff S_lib NOT enriched AND S_admin
  also not enriched.
- LIBATION_NO_CROSS_SITE_FORMULA iff S_lib not enriched (recurrence = frequency
  artifact), regardless of admin.
- LIBATION_UNDERPOWERED iff <2 stone-vessel sites have >=20 tokens OR PC power
  to detect a planted formula < 0.5.
- MACHINERY_UNINFORMATIVE iff PC failed calibration.

## Non-circularity

Anonymous word-forms (sign tuples); genre = physical support field (given, not
inferred from text); the token->site reassignment null preserves word-form
frequencies AND per-site token totals, so cross-site recurrence in S is beyond
frequency + site-size. L2/L3 only. No reading, no phonetic value, no meaning.

## Deviations

None anticipated. If the PC fails calibration, verdict = MACHINERY_UNINFORMATIVE
and no scientific claim is made.
