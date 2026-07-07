#!/usr/bin/env python3
"""Information-budget panel (Constitution v2.1 Art. IX + B7).

Every inferential/graduating claim (layer >= L2 OR confidence >= SUPPORTED) must display the full
13-field information budget. Unicity distance is only ONE component and may NOT substitute for the panel
(Art. IX). Missing fields are shown as UNKNOWN, never silently omitted (Art. I OBSERVED/UNKNOWN). The gate
FAILS CLOSED: a graduating claim cannot be certified while a load-bearing field is UNKNOWN or the claim is
underdetermined (free parameters > independent evidence). Deterministic; no DB.

CLI:
    python3 scripts/info_budget.py   # demo panel + certification
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# the 13 Art. IX fields, in canonical order
FIELDS = [
    "raw_corpus_size", "effective_independent_evidence", "sign_inventory_uncertainty",
    "segmentation_uncertainty", "parameter_count", "search_space_size", "source_dependency_structure",
    "missing_feature_burden", "damage_rate", "class_balance", "domain_shift",
    "minimum_detectable_effect", "estimated_power",
]
# fields that MUST be known to certify a graduating claim (the inferential + multiplicity/independence core)
LOAD_BEARING = ["effective_independent_evidence", "parameter_count", "minimum_detectable_effect",
                "estimated_power", "source_dependency_structure", "search_space_size"]

CONF_ORDER = ["SPECULATIVE", "EXPLORATORY", "SUPPORTED", "HELD_OUT_SUPPORTED", "REPLICATED",
              "PROVISIONALLY_ACCEPTED", "ACCEPTED"]
POWER_FLOOR = 0.5                     # a positive graduating claim needs adequate power to detect its effect

UNKNOWN = "UNKNOWN"


def build_panel(**fields):
    """Assemble the panel from whatever the caller supplies; every missing field -> UNKNOWN."""
    unknown = [k for k in fields if k not in FIELDS]
    if unknown:
        raise KeyError(f"not Art. IX panel fields: {unknown}")
    return {k: fields.get(k, UNKNOWN) for k in FIELDS}


def underdetermined(panel):
    """Art. IX: effective degrees of freedom (parameter_count) exceeding information (effective evidence)
    -> underdetermined. Returns True/False, or None if either input is UNKNOWN."""
    p = panel.get("parameter_count"); e = panel.get("effective_independent_evidence")
    if p == UNKNOWN or e == UNKNOWN or p is None or e is None:
        return None
    return float(p) > float(e)


def requires_panel(claim_layer=None, confidence=None):
    """B7 scope: required for layer >= L2 or confidence >= SUPPORTED; bare L0/L1 observations exempt.
    FAILS CLOSED — a supplied-but-unrecognized layer or confidence string REQUIRES the panel (never exempt)."""
    layer_needs = False
    if claim_layer is not None:
        cl = str(claim_layer).strip().upper()
        if cl.startswith("L") and cl[1:].isdigit():
            layer_needs = int(cl[1:]) >= 2
        else:
            return True                                       # unrecognized layer -> require (fail closed)
    conf_needs = False
    if confidence is not None:
        cn = str(confidence).strip().upper()
        if cn in CONF_ORDER:
            conf_needs = CONF_ORDER.index(cn) >= CONF_ORDER.index("SUPPORTED")
        else:
            return True                                       # unrecognized confidence -> require (fail closed)
    return bool(layer_needs or conf_needs)


def certify(panel, claim_layer=None, confidence=None, power_floor=POWER_FLOOR):
    """Fail-closed certification (Art. IX/XVI). A claim that requires the panel is NOT certified while a
    load-bearing field is UNKNOWN, the claim is underdetermined, or it is underpowered."""
    needed = requires_panel(claim_layer, confidence)
    reasons = []
    if not needed:
        return {"required": False, "certified": True, "reasons": ["L0/L1 observation exempt (B7)"]}
    missing = [k for k in LOAD_BEARING if panel.get(k, UNKNOWN) == UNKNOWN]
    if missing:
        reasons.append(f"load-bearing fields UNKNOWN: {missing}")
    ud = underdetermined(panel)
    if ud is True:
        reasons.append(f"UNDERDETERMINED: parameter_count {panel['parameter_count']} > "
                       f"effective_independent_evidence {panel['effective_independent_evidence']}")
    ep = panel.get("estimated_power")
    if ep != UNKNOWN and ep is not None and float(ep) < power_floor:
        reasons.append(f"UNDERPOWERED: estimated_power {ep} < floor {power_floor}")
    return {"required": True, "certified": len(reasons) == 0, "underdetermined": ud,
            "reasons": reasons or ["all load-bearing fields present; not underdetermined; adequately powered"]}


def render(panel):
    """Text table for the on-screen information floor (Art. IX 'always visible')."""
    w = max(len(f) for f in FIELDS)
    return "\n".join(f"  {f.ljust(w)} : {panel.get(f, UNKNOWN)}" for f in FIELDS)


def _demo():
    panel = build_panel(raw_corpus_size=1341, effective_independent_evidence=19, parameter_count=57,
                        minimum_detectable_effect=0.92, estimated_power=0.0, damage_rate=0.18,
                        class_balance="PLACE 43 / HUMAN 23")
    print(render(panel))
    print("\ncertify (L4, SUPPORTED):", json.dumps(certify(panel, "L4", "SUPPORTED"), indent=1))


if __name__ == "__main__":
    _demo()
