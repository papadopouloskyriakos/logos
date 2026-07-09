# EPOCH-055 PREREGISTRATION — Numeral Magnitude (Accounting Scale) by Document Class

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-055
**Layer:** L2/L3 (magnitude distribution statistics only)
**Operator:** logos z.ai research worker (GLM-5.2)
**Frozen BEFORE any analysis run.**

## QUESTION
Do document classes (`support`) differ in the MAGNITUDE of their numerals — i.e., do tablets
record LARGER quantities than roundels/vessels? Does that difference SURVIVE controlling for SITE?

## DISTINCTNESS
- DISTINCT from E028 (word length): this is about numeral MAGNITUDE, not word/sign length.
- DISTINCT from E045 (numeral DENSITY): this is about the SCALE of quantities, not how often
  numerals appear.

## NON-CIRCULAR DISCIPLINE (hard)
- Magnitudes (`v`) ONLY. L2/L3 ONLY.
- NO sign values, NO readings, NO phonetics, NO semantic content.
- Prereg + plan_hash frozen BEFORE running. PC FIRST. Mechanical verdict from frozen rule.

## DATA
- `corpus/silver/inscriptions_structured.json`
- `num` tokens carry integer magnitude `v`; each inscription has `support` and `site`.
- Assign each numeral its inscription's support + site. Use `v >= 1`.
- Keep support classes with `>= 30` numerals.
- LB PC synthetic (no support metadata in real corpus): N/A — corpus HAS support metadata.

## METRIC (frozen)
- Per support class: distribution of numeral MAGNITUDES (report median + mean).
- Magnitudes are heavy-tailed → use MEDIAN and rank-based tests.
- GLOBAL test = Kruskal-Wallis across supports on numeral magnitude.

## PROTOCOL
0. Inspect: per-support n_numerals, median + mean magnitude; support × site table.
1. FREEZE prereg + plan_hash + machinery.py (with `__main__` self-check).
2. GLOBAL: per-support median magnitude; Kruskal-Wallis H + p across supports.
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) DETECT — planted magnitude-scale difference between two synthetic groups detected (p<=0.05).
   (b) FALSE-POSITIVE — two groups from same magnitude distribution: rejection <=0.10 across >=20 splits.
   If miscalibrated → MACHINERY_UNINFORMATIVE.
4. LA MAIN — SITE-CONTROLLED: WITHIN the largest site (HT) and WITHIN sites having >=2 support
   classes (each >=15 numerals), does support-class still predict magnitude (per-stratum
   Kruskal-Wallis / Mann-Whitney)? Count sites with significant within-site support-magnitude
   effect + direction consistency.
5. FROZEN MECHANICAL VERDICT:
   - ACCOUNTING_SCALE_DOCCLASS_ROBUST iff PC passed AND global Kruskal p<=0.05 AND within-site
     effect significant in >=2 sites same direction.
   - ACCOUNTING_SCALE_SITE_CONFOUNDED iff global differs BUT within-site vanishes (<2 sites)
     or direction flips.
   - NO_DOCCLASS_SCALE_DIFFERENCE iff global Kruskal p>0.05.
   - SCALE_UNDERPOWERED iff <2 sites have >=2 supports with >=15 numerals each.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to exact PATH CONTRACT paths.
7. FINAL REPLY: verdict, per-support median magnitudes, global Kruskal p, within-site sig sites,
   PC pass y/n, one honest bottom line. Magnitudes only; NO readings. layer="L2/L3".

## VERDICT PRECEDENCE (frozen)
PC failure → MACHINERY_UNINFORMATIVE (highest precedence).
Else if <2 sites testable → SCALE_UNDERPOWERED.
Else if global p>0.05 → NO_DOCCLASS_SCALE_DIFFERENCE.
Else if <2 sig sites same direction → ACCOUNTING_SCALE_SITE_CONFOUNDED.
Else → ACCOUNTING_SCALE_DOCCLASS_ROBUST.
