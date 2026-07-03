# Equivalence gate results (PREREG.md §3) — recorded BEFORE any model class runs

Run: 2026-07-03, `python3 run_gates.py` (artifact: `results/gate_results.json`;
per-site counts: `results/loso_baseline_counts.json`). Frozen snapshot source:
`scripts/comparison/morphology.py` @ `1aa1249`.

## Gate A — deterministic point estimates (criterion: 4-decimal EXACT; mismatch = STOP)

| entry | published | reproduced | match |
|---|---|---|---|
| DP-unigram micro-F1 | 0.4361 | **0.4361** | EXACT |
| random micro-F1 | 0.3888 | **0.3888** | EXACT |
| Morfessor (informative) | 0.1556 | 0.1556 | EXACT |

LOSO wall-clock: 20.6 s (CPU, single process). **PASS.**

## Gate B — reconstructed site-clustered bootstrap (B=4,000, seed 20260703)

Criterion: 95% CI bounds each within ±0.005 of the published [0.021, 0.099]; P(gap>0) ≥ 0.99.

- Reconstructed DP−random gap 95% CI: **[0.0204, 0.0991]** (deviations 0.0006 / 0.0001)
- P(gap>0) = **0.9985**; gap mean 0.0518; Bonferroni 98.33% CI [0.0124, 0.1075]
- Stability (informative), seeds 20260704–07: CIs [0.0204,0.0971], [0.0214,0.0991],
  [0.0214,0.0966], [0.0201,0.0974]; P(gap>0) 0.997–0.999. **PASS.**

**Verdict: GATES PASSED — the pre-registered model classes may run.**
