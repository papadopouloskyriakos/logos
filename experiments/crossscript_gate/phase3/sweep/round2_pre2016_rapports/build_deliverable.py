#!/usr/bin/env python3
"""build_deliverable.py — assemble the machine-readable, cross-referenced index of the
Linear A entries of the rapport series 1996-2021 (the deliverable shared with M. Del Freo).
Merges the round-1 fragment (Rapport 2016-2021) with the four round-2 fragments and adds a
mechanical corpus_status column (presence in the lineara.xyz-derived research corpus, via
the declared alias map). Counts are generated (index_counts.json), never hand-written."""
from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter

from round2_scan import ALIASES as R2_ALIASES, D_KEYS, FLAG_KEYS, norm

_HERE = os.path.dirname(os.path.abspath(__file__))
_SWEEP = os.path.dirname(_HERE)
OUT = os.path.join(_HERE, "deliverable")

SOURCES = [
    ("1996-2000", "fragments/delfreo_1996-2000.csv", _HERE),
    ("2001-2005", "fragments/delfreo_2001-2005.csv", _HERE),
    ("2006-2010", "fragments/delfreo_2006-2010.csv", _HERE),
    ("2011-2015", "fragments/delfreo_2011-2015.csv", _HERE),
    ("2016-2021", "fragments/delfreo.csv", _SWEEP),
]

R1_ALIASES = {
    "KN Zb 36a-d": ["KNZb<36>", "KNZb<37>"],
    "PYR Zb 5 (-> PYR Yb 01 (?))": ["PYRZb5"],
    "KN S (4/4) 01": [],
    "KN Zg 57": [], "KN Zg 58": [], "ZA 11": [],
    "(unassigned; Kommos vase fragment 2019)": [],
    "(unassigned; Phaistos Hagia Photini fragment)": [],
    "(unassigned; Phaistos Chalara fragment)": [],
    "(Zominthos libation table)": [],
    "SA We 4": [],
}
ALIASES = {**R1_ALIASES, **R2_ALIASES}

# items recorded in corpus/derived/post_gorila_additions/ (ours)
ADDITIONS = {
    "(unassigned; Phaistos Chalara fragment)": "ph_chalara_2017.json",
    "THE Zb 14": "the_zb_14.json (duplicate of corpus THEZb15, noted)",
    "VRY Za 4 (?)": "vry_za_4.json",
    "KN Zb 36a-d": "kn_zb_36a-d.json",
    "PSE Zb 1": "pse_zb_1.json",
    "SA We 3": "sa_we_3.json",
    "SA We 4": "sa_we_4.json",
}


def build() -> None:
    os.makedirs(OUT, exist_ok=True)
    inv = {norm(r["doc_id"]): r["doc_id"] for r in
           csv.DictReader(open(os.path.join(_SWEEP, "corpus_inventory.csv")))}
    rows_out, counts = [], Counter()
    for window, frag, base in SOURCES:
        with open(os.path.join(base, frag), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                r = {k.split("(")[0]: v for k, v in r.items()}
                des = r["designation"]
                if des.startswith("(GAP:"):
                    continue  # round-1 gap rows: resolved by this very acquisition
                notes_all = (r["notes"] + " " + r["description"]).lower()
                if des in ALIASES:
                    ids = ALIASES[des]
                    hits = [inv[norm(i)] for i in ids if norm(i) in inv]
                    present = bool(ids) and len(hits) == len(ids)
                else:
                    present = norm(des) in inv
                    hits = [inv[norm(des)]] if present else []
                if present:
                    status = "in corpus"
                    if hits and norm(des) not in {norm(h) for h in hits}:
                        status += " (as %s)" % "/".join(hits)
                    if any(k.lower() in notes_all for k in FLAG_KEYS):
                        status += "; see notes (divergence/doubt flag)"
                    counts["in_corpus"] += 1
                elif des in ADDITIONS:
                    status = ("absent from corpus; recorded in our additions layer (%s)"
                              % ADDITIONS[des])
                    counts["additions_layer"] += 1
                elif any(k in notes_all for k in D_KEYS):
                    status = "absent - correctly (negative verdict / deletion / non-item)"
                    counts["correctly_absent"] += 1
                elif r["accessibility"] == "pending_edition" or r["translit_printed"] == "no":
                    status = "absent (pending edition / no published reading)"
                    counts["absent_pending"] += 1
                else:
                    status = "absent (acquisition gap)"
                    counts["absent_gap"] += 1
                rows_out.append({"rapport_window": window, "designation": des,
                                 "site": r["site"], "description": r["description"],
                                 "publication": r["publication"], "year": r["year"],
                                 "pages": r["pages"],
                                 "translit_printed_in_rapport": r["translit_printed"],
                                 "accessibility": r["accessibility"],
                                 "corpus_status": status, "notes": r["notes"]})
                counts["rows_" + window] += 1
    path = os.path.join(OUT, "rapport_la_index_1996-2021.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    summary = {"total_rows": len(rows_out), **counts}
    json.dump(summary, open(os.path.join(OUT, "index_counts.json"), "w"), indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    build()
