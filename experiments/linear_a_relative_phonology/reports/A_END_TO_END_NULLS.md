# A6 — Complete Null Battery + WP-A Verdict

## VERDICT: `CV_ANALOGUE_REFUTED`

**One-paragraph verdict.** The Foundry "position/distributional structure breaks the C/V symmetry on
opaque Linear B" result does **not** replicate under a proper end-to-end null battery. Its headline
significance (WP3 7-fold CV AUC 0.835, perm_p 0.01; WP1 single-feature 0.744, p 0.035) is an artifact
of two things stacked together: a **one-sided permutation null** (with only 5 vowels among 77 signs, a
*random* labeling reaches oriented AUC ≥ 0.828 about **15%** of the time — `random_cv_labels` p =
**0.146**), and a **frequency confound** (labels permuted *within* their own log-frequency quartiles
still reach the observed AUC **13%** of the time — `frequency_matched_labels` p = **0.130**; i.e. the
"vowel signal" is nothing more than "vowels are the high-frequency signs"). The claim fails every
confound-controlling test simultaneously: (a) the two **independent unsupervised models** do not
replicate it (GMM AUC 0.704 vs its own null-95 0.762; HMM 0.719 vs 0.761 — both *below* their null
bands); (b) **frequency-band grouped CV** collapses it (all-feature AUC 0.658, perm_p 0.125;
position-only **0.481**, i.e. *below chance*); (c) destroying within-word **order** leaves the
all-feature AUC *unchanged* (0.839 ≈ 0.828), proving order carries no signal; and (d) at the **measured
Linear-A operating point** the whole thing degrades to 0.595 against a 0.917 chance band. The only two
nulls it "passes" (`best_of_segmentation` p=0.01, `best_of_seed` p=0.016) use the *directed* AUC and so
merely re-inherit the same one-sided optimism; they correct threshold/seed degrees of freedom, not the
frequency confound or the model. Under the honest **oriented** null the result is not significant even
before multiplicity correction. **REFUTED.**

---

## 1. Best surviving configuration under audit

From A1–A5, the single configuration that survived the naive (Foundry) label-permutation test was:

> **M1 — supervised 7-feature, sign-grouped 7-fold logistic-regression CV on the full DĀMOS Linear B
> analogue** (13,562 wordforms → 77 signs at freq ≥ 20, 5 true vowels). Features
> `[initial_rate, final_rate, mean_pos, lone_rate, lnbr_ent, rnbr_ent, log_freq]`.

Reproduced observed statistic (independent reimplementation, no Foundry import):

| statistic | A6 (directed) | Foundry |
|---|---|---|
| grouped-CV AUC, all 7 features | **0.828** | 0.835 |
| grouped-CV AUC, position-only (6 feats, no `log_freq`) | **0.778** | — |
| single-feature position AUC | 0.744 (A1) | 0.744 |

The complete null battery below is run on this configuration.

---

## 2. Null battery — results

All p-values are `(#null ≥ obs + 1)/(N + 1)`. Label nulls use the **oriented** AUC
(`max(a, 1−a)`) to match a two-sided C/V detector, compared against the **directed** observed AUC —
exactly the honest two-sided comparison A3's `audit_supplement` flagged the Foundry p=0.01 for lacking.

### 2a. Label nulls (true features fixed, permute the C/V label)

| # | null | obs | null mean | null p95 | **p** | reads as |
|---|---|---|---|---|---|---|
| 1 | `random_cv_labels` (uniform, 5-of-77) | 0.828 | 0.679 | 0.903 | **0.146** | **fails**: not significant even before multiplicity |
| 2 | `frequency_matched_labels` (permute within log-freq quartiles) | 0.828 | 0.705 | 0.864 | **0.130** | **fails**: AUC is explained by the frequency location of the vowels |

The true vowels sit in the top frequency quartiles; when fake "vowel" sets are drawn to match that
frequency profile, they reach the observed AUC 13% of the time. There is no C/V structure beyond "vowels
are frequent."

### 2b. Data nulls (TRUE labels fixed, destroy corpus structure, recompute features)

Marginal sign frequency (hence `log_freq`) is preserved by all four shuffles, so the residual AUC after
a shuffle is the pure frequency contribution. `p_pos` / `p_all` = fraction of structure-destroyed
realizations that still reach the observed position-only / all-feature AUC (n=40 each).

| # | null (what it destroys) | all-feat AUC | pos-only AUC | p_all | p_pos |
|---|---|---|---|---|---|
| 3 | `shuffled_sign_positions` (within-word **order**) | 0.839 ± 0.027 | 0.771 ± 0.030 | 0.68 | 0.44 |
| 4 | `shuffled_documents` (global length-matched token reshuffle) | 0.763 ± 0.036 | 0.592 ± 0.068 | 0.073 | 0.024 |
| 5 | `site_preserving_shuffle` (reshuffle within site) | 0.770 ± 0.027 | 0.580 ± 0.052 | 0.024 | 0.024 |
| 6 | `series_preserving_shuffle` (reshuffle within series) | 0.766 ± 0.035 | 0.587 ± 0.066 | 0.049 | 0.049 |

