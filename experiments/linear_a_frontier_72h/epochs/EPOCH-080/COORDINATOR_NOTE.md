# EPOCH-080 — Coordinator resolution of a gate `passed:false` (null-definition, not a defect)

**Verdict banked:** `LINE_SPACING_REGULAR_CROSS_SITE` (unchanged from the worker's result.json).
**Gate mechanical outcome:** `passed:false`, `repairs:2`, sole problem
`NULL_MED_RECON_MISMATCH: result=0.3541 vs my_recon=0.658`.
**Coordinator decision:** BANK with a documented override — the gate failure was a limitation of the
epoch's `repro_check` (it hardcoded the naive *unconditional* null), NOT a defect in the worker's result.
Per Constitution / the campaign architecture, the gated runner deliberately does not adjudicate scientific
soundness — the null's validity is the coordinator's call. This note records the investigation (Art. XVII
append-only; this is a RESOLUTION, it does not alter the worker's result.json).

## What happened
The `repro_check` in `run_e080.py` reconstructed the random row-allocation null with a plain uniform-breakpoint
composition (`_rand_composition`), yielding null-median ≈ 0.658, and flagged the worker's reported null-median
0.354 as a mismatch (tolerance 0.12). The worker instead used a **clustering-conditional** null
(`_rand_composition_above`): random compositions are rejected unless every generated pitch exceeds the
row-clustering tolerance (0.6 × median glyph-height). Both are documented in the worker's `machinery.py`
docstring and in the result.json `deviations` field (a pre-data, justified NULL REFINEMENT).

## Why the worker's conditional null is the CORRECT one (independently reproduced)
The observed row pitches all exceed the clustering tolerance *by construction* — the y-band clustering that
recovers the rows merges any two rows closer than the tolerance. An unconditional null generates sub-tolerance
pitches that the same clustering would have merged (fewer rows), so it is **not exchangeable** with the observed
data and makes the observed look systematically "more regular" than random even when it is not. Coordinator
independently reproduced the exchangeability failure with a random-rows synthetic:

| null | corpus null-median (recon) | PC false-positive rate (recon) |
|------|---------------------------|-------------------------------|
| **conditional** (worker) | **0.368** (≈ worker 0.354) | **0.05** (≈ worker 0.08) — PASSES |
| unconditional (repro_check) | 0.659 (≈ repro 0.658) | **1.00** (worker warned ~0.72) — FAILS |

The unconditional null flags random-row synthetics as "regular" ~100% of the time → it is the WRONG null. The
conditional null restores exchangeability (false-positive ≤ 0.10) while preserving the prereg's intent (same row
count, same column span, destroys only the regularity of spacing).

## Why the verdict is robust regardless
Observed S_obs (median doc line-pitch-CV) = 0.118 (worker) / 0.111 (coordinator recon) is far below BOTH nulls
(0.354 conditional and 0.658 unconditional), so `perm_p = 0.0` either way. The null refinement changes only the
PC calibration and the reported effect ratio (0.33 conditional vs 0.17 unconditional — the conditional is the
MORE conservative, smaller-effect report). Cross-site: 3/3 testable sites significant under the conditional null
(HT 0.121 vs 0.363; Khania 0.118 vs 0.313; Zakros 0.108 vs 0.351; all perm p=0).

## Contrast with EPOCH-059
E059 was the mirror image: the worker's null was BUGGY (all sites drawn from one shared unigram), the coordinator
recomputed the correct per-site null, and the apparent positive was OVERTURNED to null (SUPERSEDING correction).
E080 is the opposite outcome from the same discipline: the worker's null is MORE correct than the coordinator's
first-pass `repro_check`, the coordinator independently confirmed it (conditional null reproduces + exchangeability
holds), and the positive STANDS. Both show the gate + independent-null-reconstruction rule working as intended —
it surfaces every null-definition disagreement for adjudication, in whichever direction the evidence falls.

## Lesson (process)
`repro_check` for a composition/permutation null must reconstruct the SAME exchangeability conditioning the worker
used (here: the clustering floor), not a naive unconditional version — otherwise it raises false mismatches on
legitimate, more-careful nulls. The worker's machinery docstring is the source of truth for the null definition;
read it before trusting a `repro_check` numeric flag.
