# A2 — Multiplicity Audit of the Foundry position→C/V symmetry-break result

**Constitution v2.2, Art. VII (complete search receipt) / VIII (effective_n, not raw_n) / XII (no grading a
target by the rule that created it).**
Script: `scripts/a2_multiplicity.py` (imports the A1 primitives so both tasks share ONE implementation).
Data: `data/A2_multiplicity.json`. Seed `20260708`. All numbers below are **measured**, not asserted.

## The question A1 deferred

A1 proved the three headline numbers reconstruct *exactly*: single-feature position (`initial_rate`) AUC
**0.744** (perm_p 0.035), 7-feature 7-fold CV AUC **0.835** (perm_p 0.01). A2 asks the honesty question:
**was that significance corrected for the search that produced it?** It was not. Below, each degree of freedom
is enumerated, then the corrected significances are computed.

Two statistically distinct objects must be kept apart, and the audit reaches **opposite** verdicts on them:

| object | what its reported p covers | corrected verdict |
|---|---|---|
| **(I)** single-feature "position is the best symmetry breaker", p=0.035 | ONE feature, no correction for choosing it as best-of-family | **DOWNGRADED / does not survive** |
| **(II)** 7-feature CV perm_p=0.01 | label-permutation through the *entire* 7-fold fit | **honest wrt overfitting; survives — but is a frequency prior, not positional structure** |

---

## 1. Selection degrees of freedom (what was effectively tried)

| # | DOF | alternatives effectively available | how counted |
|---|---|---|---|
| 1 | **feature-family / channel** — `initial_rate` (POSITION) reported as THE single best symmetry breaker | **7** computed distributional features; **13** atlas channels nominal; **2** internal single-feature-computable atlas channels now (POSITION, PHONOTACTICS) | the 7 features are the concrete search that produced "position is best"; the 13-channel `symmetry_breaking_atlas.json` is the nominal family |
| 2 | **freq≥20 inventory threshold** | ≥5 (grid 10/15/20/25/30; the cut is a continuous DOF) | inventory sizes: 80/78/77/72/69 signs |
| 3 | **7-fold + seed** | fold-count ∈ {5,7,10}; seed ∈ {20260708,1,2,3} | the CV perm null re-integrates label noise but not the *choice* of fold/seed |
| 4 | **model family** | ≥3 (logreg / LDA / single-threshold / tree) | logreg's perm null re-fits the *same* model, so it is honest wrt overfitting; model *selection* is uncorrected |
| 5 | **analogue choice** | ≥2–3 readable syllabaries (Linear B, Cypriot Greek, …) | only LB has a loader in scope; folded in analytically, not empirically |

A fully-crossed internal-only garden of forking paths is on the order of **7 × 5 × 3 × 4 ≈ 420 configs** (before
model family / analogue). The principled correction is not this product but the **best-of-K permutation nulls**
below, which *re-select the winner under every permutation*.

---

## 2. (I) The single-feature "position" claim does NOT survive multiplicity

### 2a. Per-feature family (77-sign integer inventory — the correct set per A1)

Single-feature AUC and label-permutation p (n=2000) for **every** feature, with Holm and BH-FDR over the family:

| feature | AUC | \|AUC−0.5\| | perm_p (1-sided) | perm_p (2-sided) | **Holm** (2-sided, ×7 family) | **BH-FDR q** |
|---|---|---|---|---|---|---|
| **log_freq** | **0.878** | 0.378 | **0.0015** | **0.0025** | **0.0175 ✔** | **0.0175 ✔** |
| **rnbr_ent** | 0.800 | 0.300 | 0.0140 | 0.0275 | 0.165 ✗ | 0.0963 ✗ |
| **initial_rate (POSITION)** | 0.744 | 0.244 | **0.035** | 0.072 | **0.36 ✗** | **0.168 ✗** |
| mean_pos | 0.319 | 0.181 | 0.9115 | 0.1864 | 0.7456 | 0.3262 |
| lnbr_ent | 0.564 | 0.064 | 0.3348 | 0.6672 | 1.0 | 0.9341 |
| final_rate | 0.517 | 0.017 | 0.4443 | 0.9105 | 1.0 | 1.0 |
| lone_rate | 0.500 | 0.000 | 1.0 | 1.0 | 1.0 | 1.0 |

**Two mechanical findings, both damaging to the WP1 headline:**

1. **Position is not the best symmetry breaker — it is third.** `log_freq` (AUC 0.878) and `rnbr_ent`
   (AUC 0.800) both beat `initial_rate` (0.744). The claim "position was the single best symmetry-breaker"
   (atlas note; WP1 framing) is **false** on its own numbers. The best channel is *frequency*.
2. **`initial_rate` survives no correction.** Bonferroni over the 7-feature family: 0.035 × 7 = **0.245**.
   Over the 13 nominal atlas channels: **0.455**. Holm-adjusted (two-sided) = **0.36**. BH-FDR q = **0.168**.
   Every family-wise / FDR correction leaves position **non-significant** at α=0.05.

The *only* feature that survives family-wise correction is **`log_freq`** (Holm 0.0175, BH q 0.0175) — and
`rnbr_ent` does not (Holm 0.165). So after correction, the surviving symmetry-breaking channel is
**log-frequency**, a typological prior (vowels are high-frequency), **not** word position.

> On the 74-sign explog inventory the Foundry actually used for WP3, `initial_rate` is AUC 0.759, one-sided
> p 0.027 — still well inside the family it must be corrected against; nothing changes.

### 2b. End-to-end best-of-K permutation null (re-selects the winner every permutation)

