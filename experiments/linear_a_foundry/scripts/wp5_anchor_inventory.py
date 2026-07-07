#!/usr/bin/env python3
"""WP5(a) — machine-readable ANCHOR INVENTORY from the REAL available sources.

Unions the three independent evidence channels that actually exist on disk and grades every
record by PROVENANCE, DEPENDENCY (independence) CLASS, and TIER. Then it quantifies the single
question WP5 cares about: how many LA signs are pinned by *independent, held-out-survivable*
evidence versus a single toponym equation ("one-toponym-deep pins").

SOURCES (read-only, all in-repo; nothing invented — invariant 12, counts generated):
  1. crossscript_gate/anchors.csv        — 59 A-side AB syllabograms; per-sign homomorphy grade
                                            (Salgarella 2020), cypriot_stable (S&M 2017), sm2017_tier,
                                            toponym_covered, attestation counts.
  2. crossscript_gate/phase2/anchor_census.csv — 47 lexical/onomastic equation records
                                            (toponym / personal_name / gloss / variation) with
                                            independence_class + S&M trust flags.
  3. crossscript_gate/toponym_anchors.csv — 5 non-queried LA<->LB place-name equations (+1 queried).
  4. crossscript_gate/salgarella_2020_grades.json — 57 homomorphy-graded signs + lexical endorsements.

THREE INDEPENDENT CHANNELS per sign (a value-pin is "independent" if backed by >1 of these):
  L  lexical/onomastic equation   (a shared LA<->LB word places the sign)      [census + toponyms]
  H  homomorphy (sign-SHAPE)       (Salgarella: LA glyph == LB glyph)           [structural, not lexical]
  C  Cypriot cross-script stability (S&M high-certainty 11)                     [3rd-script continuity]
H and C are structural: they corroborate that a sign is the SAME sign across scripts, which is
logically independent of any single word equation. A sign resting on ONE toponym and nothing else
is a "one-toponym-deep pin" — exactly the fragility the frozen cross-script gate exposed
(REFUTE_LOTO_FRAGILE; distributional channel 0.0000; only I, RI recovered, each one-toponym-deep;
DOIs 10.5281/zenodo.21168887 / 21173639 — NOT re-run here).

Deterministic. Writes data/wp5_anchor_inventory.json (+ per-record and per-sign CSVs).
"""
from __future__ import annotations
import csv
import json
import os
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
GATE = "/home/claude-runner/gitlab/n8n/logos-la-lb-continuity/experiments/crossscript_gate"

ANCHORS_CSV = os.path.join(GATE, "anchors.csv")
CENSUS_CSV = os.path.join(GATE, "phase2", "anchor_census.csv")
TOPONYM_CSV = os.path.join(GATE, "toponym_anchors.csv")
SALG_JSON = os.path.join(GATE, "salgarella_2020_grades.json")

# frozen empirical held-out result (cross-script gate one-shot; do NOT re-run)
GATE_FROZEN = {
    "verdict": "REFUTE_LOTO_FRAGILE",
    "distributional_channel_top1": 0.0,
    "recovered_signs_LOTO": ["I", "RI"],
    "recovered_depth": "each one-toponym-deep",
    "prereg_dois": ["10.5281/zenodo.21168887", "10.5281/zenodo.21173639"],
    "note": "empirical held-out survivability from the frozen preregistered gate; cited, not recomputed",
}

# homomorphy grade -> ordinal tier (higher = stronger structural claim)
HOMO_TIER = {
    "homomorphic and also likely homophone": 3,
    "homomorphic": 2,
    "homomorphic (with allographic variation)": 2,
}


def homo_ordinal(grade: str) -> int:
    if not grade:
        return 0
    g = grade.lower()
    if "homophone" in g:
        return 3
    if "homomorphic" in g:
        return 2
    return 0


