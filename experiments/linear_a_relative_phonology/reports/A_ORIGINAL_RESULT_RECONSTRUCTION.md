# A1 — Original Result Reconstruction

**Task:** Independently recompute the Foundry "position → C/V symmetry-break" result from scratch, so a bug
in the Foundry scripts cannot hide inside the audit. Confirm (or refute) the three headline numbers:
single-feature position AUC **0.744**, 7-feature 7-fold CV AUC **0.835**, permutation p **0.01**.

**Verdict:** `REPRODUCED`. All three published numbers reproduce **exactly** with a fully independent
reimplementation. The reconstruction also pins down a previously-undocumented reason WP1 and WP3 grade on
different sign counts (77 vs 74): a floating-point artifact in WP3's frequency threshold. Neither of these is
yet an evaluation of whether the result *survives* proper multiplicity / grouping / Linear-A-scale scrutiny —
that is the job of the later tasks. A1 only establishes that the number under audit is real and correctly
transcribed.

Script: `scripts/a1_recompute.py` (no Foundry import). Data: `data/A1_recompute.json`. Seed `20260708`.

---

## 1. Dataset

- **Corpus:** Linear B DĀMOS Mycenaean transliterations, parsed into **syllabic wordforms** by
  `scripts/cross_script/data.py::load_b_damos()` (loader imported read-only from the main worktree because
  the raw corpus is licensed/gitignored and only materialized there; the loader code is byte-identical to
  this worktree's copy). Only syllabograms survive — logograms, metrograms, numerals and editorial marks are
  rejected at parse time.
- **Unit of analysis:** the **word** (wordform), not the tablet. **n = 13,562** wordforms.
- Each sign is its uppercase phonetic VALUE token (`QE`, `PA`, `A`, …); `*NN` for un-valued numbered signs.

## 2. Sign inventory and the freq≥20 threshold

Features are computed per sign over all 13,562 wordforms; only signs with total frequency **≥ 20** are graded
(rare signs have unstable position statistics). The threshold is where WP1 and WP3 silently diverge:

| | threshold expression | n signs | vowels present |
|---|---|---|---|
| WP1 (`wp1_symmetry_break.py`) | integer `freq >= 20` | **77** | 5 (A E I O U) |
| WP3 (`wp3_cv_recovery.py`) | `math.exp(math.log(freq)) >= 20` | **74** | 5 |

**Finding (mechanical, not opinion):** three signs sit at *exactly* freq = 20 — **`*47`, `*63`, `TA2`** —
and `math.exp(math.log(20))` evaluates to `19.999999999999996 < 20`, so WP3 drops them. This is why the
"same" analysis reports 77 signs in WP1 and 74 in WP3. A clean integer threshold keeps all 77. This is a
transcription/robustness wrinkle, documented here and carried into the sensitivity table below; the later
audit tasks should treat 77 (integer) as the correct inventory.

## 3. C/V labels (grading only — never a model input)

Positive class = the 5 signs whose known Linear B value is a pure vowel: **A, E, I, O, U**. These labels form
the `y` vector used to *score* AUC and to *permute* for the null. They are never fed to the model as a
feature — every feature (below) is a pure distributional statistic over sign identities. This preserves
non-circularity: the classifier never sees a phonetic value on its input side.

## 4. The 7 features (per sign)

Reimplemented in `feature()`:

1. `initial_rate` — P(word-initial | occurs)
2. `final_rate` — P(word-final | occurs)
3. `mean_pos` — mean normalized position `i/(L-1)` (0.5 for length-1 words)
4. `lone_rate` — (# length-1 words = this sign) / freq
5. `lnbr_ent` — Shannon entropy (nats) of the left-neighbour distribution
6. `rnbr_ent` — Shannon entropy (nats) of the right-neighbour distribution
7. `log_freq` — `ln(freq)`

## 5. Model, split, permutation null (all reimplemented independently)

- **Classifier** (`logreg()`): L2-regularized logistic regression, full-batch gradient descent,
  `l2 = 1.0`, `iters = 500`, `lr = 0.3`, features z-score standardized on the full sign set (`standardize()`).
- **AUC** (`auc()`): Mann–Whitney (rank) AUC, ties credited 0.5.
- **Cross-validation** (`cv_auc()`): **7-fold**; folds are shuffled-index-modulo-k (`order = shuffle(range n, seed=20260708)`, fold f = indices with `i % 7 == f`). Out-of-fold scores are pooled and AUC'd once.
- **Single-feature AUC:** raw `initial_rate` ranked against the C/V labels (no model).
- **Permutation p:** relabel the `y` vector (`random.Random(20260708)`), recompute the statistic, repeat;
  `p = (#{null ≥ observed} + 1)/(n + 1)`. Single-feature null `n = 2000`; CV null `n = 200` (each null
  refits all 7 folds). Same seed and fold structure as the observed run.

## 6. Recomputed vs published

| statistic | published | recomputed | match |
|---|---|---|---|
| WP1 single-feature `initial_rate` AUC (77 signs) | 0.744 | **0.744** | ✔ exact |
| WP1 permutation p (n=2000) | 0.035 | **0.035** | ✔ exact |
| WP3 7-feature 7-fold CV AUC (74 signs) | 0.835 | **0.835** | ✔ exact |
| WP3 permutation p (n=200) | 0.01 | **0.01** | ✔ exact |
| WP3 ablation `log_freq_only` | 0.838 | **0.838** | ✔ exact |
| WP3 ablation `position_only` | 0.67 | **0.67** | ✔ exact |
| WP3 ablation `minus_log_freq` | 0.783 | **0.783** | ✔ exact |

**The published numbers are real and correctly reported.** An independent codebase, sharing only the raw
corpus and the documented methodology, lands on the identical values.

## 7. Sensitivity already visible at reconstruction time (flagged for later tasks)

These are not part of the "does it reproduce" verdict, but the reconstruction surfaces two facts the later
tasks must reckon with:

- **The headline 0.835 is a frequency prior, not a position discovery.** The Foundry's own ablation — which I
  reproduce exactly — shows `log_freq_only = 0.838 ≥ all-features = 0.835`, while `position_only = 0.67`.
  The single most predictive input is *how often a sign occurs* (vowels are high-frequency), a typological
  prior, not corpus-internal positional structure. The genuinely position-driven signal is ~0.67.
- **Correcting the freq threshold weakens the structural signal.** On the clean integer 77-sign inventory
  (the correct set): CV AUC 0.835 → **0.825**, `log_freq_only` 0.838 → **0.794**, and crucially
  `position_only` 0.67 → **0.586** (barely above the 0.5 chance floor). The 3 dropped freq-20 signs were
  helping the position story; with them restored, position-only structure is markedly thinner. The
  single-feature `initial_rate` AUC on the 74-sign set is 0.759 (vs 0.744 on 77).

Multiplicity correction, grouped CV, and Linear-A-scale degradation remain to be tested — those are the
downstream tasks. A1's conclusion is narrow and firm: **the number under audit reconstructs exactly.**
