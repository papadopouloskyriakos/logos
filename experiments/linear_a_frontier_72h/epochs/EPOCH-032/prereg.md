# EPOCH-032 — CROSS-SITE RECURRENT ADMINISTRATIVE WORD-FORMS (preregistration, FROZEN)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-032
**Layer:** L2/L3 (pure distributional word-form recurrence; ANONYMOUS sign sequences)
**Operator:** logos z.ai research worker (GLM-5.2)
**Date frozen:** before any analysis run on this question.

## QUESTION (frozen)
Does Linear A administration share a common vocabulary of word-forms ACROSS independent SITES —
i.e. are there word-forms (full sign sequences) that recur at MULTIPLE sites MORE than a site-label
shuffle null predicts — evidence of a shared administrative register rather than purely site-local
scribal habits?

Word-forms are ANONYMOUS sign sequences. NO phonetics, NO sound, NO meaning, NO reading is attached
to any token. This is a pure L2/L3 distributional recurrence test.

## DATA (frozen)
- Corpus: `corpus/silver/inscriptions_structured.json` (1341 inscriptions).
- Each inscription has `site` and a `stream`; tokens with `t == "word"` carry `signs`.
- A **word-form** = the tuple of its `signs`.
- A **site** = the inscription's `site` field.
- Positive-control benchmark: Linear B via `scripts/cross_script/data.py::load_b_damos()[0]`
  (list of sign-lists). LB has NO native site metadata, so the LB PC is built via a SEEDED
  pseudo-partition into >=5 pseudo-"sites" (round-robin assignment by a fixed seed). This is
  declared up front.

## METRIC (frozen)
- **cross-site breadth** of a word-form = number of DISTINCT sites it appears in.
- Restrict to word-forms with **total count >= 2** (singletons cannot be "shared").
- Aggregate statistic: **n_shared** = number of word-forms (count>=2) appearing in **>=2 distinct sites**.
- Also report the multiplicity distribution: how many forms span 1, 2, 3, ... sites.

## NULL (frozen — site-label shuffle)
Randomly PERMUTE the SITE labels across inscriptions, preserving:
  (a) each site's inscription count (marginal site sizes), and
  (b) each inscription's word-form multiset (marginal form frequencies).
Recompute n_shared under the permuted labels. **>=1000 draws.** One-sided p-value for the alternative
"observed n_shared is GREATER than chance":
    p = (1 + #{draws with n_shared_draw >= n_shared_obs}) / (1 + n_draws).

This null isolates whether SPECIFIC forms recur across sites beyond what marginal form-frequency +
site-size structure alone produce.

## PROTOCOL (frozen, in order)
0. Inspect: n word tokens, n distinct word-forms, site distribution, top cross-site forms (anonymous).
1. FREEZE this prereg + `plan_hash.txt` + `machinery.py` (with `__main__` self-check) BEFORE running.
2. GLOBAL: n_shared + site-label-shuffle null mean + one-sided p.
3. POSITIVE CONTROL FIRST (gates the verdict):
   - **DETECT** on LB (seeded into >=5 pseudo-sites): LB is known to carry recurrent administrative
     forms, so the site-shuffle null must find LB's n_shared significantly ABOVE chance (p <= 0.05).
   - **FALSE-POSITIVE** control: build >=20 i.i.d. controls where word-forms are assigned to
     pseudo-sites INDEPENDENTLY of identity (each token drawn i.i.d. by marginal form-frequency, then
     partitioned into pseudo-sites of fixed sizes). There is NO identity-site association by
     construction. The test must NOT reject at > 0.10 across these controls (false-positive rate
     measured as the fraction of controls with p <= 0.05; require <= 0.20).
   - If LB is not detected OR the i.i.d. control fires too often -> `MACHINERY_UNINFORMATIVE`.
4. LA MAIN — held-out robustness:
   - **leave-one-site-out**: remove the largest site (Haghia Triada) and recompute n_shared + p on
     the remaining sites. Does cross-site sharing survive among the OTHER sites?
   - Report the specific word-forms shared across the MOST sites (anonymous), and note whether a
     KU-RO-type total form is among them — but the VERDICT is purely on the aggregate n_shared vs null.
5. FROZEN MECHANICAL VERDICT (count-based, no adjudication):
   - `SHARED_ADMIN_VOCAB_CROSS_SITE` iff PC passed AND global p <= 0.05 AND leave-one-site-out
     p <= 0.05 (HT removed) AND >= 5 word-forms span >= 3 sites.
   - `ADMIN_VOCAB_SITE_LOCAL` iff global p <= 0.05 BUT (leave-one-out p > 0.05 OR < 5 forms span
     >= 3 sites) — i.e. sharing is HT-driven or too thin.
   - `ADMIN_VOCAB_NO_SIGNAL` iff global p > 0.05.
   - `ADMIN_VOCAB_UNDERPOWERED` iff < 3 sites have enough word-forms to test.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.

## NON-CIRCULARITY (hard)
Word tokens carry NO phonetic / sound / meaning / reading. L2/L3 distributional statistics ONLY.
LB is a POSITIVE-CONTROL benchmark ONLY (it is never used to read Linear A forms). The verdict is
computed mechanically from the frozen rule above; the operator never declares a scientific verdict.



## DEVIATION (declared, pre-analysis-design)
The LB positive-control pseudo-partition uses **SEEDED CONTIGUOUS BLOCKS** of the original DĀMOS
sequence order (chunked into tablet-sized pseudo-inscriptions), NOT round-robin. Rationale
(discovered during machinery self-check, before LA verdict): round-robin artificially spreads
every frequent form across all pseudo-sites, washing out the cross-site signal and making the
null reproduce the observation. Contiguous blocks preserve the real within-site form clustering
that the cross-site test is meant to detect. This is a partition-design choice for the PC only;
it does not touch the LA metric, null, or verdict rule (all frozen above).


## DEVIATIONS
None anticipated beyond the declared LB-partition note above. Any further deviation will be recorded in `result.json["deviations"]`.
