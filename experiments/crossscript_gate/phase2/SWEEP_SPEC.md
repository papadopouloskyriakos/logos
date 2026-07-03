# SWEEP_SPEC — Phase 2 Step 1: anchor-quota power sweep (PRE-COMMITTED before any cell runs)

**Frozen: 2026-07-03, before any sweep cell executes.** The quota is READ OFF the resulting
curves by the mechanical rule in §5 — never chosen after seeing them. This sweep is entirely
SYNTHETIC: abstract anchor words over the eligible sign pool. No real candidate anchor, no real
held-out label, no recovery model on real data. Nothing under `paper/` is read or written.

## 1. Inherited frozen elements (verbatim provenance)

- Verdict band (commit `00fb9ea`): **GO iff power ≥ 0.80 at some s ≤ 3**; MARGINAL ≤ 8; NO-GO
  otherwise; INVALID iff s=0 false-fire > 0.14 or s=13 power < 0.90 (machinery checks).
- Strength grid (Addendum B, `33a3fec`): s ∈ {0, 0.5, 1, 2, 3, 5, 8, 13}, verbatim.
- Detection rule (Phase-1 final, PREREG_FINAL §B/§E at N=1): add-one permutation p_raw < 0.05
  against the permuted-graph null, n_perm = 200 (the frozen power-sim convention).
- Design universe (Phase-0.5-certified lineage): 51 robust anchors; U = real DĀMOS PPMI
  (w2/cds 0.75) → SVD d=24 value embeddings; 73 candidates; synthetic LA side
  X = s·(Q·U_true) + N(0, I₂₄), L2-normalised; Procrustes stand-in decoder; held-out signs
  drawn from the **49 eligible** (ineligible {SI, MU} per PREREG_FINAL §D).

## 2. Axes

- **n_anchors ∈ {5, 8, 10, 15, 20, 25, 30, 40}** synthetic anchor words.
- **Redundancy regime R ∈ {1, 2, 3}** = maximum anchor-word memberships ("legs") per sign,
  enforced during anchor generation.
- **h = 20**, drawn **uniformly** from the 49 eligible per replicate. (Disclosed deviation from
  Phase-1's coverage×frequency stratification: synthetic coverage changes per replicate, so the
  real-coverage strata do not transfer; uniform draws are the conservative choice — pin-supply
  luck is included in the power estimate.) One descriptive sensitivity row at h = 15 and h = 25
  is run at the quota cell only, AFTER the quota is read off (sanctioned descriptive extra).
- **Feasibility pre-rule (fixed now):** a cell is infeasible iff its minimum possible sign-slot
  demand exceeds capacity: 3·n_anchors > 49·R. Skipped cells (recorded, not run):
  R=1: n ∈ {20, 25, 30, 40}; R=2: n ∈ {40}. Runnable grid = **19 cells**.

## 3. Synthetic anchor generation (per replicate — coverage randomness is averaged over)

- Word lengths i.i.d. from the REAL S&M Table 6.3 LA-side alphabetic length distribution:
  **P(len 3) = 23/30, P(len 4) = 7/30** (30 alphabetic forms on book p. 101: 23 three-sign, 7
  four-sign; the MI+JA+RU ligature excluded; Table 6.4's five toponym forms are contained in
  this list). Using LENGTHS (a provenance fact) is the only contact with real anchors — no real
  anchor identity, coverage, or effect enters the sweep.
- Each word's signs: drawn without replacement (within the word) uniformly from the 49 eligible,
  subject to the cap: no sign may belong to more than R anchor words. Rejection-resample the
  word (≤ 1,000 attempts) if the cap cannot be met; a replicate that cannot realize its anchor
  set is regenerated with the next sub-seed (counted and reported).
- Collisions emerge naturally: a word with ≥ 2 held-out member signs pins none of them (the
  frozen `_pinned` mechanic, verbatim semantics).

## 4. Operative curve: LOTO-SURVIVAL power

Per replicate: draw anchors, draw h=20, plant signal at s, fit Procrustes on the 31 train
anchors, score:
- **full** (pins active) and **LOAO_j** for each synthetic anchor word j (word j's pins
  removed; NN prediction replaces them) — obs and all n_perm null draws (one fit per draw, all
  scorings from it, exactly the Phase-1 `axis_run` pattern).
- **Detection (operative):** full clears (p_raw < 0.05) AND every LOAO_j clears — the event
  Phase 1's clause (ii) would have accepted. **LOTO-survival power(cell, s) = fraction of
  replicates detecting.**
- Raw-bar power (full-only) reported alongside, descriptive.
- **Machinery validity, run once** (pins OFF, identical across cells): s=0 false-fire ≤ 0.14
  and s=13 power ≥ 0.90, else INVALID → fix harness, thresholds unmoved.

## 5. Quota-derivation rule (mechanical, fixed now)

Order the 19 runnable cells by **(n_anchors ascending, then R ascending)**. The **quota is the
FIRST cell whose LOTO-survival power meets the frozen GO band (≥ 0.80 at some s ≤ 3)**.
Tie-breaks are inherent in the ordering (prefer fewer anchors, then lower redundancy). If NO
cell meets the band: that is the result (a design-space bound); report it and STOP before any
gap analysis is framed as achievable. The quota statement reads: "N vetted anchors with ≤R legs
per sign cap (realized coverage reported) make a true positive LOTO-survivable at the frozen
band."

## 6. Replicates, seeds, escalation

- **n_rep = 100 per (cell, strength)** — raised from the prior 50 because the quota is a
  band-edge read-off: at power 0.8, SE = √(0.8·0.2/100) ≈ 0.040 (vs 0.057 at 50), halving the
  chance of a wrong-cell call between adjacent cells.
- Seeds: master **20260712**; replicate seed = master + 100000·cell_index + 1000·strength_index
  + rep (cell_index = position in the §5 ordering). Anchor sets regenerate per replicate.
- **Escalation rule:** profile ONE cell first; if the projected full-sweep wall-clock exceeds
  **6 hours** on the available cores, STOP and report the projection before launching. CPU
  only; no GPU.

## 7. Step separation (binding)

This sweep never sees a real candidate anchor. The Step-2 census (provenance-only) never sees a
statistic. The two meet only at a future Phase-2 freeze under a new pre-registration and a new
external timestamp.
