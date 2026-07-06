# Toponym-anchor power envelope (PILOT — provisional; `experiments/power/power_sim.py`)

**Design analysis, not a confirmatory result.** Abstract Monte-Carlo (no real anchor↔LA matching):
simulates a fuzzy-match-under-mapping-search procedure over synthetic anchors/candidates to estimate
end-to-end false-positive and recovery rates at Linear-A scarcity. All parameters **PROVISIONAL
pending REQ-02 (Hoch) calibration** of the real Egyptian→foreign distortion. Params: `n_cand=11`
(= the tier-B TOPONYM_LIKE count from Task A), `V=20`, anchor/candidate length 3, mapping
flexibility 3, Hamming tol 1, search budget 300, graduate = ≥75% of anchors matched by one mapping.
Compute: local, 1 core, seconds — **zero CSA/fence contention.**

## Envelope (300 trials/cell)

| n_anchors | **in-sample FP** | in-sample TP | **held-out FP** | held-out TP |
|---:|---:|---:|---:|---:|
| 2 | **1.00** | 1.00 | **0.26** | 0.35 |
| 3 | **0.97** | 1.00 | **0.27** | 0.37 |
| 4 | **1.00** | 1.00 | **0.27** | 0.39 |
| 5 | **0.98** | 1.00 | **0.22** | 0.45 |
| 6 | **0.72** | 0.95 | **0.30** | 0.41 |

## Findings (honest, and decision-relevant)

1. **In-sample best-of-search is uninformative — NO_POWER.** With FP ≈ 0.72–1.00, a search over
   sign-value mappings "explains" the graduation threshold of anchors **by chance almost always**.
   Any confirmatory design that scores in-sample match count is invalid — the null does exactly as
   well. (This is the multiple-testing trap relocated into the mapping search.)
2. **Held-out generalization is necessary but, alone, still under-powered at this scarcity.** Requiring
   the mapping learned on training anchors to predict a **held-out** anchor drops FP to ≈ 0.22–0.30,
   but recovery is only ≈ 0.35–0.45 — a signal-to-null gap of just ~0.15, and FP ≈ 0.25 is far too
   high for a credible anchor claim. **More anchors (2→6) does not clearly rescue it** in this regime.
3. **The two levers that matter are not "more anchors" but constraint:** (a) a **FROZEN correspondence
   model** (no mapping search — the `frozen` branch in the sim), and (b) **longer, real anchor
   skeletons** (Knossos `kA-n-yw-SA` is ~4–5 elements, not 3) + **fewer, higher-confidence candidates**.
   These cut the coincidental-match probability that drives FP.

## Verdict (provisional): the toponym-anchor experiment is **NOT_READY / leans NO_POWER as naively scoped.**
With only ~3–4 securely-identified Egyptian toponyms (Knossos/Amnisos/Lyktos) and flexible matching,
the design cannot currently separate signal from chance. This is a **successful design-level null**:
it says *don't run a confirmatory toponym match expecting a positive result* until the design is
constrained. What could change it (to be measured once REQ-02 is applied): the **frozen
Hoch-calibrated distortion model** (removing the mapping search), real skeleton lengths, a tightened
candidate set, and mandatory held-out evaluation. The envelope must be **re-run with those calibrated
parameters** before any go/no-go — see `POWER_ASSUMPTIONS.md`.
