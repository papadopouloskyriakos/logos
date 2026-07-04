#!/usr/bin/env bash
# status_table.sh — one formatted sweep status block (30-min heartbeat monitor).
cd "$(dirname "$0")/../.." || exit 0
NOW=$(date -u +%s); RELAUNCH=$(date -u -d '2026-07-03T22:58:41Z' +%s); MK=$((133*3600))
DONE=$(ls runtime/csa_sweep/cells/*.json 2>/dev/null | wc -l); REM=$((168-DONE))
INFLIGHT=$(ls runtime/csa_sweep/cells/*.claim 2>/dev/null | wc -l)
pgrep -f "resume_sweep.py --run" >/dev/null && SCHED=ALIVE || SCHED=DOWN
BREACH=$(python3 experiments/sufficiency/fence_check.py 2>/dev/null); FENCE=$([ -z "$BREACH" ] && echo HOLDING || echo "BREACH:$BREACH")
ELAP=$(( NOW-RELAUNCH )); LEFT=$(( MK-ELAP )); [ $LEFT -lt 0 ] && LEFT=0
DTEN=$(( LEFT*10/86400 ))                    # days*10 for one decimal, integer math
CELLS=$(python3 - <<'PP'
import os,subprocess
sched=subprocess.check_output(['pgrep','-f','resume_sweep.py --run']).split()[:1]
sched=sched[0].decode() if sched else ''
out=[]
for pid in subprocess.check_output(['pgrep','-f','resume_sweep.py --cell']).split():
    pid=pid.decode()
    try:
        st=open(f'/proc/{pid}/stat').read().split()
        if st[3]!=sched: continue                      # parents only (PPID=scheduler)
        cpuh=(int(st[13])+int(st[14])+int(st[15])+int(st[16]))/100/3600
        cl=open(f'/proc/{pid}/cmdline','rb').read().split(b'\x00')
        cell=[c.decode() for c in cl if b':' in c and b'-' in c][:1]
        out.append(f"{cell[0].split(':')[0][:3]}{cell[0].split(':')[1]}s{cell[0].split(':')[2]}={cpuh:.1f}h")
    except Exception: pass
print(' '.join(sorted(out)) or 'none')
PP
)
RUN=$(for pid in $(pgrep -f "resume_sweep.py --cell"); do awk '{print $3}' /proc/$pid/stat 2>/dev/null; done | grep -c R); TOT=$(pgrep -cf "resume_sweep.py --cell")
PCT=$(( DONE*100/168 )); L1=$(awk '{print $1}' /proc/loadavg)
PSI=$(awk -F'[= ]' '/some/{print $5}' /proc/pressure/cpu 2>/dev/null)   # cpu stall avg60 %
SWAP=$(free -m | awk '/Swap/{print $3}')
RQP=$(python3 - <<'PP'
import subprocess
prot=set(range(14))|{15,16}; n=0
for ln in subprocess.check_output(['ps','-eo','psr,stat,args','--no-headers']).decode().splitlines():
    x=ln.split(None,2)
    if len(x)<3 or int(x[0]) not in prot: continue
    if 'resume_sweep.py' in x[2]: continue
    if x[1].startswith('R'): n+=1
print(n)
PP
)
echo    "┌─ CSA sufficiency sweep — $(date -u '+%Y-%m-%d %H:%M') UTC ──────────"
echo    "│ progress  : ${DONE}/168 cells (${PCT}%)   remaining ${REM}"
echo    "│ in-flight : ${INFLIGHT} cells (biggest-first, concurrency 4 = 16 fenced cores)"
echo    "│ scheduler : ${SCHED}      fence: ${FENCE}      running: ${RUN}/${TOT} tasks in R (executing)"
printf  "│ elapsed   : %dh%02dm since fenced relaunch\n" $((ELAP/3600)) $(((ELAP%3600)/60))
echo    "│ ETA (fit) : ~${DTEN:0:-1}.${DTEN: -1} days left  (nominal ~5.5d, pess ~7-8d)"
echo    "│ agentic   : cpu-stall(avg60) ${PSI}%  protected-runq ${RQP}/16  swap ${SWAP}MB  [tripwire=stall↑/runq>>16/swap>0]"
echo    "│ load1     : ${L1}  (raw; inflated by sweep launch-bound tasks — not the tripwire metric)"
echo    "│ liveness  : per-cell cumCPU ${CELLS} (must RISE each tick; flat=hang)"
echo    "└──────────────────────────────────────────────"
