# EPOCH-016 — PREREGISTRATION (frozen BEFORE any verdict run)

**Campaign:** linear-a-frontier-72h · frontier **F9** (new optimization architectures)
**Epoch question:** SIMULATION-BASED INFERENCE PILOT — can an amortized SBI estimator (a neural
pair-posterior trained on a generative admin-syllabary simulator) recover relative sign
VALUE-CLASS structure (consonant rows / vowel columns; gauge-invariant, no absolute labels) on an
opaque known script degraded to Linear A scale, at LA anchor budgets (0/3/5), where the
G-surface anchor-geometry solvers failed (E003/E006)?
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Substantive gate:** A.
**Articles triggered:** V (claim layers), VII (search receipt), VIII (effective_n + multiplicity),
IX (info budget), XI/XII (non-circularity), XV (transfer licences — nothing here earns anything),
XXII (stage header).
**Claim layer of ANY result here: L2 (relative/structural), KNOWN-script calibration only.
LINEAR A IS NEVER LOADED by the analysis script. No LA value claim can emerge. An LA
application, if ever, requires its own prereg.**

## Design (frozen; script sha256 `520bc4e72b4eb2ff65e704091a2979bd696babb296414405da9d8d36efe0a77d`)

Script: `scripts/e016_sbi_pilot.py`. All hyperparameters below are frozen with ZERO tuning
(defaults chosen before any verdict-relevant number was seen; one dev-scale `--simonly` smoke run
was executed pre-freeze on SIMULATIONS ONLY — archived at `data/sbi_pilot/E016_smoke_simonly.json`
— to verify the code runs; Linear B was not loaded in it).

### 1. Generative simulator (true prior, matched to measured stats)

Admin-syllabary corpora over an opaque C×V grid: C~U{10..14} rows (incl. null-consonant row),
V~U{4,5} columns; consonant Zipf s_c~U(0.6,1.0) (measured: LA top-60 slope .781, LB core slope
.799); vowel Zipf s_v~U(0.4,0.9); lexicon Zipf ~U(0.8,1.2) over 300–900 lemmas; word length
geometric with mean ~U(1.6,3.4) syllables, cap 8 (measured: LA 1.84, LB 3.23); vowel-harmony
prob ~U(0,0.5) (plants the same-VOWEL signal); final-vowel paradigm rate ~U(0.25,0.6) with 1–2
alternants (plants the same-CONSONANT signal); formula rate ~U(0.05,0.4) with site-specific
header words; 3–10 sites, Dirichlet imbalance alpha ~logU(0.25,2) + per-site lemma re-weighting
(measured: LA 52 sites, top share .63); words/doc mean ~U(1.5,4.0) (measured LA 2.35).
Consonant/vowel frequency-rank→identity permutations are drawn per simulation so frequency rank
is not the label. Sign ids are opaque; ground-truth (row,col) used ONLY for scoring.

### 2. SBI estimator (amortized neural pair-posterior)

- Training: N_TRAIN=200 sims from the true prior, token budgets logU(4000,30000); 12 pairwise
  features per sign pair (freq≥3 signs): PPMI-context cosine (L+R joint, L, R), 2nd-order cosine,
  final/non-final minimal-pair scores, position-distribution similarity, freq ratio,
  |Δlog f|, Σlog f, |Δ final-share|, |Δ initial-share|. Pool ≤400k pairs.
- Two sklearn MLPClassifiers (64,32), alpha 1e-4, max_iter 200, early stopping: P(same
  consonant row | features) and P(same vowel column | features).
- Class recovery: predicted-probability affinity matrix → spectral clustering (precomputed
  affinity, k = ORACLE number of classes present among kept signs — granted equally to every
  method), anchors (if any) enter as hard equality/inequality constraints on the affinity.
  ARI scored on NON-anchor signs only.

### 3. Baselines (matched anchor budgets, same oracle k, same kept signs)

- **BASE_SPEC** — spectral clustering on the raw 2nd-order-cosine affinity with the same anchor
  constraints ("surface" stand-in: what raw distributional geometry gives without SBI).
- **BASE_M1** (b>0 only) — anchor-profile geometry, the E003 G-surface / M1 estimator analogue:
  sign = vector of PPMI-cosine similarities to the b anchors, k-means(k). This is the geometry
  that delivered .039 at b=5 on the E003 surface.
- **BASE_GW** — the E006-best estimator analogue: entropic Gromov–Wasserstein (eps .05, 50 outer
  iters, sinkhorn 200) coupling the corpus dissimilarity graph to an idealized C×V grid template
  (same-row .35 / same-col .65 / else 1.0), anchors fused at alpha .5 when b>0 (E006 values);
  graded axis-swap-BEST (generous to the baseline, conservative against SBI). If it returns
  non-finite couplings it is marked degenerate and excluded from that replicate.

### 4. Benchmark (the verdict data) — opaque Linear B degraded to LA scale

