# EPOCH-062 PREREGISTRATION (FROZEN)

## Task
Is the standalone marker (U+1076B, Python `"\U0001076b"`) DOCUMENT-PERIPHERAL
(heading/colophon position) or an INTERIOR separator within multi-line inscriptions?

Layer: **L2** (pure token-position structure; document line-index of an anonymous
frequent token TYPE). NO sign value, NO reading, NO phonetics/meaning.

## Target (NON-CIRCULAR)
- Target token TYPE: `t == 'other'` AND `"\U0001076b" in raw`.
- Position metric: DOCUMENT content-line index `li` within the inscription.
- A **content-line** is a maximal run of CONTENT tokens (`t in {word,num,other}`)
  bounded by `nl` / START / END. `div` and `nl` are structural, NOT content;
  `div` does NOT flush a content-line (only `nl`/START/END bound it).
- Content-lines indexed `0..L-1`.
- **Testable inscriptions**: `L >= 3` content-lines AND `>= 1` marker-bearing
  content-line (so an interior exists).
- **TARGET markers**: all `other` tokens with `"\U0001076b" in raw` occurring in
  testable inscriptions.

## Metric (FROZEN, primary)
- **PERIPHERAL rate** = fraction of TARGET markers whose `li == 0` (FIRST/heading)
  OR `li == L-1` (LAST/colophon).
- Secondary: **HEADING rate** (`li==0`), **COLOPHON rate** (`li==L-1`),
  **INTERIOR rate** (`0 < li < L-1`).

## Null (FROZEN)
Within EACH testable inscription, RE-PLACE each of its markers' content-line
index uniformly at random in `{0,...,L-1}` (independent; preserving marker count
per inscription and the inscription's `L`). Recompute PERIPHERAL rate.
- `>= 500` reshuffles.
- Perm p (peripheral) = `frac(null peripheral >= observed)`, one-sided (enrichment).
- Under null, expected peripheral rate = marker-weighted mean of `2/L`.
- ALSO one-sided perm p for HEADING (`li==0` vs uniform `1/L`) and COLOPHON
  (`li==L-1` vs uniform `1/L`) separately.

## Positive Control (SYNTHETIC, gates verdict)
- (a) DETECT: plant a corpus where every marker sits on FIRST or LAST content-line;
  confirm peripheral enrichment flagged (`perm p <= 0.05`).
- (b) FALSE-POSITIVE: plant markers placed UNIFORMLY at random among content-lines;
  confirm peripheral NOT flagged (rejection `<= 0.10` across `>= 20` draws).
- If miscalibrated -> `MACHINERY_UNINFORMATIVE`.

## Cross-site
Per site with `>= 10` testable markers: recompute peripheral rate + null + perm p +
direction. Count sites significant same direction (enriched). Leave-one-site-out
on Haghia Triada.

## Frozen Mechanical Verdict
- `MARKER_DOCUMENT_PERIPHERAL_CROSS_SITE` iff PC passed AND global peripheral
  enriched (`perm p <= 0.05`) AND significant same-direction (enriched) in `>= 2`
  sites AND survives leave-one-site-out.
- `MARKER_PERIPHERAL_SITE_LOCAL` iff global peripheral enriched BUT `< 2` sites /
  fails LOO.
- `MARKER_INTERIOR_ENRICHED` iff global peripheral significantly DEPLETED
  (opposite tail `p <= 0.05`).
- `MARKER_POSITION_UNIFORM` iff peripheral neither enriched nor depleted.
- `MARKER_POSITION_UNDERPOWERED` iff `< 2` sites have `>= 10` testable markers.
- `MACHINERY_UNINFORMATIVE` iff PC failed.

## Discipline
Proposer/operator, never adjudicator. MECHANICAL verdict from FROZEN rule.
PC is synthetic; will be stated plainly.
