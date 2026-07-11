#!/usr/bin/env bash
# LOGOS-2 post-closure F1b daily check — conservative, once per day via cron.
# ONLY duty: log CSA-sweep health; when the sweep ends, resume the session ONCE for the
# frozen F1b addendum flow (imports/E201_F1B). Never reopens the campaign.
set -euo pipefail
PC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$PC/logs/f1b_daily.jsonl"
DONE="$PC/state_f1b_triggered"
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
ev() { printf '{"ts":"%s","event":"%s","detail":"%s"}\n' "$(ts)" "$1" "$2" >> "$LOG"; }
exec 9>"$PC/.f1b.lock"; flock -n 9 || exit 0
[ -e "$DONE" ] && { ev "noop" "F1b already triggered"; exit 0; }

if pgrep -f "experiments/sufficiency/resume_sweep.py" >/dev/null; then
  N=$(pgrep -cf "CSA_OptMatcher|resume_sweep" || echo 0)
  ev "sweep_running" "scheduler alive; ${N} related processes"
  exit 0
fi

# scheduler gone: COMPLETE only if no cells are pending; a crash leaves pending cells
PENDING=$(python3 - <<'PY'
import sys; sys.path.insert(0, "experiments/sufficiency")
import resume_sweep as rs
print(len(rs.pending_cells("runtime/csa_sweep")))
PY
)
if [ "${PENDING:-1}" -gt 0 ]; then
  ev "sweep_not_running_incomplete" "scheduler gone with ${PENDING} cells pending — crashed/stopped, NOT complete; no trigger"
  exit 0
fi

# sweep genuinely complete -> trigger the addendum flow exactly once
touch "$DONE"
ev "sweep_ended" "resuming session once for the F1b addendum"
SID=$(jq -r '.session_id' "$PC/../automation/state/session.json")
claude -r "$SID" -p "$(cat "$PC/F1B_PROMPT.md")" --permission-mode acceptEdits \
  >> "$PC/logs/f1b_continuation.log" 2>&1 || ev "resume_failed" "manual follow-up needed; see f1b_continuation.log"
exit 0
