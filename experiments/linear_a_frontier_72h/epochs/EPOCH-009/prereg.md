# EPOCH-009 — Full-corpus SigLA stroke sweep (frontier F2, gate C/E)

**Frozen:** 2026-07-08 (hash = sha256 of this file, recorded in result.json BEFORE the run)
**Seed:** 20260708
**Claim layer:** L1 (sign-form geometry / palaeography) only. No L2+ claims, NO phonetic values
anywhere in any output. No transfer licences touched.
**Articles triggered:** V (layer wording), VII (search receipt), VIII (effective n), IX (info
budget: the channel output is a similarity matrix, not a reading), XI/XII (non-circularity: the
LB font gallery and the AB value-identity ground truth are Unicode/AB-standard and independent
of the extraction pipeline; SigLA bboxes/labels are used only to LOCATE and GROUP instances,
never to score identity against themselves), XV (no licence change), XVIII (assumption:
Salgarella's traces were drawn by a human who knew sign identities — trace-standardization may
inflate within-sign consistency vs photographs; carried as a channel caveat on every output),
XXII (this header).

## Question

E008 unblocked the per-instance stroke channel (SigLA alpha-channel trace renders) and showed a
real-but-weak counterpart signal on a 5-sign pilot (held-out MRR .273 vs chance .066, aspect
adversary .155). Scale it to the FULL SigLA corpus: (1) does per-sign aggregation across many
instances sharpen the AB-shared→LB calibration signal? (2) is the within-script allograph
signature stable (split-half self-retrieval)? (3) how many of the 69 A-only A3xx signs get
usable stroke signatures? (4) emit the calibrated all-pairs stroke-similarity matrix as a
lattice-ready channel with an honest power statement.

## Pre-freeze frame facts (inventory only, no pipeline outputs)

- SigLA browse DB on disk: 802 documents, 5,144 glyph records; 4,756 instances with sign label
  + non-degenerate bbox (w,h ≥ 12 px): 80 `AB\d+` labels, 259 `A\d+` labels, 1 other (N800).
- **The 69 "dark signs" frame** := SigLA labels `A301..A371` excluding A302, A348 (never
  assigned/attested) = exactly 69 labels, all attested with ≥1 usable bbox. A4xx–A7xx
  (composites/logograms/fractions/klasmatograms) are reported as SECONDARY coverage only.
- E008 cache: ~27 doc renders already under `data/stroke_pilot/sigla_raw/` (reused, not
  re-fetched). Render ≈ 0.4 MB each; full corpus ≈ 330 MB — full fetch is feasible, so the
  full-corpus route is chosen (the ≥200-doc stratified fallback below only triggers on fetch
  failure).

## Acquisition (polite, single-threaded, cached, gitignored)

- URL: `https://sigla.phis.me/document/<D>/<D>.png` (CC BY-NC-SA 4.0; research use, no
  redistribution). UA `logos-epoch009-stroke-sweep/1.0`; ≥1.2 s spacing; one pass over all 802
  designations + ONE retry pass over failures; cache dir
  `data/stroke_corpus/renders/` (E008 files copied in first).
- Docs failing both passes = missing; their instances count as extraction failures (fail
  closed). If < 200 documents are fetched in total, the epoch ABORTS as `SOURCE_BLOCKED`.

## Pipeline (rule-based, deterministic; frozen NOW — E008 v2 with two preregistered fixes)

1. Bbox mode per document ([x,y,w,h] vs [x,y,x2,y2]): E008 bug-fixed rule — geometric validity
   first, then max mean in-box ink density; recorded per doc. In-box density must exceed global
   density, else the doc's crops fail.
2. Crop → if max dimension > 512 px, downscale to 512 (LANCZOS) [new, deterministic guard].
3. Binarize: alpha-channel ink decode when a real alpha channel exists, else Otsu on grayscale
   with border-vote inversion (E008 `binarize`).
4. Despeckle + 3×3 closing (E008 AMENDMENT-A, held-out-confirmed; now frozen primary).
5. Skeletonize → stroke graph (E008 `skeleton_graph`): endpoints, junction clusters, loops,
   components, condensed edges (strokes), skel_len/sqrt(bbox area), 4-bin length-weighted
   orientation histogram. Aspect ratio kept OUT of the stroke vector (adversary feature).
6. `extraction_ok(instance)` := crop obtained ∧ ink fraction ∈ [0.01, 0.6] ∧ skeleton graph
   produced ∧ all features finite ∧ n_components ≤ 8 [cap raised from E008's 3: E008 showed the
   3-cap is mis-specified for genuinely multi-component signs (TI, *307, *309B); 8 chosen NOW].

