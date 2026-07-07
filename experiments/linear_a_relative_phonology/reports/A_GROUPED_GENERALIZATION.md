# A4 — Grouped / leakage-controlled evaluation of C/V recovery on opaque Linear B

**Constitution v2.2** — Art. VII (search receipt), Art. VIII (effective-n, not raw-n),
Art. XII (do not grade a target by the rule that created it), Art. IV/V (claim layers).
Seed 20260708. Corpus: full DĀMOS Mycenaean set, 13,562 syllabic wordforms; canonical unit
= the 77 LB signs with global freq ≥ 20; 5 true vowels {A,E,I,O,U}. **Non-circular:** known LB
vowel values grade the benchmark ONLY; they are never a model input. Script:
`scripts/a4_grouped.py` → data `data/A4_grouped.json`.

## The claim under audit

Foundry WP1/WP3: *"position/distributional structure breaks the C/V symmetry on opaque
Linear B"* — single-feature position AUC 0.744, 7-feature logistic 7-fold CV AUC 0.835. A3's
replication reproduced the number (M1 sign-grouped 7-fold AUC **0.828**) but already flagged
the confound: **logfreq-only AUC 0.838 ≥ all-features 0.828**, i.e. a one-feature typological
frequency prior matches the full model. A4 asks the decisive question A3 left open: **when
related units cannot leak between train and test, and when frequency is explicitly controlled,
does anything survive?**

## Two distinct leakage geometries (both tested)

The classified unit is the **sign**, whose feature vector is *estimated from a corpus*.
"Related units leaking" therefore means two different things, tested separately:

1. **Feature-domain leave-one-group-out** (site / series / formula-family / scribe / chronology
   / document / word-family). The classifier is trained on sign features estimated from the
   **complement** corpus and must recover C/V from sign features **re-estimated on the held-out
   group's corpus alone**. A signal driven by a few documents/scribes/formulae will not transfer.
   Aggregates: pooled AUC (concatenate directed scores across held-out groups) and mean-of-group
   AUC, each vs a label-permutation null (200 shuffles of the 77 sign labels, full procedure rerun).

2. **Sign-unit leave-one-frequency-band-out.** Whole log-frequency bands of *signs* are held out,
   so train and test signs occupy **disjoint frequency ranges**. This is the only grouping that
   severs the frequency confound: if C/V is merely "vowels are frequent," the model cannot rank
   vowels vs consonants inside a band it never trained on.

## Baselines (reproduced in-script, same feature code as A3)

| baseline | AUC |
|---|---|
| ungrouped in-sample (all 7 feats) | 0.897 |
| sign-grouped 7-fold, all feats (= A3 M1) | **0.828** |
| sign-grouped 7-fold, position-only (no log_freq) | 0.778 |
| sign-grouped 7-fold, **log_freq only** | 0.792 |
| Foundry single-feature position | 0.744 |
| Foundry 7-feat CV | 0.835 |

## Result 1 — feature-domain groupings: the signal SURVIVES corpus leakage

Pooled and mean AUC per grouping vs the ungrouped 0.828 baseline and the label-permutation null.

| grouping | n grps | pooled AUC | p (pool) | mean AUC | p (mean) | position-only pooled | p | null 95% |
|---|---|---|---|---|---|---|---|---|
| leave-one-**site**-out | 4 | 0.760 | 0.050 | 0.873 | 0.010 | 0.793 | 0.030 | 0.756 |
| leave-one-**series**-out | 20 | 0.817 | 0.005 | 0.863 | 0.005 | 0.803 | 0.015 | 0.758 |
| leave-one-**formula**-out (series+sub) | 62 | 0.753 | 0.030 | 0.784 | 0.020 | 0.742 | 0.035 | 0.725 |
| leave-one-**scribe**-out (hand) | 31 | 0.700 | 0.114 | 0.770 | 0.040 | 0.702 | 0.114 | 0.722 |
| leave-one-**chronogroup**-out | 12 | 0.752 | 0.055 | 0.855 | 0.005 | 0.782 | 0.020 | 0.751 |
| grouped-Kfold **document** (7) | 7 | 0.895 | 0.010 | 0.895 | 0.010 | 0.878 | 0.015 | 0.846 |
| grouped-Kfold **word-family** (7) | 7 | 0.831 | 0.015 | 0.833 | 0.015 | 0.778 | 0.030 | 0.771 |
| **chronological holdout** (early→late) | — | 0.905 | 0.025 | — | — | 0.888 | 0.025 | — |
| **chronological holdout** (late→early) | — | 0.903 | 0.010 | — | — | 0.832 | 0.055 | — |

