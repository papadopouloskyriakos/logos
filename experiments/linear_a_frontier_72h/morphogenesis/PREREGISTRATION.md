# TURING MORPHOGENESIS family — PREREGISTRATION (E091–E096)

**Frontier family:** `TURING_MORPHOGENESIS` · **priority:** IMMEDIATE · **status:** ACTIVE
**Reserved epochs (next available after E090):** E091 · E092 · E093 · E094 · E095 · E096
**Registered:** 2026-07-09 (live, inside the 72h campaign; finalization gate remains BLOCKED).
**Layer ceiling:** L2/L3 only. **Absolute sound values are NOT authorized from internal morphogenesis patterns alone**
(Constitution Art. V / Art. XV). Forbidden outputs (§11 of the brief) are hard-gated in code and reporting.

## Central hypothesis
A graph reaction–diffusion (Turing) system — local activation + longer-range inhibition + **unequal** diffusion on a
Laplacian — recovers known linguistic structure in **blinded** Linear B (phonetic values hidden), and only then is
applied to Linear A. The null-of-record: **generic graph clustering (spectral / SBM) does the same or better**, in
which case "Turing" earns nothing (E092 decides this). Prior from `EPOCH-016` (SBI): fancy methods have repeatedly
tied/lost to raw-cosine spectral clustering on this corpus — so a `GENERIC_GRAPH_CLUSTERING` / `TURING_NOT_NEEDED`
outcome is a live, expected possibility, not a failure.

## Model family (frozen)
Two-field activator–inhibitor on a graph Laplacian `L` (symmetric normalized):
`du/dt = f(u,v) − Du·L·u`, `dv/dt = g(u,v) − Dv·L·v`, with `Du < Dv` (short-range activator, long-range inhibitor).
Reaction families: **Schnakenberg**, **Gierer–Meinhardt**, **Gray–Scott** (≥2 required; ≥3 used).
**Turing instability is verified mechanically for every run** (else `TURING_MODEL_INVALID`):
1. homogeneous equilibrium `(u*,v*)` exists; 2. ODE-stable without diffusion (`Re λ(J) < 0` at λ_graph=0);
3. diffusion-driven instability: `∃` Laplacian eigenvalue `λ_k>0` with `Re λ_max(J − diag(Du,Dv)·λ_k) > 0`;
4. the unstable band is **not** explained by graph degree or connected components (degree-partialled + component-controlled).
Generic clustering relabeled as "morphogenesis" without conditions 1–4 holding is explicitly disallowed.

## Emergent-pattern → class rule (frozen)
Integrate the nonlinear RD to steady state from small random perturbations of `(u*,v*)`; the node-wise activator
pattern `u(∞)` (and the span of the linearly-unstable eigenmodes) is clustered (k chosen by the same frozen rule for
model and all controls) → **anonymous sign classes**. No value is read from a pattern.

## Ground truth (blinded; evaluation only)
DĀMOS Linear B (13,562 sequences, 74 syllabogram signs). Signs are mapped to **opaque IDs** before any graph is
built; the model never sees a value. Held-out truth from the CV structure of the sign value: **vowel class**
(A/E/I/O/U), **consonant class** (D/J/K/M/N/P/Q/R/S/T/W/Z + pure-vowel), and syllabogram/logogram/numeral role.

## Per-epoch commitments
- **E091 — Blinded LB calibration.** Graph views: `G_POSITION` (L/R context, PPMI), `G_SUBSTITUTION` (shared
  L+R context), `G_FORMULA` (shared document/slot co-membership), `G_MULTILAYER` (combined). Verify Turing conditions;
  recover vowel/consonant/role classes; held-out signs (frequency-disjoint + random sign holdout) via neighbor MRR.
  Positive controls: planted-Turing synthetic graph (recover blocks) + the LB graph itself. Negative controls:
  degree-preserving rewiring, label permutation, within-layer edge shuffle, **equal-diffusion** (Du=Dv), **linear
  diffusion only**, **reaction-only** (no diffusion). Metrics: ARI, NMI, macro-F1, AUC, MRR, seed-stability.
  Verdicts: `TURING_LINEAR_B_RECOVERY_SUPPORTED / _PARTIAL / _NULL / _NO_POWER / TURING_MODEL_INVALID`.
- **E092 — Turing-specificity.** Same recovery task vs baselines: spectral clustering, Laplacian eigenmaps, SBM,
  community detection, GMM-on-embedding, (GNN if feasible), linear diffusion, equal-diffusion RD, reaction-only.
  Multiplicity charged over graph-view × reaction-family × params × Du,Dv × init × k × threshold × seed × baseline
  (best-of-search nulls). Turing-specific positive requires: instability verified **and** held-out > best baseline
  **and** search-adjusted significance **and** cross-view stability. Else `GENERIC_GRAPH_CLUSTERING` /
  `TURING_NOT_NEEDED` / `TURING_SPECIFIC_NULL`.
- **E093 — LB→LA degradation surface.** ≥100-cell factorial over corpus size, type/token count, short-form rate,
  hapax rate, site imbalance, damage, missing boundaries/genre/scribal/layout, A-only proportion, freq skew, formula
  repetition; multiple seeds/cell; measure recovery/stability/calibration/FP/equivalence-class reduction; locate the
  LA operating point. Verdicts: `LINEAR_A_ABOVE / _NEAR / _BELOW_THRESHOLD / DEGRADATION_MODEL_INCONCLUSIVE`.
- **E094 — Sequence/segmentation/formula morphogenesis.** RD over position graphs (token/boundary/slot/entry nodes);
  recover word/morpheme/formula/entry boundaries in blinded LB vs DP-unigram/Bayesian/MDL/finite-state/random.
  Freeze before LA; LA outputs probabilistic only.
- **E095 — Geographic/scribal/regional morphogenesis.** RD over site/phase/scribe/genre/allograph graphs; calibrate
  on LB regional/scribal structure with provenance + font + site-doc + genre + freq controls; then frozen LA.
  No "dialect" label without independent evidence.
- **E096 — Frozen LA application.** Only families/parameter-rules that passed E091 calibration + the E092
  specificity gate. No retuning on LA. Authorized: anonymous sign classes, substitution communities, segmentation
  probabilities, formula-region classes, regional classes, per-sign entropy reduction, held-out formula prediction,
  prospective predictions. Forbidden: sound values, translations, language-family ID, "pattern = phoneme".
  Held-out: leave-one-site-out, leave-one-formula-family-out, leave-one-frequency-band-out, untouched inscriptions.

## Full adaptive null (frozen; E092/E096 gates)
Reproduces graph-view/reaction/param/diffusion/init/mode/baseline/threshold/seed selection + best-result reporting.
Null families: degree-preserving rewiring, configuration-model, layer-preserving edge shuffle, site/formula-label
shuffle, token-order shuffle, equal-/linear-/reaction-only dynamics, latent-free synthetic graphs, planted-non-Turing
clusters, wrong-script controls, best-of-param/view/model. Draws: cheap ≥1000, moderate ≥300, full adaptive ≥100.

## Substantive-epoch gate (each epoch)
implemented model · positive control · negative controls · mechanical verdict · persisted machine-readable results ·
successor decision. A **failed calibration is a valid epoch**. No runtime padding; no finalization before the clock.

## Content hash
`plan_hash` per epoch = sha256 of that epoch's frozen prereg slice + code manifest, written to the epoch dir.