## Aggregation

- Per SigLA sign label: signature = per-feature MEAN over ok instances; allograph spread =
  per-feature SD + mean pairwise z-distance (z from the all-instance pool). Usable signature :=
  ≥1 ok instance; robust := ≥3 ok instances.

## Legs & controls (PC first; fail closed)

- **PC (positive control, run FIRST):** E008's 5 synthetic glyphs (+ O T X L) with analytic
  (endpoints, junctions, loops) ground truth; PASS ≥4/5. FAIL ⇒ verdict NOT_USABLE, stop.
- **LEG-1 calibration at scale (AB-shared → LB font gallery, 74 renders):** eligible values =
  the 57 shared values with LA+LB font renders ∧ ≥1 SigLA `AB<nn>` attestation (E008 frame,
  unicodedata AB-number map). Query = per-value AGGREGATE epigraphic signature; rank over the
  74-render gallery by Euclidean distance on gallery-z-scored stroke features; truth = same
  editorial value. Metrics: MRR, top-1, top-5.
  NC1 chance: 20,000-draw permutation null (iid uniform ranks, n = realized query count);
  one-sided p. NC2 adversary: aspect-only ranking of the same queries. Scale comparison
  (descriptive, direction preregistered): per-instance MRR (every ok instance as its own query)
  vs aggregate MRR vs E008 pilot .273.
- **LEG-2 allograph stability (within-script, label-blind identity):** signs of ANY label with
  ≥4 ok instances; split instances even/odd by sorted (designation, glyph index); half-A
  signature queries the gallery of ALL half-B signatures (z-scored on that gallery); rank of own
  sign. Self-retrieval MRR + 20,000-draw permutation p. NC2b: aspect-only same protocol.
- **LEG-3 dark-sign coverage:** usable + robust signature counts over the 69 A3xx frame
  (primary) and over all 259 A-labels (secondary, descriptive).
- **Output:** all-pairs similarity matrix over every usable signature + the 74 LB font renders
  as a marked separate block; channels DECOMPOSED (topology z-distance on the 5 count features;
  orientation-histogram L1; |Δlog aspect|; combined z-Euclid), NO values/readings; written to
  `data/stroke_corpus/stroke_similarity_matrix.json` (+ per-instance features parquet/json).

## Mechanical verdict (frozen thresholds)

- LEG1_PASS := realized calibration n ≥ 30 ∧ NC1 p(MRR_agg) < 0.01 ∧ MRR_agg > MRR_aspect_agg.
- LEG1_WEAK := realized n ≥ 30 ∧ p < 0.05 ∧ MRR_agg > MRR_aspect_agg.
- LEG2_PASS := stability n ≥ 15 signs ∧ p(self-MRR) < 0.01 ∧ self-MRR > aspect self-MRR.
- LEG3_PASS := usable coverage of the 69-sign frame ≥ 0.50.
- **STROKE_CHANNEL_CALIBRATED_USEFUL** := PC ∧ LEG1_PASS ∧ LEG2_PASS ∧ LEG3_PASS.
- **STROKE_CHANNEL_CALIBRATED_WEAK** := PC ∧ LEG1_WEAK ∧ (LEG2_PASS ∨ LEG3_PASS) ∧ ¬USEFUL.
- **STROKE_CHANNEL_NOT_USABLE** := otherwise (incl. PC fail or SOURCE_BLOCKED abort).
- Multiplicity: exactly one confirmatory test per leg (2 p-values total); Holm over {p1, p2}
  reported alongside raw. Everything else (scale comparison, secondary coverage, matrix
  descriptives) is descriptive and worded as such.

## Honest-accounting commitments

- A calibration hit shows an epigraphic-trace stroke graph can find the STANDARDIZED LB
  counterpart form; it supports NO reading and no sign-value claim (L1 only).
- Trace-standardization confound (Art. XVIII assumption above): traces are human re-drawings by
  an expert who knew the sign identities; stability (LEG-2) is therefore an UPPER BOUND on
  photograph-level allograph stability. Stated on every output.
- effective n: LEG-1 n = realized eligible values (≤ 57), one query family, no sign selection
  by the analyst (frame is exhaustive). LEG-2 n = all qualifying signs, exhaustive.
- Fetch failures and extraction failures are counted and reported; nothing is silently dropped.
- If the run reveals a pipeline BUG (not a threshold choice), the fix is applied, logged as a
  deviation, and both pre-fix and post-fix numbers are reported; thresholds themselves are
  immutable.
