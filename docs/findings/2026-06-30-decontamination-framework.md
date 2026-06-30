# Finding 2026-06-30 — decontamination-layer framework (#4): S_phono / S_morph / N_eff / L_virgin, wired + adversarially hardened

Built the remaining held-out-statistics + decontamination machinery from
`docs/design/comparison-layer.md` §A.2/B.2/C.2 and wired it (additively) into `verdict.grade`.
Produced by a 10-agent workflow (4 parallel implementers → 1 integrator → 5 adversarial verifiers),
then **hardened by hand against the verifiers' findings** before commit — the "verify, don't trust"
contract. The Packard banded-permutation null (B.1) and the Euler-γ order statistic (`expected_max_*`,
B.3) already existed, so the genuinely-new pieces are the four modules below plus the order-stat bar.

## What was built

- **`scripts/comparison/phonostat.py`** — **S_phono**, the WEAK surface-plausibility statistic: an
  add-k n-gram phonotactic model over L's lexicon scoring held-out forms' per-symbol log-likelihood.
  Honest NaN/degenerate path. (14 tests)
- **`scripts/comparison/morphostat.py`** — **S_morph**, the STRONG/Kober statistic: does L's affix
  inventory recur **productively** (≥2 distinct stems) and **consistently** (across independent
  inscriptions) above a within-form null? Returns separate `has_power` / `is_significant` flags + the
  F.1 no-power escape. (15 tests)
- **`scripts/comparison/searchlog.py`** — **N_eff instrumentation** (§B.2, invariant 12): a
  deduplicating `SearchLog` whose `.n_eff` is the *exact* distinct-candidate count a future scanner
  produces, replacing the hand-passed int. (20 tests)
- **`scripts/comparison/litindex.py`** — **L_known/L_virgin partition** (§C.2) + a small, cited,
  **non-exhaustive seed** literature index (GORILA Linear-B-value transfers) + `virgin_support`. (15 tests)
- **Integration** — `logos_stats.expected_max_order_stat(mu0,σ0,N)` (generalizes `expected_max_sharpe`
  to a non-zero null mean; the §B.3 bar); `verdict.grade` now reports S_phono/S_morph + the order-stat
  bar/DSR, consumes the instrumented N_eff, and feeds `virgin_support` into the §E gate.

## Verifier-found defects — fixed (not just noted)

- **HIGH — S_morph conflated repetition with morphology.** A single formula word copied across 5
  inscriptions scored identically to productive affixation — the dominant false positive on exactly
  the short/formulaic corpus F.1 targets. **Fix:** a productivity gate — an affix earns credit only
  when it attaches to ≥2 **distinct stems** (residual after stripping). Repetition → 1 stem → 0 credit.
  Empirically re-measured after the fix: false-positive rate on structureless (within-form-shuffled)
  corpora = **3.0% (6/200)** — the nominal one-sided z≥2 rate, z-dist mean≈0/σ≈1.0 — and power on a
  genuine recurring-affix corpus = **100% (50/50)**. Locked by regression tests.
- **LOW→ real — the verdict morph clause was a tautology** (`verdict.py`): keyed off `is_powered`,
  which already implied `deflated>0`, so it could never be False. **Fix:** split `has_power` (the
  corpus *can* test morphology) from `is_significant` (it passed). Now `has_power & ¬significant` makes
  the clause **False** (the strong test was available and the candidate failed it) and blocks
  graduation; no-power stays neutral-True. AND-ing it is monotone — the gate only got STRICTER, so no
  previously-failing case can now graduate. Locked by a verdict-level regression test.
- **MEDIUM — searchlog sanity bound false positive.** Comparing the joint-map `n_eff` to the per-pair
  product `S·V·R·F·G` flagged honest multi-sign logs as dedup bugs. **Fix:** a **per-dimension**
  tripwire (distinct pairs ≤ S·V, signs ≤ S, lexemes ≤ R_L, segmentations ≤ G_seg) — joint maps can't
  trip it, real over-specification still does. Regression tests both directions.
- **LOW — phonostat degenerate hole** (an all-empty-string lexicon reported a finite likelihood):
  `is_degenerate` now also fires when the vocab carries no character evidence (`⊆ {END,UNK}`).
- **LOW — morphostat negative-seed crash:** composite null seed reduced mod 2³².

## Honest limitations recorded (not fixed — by design)

S_phono is the explicitly WEAK statistic and stays so: its add-k denominator depends on alphabet size
V (cross-lexicon comparison needs **inventory-matched** lexicons — the F.2 calibration supplies this),
and its length-normalization is approximate for heavily-OOV material (the bias cancels on a common
held-out set). Both are documented in the module; S_phono is never verdict-bearing.

## Verified (independently re-run by me)

- **226 passed, 4 xfailed** (was 156 at the scaffold; +64 new module tests +6 new regression tests).
- `verdict.py` grep CLEAN: no `anthropic`/`openai`/`llm_call`/`claude`/`ollama`/`http`; still the
  **sole writer** of the `verdicts` table (invariant 2/3 hold post-edit).
- The §E gate was only made **stricter** — the morph clause can now block but never graduates a
  previously-failing case.

## Gaps / next (unchanged roadmap)

The **comparison scanner** (the hypothesis generator that drives `SearchLog` and feeds `predict`) is
still unbuilt; the litindex **full population** (Gordon/Best/Di Mino Semitic proposals — the `*301`
exemplar is *not yet quarantined*) is the deferred bounded task; the **C.4 LLM-ablation** (gemma3 on
`nllei01gpu01`, ~25 min) and **#5 learning curves** (CPU batch) are the GPU offloads. S_morph remains
the gold-standard-WHEN-POWERED; on Linear A's short/formulaic corpus it will frequently report
no-power honestly — that is the F.1 design, not a bug.
