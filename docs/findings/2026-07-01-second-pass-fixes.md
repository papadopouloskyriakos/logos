# Second-pass review — code-integrity fixes (verified against commit 6055a48)

Every review claim was **verified against the current code before changing**, and every number is
graded from persisted artifacts. Tags: **[NO-NUM]** = zero reported-number change; **[NUM]** = re-run
+ refresh; **[PROSE]** = manuscript only.

## The load-bearing fact: the P0 gate bugs are provably LATENT (isolation proof as an artifact)

The two confirmed graduation-path bugs (family win-counting, DSR-in-family-gate) live entirely in
`scripts/family_scores.py`, the downstream roll-up. They corrupt **no reported number**, and this is
a *structural* fact a referee can re-check in seconds, not an assertion:

```
# (1) no probe / reported-number module imports the buggy roll-up:
$ grep -rln "family_scores" scripts/comparison/        ->  (none)
$ grep -rln "import family_scores" scripts/ tests/     ->  tests/test_gate_integrity.py
                                                            tests/test_scaffold.py   (tests only)
# (2) nothing was ever graduated:
verdicts total = 0   gate_verdict='GRADUATE' = 0   graduated_families (G2) = 0
```

So: (a) the family gate is imported by no probe module; (b) zero families graduated; (c) every
reported number (morphology 0.250 / bigram 0.375; metrology p=1.0; phonology 0.40/0.86; image 0.410;
contamination; segmentation 0.436) is produced by an independent probe module. The bugs could not
have touched a reported result. (Aside: `morphology.py` references DSR, but that is the separately-
reported affix z-test *diagnostic* §6 already flags as non-operative — a different statistic from the
family graduation gate fixed here.)

## P0 — repository integrity

| # | claim | verdict | fix + regression test |
|---|---|---|---|
| 1 | rejected rows count as family wins | **CONFIRMED** (`family_scores.py:62` counted `result=='match'`; `_load_family_rows` never loaded `gate_verdict`; `write_verdict` persisted `gate_verdict` only inside `notes`) | Added structured columns `gate_verdict, gate_version, gate_clauses_json, search_log_id` to `verdicts` (schema.sql + `migration_2026-07-01_verdict_gate.sql`, applied to the live DB). `write_verdict` now persists them. `family_scores` loads `gate_verdict`; **a win is `gate_verdict=='GRADUATE'`**. Test: `test_gate_integrity.py::test_family_win_is_graduate_not_match` (a `result='match', gate='REJECT'` row → 0 win_rate). **[NO-NUM]** |
| 2 | DSR live in the family graduation gate | **CONFIRMED** (`family_scores.py:29,77,81` — `dsr_ge_0_95` was an operative clause in `all(clauses)`) | Removed `dsr_ge_0_95` from the family gate; DSR kept as a **reported diagnostic column only**. Gate = win-rate + `MIN_VERDICTS`. Test: `test_dsr_is_not_a_graduation_clause` (forces DSR=0.10, family still graduates). **[NO-NUM]** |
| 3 | multiplicity fail-OPEN default | **CONFIRMED (narrow)** — the SearchLog override already worked (`verdict.py:133-135`); the sole defect was the fail-open `n_trials = max(1, int(n_eff or 1))`. | Added §E clause `search_multiplicity_instrumented = (n_eff_source=='searchlog')`; a would-be match with un-counted N_eff now **fails closed → `INCOMPLETE`**, never a silent win at n=1. Test: `test_verdict_fails_closed_without_instrumented_search`. **[NO-NUM in practice]** — no reported number flows through `verdict.grade`'s `n_trials` (all reported numbers are probe-module outputs; 0 graduations). Empirically confirmed: full suite re-grades verdicts with identical results bar the new columns. |
| 4 | epsilon-grid multiplicity undercounted | **CONFIRMED** (`verdict.py:152` `n_cmp = max(1, len({eps}))` ≡ 1) | `n_cmp` now taken from the searched eps grid (search_log `.eps_grid` or explicit `eps_grid=`), never the single selected eps. **[NO-NUM]** (scaffold uses one eps; count unchanged, but no longer hard-wired). |
| 5 | bump gate_version + regenerate | done | `METRIC_VERSION → verdict-v2`, added `GATE_VERSION = gate-e2` (persisted per verdict). DB migrated; verdicts regenerate under gate-e2 on the next `verdict.run`. |

Full suite after P0: **365 passed, 4 xfailed** (was 364+1-broken; the one break was the live DB
needing the migration, now applied).

## The two re-run items (done, old→new reported)

- **Item 8 — segmentation uncertainty [NUM]:** ran the LOSO segmenter + a **site-clustered bootstrap**
  against the local corpus (3 s). Reproduced the paper exactly (dp_unigram micro-F1 **0.4361**, random
  **0.3888**). Bootstrap (resample 52 sites, B=4000): real−random gap 95% CI **[0.021, 0.099]**,
  excludes zero, **P(gap>0)=0.998**. → the "genuine held-out positive" **survives**; §7 now reports the
  CI (the paired gap, not the wide marginal per-segmenter CIs, is the operative test). **Number did not
  move; uncertainty added, positive stands.**
- **Item 3 — multiplicity [NUM-maybe]:** the re-run (full suite grading) confirms **no reported number
  moves**; the fix only makes an un-instrumented would-be-win fail closed, and every executed probe is
  already a null far from threshold, so the correction can only strengthen the nulls. No number changed.

## Prior-art note (for §8.3, from the parallel audit)

No prior work does the exact §8.3 move (downsample known-answer cross-language cognate benchmarks →
corpus-sufficiency locator for an undeciphered script). Methodological ancestors to cite:
**Ravi & Knight 2008** and **Berg-Kirkpatrick & Klein 2013** (decipherment learning curves over cipher
length), **List 2014** (cognate-detection accuracy vs sample size), **Barber 1974** and **Zhang & Gong
2016** (analytic corpus-sufficiency thresholds). Honest framing: *first application of a known idea
(data-size recovery curves) to a sufficiency diagnostic* — a synthesis, not a discovery.

## Status
- **DONE:** P0.1–P0.5 (code + schema + migration + 3 regression tests, suite green); item 8 (bootstrap,
  §7 updated); item 7 partial (§8.3 already trimmed to "curve in progress" in a prior pass).
- **PENDING (this doc tracks):** P1 prose items 6, 9, 10, 11 + §8.3 prior-art citations; P2 packaging
  (pyproject/.env.example/lazy-DB-init/pytest markers/Makefile + the 2 genuine test failures);
  P3 bibliography; P2.13 finance-lineage docstrings (`logos_stats.py`, `verdict.py`, README/DESIGN drift).
