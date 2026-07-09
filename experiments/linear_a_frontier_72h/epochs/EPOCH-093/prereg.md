# EPOCH-093 — frozen prereg slice (LB→LA degradation surface)

**Family:** TURING_MORPHOGENESIS (E091–E096) · **priority:** IMMEDIATE · **layer:** L2 · **gate:** A
**Parent prereg:** `morphogenesis/PREREGISTRATION.md` (E093 slice frozen for the plan_hash).

## Question (frozen)
E092 settled that Turing is not needed; the operative campaign question is: does ANY graph method recover
phonetic-class structure at **Linear A's data scale**, or is LA below the detection threshold — and is the binding
constraint DATA VOLUME or something else? LA vs LB differ mainly in data volume (LA ~4,245 tokens vs LB ~43,868;
vocab 85 vs 89, nearly equal). Degrade LB by token budget and locate LA on the recovery surface.

## Design (frozen)
- **Method:** the generic-best graph method from E092 (Laplacian-eigenmap k-means), best-of-{SUBSTITUTION,
  MULTILAYER} view. Turing is NOT used (E092: not needed).
- **Factorial (≥100 cells):** token_budget ∈ {2000, 4000, 6000, 10000, 20000, 43868} × min_count ∈ {2,3,5} ×
  subsample_seed ∈ {0..5} = 108 cells. Subsample = random sequences until the token budget is reached.
- **Truth channels:** role (syllabogram-vs-other; trivial/degree) and vowel (phonetic-class; meaningful), frozen
  k=2 / k=5.
- **Per-cell controls (mandatory frequency-artifact guard):** permutation-null floor (100 draws, p95) AND a
  **frequency-only baseline** (cluster by log-frequency) AND degree-only. A cell counts as a MEANINGFUL detection
  only if recovery beats BOTH the permutation floor AND frequency-only (+0.03). (position→C/V and reduced-seed were
  both refuted as frequency artifacts earlier in this campaign — the frequency guard is required, not optional.)
- **LA placement:** LA's token budget (structural stat only — token count; NO phonetic values read) is mapped to
  the nearest cell (min_count=3, matching E091/E092).

## Verdicts (mechanical)
- **LINEAR_A_ABOVE_THRESHOLD** — at LA scale the vowel channel gives a meaningful (non-frequency-artifact)
  detection in ≥50% of subsamples.
- **LINEAR_A_NEAR_THRESHOLD** — meaningful detection in 20–50%.
- **LINEAR_A_BELOW_THRESHOLD** — <20% at LA scale though ≥50% at full budget (data-limited).
- **DEGRADATION_MODEL_INCONCLUSIVE** — the vowel channel fails the frequency guard even at full budget (no
  detection regime to place LA against).

## Scope / forbidden
L2, opaque sign IDs. A LINEAR_A_ABOVE_THRESHOLD verdict means only that LA's DATA VOLUME suffices to detect the
weak blinded-LB co-occurrence signal — it licenses **no** LA sound values, no vowel readings, no translation
(brief §11). Whatever the outcome, the binding-constraint question (data vs signal-weakness vs no-transfer) is the
deliverable.
