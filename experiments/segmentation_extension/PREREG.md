# PRE-REGISTRATION — segmentation extension (revision-queue only)

**Frozen: 2026-07-03, BEFORE any model run.** This file is committed before the equivalence
gates execute and before any pre-registered model class runs. Nothing here is edited after
results are seen; any amendment would require a new dated addendum that adds no model class.

**Scope guard.** The paper is under review at TACL. The published segmentation positive —
DP-unigram micro-F1 **0.436** vs random-boundary **0.389**, site-clustered bootstrap 95% CI
**[0.021, 0.099]**, P(gap>0)=0.998 (52 sites, 4,000 draws) — is the untouched baseline/anchor,
never a target to beat. Nothing under `paper/` is read or written by this experiment. No
sound-value, phonetic, or decipherment claim is made: **word boundaries only**.

---

## 1. Hypothesis

Richer segmentation model classes recover the scribes' word divisions above the
random-boundary floor by a site-clustered margin whose 95% CI excludes zero — the same bar
the published DP-unigram cleared. Secondary question: does any richer class recover **more**
boundary structure than the DP-unigram anchor (model−DP gap CI), or does the published result
stand as the best available? A null, a worse number, or a memorizing neural model are all
valid, reportable outcomes.

## 2. Provenance of the grading machinery (§0 finding, resolved by approval)

- The **metric** (boundary-level micro-F1) exists as reusable code in
  `scripts/comparison/morphology.py` at commit **`1aa12496a9d9e84f1906b1a40c4089335a51b3d1`**.
- The **site-clustered bootstrap** behind the published CI was a one-off (2026-07-01, "Item 8",
  commit `5a8ec26`), never committed; its seed is unrecorded. It is reconstructed here from its
  published specification (preprint App. A): *"resample the 52 sites with replacement, 4,000
  draws … the paired gap, not the wide marginal per-segmenter CIs, is the operative test."*
- **Approved approach (operator decision, 2026-07-03): copy-in frozen snapshot**, not live
  import. The metric functions and segmenter classes are copied verbatim from
  `scripts/comparison/morphology.py` @ `1aa1249` into
  `experiments/segmentation_extension/frozen_metric.py` with the source commit recorded in its
  header. No file outside `experiments/segmentation_extension/` + `docs/revision-queue/` is
  modified. Copied objects: `Inscription`, `load_corpus`, `SignCodec`, `true_boundaries`,
  `_prf`, `_boundary_rate`, `_score_segmenter_on`, `_score_random_on`, `random_boundaries`,
  `DPUnigramSegmenter`, `MorfessorSegmenter`, and the leave-one-site-out fold loop of
  `boundary_recovery` (generalized ONLY to accept arbitrary segmenters and to retain per-site
  tp/fp/fn; fold order, rng construction, and rng consumption order unchanged).

## 3. HARD EQUIVALENCE GATES (blocking; run and recorded before any model class)

Committed here per operator instruction. Results go to
`experiments/segmentation_extension/GATE_RESULTS.md`, committed before any model run.

- **Gate A — deterministic point estimates, EXACT.** The experiment-local LOSO driver, running
  the snapshot `DPUnigramSegmenter` (`alpha=2.0, p_boundary=0.5, max_len=8, iters=6, seed=0`)
  plus the random baseline (single `np.random.default_rng(0)`, sorted-site consumption order),
  must reproduce **micro-F1 0.4361 (DP-unigram) and 0.3888 (random) to 4 decimals exactly**
  (Morfessor 0.1556 recorded informatively). **If the point estimates do not match exactly:
  STOP and report — that is a real discrepancy, not a tolerance question.** No model class runs.
- **Gate B — reconstructed bootstrap, toleranced.** The reconstructed site-clustered bootstrap
  (spec in §4) at **bootstrap seed 20260703**, applied to the DP-unigram vs random per-site
  counts from Gate A, must yield a 95% CI whose **bounds each fall within ±0.005 of
  [0.021, 0.099]** and **P(gap>0) ≥ 0.99**. CI stability across seeds 20260704–20260707 is
  reported (informative, non-blocking).

Only after both gates pass and are recorded do any new model classes run.

