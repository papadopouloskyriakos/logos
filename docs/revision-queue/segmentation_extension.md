# Segmentation extension — pre-registered richer model classes (revision-queue)

**Date:** 2026-07-03. **Status:** pre-registered extension, executed under the frozen protocol.
**Scope guard honored:** no file under `paper/` was read or modified at any point; the published
segmentation positive (DP-unigram micro-F1 0.436 vs random 0.389, site-clustered 95% CI
[0.021, 0.099], P(gap>0)=0.998) is untouched and remains the anchor. No sound-value, phonetic,
or decipherment claim is made — word boundaries only.

Artifacts: `experiments/segmentation_extension/` (PREREG.md, GATE_RESULTS.md, code,
`results/*.json`).

## 1. Verification of the published machinery (§0 of the task)

- **Current segmenter.** `scripts/comparison/morphology.py` — `DPUnigramSegmenter`
  (lines 616–697): Goldwater-style DP-unigram, deterministic Viterbi-MAP hard-EM (not Gibbs);
  `alpha=2.0, p_boundary=0.5, max_len=8`, published run `dp_iters=6, seed=0`. Morfessor
  Baseline wrapper at lines 699–753. Pure numpy + optional `morfessor` 2.0.6.
- **Metric.** Boundary-level micro-F1: per inscription, the whole encoded sign stream; predicted
  internal cut positions vs the scribe's cut positions (`true_boundaries`, `_prf`,
  `_score_segmenter_on`, lines 765–811); tp/fp/fn pooled over all inscriptions of all held-out
  folds. Streams of length ≤1 are unscoreable and skipped.
- **Held-out protocol.** Leave-one-site-out over 52 sites (incl. the `"(unknown)"` bucket,
  `min_site_size=1`), fold order = sorted site names; random baseline draws boundaries at the
  TRAIN-fold scribal rate from one sequential `np.random.default_rng(0)`.
  **Disclosed quirk (replicated for pairing):** the original keys test folds by
  `ins.site or "(unknown)"` but filters train by `ins.site != site`, so the `"(unknown)"` fold's
  3 inscriptions are also in their own (unsupervised) training set.
- **The published CI's harness did not exist as code.** The site-clustered bootstrap behind
  [0.021, 0.099] was a one-off (2026-07-01, "Item 8", commit `5a8ec26`), never committed, seed
  unrecorded; the runtime artifact keeps only rounded per-site F1s, not the per-site tp/fp/fn a
  cluster bootstrap needs. Resolved by an operator-approved **copy-in refactor**: metric +
  segmenters copied verbatim (source commit `1aa1249`) into
  `experiments/segmentation_extension/frozen_metric.py`; LOSO driver + bootstrap reconstructed
  from the published spec in `harness.py`.
- **Frozen-invariant guards.** No test pins 0.436; the freeze is byte-hashes of `paper/build/*`
  in the submission notes. No CI config or git hooks exist. This experiment writes only under
  `experiments/segmentation_extension/` + `docs/revision-queue/` and cannot trip anything.
- **Corpus (measured).** 1,341 inscriptions / 52 sites / 3,147 word tokens / 1,165 distinct
  word types (984 multi-sign) / 5,792 sign tokens / 259 distinct signs; 618 scoreable streams
  (>1 sign). Site sizes: min 1 / median 2 / max 845 (Haghia Triada dominates bootstrap
  variance). Baseline run: CPU-only, 52-fold LOSO (DP + Morfessor + random) = **20.6–22.2 s**
  single-process.

## 2. Equivalence gates (blocking, PREREG §3 — both PASSED before any model ran)

- **Gate A (exact):** experiment driver reproduced DP-unigram **0.4361** / random **0.3888**
  / Morfessor 0.1556 — 4-decimal exact.
- **Gate B (toleranced):** reconstructed bootstrap (B=4,000, seed 20260703) gave DP−random gap
  95% CI **[0.0204, 0.0991]** vs published [0.021, 0.099] (deviations 0.0006/0.0001, tolerance
  ±0.005), P(gap>0)=**0.9985**; stable across 4 further seeds. The original one-off's seed is
  unrecoverable, so "same seeds" is satisfiable only for the reconstruction going forward; all
  entries below are graded on the SAME draws (seed 20260703), fully paired.

