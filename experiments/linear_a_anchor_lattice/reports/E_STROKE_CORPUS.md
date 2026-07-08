# E_STROKE_CORPUS — palaeographic stroke/orientation channel (E1–E2)

Seed 20260708. Non-circular: no phonetic value builds any feature. Signs are grouped only by
GORILA sign-name (a palaeographic identification) and allograph_family. Data:
`experiments/linear_a_anchor_lattice/data/stroke_corpus/`.

## E1 — Source + licence audit

SigLA (© Salgarella & Castellan, CC BY-NC-SA 4.0) is a *palaeographic* database, but the
local snapshot (`corpus/bronze/sigla_browse_2026/`) is the **browse/landing snapshot only**.
The client blob `database.js` ships exactly two OCaml-Marshal variables:

| var | content |
|-----|---------|
| `signs` | id / class / `gorila_number` / name / ref — **no geometry** |
| `data`  | per-document glyph list, each glyph = `{sign, is_divider, bbox=[x,y,w,h]}` |

- `grep` for `svg / <path / stroke / d= / polyline / bezier / png / data:image` in `database.js` → **0 hits**.
- The per-document facsimile drawings (`document/<designation>/<designation>.png`, into whose
  pixel space the bboxes index) were **deliberately not scraped** (PROVENANCE: "explicitly no
  bulk per-document scraping").
- **Conclusion:** the only geometry present is **axis-aligned bounding boxes**. No stroke
  polylines, no skeleton, no contour, no orientation angle, no glyph raster/vector. True-stroke
  evidence is **absent from the source we hold**, though it exists upstream (SigLA's drawings).

Corpus counts (measured): **802 documents, 4 756 named glyph-bbox instances, 340 distinct signs**;
113 signs with ≥5 instances, 89 with ≥10. Metadata channels present per document:
chronology (`period`, 778/802), geography (`site`, 8 sites), admin-function (`support`:
Tablet 452 / Nodule 166 / Roundel 146 / …).

Allograph families (`signs_ontology.json`): 156 families, **9 multi-member** (e.g. PA/PA3,
*309/*309B/*309C). All 9 use silver diplomatic tokens (PA, RA2, *309) that do **not** join to
SigLA's GORILA sign-names (AB81, A707) without the GORILA value map — and every multi-member
member has **0** SigLA bbox instances. The within-family shape-consistency calibration is
therefore **unrunnable** (0 usable pairs).

**Facsimile vs modern font:** we use only the facsimile-derived bbox metadata. No Unicode/Aegean
modern-font glyph is used as shape evidence anywhere (task constraint honoured).

## E2 — Two independent stroke representations

**(a) Rule-based bbox-geometry representation — BUILT** (`data/stroke_corpus/rep_a_bbox_geometry.json`).
Per sign: `aspect_mean/sd` (bbox `w/h`, the only **scale-invariant** sign-intrinsic observable),
`logrel_mean/sd` (bbox area ÷ within-document median area — a per-document-normalised size; note
**still scale-confounded** because pen/drawing scale differs across documents and no absolute mm
scale is recoverable from bbox alone). This is the "even bbox+aspect if strokes absent" fallback
the task authorises.

**(b) Learned skeleton/contour vector representation — SOURCE_BLOCKED.** A contour/skeleton
embedding needs a raster or vector glyph. None is in the snapshot. We refuse to substitute modern
font glyphs (they would encode a typographer's regularised idea of each sign, not the excavated
hand — that is exactly the circular shape-only channel LIN-08 forbids). The ingestion pipeline is
specified but not fed: `[fetch SigLA per-doc drawing] → [crop by bbox] → [binarise] →
[skeletonise / contour-trace] → [endpoint/junction/loop graph + Fourier-descriptor embedding]`.
Blocked at step 1 (drawings not held; re-fetch is an 802-document bulk scrape against a polite-access
+ CC BY-NC-SA source — out of scope for this task).

### Channel availability matrix

| sub-channel | available | basis |
|---|---|---|
| aspect_ratio | ✅ | bbox `w/h`, scale-invariant |
| relative_size | ✅ (confounded) | bbox area ÷ within-doc median |
| stroke_count | ❌ SOURCE_BLOCKED | needs tracing |
| endpoints/junctions | ❌ SOURCE_BLOCKED | needs skeleton |
| curves/loops | ❌ SOURCE_BLOCKED | needs contour |
| orientation | ❌ SOURCE_BLOCKED | bbox axis-aligned, no angle |
| contour_embedding (E2b) | ❌ SOURCE_BLOCKED | needs raster/vector glyph |

**Verdict:** the palaeographic shape channel reduces, in the data we hold, to a single
scale-invariant scalar (aspect ratio) plus a scale-confounded size. Every genuinely
*stroke/orientation* sub-channel is **SOURCE_BLOCKED**. See E_KNOWN_SCRIPT_CALIBRATION for what
that residual scalar can and cannot do.
