#!/usr/bin/env python3
"""Assumption-register enforcement hook (Constitution v2.0/2.1 Art. XVIII).

Art. XVIII: a FALSE (or STALE) load-bearing premise BLOCKS downstream execution. A stage declares the
assumptions it depends on and calls `require()` at entry; if any is FALSE/STALE it raises (fail closed).
Reads governance/assumption_register.json (schema v2, append-only). Deterministic; no DB.

CLI:
    python3 scripts/assumption_gate.py            # list blocking (FALSE/STALE) load-bearing premises
    python3 scripts/assumption_gate.py A01 A06    # check a stage's dependencies
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = os.path.join(_REPO, "governance", "assumption_register.json")
BLOCKING_STATUSES = {"FALSE", "STALE"}


def load_register(path=REGISTER):
    with open(path) as f:
        return json.load(f)


def _by_id(reg):
    return {a["assumption_id"]: a for a in reg["assumptions"]}


def status_of(aid, reg=None):
    reg = reg or load_register()
    a = _by_id(reg).get(aid)
    if a is None:
        raise KeyError(f"unknown assumption '{aid}' (Art. XVIII/XVI: fail loud)")
    return a.get("current_status", a.get("status"))


def blocking(reg=None):
    """All load-bearing premises whose current status BLOCKS execution (FALSE/STALE)."""
    reg = reg or load_register()
    return [a["assumption_id"] for a in reg["assumptions"]
            if a.get("load_bearing") and a.get("current_status", a.get("status")) in BLOCKING_STATUSES]


def check(assumption_ids, reg=None):
    """Assess a stage's declared dependencies. Returns {ok, blocked:[{id,status,statement}], ...}."""
    reg = reg or load_register()
    by = _by_id(reg)
    blocked = []
    for aid in assumption_ids:
        a = by.get(aid)
        if a is None:
            raise KeyError(f"unknown assumption '{aid}' (Art. XVIII/XVI: fail loud)")
        st = a.get("current_status", a.get("status"))
        if a.get("load_bearing") and st in BLOCKING_STATUSES:
            blocked.append({"id": aid, "status": st, "statement": a["statement"]})
    return {"ok": not blocked, "blocked": blocked, "checked": list(assumption_ids)}


def require(assumption_ids, reg=None):
    """Fail-closed gate (Art. XVIII): raise if any declared dependency is FALSE/STALE."""
    r = check(assumption_ids, reg)
    if not r["ok"]:
        ids = ", ".join(f"{b['id']}({b['status']})" for b in r["blocked"])
        raise RuntimeError(f"BLOCKED by FALSE/STALE load-bearing assumption(s): {ids} — Art. XVIII")
    return True


def main():
    args = sys.argv[1:]
    reg = load_register()
    if not args:
        print("blocking (FALSE/STALE) load-bearing premises:", blocking(reg) or "none")
        return
    print(json.dumps(check(args, reg), indent=1))


if __name__ == "__main__":
    main()
