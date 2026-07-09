# EPOCH-060 PREREGISTRATION (FROZEN)

## Task
Linear A frontier-72h campaign, EPOCH-060. Metrological / logographic ledger entry
template (L2). NEW CHANNEL: the corpus `other` tokens are a coherent class split into
(a) LOGOGRAMS / ideograms (GORILA commodity signs, raw values starting with `*`, e.g.
`*304`,`*305`,`*308`) and (b) FRACTION signs (the Linear A fraction system, raw values
containing the fraction slash `⁄` e.g. `¹⁄₂`,`¹⁄₄`,`¹⁄₃`, or a Unicode vulgar-fraction
char in the block U+2150..U+215F).

## Layer
L2 ONLY. Token CLASSES (logogram / fraction / word / num) by POSITION only. The
logogram's identity (`*304` = which commodity) and the fraction's VALUE (½ vs ¼) are
NOT used — only the token's CLASS and its POSITION. NO sign values, NO readings, NO
phonetics/meaning, NO metrological arithmetic.

## Hypotheses
- H1 LOGO->NUM: logogram-class tokens are immediately followed by a `num` token
  (commodity-sign then quantity) more than a within-line position-shuffle null.
- H2 FRAC-TERMINAL: fraction-class tokens are ENTRY-TERMINAL (immediately followed by
  a line-break `nl` or END) more than a within-line position-shuffle null.

## Token classification (frozen)
For each token in the ordered `stream`:
- `t == 'word'` -> WORD
- `t == 'num'` -> NUM
- `t == 'div'` -> DIV
- `t == 'nl'` -> NL
- `t == 'other'`:
  - LOGOGRAM if `raw` starts with `*`
  - FRACTION if `raw` contains `⁄` OR contains a char in U+2150..U+215F (vulgar fraction)
  - else OTHERSIGN (ignored for both hypotheses)

## Metrics (frozen)
- H1 LOGO->NUM = (# logogram tokens whose next token is `num`) / (# logogram tokens).
  Next token = stream[i+1] if exists else END (END is not `num`).
- H2 FRAC-TERMINAL = (# fraction tokens whose next token is `nl` OR END) /
  (# fraction tokens).

## Null (frozen, unified)
Within EACH line (segment of non-NL tokens delimited by NL tokens), randomly PERMUTE
the order of the non-NL tokens, preserving the line's token multiset and the NL/line
structure. Recompute H1 and H2 on the permuted corpus. >=500 permutations. perm p =
frac(null stat >= observed), one-sided (enrichment). This tests whether logograms sit
before numerals AND fractions sit line-final MORE than random ordering within the same
lines.

## Positive control (gates verdict), SYNTHETIC
- (a) DETECT: plant a corpus where logograms ALWAYS precede `num` and fractions are
  ALWAYS line-final; confirm both H1, H2 enriched (perm p <= 0.05).
- (b) FALSE-POSITIVE: plant a corpus with logograms/fractions placed UNIFORMLY at
  random within lines; confirm H1, H2 NOT flagged (rejection rate <= 0.10 across
  >=20 draws).
- If it cannot detect the planted template OR fires on uniform placement ->
  MACHINERY_UNINFORMATIVE.

## Cross-site
Per site with >=10 logograms (H1) / >=10 fractions (H2), recompute statistic + perm p
+ direction; count sites significant same direction, each hypothesis separately.

## Frozen mechanical verdict
- METRO_LOGO_ENTRY_TEMPLATE_CROSS_SITE iff PC passed AND BOTH H1 and H2 globally
  enriched (perm p <= 0.05) AND EACH holds in >=2 sites same direction.
- PARTIAL_METRO_LOGO_TEMPLATE iff PC passed AND exactly ONE of H1, H2 holds cross-site
  (>=2 sites).
- METRO_LOGO_TEMPLATE_SITE_LOCAL iff global enrichment BUT neither reaches >=2 sites.
- NO_METRO_LOGO_STRUCTURE iff neither H1 nor H2 globally enriched.
- METRO_LOGO_UNDERPOWERED iff <2 sites have >=10 logograms AND <2 sites have >=10
  fractions.
- MACHINERY_UNINFORMATIVE iff PC failed.

## Non-circularity
Token CLASSES derived solely from corpus tagging (`t=='other'` + raw pattern) and
POSITION only. No phonetic/semantic/metrological value used. L2 ONLY. LB PC synthetic
(LB stream lacks this structure).
