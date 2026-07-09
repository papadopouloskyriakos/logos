# EPOCH-085 REPORT — Heading-Size Hierarchy (top spatial row vs body)

**Task:** Do scribes mark the document heading (top spatial row) with LARGER glyphs than the body?
**Layer:** L2 (opaque IDs, bbox areas + row positions only; no phonetic/semantic values).
**Axis:** size × document REGION (top row vs body). DISTINCT from E077 (word-initial), E078 (frequency), E079–084 (spacing/pitch).

## Method
Per doc: R = log( median glyph AREA in first/top row / median glyph AREA in all remaining rows ).
Global S_obs = median of R over docs. Null = random-row-as-pseudo-heading (uniformly pick a row per doc, recompute R).
Directional perm_p = fraction of null draws with median-R ≥ S_obs (heading LARGER). Per-site + global + synthetic PC.

## Positive Control (gates verdict) — PASSED
- DETECT arm: 40 synthetic docs, first-row areas inflated ×1.7 → power = 1.0 over 20 reps (detect_p ≈ 0.001).
- FALSE-POSITIVE arm: 40 synthetic docs, all rows same distribution → fire-rate = 0.0 (≤ 0.10).
- Machinery is well-calibrated and informative.

## Results

| Level | S_obs | null_median | perm_p | n_docs | significant |
|---|---|---|---|---|---|
| GLOBAL | +0.048 | +0.006 | 0.126 | 215 | no |
| Haghia Triada | +0.092 | +0.009 | **0.020** | 128 | **yes** |
| Khania | −0.141 | −0.007 | 0.977 | 29 | no (REVERSED) |
| Zakros | −0.017 | −0.014 | 0.539 | 20 | no |

## Verdict (frozen rule, mechanical)
**HEADING_SIZE_HIERARCHY_SITE_LOCAL**

PC passed; global NOT significant (perm_p=0.126); exactly 1 site (Haghia Triada) significant → site-local.
Not cross-site (only 1/3 sites significant). Not null (HT is significant). Not underpowered (3 sites ≥15 docs, PC power=1.0).

## Bottom line
The heading/top row does NOT use larger glyphs as a cross-site Linear A convention. The effect is a **Haghia Triada register**: HT's top row is ~9% larger than a random row would be (p=0.020), while Khania is reversed (top row smaller, p=0.977) and Zakros is null. This **mirrors E081's HT-only left-margin justification** — both are visual-hierarchy conventions that appear at Haghia Triada but do not generalize across the Linear A corpus, suggesting HT scribal practice employed a richer set of layout salience cues than the other centres.

A site-local result is a full, expected outcome (the coordinator pre-check flagged the prior as SITE_LOCAL to HT, not a foregone cross-site positive).
