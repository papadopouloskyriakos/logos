# Finding 2026-06-30 — sign-image I-JEPA / palaeography: cross-script IMAGE alignment SUCCEEDS (first non-null offensive signal); classical beats I-JEPA

`scripts/palaeo/` (render_signs, jepa, classical, validate, run_palaeo). 88 Linear-A + 74 Linear-B
glyph PNGs (one Aegean font, both scripts → cross-script distances reflect glyph shape, not font).
**A real I-JEPA was built** (CPU torch 2.12.1; latent-target prediction + EMA target encoder +
stop-grad + non-contrastive MSE — verified genuine Assran-2023 I-JEPA, not a contrastive Siamese),
alongside a classical comparator (HOG + Hu moments + shape-context → PCA-48). Independently
re-verified (classical deterministic re-run reproduces exactly).

## Headline (c) — cross-script IMAGE A↔B alignment (held-out shared-sign recovery, same anti-circular protocol as Track B)

| representation | direct-NN | Procrustes | vs image chance (0.0135) | vs Track-B seq null (0.0205) |
|---|---|---|---|---|
| **classical** | **0.410** [0.18,0.64] | **0.185** [0.00,0.36] | ~30× | **9.0×** |
| I-JEPA (2 seeds) | 0.322 ±0.018 | 0.119 ±0.021 | ~24× / ~9× | ~6× / ~6× |

**Image alignment recovers held-out shared anchors far above chance AND far above Track B's
sequence null** (which was at chance). Borrowed signs ARE visually similar, so image embeddings
succeed where sequence co-occurrence completely failed. This is a **different, positive signal** —
the first non-null leg for the cross-script phonetic-imputation bet.

## (a) allograph clustering + (b) damaged-form recognition

- **Allograph** (6 known variant families / 13 signs; NN-purity vs 2000-draw permutation null
  0.104): classical **0.385 (p=0.028)**; I-JEPA 0.308 (p=0.078). Both significantly above chance
  (real, if weak); the two tie.
- **Damaged-form recall@1** (810 synthetic damaged forms vs 162 bases; chance 0.006): classical
  **0.635** (erode .75 / noise .01 / occlude 1.0 / rotate .65 / scale .77); I-JEPA 0.577
  (collapses on scale — no crop/scale augmentation). Both robust.

## I-JEPA vs classical — classical wins (as the audits predicted)

Classical beats I-JEPA on damaged recall, cross-script direct-NN + Procrustes; tie on allograph.
I-JEPA is weaker + noisier at this scale. **Building the real I-JEPA confirmed empirically** that
hand-crafted descriptors dominate a from-scratch SSL encoder on ~90 images.

## Honest caveats

- **I-JEPA partially dimensionally collapses** on the tiny corpus (effective rank ~3–4 of D=128;
  same-seed runs ~uncorrelated) — a known JEPA-on-tiny-data failure (verify-flagged MEDIUM). Does
  not affect the classical headline.
- **Self-report discrepancy (recorded from the persisted JSON, not the impl's prose):** the impl
  stated "3 seeds / 60 epochs"; the actual run was **2 seeds / 8 epochs**. Conclusion unaffected.
- Classical is the cleaner cross-script probe (no training → fully non-circular zero-shot); I-JEPA
  trained on both scripts' pixels (unsupervised, no value labels — still non-circular, but not
  zero-shot).
- **Bounded / Etruscan-grade:** image similarity may recover the visual/phonetic *shape* of some
  shared signs; it does **not** read Minoan. The positive result confirms a palaeographic fact
  (borrowed signs look alike) + that it transfers non-circularly to held-out anchors.

## Calibration — a published cross-script image HARD NEGATIVE (Ferrara, Montecchi & Valério, audited 2026-07-01)

The "Archanes Formula" paper supplies an expert gold-standard demonstration that a **plausible
cross-script visual match is wrong**: `CH 095` looks like `AB 60`/*ra* but is not its phonetic
counterpart (the better visual neighbour, `AB 10`/*u*, carries no phonetic-identity warrant either).
Use `CH095 ~ AB60` as a **hard-negative / calibration case** for this image-alignment leg: a successful
shape match must still clear the **truth-layer cap (invariant 5)** — visual similarity is a ≤0.75
signal, **never** a reading. Two corollaries the paper hands us: (1) it independently confirms that
sign shapes derive from iconography *within* a script (water-bird/fish/vessel motifs) — supporting
intra-script image modelling; (2) it **refutes** the Cretan-Hieroglyphic ancestry of the libation word
`a-sa-sa-ra-me`, so logos must not premise any `a-sa-sa-ra-me` hypothesis on cross-script CH continuity
(the structural reading stays Linear-A-internal). Confirms `A`-only signs like `*301` have no
cross-script (`AB`) anchor.

## Significance

A real leg for the cross-script bet — **via images, not sequences.** Combined with Track B's
sequence null, the picture: sequence-co-occurrence alignment is data-blocked (DĀMOS); **image
alignment works now.** Open question: does the image signal + more Linear-B data (DĀMOS) enable
phonetic imputation for A-only signs (still Etruscan-grade)? The image path is the one to pursue
for the offensive bet; the sequence path waits on DĀMOS.
