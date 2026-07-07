# A5 — Degradation Response Surface

**Task.** Degrade opaque Linear B toward Linear A along *separate* axes and measure C/V
recovery (A3-style models) as a function of each: corpus size, hapax rate, site imbalance,
simulated damage (sign dropout), segmentation uncertainty (word merge/split), missing layout,
missing scribe, short sequence length (truncate), and notation loss. Produce the full
response surface plus the two key 2-way interactions, identify collapse axes, and locate
Linear A's actual operating point on each.

**Scripts / data.** `scripts/a5_degradation_surface.py` → `data/A5_surface.json`. Seed
`20260708`. Primary metric = **M1 grouped-by-sign 7-fold logistic CV AUC on all 7 features**
(the Foundry headline, reported 0.835). Secondary = M1 position-only AUC (drop `log_freq`, the
actual distributional channel) and M2 unsupervised GMM AUC (robustness). Per-level
permutation-null 95th-percentile band (n_perm = 200) defines chance; the sign-set is held
**FIXED** (the 77 LB signs at freq ≥ 20 in full LB, 5 vowels) across every degraded cell, so
AUC is comparable — the corpus degrades, the benchmark does not. **Non-circular:** known
LB/LA vowel labels grade the benchmark only, never enter a model.

---

## Headline verdict — the surface is a FLAT, NON-SIGNIFICANT plateau

**`baseline_full_LB`: M1-all AUC = 0.828, null-mean = 0.681, null-95 = 0.908 → p ≈ 0.16.**
The undegraded, full-corpus opaque-LB C/V AUC **does not clear its own permutation-null 95%
band.** This reproduces A3 (perm_p 0.16) and the Foundry's own 0.835 sits at ~the 80th–85th
percentile of the label-shuffle null. **In no cell of the entire surface — 73 degradation
cells across 9 axes plus 32 interaction cells — does M1-all AUC exceed its own null-95.**

Consequence: there is **no significant signal to degrade.** A "degradation response surface"
presupposes a signal that decays; here the response variable is a ~0.83 noise plateau
(frequency-confounded, see below) that drifts in [0.64, 0.89] with sampling and artifacts and
**never becomes significant at any operating point, degraded or not.** The 5-positive
grouped-CV null is very wide (mean 0.68, 95% 0.90) because of orientation freedom + a tiny
positive set; 0.83 lives inside it.

**Linear A's real operating point is OFF the reachable surface (below chance):** measured on
the real LA corpus with the LA pure-vowel benchmark, M1-all = **0.595**, pos = 0.607,
gmm = 0.53, against null-mean 0.70 / null-95 0.917 — i.e. LA sits **below its own null mean.**
No single-axis degradation of LB, and neither tested interaction, reproduces this: every
degraded-LB cell stays ≥ ~0.82. The LB→LA gap (0.83 → 0.60) is therefore **not attributable
to any modeled axis**; it reflects the different benchmark itself (only 4 pure-vowel positives
among 46 LA signs, a genuinely different language, unsegmented long inscriptions).

**Ruling:** `REFUTE` the Foundry symmetry-break claim (not significant even on full opaque LB;
what little the metric shows is a frequency artifact, not phonology) **+ `NO_POWER` at
Linear-A scale.** No transfer licence is earned; the C/V-recovery claim stays at L2.

---

## Per-axis response surface

`collapse?` = whether M1-all AUC ≤ its own null-95 (= inside the chance band = **not
significant**). It reads **YES at every cell**, which is the point: nothing is ever above
chance. Read the columns for the *shape* of the noise and where the frequency artifact leaks.

