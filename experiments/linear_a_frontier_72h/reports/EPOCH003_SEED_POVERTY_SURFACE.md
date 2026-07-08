# EPOCH-003 — Seed-poverty + corpus-power surface for the trigram-frame motif bridge

**Verdict: `BRIDGE_NOT_VIABLE_AT_LA_SEED_BUDGET` · measured minimum seed budget = LOO (46) —
no finite budget in {3…30} Holm-survives on the KNOWN pair at any corpus fraction.**

Frontier F3 · gate A/E · plan_hash `be6dd7e786d373df3cad5c9b9bdba9b1786e6d98629a6c211eee9e8901e025d6`
(prereg frozen 2026-07-08T03:46:58Z before any run) · seed 20260708 · claim layer **L2**
(KNOWN-script power calibration; no LA value claim; licences unchanged).
Articles: V, VII, VIII, IX, XI, XII, XV, XXII.

## Question

EPOCH-002's cross-script recovery — the first Holm survivor in this channel's history
(KNOWN LB↔Cypriot, MF_A trigram + M1 NN-transfer LOO, 7/47 = 0.149, p = 0.001) — ran with
**46 anchors**. Linear A has **~5 firm toponym equations**. Does the bridge survive LA's
seed budget and corpus power? Measured entirely where ground truth exists.

## Design (as preregistered, executed in full)

