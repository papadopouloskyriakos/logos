# EPOCH-006 — Seed-efficient estimators for the motif bridge (E003 open door)

**Verdict: `SEED_EFFICIENCY_NOT_ACHIEVED`** (all four estimators `SEED_EFFICIENT_NOT_ACHIEVED`).
Frontier F3, gate A. Prereg `epochs/EPOCH-006/prereg.md`, plan_hash `23fc9fd2…8fd4df`
(frozen 2026-07-08T04:13:52Z before any corpus run). Seed 20260708. Claim layer **L2**,
KNOWN-script calibration only — **no Linear A data touched, no licence change (Art. XV)**.

## Question

E003 left one open door: at the LA operating point (b=5 seeds, f=0.75) the required
Holm-surviving hit rate (5/42 = 0.119) is *below* the channel's measured LOO rate (0.149),
yet M1's anchor-profile geometry delivers only 0.039 — a 3× shortfall attributed to
**estimator geometry, not information**. E006 tests four estimators whose anchors only FIX A
GLOBAL TRANSFORM/COUPLING over the full unsupervised MF_A trigram-motif graph:

| | estimator | anchors used as |
|---|---|---|
| EST_GW | landmark-fused entropic Gromov–Wasserstein (α=0.5, ε=0.01) | fused penalty in the GW cost |
| EST_SPEC | orthogonal Procrustes on Laplacian eigenmaps (k=6) | landmark rows for the rotation |
| EST_OT | anchor-regularized Sinkhorn on the unsupervised M2-signature cost (α=0.5, ε=0.05) | fused penalty |
| EST_CCA | ridge linear map (λ=0.1) on the same eigenmaps | regression rows |

Identical discipline + **identical RNG streams** as E003 (replicate-paired with its M1 cells);
all hyperparameters frozen in the prereg; one endpoint (held-out exact count, 1000-perm null);
per-test bar 0.05/12 = 0.0041667.

## Gates (all behaved)

- **PC0** harness identity: PASS (KNOWN M1-LOO 7/47, CTRL 55/71, code paths identical).
- **PC1** (LOO b=46, per estimator): EST_GW 47/47 p=.001 PASS, EST_OT 47/47 p=.001 PASS —
  both **elimination-assisted exactly as declared** (coupling marginals push the one free row to
  the one free column; a necessary-but-weak gate). EST_SPEC **4/47 p=.017 FAIL — reproducing
  E002's M4 LOO to the sign**, which doubles as the declared code-path check. EST_CCA 2/47 FAIL.
- **Negative control** (b=5, all 5 anchors scrambled): FLOOR for all four estimators.

## Results

**Verdict cell — KNOWN (b=5, f=0.75), the LA operating point** (E003 M1 reference: acc .034, med_p .599):

| estimator | acc | median p | verdict |
|---|---|---|---|
| EST_GW | .051 | .267 | FLOOR |
| EST_SPEC | .025 | .599 | FLOOR |
| EST_OT | .071 | .081 | FLOOR |
| EST_CCA | .023 | .652 | FLOOR |

**Seed column — KNOWN f=1.0** (M1 b5 reference: .039, med_p .417): EST_GW .067/.070/.076/.084
and EST_OT .069/.071/.084/.082 at b=3/5/7/10, median p ≈ .06–.08 throughout — consistently
~**1.8× M1's hit rate**, consistently short of NOMINAL, far from the .0042 bar. EST_SPEC/EST_CCA
at M1's floor or below. Wrong-anchor robustness: UNINFORMATIVE by the frozen rule (all clean
KNOWN b=5 cells FLOOR); descriptively no estimator was catastrophically poisoned at kw=1
(EST_OT kw=1 acc .081 ≥ clean .071 — different seed streams, noise-level).

**PC2 — CTRL identity pair at b=5** (the decisive contrast): EST_GW **acc .419, p=.001,
survival 20/20** (M1: .112); EST_OT .231 SURVIVES; EST_SPEC .096 SURVIVES; EST_CCA FLOOR.
Global-transform estimators are massively seed-efficient **when the cross-graph signal is strong**.

## Reading (mechanical, then interpretation)

Mechanical: no estimator reached SURVIVES_HOLM — or even a NOMINAL median — at the verdict cell.
Committed prediction (P(all NOT_ACHIEVED)=0.60, modal) CONFIRMED, including all three PC1
sub-predictions.

Interpretation — **the E003 open door NARROWS but does not close**: estimator geometry recovers
roughly *half* the shortfall (0.039 → 0.071 against a required 0.119) and then saturates, while
the same estimators show 3.7× seed-efficiency gains on CTRL. So the binding constraint at b=5 is
now most plausibly the KNOWN cross-script channel's own SNR — and E003's "available 0.149" was
itself estimator-relative (M1 at 46 anchors), not a channel capacity. The sharper successor
question: is 0.119-at-5-seeds attainable by ANY estimator on this channel, or is the channel
SNR-limited below the bar regardless of geometry?

**LA application stays BLOCKED** (nothing earned it; a future application needs its own prereg +
anchor-integrity gate). Effective-n: verdict rests on 4 preregistered cells; 32 cells × 20
replicates total; zero hyperparameter tuning (search receipt in result.json). Runtime 29.7 s.

## Artifacts

`data/motifs/seed_efficient/E006_{result,pc0,pc1,cells_partial}.json`,
`scripts/e006_seed_efficient.py`, `epochs/EPOCH-006/{prereg.md,plan_hash.txt,result.json}`.
