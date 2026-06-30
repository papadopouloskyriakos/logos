# Finding 2026-06-30 — L_fake caveats FIXED; canary holds under the stricter corrected margin; honesty overclaims corrected

Resolves the 2 MEDIUM + LOW issues from `docs/findings/2026-06-30-lfake-canary.md`. Verify verdict
was ACCEPT WITH REQUIRED FIXES; the required honesty fixes are applied + independently re-verified
(re-run exit 0; 38 tests pass; headline now honest).

## Fixes (scripts/comparison/lfake.py, run_canary.py, __init__.py)

1. **Root-template sampler (MEDIUM, F.2) — CLOSED.** Now samples whole root TRIPLES from the
   candidate's attested trilateral-root frequency distribution (not independent marginals) +
   deterministic template-slot seating. **root_template_TV 0.84 → 0.33** (bhsa on; 0.23
   standalone). The downward floor-bias (the unsafe direction F.2 forbade) is removed.
2. **Full-Hebrew-lexicon rejection (MEDIUM) — APPLIED.** ETCBC/bhsa (6042 romanized lexemes →
   7682 canonical-skeleton reject set [lexemes + attested trilaterals]). **Whole-form real-Hebrew
   collision → 0.00000** (was ~14.8%).
3. **Corrected-margin gate (LOW).** Replaces raw `pos_recall>p95` with a Cornish-Fisher expansion
   (L_fake skew/excess-kurtosis via `logos_stats.moments`) + a Bonferroni/DSR multiple-comparisons
   haircut. Never loosens below raw p95. 3-way verdict: NO_POWER / AMBIGUOUS / CANARY_HOLDS.
4. eps_grid default consistent; held-out subsample disclosure surfaced in the report.

## Canary still holds — under the STRICTER corrected margin

eps=0.25: real **0.759** > corrected bar **0.389** (L_fake floor mean 0.365, p95 0.381) — and the
floor **moved UP** from ~0.279 (the safer direction F.2 enforced). Holds at every eps (0.15: real
0.477 > 0.023; 0.20: 0.550 > 0.071; 0.30: 0.761 > 0.389). CANARY_HOLDS_REAL_CLEARS_FLOOR.

## The honesty correction (the load-bearing change)

Dropped the **"zero real lexical content"** overclaim (it was false). The honest position, now
stated in `__init__.py`, `lfake.py`, and the `_fmt` headline:

- L_fake is **whole-form-invented** — no whole-form real Hebrew lexeme (collision ≈ 0 under bhsa).
- BUT the F.2 root-template calibration **seats attested Hebrew trilateral roots** into the forms,
  so **~75% of L_fake forms CONTAIN a real Hebrew trilateral as a substring** — by design (the
  root-structure calibration), NOT a leak. bhsa rejects whole lexemes, not the embedded
  root-substring.
- So L_fake is a **whole-form-invented, root-structured floor** — conservative (a Hebrew-memorising
  model may score it non-trivially, raising the floor in the safe direction) — NOT a "no real
  content" floor. This nuance is material for the LLM-pretraining-contamination use case.

## Verdict

ACCEPT. The canary is now **calibrated (F.2 root-template closed) AND honestly described** — fit
to serve as the false-positive floor in the decontamination layer. Caveat for the contamination
use: because real Hebrew roots are embedded by design, the canary is a *calibrated* floor, not a
definitionally-foreign one; a future strengthening (invented-but-Hebrew-structured roots, or a
root-frequency-matched synthetic root inventory) would tighten the regurgitation backstop further.
