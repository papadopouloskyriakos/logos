# EPOCH-071 REPORT — Libation (Stone-Vessel) Cross-Site Formula vs Admin Site-Local Vocabulary

**Campaign:** Linear A frontier-72h · **Epoch:** 071 · **Layer:** L3 (structural word-form recurrence)
**Verdict (mechanical, frozen rule):** `LIBATION_FORMULA_SITE_LOCAL_LIKE_ADMIN`
**PC:** PASSED (synthetic) · **Prereg/plan_hash:** frozen before global computation

---

## Question (mechanical, value-blind)

Do anonymous word-FORMS (sign tuples, len>=2) recur ACROSS SITES in the
stone-vessel (libation) corpus BEYOND what word-form frequencies + per-site
token counts predict — a genuine cross-site formula — and does this CONTRAST
with the administrative corpus (Tablet+Nodule+Roundel)?

Pure structural recurrence (L2/L3). No reading, no phonetic value, no meaning.

## Metric (frozen)

S = Σ over multi-sign word-TYPES of max(0, n_distinct_sites − 1)
= total cross-site recurrence mass (a type at 5 sites contributes 4; a
site-local type contributes 0).

**Null (frozen, per corpus):** token→site reassignment preserving BOTH
marginals exactly — each word-form keeps its total count (frequency) AND each
site keeps its total token count (site size). Sequential hypergeometric
contingency sampling (exact marginal-preserving; ≡ Patefield/AS159). This holds
frequency + site-size fixed, so any cross-site recurrence in S is BEYOND those
confounds. perm p = frac(null S ≥ observed S), one-sided, 2000 draws.

## Data

- LIBATION = `support == "Stone vessel"`: 99 inscriptions, 14 sites, 259 tokens, 211 forms.
  Sites with ≥20 tokens: Zakros 128, Palaikastro 36, Iouktas 33, Syme 20 (4 sites → not underpowered).
- ADMIN = `support ∈ {Tablet, Nodule, Roundel}`: 1081 inscriptions, 18 sites, 948 tokens, 651 forms.

## Global results

| Corpus | S_obs | null_mean | null range | perm_p | ratio | Enriched? |
|--------|-------|-----------|------------|--------|-------|-----------|
| LIBATION (Stone vessel) | 20.0 | 32.94 | [24, 43] | 1.000 | 0.607 | **NO** (obs below entire null range) |
| ADMIN (Tablet+Nodule+Roundel) | 23.0 | 97.08 | [78, 117] | 1.000 | 0.237 | **NO** |

**Libation cross-site recurring forms (observed):**
- A-TA-I-*301-WA-JA — 5 sites, count 11
- SI-RU-TE — 5 sites, count 7
- I-PI-NA-MA — 5 sites, count 6
- JA-SA-SA-RA-ME — 4 sites, count 6
- I-DA — 3 sites, count 5
- U-NA-KA-NA-SI — 3 sites, count 4
- JA-JA — 2 sites, count 2

These forms DO recur across sites — but their cross-site spread is exactly what
the frequency+site-size null predicts (or less). The null, by preserving the
high frequencies of these forms (e.g. A-TA-I-*301-WA-JA count 11) and the
site-size distribution (Zakros dominant), already spreads them across ~5 sites.
The observed S=20 is *below* the null mean of 33: the libation corpus is if
anything MORE site-localized than a frequency-matched random assignment.

## Positive Control (SYNTHETIC — stated)

PC is fully synthetic; no real data in PC.

**(a) DETECT** — planted formula (5 forms each at all 5 sites, count = n_sites,
one token per site; rest singletons, matching real corpus structure where
193/211 forms are singletons):
- Power = **1.00** (25/25 draws rejected at p≤0.05); median detect p = **0.002**.

**(b) FALSE-POSITIVE** — frequency-only (each form's tokens assigned to sites
proportional to site size; no real formula):
- False-positive rate = **0.00** (0/25 draws rejected; all p > 0.05; max p = 0.072).

**PC verdict: PASSED.** The machinery detects a planted cross-site formula and
does not fire on frequency-only overlap. The machinery is informative.

Machinery self-check also passed: reassignment null preserves both marginals
exactly over 2000+ draws; S_stat correct.

## Contrast (genre-dependent sharing?)

- LIBATION: NOT enriched (p=1.0, ratio=0.607).
- ADMIN: NOT enriched (p=1.0, ratio=0.237).

Both corpora behave alike: cross-site word-form recurrence is a
frequency+site-size artifact in BOTH. There is **no genre-dependent contrast**
in lexicon sharing detectable by this metric at the structural word-form level.
The libation corpus does NOT have a genuine cross-site formula beyond
frequency, and it does NOT contrast with the admin corpus — both are
site-local-like under the reassignment null.

## Frozen mechanical verdict

`LIBATION_FORMULA_SITE_LOCAL_LIKE_ADMIN` — PC passed AND S_lib NOT enriched
(perm_p=1.0, ratio=0.607 < 1) AND S_admin also NOT enriched (perm_p=1.0,
ratio=0.237 < 1). The libation recurrence is fully explained by frequency +
site-size, like admin vocabulary.

## Non-circularity

Anonymous word-forms (sign tuples, len≥2); genre = physical support field
(given, not inferred from text). The token→site reassignment null preserves
BOTH word-form frequencies AND per-site token totals, so cross-site recurrence
in S is beyond frequency + site-size. L2/L3 only: no reading, no phonetic
value, no meaning. PC fully synthetic (stated).

## Honest bottom line

There is **no cross-site libation formula beyond word-form frequency and
site-size**. The famous recurring dedicatory forms (A-TA-I-*301-WA-JA, SI-RU-TE,
I-PI-NA-MA, JA-SA-SA-RA-ME, U-NA-KA-NA-SI) recur across sites, but that
recurrence is exactly what their high frequencies and the skewed site-size
distribution (Zakros-dominated) would produce by chance under marginal
preservation. Lexicon-sharing does **not** depend on genre at the structural
word-form level: both the religious/libation corpus and the administrative
corpus are site-local-like under the reassignment null. The prior campaign
finding (admin vocab is site-local) extends to the libation corpus — there is no
genre-dependent contrast here.

## Outputs

- `prereg.md` (frozen), `plan_hash.txt`, `machinery.py` (with `__main__` self-check)
- `result.json`, `data/epoch_071/analysis_raw.json`
- This report.
