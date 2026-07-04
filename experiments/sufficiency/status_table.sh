#!/usr/bin/env bash
# status_table.sh — one formatted sweep status block (for the 30-min heartbeat monitor).
cd "$(dirname "$0")/../.." || exit 0
NOW=$(date -u +%s); RELAUNCH=$(date -u -d '2026-07-03T22:58:41Z' +%s); MK=$((133*3600))
DONE=$(ls runtime/csa_sweep/cells/*.json 2>/dev/null | wc -l); REM=$((168-DONE))
INFLIGHT=$(ls runtime/csa_sweep/cells/*.claim 2>/dev/null | wc -l)
pgrep -f "resume_sweep.py --run" >/dev/null && SCHED=ALIVE || SCHED=DOWN
BREACH=$(python3 experiments/sufficiency/fence_check.py 2>/dev/null); FENCE=$([ -z "$BREACH" ] && echo "HOLDING" || echo "BREACH:$BREACH")
ELAP=$(( (NOW-RELAUNCH) )); LEFT=$(( MK-ELAP )); [ $LEFT -lt 0 ] && LEFT=0
PCT=$(( DONE*100/168 ))
# agentic baseline: 1-min load contribution on the protected low-16 (proxy: total load1)
L1=$(awk '{print $1}' /proc/loadavg)
printf '┌─ CSA sufficiency sweep — %s UTC ─────────────\n' "$(date -u +%Y-%m-%d\ %H:%M)"
printf '│ progress   : %d/168 cells (%d%%)   remaining %d\n' "$DONE" "$PCT" "$REM"
printf '│ in-flight  : %d cells (biggest-first, concurrency 4)\n' "$INFLIGHT"
printf '│ scheduler  : %s        fence: %s\n' "$SCHED" "$FENCE"
printf '│ elapsed    : %dh%02dm since fenced relaunch\n' $((ELAP/3600)) $(((ELAP%3600)/60))
printf '│ ETA (fit)  : ~%.1f days left  (nominal ~5.5d, pess ~7-8d)\n' "$(echo "scale=1;$LEFT/86400"|bc)"
printf '│ load1      : %s (agentic low-16 + sweep high-16)\n' "$L1"
printf '└──────────────────────────────────────────────\n'