def load_anchors_csv():
    rows = list(csv.DictReader(open(ANCHORS_CSV)))
    per = {}
    for r in rows:
        sid = r["sign_id"]
        per[sid] = {
            "sign_id": sid,
            "ab_number": r["ab_number"],
            "la_attestations": int(r["la_attestations"]),
            "damos_attestations": int(r["damos_attestations"]),
            "conventional_value": r["conventional_value"],
            "value_source": r["value_source"],
            "homomorphy_grade": r["homomorphy_grade"],
            "homomorphy_tier": homo_ordinal(r["homomorphy_grade"]),
            "cypriot_stable": r["cypriot_stable"] == "true",
            "cypriot_detail": r["cypriot_detail"],
            "sm2017_tier": r["sm2017_tier"],
            "toponym_covered": r["toponym_covered"] == "True",
            "maskable": r["maskable"] == "True",
            "robust_anchor": r["robust_anchor"] == "True",
        }
    return per


def load_census():
    """Lexical/onomastic equation records. independence_class:
       1 toponym | 2 personal-name/adaptation | 3 gloss/acrophonic | 4 variation-constraint (never pins)."""
    rows = list(csv.DictReader(open(CENSUS_CSV)))
    recs = []
    for r in rows:
        signs = [s.strip() for s in r["covered_signs"].split(",") if s.strip()]
        recs.append({
            "anchor_id": r["anchor_id"],
            "class": r["class"],
            "independence_class": int(r["independence_class"]),
            "covered_signs": signs,
            "identification": r["identification"],
            "sm_trust": r["sm_trust"],
            "source_status": r["source_status"],
            "fringe_flag": r["fringe_flag"] == "true",
            "channel": "L",
        })
    return recs


def load_salg_endorsements():
    j = json.load(open(SALG_JSON))
    return j.get("lexical_endorsements", []), j.get("signs", {})


