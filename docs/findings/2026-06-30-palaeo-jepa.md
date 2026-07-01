# Finding 2026-06-30 — sign-image palaeography: cross-script IMAGE alignment is a font-robust but CIRCULAR engineering demonstration (NOT an archaeological positive); classical beats I-JEPA

> **UPDATE 2026-07-01 (pre-submission review fix P2).** The original headline called this the
> "first non-null offensive signal." That is **withdrawn.** Two things changed after review:
> (1) the claim on line 4 that one-font rendering makes "distances reflect glyph shape, not font"
> was an *un-controlled assertion*; it is now **tested** by a font-swap control
> (`scripts/palaeo/font_control.py`, artifact `results/palaeo/font_control.json`) which **refutes
> the font-artifact worry** — the alignment survives, even strengthens, when Linear A and Linear B
> are drawn by two *independent* type designers (Noto Sans Linear A / Noto Sans Linear B). (2) But
> the deeper **graphic-genealogy circularity** — the A↔B anchor *values* were assigned by modern
> epigraphers largely **on the basis of sign-shape similarity**, and Linear B descends graphically
> from Linear A — is **not** controllable and makes this an *engineering demonstration*, not
> independent archaeological confirmation. Relabelled accordingly throughout; I-JEPA is kept **out
> of the main claims** (over-parameterized for the information available; see below).

`scripts/palaeo/` (render_signs, jepa, classical, validate, run_palaeo, **font_control**). 88
Linear-A + 74 Linear-B glyph PNGs. The baseline renders both scripts in ONE face (Aegean); whether
that face's house-style drives the alignment is **no longer asserted but measured** — see
§ *Font-swap control* below. **A real I-JEPA was built** (CPU torch 2.12.1; latent-target
prediction + EMA target encoder + stop-grad + non-contrastive MSE — verified genuine Assran-2023
I-JEPA, not a contrastive Siamese), alongside a classical comparator (HOG + Hu moments +
shape-context → PCA-48). Independently re-verified (classical deterministic re-run reproduces
exactly). **I-JEPA is reported only as a comparator and is excluded from the main claims.**

## Headline (c) — cross-script IMAGE A↔B alignment (held-out shared-sign recovery, same anti-circular protocol as Track B)

| representation | direct-NN | Procrustes | vs image chance (0.0135) | vs Track-B seq null (0.0205) |
|---|---|---|---|---|
| **classical** | **0.410** [0.18,0.64] | **0.185** [0.00,0.36] | ~30× | **9.0×** |
| I-JEPA (2 seeds) | 0.322 ±0.018 | 0.119 ±0.021 | ~24× / ~9× | ~6× / ~6× |

**Image alignment recovers held-out shared anchors far above chance AND far above Track B's
sequence null** (which was at chance). Borrowed signs ARE visually similar, so image embeddings
succeed where sequence co-occurrence completely failed. **But this is *expected and largely
circular*, not an offensive signal** (see § *Why this is a demonstration, not a positive* below):
the anchor A↔B *values* were themselves assigned by epigraphers on the basis of sign shape, so an
image encoder recovering that value map re-derives a correspondence that was *defined* by shape.

## Font-swap control (added 2026-07-01, review fix P2) — the font-artifact worry is REFUTED

A reviewer flagged that rendering both scripts in ONE typeface (Aegean, George Douros) could make
the alignment a single-designer **house-style artifact** rather than a fact about the ancient
signs. `scripts/palaeo/font_control.py` tests this directly: re-render Linear A in **Noto Sans
Linear A** and Linear B in **Noto Sans Linear B** — two *independent* type designers, each covering
only its own Unicode block (verified: NotoA has 0 Linear B glyphs, NotoB has 0 Linear A glyphs), so
no single hand touches both scripts.

| condition (n_anchor=55, B-pool=74, chance 0.0135) | direct-NN | Procrustes |
|---|---|---|
| Aegean baseline (one face draws both) | 0.367 [0.348, 0.386] | 0.156 [0.142, 0.171] |
| **Noto cross-font (two independent designers)** | **0.416** [0.397, 0.435] | **0.195** [0.181, 0.210] |

The alignment **survives and is if anything stronger** under the cross-font swap (retains ~113% of
the Aegean direct-NN, both conditions ≫ chance). **Verdict: FONT CONFOUND REFUTED** — the
cross-script recovery is *not* a typeface-style artifact. (Artifact: `results/palaeo/font_control.json`.
Numbers here are the control's own reconstructed anchor/pool set — direct-NN 0.367 baseline — very
close to the headline probe's 0.410 on the rendered corpus.)

## Why this is a demonstration, not a positive — graphic-genealogy circularity (uncontrolled)

The font control kills the typeface artifact but **cannot touch the deeper confound**, which is why
the result is relabelled a *shape-genealogy engineering demonstration*: **Linear B was historically
adapted from Linear A**, and the A↔B transcription *values* that define the anchor set were assigned
by 20th-century epigraphers **largely on the basis of sign-shape similarity**. So "a shape encoder
recovers the A→B value map" is close to tautological — it re-derives a mapping that was *defined* by
shape — and is **not** independent confirmation of a phonetic reading. It also inherits modern
editorial glyph normalization. Under invariant 5 (truth-layer cap) a shape match is a ≤0.75 signal,
never a reading. **This leg is therefore excluded from the offensive decipherment claims.**

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

## Significance (revised 2026-07-01)

**Not an offensive leg.** Combined with Track B's sequence null, the honest picture is: image
embeddings recover the A↔B *value* map far above chance, but that map was itself *defined by sign
shape*, so the recovery is largely circular and cannot be independent evidence for any reading. The
font-swap control adds one genuinely new fact — the recovery is **not** a typeface artifact — but
does not remove the circularity. What survives as a *usable* result: (1) a validated, font-robust
palaeographic **descriptor pipeline** (classical HOG+Hu+shape-context) that could support intra-script
allograph work and damaged-sign recognition, where there is no value-circularity; (2) a documented
hard-negative (`CH095 ~ AB60`) for calibrating any future shape-based bet. The **A-only signs (e.g.
`*301`) have no cross-script anchor at all**, so images cannot even in principle impute them. The
offensive cross-script bet remains **null/data-blocked**, not open.
