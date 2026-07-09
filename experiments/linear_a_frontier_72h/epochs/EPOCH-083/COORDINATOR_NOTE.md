# EPOCH-083 — Coordinator note: benign gate override + verification

**Verdict banked:** `HORIZONTAL_REGULARITY_WIDTH_DRIVEN` (unchanged from the worker).
**Gate mechanical outcome:** `passed:false`, `repairs:2`, sole problem =
`POSSIBLE_OVERCLAIM` on result.json line 71 — the **E089 successor hypothesis** proposing a future cross-script
comparison. This is a FALSE POSITIVE of the disclaimer-aware overclaim scanner: the successor is in fact a model of
restraint — it explicitly states the comparison "cannot establish a reference distribution or validate against
known-deliberate vs known-casual writing, and any cross-corpus numeric differences are uninterpretable as evidence
of deliberateness." It is a disciplined future-work note, not a claim about E083's L2 result. Coordinator override,
banked (analogous to E080's gate adjudication).

## Independent verification (coordinator)
- **In-gate `repro_check` PASSED (ran twice, consistent):** S_obs = 0.338 vs width-preserving random-gap null
  0.269 → WIDTH-DRIVEN (observed pitch-CV is NOT below the null; if anything above). Matches result
  (S_obs 0.338, null 0.271, perm_p 1.0, ratio 1.25). (repro n=257 vs result n=237 differ only because repro counts
  >=6-glyph docs while the metric needs >=3 pitches — not load-bearing; S_obs/null identical.)
- **PC re-confirmed from scratch:** DETECT deliberate-even-gaps flagged 1.0; FALSE-POSITIVE width-only-random-gaps
  flagged 0.0 — clean calibration (matches worker PC: PASSED, power 1.0, false-pos 0.0). Crucially, this PC PASSES
  where E082's failed, because the width-preserving null keeps the actual widths in BOTH observed and null, removing
  the glyph-width confound that made E082 uncalibratable.
- **Per-site:** HT (0.381 vs 0.292), Khania (0.291 vs 0.230), Zakros (0.346 vs 0.272) — all three: observed pitch-CV
  ABOVE the width-preserving null, perm_p=1.0, `deliberate=false`. Consistent across all sites.

## What it means (append-only qualification of E079 — Art. XVII)
E079's L2 fact stands: center-to-center PITCH is more regular than a random-COMPOSITION null. But E083 establishes
(with a passing PC) that this regularity is **driven by glyph WIDTH (uniform sizes, E076), NOT by deliberate even
GAP spacing** — the inter-glyph gaps are not deliberately regular (observed is at/above a width-preserving null).
So E079's *interpretation* ("ruled/monospaced-like deliberate spacing") is QUALIFIED: the horizontal "grid" is a
glyph-size-uniformity effect, not a deliberate spacing convention. This does NOT overturn E079's measurement; it
refines what it means. E082 first flagged this (via a failed PC); E083 certifies it (via a passing PC on the clean
width-preserving null). E080 (vertical line spacing) is untouched here — its analogous line-height confound is a
separate successor.
