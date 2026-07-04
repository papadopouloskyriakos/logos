#!/usr/bin/env bash
# smt_remedy.sh — DESIGNATED TRIPWIRE RESPONSE (do NOT run unless the agentic baseline degrades).
#
# Replaces the earlier "drop 6 -> 10 cores" idea. Re-splits the 32-core container along COMPLETE
# hyperthread sibling pairs so the fence and the agentic system share ZERO silicon:
#   FENCE (hard, 16 logical = 8 full physical cores, both siblings in-container):
#     5,6,7,10,12,15,17,21,37,38,39,42,44,47,49,53
#   PROTECTED (16 singletons whose HT sibling lives OUTSIDE the container):
#     0,1,2,3,4,8,9,11,13,16,18,20,51,54,55,57
# Verified against /sys/.../topology/thread_siblings_list: straddle after re-split = NONE.
# Trade-off: sweep self-contends on SMT within its 8 physical cores (~20-25% slower); still 16
# logical fenced. Result-neutral (affinity only) -> cells stay byte-identical. LIVE re-pin, NO kills.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PAIRED="5,6,7,10,12,15,17,21,37,38,39,42,44,47,49,53"

echo "[remedy] re-pinning all live sweep tasks onto the paired fence: $PAIRED"
n=0
for pid in $(pgrep -x python3); do
  cl=$(tr '\0' ' ' </proc/$pid/cmdline 2>/dev/null || true)
  case "$cl" in *resume_sweep.py*) : ;; *) continue;; esac
  # re-pin the process AND every thread (-a); children inherit going forward
  taskset -a -pc "$PAIRED" "$pid" >/dev/null 2>&1 && n=$((n+1)) || echo "  warn: could not re-pin $pid"
done
echo "[remedy] re-pinned $n live sweep processes (threads included)."

# rewrite the launcher's fence so RESUMED/new cells use the paired fence too
sed -i 's/^FENCE=.*/FENCE="'"$PAIRED"'"   # SMT-remedy paired fence (hard physical-core isolation)/' \
    "$ROOT/experiments/sufficiency/run_fenced.sh"
echo "[remedy] run_fenced.sh FENCE updated to the paired set for future launches."

echo "[remedy] VERIFY: no sweep proc on PROTECTED cores 0,1,2,3,4,8,9,11,13,16,18,20,51,54,55,57"
python3 - <<'PY'
import subprocess
prot={0,1,2,3,4,8,9,11,13,16,18,20,51,54,55,57}; bad=[]
for pid in subprocess.check_output(['pgrep','-x','python3']).split():
    pid=pid.decode()
    try: cl=open(f'/proc/{pid}/cmdline','rb').read().replace(b'\x00',b' ').decode()
    except Exception: continue
    if 'resume_sweep.py' not in cl or '--' not in cl: continue
    try: psr=int(subprocess.check_output(['ps','-o','psr=','-p',pid]).strip())
    except Exception: continue
    if psr in prot: bad.append((pid,psr))
print('  paired fence:', 'HOLDING' if not bad else f'BREACH {bad}')
PY
