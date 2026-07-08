# EPOCH-008 — GORILA-plate stroke recovery pilot → STROKE_RECOVERY_PARTIAL

**Frontier F2, gate C · claim layer L1 (sign-form geometry only) · seed 20260708**
**Prereg** `epochs/EPOCH-008/prereg.md` sha256 `67ea9ac471221ec91ebe1067d3696af725b14951d443637c4c9574fa6181e6a2` (frozen before run)
**Addendum** `prereg_addendum1.md` sha256 `197a64249b944624e38a9624781acd0a12158d3b85fab338219133799862334e` (frozen before held-out run)
**Artifacts** `epochs/EPOCH-008/{result.json,result_addendum1.json}`, `data/stroke_pilot/` (SigLA PNGs gitignored, CC BY-NC-SA)
**Articles**: V, VII, VIII, XI/XII, XV (no licence change), XVII (v1 failure preserved, never overwritten), XXII.

## Question and answer

The stroke channel is SOURCE_BLOCKED on the SigLA *database payload* (bbox-only). Can usable
stroke graphs be recovered from published facsimile-derived drawings? **Yes, partially — and
the practical route is NOT GORILA plates but SigLA's per-document trace-render PNGs**
(raster renders of Salgarella's GORILA-derived vector traces, live at
`sigla.phis.me/document/<D>/<D>.png`, CC BY-NC-SA 4.0). Verdict per frozen rules:
**STROKE_RECOVERY_PARTIAL**.

## (1) Licensing / availability audit

| Source | On disk? | Nature | Licence | Stroke-usable? |
|---|---|---|---|---|
| GORILA I–V plates | NO | page scans at cefael.efa.gr (Ét. Crét. 21) | EFA copyright, read-online | blocked for bulk use; segmentation+labelling ≈ 60–120 h |
| SigLA trace PNGs | NO (fetched here: 37 docs) | raster of hand-traced vectors, per document + per-glyph bboxes on disk | CC BY-NC-SA 4.0 (site-stated) | **YES — best route** |
| SigLA database.js (on disk) | yes | bboxes + transcriptions only | CC BY-NC-SA | no strokes (confirmed blocked) |
| `sign_images/{linA,linB}` (on disk) | yes | Aegean.ttf font renders, 96 px | UFAS (research-only) | standardized forms only, not epigraphic |
| Salgarella 2020 ch. 2 PDF | yes | ~655 embedded 150-dpi CMYK glyph cells | CUP copyright | marginal (tiny, tabular) |
| Kanta et al. 2024 | yes | 300-dpi photographs | journal OA page | photos, not drawings |
| Davis 2013 | NO | — | — | not in repo |

## (2) 10-sign pilot extraction (5 AB-shared: DA U RA PI DE · 5 A-only: *321 *333 *310 *301 *309B)

Sample drawn by `random.Random(20260708)` from the full eligible frame (57 AB-shared,
20 A-only attested with ≥12 px bboxes); ≤2 attestations/sign by largest bbox; 19 documents
fetched politely. Positive control (5 synthetic glyphs with analytic endpoint/junction/loop
ground truth) **PASS 5/5** — after two PC-stage extractor fixes (intra-junction-cluster
self-edge artifact; done before any pilot data was touched).

- **v1 (frozen prereg pipeline): 3/10 extraction ok → INFEASIBLE.** Cause: SigLA renders are
  RGBA with ink in the alpha channel and anti-aliasing specks; the frozen `n_components ≤ 3`
  rule dies on specks. (Alpha decoding + a bbox-mode geometric-validity fix were I/O bug
  fixes applied to both pipelines; the despeckle step below was not in the prereg.)
- **v2 (AMENDMENT-A, post-hoc, documented): despeckle (drop components < max(4 px, 2 % of
  largest) + 3×3 closing): 8/10 ok**, per-sign confidence MEDIUM (HIGH ×1). Failures: DE
  (KH 88 bbox catches a stroke tangle), *309B (TY 2 hatching → 55 components).

## (3) Known-script mini-calibration (query = epigraphic trace crop, gallery = 74 LB font renders)

| Metric | v1 frozen | v2 amended | v2 held-out (fresh signs) | font-render upper bound | chance |
|---|---|---|---|---|---|
| stroke MRR | 0.023 | **0.307** | **0.273** (n=4) | 0.653 | 0.066 |
| perm p (20 k) | 0.59 | **0.011** | **0.031** | 5×10⁻⁵ | — |
| aspect-baseline MRR | 0.016 | 0.018 | 0.155 | 0.096 | 0.066 |

Top-1 hits: PI (debug set), KA (held-out). NC3 degradation (25 damaged font variants):
MRR 0.925, retention 1.42 ≥ 0.5 → graph features robust to erode/noise/occlude/rotate/scale.

## (4) Mechanical verdict chain

1. v1 frozen → **STROKE_RECOVERY_INFEASIBLE** (3/10 < 6). Preserved, not overwritten.
2. AMENDMENT-A was adopted after seeing v1 failures ⇒ hypothesis-generating (Art. XII), so a
   **held-out confirmation** was frozen (ADDENDUM-1) on 10 fresh signs
   (TA2 TI WI KA RO · *309 *312 *307 *306 *305), zero overlap, pipeline byte-frozen.
3. Held-out: extraction **7/10** (< 8 bar), calibration MRR 0.273, p 0.031 > chance and
   > aspect 0.155 ⇒ **AMENDMENT_PARTIAL** ⇒ epoch verdict **STROKE_RECOVERY_PARTIAL**.

## Honest accounting

- The binding constraint is no longer source access — it is (a) **bbox intrusion** (neighbour
  strokes/dots inside SigLA bboxes) and (b) the `n_components ≤ 3` criterion being
  **mis-specified for genuinely multi-stroke signs** (TI, *307, *309B are drawn as many
  disconnected strokes; a components cap conflates sign anatomy with noise).
- Discrimination is real but weak: ~4.5× chance MRR on held-out epigraphic crops vs ~10× for
  standardized font renders — the gap is allography + trace noise, not the extractor (PC 5/5,
  NC3 robust).
- n = 4–5 calibration queries per set; effective n is small and preregistered; nothing here
  is a reading, a value, or a licence change (stays L1).
- **Cost to fix**: SigLA full sweep = one ~30-min polite download (802 docs) + compute; the
  GORILA/CEFAEL plate route (60–120 h + permission) is dominated and should not be pursued.
