# EPOCH-084 — Coordinator note: benign gate override + PC-marginality resolution

**Verdict banked:** `LINE_SPACING_DELIBERATE_CROSS_SITE` (confirms/hardens E080). The symmetric partner of E083
(which QUALIFIED E079 as width-driven); E084 CONFIRMS E080's vertical regularity is DELIBERATE.

## Gate override (benign overclaim false-positive)
Gate `passed:false`, `repairs:2`, sole problem = `POSSIBLE_OVERCLAIM` on EPOCH084_REPORT.md line 65 — the
"Bottom line" RESULT DESCRIPTION ("the observed gap arrangement yields lower line-pitch-CV than random gaps would
under preserved row heights"). This is a factual, in fact self-disciplined description (it even adds the caveat
"this indicates the gap arrangement is non-random with respect to pitch regularity, not that the gaps are
independently uniform or ... additively contribute a separable regularity component"). The overclaim scanner
false-fired (same benign pattern as E083's E089-successor flag). Coordinator override, banked.

## PC-marginality resolution (the substantive check)
On first re-confirmation the coordinator saw a false-positive rate of 0.20 (15-rep run) — above the 0.10 bar,
inconsistent with the worker's 0.067 and the pre-launch 0.067. Rather than accept either number, the coordinator
computed a STABLE estimate (60 reps each, across three gap-scales 0.3/0.6/1.0): DETECT = 1.00 throughout;
FALSE-POSITIVE = 0.08 / 0.05 / 0.03. The PC PASSES reliably; the 0.20 was small-sample noise. The vertical test is
slightly noisier than E083's horizontal one (inter-line gaps are larger relative to heights than inter-glyph gaps
are relative to widths), but the false-positive rate is stably ≤ 0.10.

## Independent verification
- `repro_check` PASSED (ran twice, consistent): S_obs = 0.111 vs height-preserving random-gap null 0.161 →
  DELIBERATE (observed BELOW null). Matches result (0.1105 vs 0.1603, perm_p 0.002, ratio 0.69).
- Per-site: HT (0.119 vs 0.173, perm_p 0.002, deliberate ✓), Zakros (0.108 vs 0.142, perm_p 0.032, deliberate ✓),
  Khania (0.111 vs 0.130, perm_p 0.18 — direction right but UNDERPOWERED at n=25). 2/3 sites significant → CROSS_SITE.

## The finding (with E083, the spatial refinement)
E079/E080 established a "2D ruled grid" (pitch regular in both axes). E082→E083→E084 decompose it:
- **Horizontal (E083):** WIDTH-DRIVEN — the within-line glyph regularity is a downstream effect of uniform glyph
  size (E076), NOT deliberate gap spacing.
- **Vertical (E084):** DELIBERATE — the between-line spacing survives a height-preserving null (obs << null,
  2/3 sites, PC passed); the scribes controlled line spacing deliberately.
So the "grid" is really **deliberately-ruled LINES** whose within-line glyph regularity is a byproduct of uniform
glyph size. E080 STANDS and is hardened (regular → deliberately regular); E079's positive STANDS but its
deliberate-spacing interpretation is qualified (E083). Append-only (Art. XVII): E079/E080 ledger entries unchanged.
