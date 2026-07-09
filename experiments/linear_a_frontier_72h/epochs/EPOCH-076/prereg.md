# EPOCH-076 PREREGISTRATION (FROZEN)

## Question (mechanical, value-blind)
Is a sign's normalized GLYPH SIZE a SHARED cross-site graphic convention (each sign drawn at a consistent
relative size across sites), or SITE-LOCAL (size is site-idiosyncratic)?

This is a PURE STRUCTURAL GRAPHIC property (L2). Signs are OPAQUE catalog identifiers (e.g. 'AB59') used
ONLY as identity labels. NO phonetic value, NO reading, NO meaning is used or implied. Glyph size is
bounding-box area, independent of any value.

## Data
`experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json` — JSON list of documents, each
`{"designation","support","site","period","glyphs":[{"sign","bbox":[x,y,w,h],"is_divider"}]}`.
787 docs, 5144 glyphs. bbox=[x,y,width,height]; glyph area = w*h.
EXCLUDE glyphs with is_divider=true. Sites with >=15 usable docs (>=4 non-divider bbox glyphs):
Haghia Triada, Khania, Zakros, Phaistos, Knossos.

## Metric (frozen)
1. For each document with >=4 non-divider bbox glyphs:
   - log-area = log(max(1, w*h)) per glyph.
   - WITHIN that document z-score the log-areas: subtract doc mean, divide by doc population sd
     (sd=0 -> use 1). This is each glyph's NORMALIZED SIZE.
2. Per SITE, per SIGN: mean normalized size over all that sign's glyphs at that site.
   Keep (site, sign) cells with >=5 glyph observations.
3. A site's SIZE PROFILE = {sign: mean_norm_size}.
4. CROSS-SITE statistic: for each unordered SITE-PAIR among the 5 big sites, Pearson correlation r of the
   two size profiles over their COMMON signs (require >=8 common signs, else that pair is untestable).

## Null (frozen, per site-pair)
SIGN-LABEL shuffle: randomly permute the {sign -> mean_norm_size} assignment in ONE site's profile over the
common signs, recompute r; >=2000 draws; one-sided perm p = frac(null r >= observed).
Shared size convention = correlation beyond chance sign-size pairing.

## Positive Control (SYNTHETIC, gates verdict)
(a) DETECT-SHARED: build synthetic multi-site data where each sign has a FIXED intrinsic size across sites
    (plus per-glyph noise); confirm cross-site r is high and flagged (perm p<=0.05); report power_est over
    >=20 replicates.
(b) FALSE-POSITIVE: build data where each site assigns sizes to signs INDEPENDENTLY at random
    (site-idiosyncratic); confirm r is at the null (rejection <=0.10 across >=20 draws).
If PC fails -> MACHINERY_UNINFORMATIVE.

## Frozen Mechanical Verdict
- GLYPH_SIZE_SHARED_CROSS_SITE iff PC passed (power_est>=0.5) AND size-profile correlation significant
  (perm p<=0.05, r>0) in >=2 testable site-pairs.
- GLYPH_SIZE_SITE_LOCAL iff correlations are at/below the null (not significant) across the testable pairs.
- GLYPH_SIZE_UNDERPOWERED iff <2 site-pairs have >=8 common signs.
- MACHINERY_UNINFORMATIVE iff PC detect/false-positive calibration fails.

## Discipline / Non-circularity
Within-document z-scoring removes per-photo/per-tablet absolute scale (no pixel-scale leak). The metric is
the cross-site correlation of per-sign mean normalized size; the sign-label-shuffle null destroys the
sign->size association, so any correlation is BEYOND chance sign-size pairing. Sign identity is an opaque
ID (no value used). L2 ONLY.
