# EPOCH-037 — LINE-FINAL NUMERAL / LEDGER LINE TEMPLATE (preregistration, FROZEN)

Campaign: Linear A frontier-72h. Epoch: EPOCH-037. Layer: L2/L3 (token-position structure).
Author/operator: logos z.ai research worker (GLM-5.2). Role: PROPOSER/OPERATOR (never adjudicator).

## 1. HYPOTHESIS (testable, falsifiable)

Within a Linear A ledger LINE (a run of content tokens delimited by a line break), the
NUMERAL token is disproportionately LINE-FINAL — i.e. the layout is the canonical
"entry ... quantity [line break]" one-entry-per-line ledger template. This is the LINE
dimension of the entry template; together with E031 (WORD→NUMERAL entry-then-quantity,
certified) it would map the full positional template: WORD first, NUMERAL last, within
each line.

This is PURE TOKEN-POSITION structure (L2/L3). No numeral-value arithmetic, no
phonetics, no meaning, no reading.

## 2. NON-CIRCULARITY / DISCIPLINE (hard constraints)

- Tokens carry NO phonetic / sound / meaning / reading information. Only token TYPE
  ('word','num','nl','div','other') and POSITION are used.
- L2/L3 positional statistics ONLY.
- Linear B (load_b_damos) is a POSITIVE-CONTROL BENCHMARK ONLY — used to validate that
  the machinery (a) detects a PLANTED line-final-numeral bias and (b) does NOT fire on
  position-randomized pseudo-lines. LB is NEVER used as evidence for the LA claim.
- The NULL is calibrated BY CONSTRUCTION (within-line position permutation), so it
  cannot inherit any LA-side structure beyond the per-line token multiset.

## 3. DATA (verified)

- Source: `corpus/silver/inscriptions_structured.json` (1341 inscriptions).
- Each inscription has 'site' and an ORDERED 'stream' of tokens with type field 't' in
  {'word','num','nl','div','other'}. 'nl' = line break; 'num' = numeral.
- LINE DELIMITER DECISION (frozen): **'nl' ONLY**. Rationale (from inspection):
  of 463 'div' tokens, 341 are followed by content (intra-line section/heading
  divider) and only 96 by 'nl'; 'div' is therefore a within-line / heading separator,
  NOT a line break. The 'nl' token is the true line break (2073 of 2114 'nl' are
  followed by content or end-of-stream). Sensitivity check: nl-only vs nl+div give
  near-identical p_num_last (0.867 vs 0.866) and qualifying-line counts (1158 vs 1147),
  confirming 'div' is mostly intra-line. Primary = nl-only.
- A LINE = the run of CONTENT tokens ('word','num','other'; separators ignored)
  between consecutive 'nl' breaks.
- QUALIFYING LINE: >=2 content tokens AND contains >=1 'num'.
- LB positive control: `load_b_damos` (scripts/cross_script/data.py) — build
  pseudo-lines from DAMOS wordforms (SAY SO in report).

## 4. METRIC (frozen)

Among qualifying lines:
- p_num_last  = fraction whose LAST content token is 'num'.  (test statistic)
- p_num_first = fraction whose FIRST content token is 'num'. (control: should NOT be
  final-biased; expected low / not elevated)

NULL (frozen, within-line position permutation — calibrated by construction):
For each qualifying line, permute the ORDER of its content tokens (keeping the
multiset, hence the per-line num-count fixed), recompute p_num_last; >=2000 draws.
One-sided p = fraction of draws with permuted p_num_last >= observed p_num_last
(testing "numerals are line-final MORE than chance").

## 5. PROTOCOL (in order)

0. Inspect (DONE, see §3): line delimiter = nl only; 1158 qualifying lines globally;
   8 sites with >=15 qualifying lines (Haghia Triada 772, Zakros 115, Khania 93,
   Phaistos 34, Tylissos 30, Arkhalkhori 30, Malia 28, Palaikastro 18). Global
   p_num_last observed = 0.867.
1. FREEZE prereg + plan_hash BEFORE running. machinery.py with __main__ self-check.
2. GLOBAL: p_num_last observed; within-line permutation null mean + one-sided p;
   p_num_first (control).
3. POSITIVE CONTROL FIRST (gates verdict). Build pseudo-lines with a PLANTED
   line-final-numeral bias; confirm the null (a) DETECTS it (p<=0.05, correct
   direction); AND (b) FALSE-POSITIVE: on position-randomized pseudo-lines, rejection
   rate <=0.10 across >=30 sets. If it cannot detect a planted line-final bias OR
   fires on randomized position -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE held-out: per site with >=15 qualifying lines, compute
   p_num_last + within-line permutation p; count sites significant (p<=0.05) same
   direction; require CONSISTENT direction. Leave-one-site-out on the largest site
   (Haghia Triada).
5. FROZEN MECHANICAL VERDICT (count):
   - LINE_FINAL_NUMERAL_CROSS_SITE_ROBUST iff PC passed AND global p<=0.05 (num
     line-final > chance) AND >=3 sites individually significant same direction AND
     survives leave-one-site-out.
   - LINE_FINAL_NUMERAL_SITE_LOCAL iff global significant BUT <3 sites OR direction
     flips OR collapses under LOO.
   - LINE_FINAL_NUMERAL_NO_SIGNAL iff global p>0.05.
   - LINE_FINAL_UNDERPOWERED iff <3 sites have >=15 qualifying lines.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.

## 6. SCOPE / HONESTY

Token-position ledger layout (L2/L3) ONLY. No numeral arithmetic, no phonetics, no
meaning, no reading of Minoan. A "line-final numeral" finding is a statement about
editorial token-position structure in the silver corpus, consistent with a ledger
layout; it is NOT a decipherment claim.
