# E207 amendment R1 — probability sign error (defect repair; as-run results VOID)

**Committed:** 2026-07-10, after the as-run battery completed and BEFORE any amended rerun.
The as-run outputs are preserved unchanged in `results_asrun_R0/` and are **INVALID**.

## The defect
`battery.py::Battery._p_stem` computed the compositional stem probability as
`math.exp(-sum(math.log(p_pos)))` — the RECIPROCAL of the intended product (sign error), so
M3/M4/M6 scored with pseudo-probabilities > 1 and impossible held-out NLLs (M3 = 0.147
bits/sign on unseen types). Caught by post-run sanity review (a held-out score below ~3
bits/sign on 984 types is information-theoretically implausible for this corpus).
The as-run verdict PREDICTIVE_FUNCTIONAL_CLASS is void.

## The repair (no result-driven adaptation)
`exp(-sum(log p))` → `exp(sum(log p))`. No thresholds, model definitions, seeds, synthetics,
or verdict logic change. Also documented: M1_indep is identical to M0 under the length-factored
scoring used here and is reported as M0 (plan.json listed both; no separate M1 is computed).

sha256 of this amendment appended to plan_hash.txt (append-only).
