# E_LINEAR_A_CORRESPONDENCES — ranked correspondences, channels decomposed (E4)

Seed 20260708. Full table: `data/stroke_corpus/E4_ranked_correspondences.json` (top 60).

## What this is — and what it is NOT

This ranks Linear-A **sign pairs by bbox-geometry proximity** and decomposes each pair across the
channels the task asks for. It is published as a **floor artifact only**. Per E3, the shape channel
has no sign-identity power (within-LA AUC 0.57–0.60), so a small shape distance here is **not**
evidence that two signs correspond. Shape-only value transfer is the LIN-08 forbidden route
(CIRCULAR, capped ≤0.75, DO_NOT_REPEAT). Nothing below earns a licence.

## Channel decomposition

For each ranked pair we report, per the task's requested axes:

- **shape** — z-scored [aspect, log relsize] centroid distance (WEAK; generic-visual only).
- **stroke / orientation** — **SOURCE_BLOCKED** for every pair (no tracings, no angle).
- **chronology** — Jaccard-style overlap of the two signs' document `period` distributions.
- **geography** — overlap of document `site` distributions.
- **admin-function** — overlap of document `support` (Tablet/Nodule/Roundel) distributions.

Chronology/geography/function are **contextual co-occurrence** channels (they say two signs appear
in similar documents), not shape channels; they cannot on their own assert a *sign* correspondence
either, and are reported to keep the decomposition honest and to flag confounds (two signs sharing
Haghia-Triada LM IB tablets will co-vary on all three regardless of shape).

## Sample (top of the ranked list — floor only)

| a | b | shape dist (z) | site ov | period ov | support ov |
|---|---|---|---|---|---|
| A301 | A606 | 0.005 | 0.137 | 0.208 | 0.000 |
| A312 | AB61 | 0.019 | 0.259 | 0.308 | 0.308 |
| AB51 | A303 | 0.022 | 0.222 | 0.704 | 0.704 |
| A610 | A622 | 0.026 | 0.783 | 0.864 | 0.864 |
| AB02 | A705 | 0.026 | 0.168 | 0.181 | 0.168 |

The near-zero shape distances are an artifact of a 1-D-ish feature (many signs share aspect ≈ 0.8);
they carry no identity content. Pairs that also share high chronology/geography/function overlap
(e.g. A610/A622) are co-located administrative signs, a context confound — **not** a shape descent
claim.

## Verdict

No LA↔LA or LA↔(readable script) sign correspondence is asserted. The shape channel is a floor with
no discriminative power; the stroke/orientation legs and the entire cross-script calibration are
SOURCE_BLOCKED. This table exists so a future run — once true SigLA drawings are ingested and E2(b)
skeleton/contour embeddings replace the bbox scalar — has a decomposed baseline to beat. Until then:
**no correspondence, no licence, no value transfer.**
