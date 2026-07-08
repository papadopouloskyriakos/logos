# EPOCH-035 PREREGISTRATION (FROZEN)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-035
**Layer:** L2/L3 (positional / document-structural statistics ONLY)
**Date frozen:** BEFORE computing any p-value on the test metric. The candidate SELECTION RULE
and the METRIC below are committed before the null is run.

## 1. QUESTION (frozen)

Is there a recurring WORD-FORM over-represented in **inscription-FINAL position** (the LAST word
token of an inscription — the mission-named "KU-RO terminal / total ledger slot"), and is that
effect **ROBUST across independent SITES**?

This is the SYMMETRIC counterpart of E034 (which found the A- class marks inscription-INITIAL /
heading position). Here we ask the document-END question: a "total / summary-line" slot. Tested
PURELY POSITIONALLY and ANONYMOUSLY — the data surfaces which form; we do NOT assume or name it.
No phonetics, no sound, no meaning, no numeral arithmetic. "total-slot" = INSCRIPTION-FINAL
POSITION only.

## 2. DATA (verified)

- `corpus/silver/inscriptions_structured.json` — list of inscriptions; each has `site` and an
  ORDERED `stream`. Word tokens have `t=='word'` + `signs`.
- **Word sequence of an inscription** = the `word` tokens in stream order (non-word tokens ignored
  for position).
- **Inscription-final word** = the LAST word token of an inscription. Only inscriptions with
  **>=2 word tokens** count (a single-word inscription has no positional contrast).
- **LB positive control** via `load_b_damos` (DĀMOS Mycenaean wordforms). DĀMOS has NO site /
  inscription metadata -> a SEEDED partition into pseudo-inscriptions is used (stated explicitly).

## 3. CANDIDATE SELECTION RULE (frozen, pre-committed — avoids post-hoc cherry-picking)

**CANDIDATE** = the word-form with the MOST inscription-FINAL occurrences, among forms with
**total count >= 8 AND final count >= 5**. Selection is by FINAL COUNT. If no form meets the
threshold -> `TERMINAL_SLOT_UNDERPOWERED`.

(Inspection performed BEFORE freezing the p-value computation: the surfaced candidate is the
single-sign anonymous sequence `NI` — final count 22, total 71. This identifier is reported only
as an anonymous sign sequence; the VERDICT does not depend on any assumed value of it.)

## 4. METRIC (frozen)

The candidate's **FINAL-POSITION ENRICHMENT**: among ALL its occurrences within >=2-word
inscriptions, the fraction that are the LAST word of their inscription.

- `final_enrichment` = (candidate occurrences that are inscription-final) / (all candidate
  occurrences in >=2-word inscriptions).  (TEST axis)
- `initial_rate` = (candidate occurrences that are inscription-initial) / (all candidate
  occurrences).  (CONTROL axis — a total-slot form should be FINAL-biased, NOT initial-biased.)

## 5. NULL (frozen — WITHIN-INSCRIPTION POSITION PERMUTATION)

For each inscription, **randomly permute its word ORDER** (word multiset held fixed), recompute the
candidate's final-position count; **>=2000 draws**. **One-sided p** for "the candidate is
inscription-final MORE than chance" = fraction of draws with permuted final-count >= observed.

This holds each inscription's word multiset fixed and tests POSITION only. It is **calibrated by
construction**: permuting positions = H0 of no positional preference, so the false-positive rate
under H0 is controlled at the nominal level (verified by the FALSE-POSITIVE arm of the PC).

## 6. PROTOCOL (in order)

0. **Inspect:** n inscriptions with >=2 words; top-10 inscription-FINAL word-forms by final count
   (anonymous sign sequences) + their total counts; identify the CANDIDATE per the frozen rule.
1. **FREEZE** this prereg + `plan_hash.txt`; write `machinery.py` with `__main__` self-check.
2. **GLOBAL:** candidate final-position enrichment (observed) + position-permutation null mean +
   one-sided p; and its initial-position rate (control).
3. **POSITIVE CONTROL FIRST (gates verdict).** On LB:
   - Build pseudo-inscriptions by chunking DĀMOS wordforms into ordered groups (seeded; no site
     metadata in DĀMOS -> SAY SO).
   - **DETECT (planted terminal bias):** force a chosen form to be inscription-final in ~X% of
     pseudo-inscriptions (plant a terminal bias); the position-permutation null MUST reject
     (p<=0.05) in the correct direction (final-biased).
   - **FALSE-POSITIVE:** on position-randomized pseudo-inscriptions (word order permuted within
     each pseudo-inscription = exact H0), rejection rate (frac p<=0.05) MUST be <=0.10 across
     >=30 independent sets.
   - If it cannot detect a planted terminal bias OR fires on randomized position ->
     `MACHINERY_UNINFORMATIVE`.
4. **LA MAIN — CROSS-SITE held-out:** per site with **>=10 occurrences of the candidate** OR
   (fallback) test the AGGREGATE **final-slot concentration** per site: is the site's set of
   final-position forms more concentrated (top-form share = the most-frequent final form's share
   of all final slots) than its position-permutation null? Count sites significant (p<=0.05) in
   the SAME direction (concentrated). **Leave-one-site-out** on the largest site (Haghia Triada):
   exclude it, recompute global candidate p. If the candidate is too sparse per-site, use the
   aggregate final-concentration metric and SAY SO.
5. **FROZEN MECHANICAL VERDICT (count):**
   - `TERMINAL_TOTAL_SLOT_CROSS_SITE_ROBUST` iff PC passed AND global candidate final-enrichment
     p<=0.05 AND >=2 sites show significant final-position structure same direction AND survives
     leave-one-site-out.
   - `TERMINAL_TOTAL_SLOT_SITE_LOCAL` iff global significant BUT <2 sites OR collapses under
     leave-one-site-out.
   - `TERMINAL_TOTAL_SLOT_NO_SIGNAL` iff global p>0.05.
   - `TERMINAL_SLOT_UNDERPOWERED` iff no form meets the candidate threshold / <2 sites testable.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.

   (Order of precedence: MACHINERY_UNINFORMATIVE > UNDERPOWERED > NO_SIGNAL > SITE_LOCAL >
   CROSS_SITE_ROBUST, evaluated top-down; first match wins.)

## 7. OUTPUTS (exact PATH CONTRACT paths)

`prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json`,
`reports/EPOCH035_REPORT.md`, `data/epoch_035/`.

## 8. NON-CIRCULARITY (hard)

Word-forms are ANONYMOUS sign sequences carrying NO phonetic / sound / meaning / reading. L2/L3
positional statistics ONLY. The candidate is identified by a FROZEN selection rule (most final
occurrences among forms meeting a count threshold), NOT by any assumed value. LB is a
POSITIVE-CONTROL benchmark ONLY (it is never used to read or validate a Linear A claim; it only
certifies that the machinery can detect a planted positional effect and does not fire on noise).
