# EPOCH-009 — Full-corpus SigLA stroke sweep (frontier F2, gate C/E)

**Prereg:** `epochs/EPOCH-009/prereg.md`, sha256 `ec87a23b87d0c984ba47e79d6b9d8dfd0d83f397fa5a1f05cb188e3cc8d88cdc`,
frozen 2026-07-08T04:44:07Z — BEFORE any corpus render was analyzed. Seed 20260708.
**Claim layer:** L1 (sign-form geometry) only. NO phonetic values anywhere. No licences touched.
**Articles:** V, VII, VIII, IX, XI/XII (LB gallery + AB value ground truth are Unicode/font-standard,
independent of the extraction pipeline), XV, XVIII (trace-standardization assumption), XXII.
**Verdict (mechanical, frozen thresholds): `STROKE_CHANNEL_CALIBRATED_USEFUL`** — all four legs pass.

## What ran

E008's held-out-confirmed pipeline (alpha-channel ink decode → despeckle+closing → skeleton
stroke graph: endpoints/junctions/loops/components/strokes/skel-length/orientation; aspect kept
out as adversary), frozen this time as primary, applied to the ENTIRE SigLA corpus.

- **Positive control** (run first): 5/5 synthetic glyph ground truths — PASS.
- **Acquisition:** 802/802 document renders fetched politely (1.2 s spacing, 1 retry pass,
  0 failures; 767 new + 35 E008 cache; ~330 MB, gitignored, CC BY-NC-SA — no redistribution).
- **Extraction:** 4,756 usable-bbox glyph instances → **3,744 ok (78.7%)**. Failures: 1,009
  `too_many_components` (>8 post-despeckle), 3 bbox-density. 303 sign labels get usable
  signatures (≥1 ok instance); 133 robust (≥3); median 2 instances/label.

## Legs (all preregistered; one confirmatory test each)

### LEG-1 — AB-shared → LB-font calibration at scale (n = 57/57 frame values realized)
| metric | value |
|---|---|
| aggregate-signature MRR (74-render gallery) | **0.1710** |
| NC1 permutation p (20k) | **1.5e-4** (Holm 1.5e-4) |
| NC2 aspect-only adversary MRR | 0.0987 |
| chance MRR | 0.0663 |
| top-1 / top-5 | 3 / 14 (24.6% top-5) |
| per-instance MRR (n=2,575 queries) | 0.1427 |
| E008 pilot (n=5) | 0.273 |

**PASS** (n≥30, p<0.01, beats aspect). Honest reading: the channel is real but modest.
**The n=5 pilot overestimated it** (0.273 → 0.171 at full frame; preregistered
`scale_improves` comparator = FALSE against the pilot). Aggregation over instances does beat
single-instance queries (0.171 vs 0.143, +20% rel.). Top-1 hits: ME, SA, TWE; worst: MI, QE,
SU, JA, QI. The binding loss is the epigraphic-trace → standardized-font domain gap (see LEG-2).

### LEG-2 — within-script allograph stability (signs with ≥4 ok instances, n = 116)
| metric | even/odd (frozen) | doc-disjoint (post-hoc audit) |
|---|---|---|
| split-half self-retrieval MRR | **0.3993** | 0.3888 |
| top-1 / top-5 | 33 / 59 (51% top-5) | 32 / 59 |
| aspect adversary MRR | 0.1126 | 0.0786 |
| permutation p | **5e-5** (Holm 1e-4) | 5e-5 |
| chance MRR | 0.0459 | 0.0463 |

**PASS**, and the post-hoc document-disjoint split (no same-document/tracing-session pair
crosses the halves) barely moves it → NOT same-document leakage. Class breakdown
(doc-disjoint): AB signs 0.49 (n=68), A3xx dark signs 0.23 (n=15), other A-labels 0.25 (n=32)
— all ≫ chance 0.046.

### LEG-3 — dark-sign coverage (the 69 A3xx signs)
**65/69 usable (94.2%)**; 21/69 robust (≥3 instances). Missing: A335, A347, A361, A365.
Secondary: 223 of 259 A-labels usable overall. **PASS** (≥0.50).

## Output channel

`data/stroke_corpus/stroke_similarity_matrix.{json,npz}` — 377 names (303 epigraphic
aggregate signatures + 74 LB-font renders as a MARKED separate block), channels decomposed:
topology z-distance (5 count features), orientation-histogram L1, |Δlog aspect|, combined
11-dim z-Euclid. Per-name instance counts and per-instance features
(`data/stroke_corpus/features/instances.json`) included. NO values, NO readings.

**Honest power statement (attach to any downstream use):** cross-standardization retrieval
MRR 0.171 / top-5 25% (i.e., a stroke-similarity neighborhood is a weak, real prior — wrong
3 times out of 4 even at top-5); within-corpus allograph identity MRR ~0.39 / top-5 51%.
The channel is stronger as an LA-internal form-clustering axis than as an LA→LB bridge.
Trace-standardization caveat (Art. XVIII): SigLA traces are expert re-drawings made with
knowledge of sign identity; all stability numbers are UPPER BOUNDS on photograph-level
allography. LEG-1 is immune to label circularity (gallery + truth are font/Unicode-standard).

## Deviations

None from the frozen thresholds or pipeline. Post-hoc analyses (doc-disjoint split, class
breakdowns, hit lists) are labeled POSTHOC in `epochs/EPOCH-009/posthoc.json` and change no
verdict. The `scale_improves=false` finding is reported exactly as preregistered.

## Artifacts

- `epochs/EPOCH-009/{prereg.md,result.json,posthoc.json}`
- `scripts/{epoch009_fetch.py,epoch009_stroke_corpus.py,epoch009_posthoc.py}`
- `data/stroke_corpus/{renders/ (802, gitignored), features/, stroke_similarity_matrix.json,
  stroke_similarity_matrix.npz, fetch_log.json}`
