# EPOCH-008 — GORILA-plate stroke recovery pilot (frontier F2, gate C)

**Frozen:** 2026-07-08 (hash = sha256 of this file, recorded in result.json)
**Seed:** 20260708
**Claim layer:** L1 (sign-form geometry / palaeography). No L2+ claims. No transfer licences touched.
**Articles triggered:** V (layer wording), VII (search receipt), VIII (effective n), XI/XII
(non-circularity: the LB gallery and the value-identity ground truth are Unicode/AB-standard,
independent of the extraction pipeline), XV (no licence change), XXII (this header).

## Question

The per-instance stroke channel is SOURCE_BLOCKED on the SigLA *database payload* (bbox-only).
Can usable stroke graphs nevertheless be recovered from PUBLISHED facsimile-derived drawings —
(a) material already on disk, (b) SigLA's per-document trace PNG renders (raster renders of
Salgarella's GORILA-derived vector traces, CC BY-NC-SA 4.0, live at sigla.phis.me), and what
would GORILA-plate acquisition itself cost?

## Pre-run source-inventory facts (audit, completed before this freeze; not outcomes)

- On disk there are NO GORILA facsimile plates. Available drawing-like material:
  1. `corpus/bronze/sign_images/{linA,linB,damaged}` — 88 LA + 74 LB **font renders**
     (Aegean.ttf, 96 px) + 525 degraded variants. Standardized typographic forms, not epigraphic.
  2. `corpus/bronze/salgarella_2020/10.0_*.pdf` — ~655 embedded raster images, mostly tiny
     150-dpi CMYK glyph cells (CUP copyright).
  3. `corpus/bronze/kanta_etal_2024_anetaki/*.pdf` — 300-dpi photographs (not line drawings).
  4. `corpus/bronze/sigla_browse_2026/` — bboxes + transcriptions for 802 docs, no images.
- Live probes (HTTP 200): `sigla.phis.me/document/<D>/<D>.png` (full-document trace render);
  `cefael.efa.gr` (GORILA = Études Crétoises 21, page scans, EFA copyright, read-online).

## Sample (deterministic; frozen procedure, executed by the run script)

- Map Unicode Linear A codepoints → AB numbers (unicodedata names) → editorial values
  (`corpus/bronze/palaeo/linA_codepoint_map.json`); SigLA transcription names `AB<nn>` / `A3xx`.
- **Eligible AB-shared**: value in the 57 shared values ∧ LA font render exists ∧ LB font render
  exists ∧ ≥1 SigLA attestation with a non-degenerate bbox (w,h ≥ 12 px under the chosen bbox
  interpretation).
- **Eligible A-only**: LA font render `*NNN.png` (base number, ignoring B/C variant suffixes) ∧
  SigLA sign `A<NNN>` attested with a non-degenerate bbox.
- `random.Random(20260708).sample(sorted(eligible), 5)` for each group → 10 pilot signs.
- Per sign: top-2 attestations by bbox area (prefer distinct documents). Download only the
  needed full-document PNGs (expected ≤ 20 files), polite ≥1.5 s spacing, single pass, kept
  gitignored (CC BY-NC-SA; research use, no redistribution).
- Bbox interpretation ([x,y,w,h] vs [x,y,x2,y2]): choose whichever maximizes mean in-box ink
  density across each document's glyphs; record the choice. If neither yields in-box ink density
  > global density, the crop FAILS (counts against extraction).

## Pipeline (rule-based, deterministic)

Binarize (Otsu on grayscale, ink = darker side, auto-invert), largest-margin pad, then
`skimage.morphology.skeletonize`. Skeleton graph: endpoints (deg 1), junction clusters
(deg ≥ 3, merged within 8-neighbourhood), connected components C, cycles = E − V + C on the
condensed critical-point graph; features:
`[n_endpoints, n_junctions, n_loops, n_components, n_strokes(=condensed edges),
 skel_len/sqrt(area_bbox), orientation histogram (4 bins, weighted by segment length)]`
plus, kept OUT of the stroke vector: bbox aspect ratio (baseline feature).
Distance = Euclidean on gallery-z-scored stroke features.

## Controls (run FIRST)

- **PC (positive control):** 5 synthetic 96-px glyphs with analytic ground truth —
  `+` (4 endpoints,1 junction,0 loops), `O` (0,0,1), `T` (3,1,0), `X` (4,1,0), `L` (2,0,0 with
  1 corner tolerated as junction 0..1). PASS iff ≥4/5 match ground truth exactly on
  (endpoints, junctions, loops) with the stated L tolerance. PC fail ⇒ verdict INFEASIBLE
  (pipeline invalid), regardless of everything else.
- **NC1 (chance):** permutation null for MRR — 20,000 draws of 5 iid uniform ranks over the
  74-sign LB gallery; one-sided p = P(null MRR ≥ observed).
- **NC2 (cheap-feature adversary):** aspect-ratio-only ranking of the same queries.
- **NC3 (degradation):** damaged font variants (erode/noise/occlude/rotate/scale) of the 5
  AB-shared LA signs as queries; retention = MRR_damaged / MRR_clean_font.

## Calibration (5 AB-shared signs)

Query = SigLA epigraphic trace crop (primary) and LA font render (same-source upper bound);
gallery = 74 LB font renders; truth = same editorial value. Metrics: MRR, top-5 count.

## Mechanical verdict (frozen)

- `extraction_ok(sign)` := crop obtained ∧ ink fraction ∈ [0.01, 0.6] ∧ skeleton graph produced
  ∧ n_components ≤ 3 ∧ all features finite. Confidence per sign: HIGH if additionally
  n_components = 1, else MEDIUM.
- **STROKE_RECOVERY_FEASIBLE** iff PC PASS ∧ extraction_ok ≥ 8/10 ∧ epigraphic-query stroke
  MRR p < 0.05 (NC1) ∧ stroke MRR > aspect MRR (NC2).
- **STROKE_RECOVERY_PARTIAL** iff PC PASS ∧ extraction_ok ≥ 6/10 ∧ ¬FEASIBLE.
- **STROKE_RECOVERY_INFEASIBLE / SOURCE_BLOCKED** otherwise.
- FEASIBLE, if reached, is earned via the **SigLA-trace route** (raster renders of traces);
  the GORILA-plate route proper is priced (per-sign cost estimate) but not claimed, since no
  plate scans are processed here. Wording of any result stays at L1.

## Honest-accounting commitments

- The LB gallery is font-rendered; a hit therefore shows the stroke graph of an *epigraphic
  trace* carries enough geometry to find the *standardized* counterpart — exactly the practical
  use case — but per-instance LA↔LA allography is NOT tested beyond the ≤2-instance
  consistency check, and nothing here supports any reading.
- n = 5 calibration signs (effective n = 5, one query family, preregistered once; no sign
  cherry-picking — RNG sample from the full eligible frame).
- If SigLA downloads fail mid-run, the affected signs count as extraction failures (fail closed).
