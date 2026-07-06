# Red-team of the Cretan-anchor preregistration — findings & response (2026-07-06)

Before minting the plan_hash, the v1 preregistration was adversarially red-teamed across 6 failure-mode
lenses (workflow `wf_3bfac2b3-fdf`, 7 agents, 0 errors). **Verdict: `REVISE_THEN_COMMIT`** — the design
survives but v1 had 6 blocker-class defects. v1 was **withdrawn**; v2 (`PREREG_cretan_anchor_test.md`)
closes them. The plan_hash remains **empty** pending the §15 preconditions. This is the audit trail.

## Blockers → how v2 answers them

| # | Blocker (v1) | v2 fix |
|---|---|---|
| B1 | **Triviality / no model-free baseline.** The primary skeletons are near-identical across scripts (Lyktos `r-k-t`=`r-k-t` exact); a dumb edit-distance ranker would CONFIRM with the Semitic model doing nothing — all v1 nulls were scrambled-*model* nulls. | Added **identity/edit-distance baseline `B_id`** M2 must beat; new verdict tier **RECOVERED_TRIVIAL** when M2 recovers but ≤ baseline (§6–§7). |
| B2 | **Skeletonization is an answer-aware DoF.** No single blind function; Egyptian kept aleph while LB dropped it; the two files disagreed on Amnisos (`m-n-s` vs `(ʾ)-m-n-s`). | **One hash-pinned `f()`** applied identically to all three surfaces; conventions (aleph/glide drop, š≠s) pinned *inside* `f()`; `f(target_LB)==pool_entry` assertion; Amnisos reconciled (§3). |
| B3 | **Reading independence fails.** Edel read the eroded ovals *using* the Greek IDs → the Egyptian skeleton is not independent of the answer. | Precondition: source **Falttafeln 13/14** for ID-blind sign-level readings; else the claim is scoped to "recovers Edel's ID-informed readings" with the leak documented per anchor (§11, §15.6). |
| B4 | **Generic-Egyptian ablation missing.** The permuted null only shows the model learned *something*; a model knowing only generic Egyptian sign values would beat it and recover all targets — so CONFIRM couldn't isolate *Semitic→Aegean generalization*. | Added **generic-Egyptian ablation `B_egy`**; the strong claim attaches only when M2 beats `B_egy` too (§6–§7, §13). |
| B5 | **Statistical core invalid.** `p0` an unspecified-draw MC point estimate (could be 0 → auto-CONFIRM); `Binomial(3,p0)` assumes i.i.d. anchors that are correlated; `best_of_100` undefined. | Replaced with a **joint MC permutation test** (`N≥10,000`, `p=(1+#{r1≥r1_obs})/(1+N)`, never 0) that carries the shared-pool/shared-map correlation with no i.i.d. assumption (§6). |
| B6 | **`n_hypotheses=1` is false.** The En Cretan block is 6 ovals, not 3; reducing to the 3 cleanest matches was done with the skeletons in view. | **Skeleton-blind, model-blind anchor rule** (Cretan ∧ non-palimpsest ∧ surviving ∧ not-fraglich) deterministically yields the set; model-behaviour annotations struck; 6→3 deflated; full-6 as symmetric secondary (§3, §8). |

## Majors → v2

- Pool unfrozen + no no-pilot attestation → §15 preconditions + **no-pilot attestation** (§12); freeze/run
  as separate timestamped git events.
- "Zero Cretan data" was a *label* predicate → **skeleton-collision hold-out** (remove training pairs whose
  skeleton matches any target within Levenshtein 1), exact exclusion predicate, new corpus sha (§11).
- No confusability floor → **≥3 distractors within edit-distance ≤1 per target, else NO_POWER** (§4).
- Pool-source fork (DĀMOS vs Ventris–Chadwick) → **one committed source** + explicit inclusion predicate (§4).
- `p0` aggregation ambiguity / wrong NO_POWER quantity → dissolved by the permutation test + power re-anchored
  on a clearable endpoint (§6, §10).
- Heads-I-win "sensitivity" bucket → **symmetric** secondary with pre-committed interpretation (§8).
- §13 overclaim → claims scaled to `r1` (2/3 "provisional", 3/3 strong), **non-compounding** ≤0.75 cap,
  "licenses" = *permits proposing* a separately-gated probe (§13).

## Minors folded in

Skeleton-uniqueness assertion; bit-identical tie rule across scorers; surprisal reported as `−log₂(p_emp)`
not `log₂ M`; honest pre-data prior (0.4, not the 0.75 ceiling); struck the misleading Lyktos "l→r" note
(both sides are already `r` at test time — it is the pure-identity anchor).

## Net

The red-team converted a naive, near-circular test into a rigorous one whose **strongest honest outcome**
is "the Semitic-trained map beats identity + generic-Egyptian + scramble baselines," not "the phonetic
bridge is real." The most consequential lesson: on these specific toponyms the Egyptian and Aegean
skeletons are near-identical, so a bare recovery is expected and uninformative — the test's discriminating
power lives entirely in the **increment over the model-free baselines**, which v2 now measures. Whether the
Cretan set can clear that bar at all is itself uncertain and is exactly what the (still-unminted) test will
decide.
