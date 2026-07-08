# EPOCH-041 — SIGN POSITIONAL-ROLE SPECIALIZATION (templatic vs free morphology; L2/L3)

## QUESTION
What FRACTION of the Linear A sign inventory is POSITION-SPECIALIZED — i.e. appears
significantly more in ONE within-word position (initial / medial / final) than a
within-word permutation null predicts? A HIGH specialized fraction => templatic/slot
morphology (signs have fixed structural roles); a LOW fraction => positionally-free
signs. Is the specialization level ROBUST across sites?

## SCOPE / DISCIPLINE (hard)
- Pure positional structure (L2/L3): signs are ANONYMOUS. No phonetics, no sound,
  no meaning, no value, no reading is assigned. "Specialized" is a positional-
  distribution statistic, NOT a morpheme-with-meaning.
- LB is a POSITIVE-CONTROL benchmark ONLY (it has known positional structure:
  grammatical case endings, common word-initial syllables). LB signs are likewise
  treated as anonymous tokens for the PC; their phonetic values are NOT used.
- Freeze prereg + plan_hash BEFORE running. PC FIRST. Mechanical verdict from the
  frozen rule below.

## DATA
- LA corpus: `corpus/silver/inscriptions_structured.json`. Word tokens are stream
  entries with `t=='word'` and a `signs` list. Only words with `len(signs)>=2`.
- Positions: INITIAL = index 0; FINAL = index -1; MEDIAL = any interior index
  (only defined for words with `len(signs)>=3`).
- LB positive control: `scripts/cross_script/data.py::load_b_damos()[0]` — list of
  word sign-sequences (anonymous tokens).

## METRIC (frozen)
For each sign S with >=15 occurrences (counted in len>=2 words), test whether S's
observed count in EACH position (initial, final; medial for len>=3 words) exceeds
its within-word permutation null (one-sided, upper tail).

NULL (frozen, within-word permutation, calibrated):
- Permute the signs WITHIN each word (preserving word lengths and per-word sign
  multisets). Recompute each sign's per-position counts. >=2000 draws.
- Per-sign per-position p-value = (1 + #(draws where count >= observed)) / (1 + #draws).
- DRAWS: >=2000 (minimum per spec). In practice 5000 draws are used to resolve the
  Holm p-value floor (with 2000 draws the floor 1/2001 blocks Holm when many signs
  are simultaneously enriched, as in LB). This is a documented, conservative choice
  (more draws => tighter null, harder to pass); recorded in deviations.
- Holm correction across all (sign x position) tests at family alpha 0.05.
- A sign is POSITION-SPECIALIZED if it is significantly enriched in at least one
  position after Holm correction.
- SPECIALIZED_FRACTION = (#specialized signs) / (#signs tested).

## PROTOCOL
0. Inspect: n words len>=2, len>=3; n signs tested (>=15 occ); rough observed
   specialized fraction.
1. FREEZE prereg + plan_hash; machinery.py with __main__ self-check.
2. GLOBAL: SPECIALIZED_FRACTION (Holm-corrected); break down by position
   (initial- vs final- vs medial-specialized); list specialized signs ANONYMOUSLY
   with preferred position + initial/final rates.
3. POSITIVE CONTROL FIRST (gates verdict). On LB:
   (a) DETECT — LB specialized fraction must be significantly ABOVE chance level
       (>alpha, i.e. more signs specialize than Holm false-positives); quantify vs
       a within-word-shuffled LB where the fraction must drop to ~chance.
   (b) FALSE-POSITIVE — on within-word-shuffled words, specialized fraction <=0.10
       across >=20 sets. If it cannot detect LB's positional structure OR fires on
       shuffled words -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE held-out: per site with >=200 word-tokens, compute the
   specialized fraction; report per-site fractions. Leave-one-site-out on HT.
   Cross-site here = the specialized FRACTION is similar across sites, not a
   single-sign test.
5. FROZEN MECHANICAL VERDICT (thresholds fixed here):
   - HIGH_POSITIONAL_SPECIALIZATION_CROSS_SITE iff PC passed AND
     global specialized_fraction >= 0.20 AND per-site fractions >= 0.15 in >=3
     sites (consistent, not one-site).
   - POSITIONAL_SPECIALIZATION_SITE_LOCAL iff global >= 0.20 BUT concentrated in
     <3 sites / collapses under LOO.
   - LOW_POSITIONAL_SPECIALIZATION iff global specialized_fraction < 0.20 (most
     signs are positionally free).
   - SPECIALIZATION_UNDERPOWERED iff <3 sites have >=200 tokens OR <15 signs
     testable.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.

## OUTPUTS
- prereg.md, plan_hash.txt, machinery.py, result.json, report (EPOCH041_REPORT.md),
  data dir (data/epoch_041/).
- result.json keys: task_id="EPOCH-041", method, result, verdict (one allowed
  token), numbers, key_findings (>=3), successor_hypotheses (>=5), layer="L2/L3",
  la_touched=true, non_circular (str), deviations (list).
- numbers.global, numbers.specialized_signs, numbers.positive_control,
  numbers.cross_site (exact shapes per task spec).

## NON-CIRCULARITY
Signs carry NO phonetic/sound/meaning/reading. L2/L3 statistics ONLY. LB is a
positive-control benchmark ONLY; its deciphered values are not used in any LA
inference. The verdict is a positional-distribution statistic, not a decipherment.
