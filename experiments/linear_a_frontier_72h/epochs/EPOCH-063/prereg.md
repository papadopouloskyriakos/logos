# EPOCH-063 PREREGISTRATION — Is Linear A's standalone-marker inventory POSITION-DIFFERENTIATED?

**Campaign:** Linear A frontier-72h · **Epoch:** 063 · **Layer:** L2 (pure token-position structure)
**Frozen BEFORE any analysis run.** Proposer/operator; mechanical verdict from a frozen rule.

## Question

E061 showed the most frequent `other` token M1 = U+1076B (`"\U0001076b"`, n≈440 testable) is LINE-ISOLATED.
E062 showed M1 is DOCUMENT-PERIPHERAL (first/last content-line, 0.691 vs 0.382 null, 6/6 sites).
The SECOND-most-frequent non-logogram/non-fraction `other` token is M2 = U+2014 (em-dash `"—"`, n≈52),
which is ALSO line-isolated (~0.94).

**Do M1 and M2 occupy DIFFERENT document-position niches** — i.e., is the standalone-marker inventory
POSITION-DIFFERENTIATED (M1 brackets document ENDS while M2 marks the INTERIOR), or are the two markers
positionally REDUNDANT (both peripheral)?

A DIFFERENTIATED result establishes that LA documents deploy a SYSTEM of ≥2 line-isolated tokens with
COMPLEMENTARY structural roles.

## Scope (anonymous, L2)

- Pure token-position structure: anonymous token TYPES by document content-line index only.
- NO sign value, NO reading, NO phonetics/meaning.
- Targets: token TYPES whose `raw` contains `"\U0001076b"` (M1) or `"—"` (M2).
- DOCUMENT LINE-POSITION only; L2 ONLY.

## Honest scope caveats (stated up front)

1. **M2 is CONCENTRATED at Haghia Triada** (only HT has ≥10 M2 markers; HT=21, all others <10).
   M2's CROSS-SITE robustness CANNOT be certified — the M2 leg is **HT-anchored + global**, NOT
   cross-site-certified. Reported honestly.
2. **M2 = U+2014 (em-dash) MAY be a transcription RULING/DIVIDER mark** rather than an inscribed
   syllabogram. We do NOT claim M2 is an inscribed sign — only that it is a line-isolated TOKEN occupying
   the interior niche. The finding (complementary document positions) is robust either way (inscribed
   interior sign OR ruled interior divider); interpret at L2 accordingly.

## Data

- Corpus: `corpus/silver/inscriptions_structured.json` (ordered `stream`; tokens `t in {word,num,div,nl,other}`;
  `other` carry `raw`).
- CONTENT-LINE = maximal run of content tokens (`t in {word,num,other}`) bounded by `nl`/START/END;
  `div` does NOT flush a line. Index `0..L-1`.
- TESTABLE inscriptions: `L >= 3` content-lines AND `>= 1` target marker (so an interior exists).

## Metric (frozen)

For each marker, PERIPHERAL = (content-line index `li in {0, L-1}`); HEADING = (`li==0`);
INTERIOR = (`0 < li < L-1`).

- **H1 (M2 interior-enrichment):** M2 peripheral rate vs the WITHIN-INSCRIPTION LINE-SHUFFLE null
  (re-place each M2 marker's line index uniformly in `{0..L-1}` within its inscription, preserving count + L;
  ≥1000 draws). One-sided DEPLETION `p_deplete = frac(null_peripheral <= observed)` (M2 is INTERIOR =
  peripheral BELOW null). Also report M2 heading depletion (`li==0` vs `1/L` null).
- **H2 (differentiation contrast):** observed peripheral-rate DIFFERENCE `d = periph(M1) - periph(M2)`.
  NULL: POOL all M1+M2 marker records `(li,L)`, RELABEL which are M1 vs M2 preserving the two counts,
  recompute `d`; ≥1000 draws; one-sided perm `p = frac(null d >= observed d)` (M1 more peripheral than M2).
- NULL for M2 also anchored to the marker-weighted mean of `2/L` (expected peripheral under uniform).

## Protocol

0. Inspect: n M1, n M2 testable; peripheral/heading/interior breakdown each; M2 per-site counts.
1. FREEZE prereg + plan_hash; `machinery.py` with `__main__` self-check (validate line-shuffle null +
   relabel-contrast null on synthetics).
2. GLOBAL: M1 peripheral, M2 peripheral; M2 interior-enrichment (`p_deplete` vs null); contrast `d` + perm `p`.
3. POSITIVE CONTROL FIRST (gates verdict), SYNTHETIC:
   (a) DETECT — plant a corpus where M1 is ALWAYS peripheral and M2 is ALWAYS interior; confirm
       differentiation flagged (M2 peripheral depleted `p<=0.05` AND contrast perm `p<=0.05`).
   (b) FALSE-POSITIVE — plant BOTH M1,M2 at the SAME (peripheral) positions; confirm differentiation
       NOT flagged (contrast rejection `<=0.10` across ≥20 draws). If miscalibrated → MACHINERY_UNINFORMATIVE.
4. M2 CROSS-SITE (report honestly): per site with ≥10 M2 markers, M2 peripheral vs null. Expect only HT
   testable; report `n_sites_testable` and say M2 is HT-anchored (cross-site NOT certified). M1 cross-site
   is already established in E062 — do NOT re-litigate; cite it.
5. FROZEN MECHANICAL VERDICT:
   - `MARKER_SYSTEM_POSITION_DIFFERENTIATED` iff PC passed AND M2 peripheral significantly DEPLETED vs its
     null (`p_deplete<=0.05`, i.e. M2 is interior-enriched) AND the contrast `d=periph(M1)-periph(M2)` is
     significant (perm `p<=0.05`, M1 more peripheral than M2). [M1's own periphery is E062-established.]
   - `MARKER_SYSTEM_UNDIFFERENTIATED` iff M2 is NOT significantly less peripheral than M1 (contrast NS) —
     the two markers share the same (peripheral) niche.
   - `SECOND_MARKER_UNSTRUCTURED` iff M2's document position is uniform (neither peripheral-enriched nor
     interior-enriched vs null) — M2 has no systematic document position.
   - `MARKER_SYSTEM_UNDERPOWERED` iff `n_M2 testable < 20`.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.

## Non-circularity

Targets = anonymous token TYPES by `raw` substring; document content-line index only; L2 only. No sign
value, no reading, no phonetics/meaning used. PC is SYNTHETIC (stated plainly).
