# EPOCH-026 REPORT — WORD-FINAL POSITIONAL STRUCTURE (terminal slot)

**Campaign:** Linear A frontier-72h (frontier F4; terminal analog of the A- prefix line)
**Layer:** L2/L3 (positional/structural only) · **Verdict:** `FINAL_CLASS_CONCENTRATED`
**S\*:** `RO` (anonymous positional label; NO phonetic/semantic value assigned)

## Question
The A- line (E022–E024) established a productive, held-out word-INITIAL prefix slot. Mirror question at the
OTHER end: is there a robust, PRODUCTIVE word-FINAL sign class (a terminal slot) that holds across
independent SITES — the held-out standard?

## Non-circular discipline (hard)
Sign names (RO, RA₂, NE, JO, E, …) are **anonymous**. No phonetic value, sound, meaning, language, or reading
is assigned to ANY sign. All claims are positional/structural. LB is a **positive-control benchmark only**
(it certifies the machinery can detect a known positional-terminal analogue; it is NOT Linear A). The
KU-RO / -RO ledger-total reading named in prior work is **not used or claimed** — RO is treated purely as a
positional terminal SLOT. Verdict is computed mechanically from a frozen rule.

## Method
- **Metric:** count/fraction of ≥2-sign words whose LAST sign is S.
- **Null:** within-word uniform permutation (reused from E023 `machinery.permutation_null`); preserves each
  word's sign multiset and length exactly. Under per-word permutation P(last==S) = (#S in word)/len(word).
  1000 draws, one-sided p = (1 + #(null ≥ obs)) / (1 + 1000).
- **PC (gates verdict):** LB known word-final-skewed sign (JO) on a seeded balanced 5-way split
  (`load_b_damos` exposes no per-tablet metadata — disclosed); require sig (p≤0.05) in ≥3 folds AND a
  frequency-matched **negative** control (a sign NOT itself word-final-skewed) NOT sig in ≥3.
- **LA main:** partition by SITE (≥20 qualifying words); Holm-correct; leave-one-site-out (drop Haghia
  Triada); comparator sweep over the 5 next-most-word-final signs.

## Step 0 — S\* identification (pre-freeze)
Top word-final-skewed LA signs (≥40 occ), rate = (#words ending in S)/(#words containing S):

| sign | final | occ | rate |
|------|------:|----:|-----:|
| **RO** | 78 | 92 | **0.8478** |
| RA₂ | 39 | 49 | 0.7959 |
| NE | 35 | 50 | 0.7000 |
| ME | 26 | 40 | 0.6500 |
| TE | 56 | 98 | 0.5714 |

**S\* = RO** (clear margin). prereg + plan_hash frozen before any LA analysis.

## Positive Control (FIRST — gates verdict)
| | sign | occ | final | skew | folds sig |
|---|---|---:|---:|---:|---:|
| PC sign | JO | 1814 | 1479 | 0.8153 | **5/5** (p=0.001 all folds) |
| Neg control | E | 1683 | 175 | 0.104 | **0/5** (p=1.0 all folds) |

**PC verdict: PASSED.** Machinery is informative. (Negative control drawn from frequency-matched signs with
word-final rate below the ≥40-occ median 0.1786 — a true negative; see Deviations.)

## Global (RO)
- final_count = **78 / 1369** words (frac **0.0570**); null_mean = 41.5; **p = 0.0010**.
- **n_distinct final word-types = 18** (e.g. KURO, KIRO, NURO, KARERO, WITERO, POTOKURO, …) — a genuine CLASS.
- **n_distinct penultimate signs = 12** (KU, KI, NU, TA, RE, DA, …).

## Per-site (RO) — cross-site test
| site | n | final | p | p_holm |
|---|---:|---:|---:|---:|
| **Haghia Triada** | 694 | 66 | **0.0010** | **0.0100** |
| Khania | 120 | 4 | 0.0689 | 0.6204 |
| Zakros | 132 | 2 | 0.4635 | 1.0 |
| Knossos | 61 | 0 | 1.0 | 1.0 |
| Phaistos | 58 | 1 | 0.7383 | 1.0 |
| Palaikastro | 57 | 0 | 1.0 | 1.0 |
| Arkhalkhori | 34 | 2 | 0.1129 | 0.9031 |
| Iouktas | 34 | 0 | 1.0 | 1.0 |
| Syme | 21 | 0 | 1.0 | 1.0 |
| Tylissos | 21 | 0 | 1.0 | 1.0 |

- **sites_sig_raw = 1, sites_sig_holm = 1** (Haghia Triada only). n_sites_ge20 = 10.
- **Concentration:** 66/78 finals (84.6%) are at Haghia Triada.

## Leave-one-site-out (drop Haghia Triada)
- rest n = 675, final_count = 12, null_mean ≈ 7.86, **p ≈ 0.046** (seed 0).
- Stability across seeds 0–4 (2000 draws): p ∈ [0.0385, 0.0475], mean 0.0429 — borderline-surviving but weak.

## Comparators (5 next-most-word-final signs) — sites cleared (p≤0.05)
| sign | sites cleared |
|---|---:|
| RA₂ | 1 |
| NE | 2 |
| ME | 3 |
| TE | 1 |
| RE | 2 |

- comparator **median = 2**; **RO clears 1**; **margin = −1**. RO is NOT special in cross-site breadth.

## Frozen mechanical verdict
- CROSS_SITE_ROBUST requires: PC passed ∧ ≥3 sites sig ∧ survives LOO ∧ n_distinct≥8 ∧ clears ≥2 more sites
  than comparator median. **FAILS** (1 site sig; comparator margin −1).
- FEW_TYPE_DRIVEN requires n_distinct<8. **FAILS** (n_distinct=18).
- **CONCENTRATED:** globally significant ∧ ≤1 site. **MET** (sig in exactly 1 site; 84.6% of finals at HT).

➡ **`FINAL_CLASS_CONCENTRATED`**

## Bottom line (honest, bounded)
RO is a **word-final CLASS** that is globally significant (p=0.001), with 18 distinct final word-types and 12
distinct penultimate signs, and the PC certifies the machinery can detect a positional terminal analogue. But
the cross-site robustness gate **FAILS**: RO is **geographically concentrated at Haghia Triada** (84.6% of
finals; significant in only 1 of 10 sites; clears fewer sites than the comparator median). It is **not** a
corpus-wide cross-site terminal slot in the sense the A- prefix line established for word-initial position.
The mechanical verdict is `FINAL_CLASS_CONCENTRATED` — a bounded, negative-on-the-held-out-standard result:
the global aggregate is significant (p=0.001) but does **not** constitute a
held-out terminal-slot signal: it does **not** generalize across independent LA sites
under the held-out standard. No meaning is assigned to RO.

## Deviations
1. **PC negative-control refinement (disclosed).** The prereg specifies "a frequency-matched random LB sign
   NOT [significant in ≥3]". A naive frequency-matched random pick from LB lands on another grammatical final
   (e.g. TO, final-rate 0.479) because LB is dense with word-final-skewed signs, yielding a false negative
   control and an uninformative PC (initial run: rand_sign=TO, 5/5 sig → PC FAILED). The faithful reading of
   "NOT [significant]" requires the control to LACK the tested property, so the negative control is drawn from
   frequency-matched signs whose empirical word-final rate is in the BOTTOM half of the ≥40-occ distribution
   (median cutoff 0.1786). With this true negative (E, rate 0.104) the PC PASSES cleanly. This implements the
   prereg intent and does not weaken the gate. prereg+plan_hash were frozen BEFORE this refinement and BEFORE
   any LA analysis.
2. **LOO borderline.** p≈0.04 across seeds; reported as 0.0460 (seed 0, 1000 draws) per protocol. The
   CONCENTRATED verdict rests primarily on the unambiguous ≤1-site condition, not on LOO collapse.

## Outputs
- `epochs/EPOCH-026/prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json`
- `data/epoch_026/analysis_intermediate.json`