## 3. Pre-run adversarial review (PREREG Addendum A)

A 5-reviewer + independent-verification workflow ran after the gates but **before any graded
execution**; PYP mathematics and the bootstrap statistics reviews returned clean. Three
confirmed findings, all Class 2 (neural), all fixed pre-run: (1) *major* — dev-threshold/early
stopping calibrated on padded-batch probabilities while grading decodes unpadded
(backward-LSTM pad-state contamination; fixed with packed sequences, padded-vs-solo now
bit-identical); (2) vocab built from the non-dev subset vs the frozen "train-fold signs"
(fixed); (3) the `"(unknown)"`-fold quirk placed 2 labeled held-out streams (DRAZg1, INZb1;
both single-word) into supervised training (fixed by a Class-2-only exclusion; unsupervised
entries keep the quirk for anchor pairing). No graded number existed when the fixes were made.

## 4. Results per pre-registered model class

All entries graded on the identical 52-fold LOSO protocol, identical frozen metric, identical
random per-site counts (reused byte-identical from the gate run), and identical bootstrap draws
(B=4,000, seed 20260703). "Clears" = the entry−random gap 95% CI excludes zero (the anchor's
bar). Bonferroni CI = the pre-committed 98.33% family-corrected interval (3 classes).

| entry | regime | micro-F1 | P | R | cut-rate | gap vs random, 95% CI | Bonferroni CI | P(gap>0) | clears |
|---|---|---|---|---|---|---|---|---|---|
| random floor | — | 0.3888 | 0.405 | 0.374 | 0.406 | — | — | — | — |
| **DP-unigram (anchor)** | unsup. | **0.4361** | 0.372 | 0.526 | 0.573 | +0.052 [+0.020, +0.099] | [+0.012, +0.108] | 0.9985 | yes (published) |
| **PYP-unigram Gibbs** | unsup. | **0.5590** | 0.408 | 0.886 | 0.880 | +0.162 [+0.098, +0.189] | [+0.082, +0.193] | 1.0000 | yes (caveats below) |
| **tiny BiLSTM (graded)** | **supervised** | **0.6217** | 0.664 | 0.585 | 0.357 | +0.237 [+0.188, +0.322] | [+0.172, +0.336] | 1.0000 | yes |
| **Morfessor tuned** | unsup. | **0.1564** | 0.356 | 0.100 | 0.114 | −0.206 [−0.291, −0.075] | [−0.298, −0.047] | 0.0010 | no (worse than random) |
| *diagnostic: all-boundaries* | degenerate | *0.5773* | *0.406* | *1.000* | *1.000* | — | — | — | *(post-hoc reference)* |

Gap vs the DP-unigram anchor (same paired draws): PYP +0.110 [+0.051, +0.150] (P=1.0);
BiLSTM +0.185 [+0.131, +0.238] (P=1.0); Morfessor tuned −0.258 [−0.326, −0.130] (P=0.0).

**Class 1 — PYP-unigram Gibbs** (wall-clock 339 s, 3×52 chains on 18 CPU cores; chain seeds
`20260700 + 1000·chain + fold`). Posterior means: discount d ≈ 0.40 (median over folds),
concentration α ≈ 21. **Convergence target NOT attained:** split-R̂ on the log-joint exceeded
the pre-registered 1.1 in 41/52 folds (median 1.16, max 1.49) at the frozen 1,000-sweep budget
— reported honestly per PREREG; the graded number carries this caveat. Pre-registered sanity
checks: planted-lexicon recovery PASSED; the d=0/fixed-hyper Gibbs control scored in-sample
0.568 vs the Viterbi-MAP DP's in-sample 0.356 — i.e. most of the PYP-vs-DP difference is an
**inference-quality effect (Gibbs + posterior-mean vs hard-EM MAP), not the Pitman–Yor
discount**.

