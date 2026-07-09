# EPOCH-061 PREREGISTRATION (FROZEN)

## Task
Is the most frequent 'other' sign a SYSTEMATIC LINE-ISOLATED document marker? (document structure; L2)

## Target (anonymous, position-only)
The token TYPE whose `raw` field contains the Python string `"\U0001076b"`
(U+1076B). Selection criterion is PURELY the raw substring match on the
'other' token class — NO sign value, NO reading, NO phonetics, NO meaning.
This is an anonymous frequent token TYPE selected by POSITION behaviour only.

Layer: **L2** (token-position structure). No L3+ interpretation.

## Data
`corpus/silver/inscriptions_structured.json` — list of inscriptions, each with
an ordered `stream` of tokens. Token `t` ∈ {word, num, div, nl, other}. 'other'
tokens carry a `raw` string. TARGET tokens = `t=='other'` AND `"\U0001076b" in raw`.
Verified n=474 across sites (HT 187, Khania 154, Zakros 52, Knossos 28,
Phaistos 22, Arkhalkhori 14, ...).

## Metric (frozen)
LINE-ISOLATION rate = fraction of TARGET tokens that are ALONE on their
content-line: the immediately-preceding token-type ∈ {nl, div, START} AND the
immediately-following token-type ∈ {nl, div, END} (no word/num/other
content-token adjacent). START/END are the stream boundaries.

## Null (frozen)
Within EACH inscription, RE-PLACE the same number of TARGET tokens uniformly
at random among the inter-content-token gaps, preserving the inscription's
non-target token sequence and nl structure, and the target count. Recompute
the line-isolation rate. ≥500 reshuffles. Perm p = frac(null ≥ observed),
one-sided (enrichment).

Operationalisation of the null: within an inscription, take the list of
"slot positions" = the indices in the non-target stream skeleton at which a
target token could sit (i.e. the gaps between consecutive non-target tokens,
including before-first and after-last). Uniformly choose k = (target count)
distinct slots with replacement-free sampling; a placed target is "isolated"
iff the slot is bounded on both sides by a non-content boundary token
(nl/div/START/END) of the skeleton. This preserves nl structure and target
count exactly.

## Positive Control (synthetic — gates verdict)
(a) DETECT: plant a corpus where the target is ALWAYS line-isolated (its own
line). Confirm perm p ≤ 0.05.
(b) FALSE-POSITIVE: plant a corpus where the target is placed UNIFORMLY at
random content positions. Confirm rejection ≤ 0.10 across ≥20 draws.
If miscalibrated → MACHINERY_UNINFORMATIVE.

## Cross-site
Per site with ≥15 target tokens: isolation rate + null + perm p + direction.
Leave-one-site-out on HT.

## Frozen Mechanical Verdict
- STANDALONE_MARKER_CROSS_SITE iff PC passed AND global isolation enriched
  (perm p ≤ 0.05) AND significant same-direction in ≥2 sites AND survives
  leave-one-site-out.
- STANDALONE_MARKER_SITE_LOCAL iff global enriched BUT <2 sites / fails LOO.
- NOT_LINE_ISOLATED iff global isolation NOT enriched beyond the null.
- STANDALONE_UNDERPOWERED iff <2 sites have ≥15 target tokens.
- MACHINERY_UNINFORMATIVE iff PC failed.

## Non-circularity
Target = anonymous token TYPE by raw-substring match; metric = pure
token-position structure (L2); null = within-inscription uniform re-placement
preserving skeleton. No sign value, reading, phonetics, or meaning used at
any step. PC is synthetic (declared).
