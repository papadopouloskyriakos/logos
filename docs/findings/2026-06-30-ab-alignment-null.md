# Finding 2026-06-30 — Track B A↔B alignment: held-out recovery is at CHANCE (an honest null)

The cross-script phonetic-imputation bet, tested the way the audits demanded — **held-out-shared-
sign recovery** (inherited Linear-B values cannot be both anchor and proof). **Result: the bet is
NOT supported on current data. No phonetic values are imputed.** This is a publishable null, not a
failure. Independently re-verified (deterministic re-run reproduces the numbers).

> **UPDATE 2026-07-01 — the DĀMOS "data-block" is now tested, not assumed.** The original null ran
> against a 919-wordform Linear-B/Greek cognate file and recommended "repeat with the full DĀMOS
> corpus." That corpus was already harvested (`corpus/bronze/linearb/damos/`, 5,840 tablets); it was
> just not ingested. It now is (`data.load_b_damos()`, `run_ab.py --b-source damos`): **13,562
> Linear-B wordforms (≈15× the cog), 89 sign-values, 56 anchors.** The result is **still at chance** —
> best of five methods (CCA) 0.025 vs chance 0.011, `clearly_above_chance = False`, against a
> **positive control that recovers 0.947** (so the harness works; the null is a real null). Ingesting
> the full Linear-B corpus therefore **refutes the "data-blocked until DĀMOS" framing**: the block is
> not corpus volume but an *absent distributional signal* — cross-script sign co-occurrence does not
> carry the A↔B phonetic map, even at full Mycenaean scale. Artifact:
> `scripts/cross_script/results_ab_damos.json` (the original cog run stays at `results_ab.json`).

## Setup (scripts/cross_script/)

- **Bridge:** Linear-A signs (Latin tokens; the token IS the inherited value, e.g. QE, RA2) ↔
  Linear-B signs (Unicode codepoints; value parsed from the official Unicode name). A **script-
  borrowing** join (same sign, two scripts) — NOT a cognate join. **55 shared-sign anchors** (the
  59 AB signs minus JU/PA3/TWE/ZU, unattested in the 919-row B file).
- **Embeddings:** PPMI co-occurrence (window 2, cds 0.75) → TruncatedSVD (d∈{16,24,32}), built
  **unsupervised** per script (E_A from the A corpus, E_B from the B corpus).
- **Five alignment methods:** frequency/positional, graph (IsoRank), CCA, **orthogonal Procrustes
  (MUSE/Mikolov-2013)**, entropic OT (Sinkhorn) — each fit on TRAIN anchors only.
- **Validation:** 200 bootstrap splits, 80/20 train/held-out over the 55 anchors (fit on 44, test
  on 11); nearest-neighbour search over all 69 B signs (chance = 1/69 = 0.0145); plus LOO.

## Result (mean accuracy / 95% CI)

| method | mean | CI | vs chance (0.0145) | clears? |
|---|---|---|---|---|
| **procrustes (best)** | 0.020 | [0.000, 0.091] | ~chance | **no** |
| freq_position | 0.019 | [0.000, 0.091] | ~chance | no |
| sinkhorn_ot | 0.018 | [0.000, 0.091] | ~chance | no |
| cca | 0.010 | [0.000, 0.091] | ~chance | no |
| graph_isorank | 0.003 | [0.000, 0.091] | ~chance | no |
| random_chance | 0.015 | [0.000, 0.091] | (the floor) | — |

**LOO (finest resolution):** procrustes **0/55**, freq_position 1/55, sinkhorn_ot 0/55.
**No method's lower-CI clears the chance floor → imputation withheld** (the gate refuses; an
imputed value without a recoverable signal would be circular noise).

## The null is real, not a broken test (controls)

- **Positive control** (synthetic rotated+noisy isomorphism, built from the *same* noisy B
  embeddings): **0.989** [0.909, 1.000] → the harness recovers a known alignment. **Pipeline sound.**
- **Negative control** (shuffled anchor join): **0.006** ≈ chance → no spurious signal.
- So the cross-script null is genuine, not an implementation bug.

## Why (honestly, two causes — not yet separable)

1. **Linear-B data is thin (binding constraint):** 919 wordforms / 3,450 tokens / 69 signs vs the
   full **DĀMOS ~5,500-tablet corpus** (not bulk-downloadable; needs a data request). PPMI stats on
   ~50 tokens/sign are noisy; a 69-sign distributional geometry cannot be stably anchored. A-only
   imputation targets are also rare (median frequency 4).
2. **Structural possibility:** Linear A writes **Minoan**, Linear B writes **Greek**. Sign
   co-occurrence encodes each language's phonotactics; the two embedding geometries are not
   guaranteed isomorphic, so a Procrustes rotation learned on ~44 anchors need not generalise.
   This is the **Etruscan-grade ceiling** — even ideal data may recover only partial phonetic shape.

DĀMOS would resolve (1); only it can tell us whether (2) is also in force.

## Significance

This is the discipline machinery doing its job: a **falsifiable, non-circular** test of the one
offensive lever, run before any claim, that **failed and was reported honestly** — no cherry-
picked "apparent correspondence," no overclaim. Per the reframing (maintainer assessment §6 +
paper-audit §3): the cross-script A↔B phonetic-imputation bet is **not supported on current data**
and is **gated behind the DĀMOS data request**. logos's standing contribution remains the
**decontamination + discipline layer** (L_fake canary, literature-virgin signs, LLM-ablation,
integrated graduation gate) — this null is itself part of that honest deliverable.