Per-site all-vowel AUC is uniformly high (PY 0.887, KN 0.884, TH 0.885, MY 0.838; all 5 vowels
testable in each). Reading: **the C/V partition is NOT an artifact of a handful of related
documents, sites, scribes, series/formulae, or a single period.** It re-manifests in essentially
every large subcorpus and across the chronological divide. The lone weak grouping is **scribe**
(pooled 0.700, p = 0.114, inside the null 95th pct 0.722) — but scribes partition the corpus most
finely, so held-out feature domains are small and noisy; mean-of-groups is still 0.770 (p = 0.040).

Note the pooled < mean gap (e.g. site 0.760 vs 0.873): pooling concatenates *directed
`decision_function` scores from separately-trained per-domain models*, whose scales are not
comparable, which deflates pooled AUC. Mean-of-groups is the cleaner "does C/V recover *within*
each held-out domain" measure. Both are reported; both clear their own nulls for every grouping
except scribe-pooled.

## Result 2 — sign-unit frequency-band leave-out: the signal COLLAPSES

Hold out whole log-frequency bands of signs (4 equal-count bands). Train and test signs then have
**disjoint** frequency ranges. OOF directed AUC over all signs, 200-shuffle null.

| feature set | OOF AUC | perm p | null mean | null 95% |
|---|---|---|---|---|
| all 7 features | **0.658** | 0.125 | 0.444 | 0.724 |
| **position-only** (no log_freq) | **0.481** | 0.345 | 0.420 | 0.711 |
| log_freq only | 0.558 | 0.185 | 0.414 | 0.673 |

Band composition (why): vowels are frequency-segregated.

| band | n signs | n vowels | log_freq range |
|---|---|---|---|
| 1 (lowest) | 20 | **0** | 3.00–4.65 |
| 2 | 19 | **0** | 4.70–6.10 |
| 3 | 19 | 1 | 6.14–6.75 |
| 4 (highest) | 19 | **4** | 6.85–7.58 |

**Four of five vowels sit in the top frequency quartile; zero are in the bottom half.** Once the
model is forbidden from ranking signs by frequency band, position/distribution recovers C/V *at
chance* (position-only 0.481; all-feats 0.658 falls **inside** its own null's 95th percentile of
0.724, p = 0.125 — not significant). The residual "position" signal in the corpus-domain tests is
itself frequency-driven: right-/left-neighbour entropy has a mechanical ceiling of log(freq)
(a sign attested N times cannot exceed log N nats of context entropy), so "frequent" and
"high-entropy/vowel-like" are the same axis.

## Verdict — DOWNGRADE / REFUTE-AS-STATED

- The recoverable structure is **robust to document/site/scribe/series/formula/word-family/
  chronology leakage** (Result 1). It is a *stable* statistical regularity of the corpus, not an
  overfit to related units. That much of the Foundry/A3 result stands.
- But it is a **frequency typological prior, not a position/distributional break of the C/V
  symmetry.** The one grouping that isolates position from frequency — leave-one-frequency-band-out
  — takes position-only recovery to **0.481 (chance, p = 0.345)** and the full model to a
  non-significant 0.658. The Foundry wording *"position/distributional structure breaks the C/V
  symmetry"* is **not earned**; the honest statement is *"vowels are among the most frequent signs,
  and any frequency-ordered score recovers them — including in every subcorpus, precisely because
  frequency rank is preserved everywhere except when you deliberately hold a frequency band out."*
- Corpus-domain robustness therefore **cannot** be read as evidence for an independent positional
  signal: the grouped tests that pass all leave frequency rank intact, so they cannot distinguish
  a positional cause from a frequency cause. Only the frequency-band test can, and it refutes the
  positional reading.

**Claim-layer impact (Art. V):** the surviving effect is an **L2 structural** fact — signs
partition into a high-frequency class that happens to contain the vowels — with **no functional,
phonetic, or positional-mechanism licence**. It confers no C/V *reading*: it is the trivially
recoverable "vowels are frequent" prior, which will "work" identically and just as vacuously at
Linear-A scale (where the 5 pure-vowel signs are likewise among the most frequent), delivering a
frequency-ranked candidate list with zero independent phonetic content.

**Status:** `SIGNAL_IS_FREQUENCY_PRIOR — position/distribution C/V break NOT_SUPPORTED under
frequency control`. Robust across corpus domains; collapses to chance (AUC 0.481) under
leave-one-frequency-band-out. Supersedes the Foundry "position breaks C/V symmetry" wording.

## Files

- `scripts/a4_grouped.py` — grouped-evaluation engine (LOGO feature-domain, grouped K-fold,
  sign-unit frequency-band leave-out, chronological holdout; 200-shuffle nulls throughout).
- `data/A4_grouped.json` — all per-group AUCs, per-band composition, nulls, p-values.
