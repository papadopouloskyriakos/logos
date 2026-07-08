# EPOCH-051 — Preregistration (FROZEN before main run)

## Task
A-HEADING x ACCOUNTING-INTENSITY INTERACTION (L2/L3).
Connects E034 (A-initial words mark inscription-INITIAL/heading position) + E045
(document classes differ in accounting intensity = numeral-density).

**Question:** do inscriptions whose FIRST word token's first sign is exactly `A`
("A-headed" documents) have a DIFFERENT numeral-density than non-A-headed documents —
i.e. does the A-heading mark a document FUNCTION (e.g. A-headed = label/heading-type,
numeral-sparse; vs account-type)? And is the difference ROBUST across sites, controlling
for the confound that A-heading and numeral-density might both just track document
class / site?

## Discipline (NON-CIRCULAR, hard)
- `A-` = the first sign token of the first word token of the inscription, equal to the
  literal sign string `"A"` (anonymous positional token; NO phonetic value, NO meaning).
- `numeral_density` = (#num tokens) / (#word tokens + #num tokens) over the inscription
  stream. Content tokens only; `div`/`nl`/`other` ignored.
- Eligibility: inscriptions with `>=2` content tokens AND `>=1` word token.
- Layer L2/L3 ONLY. LB is control-only (LB lacks this positional+numeral structure;
  stated explicitly).
- NO phonetics, NO semantics, NO values read off the signs.

## Data
`corpus/silver/inscriptions_structured.json` (1341 inscriptions). Each has `site`,
`support`, and a `stream` of tokens (`{t:"word",signs:[...]}`, `{t:"num",v:int}`,
`{t:"div"|"nl"|"other"}`).

## Metric (frozen)
Compare `numeral_density` between A-HEADED vs NON-A-HEADED inscriptions via
Mann-Whitney U on per-inscription density (two-sided). Report GLOBAL effect + direction
(which group has higher mean density). Confound control: also test WITHIN the largest
document class (Tablet) and WITHIN the largest site (Haghia Triada) whether A-heading
still predicts density (stratified Mann-Whitney, same direction required). Cross-site:
per site with `>=15` A-headed AND `>=15` non-A-headed, run Mann-Whitney + direction;
count significant sites (p<=0.05); require consistent direction. Leave-one-site-out
on HT (pooled-minus-HT Mann-Whitney).

## Protocol
0. Inspect: n A-headed vs non-A-headed; mean density each; A-heading rate by support/site.
1. FREEZE prereg + plan_hash; write machinery.py with `__main__` self-check.
2. GLOBAL: density A-headed vs non-A-headed (means + MW-U p + direction).
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) DETECT — plant a group-density difference (shift one group's density); require
       detection p<=0.05 in the correct direction.
   (b) FALSE-POSITIVE — two groups drawn from the SAME density distribution; require
       rejection rate <=0.10 across >=20 random splits.
   If miscalibrated -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — confound-controlled + cross-site:
   (a) WITHIN Tablet and WITHIN Haghia Triada, does A-heading still predict density?
   (b) per testable site (>=15 each group): MW-U + direction; count sig; consistency.
   Leave-one-site-out on HT.
5. FROZEN MECHANICAL VERDICT (one token):
   - `A_HEADING_MARKS_DOC_FUNCTION_CROSS_SITE` iff PC passed AND global sig AND survives
     within-Tablet AND within-HT (same direction) AND sig in >=2 sites same direction.
   - `A_HEADING_FUNCTION_SITE_LOCAL` iff global sig BUT vanishes under confound control
     / <2 sites / direction flips.
   - `A_HEADING_NO_FUNCTION_DIFFERENCE` iff global density difference not significant.
   - `A_HEADING_FUNCTION_UNDERPOWERED` iff <2 sites have >=15 in each group.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.
6. Write outputs to PATH CONTRACT paths.

## Frozen before any main-analysis code execution.
