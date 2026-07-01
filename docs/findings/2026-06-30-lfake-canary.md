# Finding 2026-06-30 — L_fake canary: self-validation HOLDS (2 MEDIUM caveats)

The headline-novel piece, validated. `scripts/comparison/` (lfake.py, nulls.py, lexstat.py,
run_canary.py). Independently re-confirmed (deterministic re-run reproduces; 21/21 tests pass).

## Self-validation: the canary works

L_fake calibrated to Hebrew (semitic trilateral-root mode); positive control = real
Ugaritic↔Hebrew `S_lex`; canary = `S_lex(Ugaritic, L_fake)`.

> **UPDATE 2026-07-01 (P1.4/P4):** re-run at **n_fake=300** (was 16), so the L_fake floor is
> estimated from enough instances to resolve its tail, and the operative bar is the
> corrected-margin (Cornish–Fisher skew/kurtosis + Bonferroni-over-ε) value, not the raw p95. The
> positive control is `n_fake`-independent and unchanged; the thicker floor is higher than the
> 16-instance p95 (which understated the tail), and real still clears the **corrected** bar at
> every ε. `root_template_TV=0.33`, `residual_real_collision_rate=0.0`. Artifact:
> `results/lfake_canary.json`. Runtime: `run_canary` now scores `s_lex` through a process pool
> (`_parallel_slex`, verified bit-identical), ~45 min → ~5.5 min.

| ε | REAL cognates | L_fake p95 (n=16) | L_fake p95 (n=300) | corrected-margin bar (n=300) | verdict |
|---|---|---|---|---|---|
| 0.15 | 0.477 | 0.012 | 0.020 | 0.023 | CANARY_HOLDS |
| 0.20 | 0.550 | 0.031 | 0.074 | 0.079 | CANARY_HOLDS |
| 0.25 | 0.759 | 0.279 | 0.384 | 0.389 | CANARY_HOLDS |
| 0.30 | 0.761 | 0.279 | 0.384 | 0.390 | CANARY_HOLDS |

Real cognates clear the corrected-margin L_fake floor at every ε; fabricated L_fake sits at the floor. Even the
**leakage-controlled held-out split** (Hebrew lexicon built on one half, scored on held-out
Ugaritic whose cognate is absent) clears. → the canary catches spurious Gordon/Di Mino-style
matches. Calibration (Nair-style, divergence published): phoneme_freq_TV=0.035, length_TV=0.040,
lexicon_size exact; deterministic; parameter sweep confirms a calibration valley at temp=1.0.

## TWO MEDIUM caveats (verify-caught — FIX before the LLM-contamination use case)

1. **Root-template calibration gap (F.2 partial miss).** The generator samples the 3 root
   consonants *independently* from the marginal distribution → `root_template_TV=0.84`,
   `bigram_KL=1.47` (the root-co-occurrence structure that makes a Semitic lexicon
   search-attractive is unmatched). This biases the false-positive floor **DOWNWARD** (L_fake
   less root-structured → less matchable → lower floor → easier to clear) — the unsafe direction
   F.2 was written to prevent. The divergence is published but the verdict does not gate on it.
   **Fix:** sample root triples from the candidate's empirical root-frequency distribution.
2. **Regurgitation-proofing partial.** Rejection-sampling is only against the calibration gold
   file, so real Biblical-Hebrew roots from outside it (`yhw`, `mwt`, `hll`, `mwr`…) leak into
   ~100% of instances. The "ZERO real lexical content" wording is therefore **too strong** (true
   only for the calibration set, not the Hebrew language). A test now exposes this so it cannot
   be silently re-asserted. **Fix:** rejection-sample against a full Hebrew lexicon (ETCBC/bhsa,
   cloneable) + correct the wording + publish the residual collision rate.

## LOW issues

Dead AMBIGUOUS verdict branch (no_power and clears_p95 are complements); verdict gate uses raw
`pos_recall>p95` not the design's corrected (skew/kurtosis/DSR) margin; `eps_grid` default
mismatch (run vs main); the 800-form Ugaritic subsample disclosure isn't surfaced in the
human-readable report; Nair citation slightly looser than the paper-audit's validated framing.

## Verdict

**FIT FOR PURPOSE for the self-validation** (real cognate signal conclusively clears the
structural floor, robustly across ε and under leakage control). The two MEDIUM fixes are
**required before pointing the canary at its headline LLM-pretraining-contamination use case**
(task #22). The null remains the deliverable; the canary is a floor, not a discovery.