### 1. Corpus size (word subsample fraction)
| frac | AUC all(±sd) | AUC pos | AUC gmm | null95 | tokens | hapax | mean_len | within chance band |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 0.828±0.0 | 0.778 | 0.706 | 0.908 | 43868 | 0.011 | 3.24 | YES |
| 0.5 | 0.836±0.005 | 0.793 | 0.697 | 0.908 | 21934 | 0.016 | 3.24 | YES |
| 0.25 | 0.838±0.007 | 0.798 | 0.699 | 0.917 | 10929 | 0.048 | 3.22 | YES |
| **0.0968 (LA size)** | 0.856±0.013 | 0.822 | 0.670 | 0.900 | 4258 | 0.085 | 3.24 | YES |
| 0.05 | 0.847±0.027 | 0.832 | 0.638 | 0.900 | 2216 | 0.107 | 3.27 | YES |
| 0.025 | 0.838±0.059 | 0.792 | 0.636 | 0.912 | 1095 | 0.154 | 3.23 | YES |
| 0.0125 | 0.818±0.058 | 0.810 | 0.592 | 0.904 | 552 | 0.132 | 3.25 | YES |

Shrinking the corpus 80× (to well below LA's token count) does **not** collapse M1-all — it
drifts *up* slightly (small-sample AUC bias with 5 positives), with rising variance (sd
0.0→0.06). GMM (the honest unsupervised readout) does decay monotonically 0.706→0.592, but it
starts at chance and ends further into chance. **Size alone is not a collapse axis** for this
metric, and it never made the signal significant.

### 2. Hapax injection (token → fresh-unique-symbol prob)
| inject_p | AUC all(±sd) | AUC pos | AUC gmm | null95 | realized hapax-type-rate | within band |
|---|---|---|---|---|---|---|
| 0.0 | 0.828±0.0 | 0.778 | 0.706 | 0.908 | 0.011 | YES |
| 0.05 | 0.838±0.005 | 0.790 | 0.706 | 0.911 | 0.962 | YES |
| 0.1 | 0.831±0.004 | 0.797 | 0.705 | 0.917 | 0.980 | YES |
| 0.2 | 0.850±0.010 | 0.828 | 0.708 | 0.922 | 0.990 | YES |
| 0.4 | 0.855±0.009 | 0.839 | 0.682 | 0.925 | 0.995 | YES |

Flooding the corpus with hapax context (up to 99.5% hapax types) leaves the benchmark signs'
recovery essentially unchanged — the frequent 77 signs' features are robust to unique-symbol
noise in their neighbours. **Hapax rate is not a collapse axis.** LA's real hapax-type-rate
(0.071) is trivially inside the benign range.

### 3. Site imbalance (Dirichlet α over 20 synthetic sites; small α = extreme imbalance)
| α | AUC all(±sd) | AUC pos | AUC gmm | null95 | within band |
|---|---|---|---|---|---|
| 1000 (uniform) | 0.841±0.005 | 0.797 | 0.709 | 0.911 | YES |
| 1.0 | 0.833±0.012 | 0.785 | 0.690 | 0.917 | YES |
| 0.3 | 0.834±0.014 | 0.790 | 0.691 | 0.912 | YES |
| 0.1 | 0.846±0.030 | 0.816 | 0.696 | 0.911 | YES |
| 0.03 | 0.840±0.035 | 0.822 | 0.655 | 0.909 | YES |

No effect on M1-all, rising variance only. GMM softens slightly. **Site imbalance is not a
collapse axis.** LA's real site Gini ≈ **0.885** (Haghia Triada ≈ 63% of inscriptions) does not,
by itself, sink C/V recovery in this design.

### 4. Simulated damage — sign dropout (per-token deletion prob)
| drop_p | AUC all(±sd) | AUC pos | AUC gmm | null95 | mean_len | within band |
|---|---|---|---|---|---|---|
| 0.0 | 0.828±0.0 | 0.778 | 0.706 | 0.908 | 3.24 | YES |
| 0.1 | 0.889±0.015 | 0.845 | 0.712 | 0.900 | 2.92 | YES |
| 0.2 | 0.867±0.013 | 0.815 | 0.683 | 0.908 | 2.62 | YES |
| 0.35 | 0.883±0.023 | 0.848 | 0.738 | 0.892 | 2.23 | YES |
| 0.5 | 0.879±0.019 | 0.850 | 0.796 | 0.912 | 1.86 | YES |
| 0.7 | 0.880±0.019 | 0.862 | 0.837 | 0.912 | 1.46 | YES |

Damage makes the metric go **UP**, not down — a clean **artifact**: deleting medial signs
shortens words, which inflates `initial_rate`/`final_rate` separability and (at heavy dropout)
collapses words to length-1, where the readout is pure unigram frequency (GMM climbs to 0.837).
This is a red flag that the metric tracks word-shape/frequency, not a phonological channel.

### 5. Segmentation uncertainty — word merge (words concatenated per pseudo-inscription)
| words/seq | AUC all(±sd) | **AUC pos** | AUC gmm | null95 | mean_len | within band |
|---|---|---|---|---|---|---|
| 1 | 0.828±0.0 | **0.778** | 0.706 | 0.908 | 3.24 | YES |
| 2 | 0.836±0.008 | **0.781** | 0.775 | 0.894 | 6.47 | YES |
| 3 | 0.840±0.004 | **0.779** | 0.799 | 0.914 | 9.70 | YES |
| 4 | 0.832±0.016 | **0.767** | 0.788 | 0.887 | 12.94 | YES |
| 6 | 0.863±0.005 | **0.799** | 0.757 | 0.911 | 19.40 | YES |

Merging words (destroying true word boundaries, LA's real condition) erodes the **position-only**
channel (0.778 → 0.767) while M1-all is held up by `log_freq` (frequency is invariant to
merging). This is the diagnostic that the "position/distribution structure" is weak and
frequency does the lifting. Still never significant.

### 6. Short sequence length — truncate word to first L signs
| max_len | AUC all | **AUC pos** | AUC gmm | null95 | within band |
|---|---|---|---|---|---|
| 99 (none) | 0.828 | 0.778 | 0.706 | 0.908 | YES |
| 6 | 0.825 | 0.778 | 0.708 | 0.908 | YES |
| 5 | 0.836 | 0.792 | 0.708 | 0.908 | YES |
| 4 | 0.844 | 0.789 | 0.731 | 0.908 | YES |
| 3 | 0.872 | 0.825 | 0.758 | 0.892 | YES |
| 2 | 0.839 | 0.792 | 0.758 | 0.890 | YES |
| **1** | 0.869 | **0.225** | 0.906 | 0.904 | YES |

The `max_len=1` row is the smoking gun: with single-sign "words," `AUC-pos` **inverts to 0.225**
(nonsense) while `AUC-all` = 0.869 and `AUC-gmm` = 0.906 — because length-1 reduces the model
to a **unigram-frequency detector** and vowels happen to be high-frequency. The metric's
apparent "success" is a frequency prior, not phonology. **N.B. LA is NOT short** — its
inscriptions average 7.88 tokens (longer than LB words); LA's deficit is segmentation, not
brevity, so LA sits at the benign end of this axis.

### 7. Notation loss (fraction of low-freq TYPES merged to a shared UNK)
| frac merged | AUC all | AUC pos | AUC gmm | null95 | n_types | within band |
|---|---|---|---|---|---|---|
| 0.0 | 0.828 | 0.778 | 0.706 | 0.908 | 89 | YES |
| 0.1 | 0.828 | 0.778 | 0.706 | 0.908 | 81 | YES |
| 0.25 | 0.844 | 0.772 | 0.678 | 0.917 | 68 | YES |
| 0.5 | **0.686** | 0.650 | 0.864 | 0.879 | 46 | YES |
| 0.75 | **0.642** | 0.644 | 0.528 | 0.871 | 23 | YES |

The **only** synthetic axis that pushes the M1-all point estimate clearly **down** (toward the
null) — but only once ≥ 50% of the inventory is dissolved, which also swallows benchmark
consonants and gutts the context. It is **irrelevant to LA**, whose notational resolution
(85 types) ≈ LB's (89): LA sits at ≈ 0 on this axis.

### 8–9. Missing layout / missing scribe — NULL AXES
The A3 C/V channel uses only intra-sequence distributional features (`initial_rate`,
`final_rate`, `mean_pos`, `lone_rate`, `lnbr_ent`, `rnbr_ent`, `log_freq`). **Layout and scribe
are not inputs**, so removing them is the identity transform — AUC-all/pos/gmm =
0.828/0.778/0.706 with vs without, exactly. LA lacks both channels, but they never contributed
to this metric, so their absence costs nothing here (and, conversely, cannot be leaned on).

---

## Key 2-way interactions

### size × sequence-length (M1-all AUC grid)
| frac \ max_len | 99 | 4 | 3 | 2 |
|---|---|---|---|---|
| 1.0 | 0.828 | 0.844 | 0.872 | 0.839 |
| 0.25 | 0.827 | 0.833 | 0.861 | 0.840 |
| **0.0968 (LA)** | 0.836 | 0.884 | 0.873 | 0.882 |
| 0.05 | 0.854 | 0.846 | 0.845 | 0.850 |

### size × hapax (M1-all AUC grid)
| frac \ inject_p | 0.0 | 0.1 | 0.2 | 0.4 |
|---|---|---|---|---|
| 1.0 | 0.828 | 0.839 | 0.850 | 0.854 |
| 0.25 | 0.842 | 0.871 | 0.847 | 0.861 |
| **0.0968 (LA)** | 0.838 | 0.858 | 0.825 | 0.867 |
| 0.05 | 0.885 | 0.849 | 0.870 | 0.847 |

**No synergistic collapse.** Both grids stay in [0.82, 0.885] and every cell remains inside its
null band (null-95 ≈ 0.89–0.94). Compounding small size with short/hapax-heavy corpora does
not drive the metric toward LA's real 0.60. There is no interaction that manufactures — or
destroys — a signal, because there is no signal.

---

## Where does Linear A actually sit? (measured, not extrapolated)

| axis | LA operating value | reachable by degrading LB? | collapses M1-all in LB? |
|---|---|---|---|
| corpus size | 4,245 tok = **0.097×** LB | yes (tested to 0.0125×) | **no** |
| hapax type rate | **0.071** (LB 0.011) | yes (tested to 0.995) | **no** |
| site imbalance | Gini **0.885** | yes (α→0.03) | **no** |
| damage / dropout | substantial (unquantified; silver strips masks) | yes (to 0.7) | **no** (artifact ↑) |
| segmentation | **unsegmented** (real deficit) | yes (merge to 19 tok/seq) | **no** (pos-only ↓ only) |
| seq length | **7.88** (LONGER — benign end) | yes | **no** |
| notation loss | ≈ 0 (85 vs 89 types) | yes | only ≥0.5 (irrelevant to LA) |
| layout / scribe | absent | identity (not an input) | **no effect** |

**Measured LA C/V recovery on its own benchmark: M1-all 0.595, pos 0.607, gmm 0.53; null-mean
0.70, null-95 0.917.** LA is at/below chance and **cannot be reached by degrading LB along any
tested axis or pair** (all degraded-LB cells ≥ ~0.82). The LB(0.83)→LA(0.60) drop is not an
axis effect — it is the different, smaller, genuinely-foreign benchmark (4 pure-vowel
positives among 46 signs).

---

## Which axes cause collapse?

- **None** collapses a *real* signal, because M1-all is never significant (it is a
  frequency-confounded ~0.83 plateau inside a wide 5-positive null).
- Of the synthetic axes, **only `notation_loss ≥ 0.5`** drives the point estimate below ~0.70
  — and that regime is off LA's map.
- **`damage/dropout` and `truncate→1` move the metric UP as an artifact** (word-shortening →
  frequency detector), exposing that the "position/distribution" story is largely `log_freq`.
- LA's real distinguishing conditions (0.097× size, unsegmented, Gini 0.885) each individually
  leave M1-all ≥ 0.82 in LB, so **the LA null is not a "1.7× below power" degradation of a live
  signal** — it is the absence of the signal on a different benchmark.

## Compliance

Articles VII (search receipt — full grid, all axes/levels reported, no cherry-pick), VIII
(effective_n — 5-positive grouped-CV null carried at every cell), IX (information budget —
metric shown against its permutation-null band throughout), XII (no grading a target by the
rule that made it — benchmark held fixed, labels never a model input). Claim layer stays **L2**;
**no phonetic/LEXICAL transfer licence earned** (SEMANTIC+ remains NOT_AUTHORIZED). Verdict:
**REFUTE + NO_POWER**, appended (never overwrites the Foundry record; supersedes its power
interpretation).
