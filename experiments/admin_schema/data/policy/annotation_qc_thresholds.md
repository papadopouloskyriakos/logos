# Annotation QC plan — FROZEN — Stage 5 approved 2026-07-07

## Two-pass protocol

**Pass 1 — independent.** Two independent annotations of the full GOLD_A candidate set if feasible; else a
**stratified subset** large enough to estimate agreement by coarse role, site, and document series (target:
≥30 items per stratum where the stratum exists). Annotators work from source citations + the structural
graph, blind to each other.

**Pass 2 — adjudication.** For every disagreement: preserve BOTH original labels; record the disagreement
category (coarse-role / fine-role / relation / tier); cite the source basis; adjudicate explicitly; never
silently overwrite. Adjudicated agreement is reported **separately** from independent agreement.

## Agreement gate (§X — proposed frozen thresholds)

```
Krippendorff α ≥ 0.80         → eligible for primary coarse-role gold
0.67 ≤ α < 0.80               → provisional / sensitivity-only
α < 0.67                       → NOT eligible as primary gold
```

Also report: raw agreement; Cohen's κ where applicable; class-specific confusion; and agreement **by site ·
by document series · by support type**. A class below 0.80 is demoted out of GOLD_A / the primary gate.

## Required double annotation (§X)

Independent double annotation required for: (1) every item in the sealed evaluation set; (2) every
load-bearing GOLD_A non-trivial item; (3) a stratified train/dev sample covering every coarse role, **site
(19), document series (23), and support type**. Full double annotation preferred if feasible.

## Guards

- Adjudicated agreement is NOT treated as independent agreement.
- Low-agreement fine classes → coarse-only.
- Damage-dependent items cannot be GOLD_A regardless of agreement.
- Annotator identity + adjudicator recorded per row (`annotator_1/2`, `adjudicator`, `adjudication_status`).
