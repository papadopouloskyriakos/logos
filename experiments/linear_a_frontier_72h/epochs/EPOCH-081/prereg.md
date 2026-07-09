# EPOCH-081 PREREGISTERED PROTOCOL (FROZEN)

## Task
EPOCH-081 — Are Linear A document rows LEFT-ANCHORED (aligned at a common left margin, ragged right edge =
left-justified layout), beyond an edge-exchangeability null, and cross-site? Spatial modality, Layer L2.

## Relation to prior epochs (NON-OVERLAP)
- E079: HORIZONTAL glyph SPACING within a line is regular (intra-row x-gaps).
- E080: VERTICAL line SPACING between rows is regular (inter-row y-gaps).
- E081 (this): ANCHORING — do row LEFT edges align (small spread) while RIGHT edges are ragged (large spread)?
  Anchoring is orthogonal to spacing: a grid can be evenly spaced yet ragged-left, or left-aligned yet unevenly
  spaced. E081 tests only edge alignment, not spacing. DISTINCT from E079/E080.

## L2 discipline (hard)
Signs are OPAQUE IDs. NO value, NO reading, NO meaning. Only glyph POSITIONS (row left/right x-edges) matter.
Reading DIRECTION is a corpus assumption; left-ANCHORING (physical margin alignment) is a separate geometric fact
tested by an edge-swap null on geometry only. NON-CIRCULAR.

## Data
`experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json` — list of docs; each doc has
`glyphs[{sign, bbox:[x,y,w,h], is_divider}]`. EXCLUDE `is_divider` glyphs. bbox: x=left edge, glyph spans
[x, x+w]; y=top, y-center = y + h/2.

## Row definition
A ROW = a y-band. Cluster non-divider glyphs by y-center using single-linkage within tolerance
`0.6 * median(glyph height)` of the doc (running cluster mean). Per row:
- LEFT-edge  = min glyph-left-x  (= min bbox[0])
- RIGHT-edge = max glyph-right-x (= max bbox[0]+bbox[2])

## Usable docs
A doc is usable iff it has >=6 non-divider bbox glyphs AND >=3 rows after clustering.

## Per-doc metric (scale-free)
- `medw` = median glyph WIDTH in the doc.
- `lsd` = pstdev(row LEFT-edges)  / medw
- `rsd` = pstdev(row RIGHT-edges) / medw
- doc asymmetry `a = rsd - lsd`  (POSITIVE => left-anchored: left tighter than right).

## Corpus statistic
`S_obs = MEDIAN(a)` over usable docs. Positive & large => left-anchored.

## NULL (frozen, EDGE-EXCHANGEABILITY, sign-symmetric)
Edges are exchangeable (no horizontal anchoring preference). For each null draw:
- For each usable doc, sample `s` in {+1,-1} uniformly; contribute `s * (rsd - lsd)`.
- `S = median(contributions)`.
- >=2000 draws. One-sided perm p = frac(null S >= S_obs).
(Left-anchored = observed asymmetry more positive than the sign-symmetric swap null.)

## Reported numbers
S_obs, null-median (~0), perm p, median(lsd), median(rsd), frac(lsd<rsd); per-site same for sites with >=15
usable docs (Haghia Triada, Khania, Zakros).

## POSITIVE CONTROL (SYNTHETIC, gates verdict) — three arms
Synthetic docs mimic real geometry: ~6-12 rows, glyph widths ~ median real width, y-rows spaced ~ median real
height, jittered within tolerance. Three arms:
- (a) DETECT — LEFT-justified: rows share a common left margin (small left jitter), variable row length so right
  edges ragged. Expect S_obs>0 flagged (perm p<=0.05). power_est over >=20 reps.
- (b) FALSE-POSITIVE — CENTERED: rows centered (both edges equally ragged). Expect S_obs~0 NOT flagged
  (reject <=0.10).
- (c) DIRECTION — RIGHT-justified: rows share a common right margin, left ragged. Expect S_obs<0 and NOT flagged
  as left-anchored.
If PC cannot detect left-justification, OR fires on centered, OR calls right-justified left-anchored =>
MACHINERY_UNINFORMATIVE.

## CROSS-SITE
Per site with >=15 usable docs (HT, Khania, Zakros): recompute S_site + swap-null + perm p + direction. Count
sites significant left-anchored (perm p<=0.05 AND S_site>0).

## FROZEN MECHANICAL VERDICT (one token)
- LEFT_MARGIN_ANCHORED_CROSS_SITE iff PC passed (power_est>=0.5, no centered-FP, right-just correctly not
  flagged) AND global S_obs>0 significant (perm p<=0.05) AND significant left-anchored in >=2 sites.
- LEFT_MARGIN_ANCHORED_SITE_LOCAL iff global significant BUT <2 sites significant.
- MARGIN_NOT_ANCHORED iff global S_obs NOT significantly >0 (edges exchangeable).
- RIGHT_MARGIN_ANCHORED iff global S_obs significantly <0 (right edges tighter; right-justified/RTL).
- MARGIN_UNDERPOWERED iff <2 sites with >=15 usable docs OR PC power_est<0.5.
- MACHINERY_UNINFORMATIVE iff PC calibration fails (any of the three arms).

## Outputs (PATH CONTRACT)
prereg.md, plan_hash.txt, machinery.py, result.json, report (EPOCH081_REPORT.md), data dir epoch_081/.
