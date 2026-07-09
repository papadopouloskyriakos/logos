"""F12 launch gate — is the morphogenesis (F11) block terminal, so E097 may start?

Mechanical, not a judgment call. The F12 CROSS_DISCIPLINARY family is WAITING_ON_MORPHOGENESIS until every F11
reserved epoch (E091-E096) has reached a terminal status:
  BANKED / COMPLETE  -> done
  DE_AUTHORIZED / TERMINATED / CLOSED -> resolved (not going to run)
An epoch still RESERVED_ACTIVE / RUNNING / PROPOSED blocks the launch.
Also requires the campaign clock to be unexpired-irrelevant (F12 runs INSIDE the campaign; finalization stays
blocked regardless). Prints MORPH_TERMINAL: true/false and the blocking epochs.
"""
import sys, os, re, json

REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
LEDGER = os.path.join(REPO, "experiments/linear_a_frontier_72h/EPOCH_LEDGER.yaml")
MORPH_EPOCHS = [f"EPOCH-{n:03d}" for n in range(91, 97)]          # E091..E096
TERMINAL = {"BANKED", "COMPLETE", "COMPLETED", "DE_AUTHORIZED", "TERMINATED", "CLOSED", "SUPERSEDED"}
BLOCKING = {"RESERVED_ACTIVE", "RUNNING", "PROPOSED", "WAITING_ON_MORPHOGENESIS"}


def last_status_per_epoch(path):
    """Parse the ledger for each epoch's LAST status: entry (last-wins, matching the append-only convention)."""
    status = {}
    cur = None
    with open(path) as fh:
        for line in fh:
            m = re.match(r"\s*-?\s*epoch_id:\s*([A-Za-z0-9-]+)", line)
            if m:
                cur = m.group(1); continue
            s = re.match(r"\s*status:\s*([A-Za-z_]+)", line)
            if s and cur:
                status[cur] = s.group(1).strip()
    return status


def morph_terminal():
    st = last_status_per_epoch(LEDGER)
    blocking = []
    for e in MORPH_EPOCHS:
        s = st.get(e, "MISSING")
        if s not in TERMINAL:
            blocking.append((e, s))
    return (len(blocking) == 0), blocking, st


if __name__ == "__main__":
    ok, blocking, st = morph_terminal()
    print("MORPH_TERMINAL:", ok)
    print("F11 statuses:", {e: st.get(e, "MISSING") for e in MORPH_EPOCHS})
    if blocking:
        print("BLOCKING (must be banked or de-authorized/terminated before E097 launches):")
        for e, s in blocking:
            print(f"  {e}: {s}")
        print("\nACTION: complete/terminate the blocking F11 epochs first; F12 stays WAITING_ON_MORPHOGENESIS.")
    else:
        print("ACTION: morphogenesis is terminal -> flip F12 E097-E102 status to ACTIVE and launch EPOCH-097.")
    sys.exit(0 if ok else 1)
