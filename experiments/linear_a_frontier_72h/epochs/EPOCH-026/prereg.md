# EPOCH-026 — WORD-FINAL POSITIONAL STRUCTURE (terminal slot)

**Campaign:** Linear A frontier-72h (frontier F4, terminal analog of the A- prefix line)
**Layer:** L2/L3 (positional/structural statistics only)
**Claim ceiling:** a productive word-FINAL sign class (a terminal SLOT) that holds across independent
SITES — the held-out standard. NO phonetic/semantic value assigned to ANY sign.

## Question
The A- line (E022–E024) established a productive, held-out word-INITIAL prefix slot. Mirror question at the
OTHER end of the word: is there a robust, PRODUCTIVE word-FINAL sign class (a terminal slot) that holds
across independent SITES — the held-out standard? (Prior LA work names a KU-RO / -RO ledger-total terminal
as a durable L2/L3 pattern; here we test the strongest word-final sign purely POSITIONALLY, no semantic claim.)

## Non-circular discipline (hard)
- Sign names (RO, RA₂, NE, ...) are ANONYMOUS. Assign NO phonetic value, sound, meaning, language, or reading
  to ANY sign. Positional/structural statistics ONLY (L2/L3).
- LB is a positive-control benchmark ONLY (it is NOT Linear A; it only certifies the machinery can detect a
  known positional-terminal analogue).
- Verdict is computed mechanically from a FROZEN rule; the operator never decides truth by narration.

## Data
- `corpus/silver/inscriptions_structured.json`: list of inscriptions; each has `site`, `support`, `context`
  and a `stream` whose `t=='word'` tokens carry a `signs` list. Analyze words with >=2 signs.
- LB positive control via `scripts.cross_script.data.load_b_damos` (returns list of word sign-lists).

## Metric
- For a sign S: count (and fraction) of >=2-sign words whose LAST sign is S.
- Null: within-word uniform permutation (REUSED from E023 `machinery.permutation_null`); preserves each
  word's sign multiset and length exactly. Under per-word permutation, P(last==S) = (#S in word)/len(word).
  1000 draws, one-sided p = (1 + #(null >= obs)) / (1 + 1000). Tests whether S is word-final MORE than its
  within-word-permuted position predicts.

## Protocol (frozen, in order)
0. Inspect. Compute per-sign word-FINAL rate = (#words whose LAST sign is S) / (#words containing S), for
   signs with >=40 occurrences. Identify the most word-final-skewed sign S* (report the top ~5).
1. FREEZE this prereg + plan_hash. Write `machinery.py` (imports E023 permutation_null) with self-check.
2. GLOBAL: for S*, word-final count/frac over all >=2-sign words; null p (1000 draws, one-sided). Also
   n_distinct word-types ending in S* (productivity) and n_distinct penultimate signs.
3. POSITIVE CONTROL FIRST (gates the verdict): on LB pick a KNOWN word-final-skewed sign with >=40 occ
   (LB has grammatical finals) as the terminal analog; partition LB by a seeded balanced 5-way split (NO
   per-tablet metadata available in load_b_damos — disclosed); require it significant (p<=0.05) in >=3
   partitions AND a frequency-matched random LB sign NOT significant in >=3 partitions. If PC fails ->
   MACHINERY_UNINFORMATIVE.
4. LA MAIN (cross-site): partition LA by SITE; keep sites with >=20 qualifying words; for each compute S*
   word-final count, null p (1000 draws); Holm-correct across the site family; leave-one-site-out (drop the
   largest site = Haghia Triada; is S* still final-significant on the rest?).
5. PRODUCTIVITY + COMPARATORS: n_distinct word-types ending in S* (must be a class, not one word); and for
   the 5 next-most-word-final comparator signs, how many sites each clears — S* is special only if it clears
   >=2 more sites than the comparator median.
6. FROZEN MECHANICAL VERDICT (decide by counting):
   - `FINAL_CLASS_CROSS_SITE_ROBUST` iff (PC passed) AND S* final-significant in >=3 sites AND survives
     leave-one-site-out AND n_distinct_final_types>=8 AND clears >=2 more sites than the comparator median.
   - `FINAL_CLASS_CONCENTRATED` iff globally significant but <=1 site / collapses under leave-one-site-out.
   - `FINAL_CLASS_FEW_TYPE_DRIVEN` iff significant but n_distinct_final_types<8 (one/few word-types).
   - `FINAL_CLASS_UNDERPOWERED` iff too few sites/occurrences to test.
   - `MACHINERY_UNINFORMATIVE` iff the PC failed.

## Observed corpus structure (step 0, pre-freeze)
- Total >=2-sign words: 1369.
- TOP word-final-skewed signs (>=40 occ): RO 0.8478 (78/92), RA₂ 0.7959 (39/49), NE 0.7000 (35/50),
  ME 0.6500 (26/40), TE 0.5714 (56/98). => S* = RO (clear margin).
- Sites with >=20 qualifying words: Haghia Triada, Khania, Knossos, Phaistos, Zakros, Palaikastro, Malia
  (7 sites testable; Thera 17 <20).
- LB known word-final-skewed (>=40 occ): JO 0.8153, MO 0.7973, DE 0.6960 (grammatical finals available for PC).

## Outputs
- prereg.md, plan_hash.txt, machinery.py, result.json, EPOCH026_REPORT.md, intermediate JSON in data dir.
