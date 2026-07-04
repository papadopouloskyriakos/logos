# STEP A ruling — does the deposited Exit-B registration claim per-cell determinism?

**Source (readable mirror of the deposited paper; `paper/` not touched):**
`docs/preprint/logos-preprint-2026-07-01-condensed-v6.md`, §"Registered extension: a
known-answer sufficiency curve" (lines 145–147) and §8/§9 (lines 169–173).

## Verbatim quotes

- (§ registered extension, l.147) "The completed 2,000-step curve (near-converged: Luvian→Hittite
  0.462 vs. published 0.475, Phoenician→Ugaritic 0.760 vs. 0.805; **every recovery a *lower
  bound***) splits the branches at the sweep's Linear-A-scale locator … Linear B→Greek, the
  primary analog, stays at its chance floor (**0.044 ± 0.023, n=276**; floor ≈ 0.004), while
  Cypriot→Greek sits marginally above (0.066, n=346). **Under-convergence keeps the at-floor
  branch non-definitive**; full per-size and per-cell artifacts are deposited (`results/csa/`)."
- (l.147, framing) "any recovery is an **optimistic benchmark, conditional on a known cognate
  relationship** … neither branch is a decipherability claim."
- (§9, l.173) "its accuracy-vs-size curve is computed and deposited … any above-chance recovery on
  known-answer benchmarks is **true by construction**."
- (§9.7 reproducibility, l.179) reproducibility is asserted only of the **code/harness against a
  locally obtained corpus** — never of a per-cell numerical value.

## Verdict: **(a) — stochastic replicate/curve.**

The registration reports the sweep as an **aggregate with dispersion** (`0.044 ± 0.023`, with an
n), every recovery a **lower bound**, the at-floor branch explicitly **non-definitive**, and the
whole thing an **optimistic benchmark**. It makes **no claim of seed-based reproducibility or
deterministic per-cell measurement** anywhere; seeds 0–3 are swept to produce replicates that are
averaged into the reported mean ± sd. The only "reproducibility" claim (§9.7) is code/data
reproducibility, not per-cell numerical determinism.

**Consequence:** the 8.08-vs-7.58 fixed-seed non-determinism (INSTRUMENTATION_AUDIT.md) does NOT
falsify any deposited claim — the deposited `± 0.023` dispersion already subsumes cell-to-cell
variance (each cell is one stochastic run). The sweep is **VALID AS-IS**; no deposited-addendum /
STOP is triggered. Proceed to: (i) the report disclosures (the fixed-seed run-to-run variance is
part of the reported dispersion, to be stated in CURVE_REPORT), and (ii) STEP B — a NEW,
separately-deposited robustness study (does NOT modify the registered sweep).
