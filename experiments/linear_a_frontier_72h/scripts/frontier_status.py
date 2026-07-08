#!/usr/bin/env python3
"""frontier_status.py — zero-token status/ETA/progress printer for the Linear A frontier-72h campaign.

Prints (to the terminal, no LLM tokens): the mission one-liner, the coordinator/worker architecture
reminder (GLM via scripts, not Claude subagents), current UTC + local datetime, the campaign clock +
ETA to the finalization gate, whether finalization is authorized, the epoch-ledger verdict tally, the
latest banked epoch, and whether a GLM worker/epoch process is currently running.

Called by the 10-minute cron reminder and runnable ad hoc:  python3 <this>
"""
from __future__ import annotations
import json, os, subprocess, sys, datetime

EXP = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h/experiments/linear_a_frontier_72h"
BAR = "=" * 72


def _clock() -> dict:
    try:
        r = subprocess.run([sys.executable, "scripts/clock_check.py"], cwd=EXP,
                           capture_output=True, text=True, timeout=30)
        # clock_check prints a JSON dict (exit 1 while finalization not authorized)
        return json.loads(r.stdout.strip() or "{}")
    except Exception as e:
        return {"error": f"clock_check failed: {e}"}


def _ledger() -> dict:
    path = os.path.join(EXP, "EPOCH_LEDGER.yaml")
    try:
        import yaml
        L = yaml.safe_load(open(path))
    except Exception as e:
        return {"error": f"ledger load failed: {e}"}
    rows = L if isinstance(L, list) else (L.get("epochs") or L.get("ledger") or [])
    if isinstance(rows, dict):
        rows = list(rows.values())
    rows = [r for r in rows if isinstance(r, dict) and r.get("epoch_id")]
    # dedup by epoch_id (last row wins — captures the final attempt/superseding verdict per epoch)
    by_id: dict = {}
    for r in rows:
        by_id[r["epoch_id"]] = r
    distinct = list(by_id.values())
    tally: dict = {}
    for r in distinct:
        v = str(r.get("verdict", "?")).split()[0] if r.get("verdict") else "?"
        tally[v] = tally.get(v, 0) + 1
    latest = distinct[-1] if distinct else {}
    return {"n": len(distinct), "tally": tally,
            "latest_id": latest.get("epoch_id"),
            "latest_verdict": str(latest.get("verdict", "?")).split()[0] if latest.get("verdict") else "?"}


def _worker_running() -> str:
    try:
        r = subprocess.run(["ps", "-eo", "pid,etime,cmd", "--no-headers"], capture_output=True, text=True, timeout=15)
        hits = [ln for ln in r.stdout.splitlines()
                if any(k in ln for k in ("zai_agent", "epoch_runner", "run_e0", "run_epoch")) and "grep" not in ln]
        return f"YES ({len(hits)} proc)" if hits else "no (idle)"
    except Exception:
        return "unknown"


def _fmt_eta(hours) -> str:
    if hours is None:
        return "?"
    h = float(hours)
    if h <= 0:
        return "0h (deadline reached)"
    d, rem = divmod(h, 24)
    return f"{h:.1f}h  (~{int(d)}d {rem:.1f}h)"


def main() -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    now_local = now.astimezone()
    c = _clock()
    L = _ledger()
    fin = bool(c.get("finalization_authorized"))
    print(BAR)
    print("LINEAR A — FRONTIER-72h CAMPAIGN  ·  cron reminder + status")
    print("MISSION: build independent symmetry-breaking channels; retain only sign-systems that")
    print("  make held-out predictions; earn a REAL Linear A reading, refuse a fitted one. L2/L3 ceiling.")
    print("ARCH: Claude = coordinator/verify/bank; GLM-5.2 = worker via scripts/zai_agent.py +")
    print("  scripts/epoch_runner.py (gated). NO Claude subagents for the labour. Mechanical gate decides.")
    print(BAR)
    print(f"NOW (UTC)   : {now.strftime('%Y-%m-%d %H:%M:%S')}Z")
    print(f"NOW (local) : {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    if "error" in c:
        print(f"CLOCK       : ERROR — {c['error']}")
    else:
        print(f"WINDOW      : {c.get('campaign_end_utc','?')}  (finalization gate)")
        print(f"ETA to gate : {_fmt_eta(c.get('hours_remaining'))}")
        print(f"EPOCHS      : {c.get('completed_epochs','?')} done  (minimum {c.get('minimum_epochs','?')})")
        print(f"GATES       : time_gate={c.get('time_gate')}  epoch_gate={c.get('epoch_gate')}")
        print(f"FINALIZE?   : {'AUTHORIZED' if fin else 'BLOCKED — do NOT finalize; keep running'}")
    if "error" in L:
        print(f"LEDGER      : ERROR — {L['error']}")
    else:
        print(f"LEDGER      : {L['n']} epochs  ·  latest {L['latest_id']} = {L['latest_verdict']}")
        print(f"VERDICTS    : " + "  ".join(f"{k}×{v}" for k, v in sorted(L['tally'].items(), key=lambda x: -x[1])))
    print(f"WORKER NOW  : {_worker_running()}")
    print(BAR)
    if not fin:
        print("NEXT: if worker idle + clock not expired + unblocked work remains → advance ONE gated")
        print("  epoch via epoch_runner (GLM), verify independently, bank. Capstone: §12 exhaustion map.")
    else:
        print("NEXT: finalization gate OPEN — assemble the §12 exhaustion map + mechanical FINAL verdict.")
    print(BAR)


if __name__ == "__main__":
    main()
