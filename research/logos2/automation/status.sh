#!/bin/bash
set -euo pipefail
WD=/home/claude-runner/gitlab/n8n/logos-logos2/research/logos2/automation
echo "== autopilot state =="; cat "$WD/AUTOPILOT_STATE.json"
echo "== last 5 watchdog events =="; tail -5 "$WD/logs/watchdog_events.jsonl" 2>/dev/null || echo "(none)"
echo "== cron block =="; crontab -l 2>/dev/null | sed -n '/# BEGIN LOGOS2_AUTOPILOT/,/# END LOGOS2_AUTOPILOT/p'
echo "== active agents =="; /home/claude-runner/.local/bin/claude agents --json 2>/dev/null | jq -r '.[] | "\(.pid) \(.status) \(.cwd)"' || true
