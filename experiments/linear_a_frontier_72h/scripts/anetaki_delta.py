#!/usr/bin/env python3
"""EPOCH-001 P5: mechanical delta of Anetaki editor-printed material vs corpus/silver.

Counts only (Invariant 12). Also runs the P4 negative control: no fringe reading
string may appear in any non-quarantined candidate row.

Outputs: epochs/EPOCH-001/delta.json
"""
import json, re, sys, os
from collections import Counter

BASE = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
EXP  = f"{BASE}/experiments/linear_a_frontier_72h"
SILVER = f"{BASE}/corpus/silver/inscriptions_structured.json"
CANDS  = f"{EXP}/data/anetaki_2025/sign_candidates.json"
OUT    = f"{EXP}/epochs/EPOCH-001/delta.json"

silver = json.load(open(SILVER))
cands  = json.load(open(CANDS))["candidates"]

# ---- silver universe -------------------------------------------------------
silver_types = Counter()
for doc in silver:
    for s in doc["signs"]:
        silver_types[s] += 1
    for ev in doc.get("stream", []):
        if ev.get("t") == "other" and isinstance(ev.get("raw"), str) and ev["raw"].startswith("*"):
            silver_types[ev["raw"]] += 0  # raw markers: presence only, not tokens

silver_ids = {d["id"] for d in silver}
knzg57a = next(d for d in silver if d["id"] == "KNZg57a")

# ---- editor-printed sign identities on the new carriers --------------------
# normalized AB numbers / logogram ids printed by Kanta et al. 2024 (evidence-grade rows only)
editor_rows = [c for c in cands if c["quarantine"] in ("none", "verbatim_discrepancy", "restoration")]
fringe_rows = [c for c in cands if c["quarantine"] == "fringe"]
placeholder_rows = [c for c in cands if c["quarantine"] == "unpublished_content"]

# map editor-printed identities to silver transliteration vocabulary
printed_syllabograms = ["RA", "I", "NE", "SE", "KU", "WI", "A", "DI", "KA"]  # AB60,28,24,09,81,40,08,07,77
printed_special = {
    "A664_rhyton": ("*664" in silver_types) or any("664" in t for t in silver_types),
    "CH_180_in_LA": any(t in ("*180", "AB180") for t in silver_types) or any(t.endswith("180") for t in silver_types),
    "CH_181_in_LA": any(t == "*181" or t.endswith("181") for t in silver_types),
    "hide_ideogram_CUIR": any(t in ("CUIR", "*180", "PELLIS") for t in silver_types),
}
syl_in_silver = {s: (s in silver_types) for s in printed_syllabograms}

# *301 contexts: printed anywhere in the new material?
new_301 = any("*301" in json.dumps(c) for c in editor_rows)

# A-only occurrences verifiable: need transliterated sequences -> none published
a_only_verifiable = 0

# formula-slot delta: needs sequences -> none published
formula_slots = 0

# genuinely-new-to-silver sign types among editor-printed identities
new_types = []
if not printed_special["A664_rhyton"]:
    # editors: A664 rhyton's ONLY other LA attestation = PH 8a.3.
    # silver's PH8a line 3 word = *418+L2 (and KNZg57a's preliminary reading also
    # contains *418+L2) -> *418+L2 is a strong ALIAS candidate for A664 under the
    # lineara.xyz encoding. Status therefore UNCERTAIN, not countable-new.
    ph8 = next(d for d in silver if d["id"] == "PH8a")
    alias_evidence = ("*418+L2" in ph8["signs"]) and ("*418+L2" in knzg57a["signs"])
    new_types.append({"type": "A664 (rhyton)", "silver_has_verbatim": False,
                      "alias_candidate": "*418+L2 (PH8a line 3 + KNZg57a both carry it)",
                      "alias_evidence_mechanical": alias_evidence,
                      "countable": False, "status": "UNCERTAIN_ALIAS"})
for t, present in [("CH *180 (in LA use)", printed_special["CH_180_in_LA"]),
                   ("CH *181 (in LA use)", printed_special["CH_181_in_LA"])]:
    if not present:
        new_types.append({"type": t, "silver_has": False})
new_types.append({"type": "probable NEW LA sign (handle face α) — shape unpublished", "silver_has": False,
                  "countable": False})

# ---- negative control: fringe leak ----------------------------------------
fringe_strings = []
for f in fringe_rows:
    fringe_strings += re.findall(r"[A-Za-z]{1,6}", f["sign"])
fringe_markers = ["VESSEL ru", "VESSEL ra", "VESSEL Ti", "(god) Di", "a-ka' root"]
leak = []
for c in editor_rows + placeholder_rows:
    for m in ["VESSEL ru", "VESSEL ra", "god) Di"]:
        if m in c["sign"]:
            leak.append({"row": c["row"], "marker": m})
negative_control_pass = (len(leak) == 0)

# ---- unpublished (seal-relevant) inventory ---------------------------------
unpublished = {
    "face_B_sign_groups": 6,
    "face_C_sign_groups_min": 9,
    "handle_beta_sequence_signs": 4,
    "face_A_metope_signs_min": 16,
    "fraction_signs_distinct": 6,
    "total_signs_reported": 119,
    "transliterated_sequences_published": 0,
}

delta = {
    "epoch": "EPOCH-001",
    "generated_by": "scripts/anetaki_delta.py",
    "inputs": {"silver": SILVER, "candidates": CANDS,
               "n_silver_docs": len(silver), "n_candidate_rows": len(cands)},
    "silver_state": {
        "KNZg57a_in_silver": True,
        "KNZg57a_signs": knzg57a["signs"],
        "KNZg58_in_silver": ("KNZg58" in silver_ids),
        "KNZg56_in_silver": ("KNZg56" in silver_ids),
    },
    "editor_printed_syllabograms_already_in_silver_vocab": syl_in_silver,
    "special_sign_presence_in_silver": printed_special,
    "genuinely_new_information": {
        "new_sign_types_vs_silver": new_types,
        "n_new_countable_sign_types": len([t for t in new_types if t.get("countable", True)]),
        "new_star301_contexts": 0 if not new_301 else "CHECK",
        "new_A_only_occurrences_verifiable": a_only_verifiable,
        "new_formula_slots": formula_slots,
        "new_transliterated_multi_sign_sequences": 0,
        "unpublished_seal_relevant_content": unpublished,
    },
    "negative_control_fringe_leak": {"pass": negative_control_pass, "leaks": leak},
    "note": "counts are descriptive supply metrics; no hypothesis graded; no statistical claim",
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(delta, open(OUT, "w"), indent=1)
print(json.dumps(delta, indent=1))
