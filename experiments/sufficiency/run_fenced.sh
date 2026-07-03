#!/usr/bin/env bash
# run_fenced.sh — launch the sweep scheduler HARD-FENCED onto the sweep's 16 cores.
#
# The container's assignable cpuset is 32 NON-CONTIGUOUS host cores
# (0-13,15-18,20-21,37-39,42,44,47,49,51,53-55,57). The human's "CPUs 16-31 for the sweep,
# 0-15 for the agentic system" maps to halving the SORTED effective set:
#   agentic (protected, low 16):  0-13,15,16
#   sweep   (fence,     high 16):  17,18,20,21,37,38,39,42,44,47,49,51,53,54,55,57
#
# Path: cpuset is NOT delegated to uid 1000 and systemd system-slice creation is Access-denied,
# so this uses the sanctioned FALLBACK: taskset (affinity inherited by all children) + nice 19 +
# ionice -c3. Cell code and pinned params are untouched; affinity/nice/ionice are result-neutral
# (integer edit distance + seeded RNG), so fenced cells stay byte-identical to the 92 completed.
set -euo pipefail
FENCE="17,18,20,21,37,38,39,42,44,47,49,51,53,54,55,57"   # the sweep's 16 cores (high half)
CONC="${1:-4}"                                             # 4 cells x processes=4 = 16 fenced cores
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="$ROOT/runtime/csa_sweep/logs/fenced_$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$(dirname "$LOG")"
echo "$LOG" > "$ROOT/runtime/csa_sweep/logs/CURRENT_LOG"
cd "$ROOT"
exec taskset -c "$FENCE" nice -n 19 ionice -c3 \
     python3 experiments/sufficiency/resume_sweep.py --run --concurrency "$CONC" \
       --host nllei01claude01-fenced >>"$LOG" 2>&1