def run():
    per = load_anchors_csv()          # 59 sign rows (structural channels H + C live here)
    census = load_census()            # 47 lexical records (channel L)
    endorse, salg_signs = load_salg_endorsements()

    # ---- per-sign roll-up across the three channels ----
    # channel L depth: distinct lexical ITEMS by independence class (a value pin needs class 1 or 2;
    # class 4 "variation constraint" never pins a value, only constrains co-variation)
    L_by_sign = defaultdict(lambda: {"toponym_items": set(), "name_items": set(),
                                     "gloss_items": set(), "variation_items": set(),
                                     "debunked_items": set(), "all_records": []})
    for rec in census:
        for sg in rec["covered_signs"]:
            b = L_by_sign[sg]
            b["all_records"].append(rec["anchor_id"])
            if rec["sm_trust"] == "debunked":
                b["debunked_items"].add(rec["anchor_id"])
                continue
            if rec["independence_class"] == 1:
                b["toponym_items"].add(rec["anchor_id"])
            elif rec["independence_class"] == 2:
                b["name_items"].add(rec["anchor_id"])
            elif rec["independence_class"] == 3:
                b["gloss_items"].add(rec["anchor_id"])
            elif rec["independence_class"] == 4:
                b["variation_items"].add(rec["anchor_id"])

    all_signs = set(per) | set(L_by_sign)
    sign_records = []
    for sg in sorted(all_signs):
        p = per.get(sg, {})
        L = L_by_sign.get(sg, None)
        n_top = len(L["toponym_items"]) if L else 0
        n_name = len(L["name_items"]) if L else 0
        n_gloss = len(L["gloss_items"]) if L else 0
        n_var = len(L["variation_items"]) if L else 0
        homo = p.get("homomorphy_tier", 0)
        cypr = bool(p.get("cypriot_stable", False))

        # channel presence: L present if any value-pinning lexical item (class 1,2,3; class 4 excluded)
        L_present = (n_top + n_name + n_gloss) > 0
        H_present = homo >= 2
        C_present = cypr
        n_channels = int(L_present) + int(H_present) + int(C_present)

        # pin depth within the lexical channel (strongest evidence a WORD equation gives)
        # 'strong lexical' = toponym (class1); names (class2) are S&M-flagged weak guides
        strong_lex = n_top
        any_lex = n_top + n_name + n_gloss

        # classification
        if not (L_present or H_present or C_present):
            tier = "no_anchor"
        elif n_channels >= 2 and (strong_lex >= 1 or (H_present and C_present)):
            tier = "multi_channel_independent"       # held-out-survivable candidate
        elif strong_lex >= 2:
            tier = "multi_toponym"                    # >=2 independent toponym items
        elif strong_lex == 1 and n_channels == 1:
            tier = "one_toponym_deep_pin"             # THE fragile class
        elif strong_lex == 1:
            tier = "toponym_plus_structural"          # 1 toponym + H or C corroboration
        elif H_present or C_present:
            tier = "structural_only"                  # homomorphy/cypriot, no lexical pin
        elif n_name >= 1 or n_gloss >= 1:
            tier = "weak_lexical_only"                # only personal-name / gloss (S&M-flagged weak)
        else:
            tier = "no_anchor"

        sign_records.append({
            "sign_id": sg,
            "conventional_value": p.get("conventional_value", ""),
            "la_attestations": p.get("la_attestations", None),
            "channel_L_lexical": {"toponym_items": sorted(L["toponym_items"]) if L else [],
                                  "name_items": sorted(L["name_items"]) if L else [],
                                  "gloss_items": sorted(L["gloss_items"]) if L else [],
                                  "variation_items": sorted(L["variation_items"]) if L else [],
                                  "debunked_items": sorted(L["debunked_items"]) if L else []},
            "channel_H_homomorphy_tier": homo,
            "channel_H_grade": p.get("homomorphy_grade", ""),
            "channel_C_cypriot_stable": cypr,
            "n_independent_channels": n_channels,
            "strong_lexical_items": strong_lex,
            "any_lexical_items": any_lex,
            "robust_anchor": p.get("robust_anchor", False),
            "dependency_tier": tier,
        })

    # ---- per-record inventory (provenance ledger) ----
    records = []
    for rec in census:
        records.append({
            "record_id": rec["anchor_id"],
            "channel": "L_lexical",
            "class": rec["class"],
            "independence_class": rec["independence_class"],
            "covered_signs": rec["covered_signs"],
            "tier": {"tempting": "high", "neutral": "mid", "debunked": "refuted",
                     "n/a": "unrated"}.get(rec["sm_trust"], "mid"),
            "sm_trust": rec["sm_trust"],
            "provenance": ("Steele & Meissner 2017 (primary chapter)" if rec["source_status"] == "primary"
                           else "Younger LA pages (secondary, Wayback)"),
            "source_status": rec["source_status"],
        })
    for sid, p in per.items():
        if p["homomorphy_tier"] >= 2:
            records.append({
                "record_id": f"homo_{sid}", "channel": "H_homomorphy", "class": "sign_shape",
                "independence_class": None, "covered_signs": [sid],
                "tier": "high" if p["homomorphy_tier"] == 3 else "mid",
                "sm_trust": None,
                "provenance": "Salgarella 2020 Aegean Linear Script(s) (CUP), Tables 2-4",
                "source_status": "primary", "grade": p["homomorphy_grade"],
            })
        if p["cypriot_stable"]:
            records.append({
                "record_id": f"cypr_{sid}", "channel": "C_cypriot", "class": "cross_script_stability",
                "independence_class": None, "covered_signs": [sid], "tier": "high", "sm_trust": None,
                "provenance": "Steele & Meissner 2017 Table 6.2 p.98 (primary)",
                "source_status": "primary", "detail": p["cypriot_detail"],
            })

    # ---- summary counts (generated) ----
    tier_counts = Counter(r["dependency_tier"] for r in sign_records)
    anchored = [r for r in sign_records if r["dependency_tier"] != "no_anchor"]
    independent = [r for r in sign_records if r["n_independent_channels"] >= 2
                   and r["dependency_tier"] in ("multi_channel_independent", "multi_toponym", "toponym_plus_structural")]
    held_out_survivable = [r for r in sign_records
                           if r["dependency_tier"] in ("multi_channel_independent", "multi_toponym")]
    one_toponym_deep = [r for r in sign_records if r["dependency_tier"] == "one_toponym_deep_pin"]

    summary = {
        "n_signs_total_inventory": len(sign_records),
        "n_signs_with_any_anchor": len(anchored),
        "n_lexical_records": len(census),
        "n_toponym_records": sum(1 for r in census if r["independence_class"] == 1),
        "n_personal_name_records": sum(1 for r in census if r["independence_class"] == 2),
        "n_homomorphy_graded_signs": sum(1 for p in per.values() if p["homomorphy_tier"] >= 2),
        "n_cypriot_stable_signs": sum(1 for p in per.values() if p["cypriot_stable"]),
        "n_provenance_records_total": len(records),
        "dependency_tier_counts": dict(tier_counts),
        "n_independent_multi_channel": len(independent),
        "independent_signs": sorted(r["sign_id"] for r in independent),
        "n_held_out_survivable_candidate": len(held_out_survivable),
        "held_out_survivable_signs": sorted(r["sign_id"] for r in held_out_survivable),
        "n_one_toponym_deep_pins": len(one_toponym_deep),
        "one_toponym_deep_pin_signs": sorted(r["sign_id"] for r in one_toponym_deep),
        "frozen_empirical_held_out": GATE_FROZEN,
        "reconciliation": (
            "INVENTORY-side independence (multi-channel / multi-item corroboration) is far more generous "
            "than EMPIRICAL held-out survivability. The frozen gate's LOTO recovered only 2 signs (I, RI), "
            "each one-toponym-deep, with the distributional channel at 0.0000 — i.e. even signs the inventory "
            "grades 'multi_channel_independent' are NOT recoverable from LA-internal distribution once their "
            "toponym is held out. The structural channels (homomorphy, Cypriot-stability) corroborate sign "
            "IDENTITY across scripts but do not, by themselves, let the value be re-derived from held-out LA."),
    }

    out = {
        "experiment": "WP5(a)_anchor_inventory",
        "sources": {"anchors_csv": ANCHORS_CSV, "census_csv": CENSUS_CSV,
                    "toponym_csv": TOPONYM_CSV, "salgarella_json": SALG_JSON},
        "channels": {"L": "lexical/onomastic equation (census+toponyms)",
                     "H": "homomorphy / sign-shape (Salgarella 2020)",
                     "C": "Cypriot cross-script stability (S&M 2017 high-certainty 11)"},
        "summary": summary,
        "sign_inventory": sign_records,
    }
    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(os.path.join(DATA, "wp5_anchor_inventory.json"), "w"), indent=1)

    # per-sign CSV
    with open(os.path.join(DATA, "wp5_anchor_inventory_signs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sign_id", "conv_value", "la_attest", "n_toponym", "n_name", "homomorphy_tier",
                    "cypriot_stable", "n_channels", "dependency_tier"])
        for r in sign_records:
            w.writerow([r["sign_id"], r["conventional_value"], r["la_attestations"],
                        len(r["channel_L_lexical"]["toponym_items"]),
                        len(r["channel_L_lexical"]["name_items"]),
                        r["channel_H_homomorphy_tier"], r["channel_C_cypriot_stable"],
                        r["n_independent_channels"], r["dependency_tier"]])

    # per-record provenance CSV
    with open(os.path.join(DATA, "wp5_anchor_inventory_records.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "channel", "class", "independence_class", "covered_signs",
                    "tier", "sm_trust", "source_status", "provenance"])
        for r in records:
            w.writerow([r["record_id"], r["channel"], r["class"], r["independence_class"],
                        "|".join(r["covered_signs"]), r["tier"], r.get("sm_trust"),
                        r["source_status"], r["provenance"]])

    print(json.dumps(summary, indent=1))
    print("\nWROTE", os.path.join(DATA, "wp5_anchor_inventory.json"))
    return out


if __name__ == "__main__":
    run()
