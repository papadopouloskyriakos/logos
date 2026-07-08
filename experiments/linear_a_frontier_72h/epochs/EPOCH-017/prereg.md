# EPOCH-017 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F6** (gates A/B) — photograph / second-rendering
allograph de-confound.
**Epoch question:** E012 found doc→site allograph structure (LEG1_FIRE, LEG2_FIRE) but it is
CONFOUNDED: a pure rendering-nuisance embedding beats it (nuisance_bal 0.3307 > allograph_bal
0.2797, G3 fails). Is the per-sign within<cross-site spread REAL ancient allograph variation, or a
single-tracer (SigLA) rendering artifact? This epoch runs the strongest rendering-independent
de-confound actually obtainable and reaches a mechanical verdict.
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Claim layer:** L1 ONLY (sign-form geometry). No L2+ claim can emerge; no phonetic values anywhere;
no transfer licence touched (Art. XV).
**Articles triggered:** V (L1 cap), VII (search receipt — every test/threshold enumerated here,
nothing chosen post hoc), VIII (effective_n = documents, never instances), IX (a partition-restricted
site classifier is palaeographic metadata, not a reading), XI/XII (non-circularity: site labels are
SigLA designations, independent of the E009 stroke extractor; the feature PARTITION below is defined
from the geometric semantics of the E009 extractor — count-topology vs continuous-shape — fixed BEFORE
looking at any site result, and is in fact the SAME partition (`COUNT_IDX`/`ORIENT_IDX`) already
present, unused for this purpose, in `scripts/epoch009_stroke_corpus.py` lines 26-27, written 2026-07-08
before this epoch existed), XVII (append-only; deviations in result.json), XVIII (assumptions below),
XXII (this header).

## STEP 0 — source audit (run + freeze BEFORE any test; descriptive, not gated)

1. **Photographs.** Checked in-repo (`corpus/bronze/sigla_browse_2026/*.html`, `PROVENANCE.md`) and
   live (`sigla.phis.me/about.html`, `sigla.phis.me/document/ARKH%207/`, one polite fetch each, no
   bulk scraping — consistent with the repo's existing single-pass acquisition policy). Result: SigLA
   ships only vector line-drawings/traces (`about.html`: "Dataset and drawings are available under
   CC BY-NC-SA 4.0"; document pages: "Link to tablet drawing", image files are `.png` vector traces,
   no photo/drawing toggle, no photograph referenced anywhere). **Photographs are NOT obtainable at
   sigla.phis.me.** No photograph corpus exists elsewhere in-repo (`corpus/bronze/` has no tablet
   photo directory). → **Channel (B) PHOTOGRAPH re-extraction is SOURCE_BLOCKED, evidenced.**
2. **Second independent rendering.** Searched `corpus/bronze/` for a second hand-copy/rendering
   source (GORILA plates, GesA, published facsimiles as images): none found (`corpus/bronze/sign_images`
   is a single MODERN FONT — Aegean/UFAS — glyph render per idealized sign VALUE, not per-instance,
   not an independent scholarly hand-copy of specific inscriptions; `corpus/bronze/younger_lineara` is
   text-only). SigLA's own stated basis is GORILA (Godart & Olivier) but only as a textual/attestation
   source, not as a shipped second image set. → **Channel (A) SECOND-RENDERING replication is
   SOURCE_BLOCKED, evidenced.**
3. **Scribal-hand attribution (for the negative/adversarial control).** Searched `corpus/silver/`,
   `corpus/bronze/palaeo/`, `corpus/bronze/sigla_browse_2026/`, `corpus/bronze/younger_lineara/` for
   any GORILA/SigLA same-hand or scribe attribution: none found. → **The same-scribe-across-sites
   negative control is SOURCE_BLOCKED, evidenced; substituted by a rendering-shuffle null (below),
   which needs no attribution data and directly tests the mechanism this epoch cares about.**
4. Given 1–3, this epoch runs **only channel (C) FEATURE-PARTITION**, as instructed for the case where
   no pixel source is obtainable. This is not a stall: it is the pre-registered fallback, run in full
   with its own positive control and adversarial nulls.

## Feature partition (frozen; defined from the E009 extractor's own geometric semantics, not fit to
## any site result)

E009's 10-dim stroke feature vector (`feat_vec`, `scripts/epoch008_stroke_pilot.py:154-157`) is, in
order: `[n_endpoints, n_junctions, n_loops, n_components, n_strokes, skel_len_norm, orient_0..3]`.
- **RENDERING-INVARIANT partition `INV` = indices [0,1,2,3,4]** (`n_endpoints, n_junctions, n_loops,
  n_components, n_strokes`): integer counts of the skeleton's critical-point graph (topology:
  endpoints/junctions/loops/components/condensed-edges). These are combinatorial descriptors of the
  stroke graph's connectivity — insensitive to sub-pixel choices (curve smoothing, bezier resolution,
  anti-aliasing threshold, stroke width) that a single tracer's vector pipeline makes, because
  skeletonization first collapses width and Otsu-binarization first collapses anti-aliasing before
  these counts are taken. This is EXACTLY `COUNT_IDX = [0,1,2,3,4]` already defined in
  `scripts/epoch009_stroke_corpus.py:26`, used there (before EPOCH-017 existed) to split a topology
  channel from an orientation channel in the LB-font similarity matrix — not invented post hoc for
  this epoch.
