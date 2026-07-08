# Branch & worktree map (audit basis)

Audit branch `audit/linear-a-methodology-master-inventory` forked from `main@6fd4f20`. `main` local HEAD 6fd4f20;
**NOTE `github/main@7c509c6`** carries later submission-docs commits (7c509c6, 1aa1249) ahead of local main — the
paper/submission state, not methodology. 1 tag: `review-fixes-2026-07-01`. `github/research/…-foundry@f9acd9a` is a
stale partial push (local/origin foundry = 09f7ef9).

| campaign lineage | branch | HEAD | worktree | own experiment dir(s) |
|---|---|---|---|---|
| paper + core methods | main | 6fd4f20 | logos | docs/findings (26) + shared foundations |
| 12h "crack LA" campaign | main | 6fd4f20 | logos | linear_a_campaign |
| constraint-expansion | research/linear-a-constraint-expansion | 2996567 | logos-linear-a-constraint-expansion | linear_a_constraint_expansion |
| foundry | research/linear-a-decipherment-foundry | 09f7ef9 | logos-linear-a-decipherment-foundry | linear_a_foundry |
| relative-phonology/seals | research/linear-a-relative-phonology-seals | 8a98607 | logos-linear-a-relative-phonology-seals | linear_a_relative_phonology |
| di-mino *301 audit | research/di-mino-301-exact-audit | 1cd3f86 | logos-di-mino-301-audit | di_mino_301_audit |
| blinded admin-schema | research/blinded-admin-schema-induction | dd98f1a | logos-admin-schema | admin_schema |
| no-human structural | research/no-human-structural-decipherment | 946e53e | logos-no-human-structure | no_human_structure |
| observable admin channels | research/observable-admin-channel-recovery | 71eb0e6 | logos-observable-channels | observable_channels |
| egyptian calibration gate | research/egyptian-calibration-gate | dfa291e | logos-egyptian-calibration | egyptian_calibration |
| external minoan anchors | research/external-minoan-anchors | 3310e4b | logos-external-anchors | external_anchors |
| LA-LB toponym continuity | research/la-lb-toponym-continuity | 87b4dea | logos-la-lb-continuity | la_lb_continuity |
| LA-LB ritual feasibility | research/la-lb-ritual-feasibility | e6ee2b4 | logos-la-lb-ritual-feasibility | la_lb_ritual |
| tamburini baseline repro | tamburini-baseline-repro | f4a5b4e | (no worktree) | scripts/baselines |
| shared foundations | (on main + inherited) | 6fd4f20 | logos | crossscript_gate, representation_audit, schema_induction, schema_recon, segmentation_extension, sufficiency |

Reports/data in research branches are gitignored but force-added (tracked, present on-disk in each worktree).
Corpus is symlinked/gitignored. Authoritative worktree per unique dir chosen = owning/latest branch (see
data/ARTIFACT_INDEX.csv, 923 artifacts).