`load_b_damos()` wordforms; keep words composed entirely of core CV-grid signs
(`^[DJKMNPQRSTWZ]?[AEIOU]$`; 59 signs = 13 rows × 5 cols, 97.7% of tokens; measured pre-freeze,
recorded here). R_LB=20 replicates: seeded permutation of word occurrences, truncated at ≥5,792
sign tokens (= measured LA sign-token count). Signs freq≥3 kept. Anchor budgets b∈{0,3,5};
anchors drawn uniformly from the top-30 most frequent kept signs per replicate (firm equations
are frequent signs); anchor (row,col) revealed to all anchor-using methods identically.
The SBI networks NEVER see LB during training (train = simulations only).

### 5. Controls (run BEFORE the verdict cells, in this order)

- **PC-A (positive, ample)**: 20 held-out true-prior sims at 5× LA scale (28,960 tokens), b=0.
  PASS bar: mean ARI_C ≥ 0.40. FAIL ⇒ pipeline dead ⇒ global SBI_MISCALIBRATED.
- **PC-B (positive, LA scale)**: 20 held-out true-prior sims at 5,792 tokens, b=0. No bar; this
  is the in-distribution power readout at the operating scale (reported).
- **NEG (leakage)**: 20 structure-free painted-label sims (random sign strings; (row,col) labels
  painted on arbitrarily), evaluated at b=5 (tests anchor-constraint leakage too). LEAK if
  |mean ARI_C| ≥ 0.05 AND sign-flip p < .05 ⇒ global SBI_MISCALIBRATED.
- **MISSPEC (adversarial)**: a second SBI trained on a WRONG prior (s_c~U(1.4,1.8), harmony=0,
  paradigm~U(0,0.1), wlen mean~U(1.2,1.6)), evaluated on the 20 true-prior LA-scale held-out
  sims. OOD detector: median per-pair mean-|z| under the wrong-training scaler; threshold = 95th
  pct of the same stat on 20 wrong-prior held-out sims. Outcomes: ARI_C drop ≥ 0.10 with flag
  fraction ≥ 0.50 ⇒ VISIBLE_FAILURE (acceptable); drop ≥ 0.10 with flag fraction < 0.50 ⇒
  SILENT_FAILURE ⇒ global SBI_MISCALIBRATED (a silently-wrong simulator is disqualifying for any
  unreadable-script application); drop < 0.10 ⇒ ROBUST.
- Descriptive (non-verdict): the true-prior OOD detector applied to the 20 LB replicates —
  does the simulator regard real LB as in-distribution? Reported either way.

### 6. Mechanical verdict (primary endpoint = consonant-row ARI)

Per budget b∈{0,3,5}: paired per-replicate difference d_r = ARI_C(SBI) − max(available baselines)
(per-replicate max — conservative against SBI). Two-sided sign-flip permutation test on mean d
(10,000 flips), Holm over the 3 budgets.

- **SBI_BEATS_SURFACE(b)**: mean d ≥ +0.05 AND Holm p < .05
- **SBI_UNDERPERFORMS(b)**: mean d ≤ −0.05 AND Holm p < .05
- **SBI_MATCHES(b)**: otherwise
- **SBI_MISCALIBRATED (global override)**: PC-A fail OR NEG leak OR MISSPEC silent failure.

Secondary endpoint (reported, same mechanics, explicitly labelled secondary, not
verdict-bearing): vowel-column ARI differences.

## Non-circular contract (Art. XI/XII)

The simulator is parameterized from aggregate corpus statistics only (token counts, Zipf slopes,
length/site distributions — measured pre-freeze and quoted above); no LB sign identity, no LB
value, and no LA data of any kind enters simulator design or SBI training. Ground-truth LB
(row,col) classes derive from the standard transliteration values and are read ONLY by the
scorer (and, for b>0, revealed for the b anchor signs to every method identically). The oracle
k (number of classes among kept signs) is granted to all methods equally. Nothing graded here
was produced by the rule that grades it.

## Committed prediction (before the verdict run)

- Modal: **SBI_MATCHES at all three budgets** — p = 0.35 (sim-to-real transfer gap eats the
  learned-feature advantage; baselines use LB's own geometry directly).
- SBI_BEATS_SURFACE at ≥1 budget — p = 0.20 (the learned combination of minimal-pair +
  context features is genuinely richer than raw cosine).
- SBI_UNDERPERFORMS at ≥1 budget — p = 0.20.
- Global SBI_MISCALIBRATED (incl. silent misspec failure) — p = 0.25.
- Sub-predictions: (i) PC-A passes (p=0.8); (ii) anchor budgets 3 vs 5 change ARI by < 0.05
  for every method (5 anchors of ~59 signs are near-null constraints; the interesting axis is
  b=0 gauge structure) (p=0.7); (iii) BASE_M1 is the weakest baseline at b∈{3,5} (p=0.6, the
  E003 lesson); (iv) LB flagged OOD under the true prior in ≥ half the replicates (p=0.55 —
  real language ≠ simulator; honesty readout for any future LA use).

## Multiplicity / effective n (Art. VIII)

3 verdict comparisons (budgets) × 1 primary endpoint, Holm-corrected; 20 paired replicates each.
Controls are gates, not claims. Secondary (vowel) endpoint labelled, not verdict-bearing.
No hyperparameter search anywhere (search receipt: 1 configuration, frozen).

## Compute

Local CPU only, sklearn/numpy; budgeted ≤ 30 min wall.
