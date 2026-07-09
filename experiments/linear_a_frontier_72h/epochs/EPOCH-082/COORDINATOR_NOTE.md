# EPOCH-082 — Coordinator recovery + PC adjudication (honest MACHINERY_UNINFORMATIVE)

**Verdict banked:** `MACHINERY_UNINFORMATIVE` (the worker's own computed verdict; the coordinator confirms it is the
correct, honest call — NOT rescued).
**Purpose of the epoch:** hardening / robustness of the 2D-ruled-grid finding (E079 horizontal glyph-spacing +
E080 vertical line-spacing) against the arbitrary 0.6×median-glyph-height row-clustering threshold both epochs share
(invariant #3; the analog of E075 hardening E072).

## What happened operationally (worker failure + coordinator recovery)
- **v1** (6 settings × 2 metrics × 2000-draw nulls × per-site × PC) was TOO HEAVY: the GLM worker thrashed to 58
  steps / 932K input tokens / 93K output, produced empty final output and no `machinery.py`/`result.json`. The
  coordinator killed it (stopping ~900K-token repair passes that would have re-failed) and cleaned the dir.
- **v2** (SCAFFOLDED — the exact tested metric functions handed to the worker; 4 settings; 500-draw nulls; tight
  procedure) COMPLETED THE COMPUTATION (`machinery.py` + `run_output.json` with full numbers + verdict), but the
  worker then STALLED ~20 min writing the final `result.json` (same finalization failure mode). The coordinator
  killed the stalled worker and finalized `result.json` from the worker's own `run_output.json`.
- **Split preserved:** GLM did the labor (computed the sweep + PC in `run_output.json`); the coordinator
  independently VERIFIED and ADJUDICATED, then recovered the finalization. The coordinator did not do the science.

## Independent verification (coordinator)
1. **Sweep (robustness) — VERIFIED, exact.** Recomputed S_h and S_v with independent code: tol 0.5/0.6/0.7 →
   S_h 0.333/0.338/0.375 (worker 0.333/0.338/0.375), S_v 0.119/0.111/0.119. Both metrics stay significant
   (perm_p≈0.002) and far below the E079/E080 nulls (~0.76 h, ~0.36 v) at every threshold; 3/3 sites (HT/Khania/
   Zakros) significant for both. **The 2D-grid's raw statistics are genuinely threshold-robust.**
2. **PC false-positive — the failure is REAL, not an E080-style artifact.** The worker's PC failed at
   false-positive rate 0.20 (>0.10 bar). The coordinator independently reconstructed the glyph-level random-layout
   false-positive arm and got an even WORSE rate (up to 1.00; h-only 1.00, v-only 0.60). Because an independent,
   stricter reconstruction made the PC WORSE (not better), this is the OPPOSITE of E080: there the correct null
   FIXED the PC (FP 1.00→0.05) and the positive stood; here the metric is genuinely anti-conservative for
   glyph-level random layouts, so `MACHINERY_UNINFORMATIVE` stands.

## Why the PC genuinely cannot calibrate (the real finding)
The pitch metric is center-to-center: **pitch = inter-glyph gap + glyph width.** Glyph widths are fairly uniform
(E076: glyph size is a shared convention), so the width component **regularizes the pitch even in a random layout**
— any random-gap synthetic still has a width-floored, partly-regular pitch, which the random-COMPOSITION null (which
redistributes total span freely) reads as "more regular than chance." Hence a glyph-level random-layout synthetic is
flagged as regular well above 10%. The metric cannot cleanly reject width-regularized random layouts → the
false-positive control is uncalibratable at the glyph level → `MACHINERY_UNINFORMATIVE`.

## Consequences (honest, bounded)
- **E079/E080 are UNAFFECTED.** Their own positive controls used PITCH-LEVEL random synthetics (pitches drawn
  directly as a random composition — proper) and PASSED. The E082 failure is specific to the GLYPH-LEVEL random
  synthetic, which introduces the width confound. E079/E080's verdicts stand on their own passed PCs.
- **But E082 surfaces a genuine INTERPRETIVE CAVEAT on E079** (recorded against E079, not overturning it): part of
  the observed horizontal-spacing regularity may reflect **uniform glyph widths** (E076) rather than purely
  deliberate even spacing. A width-controlled (edge-to-edge gap) metric is the right successor to separate the two.
- **Secondary caveat:** under the alternative relative-gap row-detection, the vertical-line regularity weakens
  (S_v 0.511 vs ~0.11 under height-thresholds) though it stays directionally significant — the v-regularity is
  somewhat row-detection-method-dependent.

## Why this is the RIGHT outcome (discipline working)
This is the discipline refusing to over-certify: the raw sweep "looks robust," but the epoch's own false-positive
control does not pass, so the epoch returns `MACHINERY_UNINFORMATIVE` and CERTIFIES NOTHING — exactly what should
happen when a control fails, even when the analyst would like the positive. A null/uninformative hardening is not a
stop and not a failure; it bounds what the machinery can certify and hands the width-confound question to a cleaner
successor. Contrast E080 (worker null more correct than the coordinator's check → positive stood) and E059 (worker
null buggy → positive overturned): E082 is the third pattern — the metric itself is uncalibratable for the stricter
test, so no certification either way.
