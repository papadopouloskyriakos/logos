# Exit-B — provenance of the four page-9 numbers (0.044, 0.066, 0.462, 0.760)

**Date:** 2026-07-05. **Read-only.** Findings only — no correction prose, no edits, §2 hard stop in
force, running sweep untouched. Purpose: decide the rewrite scope (two clauses vs whole sentence)
by auditing the two *unaudited* numbers (0.462, 0.760) under the same `_interp` mechanism that
clamped linb 0.044 / cypriot 0.066.

## Headline

The four numbers split into **two kinds**:
- **0.044 (Linear B→Greek) and 0.066 (Cypriot→Greek): the defect** — `_interp` **incomplete-data
  clamps**, `la_scale_in_swept_range=True` (false positive), locator readings at the 600–700 word
  locator that was never reached.
- **0.462 (Luvian→Hittite) and 0.760 (Phoenician→Ugaritic): NOT the defect** — their **entire
  corpus** is 59 / 105 words (both **complete** at deposit); the locator correctly reports
  `in_range=False` and clamps to the **full corpus**. These are genuine full-corpus recoveries used
  as convergence anchors vs published, not LA-scale readings.

So the clamp defect is confined to the two locator clauses (0.044, 0.066). A third incomplete-data
clamp exists in the deposit — **ugaritic-noiseless 0.861** — but it is **not printed in the paper**.

## 1. Per-number provenance table

| # | benchmark (paper ↔ cell) | producing read | complete sizes @ b05e7b3 | `_interp`? | clamped? | raw per-seed acc → mean |
|---|---|---|---|---|---|---|
| **0.044** | Linear B→Greek ↔ `linearb-greek` | `linear_a_locator(650)`, `in_range=True`, `AT_FLOOR_LOWER_BOUND` | [92,100,184,200,**276**] of planned […,919] | Y | **YES — incomplete-data clamp** (last complete 276 ≪ 650) | [0.04710, 0.07971, 0.01812, 0.03261] → **0.04438** |
| **0.066** | Cypriot→Greek ↔ `cypriot-greek` | `linear_a_locator(650)`, `in_range=True`, `ABOVE_CHANCE` | [69,100,139,200,208,**346**] of planned […,693] | Y | **YES — incomplete-data clamp** (last complete 346 < 650) | [0.05780, 0.02023, 0.10116, 0.08671] → **0.06647** |
| **0.462** | Luvian→Hittite ↔ `luvian-hittite` | `linear_a_locator(650)`, `in_range=False`, clamp → full corpus | [30,44,**59**] = **FULL, complete** | Y | clamp, but from the **COMPLETE full corpus**, out-of-range **flagged** → **not the defect** | [0.47458, 0.45763, 0.47458, 0.44068] → **0.46186** |
| **0.760** | Phoenician→Ugaritic ↔ `phoenician-ugaritic` | `linear_a_locator(650)`, `in_range=False`, clamp → full corpus | [21,32,52,79,100,**105**] = **FULL, complete** | Y | clamp, but from the **COMPLETE full corpus**, flagged → **not the defect** | [0.71429, 0.76190, 0.77143, 0.79048] → **0.75952** |

Every deposited number = mean of **4 seeds**; `all_converged=False` for all (plateau never fired at
2,000 steps → all are lower bounds, as the sentence hedges). The producing read for all four is the
same `linear_a_locator(la_words=650)` call in `csa_sweep.assemble_report` (l.258) → `_interp`
(`learning_curves.py` l.651). The *difference* is only whether the requested 650 lands beyond
**incomplete** data (0.044/0.066: the size list runs to 919/693 but data stops at 276/346, so
`in_range` is a false True and the clamp hides a truncation) or beyond a **complete full corpus**
(0.462/0.760: the whole corpus is 59/105 < 650, so `in_range` is a correct False and the clamp
simply returns the full-corpus value).

## 2. Published anchors (0.475, 0.805) — citation + size-match

- **Source:** the recovery method's own paper — **Tamburini 2025, CSA_OptMatcher (Frontiers in AI
  8:1581129)** (`learning_curves.CITATION`; body.tex §2.3 `\citep{tamburini2025}`). 0.475 is the
  published CSA accuracy for Luvian→Hittite (corpus `RWT2002_Luv-Hit.cog`), 0.805 for
  Phoenician→Ugaritic (`StarlingDB_Ph-Ug.cog`) — Tamburini's own benchmark corpora.
