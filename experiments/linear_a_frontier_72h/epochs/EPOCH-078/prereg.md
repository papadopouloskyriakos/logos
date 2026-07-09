# EPOCH-078 PREREGISTERED PROTOCOL — Glyph-Size Economy of Effort (cross-site, class-controlled)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-078 (third SigLA spatial epoch; follows E076 shared per-sign size convention, E077 size carries no positional info)
**Layer:** L2 (pure structural graphic property)
**Operator:** logos z.ai research worker (GLM-5.2), proposer/operator only — MECHANICAL verdict from a FROZEN rule.
**Status:** FROZEN before any null-model run.

## 1. QUESTION
Is there an ECONOMY-OF-EFFORT relationship in glyph drawing — do more FREQUENT signs get drawn
systematically SMALLER (spatial compression), the spatial analog of Zipf's law of abbreviation
(frequent words are shorter)? Tested globally, WITHIN a homogeneous sign class (the AB syllabary
vs class A), and CROSS-SITE.

## 2. CRITICAL CONFOUND (load-bearing)
Rare signs may be pictorial LOGOGRAMS (intrinsically complex/large). A raw size↔frequency
correlation could therefore be the logogram/syllabogram size-complexity difference, NOT economy.
This is controlled by testing the correlation WITHIN a homogeneous sign class. The economy verdict
REQUIRES a significant negative correlation within the AB syllabary (r_AB), not merely r_all.

## 3. DATA (verified, pre-decoded)
- `BASE/data/sigla_glyphs_bbox.json` — list of docs; each doc has `glyphs[{sign, bbox:[x,y,w,h], is_divider}]`, plus `site`.
- `BASE/data/sigla_sign_class.json` — map `{sign_name -> class}` with class in {"AB" (77 shared syllabary), "A" (298 Linear-A-only), "N"}.
- EXCLUDE `is_divider` glyphs. Use docs with >=4 non-divider bbox glyphs.

## 4. METRIC (frozen)
- Per doc (>=4 non-divider glyphs): compute log-area = ln(w*h) per glyph; z-score log-area WITHIN the doc (removes per-photo scale).
- Per SIGN: mean within-doc z-size = mean of z-scores over all that sign's glyphs (global pool); corpus frequency = total glyph count.
- Keep signs with FREQ >= 8 (global).
- PRIMARY statistic: r_all = Pearson corr(log(freq), mean_z_size) over kept signs. r<0 <=> economy (frequent drawn smaller).
- CLASS CONTROL: r_AB = same correlation restricted to class-AB signs (freq>=8); r_A = restricted to class-A signs. Report mean z-size of AB vs A signs (confound check: if ~equal, the size difference is not a class effect).

## 5. NULL MODEL (frozen)
FREQUENCY-LABEL shuffle: permute the {sign -> log(freq)} assignment over the kept signs, recompute r;
>=2000 draws; one-sided perm p = frac(null r <= observed r) (economy = more negative than chance).
Run the null for r_all AND r_AB.

## 6. CROSS-SITE
For each site with >=15 docs (Haghia Triada, Khania, Zakros, Phaistos, Knossos, Mallia), recompute
per-sign mean z-size using ONLY that site's glyphs (within-site z-scoring per doc; signs with >=5
glyphs at that site), correlate with GLOBAL log(freq); report r_site + shuffle-null perm p.
Count sites with significant negative r (perm p<=0.05).

## 7. POSITIVE CONTROL (SYNTHETIC — gates verdict)
(a) DETECT: plant signs where size decreases with planted freq; confirm r flagged negative
(perm p<=0.05); power_est over >=20 replicates.
(b) FALSE-POSITIVE: plant size independent of freq; confirm r NOT flagged (rejection rate <=0.10
across >=20 draws).
If miscalibrated -> MACHINERY_UNINFORMATIVE.

## 8. FROZEN MECHANICAL VERDICT (one allowed token)
- `GLYPH_SIZE_FREQUENCY_ECONOMY_CROSS_SITE` iff PC passed AND r_all sig negative (perm p<=0.05) AND r_AB sig negative (survives class control) AND significant negative in >=2 sites.
- `GLYPH_SIZE_ECONOMY_CLASS_CONFOUNDED` iff r_all sig negative BUT r_AB NOT significant.
- `GLYPH_SIZE_ECONOMY_SITE_LOCAL` iff r_all + r_AB significant BUT <2 sites significant.
- `NO_GLYPH_SIZE_ECONOMY` iff r_all NOT significantly negative.
- `GLYPH_SIZE_ECONOMY_UNDERPOWERED` iff <15 class-AB signs with freq>=8 OR PC power_est<0.5.
- `MACHINERY_UNINFORMATIVE` iff PC detect/false-positive calibration fails.

## 9. NON-CIRCULARITY (hard)
glyph size = within-document z-scored log bbox-area (removes per-photo scale); sign frequency =
corpus glyph count; the CLASS CONTROL (AB syllabary vs A) removes the logogram-complexity confound;
the frequency-LABEL-shuffle null destroys the size↔frequency association. size ⊥ frequency by
construction. L2 ONLY: signs are OPAQUE catalog IDs; NO phonetic value, NO reading, NO meaning.

## 10. OUTPUTS
prereg.md, plan_hash.txt, machinery.py (with __main__ self-check), result.json, report, data dir.
result.json keys: task_id="EPOCH-078", method, result, verdict, numbers, key_findings (>=3),
successor_hypotheses (>=5), layer="L2", la_touched=true, non_circular (str), deviations (list).