## 4. Grading protocol (identical for every entry; frozen)

- **Corpus:** `corpus/silver/inscriptions_structured.json` — 1,341 inscriptions / 52 sites
  (incl. the `"(unknown)"` bucket) / 3,147 word tokens / 1,165 distinct word types (984
  multi-sign) / 5,792 sign tokens / 259 distinct signs; 618 inscriptions have streams >1 sign
  (scoreable). (The task brief's "~5,800 tokens" are sign tokens; "539 word-forms" matches no
  measured count and is superseded by the numbers above, generated per invariant 12.)
- **Metric:** boundary-level micro-F1 from the frozen snapshot — per inscription, the full
  encoded sign stream; predicted internal cut positions vs the scribe's cut positions; tp/fp/fn
  pooled over all inscriptions of all held-out folds. No reimplementation.
- **Held-out protocol:** leave-one-site-out over the 52 sites (`min_site_size=1`), train on all
  other sites' full inscription streams, predict the held-out site. Fold order = sorted site
  names. Identical for every entry.
- **Random floor:** per fold, boundaries at the TRAIN-fold scribal rate (`_boundary_rate(train)`),
  one sequential `np.random.default_rng(0)` consumed in sorted-site order — the identical
  construction, giving the identical random per-site counts for every entry.
- **Site-clustered bootstrap (reconstructed):** B=4,000 draws; each draw resamples the 52 sites
  with replacement (seed **20260703**, `np.random.default_rng`); per draw, pool per-site
  tp/fp/fn for every entry and for random over the SAME resampled multiset (fully paired across
  entries and floors); compute micro-F1 per entry; gap = F1(entry) − F1(random); 95% percentile
  CI [2.5, 97.5] and P(gap>0) = fraction of draws with gap > 0. The same draws also grade
  gap(entry − DP-unigram anchor).
- **Clearing rule:** an entry *clears* iff its entry−random gap 95% CI excludes zero.
- **Multiplicity disclosure (invariant 8):** 3 pre-registered model classes ⇒ each entry also
  reports the Bonferroni family-corrected **98.33% CI** (1 − 0.05/3); the clearing rule above is
  the primary, the corrected CI is reported next to it, both pre-committed here.
- **Anchor row:** the DP-unigram is re-graded under the reconstructed harness as the labeled
  anchor (that is Gate B). The published 0.436 / [0.021, 0.099] numbers are never edited.

## 5. Model classes (FIXED NOW — no additions or hyperparameter changes after any result)

### Class 1 — Bayesian nonparametric: Pitman–Yor-process unigram Gibbs segmenter (primary)

The principled generalization of the Goldwater DP-unigram (PYP with discount d recovers the DP
at d=0). Pure CPU, Chinese-restaurant bookkeeping.

- **Model:** single-level PYP unigram lexicon (discount `d`, concentration `α`); base measure
  identical in form to the DP baseline's: `P0(w) = p♭(1−p♭)^(|w|−1) · (1/V)^|w|`, `p♭ = 0.5`,
  `V` = train-fold distinct-sign count.
- **Inference:** boundary-site Gibbs sampling (Goldwater, Griffiths & Johnson 2009) over every
  internal position of the training streams, exact CRP table tracking; inverse-temperature
  annealing linear 0.1→1.0 over burn-in.
- **Hyperpriors:** `d ~ Beta(1,1)`, `α ~ Gamma(shape=1, scale=10)`; both resampled every 10
  sweeps by slice sampling.
- **Sampler budget:** 1,000 sweeps per chain, burn-in 500, lexicon/table counts sampled every
  10th post-burn-in sweep (50 samples/chain); **3 chains** per fold.
- **Seeds:** chain seed = `20260700 + 1000·chain_id + fold_idx` (chain_id ∈ {1,2,3}, fold_idx =
  index of the site in sorted order).
- **Convergence check:** split-R̂ across the 3 chains on the per-sweep joint log-posterior;
  reported per fold (max and distribution); target < 1.1, reported honestly either way.
