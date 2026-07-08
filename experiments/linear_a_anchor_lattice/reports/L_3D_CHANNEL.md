# WP-L — 3D / Seal-Imaging Channel Readiness

**Status: SOURCE_BLOCKED** (channel does not exist as licensed, downloadable, corpus-scale data;
a tested ingestion+validation pipeline is delivered so the channel can open the day data appears).

*Articles triggered: VII (search receipt — full audit trail in `data/3d_channel/source_audit.json`),
X/XV (licence gate — validator V5), XI/XII (non-circular: synthetic ground truth only; no Linear A
value enters the pipeline), XXII (this header). Assumptions: synthetic relief model (Gaussian-stroke
engraving, negative-relief impression + noise/pose/blur) is a *lower bound* on real matching
difficulty — a PASS here licenses the pipeline's plumbing, NOT a claim that real joins are this easy.
Seed 20260708 throughout.*

## 1. Availability + licensing audit (run 2026-07-08; live API counts, not estimates)

| Source | 3D content | Downloadable | Licence | Verdict |
|---|---|---|---|---|
| CMS via iDAI.objects Arachne (~12k seals/sealings) | 2D photos/drawings only; Heidelberg "3D-forensic" pilot unreleased | no bulk; hi-res behind free registration | no CC statement; DAI/CMS rights reserved | BLOCKED (3D absent; 2D redistribution unauthorized) |
| MUSINT II (Haghia Triada sealings + Florence/Rome seals; Sketchfab user `amjasink`) | **43 photogrammetry/laser models** (paged the API) | **0/43** (`isDownloadable=false`, licence `null` = all rights reserved) | none | LICENSE_BLOCKED — the closest thing to a real corpus, view-only |
| Sketchfab downloadable search | `minoan seal` → 2 hits (1 MUSINT-derived seal CC-BY 400k faces; 1 Phaistos-disc replica CC-BY); `linear a minoan` → 1 irrelevant jar | yes | CC-BY | NO_POWER (n=1 relevant mesh, zero ground-truth joins/allographs) |
| Zenodo API | `"Linear A" AND (photogrammetry OR 3D OR RTI)` → 2 (both Maltese stones, irrelevant); `"minoan seal" AND (3D OR scan)` → 0 | — | — | EMPTY |
| Heraklion Archaeological Museum "3D Exhibition" | browser viewer, selected exhibits | no download endpoint | Hellenic Ministry of Culture (permission regime, L.4858/2021) | LICENSE_BLOCKED |
| Anetaki plot (Kanta/Nakassis/Palaima/Perna, Ariadne Suppl. 5, 2024/25; ivory scepter 2024) | 2D publication photographs only | — | publisher copyright | SOURCE_BLOCKED (no 3D/RTI released; scepter unpublished in 3D) |
| Focus-stacked macro-photogrammetry workflow (J. Cultural Heritage 2022; 3 Linear A items, ~30 µm density) | method exists | paywalled paper, no dataset repo | — | SOURCE_BLOCKED |
| "Material Insights" (2025; structured-light scans of 98 CMS impressions + 27 originals) | scans exist | not released | — | SOURCE_BLOCKED — **best data-request target** |
| SigLA (in repo) | 2D sign bboxes only (802 docs/376 signs) | already held | CC BY-NC-SA | bbox-only; WP-E already showed aspect channel has no identity power (AUC 0.57–0.60) |

**Headline counts:** relevant downloadable meshes = **1**; MUSINT II models = 43, downloadable = **0**;
Zenodo relevant datasets = **0**; CMS bulk 3D = **0**. Known-join/allograph calibration needs ≥ tens of
ground-truthed meshes → the real-data leg is unbuildable today. **No fabrication; verdict fails closed.**

## 2. Delivered pipeline (`scripts/l_3d_pipeline.py`, tested)

- **Schema v1.0** (per-record): `record_id`, `corpus_ref` (GORILA/CMS/SigLA/museum_inv/SYNTHETIC),
  `object_class` (tablet/roundel/nodule/seal/sealing/libation_table/other), `modality`
  (mesh/rti/multiangle_photo/depthmap), `file` (path/format/sha256/bytes), `geometry` (units_mm,
  bbox_mm ∈ [1, 1000] mm, counts), `acquisition`, `provenance` (**licence allowlist +
  redistributable flag**), optional `ground_truth` (joins, allograph_group).
- **Validators V1–V6, fail CLOSED**: schema/enums; sha256+size; mesh/depthmap sanity (finite,
  non-degenerate, count match); unit plausibility; **licence gate** (analysis allowlist; NC licences
  can never be flagged redistributable); ground-truth referential integrity (no self-joins/dangling).
- **Calibration harness** (what real data would face): FFT normalized cross-correlation over 4 poses
  → seal↔impression join recovery scored against an exact non-pair permutation null; allograph
  grouping via within/between NCC AUC + 1-NN.

## 3. Synthetic round-trip results (REAL numbers, seed 20260708; `data/3d_channel/synthetic_roundtrip/`)

- **Ingest+validate clean manifest: 17/17 PASS** (8 seals, 6 joined + 2 distractor impressions, 1 OBJ mesh).
- **Corruption battery: 8/8 caught, each by its intended validator** — sha256 tamper (V2),
  metre-scaled bbox (V4), forbidden licence (V5), NC-redistribution overclaim (V5), self-join (V6),
  dangling join (V6), missing field (V1), NaN depth (V3).
- **Join recovery: 6/6** planted joins recovered by argmax **and** all 6 clear the null maximum
  (planted scores 0.949–0.983 vs null max 0.575, n_null=58, null mean 0.400; min margin **0.374**).
- **Allograph grouping: AUC 0.9997**, 1-NN accuracy 1.00 (20 items, 4 groups; within-NCC 0.852 vs
  between 0.414).
- Regression test `tests/test_l_3d_pipeline.py` re-runs the whole round-trip in a temp dir: **ALL PASS**.
- One honest fix during development: the initial synthetic records reported relief range (~0.7 mm) as
  bbox-z and correctly FAILED V4 — evidence the plausibility gate bites; records now report object
  thickness.

## 4. Unblock paths (ranked)

1. **Data request to the "Material Insights" team** (98 CMS impressions + 27 originals already scanned) — the only existing ground-truth-adjacent 3D corpus.
2. **CMS/Heidelberg + MUSINT II permission requests** (data exist; the block is purely licence/download).
3. **Anetaki**: any future 3D/RTI release (scepter) would be prospective held-out material (ties to WP-M).
4. New capture: the 2022 focus-stacking workflow is replicable at ~30 µm for small inscriptions — a museum-permission problem, not a technical one.

**Compliance line:** WP-L closes as `SOURCE_BLOCKED`; no claim above L0 is made; no licence state
changes; the pipeline PASS licenses ingestion machinery only, on synthetic ground truth.
