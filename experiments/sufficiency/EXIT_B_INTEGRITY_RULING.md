# EXIT-B integrity ruling — the deposited Linear-A-scale value is an endpoint clamp

**Date:** 2026-07-04. **Verdict: CONFIRMED — the deposited Linear-A-scale recovery values for BOTH
benchmarks are `_interp` endpoint clamps from the last COMPLETE size, not genuine 600–700-word
measurements. The 600–700-word LA-scale points were never computed at deposit time.** Read-only
audit; nothing under `paper/`, and the running sweep, was touched.

## The mechanism (learning_curves.py)

`_interp(curve, x, key)` (l.616): `pts = [(size, val) for p in curve if p[key] is not None]` — it
**drops null-data points**, then `if x >= pts[-1][0]: return float(pts[-1][1])` — **clamps to the
last non-null size**. `linear_a_locator` calls `_interp(curve, la_words=650, "recovery_mean")`.

At the deposit state (the 92 cells; `results/csa/csa_full_report.json`, built 2026-07-02 00:44):
- **linearb-greek** complete sizes = {92,100,184,200,276}; sizes {400,460,600,650,689,919} had
  `recovery_mean=None, n_seeds_done=0`. `_interp(650)` → 650 ≥ 276 → **returns the size-276 value**.
- **cypriot-greek** complete sizes = {69,100,139,200,208,346}; {400,520,600,650,693} null.
  `_interp(650)` → **returns the size-346 value**.

## The six audit questions, answered mechanically

1. **`n=276`** is the **SIZE (sz276)**, not a sample count. The deposited `0.044` is the mean of the
   4 size-276 cells; `± 0.023` is their pstdev. (Cypriot `n=346` = size 346, identically.)
2. **linb 600/650/689 complete at build time?** **NO** — `recovery_mean=None`, `n_seeds_done=0`.
3. **Did `_interp` clamp the 650 locator to size 276?** **YES** — `x >= pts[-1][0]` branch;
   `interp_recovery_acc = 0.04438405797101449` == the size-276 `recovery_mean` **exactly**.
4. **Did `la_scale_in_swept_range` use planned sizes not completed points?** **YES** — it checks
   `sizes[0] <= 650 <= sizes[-1]` where `sizes` includes the null-data points (…,919), so it reads
   `True` although 650 has no data. Defect confirmed.
5. **Does "completed curve" describe the deposited artifacts?** **NO** — at deposit linb had 5/11
   and cypriot 6/11 sizes complete; every LA-scale point (600/650/689) was empty. It was a
   **partial** curve; the LA-scale numbers are clamped lower-size endpoints.
6. **Raw size-276 values** (the four the deposited number came from): acc =
   {0.04710, 0.07971, 0.01812, 0.03261}, **mean 0.04438405797101449, pstdev 0.022825368** (== the
   deposited `0.044 ± 0.023`). `recovery_std` is `pstdev` over these **4 joint seed-plus-execution
   observations** (seed and run-to-run execution variance confounded — cf. INSTRUMENTATION_AUDIT.md).

## What this means for the deposited claim

The deposited/preprint sentence — *"The completed 2,000-step curve … splits the branches at the
sweep's Linear-A-scale locator (600–700 distinct word-forms) … Linear B→Greek … stays at its
chance floor (0.044 ± 0.023, n=276) … Cypriot→Greek sits marginally above (0.066, n=346)"* —
is **inaccurate in three linked ways**:
- "completed curve": the curve was **partial** (LA-scale sizes unrun);
- "at the Linear-A-scale locator (600–700)": the values are the **size-276 / size-346** values,
  clamped — the 600–700 range was **never measured**;
- the two branch verdicts (linb "at floor", cypriot "above chance / marginally above") are read
  off **clamped lower-size endpoints**, not genuine LA-scale recovery.

**Direction of risk (load-bearing):** recovery generally rises with corpus size, so the clamped
size-276 value likely **understates** the true 650-word recovery. The load-bearing conclusion
"Linear B→Greek is at its chance floor at Linear-A scale" could therefore **flip** once the genuine
linb 600/650/689 cells complete — the very cells the running sweep is now computing (0/4 done each,
in-queue).

## Honest mitigations (stated, not exculpatory)

- The deposited verdict was `AT_FLOOR_LOWER_BOUND` with explicit hedges: "every recovery a lower
  bound", "under-convergence keeps the at-floor branch non-definitive." So the claim was flagged
  non-definitive — BUT that hedge was about the **2,000-step budget**, NOT about the value being a
  **size-276 clamp**. A reader would take 0.044 as a genuine (if under-converged) LA-scale
  measurement; it is not. The clamping defect is **separate from and additional to** the
  convergence hedge.
- `n=276` / `n=346` are (inadvertently) truthful that the numbers are from sizes 276/346 — but the
  "600–700 locator" framing presents them as LA-scale values, which they are not.

## Ruling

The published Linear-A-scale value **was produced by endpoint clamping from size 276** (linb) /
size 346 (cypriot). Per §2 this is a **HARD STOP**: no edit or deposit of the robustness
pre-registration proceeds; this is a deposited-artifact integrity decision for the human. The
running sweep is untouched and, on completion, will supply the genuine 600–700-word result that
resolves the branch honestly.
