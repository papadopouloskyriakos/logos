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


def _norm_layer(claim_layer):
    """Normalize + recognize a layer. Returns the canonical 'Ln' or None if unrecognized (fail closed)."""
    if not isinstance(claim_layer, str):
        return None
    cl = claim_layer.strip().upper()
    return cl if cl in LAYER_LICENCE else None


def check_claim(claim_layer, confidence, linear_a=True, lic=None):
    """Enforce Art. XV + B6 for a claim. Returns {allowed, reason, licence, licence_state, max_confidence}.

    FAILS CLOSED (Art. XVI): an unrecognized layer or confidence string is BLOCKED, never waved through.
    - L0/L1 (observation / sign-identification) carry no licence and are exempt from the cap (B6).
    - Any Linear A output at a LICENCED layer (L2..L9) whose licence is unearned is BLOCKED outright
      (Art. XV — the boundary tracks the licence matrix, not a bare layer number; L2 structural-role
      transfer needs STRUCTURAL just as L3 functional needs FUNCTIONAL).
    - Otherwise confidence is capped at SUPPORTED without the layer's licence (B6)."""
    lic = lic or load_licences()
    layer = _norm_layer(claim_layer)
    if layer is None:                                         # unrecognized layer -> fail closed
        return {"allowed": False, "reason": f"unrecognized claim_layer {claim_layer!r} — fail closed (Art. XVI)",
                "licence": None, "licence_state": None, "max_confidence": "SPECULATIVE"}
    licence = LAYER_LICENCE[layer]
    if licence is None:                                       # L0/L1: observation/identification, no licence
        return {"allowed": True, "reason": f"{layer} observation/identification — no transfer licence required",
                "licence": None, "licence_state": None, "max_confidence": "ACCEPTED"}
    st = state_of(licence, lic)
    is_earned = st == "EARNED"
    max_conf = "ACCEPTED" if is_earned else "SUPPORTED"       # B6: capped at SUPPORTED without the licence
    if linear_a and not is_earned:                            # Art. XV: LA transfer output needs the licence
        return {"allowed": False, "reason": f"Linear A {layer} output requires {licence} (state {st}) — Art. XV",
                "licence": licence, "licence_state": st, "max_confidence": max_conf}
    if confidence is not None:                                # B6 cap for non-LA / earned-licence claims
        cn = str(confidence).strip().upper()
        if cn not in CONF_ORDER:
            return {"allowed": False, "reason": f"unrecognized confidence {confidence!r} — fail closed (Art. XVI)",
                    "licence": licence, "licence_state": st, "max_confidence": max_conf}
        if CONF_ORDER.index(cn) > CONF_ORDER.index(max_conf):
            return {"allowed": False,
                    "reason": f"confidence {cn} exceeds the cap {max_conf} — {licence} not EARNED (B6)",
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
