#!/usr/bin/env python3
"""build_anchors.py — Phase 0 §1: generate the candidate-anchor table (anchors.csv).

Every count is COMPUTED from the repo's own loaders (invariant 12); every value/status field
carries its provenance. Nothing is guessed: fields whose primary source is not on disk are
`pending_primary` (Steele & Meißner 2017 and Salgarella 2020 are both ABSENT from the repo —
see docs/related/_acquisition.md), and no Cypriot-stable membership or homomorphy grade is
reconstructed from secondary summaries.

Data sources (all existing repo machinery, nothing re-derived):
  - A-side stream + conservative inventory: scripts/cross_script/data.load_a()
    (the Track-B pipeline's own loader — the stream the future gate would consume).
  - B-side attestations: data.load_b_damos() (full DĀMOS harvest) and data.load_b() (cog).
  - Conventional values: scripts/comparison/litindex.LB_TRANSFER_SIGNS (the repo's sourced
    lb_value_transfer seed) — plus the data.py bridge convention (GORILA romanization ==
    Unicode LB syllable value) for the 7 A-side AB signs the seed does not cover.
  - Candidate value space: the Unicode Linear B syllabary (LINEAR B SYLLABLE codepoints,
    U+10000–U+1007F), via data._b_value_from_codepoint.

The CSV contains only aggregate per-sign counts + public sign-value conventions (same class of
content as the committed litindex.py); no licensed corpus text is copied.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _ROOT)

from scripts.cross_script import data as D                     # noqa: E402
from scripts.comparison.litindex import LB_TRANSFER_SIGNS      # noqa: E402
import steele_meissner_2017 as SM                              # noqa: E402  (page-cited, verified)

MIN_LA_ATTEST = 3           # B.2's min-count for a stable context vector (phono_distributional)

CIT_SEED = ("GORILA (Godart & Olivier 1976-1985); LB values after Ventris 1953 "
            "[litindex.py lb_value_transfer seed]")
CIT_BRIDGE = ("scripts/cross_script/data.py bridge: GORILA romanization == Unicode LB syllable "
              "value (Unicode chart cross-check); NOT in the litindex seed — needs citation "
              "before graduating to seed status")
CIT_SM2017 = SM.CITATION + " — ACQUIRED 2026-07-03 (docs/related/_acquisition.md)"
CIT_SALG2020 = ("Salgarella 2020, Aegean Linear Script(s) (CUP) — ABSENT from repo "
                "(paywalled, operator-supplies; docs/related/_acquisition.md)")


# Authority tensions surfaced by the Salgarella-2020 ingest (recorded, not resolved):
SALG_TENSIONS = {
    "JU": ("Salgarella 2020 INTERNAL tension: Table 2 p.35 prints 'ju?' (light-blue, "
           "homomorphic) while her Table 4 p.37 and Index p.412 carry AB *65 as "
           "undeciphered/valueless; graded from Table 2 with her '?' preserved."),
}


def _load_salgarella_grades():
    """Salgarella 2020 per-sign grades (page-cited, verbatim), if the extraction exists.
    Source: corpus/bronze/salgarella_2020/ via salgarella_2020_grades.json — grades are HER
    printed category labels; signs she does not grade stay pending_primary."""
    p = os.path.join(_HERE, "salgarella_2020_grades.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f).get("signs", {})


def _homomorphy(t: str, grades: dict):
    g = grades.get(t)
    if not g:
        return ("pending_primary (searched Salgarella 2020 sign treatment; token not graded "
                "there)" if grades else "pending_primary")
    marks = f" {g['marks']}" if g.get("marks") else ""
    return f"{g['grade']}{marks} (Salgarella 2020, {g['page']})"


def _cypriot_status(t: str):
    """(cypriot_stable, citation_detail) for sign token t, from the acquired primary."""
    if t in SM.CYPRIOT_STABLE_11:
        e = SM.CYPRIOT_STABLE_11[t]
        det = f"Table 6.2 p.{e['page']} ({e['ab']}; CM {e['cm']}; CS {e['cs_value']})"
        if "note" in e:
            det += " — " + e["note"]
        return "true", det
    if t in SM.CYPRIOT_CANDIDATES:
        e = SM.CYPRIOT_CANDIDATES[t]
        return "candidate", f"§3 p.{e['page']}: \"{e['quote']}\" (candidate, NOT a member)"
    return "not_listed", ("not in the high-certainty eleven (§3/Table 6.2 pp. 97-99); "
                          "NOT a sourced claim of instability")


def main() -> int:
    # LB syllabary (candidate value space) from Unicode names
    syll = {}
    for cp in range(0x10000, 0x10080):
        v = D._b_value_from_codepoint(chr(cp))
        if v:
            nm = unicodedata.name(chr(cp))          # LINEAR B SYLLABLE B0NN VAL
            syll[v] = nm.split()[3]                  # the B0NN number
    a_inv, a_seqs, a_freq = D.load_a()
    bd_seqs, bd_freq, _ = D.load_b_damos()
    bc_seqs, bc_freq, _ = D.load_b()
    a_ab = sorted(t for t in a_inv if not t.startswith("*"))

    damos_attested_values = sorted(v for v in syll if bd_freq.get(v, 0) >= 1)

    covered = set(SM.TOPONYM_COVERED_SIGNS)
    salg = _load_salgarella_grades()
    rows = []
    for t in a_ab:
        la = a_freq.get(t, 0)
        damos = bd_freq.get(t, 0)
        in_seed = t in LB_TRANSFER_SIGNS
        bridged = damos >= 1
        robust = bridged and la >= MIN_LA_ATTEST
        cyp, cyp_detail = _cypriot_status(t)
        rows.append({
            "sign_id": t,
            "ab_number": syll.get(t, ""),                     # '' if not an LB Unicode syllable
            "la_attestations": la,
            "damos_attestations": damos,
            "cog_attestations": bc_freq.get(t, 0),
            "conventional_value": t.lower(),
            "value_source": "litindex:lb_value_transfer" if in_seed else "data.py bridge convention",
            "homomorphy_grade": _homomorphy(t, salg),         # Salgarella 2020, page-cited
            "cypriot_stable": cyp,                            # from the ACQUIRED S&M 2017 primary
            "cypriot_detail": cyp_detail,
            "sm2017_tier": SM.SM2017_TIER.get(t, ""),         # first tier entering the S&M grid
            "toponym_covered": t in covered,                  # in a non-queried Table-6.4 LA form
            "value_space": f"unicode_lb_syllabary_{len(syll)}",
            "maskable": bridged,                              # B-side attested in DĀMOS
            "robust_anchor": robust,                          # maskable AND >= MIN_LA_ATTEST
            "source_status": "cypriot:primary; homomorphy:pending_primary; value:secondary",
            "citations": (CIT_SEED if in_seed else CIT_BRIDGE) + " || homomorphy: " + CIT_SALG2020
                         + " || cypriot: " + CIT_SM2017,
            "disagreement_notes": SALG_TENSIONS.get(t, ""),   # authority tensions recorded,
                                                              # never resolved by convenience
        })

    # toponym seed table (Table 6.4, verified) — provenance-sourced lexical-anchor constraints
    with open(os.path.join(_HERE, "toponym_anchors.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["lb_form", "la_printed", "la_signs", "la_attestation",
                                          "lb_attestation", "page", "queried", "note", "citation"])
        w.writeheader()
        for tp in SM.TOPONYM_EQUATIONS:
            w.writerow({"lb_form": tp["lb"], "la_printed": tp["la_printed"],
                        "la_signs": "-".join(tp["la_signs"]),
                        "la_attestation": tp["la_attestation"],
                        "lb_attestation": tp["lb_attestation"], "page": tp["page"],
                        "queried": tp["queried"], "note": tp.get("note", ""),
                        "citation": SM.CITATION})

    out_csv = os.path.join(_HERE, "anchors.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = {
        "n_candidates": len(rows),
        "n_maskable": sum(r["maskable"] for r in rows),
        "n_robust_anchors": sum(r["robust_anchor"] for r in rows),
        "min_la_attest": MIN_LA_ATTEST,
        "not_maskable": [r["sign_id"] for r in rows if not r["maskable"]],
        "weak_maskable": [r["sign_id"] for r in rows if r["maskable"] and not r["robust_anchor"]],
        "n_cypriot_stable_confirmed": sum(r["cypriot_stable"] == "true" for r in rows),
        "cypriot_stable_signs": [r["sign_id"] for r in rows if r["cypriot_stable"] == "true"],
        "cypriot_candidates": [r["sign_id"] for r in rows if r["cypriot_stable"] == "candidate"],
        "n_sm2017_tiered": sum(bool(r["sm2017_tier"]) for r in rows),
        "toponym_covered_robust": [r["sign_id"] for r in rows
                                   if r["toponym_covered"] and r["robust_anchor"]],
        "n_primary_sourced_homomorph": sum("pending_primary" not in r["homomorphy_grade"]
                                           for r in rows),
        "n_homomorphy_pending_primary": sum("pending_primary" in r["homomorphy_grade"]
                                            for r in rows),
        "value_space_size": len(syll),
        "value_space_damos_attested": len(damos_attested_values),
        "value_space_unattested_in_damos": sorted(set(syll) - set(damos_attested_values)),
        "seed_signs_without_la_stream_presence": sorted(set(LB_TRANSFER_SIGNS) - set(a_ab)),
        "la_stream": {"sequences": len(a_seqs), "tokens": sum(a_freq.values())},
        "damos": {"wordforms": len(bd_seqs), "tokens": sum(bd_freq.values())},
    }
    with open(os.path.join(_HERE, "anchors_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
