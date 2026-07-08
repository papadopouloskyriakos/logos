# EPOCH-033 — PREREGISTRATION (FROZEN)

**Task:** LEDGER ENTRY-WORD vs NON-ENTRY-WORD STRUCTURAL CONTRAST (functional-class structure; L2/L3).

E031 certified the ledger grammar: WORD then NUMERAL (entry then quantity). This defines two
functional word classes by OBSERVABLE structure only:
- **ENTRY-word** = a `word` token whose IMMEDIATELY FOLLOWING stream token is `num`.
- **NON-ENTRY word** = a `word` token whose following token is NOT `num` (or it is last).

**Question:** do these two classes differ STRUCTURALLY — in (a) word LENGTH (number of signs) and
(b) A-INITIAL rate (E025's productive prefix) — and is that contrast ROBUST across independent SITES?
This distinguishes administrative ROLES by STRUCTURE ONLY (L2/L3): no phonetics, no meaning, no
numeral-value arithmetic. Anonymous signs.

## NON-CIRCULAR / DISCIPLINE (hard)
Tokens carry NO phonetic/sound/meaning/reading. L2/L3 structural statistics ONLY. LB is a
positive-control benchmark ONLY. Freeze prereg + plan_hash BEFORE running. PC FIRST. Mechanical
verdict from the frozen rule.

## DATA (verified)
`corpus/silver/inscriptions_structured.json` — each inscription has `site` and an ORDERED `stream`;
token types `word`,`num`,`nl`,`div`,`other` (numeral key = `num`). Corpus path: BASE/corpus then
repo-root corpus. ENTRY-word = `word` token whose IMMEDIATELY FOLLOWING stream token is `num`.
NON-ENTRY word = `word` token whose following token is NOT `num` (or last). LB PC via `load_b_damos`.

## METRICS (FROZEN)
For each word class compute:
- (a) mean word LENGTH (n signs);
- (b) A-INITIAL rate (fraction of >=1-sign words whose first sign is `A`).

CONTRAST statistics:
- length -> difference in mean length (entry minus non-entry);
- A-rate -> difference in A-initial rate (entry minus non-entry).

## NULL (FROZEN — LABEL PERMUTATION, calibrated by construction)
Randomly permute the entry/non-entry LABELS across the SAME set of word tokens (preserving the count
in each class), recompute the contrast; >=2000 draws; two-sided p. Exchangeable under H0 (no
structural difference between classes) => calibrated.

## PROTOCOL (in order)
0. Inspect: n entry-words, n non-entry-words (global + per site); the two length distributions; the
   two A-rates. Report counts.
1. FREEZE prereg at the PATH CONTRACT path; `plan_hash.txt="<sha256>  prereg.md"`; `machinery.py`
   at `epochs/EPOCH-033/machinery.py` with an `__main__` self-check.
2. GLOBAL: length contrast (entry vs non-entry mean length) + label-permutation two-sided p;
   A-rate contrast + label-permutation two-sided p. Report direction.
3. POSITIVE CONTROL FIRST (gates verdict). On LB, form two word groups with a PLANTED length
   difference and confirm the label-permutation test (a) DETECTS it (p<=0.05, correct direction)
   AND (b) FALSE-POSITIVE: on two groups drawn from the SAME distribution (labels assigned at
   random), rejection rate <=0.10 across >=30 splits. If it cannot detect a planted difference OR
   fires on same-distribution splits -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE held-out: per site with >=15 entry-words AND >=15 non-entry-words, compute
   the length contrast + label-permutation p (and A-rate contrast + p). Count sites significant
   (p<=0.05) for LENGTH and the DIRECTION; require CONSISTENT direction. Leave-one-site-out on the
   largest site (Haghia Triada).
5. FROZEN MECHANICAL VERDICT (count; LENGTH is the primary metric, A-rate secondary/reported):
   - `ENTRY_CLASS_STRUCTURAL_CONTRAST_ROBUST` iff PC passed AND global length-contrast p<=0.05 AND
     >=3 sites individually significant for length AND direction CONSISTENT across those sites AND
     survives leave-one-site-out.
   - `ENTRY_CLASS_CONTRAST_SITE_LOCAL` iff global length p<=0.05 BUT <3 sites significant OR
     direction flips OR collapses under leave-one-site-out.
   - `ENTRY_CLASS_NO_CONTRAST` iff global length-contrast p>0.05.
   - `ENTRY_CLASS_UNDERPOWERED` iff <3 sites have >=15 words in EACH class.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.

## VERDICT PRECEDENCE
MACHINERY_UNINFORMATIVE (PC fail) > UNDERPOWERED (<3 testable sites) > NO_CONTRAST (global p>0.05)
> SITE_LOCAL (global p<=0.05 but not robust) > ROBUST.
