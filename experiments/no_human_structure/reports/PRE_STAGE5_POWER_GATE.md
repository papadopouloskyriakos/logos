# Pre-Stage-5 power gate (§VI) — VERDICT: NO_POWER_BEFORE_MODELING

Simulated from non-trivial REFERENCE_GOLD_A only (`data/source_labels/power_gate.json`). No model trained.

| quantity | value |
|---|---|
| non-trivial REFERENCE_GOLD_A | **66** (PLACE 43 · HUMAN 23) |
| load-bearing classes present | 2/4 (HUMAN, PLACE) |
| **load-bearing classes ABSENT** | **OPERATOR_OR_RELATION, QUALIFIER** |
| independent lexical / morphological families | 66 / 63 |
| KN / non-KN | 38 / 46 |
| proposed sealed-eval size (grouped) | 19 |
| majority-class baseline | 0.652 |
| **edition-independent structural signal precision** | **0.026** (cov 0.58) |
| est O2+D8 model accuracy | 0.291 |
| min detectable accuracy (n=19, 80% power) | **0.92** |
| power at est O2+D8 | **0.0** |

## Verdict: `NO_POWER_BEFORE_MODELING`

Reasons (mechanical): (1) two load-bearing classes are **structurally absent** from the trusted non-trivial
pool — no model can recover a class with zero secure labels; (2) **O2+D8 cannot achieve useful power** — the
edition-independent signal (0.026) is *below* the majority baseline (0.65), the est accuracy (0.29) is far
under the min-detectable 0.92, and the sealed eval is only 19 grouped units → power 0.0.

## Why (the honest structural reason)
Confirmed the dependency-audit forecast: the **only edition-independent labels are the trivial classes**
(numeral/logogram/total), so the non-trivial content roles rest *entirely* on the shared decipherment
(lexical identity). Strip lexical identity (the mandatory A12 condition of the transfer model) and **there is
no independent structural signal** to recover PLACE vs HUMAN, and only 66 units across 2 classes to test it
on. **The no-human path is underpowered BEFORE any modeling** — a rigorous negative result, not a modeling
failure.

**This is not INCOMPLETE** (no source/licensing/schema blocker) — the corpus + LFs are built and audited; the
signal and effective sample sizes are simply insufficient. Per §VII, STOP: Stage 5 (pseudo-script freeze) is
**not** frozen or implemented.