113 cells: {KNOWN, CTRL} × fractions {0.05, 0.1, 0.25, 0.5, 0.75, 1.0} × budgets
{3, 4, 5, 7, 10, 15, 20, 30, LOO} + 5 wrong-seed adversarial cells; 20 replicates/cell
(5 corpus draws × 4 seed draws when f < 1); per-replicate 1000-perm exact-count null over
held-out signs; cell bar = median p ≤ 0.05/12 (the per-test bar M1:exact cleared inside
EPOCH-002's Holm-12 family) → SURVIVES_HOLM / NOMINAL (≤ .05) / FLOOR.

**Positive control (gated first): PASS** — KNOWN 7/47 and CTRL 55/71 reproduced exactly;
E002 and E003 code paths prediction-identical. **Negative control: PASS** — all-5-wrong-seed
scramble at floor (acc 0.023, p 0.64).

## The surface (KNOWN pair — the calibration that binds LA)

Exact-recovery accuracy (mean over 20 replicates) / cell verdict; full corpus row:

| budget | 3 | 4 | 5 | 7 | 10 | 15 | 20 | 30 | LOO(46) |
|---|---|---|---|---|---|---|---|---|---|
| acc | .041 | .045 | .039 | .057 | .064 | .069 | .089 | .141 | **.149** |
| median p | .25 | .29 | .42 | .16 | .15 | .095 | .11 | .051 | **.001** |
| verdict | FLOOR | FLOOR | FLOOR | FLOOR | FLOOR | FLOOR | FLOOR | FLOOR | **SURVIVES_HOLM** |

- **Seed axis:** the bridge Holm-survives ONLY at LOO (46 anchors). Even b=30 fails —
  its hit rate approaches the LOO level (.141) but only 17 held-out signs remain, so it
  cannot reach significance. `min_seed_budget = 46` under the monotone-closure scan.
- **Corpus axis (at LOO):** f=1.0 and f=0.75 SURVIVE (acc .149/.143); f=0.5 NOMINAL only
  (p .006); f ≤ 0.25 FLOOR. The bridge needs ≥ ~75% of the cog-list corpus even with all
  46 anchors. Corpus is the *secondary* constraint, exactly as predicted.
- **Harness power control (CTRL identity pair):** SURVIVES_HOLM down to **4 seeds** at
  full corpus (b4 .093 p .001; b5 .112 p .001) and down to f=0.25 at LOO (acc .450).
  The detector has small-budget power; the KNOWN failure is channel signal-strength.

## Adversarial: wrong-seed injection

KNOWN clean cells at b=5/7 were already FLOOR (contrast uninformative there — reported as
such). Declared post-hoc on CTRL, where clean signal exists:

| CTRL f=1.0 | clean | 1 wrong | 2 wrong |
|---|---|---|---|
| b=5 | SURVIVES_HOLM (.090) | **NOMINAL** (.065) | **FLOOR** (.050) |
| b=7 | SURVIVES_HOLM (.141) | SURVIVES_HOLM (.090) | SURVIVES_HOLM (.070) |

**One wrong seed among 5 poisons a genuine Holm-surviving signal below the bar** — the
G-surface anchor fragility reproduces on this channel. At 7 seeds the bridge tolerates
1–2 wrong anchors (with 36–51% accuracy loss). Any 5-seed application would additionally
require every anchor to be *correct*.

## Linear A's operating point

- Corpus mapping (frozen rule, min-side median alignable support): LA = 47 vs KNOWN
  realized {f=0.75: 41.3, f=1.0: 56.0} → **f_LA = 0.75**. (Secondary token-ratio mapping
  would clamp to 1.0; b=5 is FLOOR at both, so the mapping choice is immaterial.)
- **CELL_LA = (KNOWN, b=5, f=0.75): FLOOR** — acc .034, median p .60, survival rate .05.
- Verdict rule 3 → **BRIDGE_NOT_VIABLE_AT_LA_SEED_BUDGET**.

**The gap, quantified:** LA has 5 firm seeds; the bridge as built needs 46 (9×). Or, at 5
seeds: the Holm bar needs 5/42 held-out hits (rate .119) — the channel's LOO hit rate
(.149) actually EXCEEDS this, but M1's 5-dimensional anchor-profile geometry delivers only
.039. **The collapse is estimator geometry, not information impossibility** (declared
post-hoc, required-hit-rate MC). That is the one door this epoch leaves open.

## Committed prediction — outcome

CONFIRMED: min_seed_budget > 5 (predicted p=0.70), verdict ∈ {NOT_VIABLE, MARGINAL}
(predicted p=0.75), corpus the weaker axis at LA's point. The 0.15 tail (VIABLE) did not
occur.

## What this closes and what it opens

Closes: any direct LA application of the E002 M1-anchor bridge at today's seed budget —
running it on LA would produce an uninterpretable FLOOR cell, and with ~5 anchors a single
wrong toponym equation poisons even a true signal. The E002-LA "consistency" hit (8/51,
seeded by 50 assumed pairs) must NOT be read as evidence the bridge would work with real,
scarce seeds.

Opens (ranked successors):
1. **Seed-efficient estimators** — global-transform methods that use 5 anchors only to fix
   a rotation/coupling on *unsupervised* full-geometry (seeded GW, landmark Procrustes on
   spectral embeddings, anchor-regularized OT): required rate .119 < available .149, so a
   better estimator is not excluded. Calibrate on KNOWN first, same discipline.
2. **Anchor-integrity gate** — mechanical leave-one-anchor-out self-consistency screen,
   calibrated on KNOWN, as a precondition for ANY future seeded LA bridge (1-in-5 wrong
   poisons).
3. **Localize the threshold in (30, 46]** — budgets 35/40/43 + pooled-power estimators;
   is the true requirement ~46 or ~35? Determines the acquisition target.
4. **Grow the seed set** — independent LA↔LB equation candidates (toponym pairs beyond the
   firm 5, Anetaki II prospective gold, seal-iconography co-occurrence) toward the measured
   requirement; each candidate must pass successor-2's integrity gate.
5. **Seed-poverty sweep for the composition kernel** — E002's LA signal was largely
   order-free; the bag-of-cooccurrence channel may have different seed-efficiency. Same
   surface, composition similarity, KNOWN pair.
6. **Joint seeds×corpus requirement model** — fit the measured surface to rank concrete
   acquisitions (SigLA unpublished, new tablets) by expected movement toward viability.

Artifacts: `data/motifs/seed_poverty/{E003_surface.json, E003_positive_control.json,
E003_posthoc.json}` · `scripts/{e003_seed_poverty.py, e003_posthoc.py}` ·
`epochs/EPOCH-003/{prereg.md, plan_hash.txt, result.json}`.
