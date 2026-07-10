# E201-F1b — armed import boundary (classification: PENDING_EXTERNAL)

**Status: PENDING_EXTERNAL — not closure-blocking** (per campaign rules: F1b depends on the
operator's CSA sufficiency sweep on `main`, ETA ~2026-07-13; LOGOS-2 closure proceeds
without it).

## What may enter (and nothing else)
- Sweep OUTPUT artifacts only: `results/csa/**` JSON/CSV produced by the sweep scheduler on
  `main`. No code, no notebooks, no hand-edited numbers.
- Entry is ONLY via `import_f1b.py` in this directory, which records sha256 + source path +
  import timestamp into `IMPORT_RECEIPT.json` before anything reads the data.

## Post-closure addendum procedure (append-only; Art. XVII)
1. After the sweep completes, run `import_f1b.py <results-dir>`.
2. Score F1b under the SAME frozen harness as F1a (`experiments/E201_replay_benchmark/`),
   zero re-tuning. The F1a-frozen thresholds bind.
3. Write `ADDENDUM-F1B.md` here: verdict + receipt hash + a compliance line. The addendum
   may REFINE the E201 row (F1a stands as scored) and may NOT alter any closed LOGOS-2
   verdict, the final report's conclusions, or the E213 seal.
4. Commit + push. If the addendum contradicts a closed claim, that is an ERRATUM record,
   never a rewrite.

Known F1a context the addendum must carry: UGA 0.486 carried a 34.4% dataset-inherent
cognate-identity leak (adjudicated); LB 0.000; CSYL 0.005; calibration 0/200 (CP95 0.0149).
