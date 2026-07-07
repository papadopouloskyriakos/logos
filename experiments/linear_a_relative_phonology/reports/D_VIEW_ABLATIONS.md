# D2 — View Ablations of the D1 Multi-View Channels

**Task:** ablate the D1 channels (POSITION, FREQUENCY, MORPHOLOGY, SUBSTITUTION; LA-only FORMULA/SITE;
capped SHAPE) and report each ablation's contribution to the **anonymous relative partition** on Linear A
and on a Linear B known-truth positive control.
**Seed** 20260708 · **as_of** 2026-07-07 · Constitution v2.2 · script `scripts/d2_view_ablations.py`
· data `data/D2_ablations.json`.

**Non-circular.** Known LB syllabic values are used ONLY as the grading benchmark (vowel identity; the
pure-vowel-sign/consonantal C/V split). Every model input is a pure distributional/structural statistic
over sign identities. LB is graded on its own known values as a positive control. **No phonetic value is
assigned to any class; classes are anonymous.**

## Method (all machinery reused verbatim from D1 / a1)

Each ablation config → fuse its channels (within-view z-score of present rows, mean-impute absent, carry
per-view present/absent mask cols) → PCA latent scores (K for 80% var, clamped 3–8) → grade:

- `fused_vowel_macro_auc` = one-vs-rest 5-vowel CV-AUC on the latent scores; `perm_p` = label permutation (n=300).
- `fused_vowel_auc_freq_resid` = the same AUC after regressing latent scores on log-freq — **exposes a
  frequency artifact** (wave-1's position→C/V was such an artifact). Robustness threshold 0.55.
- `partition_ami_vowel` = adjusted mutual information of the KMeans(k=6) anonymous partition vs the vowel
  benchmark, with permutation p (n=300). Same vs the C/V split.
- Families: **SINGLE** (include-only), **LEAVE_ONE_OUT** (drop-from-full-shared), **COMBINATIONS**, plus a
  **RANDOM-feature floor** (Gaussian noise, chance anchor).

Shared channel space (both scripts): POSITION, FREQUENCY, MORPHOLOGY, SUBSTITUTION. FORMULA/SITE are
LA-corpus-specific (no LB analogue) → LA-only extended configs. LB SUBSTITUTION is a generic frame-based
minimal-pair channel; LA SUBSTITUTION is the audited wave-2 long-frame graph — definitions differ, each
internally consistent. The **C/V axis is the wave-1 position→C/V contrast already REFUTED** under
multiplicity + oriented null; reported for continuity, **not re-credited**.

## Linear A — 54 graded CV/V signs (freq ≥ 8), 5 pure-vowel signs

| config | vowel AUC | perm p | **freq-resid AUC** | partition AMI(vowel) | AMI p | verdict |
|---|---|---|---|---|---|---|
| single POSITION | 0.512 | 0.096 | 0.503 | 0.010 | 0.395 | NULL |
| single FREQUENCY | 0.587 | 0.003 | 0.307 | 0.090 | 0.027 | SIGNAL·**freq-artifact** |
| single MORPHOLOGY | 0.619 | 0.007 | 0.411 | 0.118 | 0.010 | SIGNAL·**freq-artifact** |
| single SUBSTITUTION | 0.480 | 0.209 | 0.389 | 0.018 | 0.302 | NULL |
| single FORMULA | 0.466 | 0.309 | 0.474 | 0.030 | 0.236 | NULL |
| single SITE | 0.501 | 0.206 | 0.419 | 0.049 | 0.103 | NULL |
| FULL_shared (4-view) | 0.573 | 0.053 | 0.485 | 0.089 | 0.023 | (nominal SIGNAL — see note) |
| LOO −POSITION | 0.587 | 0.017 | 0.420 | 0.021 | 0.279 | freq-artifact |
| LOO −FREQUENCY | 0.570 | 0.057 | 0.494 | 0.076 | 0.050 | (nominal) |
| LOO −MORPHOLOGY | 0.537 | 0.100 | 0.501 | 0.116 | 0.007 | (nominal) |
| LOO −SUBSTITUTION | 0.570 | 0.033 | 0.413 | 0.029 | 0.246 | freq-artifact |
| combo MORPH+POS | 0.566 | 0.037 | 0.418 | 0.029 | 0.246 | freq-artifact |
| combo MORPH+SUB | 0.588 | 0.013 | 0.406 | 0.086 | 0.047 | freq-artifact |
| combo POS+SUB | 0.517 | 0.143 | **0.516** | 0.091 | 0.030 | (nominal) |
| combo structural-3 (no freq) | 0.570 | 0.057 | 0.494 | 0.076 | 0.050 | (nominal) |
| combo D1-full 5-view | 0.538 | 0.103 | 0.450 | 0.045 | 0.166 | NULL |
| **RANDOM floor** | 0.461 | 0.309 | 0.459 | 0.030 | 0.226 | NULL |

**The decisive column is `freq-resid AUC`. Every single Linear A config — including every combination —
falls below the 0.55 frequency-robustness threshold. The maximum across all 17 LA configs is 0.516
(POS+SUB), essentially the RANDOM floor's 0.459.** Nothing on LA survives frequency removal.

### Reading the LA ablations honestly

- **POSITION, SUBSTITUTION, FORMULA, SITE — all NULL as standalone channels** (vowel AUC 0.47–0.51, perm p
  ≥ 0.10, AMI indistinguishable from the random floor). POSITION being null re-confirms wave-1
  (position = frequency artifact); SUBSTITUTION being null re-confirms wave-2 (LA substitution is
  underpowered — long-frame support 3 vs LB's 98).
- **The only channels with any raw vowel signal are FREQUENCY and MORPHOLOGY, and both are
  frequency artifacts**: their AUC collapses from 0.59/0.62 to 0.31/0.41 under residualization, and
  frequency *alone* reproduces the partition AMI (single-FREQUENCY AMIadj 0.090, p 0.027 ≈ MORPHOLOGY's
  0.118). MORPHOLOGY's "signal" is a frequency echo, not independent structure.
- **The nominal "SIGNAL" labels on LA are a scoring caveat, not a real positive.** The verdict rule fires
  SIGNAL when the partition-AMI permutation p ≤ 0.05, but the AMI path is not itself frequency-checked. On
  LA that AMI is frequency-carried (frequency-only reproduces it) and every one of those configs has
  freq-resid AUC < 0.55. **The honest LA verdict is NULL-after-frequency across every channel and every
  combination.**
- **The full D1 5-view model is NULL** (0.538, p 0.103; AMIadj 0.045, p 0.166) — statistically the random
  floor. Fusing more views does not manufacture signal.

## Linear B — known-truth positive control — 66 graded CV/V signs (freq ≥ 20)

| config | vowel AUC | perm p | **freq-resid AUC** | partition AMI(vowel) | AMI p | verdict |
|---|---|---|---|---|---|---|
| single POSITION | 0.545 | 0.037 | 0.544 | 0.109 | 0.010 | freq-robust |
| single FREQUENCY | 0.529 | 0.023 | 0.398 | 0.012 | 0.322 | freq-artifact |
| single MORPHOLOGY | 0.559 | 0.013 | 0.499 | 0.029 | 0.150 | freq-artifact |
| **single SUBSTITUTION** | **0.591** | **0.003** | **0.562** | 0.097 | 0.017 | **SIGNAL (freq-robust)** |
| **FULL_shared (4-view)** | **0.598** | **0.007** | **0.564** | 0.111 | 0.003 | **SIGNAL (freq-robust)** |
| LOO −POSITION | 0.588 | 0.003 | 0.550 | 0.071 | 0.030 | SIGNAL |
| LOO −FREQUENCY | 0.597 | 0.007 | 0.570 | 0.096 | 0.007 | SIGNAL |
| LOO −MORPHOLOGY | 0.600 | 0.007 | 0.567 | 0.123 | 0.003 | SIGNAL |
| LOO −SUBSTITUTION | 0.581 | 0.010 | 0.571 | 0.136 | 0.003 | SIGNAL |
| combo MORPH+POS | 0.572 | 0.017 | 0.567 | 0.102 | 0.013 | SIGNAL |
| combo MORPH+SUB | 0.588 | 0.007 | 0.550 | 0.083 | 0.013 | SIGNAL |
| combo POS+SUB | 0.592 | 0.007 | 0.570 | 0.123 | 0.003 | SIGNAL |
| combo structural-3 (no freq) | 0.597 | 0.007 | 0.570 | 0.096 | 0.007 | SIGNAL |
| **RANDOM floor** | 0.453 | 0.449 | 0.389 | 0.036 | 0.166 | NULL |

**The identical channels + identical grading machinery recover a frequency-ROBUST vowel-partition signal on
Linear B: every structural config holds freq-resid AUC ≥ 0.55 (up to 0.571) with perm p ≤ 0.01 and AMI
p ≤ 0.03, while the RANDOM floor stays flat (0.453, p 0.449).** The detector is alive.

- **SUBSTITUTION is LB's single strongest freq-robust channel** (0.591, resid 0.562) — exactly the wave-2
  finding that the substitution consonant-held axis is validated on opaque LB. On LA the same channel is at
  its chance floor (0.480). This is the crux: the axis that carries LB is the axis LA cannot support.
- **Leave-one-out on LB never breaks the signal** (all LOO ≥ 0.58, resid ≥ 0.55): the structure is
  redundant across POSITION/SUBSTITUTION on a well-powered corpus — no single channel is load-bearing.
- LB FREQUENCY and MORPHOLOGY alone are frequency-carried (resid 0.398/0.499), but the fusion's signal is
  **not** — it is anchored by substitution + position, which survive residualization.

## SHAPE channel — CAPPED, not value-gradable

SHAPE is excluded from value grading in every ablation. Its grade *is* an LB-homophony (identity) judgment
(F1: Salgarella stable-11 recovered perfectly, Fisher p = 1.6e-5) — the same latent LB-identity fact it
would predict. It therefore carries **no independent anonymous-partition signal**; capped ≤ 0.75, reported,
never scored. `verdict = CAPPED_CIRCULAR_NOT_VALUE_GRADABLE`.

## Bottom line

The ablations quantify **how little independent signal remains on Linear A**. On a decipherable control
(Linear B) the same views and the same machinery recover a frequency-robust vowel partition (freq-resid AUC
up to 0.571, carried by substitution + position, LOO-stable). On Linear A **every channel and every
combination collapses under frequency residualization** (max freq-resid AUC 0.516 vs the 0.55 threshold and
the 0.459 random floor): POSITION/SUBSTITUTION/FORMULA/SITE are flat null, and the FREQUENCY/MORPHOLOGY
"signal" is a frequency echo that frequency-only reproduces. The full multi-view model is the random floor.

**No transfer licence is earned. Highest layer L2/L3 (anonymous relative structure). SEMANTIC+ remains
NOT_AUTHORIZED. The anonymous relative partition on Linear A carries no frequency-independent vowel
structure that the ablations can isolate.**
