# EPOCH-057 Preregistration — The 'div' token's structural role (L2)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-057
**Layer:** L2 (pure token-position structure; token TYPES only)
**Operator:** logos z.ai research worker (GLM-5.2), proposer/operator (never adjudicator)
**Date frozen:** before any analysis machinery execution on the real corpus.

## Object (NEW CHANNEL)
The corpus 'div' token (explicit within-line word-divider mark, n=463). Distinct from E037's 'nl'
(line breaks) and from E031's word->num order test. This epoch analyzes the WITHIN-line 'div'
separator's PLACEMENT pattern.

## Question (frozen)
Is 'div' a systematic LEXICAL WORD-SEPARATOR that:
  (S1) sits at word|word boundaries (ENRICHED vs null), AND
  (S2) AVOIDS the word|numeral boundary (DEPLETED vs null) — i.e. respects 'word+numeral' as a
       bound entry unit, separating counted ENTRIES/words but never splitting a word from its quantity?
And is that placement pattern beyond a position-shuffled null AND cross-site robust?

## Discipline (hard, non-circular)
- 'div' = observed token type. Only token TYPES used: word / num / div / nl / other.
- L2 ONLY: NO sign values, NO readings, NO phonetics, NO semantics.
- Prereg + plan_hash frozen BEFORE running real-corpus machinery.
- Positive control FIRST; mechanical verdict from a FROZEN rule.
- Builds on E031 (word->num order) but tests a DISTINCT object (divider placement), not recycled.

## Data
corpus/silver/inscriptions_structured.json — each inscription has ordered 'stream' (list of token
dicts with 't' field) and 'site'. Token types: word (3147), num (1276), div (463), nl (2114),
other (1056). For each 'div', its flanking token TYPES (type immediately BEFORE and AFTER in-stream).

## Metric (frozen)
Classify each div by its (before_type -> after_type) flanking pair. Two frozen statistics:
  S1 (WORD|WORD ENRICHMENT): observed fraction of divs flanked word>...>word vs NULL.
       Specifically: fraction of divs whose before AND after content-flanking types are both 'word'
       (using the gap-based view; see NULL).
  S2 (WORD|NUM AVOIDANCE): observed COUNT of divs at a word|num OR num|word boundary (a div
       separating a word from an adjacent numeral) vs NULL expectation — is div DEPLETED at the
       word/quantity boundary?

## NULL (frozen, calibrated by construction)
Within each inscription, RE-PLACE the same number of div tokens uniformly at random among the
inter-content-token gaps (gaps between word/num/other tokens — i.e. content tokens only, excluding
nl/div from the gap skeleton), preserving the inscription's content-token sequence and its div count.
Recompute S1 and S2. >=500 reshuffles. Report observed value, null mean, permutation p (one-sided:
S1 enrichment, S2 depletion).

### Gap-based flanking definition (frozen)
A 'gap' is a position between two consecutive CONTENT tokens (word/num/other) in the inscription's
content-token subsequence. Placing a div in a gap means its before/after flanking types are the two
content tokens bracketing that gap. For the OBSERVED divs, we map each observed div to the gap it
occupies by taking the nearest preceding and following content token in the original stream (skipping
nl/other-div tokens). This makes observed and null directly comparable on the same gap space.
- S1 observed = (# divs whose bracketing content gap is word|word) / (total divs that map to a gap).
- S2 observed count = # divs whose bracketing content gap is word|num OR num|word.
- Null: same definitions on reshuffled div placements over the same gap space.

## Protocol
0. Inspect: n div; before/after token-type histograms; top (before>div>after) transitions; div by site.
1. FREEZE prereg + plan_hash; machinery.py with __main__ self-check (validate gap-reshuffle null on
   a synthetic).
2. GLOBAL: S1 word|word enrichment (obs vs null, perm p); S2 word|num avoidance (obs vs null, perm p,
   direction).
3. POSITIVE CONTROL FIRST (gates verdict), SYNTHETIC (LB PC: synthetic — Linear B corpus lacks this
   div structure; SAY SO):
   (a) DETECT — synthetic corpus where div placed ONLY at word|word gaps (never word|num); confirm
       S1 enriched (p<=0.05) AND S2 depleted (p<=0.05).
   (b) FALSE-POSITIVE — synthetic where div placed UNIFORMLY at random gaps; confirm S1/S2 NOT flagged
       (rejection rate <=0.10 across >=20 draws).
   If cannot detect planted pattern OR fires on uniform -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE: per site with >=15 div, recompute S1 + S2 (obs vs null, direction); count
   sites with significant word|word enrichment AND word|num avoidance, same direction. Leave-one-site-out
   on the global HT (recompute global p dropping each site in turn; LOO passes if all leave-one-out
   p-values remain <=0.05 for both S1 and S2).
5. FROZEN MECHANICAL VERDICT:
   - DIV_LEXICAL_SEPARATOR_CROSS_SITE iff PC passed AND global S1 word|word enrichment (perm p<=0.05)
     AND global S2 word|num avoidance (div depleted at word/quantity boundary, perm p<=0.05) AND both
     hold same-direction in >=2 sites AND survive leave-one-site-out.
   - DIV_STRUCTURE_SITE_LOCAL iff global significant BUT <2 sites / collapses under LOO / only one of S1,S2.
   - NO_SYSTEMATIC_DIV_PLACEMENT iff div placement consistent with gap-shuffle null (neither S1 nor S2
     significant).
   - DIV_UNDERPOWERED iff <2 sites have >=15 div (report the limit).
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to exact PATH CONTRACT paths.
7. FINAL REPLY: verdict, S1 (obs vs null, p), S2 (obs vs null, p, direction), n sites, PC pass y/n,
   one honest bottom line. Token TYPES only; NO sign values/readings. layer="L2".

## Allowed verdict tokens (exactly one)
DIV_LEXICAL_SEPARATOR_CROSS_SITE | DIV_STRUCTURE_SITE_LOCAL | NO_SYSTEMATIC_DIV_PLACEMENT |
DIV_UNDERPOWERED | MACHINERY_UNINFORMATIVE
