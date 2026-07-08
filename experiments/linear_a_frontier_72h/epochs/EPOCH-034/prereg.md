# EPOCH-034 PREREGISTRATION (FROZEN)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-034
**Layer:** L2/L3 (positional / document-structural statistics ONLY)
**Date frozen:** before any computation on the test metric.

## 1. QUESTION (frozen)

Do **A-INITIAL words** (word tokens whose FIRST sign is `A`) occupy the
**INSCRIPTION-INITIAL position** (the FIRST word token of an inscription) MORE than chance,
and is that effect **ROBUST across independent SITES**?

This tests a **DOCUMENT-STRUCTURAL (heading) role** for the A- class purely positionally.
"A-" and "heading" are ANONYMOUS positional labels: no phonetics, no sound, no meaning, no reading.
"heading" = DOCUMENT-INITIAL POSITION only.

**Leads:** E025 (A- is a productive word-INITIAL prefix); E033 (A-initial words are DEPLETED on
ledger entries = counted items, suggesting A- words are labels/headings not items).

## 2. DATA (verified)

- `corpus/silver/inscriptions_structured.json` — list of inscriptions; each has `site` and an
  ORDERED `stream`. Word tokens have `t=='word'` + `signs`.
- **Word sequence of an inscription** = the `word` tokens in stream order (non-word tokens ignored
  for position).
- **A-initial word** = a word whose first sign is `'A'`.
- **Inscription-initial word** = the FIRST word token of an inscription. Only inscriptions with
  **>=2 word tokens** count (a single-word inscription has no positional contrast).
- **LB positive control** via `load_b_damos` (DĀMOS Mycenaean wordforms). DĀMOS has NO site /
  inscription metadata -> a SEEDED partition into pseudo-inscriptions is used (stated explicitly).

## 3. METRIC (frozen)

Among inscriptions with >=2 word tokens:

- `p_A_first` = fraction whose FIRST word is A-initial.  (TEST axis)
- `p_A_last`  = fraction whose LAST  word is A-initial.  (CONTROL axis — A- should be
  INITIAL-biased, NOT final-biased.)
- `base_A_rate` = per-inscription mean of (A-initial words / total words) — the within-inscription
  base rate of A-initial words.

## 4. NULL (frozen — WITHIN-INSCRIPTION POSITION PERMUTATION)

For each inscription, **randomly permute its word ORDER** (word multiset held fixed), recompute
`p_A_first`; >=2000 draws. **One-sided p** for "A-initial words are inscription-initial MORE than
chance" = fraction of draws with permuted `p_A_first` >= observed.

This holds each inscription's word multiset fixed and tests POSITION only — exactly analogous to the
E023/E024 within-word sign-position null, lifted to the word-in-document level. It is **calibrated by
construction**: permuting positions = H0 of no positional preference, so the false-positive rate
under H0 is controlled at the nominal level (verified by the FALSE-POSITIVE arm of the PC).

## 5. PROTOCOL (in order)

0. **Inspect:** n inscriptions with >=2 words; global `p_A_first` (observed) vs mean A-rate;
   per-site counts.
1. **FREEZE** this prereg + `plan_hash.txt`; write `machinery.py` with `__main__` self-check.
2. **GLOBAL:** observed `p_A_first`; position-permutation null mean + one-sided p; analogous
   `p_A_last` (control axis).
3. **POSITIVE CONTROL FIRST (gates verdict).** On LB:
   - Build pseudo-inscriptions by chunking DĀMOS wordforms into ordered groups (seeded; no site
     metadata in DĀMOS -> SAY SO).
   - **DETECT (planted heading bias):** force a chosen sign-class to be inscription-initial in
     X% of pseudo-inscriptions (plant a heading bias); the position-permutation null MUST reject
     (p<=0.05) in the correct direction (initial-biased).
   - **FALSE-POSITIVE:** on position-randomized pseudo-inscriptions (word order permuted within
     each pseudo-inscription = exact H0), rejection rate (frac p<=0.05) MUST be <=0.10 across
     >=30 independent sets.
   - If it cannot detect a planted heading bias OR fires on randomized position ->
     `MACHINERY_UNINFORMATIVE`.
4. **LA MAIN — CROSS-SITE held-out:** per site with **>=15 qualifying inscriptions** (>=2 words
   each), compute observed `p_A_first` + position-permutation p; count sites significant
   (p<=0.05) in the SAME direction (initial-biased). **Leave-one-site-out** on the largest site
   (Haghia Triada): exclude it, recompute global p.
5. **FROZEN MECHANICAL VERDICT (count):**
   - `A_HEADING_ROLE_CROSS_SITE_ROBUST` iff PC passed AND global p<=0.05 (A-first > chance) AND
     >=3 sites individually significant same direction AND survives leave-one-site-out.
   - `A_HEADING_ROLE_SITE_LOCAL` iff global significant BUT <3 sites significant OR direction flips
     OR collapses under leave-one-site-out.
   - `A_HEADING_ROLE_NO_SIGNAL` iff global p>0.05.
   - `A_HEADING_UNDERPOWERED` iff <3 sites have >=15 qualifying inscriptions.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.

   (Order of precedence: MACHINERY_UNINFORMATIVE > UNDERPOWERED > NO_SIGNAL > SITE_LOCAL >
   CROSS_SITE_ROBUST, evaluated top-down; first match wins.)

## 6. OUTPUTS (exact PATH CONTRACT paths)

`prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json`,
`reports/EPOCH034_REPORT.md`, `data/epoch_034/`.

## 7. NON-CIRCULARITY (hard)

Tokens carry NO phonetic / sound / meaning / reading. L2/L3 positional statistics ONLY. LB is a
POSITIVE-CONTROL benchmark ONLY (it is never used to read or validate a Linear A claim; it only
certifies that the machinery can detect a planted positional effect and does not fire on noise).
