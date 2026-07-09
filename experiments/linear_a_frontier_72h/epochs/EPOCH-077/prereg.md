# EPOCH-077 PREREGISTRATION (FROZEN)

## Task
EPOCH-077 — Linear A frontier-72h campaign.

**Question:** Does glyph SIZE carry POSITIONAL information (a spatial prominence / heading marker), or is it
purely a per-SIGN property? Specifically: is the document-INITIAL glyph systematically LARGER than the rest
(a spatial heading/prominence marker — the visual analog of E022 A-prefix heading role, E062 document-peripheral
markers, E069 entry-initial word longer) — or is glyph size independent of position (purely per-sign, per E076)?

## Layer
L2 — pure structural graphic property. Signs are OPAQUE catalog IDs (e.g. AB59). NO phonetic value, NO reading,
NO meaning. glyph size = bbox area; position = order index. Both value-blind.

## Data
`experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json` — list of docs, each
`{"designation","support","site","period","glyphs":[{"sign","bbox":[x,y,w,h],"is_divider"}]}`.
- EXCLUDE `is_divider` glyphs.
- Use docs with >=4 non-divider bbox glyphs (~322 docs).
- Sites with >=15 docs: Haghia Triada, Khania, Zakros, Phaistos, Knossos.

## Metric (FROZEN)
- Per doc (>=4 non-divider glyphs): log-area per glyph = log(w*h); z-score WITHIN the doc
  (subtract doc mean / doc population sd; sd=0 -> 1). Glyph 0 = document-initial.
- PRIMARY statistic (initial prominence):
  `D_init = mean over docs of (z-size of glyph 0) - (mean z-size of glyphs 1..n-1 in that doc)`.
  D_init > 0  <=>  initial glyph larger.
- SECONDARY (any position effect, context only):
  `rho = mean over docs of within-doc Pearson correlation of glyph z-size with position index (0..n-1)`.
  Early-bigger => rho < 0.

## Null (FROZEN)
Within-document POSITION SHUFFLE: permute each doc's glyph order (preserve the doc's size multiset exactly),
recompute D_init (and rho). >=2000 draws. Two-sided reported; the VERDICT uses the one-sided
"initial larger" tail: `p_init = frac(null D_init >= observed D_init)`. Under this null E[D_init] = 0.

## Non-circularity
glyph size = within-document z-scored log bbox-area (removes per-photo scale). position = glyph index in the
document's transcription order (0 = first). size and position are independent measurements. The within-doc
position-shuffle null permutes which glyph sits at which position while preserving the doc's size multiset, so
any position->size effect is beyond chance. No sign value, reading, or meaning is used. L2 only.

## Protocol
0. Inspect: n docs; D_init global; rho; per-site D_init.
1. Freeze prereg + plan_hash; machinery.py with __main__ self-check (position-shuffle null gives E[D_init]~0).
2. GLOBAL: observed D_init; null mean; p_init. rho as context.
3. POSITIVE CONTROL FIRST (synthetic), gates verdict:
   (a) DETECT — plant docs where initial glyph reliably larger; confirm D_init flagged (p_init<=0.05);
       report power_est over >=20 replicates at observed doc/size scale.
   (b) FALSE-POSITIVE — plant docs with size independent of position; confirm D_init NOT flagged
       (rejection <=0.10 across >=20 draws).
   If it can't detect a planted prominence OR fires on position-independent size -> MACHINERY_UNINFORMATIVE.
4. CROSS-SITE: per site with >=15 docs, recompute D_init + within-doc position-shuffle null + p_init + direction;
   count sites significant same direction (initial larger).
5. FROZEN MECHANICAL VERDICT (one token):
   - SPATIAL_SIZE_PROMINENCE_CROSS_SITE iff PC passed (power_est>=0.5) AND global D_init>0 significant
     (p_init<=0.05) AND significant same-direction (initial larger) in >=2 sites.
   - SPATIAL_SIZE_POSITION_SITE_LOCAL iff global significant OR >=1 site significant BUT direction/effect is
     site-inconsistent (not >=2 same-direction sites).
   - NO_SPATIAL_SIZE_POSITION iff PC passed AND global D_init NOT significantly > null AND <2 sites significant
     same-direction — glyph size carries NO positional information; purely per-sign (E076). Well-powered bounded negative.
   - SPATIAL_SIZE_POSITION_UNDERPOWERED iff PC power_est<0.5.
   - MACHINERY_UNINFORMATIVE iff PC detect/false-positive calibration fails.
6. Write outputs to exact PATH CONTRACT paths.

## Frozen before any analysis run
This prereg and its plan_hash are written BEFORE the global/null/PC/cross-site computations are executed for the
verdict. The inspection in step 0 is descriptive only and does not change the metric, null, or verdict rule.
