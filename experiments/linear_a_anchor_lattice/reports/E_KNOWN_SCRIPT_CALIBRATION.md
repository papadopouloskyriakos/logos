# E_KNOWN_SCRIPT_CALIBRATION — does the shape channel recover known sign identity? (E3, E5)

Seed 20260708. All numbers measured by `scripts/E_stroke_corpus.py`;
raw → `data/stroke_corpus/E_summary.json`.

## E3 — Calibration on KNOWN identities

### Cross-script leg (LB↔Cypriot, LA↔LB) — SOURCE_BLOCKED
The task's four sub-tests (stroke→identity, +chronology→descent, descent→relative-value,
descent→absolute-value) all require **glyph geometry for a second, readable script**. No Linear B
or Cypriot glyph shape data exists in any input (DĀMOS `load_b_damos` is wordform *text*, not
tracings; SigLA is Linear A only). The cross-script stroke calibration is therefore **not
runnable** → SOURCE_BLOCKED. It cannot be faked with fonts (that would be the circular shape-only
transfer, capped ≤0.75 and DO_NOT_REPEAT).

### Within-Linear-A proxy (the only known-identity grouping we hold)
Known-identity grouping = **GORILA sign-name** (palaeographic, non-phonetic). Question: can the
bbox-geometry channel even tell same-sign instance pairs from different-sign pairs? This bounds the
channel's identity power from above. Feature = z-scored [aspect, log relsize]; similarity =
−Euclidean distance; 40 000 same-sign and 40 000 different-sign instance pairs (113 signs, ≥5
instances each).

| representation | identity-discrimination AUC |
|---|---|
| aspect **only** (scale-invariant intrinsic feature) | **0.568** |
| aspect + relative-size | **0.601** |
| chance | 0.500 |
| usable-identity threshold (reference) | ≳0.90 |

**Reading:** the sign-intrinsic feature (aspect) is essentially **at the null** for identity —
0.568. Adding relative-size lifts it to 0.601, but relative-size is scale-confounded, so part of
that lift is drawing-scale, not sign shape. Either way the channel sits **far below** any level that
could assert a sign correspondence. The task's bar — *beat generic visual similarity* — is
structurally unmeetable here because, with strokes/orientation blocked, the channel **is** generic
visual similarity (aspect+size); there is no sign-specific geometry left to add.

**Descent / chronology / value continuity sub-tests:** not run — they are conditional on a
working stroke→identity signal AND on cross-script geometry, both absent. Recorded as
SOURCE_BLOCKED, not as null results.

### Within-allograph-family consistency — UNRUNNABLE
Of 9 multi-member allograph families, **0** have ≥2 members carrying SigLA bbox instances (naming
join gap + rarity). No usable within-family pairs → test not powered.

## E5 — Leave-one-sign-out recovery

Hold out each of 4 405 instances (113 signs); classify to the nearest sign-centroid (LOO-corrected
for the true sign) in z-scored [aspect, log relsize] space.

| metric | value |
|---|---|
| top-1 accuracy | **0.0468** |
| majority baseline (always guess AB81) | 0.0402 |
| uniform chance (1/113) | 0.0088 |
| top-5 accuracy | **0.1637** |
| uniform top-5 (5/113) | 0.0442 |

**Reading:** top-1 (4.68%) barely clears the majority baseline (4.02%) — the channel adds almost
nothing to "guess the commonest sign." There is a *weak aggregate* signal (top-5 16.4% vs 4.4%
uniform, ~3.7×), i.e. bbox geometry weakly narrows the field, but it **cannot recover the identity
of a held-out sign**. This is consistent with the E3 AUC.

## Verdict

`SHAPE_CHANNEL_SOURCE_BLOCKED_FOR_STROKES`. The non-circular palaeographic channel, as it can be
built from the data we hold, carries **no usable sign-identity power** (within-LA AUC 0.57–0.60;
LOSO top-1 ≈ majority baseline). Every sub-channel that would give it power (stroke count,
junctions, curves, orientation, contour embedding) and the entire cross-script calibration are
**SOURCE_BLOCKED**. No transfer licence is earned; no value-bearing correspondence is authorised.
To make this channel real, acquire SigLA's per-document drawings (or another true-tracing source)
and re-run E2(b)+E3; until then this is an honest null-by-blockage, **not** evidence of shape
irrelevance.
