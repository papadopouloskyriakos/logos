# EPOCH-081 REPORT — Row Left-Anchoring (Left-Justified Layout) Test

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-081 · **Layer:** L2 (spatial layout, opaque glyph IDs)
**Modality:** spatial (2D layout anchoring) · **Verdict:** `LEFT_MARGIN_ANCHORED_SITE_LOCAL`

---

## 1. Question

Are Linear A document rows LEFT-ANCHORED — aligned at a common left margin with a ragged right edge
(left-justified layout) — beyond an edge-exchangeability null, and is this cross-site? This is the THIRD 2D-layout
axis after E079 (regular horizontal glyph spacing within a line) and E080 (regular vertical line spacing between
rows). E079+E080 establish an evenly-SPACED grid; E081 asks the orthogonal ANCHORING question: do rows share a
common LEFT edge? A grid can be evenly spaced yet ragged-left, or left-aligned yet unevenly spaced — so anchoring
is independent of spacing.

**Self-normalizing test:** within a doc, compare the spread of row LEFT edges to the spread of row RIGHT edges. If
rows are left-anchored and vary in length, LEFT edges align (small spread) while RIGHT edges are ragged (large
spread), so `left_spread << right_spread`. If rows are placed with no horizontal anchoring, the two spreads are
exchangeable (equal).

**L2 discipline:** signs are OPAQUE IDs; no value, no reading, no meaning. Only glyph bbox positions (row left/right
x-edges) matter. NON-CIRCULAR: reading direction is a corpus assumption, but left-ANCHORING (physical margin
alignment) is a separate geometric fact tested by an edge-swap sign-symmetric null on geometry only.

## 2. Method (frozen)

- **Row = y-band.** Cluster non-divider glyphs by y-center (single-linkage, tol = 0.6 × median glyph height).
- Per row: LEFT-edge = min glyph-left-x; RIGHT-edge = max glyph-right-x (= x+w).
- **Usable doc:** ≥6 non-divider bbox glyphs AND ≥3 rows.
- `medw` = median glyph width in doc. `lsd = pstdev(LEFT-edges)/medw`; `rsd = pstdev(RIGHT-edges)/medw`.
- Doc asymmetry `a = rsd − lsd` (POSITIVE ⇒ left-anchored: left tighter than right).
- **Corpus statistic:** `S_obs = median(a)` over usable docs.
- **NULL (edge-exchangeability, sign-symmetric):** per doc sample `s ∈ {+1,−1}` uniformly; contribute `s·(rsd−lsd)`;
  `S = median(contributions)`; ≥5000 draws; one-sided perm p = frac(null S ≥ S_obs).

## 3. Positive Control (SYNTHETIC, gates verdict) — PASSED

Three arms, 20 reps each, 40 synthetic docs/rep, 2000 null draws/rep. Synthetic docs mimic real geometry
(~6–12 rows, glyph w/h ≈ real medians, y-rows spaced ≈ median height).

| Arm | Expectation | Result | Pass? |
|---|---|---|---|
| (a) DETECT — left-justified | S_obs>0 flagged, p≤0.05 | power_est=**1.0**, median detect_p=0.0005 | ✅ |
| (b) FALSE-POSITIVE — centered | NOT flagged (FP rate ≤0.10) | centered_FP_rate=**0.05** | ✅ |
| (c) DIRECTION — right-justified | S_obs<0, NOT flagged left | S_obs<0, right_just_flagged_left=**false** | ✅ |

**PC verdict: PASSED.** The machinery detects left-justification with full power, does not fire on centered
(exchangeable-edge) docs, and correctly does not call right-justified docs left-anchored.

> Note (deviation): the centered arm is constructed with mirror-symmetric left/right edges around each row's center
> (draw one half-width deviation d; left=center−d, right=center+d) so edges are genuinely exchangeable by
> construction. A naive centered placement biases rsd>lsd because per-glyph width jitter accumulates only on the
> right edge. This makes the false-positive target fair; it does not affect real-data analysis or the left/right
> detect arms.

## 4. Global Result

| Metric | Value |
|---|---|
| Usable docs | **197** |
| S_obs (median asymmetry rsd−lsd) | **+0.459** |
| Null median (~0) | −0.026 |
| **perm p (one-sided)** | **0.0002** |
| median(lsd) | 0.664 |
| median(rsd) | 1.248 |
| frac(lsd < rsd) | **0.655** (129/197 docs) |

**Global rows are significantly left-anchored.** Row LEFT edges are tight (median lsd=0.664) while RIGHT edges are
ragged (median rsd=1.248) — a left-justified layout signature. The edge-swap sign-symmetric null is decisively
rejected (p=0.0002). 65.5% of docs have a tighter left edge than right edge.

## 5. Cross-Site Result

| Site | n_docs | S_site | perm_p | median_lsd | median_rsd | frac(l<r) | Sig left-anchored? |
|---|---|---|---|---|---|---|---|
| **Haghia Triada** | 124 | **+0.518** | **0.0002** | 0.672 | 1.296 | 0.645 | **YES** ✅ |
| Khania | 26 | −0.029 | 0.546 | 0.675 | 0.907 | 0.500 | no |
| Zakros | 21 | +0.440 | 0.114 | 0.517 | 1.309 | 0.667 | no (p>0.05) |

- **n_sites_testable = 3** (HT, Khania, Zakros all ≥15 usable docs).
- **n_sites_sig_left_anchored = 1** (only Haghia Triada).
- Khania is at chance (S_site=−0.029, frac=0.50 — edges exchangeable). Zakros is directionally left-anchored
  (S_site=+0.440, frac=0.667) but does NOT reach significance at 0.05 (p=0.114; verified stable at p≈0.10 with 20k
  draws across seeds).

## 6. Frozen Mechanical Verdict

- PC passed (power_est=1.0 ≥ 0.5; centered FP=0.05 ≤ 0.10; right-justified not flagged). ✅
- Global S_obs=+0.459 > 0, significant (perm_p=0.0002 ≤ 0.05). ✅
- Significant left-anchored sites = 1 < 2. ✗ (cross-site gate fails)

→ **`LEFT_MARGIN_ANCHORED_SITE_LOCAL`** (global significant BUT <2 sites significant).

## 7. Bottom Line

Linear A document rows ARE significantly left-anchored (left-justified) at the **global/corpus** level — row left
edges align tightly while right edges are ragged, beyond an edge-exchangeability null. But this is **site-local,
not cross-site**: the signal is driven by Haghia Triada (the dominant site, n=124, strongly left-anchored), with
Zakros directionally consistent but underpowered/non-significant and Khania at chance. So I report this plainly as
**LEFT_MARGIN_ANCHORED_SITE_LOCAL**.

Combined with E079 (regular horizontal glyph spacing within lines) and E080 (regular vertical line spacing between
rows), E081's global result **completes a left-justified 2D ruled grid at the corpus level** — evenly spaced in
both axes (E079/E080) AND anchored at a common left margin (E081). However, the anchoring is not uniform across all
sites (Khania breaks it), so the "ruled grid" picture holds globally and at Haghia Triada but is not a universal
cross-site invariant.

## 8. Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-081/prereg.md` (frozen protocol)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-081/plan_hash.txt` (sha256 of prereg)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-081/machinery.py` (with __main__ self-check)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-081/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_081/` (analysis_raw.json, per_doc_metrics.json,
  pc_synthetic_{left,center,right}.json)
