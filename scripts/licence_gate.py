#!/usr/bin/env python3
"""Transfer-licence enforcement (Constitution v2.1 Art. XV + B6).

Art. XV: a lower licence never implies a higher one; no Linear A output above the earned licence's layer.
B6: a claim's confidence class is capped by the transfer licence earned for its claim layer. This gate
reads governance/transfer_licences.json and refuses a claim worded above what is licensed. Deterministic.

CLI:
    python3 scripts/licence_gate.py                 # print current licence states
    python3 scripts/licence_gate.py L3 SUPPORTED    # may an L3 claim be SUPPORTED? (checks FUNCTIONAL)
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LICENCES = os.path.join(_REPO, "governance", "transfer_licences.json")

# Article V claim layer -> the transfer licence that gates Linear A output at that layer (Art. XV)
LAYER_LICENCE = {
    "L0": None, "L1": None, "L2": "STRUCTURAL_TRANSFER_LICENSE", "L3": "FUNCTIONAL_TRANSFER_LICENSE",
    "L4": "SEMANTIC_TRANSFER_LICENSE", "L5": "LEXICAL_TRANSFER_LICENSE", "L6": "PHONETIC_TRANSFER_LICENSE",
    "L7": "LANGUAGE_IDENTIFICATION_LICENSE", "L8": "LANGUAGE_IDENTIFICATION_LICENSE",
    "L9": "TRANSLATION_LICENSE",
}
CONF_ORDER = ["SPECULATIVE", "EXPLORATORY", "SUPPORTED", "HELD_OUT_SUPPORTED", "REPLICATED",
              "PROVISIONALLY_ACCEPTED", "ACCEPTED"]


def load_licences(path=LICENCES):
    with open(path) as f:
        return json.load(f)


def state_of(licence, lic=None):
    lic = lic or load_licences()
    entry = lic["licences"].get(licence)
    if entry is None:
        raise KeyError(f"unknown licence '{licence}'")
    return entry["state"]


def earned(licence, lic=None):
    return state_of(licence, lic) == "EARNED"


def check_claim(claim_layer, confidence, linear_a=True, lic=None):
    """Enforce Art. XV + B6 for a claim. Returns {allowed, reason, licence, licence_state, max_confidence}.

    - Linear A output at a layer with an unearned licence and confidence > SUPPORTED is BLOCKED (B6).
    - Linear A output at L3+ with an unearned licence is BLOCKED outright (Art. XV — no functional/semantic/
      phonetic LA claim without the licence)."""
    lic = lic or load_licences()
    licence = LAYER_LICENCE.get(claim_layer)
    if licence is None:                                       # L0/L1: observation, no licence needed
        return {"allowed": True, "reason": "L0/L1 observation — no transfer licence required",
                "licence": None, "licence_state": None, "max_confidence": "ACCEPTED"}
    st = state_of(licence, lic)
    is_earned = st == "EARNED"
    max_conf = "ACCEPTED" if is_earned else "SUPPORTED"       # B6: capped at SUPPORTED without the licence
    layer_n = int(claim_layer[1:])
    # Art. XV: LA output above L2 requires the licence outright
    if linear_a and layer_n >= 3 and not is_earned:
        return {"allowed": False, "reason": f"Linear A L{layer_n} output requires {licence} (state {st}) — Art. XV",
                "licence": licence, "licence_state": st, "max_confidence": max_conf}
    if confidence and confidence in CONF_ORDER and CONF_ORDER.index(confidence) > CONF_ORDER.index(max_conf):
        return {"allowed": False,
                "reason": f"confidence {confidence} exceeds the cap {max_conf} — {licence} not EARNED (B6)",
                "licence": licence, "licence_state": st, "max_confidence": max_conf}
    return {"allowed": True, "reason": "within licence + confidence cap", "licence": licence,
            "licence_state": st, "max_confidence": max_conf}


def main():
    args = sys.argv[1:]
    lic = load_licences()
    if len(args) < 2:
        for name, e in lic["licences"].items():
            print(f"  {name:32} {e['state']}")
        return
    print(json.dumps(check_claim(args[0], args[1], lic=lic), indent=1))


if __name__ == "__main__":
    main()
