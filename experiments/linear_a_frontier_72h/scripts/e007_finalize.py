#!/usr/bin/env python3
"""Assemble epochs/EPOCH-007/result.json from run + posthoc artifacts (mechanical copy)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
D = os.path.join(CAMP, "data", "ledger_roles")
run = json.load(open(os.path.join(D, "e007_results.json")))
ph = json.load(open(os.path.join(D, "e007_posthoc.json")))
phla = json.load(open(os.path.join(D, "e007_posthoc_la.json")))

res = {
    "epoch": "EPOCH-007",
    "frontier": "F5 ledger-role induction as anchor constraints",
    "plan_hash": "6c85277da7c4e5d30abdd12bca084db4076c4f12e334225f5a5c535dfc2be566",
    "prereg": "epochs/EPOCH-007/prereg.md (frozen 2026-07-08T04:13:24Z, before any run)",
    "seed": run["seed"],
    "claim_layer": "L2/L3 functional-slot only; no value/semantic claim; no licence touched (Art. XV)",
    "articles": ["V", "VII", "VIII", "IX", "XI", "XII", "XV", "XVII", "XVIII", "XXII"],
    "prior_art_differenced": {
        "observable_channels_L3_word_to_channel": "REFUTED there; NOT re-run — this epoch induces per-occurrence slot roles from within-document geometry, not word->commodity identity",
        "observable_channels_L2_doc_structure": "SUPPORTED there; this epoch asks the finer per-slot question",
    },
    "deviations": run["deviations"],
    "positive_control_PC1": run["PC1"],
    "LB_corpus": run["LB_corpus"],
    "LB_derivation": run["LB_derivation"],
    "LB_heldout": run["LB_heldout"],
    "LB_cluster_mapping": run["LB_cluster_mapping"],
    "nulls": {
        "N1_shuffled_doc": run["N1_shuffled_doc"],
        "N2_numeral_detach": run["N2_numeral_detach"],
        "N3_label_perm": run["N3_label_perm"],
    },
    "LB_fire_criteria": run["LB_fire_criteria"],
    "LB_fires": run["LB_fires"],
    "LA_leg": "NOT RUN for record (gated on LB firing; LB did not fire)",
    "posthoc_nonverdict": {
        "site_convention_divide": ph["PH3_gold_by_site"],
        "alt_decode_heldout": {
            "macro_f1": ph["PH2_heldout_altdecode"]["macro_f1"],
            "U": ph["PH2_heldout_altdecode"]["per_class"]["U"],
            "T": ph["PH2_heldout_altdecode"]["per_class"]["T"],
        },
        "la_exploratory_readout": {k: phla[k] for k in
                                   ("predicted_role_share", "C1_KURO", "C2_LOGO", "C3_KIRO", "C4_APREFIX")},
    },
    "verdict": run["verdict"],
    "verdict_reason": run["verdict_reason"],
    "licences_changed": "none",
    "artifacts": [
        "epochs/EPOCH-007/prereg.md", "epochs/EPOCH-007/plan_hash.txt",
        "reports/EPOCH007_LEDGER_ROLES.md",
        "data/ledger_roles/e007_results.json", "data/ledger_roles/e007_posthoc.json",
        "data/ledger_roles/e007_posthoc_la.json",
        "scripts/e007_ledger_roles.py", "scripts/e007_run.py",
        "scripts/e007_posthoc.py", "scripts/e007_posthoc_la.py",
    ],
}
out = os.path.join(CAMP, "epochs", "EPOCH-007", "result.json")
json.dump(res, open(out, "w"), indent=1)
print("wrote", out, "verdict:", res["verdict"])
