# D1 — Multi-view latent model of anonymous relative classes on Linear A

**Task.** Combine ONLY independently-audited channels into a single latent multi-view model of Linear A
signs (with explicit missing-channel handling), then measure which channels carry signal on LA versus
which are null. Latent classes stay **anonymous** — no phonetic value is assigned to any class.

**Non-circularity.** Every model input is a pure distributional/structural statistic over sign identities.
Known LB syllabic values (parsed from the conventional transliteration of each sign) are used **only** as
an external grading benchmark, never as a model input. Seed 20260708.
Script `scripts/d1_multiview.py`; data `data/D1_multiview.json`.

## Graded sign set
54 clean CV/V syllabograms with LA frequency ≥ 8 (of 259 distinct GORILA-word sign types).
Vowel counts A16 / E11 / I10 / U12 / O5; **only 5 pure-vowel signs** (A E I O U). The tiny pure-vowel
count is itself a power limit on the C/V contrast (below).

## Channels and their measured LA signal

Benchmark A = 5-way **vowel-identity** recovery (mean one-vs-rest 5-fold CV-AUC; chance 0.5), with a
label-permutation p. Benchmark B = **C/V** contrast (pure-vowel sign vs consonantal). Each channel is
graded **pre and post frequency-residualization** (every feature regressed on log-frequency) so a
frequency artifact is exposed. `vResid` / `CVresid` are the post-residualization AUCs.

| Channel | prior (wave 1–2) | cov | vowel-AUC | perm p | vResid | C/V-AUC | C/V p | verdict |
|---|---|---|---|---|---|---|---|---|
| **MORPHOLOGY** (affixation) | LA's real axis, word-INITIAL | 1.00 | **0.634** | 0.004 | 0.412 | 0.861 | 0.105 | SIGNAL → **frequency artifact** |
| **FREQUENCY** (log-freq) | nuisance/confound | 1.00 | 0.587 | 0.002 | 0.335 | 0.237 | 0.400 | SIGNAL → **is** the confound |
| POSITION | wave-1 freq-confounded (REFUTED) | 1.00 | 0.502 | 0.172 | 0.538 | 0.857 | 0.085 | **NULL** |
| SITE (provenance) | — | 1.00 | 0.484 | 0.168 | 0.364 | 0.674 | 0.535 | **NULL** |
| FORMULA (admin slots) | — | 1.00 | 0.396 | 0.621 | 0.464 | 0.833 | 0.152 | **NULL** |
| SUBSTITUTION (long-frame graph) | validated on LB, weak on LA | **0.574** | 0.344 | 0.645 | 0.316 | 0.262 | 0.513 | **NULL / UNDERPOWERED** |
| SHAPE (SigLA) | F1: circular, capped ≤0.75 | 1.00 | — | — | — | — | — | **CAPPED, not value-gradable** |

### Reading the table
- **No channel carries a frequency-robust phonetic (vowel-identity) signal on LA.** The only two
  channels with a nominally significant vowel-AUC — MORPHOLOGY (p=0.004) and FREQUENCY (p=0.002) —
  **both collapse to chance-or-below under frequency residualization** (0.634→0.412; 0.587→0.335).
  This is the exact wave-1 mechanism (a distributional statistic tracks log-frequency, and frequency
  weakly tracks vowel because high-frequency admin signs are vowel-skewed), now shown to also drive the
  affixation channel's apparent value signal. MORPHOLOGY's genuine LA structure is **word-initial
  affixation** — real, but not the phonetic vowel it superficially separates.
- **POSITION is null** on vowel identity (0.502, p=0.17) — a clean independent reconfirmation of the
  wave-1 "position→C/V is a frequency artifact" refutation.
- **The C/V column looks strong (0.83–0.88) but is not significant** under the correct permutation null
  (which 5 of 54 signs you call "vowels"): min p across channels = 0.085 (POSITION), fused = 0.058.
  It rests on only 5 pure-vowel signs and **is** the already-REFUTED wave-1 position→C/V contrast; it is
  reported for transparency and **not re-credited**.
- **SUBSTITUTION is missing on 43% of graded signs** (coverage 0.574) and scores below chance where
  present — consistent with wave-2's "underpowered on LA" finding (max long-frame support 3 vs LB's 98).
- **SHAPE** is present at full coverage but its only calibration (F1) is circular (the grade is an
  LB-homophony judgment = the value it should predict); capped ≤0.75 and excluded from value grading.

## Fused latent multi-view model
Core fusion over POSITION + SUBSTITUTION + MORPHOLOGY + FORMULA + SITE (FREQUENCY and SHAPE excluded as
confound/capped). **Missing-channel handling:** each view standardized on its present rows, absent signs
imputed to the view mean (0 after standardization), plus an **explicit per-view present/absent indicator
column** carried into the fused matrix (23 cols = 18 feature + 5 mask). PCA (SVD) → 4 components for 80%
variance (explained var 0.332/0.236/0.169/0.080) → KMeans(6) anonymous classes.

- **Fused vowel-identity AUC = 0.538, perm p = 0.096** (not significant); residualized 0.450. The
  multi-view fusion **does not recover phonetic vowel classes**.
- **Anonymous latent classes vs benchmark:** vs vowel partition adjusted-MI 0.046, perm p = 0.158; vs
  C/V partition adjusted-MI 0.031, perm p = 0.138. **Both null** — the latent classes are real anonymous
  structure but do not align with any phonetic-value partition beyond chance.
- Fused C/V-AUC 0.882 (perm p 0.058) — same 5-sign-limited, non-significant, already-refuted contrast.

The six anonymous classes (LATENT_00…05) are recorded in `data/D1_multiview.json` for provenance; they
are **not** labelled with any phonetic value, and by the AMI test they carry no recoverable value content.

## Which channels carry signal on LA vs are null (bottom line)

| status | channels |
|---|---|
| **frequency artifact** (nominal vowel signal, collapses on residualization) | MORPHOLOGY, FREQUENCY |
| **null** on vowel identity | POSITION, SITE, FORMULA |
| **null + underpowered / high-missing** | SUBSTITUTION |
| **capped, not value-gradable** (circular) | SHAPE |
| **real but anonymous** (structure with no recoverable value) | MORPHOLOGY word-initial affixation; the 6 fused latent classes |

**Verdict: `MULTIVIEW_NO_VALUE_RECOVERY`.** Fusing all independently-audited channels — with correct
missing-channel handling — recovers **no** frequency-robust, permutation-significant phonetic signal on
Linear A. Every channel that separates the vowel benchmark does so via frequency; the multi-view latent
model's anonymous classes do not align with vowel or C/V partitions beyond chance. Highest earned layer
stays **L2/L3 anonymous relative structure**; no transfer licence earned; **no phonetic value assigned**.
This corroborates waves 1–2 by an independent, multi-channel route: the value layer for LA is closed not
by any single failed detector but by the convergent nullity of every audited channel and their fusion.
