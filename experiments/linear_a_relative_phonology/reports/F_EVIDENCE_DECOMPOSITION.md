# F_EVIDENCE_DECOMPOSITION — cross-script LA↔LB channels, kept separate

**Task F1** · Constitution v2.2 (Art. XI/XII/XV) · seed 20260708 · 59 shared-AB correspondences · 8 channels

Articles triggered: XI (source-dependency graph), XII (no grading a target by the rule that created it), XV (transfer licences — none earned). Non-circular gate: LB `conventional_value` is a grading key on benchmarks ONLY, never a channel input.

## What F1 does and does NOT do

- Does NOT re-run the value-transfer test (Foundry admin channel = NULL; crossscript_gate = `REFUTE_LOTO_FRAGILE`) nor re-litigate the SHAPE leg (circular = LB-identity, capped ≤0.75).
- DOES decompose the combined 'cross-script correspondence' evidence into 8 separate channels and ask, mechanically, which channel (if any) is **independently calibratable** — i.e. scores a correspondence against a non-circular held-out benchmark without using the LB value it predicts.

## Per-channel decomposition (across all 59 correspondences)

| channel | coverage | discriminative | non-circular | indep. calibratable | outcome |
|---|---|---|---|---|---|
| shape | 1.0 | H=0.7376 | no | no | calibrates but CIRCULAR |
| stroke_structure | 0.0 | H=0.0 | YES | no | unpopulated |
| orientation | 0.0 | H=0.0 | YES | no | unpopulated |
| chronology | 1.0 | H=0.0 | YES | no | not sign-discriminative |
| geography | 1.0 | CV=0.3404 | YES | no | measurable, no aligned benchmark |
| admin_function | 1.0 | — | YES | YES | **calibrated → NULL** |
| scholarly_correspondence | 0.4237 | H=0.5128 | no | no | calibrates but CIRCULAR |
| source_dependency | 1.0 | H=0.5255 | YES | no | audit channel (not predictive) |

## The one calibratable channel: admin_function

- Channel: distributional admin-role (PPMI + SVD co-occurrence, Procrustes-aligned) -- uses NO phonetic value
- Benchmark: shared-AB held-out LOTO (leave-one-toponym-out), value graded by LB conventional value
- R@1=0.0 R@5=0.071 R@10=0.125 MRR=0.0624 (chance R@1=0.0112; shuffled-null R@5=0.066 MRR=0.0622)
- perm-p(R@5)=0.6 perm-p(MRR)=0.5
- **NULL -- does not beat the shuffled null; no non-circular value power at LA scale**
- Concordance: REFUTE_LOTO_FRAGILE; distributional channel = 0.0000 (independent 3rd null confirmation)
- Source: linear_a_foundry/data/wp4_summary.txt (wp4_cross_script_evolution.py CAL#2)

## Why each other channel is NOT independently calibratable

- **shape** — Circular: the grade IS an LB-homophony judgment (=identity). Calibrates perfectly but confounded with the value it should predict. Capped <=0.75. NOT independently calibratable.

- **stroke_structure** — Unpopulated: no LA<->LB stroke-decomposition dataset in the repo. Cannot be scored, so cannot be calibrated. (Would in principle be non-circular if a palaeographic stroke corpus were acquired.)

- **orientation** — Unpopulated: no glyph-orientation dataset. A sub-facet of shape; not independently measurable here.

- **chronology** — Script-level ordering (all LA predates all LB). Not sign-discriminative for a CORRESPONDENCE: it cannot pin which LB sign an LA sign maps to. LA-internal date span varies but carries no LB-value info.

- **geography** — LA per-sign site profiles ARE measurable and vary across signs, but LA (Crete find-sites) and LB (Knossos/mainland archives) share no site system, so no non-circular held-out benchmark aligns a geographic score to an LB correspondence. Measurable but not correspondence-calibratable.

- **scholarly_correspondence** — Scholarly Cypriot-stability status is itself an expert value judgment on the same latent identity. Grading it by LB/Cypriot value is circular. High-value but not INDEPENDENT of the value channel.

- **source_dependency** — A meta / audit channel (Art. XI), not a value predictor: it measures HOW independent each claim is, not what value a sign has. Finding: 0/59 correspondences rest on a PRIMARY value attestation (52 litindex-seed + 7 bridge, all secondary); the only primary legs are shape (Salgarella, pending-primary/absent from repo) and Cypriot (S&M) -- both circular. So even the provenance audit shows no independent primary support for any LA<->LB VALUE.

## Source-dependency finding (Art. XI)

- Value-source classes: {'litindex_seed(secondary)': 52, 'datapy_bridge(secondary)': 7}
- Correspondences with a PRIMARY value source: 0/59
- All value claims secondary: YES — the only primary legs are shape (Salgarella, pending-primary / book absent from repo) and Cypriot (S&M 2017), both CIRCULAR.

## Verdict

EXACTLY ONE of the eight channels (admin_function, distributional) is BOTH non-circular AND independently calibratable against a non-circular held-out benchmark -- and it calibrates to NULL. shape and scholarly_correspondence calibrate but are CIRCULAR (confounded with LB identity, capped <=0.75). chronology is not sign-discriminative; stroke_structure and orientation are unpopulated; geography is measurable but has no correspondence-aligned non-circular benchmark; source_dependency is a provenance audit (0/59 correspondences have a primary VALUE source). Net: DECOMPOSITION CONFIRMS no channel yields an independently-calibratable NON-NULL, NON-CIRCULAR LA<->LB value correspondence.

Compliance: no combined score computed; LB value used as grading key only (Art. XII honoured); transfer licence unchanged (SEMANTIC+ NOT_AUTHORIZED, Art. XV). Independently-calibratable channels: ['admin_function']
