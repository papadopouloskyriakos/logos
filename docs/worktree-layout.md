# Worktree layout — ~/gitlab/n8n/

> Tracked canonical copy (in the `logos` repo). A verbatim convenience copy lives at the filesystem
> parent `~/gitlab/n8n/logos-worktrees/README.md`, which is outside every git repo and so cannot be
> committed in place. Paths below are relative to `~/gitlab/n8n/`.

`~/gitlab/n8n/logos-worktrees/` holds **git worktrees of `logos`** (the main repo, where the frozen
TACL paper lives on `main`) — one folder per **closed research/audit campaign branch**. They share
`logos/.git`; they do not duplicate history, only the checked-out files (+ each campaign's gitignored
data).

Consolidated here 2026-07-16 (were flat siblings `../logos-<name>`, cluttering `~/gitlab/n8n/`).

## Inventory (dir → branch)
| dir | branch |
|---|---|
| admin-schema | research/blinded-admin-schema-induction |
| di-mino-301-audit | research/di-mino-301-exact-audit |
| egyptian-calibration | research/egyptian-calibration-gate |
| external-anchors | research/external-minoan-anchors |
| la-lb-continuity | research/la-lb-toponym-continuity |
| la-lb-ritual-feasibility | research/la-lb-ritual-feasibility |
| linear-a-anchor-lattice | research/linear-a-anchor-lattice |
| linear-a-constraint-expansion | research/linear-a-constraint-expansion |
| linear-a-decipherment-foundry | research/linear-a-decipherment-foundry |
| linear-a-frontier-72h | research/linear-a-frontier-72h |
| linear-a-methodology-inventory | audit/linear-a-methodology-master-inventory |
| linear-a-methodology-red-team | audit/linear-a-methodology-inventory-red-team |
| linear-a-relative-phonology-seals | research/linear-a-relative-phonology-seals |
| logos2 | research/logos2-anchor-identifiability |
| no-human-structure | research/no-human-structural-decipherment |
| observable-channels | research/observable-admin-channel-recovery |

All branches are on origin. These are disposable/recreatable:
- list:    `git -C ../logos worktree list`
- remove:  `git -C ../logos worktree remove logos-worktrees/<name>`
- recreate: `git -C ../logos worktree add ../logos-worktrees/<name> <branch>`

## Not here
- **`../logos`** — the main repo (paper, `main`). The only campaign dir outside this folder.

## Note on `logos2`
Moved in here 2026-07-16 once its blockers cleared (LOGOS2_F1B_DAILY cron removed, F1b addendum
done → zero pending items). **Caveat:** ~10 files in this closed campaign still hardcode the old
absolute path `/home/.../logos-logos2/...` (e.g. `battery.py` `SILVER=`, `status.sh` `WD=`,
`data_manifest.sha256`). Harmless — nothing runs them now — but if you ever re-run a closed logos2
script it will point at the old path; fix the constant first.
