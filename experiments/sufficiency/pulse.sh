#!/usr/bin/env bash
# pulse.sh — appends one compact liveness line every 60s to pulse.log. Tail this ONE file:
#   tail -f runtime/csa_sweep/logs/pulse.log
cd "$(dirname "$0")/../.." || exit 0
PULSE=runtime/csa_sweep/logs/pulse.log
while true; do
  DONE=$(ls runtime/csa_sweep/cells/*.json 2>/dev/null | wc -l)
  RUN=$(for pid in $(pgrep -f "resume_sweep.py --cell"); do awk '{print $3}' /proc/$pid/stat 2>/dev/null; done | grep -c R)
  SCHED=$(pgrep -f "resume_sweep.py --run" >/dev/null && echo up || echo DOWN)
  MINCPU=$(for pid in $(pgrep -f "resume_sweep.py --cell"); do
             s=$(pgrep -f "resume_sweep.py --run"|head -1); pp=$(awk '{print $4}' /proc/$pid/stat 2>/dev/null)
             [ "$pp" = "$s" ] && awk '{printf "%.1f\n",($14+$15+$16+$17)/360000}' /proc/$pid/stat 2>/dev/null
           done | sort -n | head -1)
  printf '%s  cells=%d/168  R=%d  sched=%s  min-cell-cumCPU=%sh\n' \
         "$(date -u +%H:%M:%SZ)" "$DONE" "$RUN" "$SCHED" "${MINCPU:-?}" >> "$PULSE"
  sleep 60
done