- **RENDERING-SENSITIVE partition `SEN` = indices [5,6,7,8,9]** (`skel_len_norm, orient_0..3`):
  continuous shape descriptors — normalized skeleton path length (sensitive to curve jaggedness/
  smoothing introduced by vectorization) and the 4-bin stroke-orientation histogram (sensitive to a
  tracer's habitual digitization angles and bezier-curve rendering). This is `ORIENT_IDX = [6,7,8,9]`
  (`scripts/epoch009_stroke_corpus.py:27`) plus `skel_len_norm` (index 5), grouped with it because
  both are continuous geometric measurements of curve shape rather than discrete topology counts.
- `aspect` (bbox log-aspect ratio) stays OUT of both partitions, as in E009/E012 (kept as a separate
  adversary channel throughout).

## Positive control (run FIRST; fail ⇒ STOP; fully synthetic, known ground truth)

Reuse the REAL doc/site/sign assignment structure of E012's F-SIGN robust instances (so the pairing
and permutation machinery is realistic) but replace the 10-dim feature values with **synthetic**
draws: baseline `z ~ N(0, I_10)` per instance, then, per scenario:
- **S1 (real site signal only):** add a per-site random offset vector, confined to `INV` indices,
  scaled to Cohen's-d ≈ 1.2 per dim (calibrated to E012's observed leg-1 `D_std` range 0.3–0.5, scaled
  up 2-3x so the PC is a clean, unambiguous separation — not a replica of the borderline real effect).
  `SEN` indices get pure noise (no site signal).
- **S2 (rendering nuisance only, site-correlated — mirrors the real confound):** add a per-site random
  offset vector of the SAME magnitude, confined to `SEN` indices only. `INV` indices get pure noise.
  (This models the real-world mechanism: documents from one site are typically traced together, so a
  tracer-session nuisance is site-correlated by construction — exactly what E012's G3 found.)
- **S3 (mixed, realistic):** both S1's `INV` site signal and S2's `SEN` nuisance simultaneously.
Run E012's exact leg-1 statistic (per-sign within<cross-site mean-distance gap / σ, doc-level
permutation, 2,000 draws, same seed) restricted to `INV`-only distance and, separately, `SEN`-only
distance, for each scenario.
**PC_PASS :=** in S1, `INV`-restricted test fires (p<0.01) and `SEN`-restricted does not (p≥0.05); in
S2, `SEN`-restricted fires and `INV`-restricted does not; in S3, `INV`-restricted still fires (true
signal recovered despite co-occurring nuisance) and `SEN`-restricted also fires (nuisance correctly
flagged, not laundered away). All three sub-conditions required. PC fail ⇒ verdict
`DECONFOUND_PC_FAIL`, stop — the partition method itself would not be trusted to answer the real
question.

## Main analysis — E012's confirmatory legs, restricted to each partition (confirmatory)

