#!/usr/bin/env python3
"""sweep_scan.py — §2 diff (checklist − inventory, + reverse) and §4 census re-scan of the
additions layer. Mechanical; no statistics about anchors are computed; the frozen corpus is
read-only here."""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_GATE = os.path.dirname(os.path.dirname(_HERE))
_ROOT = os.path.dirname(os.path.dirname(_GATE))
ADDITIONS = os.path.join(_ROOT, "corpus", "derived", "post_gorila_additions")


def norm(d: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", d.upper())


def diff() -> None:
    inv = {norm(r["doc_id"]) for r in csv.DictReader(open(f"{_HERE}/corpus_inventory.csv"))}
    chk = []
    for r in csv.DictReader(open(f"{_HERE}/published_record_checklist.csv")):
        chk.append({k.split("(")[0]: v for k, v in r.items()})   # strip '(yes/no/...)' suffixes
    missing, present = [], 0
    for r in chk:
        if norm(r["designation"]) in inv:
            present += 1
            continue
        cls = ("a_ingestible" if r["translit_printed"].startswith("yes")
               and r["accessibility"] == "open"
               else "c_pending_edition" if r["accessibility"] == "pending_edition"
               or r["translit_printed"] == "no"
               else "b_acquisition_gap")
        missing.append({**r, "class": cls})
    with open(f"{_HERE}/missing_items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(missing[0].keys()) if missing else
                           list(chk[0].keys()) + ["class"])
        w.writeheader()
        w.writerows(missing)
    chk_ids = {norm(r["designation"]) for r in chk}
    reverse = sorted(i for i in inv if i not in chk_ids)
    json.dump({"checklist_rows": len(chk), "already_in_inventory": present,
               "missing_total": len(missing),
               "missing_by_class": dict(Counter(m["class"] for m in missing)),
               "reverse_diff_inventory_not_in_checklist": len(reverse),
               "reverse_note": "expected large: the checklist enumerates POST-GORILA channels, "
                               "not the whole corpus — sanity signal only, nothing deleted"},
              open(f"{_HERE}/diff_summary.json", "w"), indent=2)
    print(json.dumps(json.load(open(f"{_HERE}/diff_summary.json")), indent=2))


def scan() -> None:
    census = list(csv.DictReader(open(f"{_GATE}/phase2/anchor_census.csv")))
    words = {}
    for r in census:
        toks = tuple(s.strip().upper() for s in r["covered_signs"].split(",") if s.strip())
        if len(toks) >= 2 and r["class"] in ("toponym", "personal_name", "gloss_acrophonic"):
            words[toks] = r["anchor_id"]
    new_legs, sign_delta = [], Counter()
    items = []
    if os.path.isdir(ADDITIONS):
        for fn in sorted(os.listdir(ADDITIONS)):
            if fn.endswith(".json"):
                items.append(json.load(open(os.path.join(ADDITIONS, fn))))
    for it in items:
        for w in it.get("words", []):
            toks = tuple(t.upper() for t in w)
            sign_delta.update(toks)
            if toks in words:
                new_legs.append({"anchor_id": words[toks], "word": "-".join(toks),
                                 "item": it["id"], "site": it.get("site", ""),
                                 "certainty": it.get("certainty", ""),
                                 "source": it.get("source", "")})
    out = {"n_addition_items": len(items),
           "new_legs": new_legs, "n_new_legs": len(new_legs),
           "covered_sign_attestation_delta": dict(sign_delta.most_common(30))}
    json.dump(out, open(f"{_HERE}/scan_summary.json", "w"), indent=2)
    print(json.dumps({k: v for k, v in out.items()
                      if k != "covered_sign_attestation_delta"}, indent=2))


if __name__ == "__main__":
    {"diff": diff, "scan": scan}[sys.argv[1]]()
