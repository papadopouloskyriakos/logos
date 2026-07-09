# EPOCH-076 REPORT — Is Normalized Glyph Size a Shared Cross-Site Graphic Convention, or Site-Local?

**Campaign:** Linear A frontier-72h · **Epoch:** 076 (FIRST SPATIAL EPOCH — new data modality: SigLA per-glyph bounding boxes)
**Layer:** L2 (structural graphic property only) · **Verdict:** `GLYPH_SIZE_SHARED_CROSS_SITE`
**Plan hash:** `96c59bcd1bae24794f5e1625ce50966c0bc864df0b16d5c5a7f0ab8f7031c016  prereg.md`

---

## 1. Question (mechanical, value-blind)

Does a sign's normalized GLYPH SIZE follow the **shared** pattern (each sign drawn at a consistent relative
size across sites = a shared graphic-size convention) or the **site-local** pattern (size is site-idiosyncratic)?

Signs are **OPAQUE catalog identifiers** (e.g. `AB59`) used ONLY as identity labels. NO phonetic value, NO
reading, NO meaning is used or implied. Glyph size = bounding-box area. This is a pure L2 structural graphic
property. Context: prior 75 epochs used the LINEAR silver token-streams; this epoch opens the SigLA **bbox**
modality (2D spatial positions + sizes), never used before. The campaign has shown the sign-FREQUENCY
fingerprint is **shared** cross-site (E036) but allograph SHAPE is **site-local** (E017/E020).

## 2. Data & coverage

Source: `experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json` (787 docs, 5144 glyphs; pre-decoded).

| quantity | value |
|---|---|
| usable docs (≥4 non-divider bbox glyphs) | **322** |
| usable glyphs (in usable docs, string sign) | **4130** |
| sites with ≥15 usable docs | Haghia Triada (169), Khania (52), Zakros (28), Phaistos (20), Knossos (19) |
| signs with ≥5 obs per site | HT=89, Khania=28, Zakros=34, Phaistos=11, Knossos=7 |

## 3. Metric (frozen)

1. Per doc (≥4 non-divider bbox glyphs): `log-area = log(max(1, w·h))`; **within-document z-score**
   (subtract doc mean, divide by doc population sd; sd=0 → 1). This is each glyph's **normalized size** —
   per-photo/per-tablet absolute scale is removed.
2. Per (site, sign): mean normalized size; keep cells with **≥5 glyph observations**. A site's **size
   profile** = {sign: mean_norm_size}.
3. Per site-pair: **Pearson r** of the two profiles over their **common signs** (require **≥8 common**).
4. **Null (per pair):** sign-label shuffle — permute {sign→size} in one site's profile over common signs,
   recompute r; **≥2000 draws** (5000 for real data); one-sided `perm_p = frac(null r ≥ observed)`.

Self-check (machinery `__main__`): within-doc z-score mean = 0 (max|mean| = 2e-14 over 322 docs ✓); null
Pearson E[r] ≈ 0.01 on random data ✓; null-data perm_p high ✓.

## 4. Positive Control (SYNTHETIC, gates verdict) — PASSED

| PC component | result |
|---|---|
| (a) DETECT-SHARED (fixed intrinsic sign size across sites + noise) | **power = 1.0** (20 reps, ≥2-sig-pairs gate); mean median_r = **0.911** |
| (b) FALSE-POSITIVE (site-idiosyncratic random sizes) | **false_pos_rate = 0.0**; mean median_r = **0.007**; per-pair perm_p uniform (mean ≈ 0.51) |
| **PC verdict** | **PASSED** (power ≥ 0.5 AND false_pos_rate ≤ 0.10) |

The machinery cleanly separates a shared convention (r≈0.91, always detected) from idiosyncratic sizes
(r≈0.007, never reaching the ≥2-sig-pairs gate). PC is fully synthetic.