On the REAL `data/stroke_corpus/features/instances.json` corpus (identical frame definitions as E012:
F-SIGN 60 signs, F-DOC ≈258 docs / 5 sites, same z-space, same doc-level exclusion of same-doc pairs,
same permutation nulls N1/N2a/N2b, same Holm-05 localization) — rerun, unchanged in every other
respect:
- **Leg 1' (INV):** leg-1 statistic using ONLY `INV` distance (Euclidean over indices [0,1,2,3,4]).
- **Leg 1' (SEN):** leg-1 statistic using ONLY `SEN` distance (indices [5,6,7,8,9]).
- **Leg 2' (INV):** leg-2 doc-embedding balanced accuracy using ONLY `INV` deviation dims.
- **Leg 2' (SEN):** leg-2 doc-embedding balanced accuracy using ONLY `SEN` deviation dims.
Same fire thresholds as E012 (Holm over the 4-test family {p1_INV, p1_SEN, p2_INV, p2_SEN}; FIRE :=
Holm-adjusted p < 0.01, and for leg2 also balanced_acc > p95(N2b) recomputed for that partition).
Nuisance comparator (E012's `[global_ink, density, mode, n_inst, ink_fraction, aspect]` embedding) is
recomputed once and compared against BOTH partitions' leg-2 balanced accuracy (G3-style).

## Negative / adversarial controls

- **Rendering-shuffle null (replaces the SOURCE_BLOCKED same-scribe control; needs no new source):**
  shuffle `SEN`-partition feature values across ALL ok instances (breaking any true doc/site/tracer
  correspondence for those 5 dims only, `INV` dims and labels untouched), then rerun leg-1' (SEN) and
  leg-2' (SEN). **Must collapse to null (p≥0.05, Holm)** — this both (a) sanity-checks the test
  apparatus isn't trivially significant regardless of data, and (b) is the closest obtainable proxy to
  "destroy tracer-session structure, verify the signal it carried disappears."
- **Same-scribe-across-sites:** SOURCE_BLOCKED (STEP 0.3) — recorded, not run.

## Mechanical verdict (frozen; PC fail overrides all → `DECONFOUND_PC_FAIL`)

Let `FIRE_INV := (leg1'_INV FIRE) ∨ (leg2'_INV FIRE ∧ leg2'_INV bal_acc > nuisance_bal_acc)`.
Let `FIRE_SEN := (leg1'_SEN FIRE) ∨ (leg2'_SEN FIRE ∧ leg2'_SEN bal_acc > nuisance_bal_acc)`.
- **SITE_ALLOGRAPH_REAL** := `FIRE_INV` ∧ rendering-shuffle null on SEN collapses (as required,
  independent of FIRE_SEN). Site-coherent structure lives in topology counts a single tracer's
  vectorization choices should not be able to manufacture.
- **TRACER_ARTIFACT** := ¬`FIRE_INV` ∧ `FIRE_SEN`. Site-coherent structure lives ONLY in the
  continuous curve/orientation features a vectorization pipeline can manufacture; topology carries no
  site signal once nuisance-prone dims are removed.
- **MIXED_PARTITION** := `FIRE_INV` ∧ `FIRE_SEN` but the rendering-shuffle null does NOT collapse SEN
  (apparatus concern) — reported with the caveat, both leg families given verbatim.
- **NULL_UNDER_PARTITION** := ¬`FIRE_INV` ∧ ¬`FIRE_SEN` — E012's confound could not be resolved either
  way at this power; the original CONFOUNDED verdict stands, un-upgraded.
- Multiplicity: confirmatory family = {p1_INV, p1_SEN, p2_INV, p2_SEN}, Holm, exactly as E012 pooled
  {p1,p2}.

## Honest-accounting commitments

- A `SITE_ALLOGRAPH_REAL` verdict is STILL L1 palaeographic, STILL bounded by "one trace per document"
  (tracer-vs-scribe inseparable at the document level, per E012) — this epoch only removes the
  SPECIFIC rendering-style confound G3 caught (continuous curve/orientation nuisance); it does not
  and cannot certify photograph-level truth, because no photograph channel is obtainable (STEP 0).
  This sentence appears verbatim in the report regardless of verdict.
- If `FIRE_INV` with the topology partition (5 of 10 original dims, weaker channel), the correct
  reading is "downgrades E012's confound but doesn't fully vindicate it" — NOT "decisively proves
  ancient allograph variation." Layer stays L1; no transfer licence is touched either way.
- effective_n throughout = documents (Art. VIII), matching E012.
- Nothing dropped silently: every frame's realized n reported in result.json.