Decisive line: **destroying within-word order (#3) leaves the all-feature AUC essentially unchanged
(0.839 ≈ observed 0.828, p_all = 0.68)** and even leaves position-only within noise (0.771 vs 0.778).
The "positional" story is not carried by order. Only when *co-occurrence* is destroyed (#4–6) does
position-only fall to ~0.58–0.59 (near chance) while all-feature settles at ~0.76–0.77 — the pure
`log_freq` floor. The residual is frequency, not relative phonology.

### 2c. Adaptive selection nulls (permute label, RE-RUN the full selection, take the best AUC)

| # | null (selection set) | obs best | null-best p95 | **p** | survives? |
|---|---|---|---|---|---|
| 7 | `best_of_model` {logistic-CV, GMM, best-single-feature} | 0.878 | 0.908 | **0.129** | **no** |
| 8 | `best_of_segmentation` {freq-thr 15/20/25} | 0.847 | 0.776 | 0.010 | yes* |
| 9 | `best_of_seed` {5 CV seeds} | 0.828 | 0.758 | 0.016 | yes* |

*`best_of_segmentation` and `best_of_seed` use the **directed** AUC statistic and therefore reproduce the
same one-sided-null optimism that inflates the Foundry p=0.01; they correct only the threshold- and
seed-selection degrees of freedom. Under the honest **oriented** null (#1) the same configuration is
p=0.146. `best_of_model` — the one adaptive null that admits the unsupervised orientation freedom —
**fails** (p=0.129), and its "best" 0.878 is a single-feature threshold classifier, not the CV model.

---

## 3. Mechanical decision rule and how it fires

```
REPLICATED     := independent_models_replicate AND frequency_band_grouped_CV_survives
                  AND best_of_{model,segmentation,seed} all p<0.05
                  AND frequency_matched_label_null p<0.05
                  AND position_structure_beyond_order_shuffle
REFUTED        := (NOT independent_models_replicate AND NOT frequency_band_grouped_CV_survives)
                  OR NOT survives_at_measured_LinearA_operating_point
                  OR NOT frequency_matched (frequency fully explains the AUC)
EXPLORATORY_ONLY := survives the naive label permutation but not the adaptive/grouped/confound controls
INCOMPLETE     := otherwise
```

Flags actually measured (α = 0.05):

| flag | value |
|---|---|
| survives naive (oriented) label permutation | **False** (p=0.146) |
| survives frequency-matched label null (structure beyond frequency) | **False** (p=0.130) |
| position structure beyond order-shuffle | **False** (p_pos=0.44) |
| all-feat AUC beyond global freq-shuffle | **False** (p=0.073) |
| survives `best_of_model` | **False** (p=0.129) |
| survives `best_of_segmentation` | True (p=0.010, directed) |
| survives `best_of_seed` | True (p=0.016, directed) |
| independent unsupervised models replicate (M2 **and** M3 > null95) | **False** (0.704<0.762; 0.719<0.761) |
| frequency-band grouped CV survives (A4) | **False** (AUC 0.658, p=0.125; pos-only 0.481) |
| survives at measured Linear-A operating point (A5) | **False** (0.595 < 0.917) |

The REFUTED clause fires on **three** independent grounds simultaneously:
1. `NOT independent_models_replicate AND NOT frequency_band_grouped_CV_survives` — the confound-controlled generalization is dead and no independent model reproduces it;
2. `NOT survives_at_measured_LinearA_operating_point` — collapses below the chance band at LA scale;
3. `NOT frequency_matched` — frequency alone reproduces the AUC.

The result is not merely `EXPLORATORY_ONLY`: it does not even clear the naive oriented label null.

---

## 4. Per-model grouped AUCs (for the record)

| model / grouping | AUC | reference |
|---|---|---|
| M1 logistic, sign-grouped 7-fold, all feats | 0.828 | A3/A4 |
| M1 logistic, sign-grouped 7-fold, position-only | 0.778 | A4 |
| M1 logistic, leave-one-site-out (pooled) | 0.760 | A4 |
| M1 logistic, leave-one-series-out (pooled) | 0.817 | A4 |
| **M1 logistic, frequency-band grouped, all feats** | **0.658** (p=0.125) | A4 |
| **M1 logistic, frequency-band grouped, position-only** | **0.481** (below chance) | A4 |
| M2 GMM (unsupervised) | 0.704 (null95 0.762) | A3 |
| M3 HMM (unsupervised) | 0.719 (null95 0.761) | A3 |
| Measured Linear-A operating point, all feats | 0.595 (null95 0.917) | A5 |

Site- and series-grouped CV *look* significant only because vowels are high-frequency *everywhere*; the
moment the frequency confound is itself the grouping (frequency-band LOGO), generalization vanishes
(0.658 / 0.481). That is the diagnostic separating a genuine positional channel from a frequency prior.

---

## 5. What survives, honestly

- A **frequency prior** on Linear B is real and reproducible: high-frequency signs are more often vowels
  (`log_freq`-only AUC ≈ 0.79–0.84). This is a known typological regularity, not a decipherment signal,
  and it is **not transferable** as a phonetic/relative-phonology licence.
- No claim above **L2 (structure)** is earned. The Foundry's implicit L6/L7 (phonetic) framing —
  "distributional structure breaks the C/V symmetry" as evidence of recoverable relative phonology — is
  **NOT_AUTHORIZED** by this evidence and is downgraded to a frequency observation.

Provenance: `scripts/a6_nulls.py` → `data/A6_nulls.json` (seed 20260708). Cross-work facts read
mechanically from `A3_replications.json`, `A4_grouped.json`, `A5_surface.json`. Known LB vowel values
graded benchmarks only; never a model input.
