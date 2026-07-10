#!/bin/bash
# Idempotent LOGOS2 watchdog cron installation. Preserves unrelated entries; replaces only
# the LOGOS2_AUTOPILOT marker block. CRON_FIXTURE=<file> switches to fixture mode for tests.
set -euo pipefail
WD=/home/claude-runner/gitlab/n8n/logos-logos2/research/logos2/automation
BLOCK_BEGIN="# BEGIN LOGOS2_AUTOPILOT"
BLOCK_END="# END LOGOS2_AUTOPILOT"
read_cron() { if [[ -n "${CRON_FIXTURE:-}" ]]; then cat "$CRON_FIXTURE" 2>/dev/null || true; else crontab -l 2>/dev/null || true; fi; }
write_cron() { if [[ -n "${CRON_FIXTURE:-}" ]]; then cat > "$CRON_FIXTURE"; else crontab -; fi; }
CUR=$(read_cron)
STRIPPED=$(printf '%s\n' "$CUR" | awk -v b="$BLOCK_BEGIN" -v e="$BLOCK_END" \
  'index($0,b)==1{skip=1} !skip{print} index($0,e)==1{skip=0}')
NEW_BLOCK=$(cat <<CRON
$BLOCK_BEGIN
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:/home/claude-runner/.local/bin
*/15 * * * * $WD/logos2_watchdog.sh >> $WD/logs/cron.log 2>&1
$BLOCK_END
CRON
)
{ printf '%s\n' "$STRIPPED" | sed '/^$/N;/^\n$/D'; printf '%s\n' "$NEW_BLOCK"; } | write_cron
echo "installed. verification:"
read_cron | sed -n "/$BLOCK_BEGIN/,/$BLOCK_END/p"
