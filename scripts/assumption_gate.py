#!/usr/bin/env python3
"""Assumption-register enforcement hook (Constitution v2.0/2.1 Art. XVIII).

Art. XVIII ("...explicit, VERIFIED, and pinned"): a load-bearing premise that is NOT affirmatively VERIFIED
(i.e. FALSE / STALE / UNKNOWN / PARTIAL / missing) BLOCKS downstream execution — an unverified premise
cannot silently be load-bearing (guilty until proven, Art. IV/XVI). A stage declares the assumptions it
depends on and calls `require()` at entry; if any is not VERIFIED it raises (fail closed). Reads
governance/assumption_register.json (schema v2, append-only). Deterministic; no DB.

CLI:
    python3 scripts/assumption_gate.py            # list blocking (not-VERIFIED) load-bearing premises
    python3 scripts/assumption_gate.py A01 A06    # check a stage's dependencies
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = os.path.join(_REPO, "governance", "assumption_register.json")
# Art. XVIII ("...explicit, VERIFIED, and pinned") + fail-closed doctrine: a load-bearing premise is
# non-blocking ONLY when affirmatively VERIFIED. FALSE/STALE/UNKNOWN/PARTIAL/missing/unrecognized all block
# (guilty until proven — an unverified premise cannot silently be load-bearing).
NONBLOCKING_STATUS = "VERIFIED"


def load_register(path=REGISTER):
    with open(path) as f:
        return json.load(f)


def _by_id(reg):
    return {a["assumption_id"]: a for a in reg["assumptions"]}


def _status(a):
    st = a.get("current_status", a.get("status"))
    return st.strip().upper() if isinstance(st, str) else None


def status_of(aid, reg=None):
    reg = reg or load_register()
    a = _by_id(reg).get(aid)
    if a is None:
        raise KeyError(f"unknown assumption '{aid}' (Art. XVIII/XVI: fail loud)")
    return _status(a)


def _blocks(a):
    """A load-bearing premise blocks unless it is affirmatively VERIFIED."""
    return bool(a.get("load_bearing")) and _status(a) != NONBLOCKING_STATUS


def blocking(reg=None):
    """All load-bearing premises whose current status BLOCKS execution (anything but VERIFIED)."""
    reg = reg or load_register()
    return [a["assumption_id"] for a in reg["assumptions"] if _blocks(a)]


def check(assumption_ids, reg=None):
    """Assess a stage's declared dependencies. Returns {ok, blocked:[{id,status,statement}], ...}."""
    reg = reg or load_register()
    by = _by_id(reg)
    blocked = []
    for aid in assumption_ids:
        a = by.get(aid)
        if a is None:
            raise KeyError(f"unknown assumption '{aid}' (Art. XVIII/XVI: fail loud)")
        if _blocks(a):
            blocked.append({"id": aid, "status": _status(a), "statement": a["statement"]})
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