**Class 2 — tiny BiLSTM, supervised** (wall-clock 113 s for 3×52 folds; 8,497 parameters, cap
10,000; graded seed 20260703). Stability seeds: 0.6608 (20260704), 0.6621 (20260705) — the
graded seed is the most conservative of the three; both stability runs also clear
([+0.234, +0.324] and [+0.192, +0.296]). **Memorization flag (pre-committed rule,
train−test > 0.20): FIRES on the graded seed** (train 0.8311 vs test 0.6217, gap 0.2094);
the stability seeds sit below the flag (0.163, 0.153). Disclosure: in the one `"(unknown)"`
fold this class's training pool excludes the held-out inscriptions (Addendum A); dev split and
thresholds are test-blind everywhere.

**Class 3 — Morfessor with tuned prior** (wall-clock 24 s). The test-blind rate-matching rule
selected corpusweight **1.0 — the library default — in 52/52 folds**: within the pre-registered
grid {0.05…50}, no prior setting matches the scribal boundary rate on train streams better than
the default, and held-out performance (0.1564) is statistically indistinguishable from the
published vanilla run (0.1556; the ±0.001 is train-order seeding). The published
"over-segments / not usable" verdict is **inherent, not a prior artifact**; on held-out streams
it in fact under-predicts (cut-rate 0.114), significantly WORSE than random. Reported, not
hidden, per the pre-committed rule.

## 5. Honest read

Two of the three pre-registered classes clear the anchor's bar, but the two clearings mean very
different things, and the difference is exactly the metric artifact this project polices.

Boundary micro-F1 on a corpus whose words are mostly 1–2 signs (base rate 0.406) rewards
over-segmentation: the degenerate "cut every position" strategy scores **0.5773** — above the
published anchor (0.4361) and above the PYP (0.5590). The PYP operates at an 88% cut rate with
precision equal to the base rate; its CI-solid gain over the DP anchor is therefore
**substantially a drift toward the metric's degenerate ceiling under stronger inference, not
additional recovered word-boundary structure** (the d=0 Gibbs control shows the sampler, not
the PY discount, drives the shift). Combined with the failed R̂ target, the correct reading is:
the PYP clears the pre-registered floor but does NOT demonstrate more recoverable structure
than the published DP-unigram. **The published 0.436 stands as the best defensible unsupervised
number.**

The supervised BiLSTM is the only entry that beats the degenerate reference with selective
placements (precision 0.66 ≫ 0.41 at cut-rate 0.36), at 0.62–0.66 micro-F1 across seeds. Being
supervised, it does not extend the unsupervised-induction claim; what it establishes is that
**the scribes' word divisions carry substantial cross-site-predictable regularity — roughly
0.62–0.66 micro-F1 worth, versus the 0.436 the unsupervised anchor captures** — i.e. the
published positive is a real lower bound with sizable headroom, now quantified. The graded-seed
memorization flag (0.209 > 0.20, pre-committed) tempers the point estimate; the stability seeds
(0.66, unflagged) suggest the flag is borderline rather than structural.

Morfessor's failure is inherent, closing the "tuned priors would rescue it" objection.

For a TACL revision, the actionable items are: (a) report the degenerate all-boundaries
reference (0.577) next to the published 0.436 — it contextualizes boundary micro-F1 on
short-word corpora and pre-empts the over-segmentation objection the PYP result makes concrete;
(b) optionally cite the supervised probe as the measured headroom of the segmentation signal.
Neither changes any published number. The identifiability wall is untouched; nothing here is,
or enables, a sound-value or decipherment claim.

## 6. Confirmations

- No file under `paper/` was read or written.
- The published 0.436 / CI [0.021, 0.099] is untouched (anchor row re-derived only under the
  reconstructed harness, labeled as such, for pairing).
- Frozen-invariant guards not tripped (nothing outside `experiments/segmentation_extension/`
  and `docs/revision-queue/` was modified; full paper freeze intact).
- Every pre-registered class is reported regardless of outcome; no post-hoc model or
  hyperparameter was added after any result was seen.
- One post-hoc quantity appears above and is labeled as such: the degenerate all-boundaries
  reference (0.5773). It is a diagnostic that *weakens* an apparent positive (the PYP), selects
  no model, and grades nothing — disclosure, not fishing.
