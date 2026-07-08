# EPOCH-036 PREREGISTRATION (FROZEN)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-036
**Layer:** L2/L3 (distributional sign-usage statistics ONLY)
**Date frozen:** BEFORE computing the test p-value. The METRIC, NULL, and VERDICT RULE below
are committed before the null is run on the observed data.

## 1. QUESTION (frozen)

E032 showed WORD-FORMS are site-local. This epoch asks the SIGN-INVENTORY question: do
independent SITES share the SAME sign-frequency profile — i.e. a common writing-system
fingerprint (the signs that are frequent at one site are frequent everywhere) — or do sites
DIVERGE (dialect-like), and is any single site a clear OUTLIER with a divergent profile?

Pure distributional sign-usage statistics. Signs are ANONYMOUS ids (the corpus sign tokens as
written). No phonetics, no sound, no meaning, no reading, no cognacy. "Concordance" is a
distributional statistic, NOT evidence of shared language.

## 2. DATA (verified)

- `corpus/silver/inscriptions_structured.json` — list of inscriptions; each has `site` and a
  `stream`. Sign tokens are the entries of each `word` token's `signs` list.
- **Per-site sign frequency** = count of every sign token over all word tokens of all that
  site's inscriptions.
- **Qualifying site** = a site with **>=100 sign tokens** total. (Inspection, pre-freeze: 8
  sites qualify — Haghia Triada, Khania, Zakros, Knossos, Palaikastro, Phaistos, Iouktas,
  Arkhalkhori. Union inventory = 234 anonymous sign ids.)
- **Union inventory** = the set of all sign ids attested at any qualifying site. Each site's
  frequency vector is built over this common inventory (unattested signs = count 0).
- **LB positive control** via `load_b_damos()[0]` (DĀMOS Mycenaean wordforms). DĀMOS has NO
  site metadata -> SEEDED partition into >=5 pseudo-sites (stated explicitly). LB is a
  positive-control benchmark ONLY; it never enters the LA verdict except to gate the machinery.

## 3. METRIC (frozen)

**CONCORDANCE** = the MEAN pairwise Spearman rank correlation of the per-site sign-frequency
vectors across the qualifying sites. For each site, rank the union-inventory signs by their
frequency at that site; correlate the two rankings for every site pair; average over all pairs.
High concordance => a shared writing-system fingerprint (frequent signs are frequent everywhere).

## 4. NULL (frozen — WITHIN-SITE SIGN-LABEL SHUFFLE; calibrated by construction)

For each site, take its frequency vector over the union inventory and **randomly PERMUTE which
count attaches to which sign id** (a full permutation of the sign labels on that site's vector,
preserving the site's frequency multiset/shape but destroying cross-site sign-IDENTITY
alignment). Recompute the mean pairwise Spearman over all sites. **>=1000 draws**. **One-sided
p** for "observed concordance > shuffled" = fraction of draws with shuffled concordance >=
observed.

Calibration rationale: under H0 of no shared sign-IDENTITY fingerprint, shuffling sign labels
leaves each site's frequency SHAPE intact but severs the identity correspondence between sites,
so shuffled concordance centres near 0 (verified at freeze: null mean ~0.00, std ~0.01). The
false-positive rate under H0 is therefore controlled at the nominal level (verified by the
FALSE-POSITIVE arm of the PC).

## 5. POSITIVE CONTROL (gates the verdict) — on LB (>=5 SEEDED pseudo-sites)

(a) **DETECT** — LB is ONE shared script, so its seeded pseudo-sites MUST show concordance
    significantly ABOVE the shuffle null (p <= 0.05).
(b) **FALSE-POSITIVE** — build pseudo-sites whose sign-frequency vectors are INDEPENDENT random
    permutations (no shared fingerprint): the test MUST NOT reject at a rate > 0.10 across
    >=20 such control sets.

If LB's shared fingerprint is NOT detected OR the test fires on independent controls ->
`MACHINERY_UNINFORMATIVE` (no LA verdict is issued).

## 6. LA MAIN (held-out / outlier structure)

(a) **Leave-one-site-out** — recompute concordance with each site removed in turn. Is the
    concordance driven by all sites or by a single pair?
(b) **Per-site average correlation** — for each site, its mean Spearman correlation to all other
    sites. Flag a low OUTLIER = a site whose mean correlation is > 2 SD below the across-site
    mean of per-site mean correlations, OR the clear minimum with a gap to the next.

## 7. FROZEN MECHANICAL VERDICT RULE

- `SIGN_FREQ_CONCORDANCE_CROSS_SITE` iff PC passed AND observed concordance significant
  (p <= 0.05) AND concordance survives leave-one-site-out (not driven by a single pair) AND no
  strong outlier site.
- `SIGN_FREQ_CONCORDANCE_WITH_OUTLIER` iff concordance significant (p <= 0.05) BUT >=1 site is a
  clear low outlier (divergent sign-frequency profile) -> report which.
- `SIGN_FREQ_NO_CONCORDANCE` iff observed concordance NOT significant (p > 0.05).
- `SIGN_FREQ_UNDERPOWERED` iff < 4 sites have >= 100 sign tokens.
- `MACHINERY_UNINFORMATIVE` iff PC failed.

## 8. NON-CIRCULARITY

Signs carry NO phonetic / sound / meaning / reading. All statistics are L2/L3 distributional
sign-usage only. LB is a positive-control benchmark ONLY. The verdict is a mechanical
consequence of the frozen rule + the PC gate; the operator never adjudicates.