- **Graded decode (deterministic given samples):** posterior-mean sufficient statistics
  (mean lexicon counts n̄_w, mean table counts t̄_w, T̄, posterior-mean d̄, ᾱ, averaged over all
  150 samples) plugged into the PYP predictive
  `P(w) = (n̄_w − d̄·t̄_w + (ᾱ + d̄·T̄)·P0(w)) / (N̄ + ᾱ)` (floored at ε>0), single Viterbi pass,
  `max_len = 8` (same as the DP baseline).
- **Implementation sanity checks (non-graded, run before the graded run):** (i) recovers the
  planted lexicon on the synthetic segmentable corpus (analog of
  `test_dp_segmenter_recovers_known_lexicon`); (ii) with d fixed to 0 and hyperparameter
  resampling off, lands in the DP baseline's neighborhood on the real corpus (informative only).

### Class 2 — Tiny neural sequence boundary model (supervised; capped hard)

**Regime disclosure, fixed now:** unlike the unsupervised DP/PYP, this model is trained
SUPERVISED on the scribe's own divisions from the 51 training sites and predicts the held-out
site — it estimates cross-site predictability of the scribal boundary placement, an upper-bound
style probe. It is graded against the identical random floor and bootstrap, and labeled
supervised in every table.

- **Architecture (torch 2.12.1+cpu):** sign embedding dim 16 (vocab = train-fold signs + UNK +
  pad), single-layer BiLSTM hidden 16/direction, dropout 0.2; boundary after sign i predicted
  from `[h_i ; h_{i+1}]` → linear(64→1). **Hard parameter cap: ≤ 10,000 trainable parameters**
  (expected ≈ 8.5k; the count is asserted at run time against the cap; corpus = 5,792 sign
  tokens — the over-parameterization cliff is why this is tiny).
- **Unseen test signs** map to UNK.
- **Training:** BCE on internal positions of train streams; Adam lr=1e-3, weight decay 1e-4,
  batch = 32 streams (padded), max 200 epochs; early stopping patience 15 on dev loss.
- **Dev split (deterministic, test-blind):** train streams whose `md5(iid)` last hex byte
  mod 10 == 0 form the dev set.
- **Decision threshold:** chosen per fold on the dev split maximizing dev boundary-F1 over the
  grid 0.05–0.95 step 0.05 (default 0.5 if the dev split has no positive positions). Test site
  never touched.
- **Seeds:** graded run seed **20260703** (torch + numpy); stability runs at 20260704 and
  20260705 reported.
- **Memorization check (pre-committed):** report train micro-F1 vs held-out micro-F1 per the
  same metric; **flag "memorization regime" if (train − test) micro-F1 gap > 0.20**. A
  memorizing model is a reportable negative, not a failure to hide.

### Class 3 — Morfessor Baseline with tuned prior (second baseline; optional per task, included)

Bounds whether vanilla Morfessor's published over-segmentation (0.156) is inherent or a prior
artifact.

- **Tuning (test-blind, deterministic):** corpusweight grid **{0.05, 0.1, 0.5, 1.0, 5.0, 10.0,
  50.0}**; per fold, select the weight whose predicted boundary rate on the TRAIN streams is
  closest to the TRAIN-fold scribal boundary rate. Train/decode as the snapshot wrapper
  (stdlib `random` seeded per wrapper); seed **20260703**.

## 6. Pre-committed reporting rule

Every model class above is reported in `docs/revision-queue/segmentation_extension.md`
regardless of outcome — cleared, null, worse-than-random, non-converged, or memorized. No model
is dropped for underperforming. Per class: micro-F1/P/R, entry−random gap + 95% CI +
Bonferroni 98.33% CI + P(gap>0), entry−DP-unigram gap + CI, train/test gap (Class 2), R̂
(Class 1), selected corpusweights (Class 3), wall-clock, all seeds. Sampler nondeterminism, if
any, is reported honestly.

## 7. Compute

Local CPU only (20 cores); fold- and chain-parallel via multiprocessing. No GPU: the corpus
(5,792 sign tokens) forbids model scale, and the bootstrap is arithmetic. All artifacts under
`experiments/segmentation_extension/results/` (per-site counts, bootstrap draws, per-fold
diagnostics) for auditability.
