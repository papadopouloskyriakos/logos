# EPOCH-045 Preregistration — ACCOUNTING-INTENSITY: NUMERAL-DENSITY AS A DOCUMENT-CLASS DISCRIMINANT

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-045
**Layer:** L2/L3 (token-composition structure only)
**Operator:** logos z.ai research worker (GLM-5.2)
**Frozen BEFORE any main analysis.** PC runs first and gates the verdict.

## QUESTION
Do Linear A DOCUMENT CLASSES (the `support` field) differ in ACCOUNTING INTENSITY,
defined as numeral density = (#num tokens) / (#word + #num tokens) per inscription
(content tokens only; `nl`/`div`/`other` ignored)? And does any difference SURVIVE
controlling for SITE (i.e. is it not a pure site artifact)?

Hypothesis (illustrative, not assumed): tablets/roundels are numeral-dense
(accounting) vs stone/clay vessels numeral-sparse (dedicatory/label).

## DISCIPLINE (hard)
- NO phonetic / sound / meaning / reading.
- NO numeral-value arithmetic (the `v` field is NEVER read; only the token TYPE `num` is counted).
- L2/L3 token-composition structure ONLY.
- Linear B is CONTROL-ONLY: LB DAMOS lacks per-inscription `support` metadata, so a
  planted/random doc-class density PC is built on the LA corpus itself (stated plainly).

## DATA
- Source: `corpus/silver/inscriptions_structured.json` (1341 inscriptions).
- Per inscription: `site`, `support`, `stream` (token types: word/num/nl/div/other).
- Per-inscription numeral_density = (#num) / (#word + #num).
- QUALIFYING inscriptions: those with >=2 content tokens (word+num).
- Support classes kept: those with >=20 qualifying inscriptions.

## METRIC (frozen)
- Per support class: distribution of per-inscription numeral_density.
- GLOBAL test: Kruskal-Wallis H across the kept support classes.
- NULL for significance: permutation of support labels (Kruskal-Wallis distribution).

## PROTOCOL
0. Inspect: per-support n (>=2 content tokens), mean density; support x site table.
1. FREEZE prereg + plan_hash; write machinery.py with __main__ self-check.
2. GLOBAL: per-support mean density; Kruskal-Wallis H + p across kept supports.
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) DETECT — two synthetic doc-classes with a PLANTED density difference; require p<=0.05.
   (b) FALSE-POSITIVE — two classes drawn from the SAME density distribution; require
       rejection rate <=0.10 across >=20 random splits.
   If miscalibrated (fp>0.10) OR cannot detect planted difference -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — SITE-CONTROLLED (key held-out move): WITHIN each site with >=2 support
   classes (each >=10 qualifying inscriptions), test whether support predicts density
   (Mann-Whitney between the two largest supports, or per-site Kruskal-Wallis if >2).
   Count sites with significant within-site support effect (p<=0.05) AND record DIRECTION
   (which support is denser). Require CONSISTENT direction across significant sites.
   Pooled within-site permutation test (stratified by site) for an overall p.
5. FROZEN MECHANICAL VERDICT (one token):
   - ACCOUNTING_INTENSITY_DOCCLASS_ROBUST iff PC passed AND global Kruskal p<=0.05 AND
     within-site support effect significant in >=2 sites AND direction CONSISTENT AND
     pooled within-site p<=0.05.
   - ACCOUNTING_INTENSITY_SITE_CONFOUNDED iff global differs BUT within-site vanishes
     (<2 sites) or direction flips.
   - NO_DOCCLASS_ACCOUNTING_DIFFERENCE iff global Kruskal p>0.05.
   - ACCOUNTING_UNDERPOWERED iff <2 sites have >=2 supports with >=10 inscriptions each.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE outputs to the exact PATH CONTRACT paths.

## PRE-RUN DATA INSPECTION (recorded for transparency, before any inference)
- Qualifying inscriptions (>=2 content tokens): 465 / 1341.
- Supports with >=20 qualifying inscriptions: Tablet (309), Stone vessel (75), Roundel (22).
- Sites with >=2 supports each >=10 qualifying inscriptions: **1** (Haghia Triada:
  Tablet=178, Roundel=12).
- This pre-registered structure strongly suggests the ACCOUNTING_UNDERPOWERED branch is
  likely, but the verdict is decided MECHANICALLY by the rules above after PC + main run.

## OUTPUTS
- prereg.md, plan_hash.txt, machinery.py, result.json, report, data dir (PATH CONTRACT).
- result.json keys: task_id, method, result, verdict, numbers, key_findings (>=3),
  successor_hypotheses (>=5), layer="L2/L3", la_touched=true, non_circular, deviations.
