# F — CROSS-SCRIPT Substitution-Axis Bridge: Linear A ↔ Linear B (F2 real + F3 + F4)

**Campaign:** linear-a-anchor-lattice · **seed** 20260708 · **Articles:** V, VII, VIII, XI, XII, XV.
Read the calibration first: [`F_SUBSTITUTION_BRIDGE_CALIBRATION.md`](./F_SUBSTITUTION_BRIDGE_CALIBRATION.md).
Scripts: `f2_cross_script_bridge.py`, `f4_la_relative_output.py`, `f_bridge_common.py`.
Data: `data/substitution_bridge/{F2_cross_script_bridge.json, F2_real_LA_LB_coupling.json, F4_la_relative_constraints.json}`.

**Genuinely-untried lever (per FROZEN context).** Not raw A↔B distributional transfer (LIN-08,
NULL×4) and not shape-only value transfer (circular). Instead: use the **substitution
NEIGHBORHOOD geometry** — validated as a real value-free relative axis in LB (F1) — and test
whether that geometry *aligns across scripts* well enough to transfer RELATIVE phonological
constraints, without importing a single absolute LB value.

**Non-circular contract.** Each script's neighborhood graph is built from its own sign identity /
minimal-frame membership. Alignment runs on OPAQUE node IDs (LA_/LB_). The AB shape-homomorphic
label and known values are used ONLY to build ground truth and to grade — never as a model input.

---

## F2 (real) — LA-silver ↔ LB-DĀMOS, proposed correspondences = AB shape-homomorphs

Ground-truth "proposed A↔B correspondences" = the 51 syllabogram-**AB** signs present with support
≥3 in both the LA silver corpus (3,147 word-tokens) and LB DĀMOS. These are Salgarella-style
*shape/tradition* homomorphs; their LA phonetic value is **not** confirmed — the bridge tests
whether the neighborhood geometry independently supports mapping each LA AB-sign to its
homomorphic LB counterpart. Permutation null shuffles the true partner (1000×); **Holm across
12 tests/pair.**

| Method | exact | cons-class | vowel-class | best nominal p | survives Holm (any)? |
|---|---|---|---|---|---|
| M1 NN-transfer (50 homomorph anchors, LOO) | 0.078 | 0.137 | 0.294 | exact **0.014** | **no** |
| M2 structural-signature (unsupervised) | 0.059 | 0.098 | 0.353 | vowel **0.023** | **no** |
| M3 Gromov–Wasserstein (unsupervised) | 0.000 | 0.118 | 0.294 | 0.12 | no |
| M4 spectral+Procrustes (LOO) | 0.000 | 0.098 | 0.157 | 0.38 | no |

**Zero exact survivors after Holm; zero survivors of any kind after Holm.** The two nominal
positives (M1 exact p 0.014 — the homomorphy map is weakly self-consistent under neighborhood
transfer, 4/51; M2 vowel-class p 0.023) do not survive multiplicity. The purest label-free
methods (M3 GW, M4 spectral) are at/below chance: the GW coupling is **near-uniform** (per-row max
0.0217 vs uniform 0.0196; coefficient of variation 5%) — the optimal transport finds essentially
no structure to lock onto for LA↔LB, whereas the *same* GW recovered the CTRL identity alignment
above null. The recurring (but non-surviving) residual is the **vowel axis** (≈0.29–0.35), the
same axis F1 isolates in LB.

### Verdict F2: `CROSS_SCRIPT_SUBSTITUTION_BRIDGE_NO_POWER`

The bridge cannot carry a correspondence. This is settled *a fortiori* by the calibration: the
**known** LB↔Cypriot cross-script pair is already at the chance floor after multiplicity, so the
LA↔LB application — smaller corpus, unknown language, unverified homomorphs — is **UNDERDETERMINED**
by construction, not merely "unproven." The negative is a power ceiling (methods pass the CTRL
identity control), not an implementation failure.

---

## F3 — leave-one-sign-out relative-class prediction

For every AB correspondence removed and predicted from the remaining graph (seeded methods: seed
on all-but-*i*, predict *i*; unsupervised: per-sign readout of the fixed alignment), grade whether
the predicted LB partner lands in the correct **consonant** or **vowel** equivalence class.
Aggregate accuracies with their permutation-null p (from the table above):

- Exact LOSO: 0.00–0.078; best M1 nominal p 0.014, **fails Holm**.
- Consonant-class LOSO: 0.098–0.137; **no method p < 0.05** (best M1 0.122, M4 0.080).
- Vowel-class LOSO: 0.157–0.353; only M2 nominal p 0.023, **fails Holm**.

**F3 conclusion:** leave-one-sign-out does not recover even the *relative class* of a held-out
LA↔LB correspondence at a level surviving multiplicity. No equivalence-class constraint is
licensed from the cross-script channel.

---

## F4 — LA output: relative compatibility + equivalence classes + uncertainty ONLY

Per the NO_POWER verdict, the only admissible Linear A output is relative and uncertainty-bearing.
`F4_la_relative_constraints.json` records, for each of the 51 LA AB-signs, the ranked LB partners
its GW coupling is compatible with **and** the coupling entropy.

- Geometry top-1 == homomorph: **2 / 51 (0.039)** — at the 1/51 ≈ 0.02 chance floor (KA, RI only).
- **Mean normalized coupling uncertainty = 1.000** (coupling is maximum-entropy): the per-sign
  candidate rankings carry essentially no information and must not be read as real compatibilities.
- Within-LA equivalence classes (the C4 substitution REL_CLASSes; vowel-alternation / shared-
  consonant axis) are carried through **as relative, value-free structure only** — they are a
  property of the LA graph itself (durable L2/L3), not a product of the cross-script bridge.

**Absolute-value claim: NONE.** **Licence state: PHONETIC / LEXICAL / SEMANTIC = NOT_EARNED**
(Art. XV — a relative-class reduction does not become a phonetic value). This channel does not
pin any LA sign to an LB/GORILA value and does not narrow the value lattice enough to move
**SEED_A (= 0)**.

---

## What this adds to the campaign

1. **Positive, durable (L2/L3):** the substitution-neighborhood **consonant/vowel-alternation
   axis** is real and value-free in LB, and *strengthens* under frequency- and formula-disjoint
   holdouts (F1: same_C AUC 0.70→0.75; all LOSO folds; label-shuffle p 0.003). This is a clean
   opaque-script calibration of the relative channel.
2. **Bounded negative (the point of the task):** the *cross-script* substitution bridge —
   NN-transfer, structural Hungarian, Gromov–Wasserstein OT, spectral+Procrustes — has **NO POWER**
   at Linear-A scale. It fails on the KNOWN LB↔Cypriot control after multiplicity, hence LA↔LB is
   underdetermined. The AB homomorphy map is at most weakly self-consistent (M1 4/51, dies under
   Holm) and yields no equivalence-class constraint (F3) and no value (F4).
3. **DO-NOT-REPEAT update:** substitution-neighborhood cross-script *value/correspondence* transfer
   joins raw distributional A↔B transfer as a power-limited dead end at current corpus scale —
   the blocker is corpus size (the known control fails too), so *more of the same corpus cannot
   fix it*; only a bilingual or independent held-out anchors would. Re-open only if the LA corpus
   or a value-free anchor set materially grows.

**Compliance line.** Articles V/VII/VIII/XI/XII/XV honored: claims worded at L2/L3 relative only;
non-circular (opaque IDs, values grade-only); multiplicity via Holm; permutation nulls throughout;
no licence earned; append-only (this report supersedes nothing, corrects nothing).