Under each permutation the best (channel[/threshold]) is **re-selected** by |AUC−0.5| and compared to the
observed best. This is the principled search-adjusted p (K=1000):

| search space | observed best config | obs stat | **search-adjusted p** | null best p95 |
|---|---|---|---|---|
| channel only (7 feats), fixed freq≥20 | **log_freq**, AUC 0.872 | 0.3725 | **0.023** | 0.336 |
| channel × threshold (7 feats × 5 cuts) | **log_freq** @thr10, AUC 0.883 | 0.3827 | **0.030** | 0.359 |
| **POSITION subfamily** × threshold | initial_rate @thr20, AUC 0.759 | 0.2594 | **0.163** | 0.323 |

**Reading:** *some* distributional channel survives an honest best-of-search at p≈0.02–0.03 — but the winner is
**frequency**, not position. Restricting the search to the **position subfamily** (initial/final/mean_pos/lone),
the search-adjusted p is **0.163 — not significant.** The position channel does not clear 0.05 once its own
sub-feature/threshold search is honestly paid for.

---

## 3. (II) The 7-feature CV perm_p=0.01 is honest — but it is a frequency prior, not positional structure

### 3a. The label-permutation p is legitimate wrt overfitting

`perm_p = 0.01` permutes the C/V labels through the **entire** 7-fold refit (200 nulls), recomputing pooled
out-of-fold AUC each time. That is the correct test for overfitting/CV optimism, and A1 reproduced it exactly
(0.01 on both the 74- and 77-sign inventories). **This survives** — it is *not* the uncorrected object that (I)
is. It does **not**, however, cover the *config search* (threshold / fold-count / seed / model / analogue).

### 3b. Best-of-selection CV over the config grid (re-selects the best config every permutation)

18 configs = thresholds{15,20,25} × folds{5,7,10} × seeds{20260708,1}, K=200. Under each label permutation the
**best CV AUC across all 18 configs** is re-selected and compared to the observed best-of-grid:

- observed best-of-grid CV AUC = **0.8485** (thr25 / 5-fold / seed 1)
- **search-adjusted p = 0.0299** (null best-of-grid mean 0.55, p95 0.81)

So the multi-feature CV result **survives** even after paying for the threshold/fold/seed search. The label
still carries recoverable structure the classifier finds out-of-fold.

### 3c. …but the surviving signal is FREQUENCY, not relative phonology (A1 ablation, reproduced exactly)

| feature subset | CV AUC (74) | CV AUC (77) |
|---|---|---|
| all 7 | 0.835 | 0.825 |
| **log_freq only** | **0.838** | 0.794 |
| minus log_freq | 0.783 | 0.761 |
| **position only** (init/final/mean_pos) | **0.67** | **0.586** |

`log_freq_only ≥ all-features`: the single most predictive input is **how often a sign occurs**. Strip
frequency and the CV AUC falls to 0.78; the purely **positional** structure is **0.586–0.67**, barely above the
0.5 floor on the correct 77-sign set. The classifier is re-discovering the typological universal *vowels are
frequent* — external prior knowledge, not corpus-internal *relative phonology*.

---

## 4. Verdicts (mechanical)

| claim | corrected verdict |
|---|---|
| single-feature POSITION AUC 0.744 survives Bonferroni ×7 | **NO** (0.245) |
| … survives Bonferroni ×13 atlas | **NO** (0.455) |
| … survives Holm / BH-FDR over the feature family | **NO** (0.36 / 0.168) |
| … survives position-subfamily best-of-K search | **NO** (p=0.163) |
| "position is the single **best** symmetry breaker" | **FALSE** — log_freq (0.878) and rnbr_ent (0.800) beat it |
| best-of-K over ALL channels is significant | YES (p≈0.02–0.03) — **but the winner is frequency, not position** |
| 7-feature CV label-perm p=0.01 is honest wrt overfitting | **YES** |
| 7-feature CV survives best-of-selection config search | **YES** (p=0.030) |
| the CV AUC is evidence of positional / relative-phonological structure | **NO** — it is a frequency prior (log_freq_only ≥ all; position-only 0.586–0.67) |

### Bottom line

- **DOWNGRADE the single-feature "position breaks the C/V symmetry" claim.** Its p=0.035 was never corrected
  for the feature-family / atlas-channel search that selected it; it survives **no** multiplicity correction
  (Bonferroni, Holm, FDR, or a position-subfamily best-of-K), and position is not even the best channel.
- **The 7-feature CV result is statistically real** (label-perm p=0.01 honest; survives config-search at
  p=0.03) **but is mis-described.** What survives is a **typological frequency prior** ("vowels are frequent"),
  which earns **no** relative-phonology / positional licence. The genuinely position-driven signal is 0.586–0.67
  and does not survive correction.
- **Net effect on the programme:** the symmetry-breaking atlas's headline — "internal *relative* channels are
  REAL (position AUC 0.744, p=0.035)" — is not supported after multiplicity correction. The only corrected-
  significant internal channel is frequency, which does not reduce the value equivalence classes in any
  phonetically-loaded way. This is a bounded **downgrade**, not a claim that no structure exists: `rnbr_ent`
  (right-neighbour entropy, a phonotactic channel) is suggestive (AUC 0.800, uncorrected p 0.028) but does not
  clear family-wise correction on this corpus, and is the natural target for a pre-registered, single-channel
  follow-up rather than a post-hoc best-of-family pick.

*(All figures generated by `scripts/a2_multiplicity.py`; raw values in `data/A2_multiplicity.json`.)*
