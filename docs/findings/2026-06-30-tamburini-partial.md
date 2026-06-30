# Finding 2026-06-30 — Tamburini (CSA_OptMatcher) PARTIAL reproduction: 2 benchmarks MATCH published; ugaritic-noiseless cut short by the 5h usage cap

Adopted `CSA_OptMatcher` (Tamburini 2025) as logos's non-neural baseline — the B-K&K+Luo layer that
is now published prior art. Cloned to `corpus/bronze/code/` (gitignored); wrapper
`scripts/baselines/run_tamburini.py`. **The workflow FAILED with API 429 (5-hour usage limit
reached) before returning structured output (impl/verify = null), but the CSA checkpoint logs
captured the numbers.** Reproduction at seed 0, CSA checkpoints:

| benchmark | our acc (4000 steps) | Tamburini published | match? |
|---|---|---|---|
| luvian-hittite | **0.475** | 0.475 | ✅ exact |
| phoenician-ugaritic | **0.829** | 0.805 | ✅ close (slightly above) |
| ugaritic-noiseless | 0.002 @ 25 steps only | 0.955 | ❌ not converged |

- **luvian-hittite + phoenician-ugaritic MATCH** the published Table 3 → the CSA_OptMatcher
  adoption is **VALIDATED** (the wrapper reproduces published numbers where it converged). The
  audits' "reproduce a known decipherment" credibility anchor is met.
- **ugaritic-noiseless did NOT converge** — the 2,214-cognate search space is slow (~16 min per 25
  CSA steps); only 25 steps ran (0.2%) before the 429. Full convergence (toward 0.955) would need
  many more steps ≈ hours of compute. **Deferred** to a paced re-run.

## The binding constraint: the 5-hour API usage cap

#20 ran ~77 min / 231k tokens and **hit the 5-hour usage limit** (429; resets ~15:24 UTC). This is
a **hard external constraint on the autonomous plan**: the "every-15-min continuous" cadence is
infeasible — heavy workflows (~200k tokens each) must be **spaced ~1 per 5h window**, with light
work (salvage/record/commit) between. Over the 2-week AFK this still completes the ~6-task queue,
but at ~1 heavy step per 5h, not continuously. Recorded for the operator + future cycles.
