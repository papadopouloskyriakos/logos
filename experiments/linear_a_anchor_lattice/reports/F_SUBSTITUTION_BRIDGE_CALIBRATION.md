# F — Substitution-Axis Bridge: CALIBRATION (F1 + method controls)

**Campaign:** linear-a-anchor-lattice · **branch** `research/linear-a-anchor-lattice` · **seed** 20260708
**Articles:** V (claim layers), VII (search receipt), VIII (effective_n), IX (info budget),
XI/XII (non-circularity), XV (transfer licence). **Layer of any claim here: L2/L3 relative only.**

**Non-circular contract.** Every substitution-neighborhood graph is built from sign IDENTITY,
co-occurrence and minimal-frame membership ONLY. Known LB / Cypriot / GORILA values are read
*afterward* to GRADE (ground truth + relative-class labels), never as a model input. The bridge
methods (F2) operate on OPAQUE per-script node IDs so the shared transcription label cannot leak
into the geometry. **A relative-class reduction earns no absolute value (Art. XV).**

Scripts: `f1_opaque_lb_calibration.py`, `f2_cross_script_bridge.py` (CTRL/KNOWN legs), `f_bridge_common.py`.
Data: `data/substitution_bridge/F1_opaque_lb_calibration.json`, `…/F2_cross_script_bridge.json`.

---

## F1 — Opaque-LB relative-class recovery under frequency- AND formula-disjoint holdouts

**Question.** With LB values blind, do substitution neighborhoods recover the
same-consonant / same-vowel / spelling-variant / morphophonological (word-final same-consonant)
equivalence classes under the two holdouts that killed the position channel?

Corpus: DĀMOS Linear B, 13,562 wordform tokens; 72 scorable syllabogram signs; graded sign-pairs
= {same_consonant 121, same_vowel 497, spelling_variant 9, cross 1929}. Two independent
neighborhood implementations (frequency-robust cofill-**Jaccard**; adjacency **cosine**).

| Test | same_C AUC | same_V AUC | axis = consonant? |
|---|---|---|---|
| Full corpus — Jaccard | **0.700** | 0.570 | yes |
| Full corpus — cosine (indep. impl.) | **0.738** | 0.645 | yes |
| Morphophono (word-final frames only) — Jaccard | **0.696** | — | yes |
| **(a) Frequency-DISJOINT** (within-band pairs only) — Jaccard | **0.750** | 0.612 | yes |
| **(b) Formula-DISJOINT** leave-one-series-out — Jaccard (min / median over 6 folds) | **0.683 / 0.693** | — | **all 6 folds yes** |

Permutation null (shuffle value labels among signs, 300×): observed same_C AUC 0.700 vs
null mean 0.499, null-p95 0.543 → **p = 0.0033**.

**Verdict F1: `OPAQUE_LB_CONSONANT_AXIS_RECOVERED_UNDER_HOLDOUTS`.** ≥2 independent
implementations agree the axis is consonant; the frequency-disjoint split (the exact test that
collapsed the position channel to chance ≈0.48) *strengthens* to 0.75; every leave-one-series-out
fold keeps the consonant axis; label-shuffle p = 0.003. This re-earns, under stricter holdouts,
the C_AUDIT precondition (this reproduces C_AUDIT's cofill-Jaccard same_C 0.703 within rounding).
The substitution channel carries a **real, value-free, relative (vowel-alternation) axis** in LB.

---

## Method controls — can the four bridge methods recover a KNOWN alignment?

Before applying the cross-script bridge to Linear A we calibrate the four alignment methods on
alignments whose answer is known. Similarity = cofill-Jaccard; min support 3 word-types/script;
target-side node order shuffled so an index can never leak the answer; permutation null shuffles
the ground-truth partner labels (1000×); **Holm correction across all 4 methods × 3 metrics = 12
tests per pair** (Art. VIII multiplicity).

Methods: **M1** NN-transfer (anchor-seeded, leave-one-out); **M2** structural-signature Hungarian
(unsupervised); **M3** Gromov–Wasserstein optimal transport (unsupervised, label-free); **M4**
Laplacian-eigenmap + Procrustes (anchor-seeded, LOO).

### CTRL — LB-DĀMOS split-half (identity ground truth; upper bound, n = 71)

| Method | exact | cons-class | vowel-class | exact survives Holm? |
|---|---|---|---|---|
| M1 NN-transfer (70 anchors) | **0.408** | 0.423 | 0.535 | **yes** |
| M3 Gromov–Wasserstein | 0.085 | 0.099 | 0.296 | **yes** |
| M4 spectral+Procrustes | 0.085 | 0.183 | 0.324 | **yes** |
| M2 structural-signature | 0.056 | 0.127 | 0.296 | no (nominal p 0.016) |

**The methods work.** On a same-script identity alignment with known values, the unsupervised
label-free methods (M3/M4) recover the correspondence above the permutation floor and survive
multiplicity; the heavily-seeded M1 reaches 41% exact. Note even the *upper bound* for
fully-unsupervised recovery is low (≈8–9% exact); the most recoverable relative axis is the
**vowel class** (≈0.30–0.53), consistent with F1's vowel-alternation finding.

### KNOWN — LB-cog ↔ Cypriot-cog (genuine cross-script; same syllabic value = counterpart, n = 47)

Two *deciphered* Greek syllabaries, lexical type-lists (LB 919 / Cypriot 693 words).

| Method | exact | cons-class | vowel-class | best nominal p | survives Holm? |
|---|---|---|---|---|---|
| M1 NN-transfer | 0.064 | 0.128 | 0.277 | exact 0.050 / vowel 0.041 | **no** |
| M3 Gromov–Wasserstein | 0.021 | 0.128 | 0.234 | 0.23 | no |
| M4 spectral+Procrustes | 0.043 | 0.064 | 0.170 | 0.27 | no |
| M2 structural-signature | 0.000 | 0.085 | 0.213 | 0.52 | no |

Register-mismatched variant (LB-DĀMOS ↔ Cypriot-cog, n = 48): **all methods at chance.**

**Key calibration result.** Even between two *known, related* (both Greek) syllabaries, the
cross-script substitution-neighborhood bridge sits at the **chance floor after multiplicity**.
The only nominal positives (M1 exact p = 0.05, vowel p = 0.04) do not survive Holm. This is a
**power** ceiling, not a bug — the same methods clear the CTRL identity control; the difference is
corpus size (≈700–900 word-types ⇒ sparse substitution graphs) and genuinely distinct
orthographic systems. The channel cannot carry a real cross-script correspondence at Linear-A
scale. This bounds the Linear A application before it is run (see the bridge report).

**effective_n / info budget.** ~47–71 alignable signs; substitution graphs built from ≤~900 (cog)
to 13.6k (DĀMOS) word-types; the cross-script coupling has ≤ log₂(47) ≈ 5.6 bits of addressable
identity per sign and the known-pair experiment shows the neighborhood channel supplies far less
than that at these scales.
