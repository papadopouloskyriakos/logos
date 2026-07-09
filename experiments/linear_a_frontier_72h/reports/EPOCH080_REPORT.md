# EPOCH-080 REPORT — Vertical Row-to-Row Spacing (Line Pitch) Regularity (ruled horizontal lines / page grid), cross-site

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-080 (fifth SigLA spatial epoch; ORTHOGONAL PARTNER to E079)
**Layer:** L2 (pure structural graphic / layout property)
**Verdict:** `LINE_SPACING_REGULAR_CROSS_SITE`
**Operator:** logos z.ai research worker (GLM-5.2), proposer/operator only — MECHANICAL verdict from a FROZEN rule.

---

## 1. QUESTION

E079 established that HORIZONTAL glyph spacing WITHIN a line is regular (glyphs evenly spaced along the
line, pitch-CV 0.329 vs random null 0.743, cross-site 3/3). E080 asks the **perpendicular** question:
are the LINES themselves evenly spaced DOWN the document — i.e., is the VERTICAL distance between
consecutive rows uniform (like ruled horizontal lines on a page), more so than a random partition of
the column height, and consistent cross-site? A scribe could have even glyph spacing but uneven line
spacing (or vice versa); the two are independent layout properties, and together (if both regular)
they establish a full 2D ruled GRID. Pure structural layout property (L2): signs are OPAQUE IDs; NO
value, NO reading, NO meaning; only glyph POSITIONS (row y-positions) matter.

## 2. METHOD (frozen in prereg.md)

- **Row clustering:** glyphs (non-divider) clustered into rows by y-center within 0.6 × median glyph-height.
- **Row y-position:** median y-center of the row's glyphs.
- **Vertical pitch:** consecutive row-position differences (rows sorted top-to-bottom).
- **Doc line-pitch-CV:** sd/mean of the doc's vertical pitches.
- **Corpus statistic S_obs:** MEDIAN doc line-pitch-CV over usable docs (≥6 non-divider glyphs AND ≥3 rows).
- **Null (random row-allocation):** for each doc, replace its vertical pitches with a uniform-Dirichlet /
  random-breakpoint composition summing to the SAME total row-span (same row count, same column height),
  **conditioned on every pitch exceeding the row-clustering tolerance** (exchangeability correction — see
  §6), recompute doc line-pitch-CV; S = median; 2000 draws; one-sided perm p = frac(null S ≤ S_obs).
- **DISTINCT from E079:** E079 = horizontal within-row glyph pitch (x-direction); E080 = vertical between-row
  line pitch (y-direction). Shared row-clustering primitive, orthogonal metrics.

## 3. DATA

- Source: `BASE/data/sigla_glyphs_bbox.json` (787 docs).
- Usable (≥6 non-divider glyphs AND ≥3 rows): **197 docs**.
- Sites with ≥15 usable docs (testable): **Haghia Triada (124), Khania (26), Zakros (21)** — 3 sites.
- Other sites: Phaistos (7), Arkhanos (7), Knossos (4) — below threshold, not tested.

## 4. GLOBAL RESULT

| statistic | value |
|---|---|
| n_docs | 197 |
| **S_obs** (median doc line-pitch-CV) | **0.1181** |
| null_median | 0.3541 |
| **perm_p** (2000 draws) | **0.0000** |
| ratio (S_obs / null_median) | 0.3335 |

Observed vertical pitches are ~3× more uniform than a random partition of the same column heights.
Lines are laid out at near-equal vertical intervals — a ruled/regular layout.

## 5. CROSS-SITE

| site | n_docs | S_site | null_median | perm_p | sig_regular |
|---|---|---|---|---|---|
| Haghia Triada | 124 | 0.1213 | 0.3632 | 0.0000 | **YES** |
| Khania | 26 | 0.1177 | 0.3125 | 0.0000 | **YES** |
| Zakros | 21 | 0.1081 | 0.3514 | 0.0000 | **YES** |

**3/3 testable sites significant regular.** All three sites are remarkably consistent (S_site 0.108–0.121)
and far below their site-specific nulls (~0.31–0.36).

## 6. POSITIVE CONTROL (synthetic, gates verdict) — PASSED

| check | result |
|---|---|
| detect_p_med (regular-rows synth) | 0.0000 |
| **power_est** (DETECT) | **1.000** |
| **false_pos_rate** (random-rows synth) | **0.080** (≤ 0.10) |
| pc_verdict | **PASSED** |
| self-check (regular obs<<null; random obs~null) | PASS |

**Null refinement (documented deviation, pre-data):** the preregistered random row-allocation null was
made **clustering-conditional** — null compositions are rejected if any pitch falls below the 0.6 ×
median-glyph-height row-clustering tolerance. Rationale: the observed pitches all exceed that tolerance
by construction (the clustering merges any closer rows), so an unconditional null — which freely produces
sub-tolerance pitches — is not exchangeable with the observed and inflates the false-positive rate
(unconditional fp_rate = 0.72 on random-rows synthetic; conditional fp_rate = 0.080). The conditional null
restores exchangeability while preserving the prereg's intent (same row count, same column span, destroys
only regularity). **The regularity finding does NOT depend on this refinement**: even the unconditional
null gives perm_p = 0.0 on the real data (S_obs 0.118 vs unconditional null 0.674); the refinement affects
only PC calibration.

## 7. FROZEN MECHANICAL VERDICT

Verdict rule (frozen in prereg §8):
- PC passed (power_est ≥ 0.5): **YES** (1.000)
- Global S_obs significantly < null (perm p ≤ 0.05): **YES** (p = 0.0)
- Significant regular in ≥ 2 sites: **YES** (3/3)

→ **`LINE_SPACING_REGULAR_CROSS_SITE`**

## 8. BOTTOM LINE — does this, with E079, imply a 2D ruled grid?

**Yes.** Vertical LINE spacing is a deliberate ruled/regular layout, cross-site: the median doc
line-pitch-CV is 0.118 — about one-third of a random row-allocation null (0.354, perm p = 0.0) — and
this replicates cleanly in all 3 testable sites (Haghia Triada, Khania, Zakros, all p = 0.0). Combined
with E079 (horizontal within-row glyph pitch regular, CV 0.329 vs null 0.743, cross-site 3/3), **both
axes of the Linear A writing surface are laid out at regular intervals: a full 2D ruled grid.** The
vertical regularity (CV 0.118) is notably tighter than the horizontal (CV 0.329), suggesting line
spacing is more rigidly controlled than within-line glyph spacing — consistent with pre-ruled horizontal
guidelines (explicit or mental) on which glyphs are then placed with somewhat looser horizontal discipline.

## 9. SCOPE / OPAQUE

L2 only. Signs are opaque catalog IDs. No reading, no value, no meaning. Only POSITIONS (row y-positions)
matter. PC is synthetic (declared).
