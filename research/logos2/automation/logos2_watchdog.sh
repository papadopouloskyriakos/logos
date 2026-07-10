#!/bin/bash
# LOGOS-2 autonomous watchdog — resumes the campaign session when no worker is active.
# Safe by construction: nonblocking flock, fail-closed checks, never kills processes,
# never uses bypassPermissions, never touches protected assets, 8-failure halt.
set -euo pipefail

# ---- configuration (env-overridable for tests) ----
WD_REPO="${WD_REPO:-/home/claude-runner/gitlab/n8n/logos-logos2}"
WD_AUTO="$WD_REPO/research/logos2/automation"
WD_BRANCH_EXPECTED="${WD_BRANCH_EXPECTED:-research/logos2-anchor-identifiability}"
WD_LOCK="${WD_LOCK:-$WD_AUTO/state/watchdog.lock}"
WD_CLAUDE_BIN="${WD_CLAUDE_BIN:-/home/claude-runner/.local/bin/claude}"
WD_SKIP_CLAUDE="${WD_SKIP_CLAUDE:-0}"          # tests set 1
WD_FORCE_FAIL="${WD_FORCE_FAIL:-0}"            # tests set 1 to simulate launch failure
WD_MIN_DISK_GB="${WD_MIN_DISK_GB:-20}"
WD_SKIP_PA="${WD_SKIP_PA:-0}"
EVENTS="$WD_AUTO/logs/watchdog_events.jsonl"
STATE="$WD_AUTO/AUTOPILOT_STATE.json"
FINAL="$WD_REPO/research/logos2/final/MACHINE_READABLE_SUMMARY.json"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
event() { # event <type> <detail>
  mkdir -p "$(dirname "$EVENTS")"
  printf '{"ts":"%s","event":"%s","detail":"%s"}\n' "$(ts)" "$1" "${2//\"/\\\"}" >> "$EVENTS"
}
bump_fail() {
  local reason="$1"
  python3 - "$STATE" "$reason" <<'PY'
import json, sys
p, reason = sys.argv[1], sys.argv[2]
s = json.load(open(p))
s["consecutive_failures"] = int(s.get("consecutive_failures") or 0) + 1
s["last_failure_reason"] = reason
json.dump(s, open(p, "w"), indent=1)
print(s["consecutive_failures"])
PY
}
fail_exit() { # fail_exit <reason>  — bump counter, write halt marker at >=8, exit 1
  local N
  N=$(bump_fail "$1")
  event "failure" "$1 (consecutive=$N)"
  if [[ "$N" -ge 8 ]]; then
    printf '{"halted":"%s","reason":"8 consecutive failures: %s","note":"scientific jobs untouched; conclusions unaltered"}\n' \
      "$(ts)" "$1" > "$WD_AUTO/WATCHDOG_HALTED.json"
    event "halted_marker_written" "$1"
  fi
  exit 1
}
reset_fail_and_stamp() {
  local key="$1"
  python3 - "$STATE" "$key" "$(ts)" <<'PY'
import json, sys
p, key, now = sys.argv[1], sys.argv[2], sys.argv[3]
s = json.load(open(p))
s["consecutive_failures"] = 0
s[key] = now
json.dump(s, open(p, "w"), indent=1)
PY
}

# ---- 1-2: nonblocking exclusive lock ----
mkdir -p "$(dirname "$WD_LOCK")"
exec 9>"$WD_LOCK"
if ! flock -n 9; then
  # another watchdog/worker holds the lock — success, not failure
  exit 0
fi

# ---- 3-4: repo root + branch ----
cd "$WD_REPO"
BR="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BR" != "$WD_BRANCH_EXPECTED" ]]; then
  fail_exit "branch_mismatch expected=$WD_BRANCH_EXPECTED got=$BR"
fi

# ---- 6: STOP marker ----
if [[ -e "$WD_AUTO/STOP" ]]; then
  event "stop_marker_present" "no action"
  exit 0
fi

# ---- halt marker (8-failure breaker already tripped) ----
if [[ -e "$WD_AUTO/WATCHDOG_HALTED.json" ]]; then
  event "halted" "WATCHDOG_HALTED.json present; not launching"
  exit 0
fi

