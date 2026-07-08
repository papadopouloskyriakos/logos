# EPOCH-027 — Preregistration

## Task
INITIAL-vs-FINAL cross-site generalization asymmetry in Linear A (synthesis of E023 + E026; L2/L3).

**Question (positional/structural ONLY, no meaning):** Is there a SYSTEMATIC structural
asymmetry such that word-INITIAL positional preferences generalize across independent LA
sites MORE than word-FINAL ones, across the whole sign inventory (i.e. shared initial
conventions vs site-local terminal habits)?

## Discipline (hard, non-circular)
- Sign names ANONYMIZED in interpretation (we report tokens but draw NO phonetic / sound /
  meaning / language / reading inference). L2/L3 positional statistics ONLY.
- Linear B (LB) is a POSITIVE-CONTROL BENCHMARK ONLY. We never transfer a LB reading onto LA.
- Prereg + plan_hash FROZEN before any LA computation. PC runs FIRST.
- Verdict is MECHANICAL from the frozen rule below. Operator never adjudicates.

## Data
- LA: `corpus/silver/inscriptions_structured.json`; words with `signs`; inscriptions with
  `site`; only >=2-sign words.
- LB PC: `scripts.cross_script.data.load_b_damos()[0]` (DĀMOS Mycenaean wordforms).

## Sign set & sites (chosen at inspection, frozen here)
- Qualifying signs = signs with >=30 total occurrences across >=2-sign LA words.
  (Inspection found 42 such signs; full list committed in result.json `numbers.signs_tested`.)
- Qualifying sites = sites with >=20 qualifying (>=2-sign) words.
  (Inspection found 10 such sites.)

## Per-sign, per-position cross-site counts
For each qualifying sign S and each qualifying site X:
- "INITIAL-significant at site X for S" = S is the FIRST sign of site X's >=2-sign words
  more often than the within-word uniform-permutation null predicts (one-sided p<=0.05,
  1000 draws, seed per (S,X)).
- "FINAL-significant at site X for S"   = S is the LAST  sign ... (same null, last position).
- n_init_sig_sites(S)  = # qualifying sites where S is INITIAL-significant.
- n_final_sig_sites(S) = # qualifying sites where S is FINAL-significant.

The FINAL null is the within-word uniform permutation applied to the LAST position
(P(last==S) = count_S_in_word / L), exactly symmetric to the INITIAL null. This is the
E024 `permutation_null` machinery extended to the terminal slot.

## Positive Control (PC) — runs FIRST, gates the verdict
Run the SAME per-sign init-vs-final cross-partition procedure on LB. LB has NO site
metadata in `load_b_damos`, so we use a SEEDED BALANCED 5-WAY partition of the LB
>=2-sign wordforms (seed=7; contiguous fold assignment after a seeded shuffle — SAY SO).
For each LB sign with >=30 occ across >=2-sign words, compute n_init_sig_parts and
n_final_sig_parts across the 5 folds (permutation null, p<=0.05, per fold).

LB is KNOWN to carry strong grammatical WORD-FINAL structure (inflectional endings).
**PC REQUIREMENT (frozen):** the machinery must detect LB's finals — i.e.
`mean(n_final_sig_parts) >= mean(n_init_sig_parts)` on LB. If the method reports
initial-dominance on LB (where finals dominate), it is biased ->
verdict `MACHINERY_UNINFORMATIVE`, no LA claim.

This PC makes an `INITIAL_GENERALIZES_MORE_LA` verdict non-trivial: the method is shown
NOT to manufacture initial-dominance.

## LA asymmetry test
Across the qualifying LA signs, compare paired (n_init_sig_sites, n_final_sig_sites).
- Statistic D = mean(n_init_sig_sites) - mean(n_final_sig_sites).
- Significance: LABEL-SWAP permutation null — for each sign independently swap its
  (init,final) pair with prob 0.5, recompute D; >=2000 draws; TWO-SIDED p
  (p = (1+#|D_perm|>=|D_obs|)/(1+N)).
- Cross-check: Wilcoxon signed-rank p across signs.
- Counts: # signs init>final, # final>init, # tie.

## FROZEN MECHANICAL VERDICT (one token)
- `INITIAL_GENERALIZES_MORE_LA` iff (PC PASSED) AND D>0 AND label-swap p<=0.05 AND
  (n_init_gt_final > n_final_gt_init).
- `FINAL_GENERALIZES_MORE_LA`   iff (PC PASSED) AND D<0 AND label-swap p<=0.05 AND
  (n_final_gt_init > n_init_gt_final).
- `NO_POSITIONAL_ASYMMETRY`     iff (PC PASSED) AND label-swap p>0.05.
- `ASYMMETRY_UNDERPOWERED`      iff (<6 qualifying signs) OR (<5 qualifying sites).
- `MACHINERY_UNINFORMATIVE`     iff PC FAILED.

Power check at inspection: 42 signs, 10 sites -> NOT underpowered.

## Outputs (exact paths)
- prereg.md  -> this file
- plan_hash.txt -> "<sha256>  prereg.md"
- machinery.py -> epochs/EPOCH-027/machinery.py (imports E024 permutation_null; __main__ self-check)
- result.json -> numbers + verdict
- report      -> reports/EPOCH027_REPORT.md
- data dir    -> data/epoch_027/ (per-sign per-site CSVs)

## Reproducibility
- All RNG seeded. n_draws=1000 for per-site/per-fold nulls; >=2000 for label-swap.
- result.json carries `method`, `numbers`, `key_findings`, `successor_hypotheses` (>=5),
  `layer="L2/L3"`, `la_touched=true`, `non_circular` (str), `deviations` (list).