- **But:** the sentence (body.tex l.721) carries **no `\citep`** at the numbers; they are **prose
  literals**. There is **no in-repo constant** (the only `published_csa` is `nan`, on the unused
  H100 path) and the report JSON stores **no published anchor** for these benchmarks. The exact
  corpus size Tamburini's figures apply to is **not documented locally**.
- **Size-match verdict (per pair):** our 0.462/0.760 are **full-corpus** recoveries on the **same
  cog corpora** Tamburini used (59 / 105 words). So the comparison is **size-matched** (full-vs-full
  on the same benchmark corpus) *conditional on* Tamburini's figures being on that same corpus —
  plausible (the cog files are his) but **not locally verifiable**. It is **not convergence-matched**:
  ours are 2,000-step lower bounds (`all_converged=False`), his are converged; the small deficits
  (0.475−0.462 = 0.013; 0.805−0.760 = 0.045) are consistent with mild under-convergence — the
  intended "near-converged" reading.

## 3. Affected `results/csa/` files

- **`csa_full_report.json` — the only affected deposited file.** It holds **three** incomplete-data
  clamps: `linearb-greek` 0.0444, `cypriot-greek` 0.0665, **`ugaritic-noiseless` 0.8609** (all
  `in_range=True`, data ≤ 221/276/346 of planned ≥ 650), plus two benign full-corpus clamps
  (`luvian-hittite` 0.4619, `phoenician-ugaritic` 0.7595, `in_range=False`). Of the three defective
  clamps, only linb + cypriot surface in the paper; **ugaritic-noiseless 0.861 is deposited-only**.
- `csa_cells_2026-07-02.tgz` — **raw per-cell JSONs only, no locator output** → not affected (raw
  acc values are correct).
- `curve_lowerbounds.INVALID.json` — **0 clamp signatures**, already marked `.INVALID` (superseded
  pre-deposit) → not affected.

## 4. Benchmark name map (paper ↔ sweep cell ↔ cog corpus)

| Paper name | Sweep cell name | Cog corpus | full corpus |
|---|---|---|---|
| Linear B→Greek | `linearb-greek` | `linear_b-greek.cog` (syllabic) | 919 |
| Cypriot→Greek | `cypriot-greek` | `csyl-greek.cog` (syllabic) | 693 |
| Luvian→Hittite | `luvian-hittite` | `RWT2002_Luv-Hit.cog` | 59 |
| Phoenician→Ugaritic | `phoenician-ugaritic` | `StarlingDB_Ph-Ug.cog` | 105 |
| *(not in the sentence)* | `ugaritic-noiseless` | `uga-heb.no_speNL.cog` (Ugaritic→Hebrew, noiseless) | 2214 |

## 5. `learning_curves.py` import-path verdict (for the code-continuity rule)

**In the running-sweep execution path: YES.** `learning_curves` is imported at module top by both
`resume_sweep.py` (l.40) and `csa_sweep.py` (l.72), and every cell runs as a fresh
`resume_sweep.py --cell` subprocess → **every cell worker imports `learning_curves`**.

**But the locator functions are report-side only.** `run_cell` (the cell computation) references only
`lc.KNOWN_ANSWER_BENCHMARKS / _DATA_DIR / parse_cog / downsample / write_cog / chance_floor /
benchmark_stats`. It **never** calls `linear_a_locator` or `_interp` — those run **only** in
`assemble_report` (l.258). A locator-guard fix would touch exactly `_interp` / `linear_a_locator`,
which the cell path never executes, so the fix is **computationally neutral to every cell**.

**Verdict:** because `learning_curves.py` is in the cell import graph, the conservative,
rule-abiding action is to **apply the locator-guard fix only after the sweep completes** (running
cells already loaded the old module; a post-edit cell would import the changed file). The mitigating
technical fact — the guard touches only report-side functions never called in `run_cell`, so no cell
output can change — means the fix *could* be applied to a report-only path sooner if the human
accepts the imported-but-not-called distinction; the default under "same committed cell code" is to
wait.

## Bottom line for rewrite scope

The clamp defect is in **two clauses** (0.044, 0.066), not four. The 0.462/0.760 convergence anchors
are genuine complete full-corpus values, size-matched (mod the uncited published corpus) and already
hedged as lower bounds. The **"completed 2,000-step curve"** framing and the **"splits the branches
at the … locator (600–700)"** placement are the sentence-level overstatements that span all four.
(Scope is stated as a finding; the correction wording is a separate, later task.)