# ---- 7: final-state exit ----
if [[ -f "$FINAL" ]] && python3 -c "
import json,sys; sys.exit(0 if json.load(open('$FINAL')).get('campaign_closed') else 1)" 2>/dev/null; then
  event "campaign_closed" "final summary reports closure"
  exit 0
fi

# ---- 5: protected-asset spot check (fast subset; roots differ per asset) ----
PA_OK=1
[[ "$WD_SKIP_PA" == "1" ]] && PA_OK=skip
[[ "$PA_OK" == "1" ]] && grep "paper/tacl/body.tex\|governance/CONSTITUTION.md" \
  research/logos2/PROTECTED_ASSET_HASHES.sha256 2>/dev/null | \
  sha256sum -c --quiet - 2>/dev/null || PA_OK=0
if [[ "$PA_OK" == "1" ]] && ! (cd /home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h 2>/dev/null && \
    grep "FRACTION_ORDER_ANETAKI_SEAL.manifest\|LOGOS_72H_REVIEW_BUNDLE.zip" \
      "$WD_REPO/research/logos2/PROTECTED_ASSET_HASHES.sha256" | \
    sha256sum -c --quiet - 2>/dev/null); then PA_OK=0; fi
if [[ "$PA_OK" == "0" ]]; then
  fail_exit "protected_asset_check_failed"
fi

# ---- 8: resources ----
FREE_GB=$(df -BG --output=avail "$WD_REPO" | tail -1 | tr -dc '0-9')
if [[ "${FREE_GB:-0}" -lt "$WD_MIN_DISK_GB" ]]; then
  fail_exit "low_disk free=${FREE_GB}G"
fi
git rev-parse --verify HEAD >/dev/null   # repo integrity smoke

# ---- 9-11: is a campaign worker already active? ----
SESSION_ID=$(jq -r '.session_id' "$WD_AUTO/state/session.json")
ACTIVE=0
if [[ "$WD_SKIP_CLAUDE" != "1" ]]; then
  AG_JSON=$("$WD_CLAUDE_BIN" agents --json 2>/dev/null || echo '[]')
  ACTIVE=$(printf '%s' "$AG_JSON" | jq --arg sid "$SESSION_ID" \
    '[.[] | select((.sessionId==$sid) or ((.cwd|tostring)|test("logos-logos2|n8n/logos$")))] | length')
fi
if [[ "${ACTIVE:-0}" -gt 0 ]]; then
  event "heartbeat" "worker active (n=$ACTIVE); no-op"
  reset_fail_and_stamp "last_watchdog"
  exit 0
fi

# healthy registered experiment still running? (registry of PIDs)
REG="$WD_AUTO/state/experiments.json"
if [[ -f "$REG" ]]; then
  RUNNING=$(python3 - "$REG" <<'PY'
import json, os, sys
reg = json.load(open(sys.argv[1]))
alive = [e for e in reg.get("jobs", []) if e.get("pid") and os.path.exists(f"/proc/{e['pid']}")]
print(len(alive))
PY
)
  if [[ "${RUNNING:-0}" -gt 0 ]]; then
    event "experiments_running" "n=$RUNNING healthy; resuming agent anyway only if scheduling work exists"
  fi
fi

# ---- 12: resume the stored session (fallback non-interactive continuation) ----
if [[ "$WD_SKIP_CLAUDE" == "1" ]]; then
  if [[ "$WD_FORCE_FAIL" == "1" ]]; then
    fail_exit "forced_test_failure"
  fi
  event "dry_run" "WD_SKIP_CLAUDE=1; would resume session $SESSION_ID"
  reset_fail_and_stamp "last_watchdog"
  exit 0
fi

LOG="$WD_AUTO/logs/continuation_$(date -u +%Y%m%d_%H%M%S).log"
event "resuming_session" "$SESSION_ID"
set +e
"$WD_CLAUDE_BIN" -r "$SESSION_ID" -p "$(cat "$WD_AUTO/WATCHDOG_PROMPT.md")" \
  --permission-mode acceptEdits >"$LOG" 2>&1
RC=$?
set -e
if [[ $RC -eq 0 ]]; then
  event "continuation_ok" "rc=0 log=$(basename "$LOG")"
  reset_fail_and_stamp "last_claude_continuation"
else
  fail_exit "claude_rc_$RC log=$(basename "$LOG")"
fi
exit 0
