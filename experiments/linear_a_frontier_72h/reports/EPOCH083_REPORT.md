# EPOCH-083 REPORT — Is E079's Horizontal Pitch-Regulariry Deliberate Even Spacing, or a Glyph-Width Artifact?

**Task ID:** EPOCH-083
**Layer:** L2 (geometry only, opaque IDs, positions only)
**Qualifies/Tests:** E079 (horizontal pitch-regularity)
**Verdict (mechanical, frozen rule):** `HORIZONTAL_REGULARITY_WIDTH_DRIVEN`

---

## 1. Question

E079 found that horizontal center-to-center PITCH is regular (pitch-CV ≈ 0.329 vs a random-composition null ≈ 0.743). But pitch = inter-glyph GAP + glyph WIDTH, and glyph widths are fairly uniform (E076). Uniform widths alone regularize pitch even with random gaps. E082 surfaced this confound and returned `MACHINERY_UNINFORMATIVE` because its positive control could not separate the two mechanisms.

**E083 separates them** with a WIDTH-PRESERVING random-gap null: keep each glyph's actual width and the row's center-span, randomize ONLY the gap allocation, recompute pitch-CV. If observed pitch-CV ≪ this null → gaps are deliberately regular. If observed pitch-CV ≥ this null → the regularity is width-driven and E079 is qualified (the pitch signal is explained by width).

## 2. Method

- **Data:** `experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json`. Exclude `is_divider`; docs with ≥6 non-divider bbox glyphs. Sites with ≥15 usable docs: **Haghia Triada (138), Khania (29), Zakros (21)** — 237 docs total.
- **Observed:** median over docs of E079's center-to-center pitch-CV (rows = y-bands at tol 0.6 × median glyph height; rows with ≥3 glyphs).
- **Null (width-preserving random-gap):** for each row, keep the sorted glyph widths and the center-span; draw `k-1` uniform cut points in the residual gap-space to allocate the `k` gaps; reconstruct pitch = half-width + gap + half-width; take CV. Median over docs.
- **Test:** one-sided permutation, `perm_p = (#{null_median ≤ S_obs} + 1)/(ndraw + 1)`, ndraw = 500. Deliberate spacing = observed pitch-CV significantly BELOW the null (perm_p ≤ 0.05).
- **Discipline:** L2, opaque IDs (no sign identities), bbox geometry only.

## 3. Positive Control (synthetic, gates verdict) — PASSED

| Arm | Construction | Expectation | Result |
|---|---|---|---|
| (a) DETECT | 40 docs, EQUAL gaps + variable widths ~ U[4,9] | perm_p ≤ 0.05 | **detect_p = 0.005** ✓ |
| (a) power | 15 reps of DETECT arm | power ≥ 0.5 | **power_est = 1.0** ✓ |
| (b) FALSE-POS | 40 docs, RANDOM gaps + SAME variable widths | rate ≤ 0.10 | **false_pos_rate = 0.0** ✓ |

The machinery cleanly detects synthetic deliberate even-spacing and produces zero false positives on width-only random-gap docs. **PC PASSED** — the negative corpus result below is a genuine property of the data, not a calibration failure. This also resolves E082's `MACHINERY_UNINFORMATIVE`: the width-preserving null IS separable here.

## 4. Results

### Global (237 docs)
| Metric | Value |
|---|---|
| Observed pitch-CV (S_obs) | **0.338** |
| Width-preserving null median | **0.271** |
| perm_p | **1.0** |
| ratio (S_obs / null) | **1.25** |

Observed pitch-CV is **ABOVE** the width-preserving null (ratio 1.25), not below. perm_p = 1.0 (with the +1 pseudocount, (500+1)/501) indicates that all 500 null draws produced a median pitch-CV ≤ the observed; the test therefore fails to reject the null of deliberate spacing. This does NOT establish that the observed gaps are less regular than random — only that no deliberate regularity was detected once widths were held fixed.

### Per-site
| Site | n_docs | S_obs | null_median | perm_p | deliberate |
|---|---|---|---|---|---|
| Haghia Triada | 138 | 0.381 | 0.292 | 1.0 | false |
| Khania | 29 | 0.291 | 0.230 | 1.0 | false |
| Zakros | 21 | 0.346 | 0.272 | 1.0 | false |

**Zero sites** show observed pitch-CV below the width-preserving null. The result is uniform across all three sites.

## 5. Frozen Verdict

PC PASSED, ≥2 qualifying sites, PC power ≥ 0.5 → not underpowered, not uninformative.
Global perm_p = 1.0 > 0.05 → observed pitch-CV is NOT significantly below the width-preserving null.

→ **`HORIZONTAL_REGULARITY_WIDTH_DRIVEN`**

## 6. Bottom Line

**E079's horizontal pitch-regularity is a glyph-WIDTH artifact, not deliberate even spacing.** Once each glyph's actual width and the row's center-span are held fixed, even *random* gap allocation yields pitch-CV ≈ 0.27 — already at or below the observed 0.338. The inter-glyph GAPS themselves carry no detectable deliberate regularity in any of the three qualifying sites. E079's signal is fully explained by the combination of (i) fairly uniform glyph widths (E076) and (ii) the bounded row span; the apparent evenness of pitch is a geometric consequence, not a scribal intent to space glyphs evenly.

## 7. Non-circularity

The width-preserving null reuses each glyph's actual width and the row center-span; only gap allocation is randomized. This isolates gap-regularity from width-regularity. E079's original random-composition null is replaced by a stricter, width-matched null, so any signal here is NOT explainable by E079's mechanism. No sign identities used; bbox geometry only.

## 8. Successor hypotheses

- **E084 (L2):** Are glyph WIDTHS themselves deliberately uniform within rows (vs corpus-shuffled null)? The width-uniformity that drives pitch-regularity may itself be the deliberate scribal act.
- **E085 (L2):** Decompose pitch-CV into width-CV + gap-CV contributions per row; quantify how much the bounded line span mechanically forces pitch-CV down.
- **E086 (L2):** Apply the identical width/height-preserving null to VERTICAL (inter-row) spacing.
- **E087 (L2):** Per-sign-class width uniformity (geometry only) — do high-frequency signs have especially uniform widths?
- **E088 (L2):** Test deliberate spacing at divider-delimited word/group granularity rather than per-glyph.
- **E089 (L2):** Cross-script control — apply the same null to an external writing corpus to obtain a comparative reference distribution for width-driven pitch-CV. No ground-truth deliberateness label exists for any corpus, so this is exploratory calibration only, not validation against known-deliberate vs known-casual writing.
