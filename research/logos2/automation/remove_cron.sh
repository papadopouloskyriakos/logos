#!/bin/bash
set -euo pipefail
BLOCK_BEGIN="# BEGIN LOGOS2_AUTOPILOT"; BLOCK_END="# END LOGOS2_AUTOPILOT"
read_cron() { if [[ -n "${CRON_FIXTURE:-}" ]]; then cat "$CRON_FIXTURE" 2>/dev/null || true; else crontab -l 2>/dev/null || true; fi; }
write_cron() { if [[ -n "${CRON_FIXTURE:-}" ]]; then cat > "$CRON_FIXTURE"; else crontab -; fi; }
CUR=$(read_cron)
printf '%s\n' "$CUR" | awk -v b="$BLOCK_BEGIN" -v e="$BLOCK_END" \
  'index($0,b)==1{skip=1} !skip{print} index($0,e)==1{skip=0}' | write_cron
echo "LOGOS2 block removed; unrelated entries preserved."