> **Deviation note (transparent):** initial PC runs showed an inflated false-positive rate (up to 1.0) caused
> by (i) a stale `__pycache__` and (ii) seed-coupling between the data-generation RNG and the permutation RNG
> when both derived from the same base offset. Resolved by clearing the cache and **fully decoupling** the two
> RNG streams (data seed `1000+rep*7`/`2000+rep*7`; perm RNG `9000+rep*13`/`8000+rep*13`). No change to the
> frozen metric, null, or verdict rule.

## 5. Cross-site results (real data)

5 of 10 site-pairs are testable (≥8 common signs); **all 5 are significant** (perm_p ≤ 0.0016, r > 0).

| site A | site B | common signs | r | perm_p | sig |
|---|---|---:|---:|---:|:---:|
| Haghia Triada | Khania | 25 | **+0.794** | <0.0002 | ✓ |
| Haghia Triada | Phaistos | 11 | **+0.816** | 0.0016 | ✓ |
| Haghia Triada | Zakros | 34 | **+0.698** | <0.0002 | ✓ |
| Khania | Zakros | 18 | **+0.740** | 0.0008 | ✓ |
| Phaistos | Zakros | 9 | **+0.854** | 0.0012 | ✓ |

- **n_pairs_testable = 5**, **n_pairs_sig = 5**, **median r = 0.794**.
- Anchor pairs (Haghia Triada vs each other big site): HT-Khania, HT-Phaistos, HT-Zakros all significant.
  HT-Knossos untestable (only 7 common signs).
- Untestable pairs (Knossos has only 7 signs with ≥5 obs): HT-Knossos, Khania-Knossos, Khania-Phaistos,
  Knossos-Phaistos, Knossos-Zakros.

## 6. Frozen mechanical verdict

PC PASSED (power=1.0 ≥ 0.5, false_pos_rate=0.0 ≤ 0.10) AND ≥2 testable site-pairs significant (5/5, r>0,
perm_p ≤ 0.05) ⇒

### `GLYPH_SIZE_SHARED_CROSS_SITE`

Normalized glyph size is a **SHARED cross-site graphic convention**: each sign is drawn at a consistent
relative size across sites, beyond chance sign-size pairing. This matches the **shared sign-frequency
fingerprint** pattern (E036), NOT the site-local allograph-shape pattern (E017/E020).

## 7. Non-circularity

Within-document z-scoring of log bbox-area removes per-photo/per-tablet absolute pixel scale (no scale leak).
The metric is the cross-site correlation of per-sign **mean** normalized size; the sign-label-shuffle null
destroys the sign→size association, so any correlation is beyond chance sign-size pairing. Sign identity is
an opaque catalog ID — no value/reading/meaning used. L2 only.

## 8. Bottom line

**Glyph size is a SHARED cross-site graphic convention, not site-local.** Every testable site-pair
(5/5) shows a large, significant positive correlation of per-sign normalized size (r ≈ 0.70–0.85,
perm_p ≤ 0.0016), and the synthetic positive control confirms the machinery detects shared conventions
(power=1.0) without firing on idiosyncratic ones (false-positive rate=0.0). This is the same "shared"
structure seen in the sign-frequency fingerprint (E036), and contrasts with site-local allograph shape
(E017/E020).

## 9. Successor hypotheses

- **E077:** Is the shared size convention driven by a few high-frequency signs, or uniform across the
  inventory? (per-sign contribution / leave-one-out)
- **E078:** Does normalized size correlate with a graphic-complexity proxy (stroke/component count)
  cross-site — is the convention complexity-graded?
- **E079:** Is the within-document size RANK of signs shared cross-site (ordinal convention), in addition
  to z-scored magnitude?
- **E080:** Do underpowered sites (Knossos, Phaistos) join the convention with more data (relaxed min-obs /
  pooled periods)?
- **E081:** Is glyph size shared across PERIODS within a site, or period-locked (LM I vs LM III)?
- **E082:** Cross-modal: does the shared size convention align with the shared frequency fingerprint (E036)
  — are frequent signs drawn at a characteristic relative size?
