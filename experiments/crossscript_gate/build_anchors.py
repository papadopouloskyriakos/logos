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

MIN_LA_ATTEST = 3           # B.2's min-count for a stable context vector (phono_distributional)

CIT_SEED = ("GORILA (Godart & Olivier 1976-1985); LB values after Ventris 1953 "
            "[litindex.py lb_value_transfer seed]")
CIT_BRIDGE = ("scripts/cross_script/data.py bridge: GORILA romanization == Unicode LB syllable "
              "value (Unicode chart cross-check); NOT in the litindex seed — needs citation "
              "before graduating to seed status")
CIT_SM2017 = ("Steele & Meissner 2017, 'Linear A and Linear B: structural and contextual "
              "concerns', in Understanding Relations Between Scripts (Oxbow), 93-110 — "
              "ABSENT from repo (all-rights-reserved, not acquired; docs/related/_acquisition.md)")
CIT_SALG2020 = ("Salgarella 2020, Aegean Linear Script(s) (CUP) — ABSENT from repo "
                "(paywalled, operator-supplies; docs/related/_acquisition.md)")


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

    rows = []
    for t in a_ab:
        la = a_freq.get(t, 0)
        damos = bd_freq.get(t, 0)
        in_seed = t in LB_TRANSFER_SIGNS
        bridged = damos >= 1
        robust = bridged and la >= MIN_LA_ATTEST
        rows.append({
            "sign_id": t,
            "ab_number": syll.get(t, ""),                     # '' if not an LB Unicode syllable
            "la_attestations": la,
            "damos_attestations": damos,
            "cog_attestations": bc_freq.get(t, 0),
            "conventional_value": t.lower(),
            "value_source": "litindex:lb_value_transfer" if in_seed else "data.py bridge convention",
            "homomorphy_grade": "pending_primary",            # Salgarella 2020 not on disk
            "cypriot_stable": "pending_primary",              # Steele & Meissner 2017 not on disk
            "value_space": f"unicode_lb_syllabary_{len(syll)}",
            "maskable": bridged,                              # B-side attested in DĀMOS
            "robust_anchor": robust,                          # maskable AND >= MIN_LA_ATTEST
            "source_status": "secondary",                     # citation held; primary edition absent
            "citations": (CIT_SEED if in_seed else CIT_BRIDGE) + " || homomorphy: " + CIT_SALG2020
                         + " || cypriot: " + CIT_SM2017,
            "disagreement_notes": "",                         # none DOCUMENTED in-repo; capture
                                                              # deferred to primary acquisition —
                                                              # never resolved by convenience
        })

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
        "n_cypriot_stable_confirmed": 0,
        "n_primary_sourced_homomorph": 0,
        "n_pending_primary": len(rows),
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
