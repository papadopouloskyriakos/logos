# PREREG DRAFT — cross-script LA↔LB value-recovery gate (C2 offensive)

**STATUS: DRAFT (Phase 0).** This file is a pre-registration *draft*. The **binding**
pre-registration is a future commit that freezes the final design AFTER the §3 go/no-go verdict
and (if pursued) the primary-source acquisitions. **No recovery model may run on real data
before that freeze.** Phase 0 builds prerequisites only. The §3 power thresholds below are
binding on the Phase-0 power analysis itself: they are committed BEFORE any power run executes,
and a threshold written after seeing power curves is void.

Nothing under `paper/` is read or written by this experiment.

---

## 1. Feature contract (circularity ban) — BINDING on all future gate code

### BANNED — any glyph-image or shape-derived feature

HOG, Hu moments, shape-context, render embeddings, visual-similarity scores, JEPA/palaeo
embeddings, anything downstream of sign IMAGES (`corpus/bronze/sign_images/`, `scripts/palaeo/`,
the rendered-font pipeline). **Reason:** the repo's own cross-script image-leg finding
(docs/findings/2026-06-30-palaeo-jepa.md; CLAUDE.md status: "cross-script image leg = circular
demonstration, capped ≤ 0.75") — shape features recover the A↔B mapping *circularly*, because
the conventional values were historically assigned by shape homomorphy. A gate cleared on shape
features validates the convention against itself and proves nothing.

### ALLOWED

- **LA-internal distributional features**: sign co-occurrence / positional statistics — the B.2
  PPMI machinery (`phono_distributional.build_context_vectors`) and word-position statistics
  from the structured silver (word-initial/-final/interior profiles).
- **LB-side lexical and phonotactic constraints**: DĀMOS-derived (`data.load_b_damos`) wordform
  statistics — value-in-word positional profiles, neighbour-value phonotactics, word-length
  distributions.
- **Lexical/toponym anchor constraints** (the pa-i-to / ku-do-ni class) — **currently ZERO
  infrastructure in the repo** (grep: no pa-i-to/ku-do-ni/toponym hits). Each such anchor
  requires its own per-item provenance sourcing (edition + page) BEFORE use; unsourced anchors
  are inadmissible.
- **The Cypriot-stable line** as a train/test split axis and independent corroboration —
  admissible only after Steele & Meißner 2017 is acquired (currently `pending_primary` on all
  59 anchor rows).

### Labels rule

Conventional value assignments (litindex `lb_value_transfer`, the `data.py` bridge) enter ONLY
as held-out labels and train-anchor supervision, NEVER as features. No feature may be computed
from a sign's own conventional value.

### Enforceability clause (inherited by the future gate prompt)

The eventual model code must be **grep-clean** of image/shape modules, verified by an automated
test in the same pattern as `test_morphology.test_does_not_import_verdict`: no import or
reference matching `(palaeo|jepa|sign_images|hog|hu_moment|shape|render|PIL|cv2|skimage|torchvision)`
in any module under `experiments/crossscript_gate/` that touches real data, and a fresh-
interpreter import of the gate entrypoint must not pull any of those modules into `sys.modules`.
The Phase-0 power analysis (`power_precheck.py`) is bound by the same clause.

---

## 2. Power pre-check thresholds — PRE-COMMITTED (§3 Step 1; frozen BEFORE any power run)

### Design constants (from the anchor table, real numbers)

- n_anchors = **51** robust anchors (ANCHORS.md; ≥3 LA attestations, DĀMOS-bridged).
- Held-out budget h = **10** (primary); sensitivity h ∈ {5, 15, 20} (non-binding, reported).
- Candidate value space = **73** DĀMOS-attested Unicode LB syllabary values (chance 1/73 ≈ 0.0137).

### Simulation design (B.2 planted-positive-control pattern, `_power_control` convention)

- **Value embeddings U_v (ALLOWED features, real geometry):** PPMI (window 2, cds 0.75) →
  TruncatedSVD d=24 over the real DĀMOS wordforms — the exact embedding recipe of the existing
  Track-B pipeline — L2-normalised, one vector per candidate value.
- **LA-side synthetic features (never real vectors with real labels):**
  `X_sign = s · (R @ U_{v(sign)}) + ε`, ε ~ N(0, I_24), then L2-norm; R = a fixed random
  orthogonal map drawn per replicate; s = planted strength in units of the unit noise (the B.2
  strength convention — B.2's real-data control fired at s = 2.0 on its 50-sign problem).
- **Stand-in decoder (simulation only, NOT a recovery model on real data):** orthogonal
  Procrustes (`scripts/cross_script/align_methods.Procrustes`, reused) fit on the 41 train
  anchors; held-out prediction = nearest neighbour among all 73 candidate value embeddings.
- **Metric:** held-out top-1 value-recovery accuracy (top-5 reported, non-binding).
- **Null (the gate's own null):** permuted-graph — permute the anchor↔value assignment across
  all 51 anchors, rerun the identical pipeline; n_perm = 200 per replicate; detection iff
  add-one permutation p < 0.05 (Phipson–Smyth, as in B.2).
- **Replicates:** n_rep = 50 per strength; power(s) = fraction of replicates detecting.
- **Strength grid:** s ∈ {0, 0.5, 1, 2, 3, 5, 8, 13} (B.2's grid + 0 calibration + 0.5).
- **Seeds:** master 20260703; replicate seed = 20260703 + 10000·strength_index + rep.

### Verdict thresholds (frozen now)

- **INVALID (harness, not corpus):** false-fire rate at s=0 exceeds 0.14 (>7/50; binomial 95%
  bound on nominal 0.05), OR power at s=13 is below 0.90 (the B.2 "broken test" branch: a
  near-noiseless plant must be detectable). INVALID means fix the harness and rerun; the
  thresholds themselves do not move.
- **GO:** power ≥ 0.80 at some s ≤ 3.
- **MARGINAL:** not GO, and power ≥ 0.80 at some s ≤ 8. Decision escalates to the operator with
  the curves.
- **NO-GO:** power < 0.80 for all s ≤ 8.
- **Pre-committed NO-GO follow-up:** sweep synthetic n_anchors ∈ {51, 100, 150, 200, 300}
  (h = 0.2·n, |V| = 73) and report the smallest n at which GO would hold — the "the design would
  have power at N anchors" bound, itself a publishable identifiability result.

The commit hash of THIS file at power-run time is recorded in the results JSON; a mismatch
voids the run.

---

## 3. Edge statement — what is, and is not, new (written against the actual repo code)

Honesty first: **the naive edge claim is half false.** "Masked-homomorph full-value prediction"
is NOT new in this repo. `scripts/cross_script/validate.py` already implements exactly that
protocol — *"Split the 55 anchors into TRAIN (80%) and HELD-OUT (20%) … For each held-out
anchor s: map E_A(s) into B-space, take its nearest neighbour among ALL B signs"* — over five
alignment methods, 200 bootstrap splits, and it returned **chance-level recovery even at full
DĀMOS scale** (best 0.025 vs chance 0.011; positive control 0.947; finding
2026-06-30-ab-alignment-null.md). Any gate built on sign-level co-occurrence-geometry alignment
would be a rerun of a published-in-repo null.

The genuine edges of the proposed gate, stated precisely:

1. **Feature channel, not task**: the failed channel was *sign-level co-occurrence geometry*
   (PPMI-SVD spaces aligned Procrustes/CCA/OT). The gate's channel is **word-level
   lexical/phonotactic constraint matching**: a masked LA sign's positional profile *inside LA
   word-forms* (the scribes' divisions — which the segmentation positive shows carry real,
   held-out-recoverable structure) scored against each candidate value's profile *inside DĀMOS
   wordforms* (position-in-word, neighbour phonotactics, word-length). B.2, for comparison, was
   a *C/V class* LOO-1NN on LA context alone (13-class consonant / 5-class vowel;
   `phono_distributional.run_pilot`), not full-value prediction with LB-side lexical context.
2. **Cypriot-stable split axis** (independent corroboration the repo has never used) — a fixed,
   externally-motivated held-out set rather than random splits. Contingent on acquiring Steele
   & Meißner 2017 (currently absent; all rows `pending_primary`).
3. **Lexical/toponym anchors as hard constraints** (pa-i-to class) — genuinely absent from the
   repo today; requires per-item provenance sourcing before admission.
4. **A formal fail-closed gate**: committed hypothesis rows (plan_hash), SearchLog multiplicity
   accounting, permuted-graph null, and pre-committed thresholds — the prior Track-B run was an
   honest probe with held-out protocol and controls, but not a pre-registered gate.

Prior odds, stated: with the alignment null (chance at 15× corpus scale) and B.2's data-limited
null on the books, the reasonable prior for the gate is unfavorable. Both outcomes are
publishable (§4); the NULL abstract is the likelier one. That is not a reason to skip the gate —
it is the reason the gate must be pre-registered before anyone runs it.

---

## 4. Dual outcome abstracts (written BEFORE any gate run — the discipline)

### (i) CLEARED

> The syllabic values of Linear A's shared (AB) signs are conventionally back-projected from
> Linear B, a transfer never empirically validated at the value level. We pre-registered a
> held-out value-recovery gate: N homomorphic anchor signs were masked, and their values
> predicted from non-shape evidence only — Linear-A-internal distributional structure and
> Linear-B lexical/phonotactic constraints from the 13,562-wordform DĀMOS corpus — under a
> permuted-graph null with pre-committed thresholds and multiplicity accounting. Recovery
> exceeded the null for N held-out signs (top-1 accuracy X vs chance 1/73), the first
> gate-cleared empirical support for backward projection on any subset of the syllabary.
> Shape-derived features were excluded by construction, breaking the historical circularity of
> shape-assigned values. We release the anchor table, feature contract, and gate artifacts; the
> result licenses no reading of Minoan — it validates sign *values*, not language.

### (ii) NULL

> The syllabic values of Linear A's shared (AB) signs are conventionally back-projected from
> Linear B; we tested whether that convention is independently recoverable from non-shape
> evidence. In a pre-registered, held-out gate, masked anchor signs' values were predicted from
> Linear-A-internal distributional structure plus Linear-B lexical/phonotactic constraints
> (DĀMOS, 13,562 wordforms) against a permuted-graph null with pre-committed thresholds.
> Recovery did not exceed chance (1/73), extending the repo's alignment-geometry null to the
> lexical-constraint channel: at current corpus scale, the LA↔LB value convention rests on
> shape homomorphy alone, and no non-shape channel yet carries it. Combined with a planted-value
> power analysis locating the corpus size at which the design would detect a real signal, this
> is a quantitative identifiability bound — strengthening the thesis that Linear A's limit is
> information, not effort, and mapping exactly what evidence a future decipherment claim must
> produce.

---

## 5. Status clause

This document is a **draft**. Binding effect: only §2 (power thresholds, binding on the Phase-0
power analysis, frozen at commit time) and §1 (feature contract, binding on all future gate
code, including the power analysis). Everything else — the final feature set, the held-out
axis, the anchor exclusions for conflicted signs, the grading clauses — is frozen by a future
pre-registration commit AFTER the go/no-go verdict and primary-source acquisitions. **No
recovery model runs on real data before that freeze.**
