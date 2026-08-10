#!/usr/bin/env python3
"""round2_scan.py — corpus-completeness sweep ROUND 2 (pre-2016 rapports, received from
M. Del Freo 2026-08-10). Mechanical diff of the four round-2 fragment CSVs against the
frozen corpus inventory, plus a silver-reading verification dump and the census scan of
the round-2 additions. The frozen corpus is read-only here; no statistics about anchors
are computed.

Deltas vs round-1 sweep_scan.py, all declared here (Art. VII / XI):
  1. ALIASES: an explicit designation -> inventory-id map for identities that plain
     normalization cannot see (sided IDs, alternative numbering schemes, sigla variants).
     Every alias is printed with the diff output.
  2. Classifier: round-1 classes kept; one amendment (a_ingestible no longer requires
     accessibility == open, because the held rapport itself prints the reading — the
     round-1 situation where the OA rapport was the source, generalized to the four
     author-PDF rapports we now hold); one new class d_correctly_absent for rows whose
     absence from the corpus is the *endorsed* state (negative verdicts, deletions,
     anepigraphic and bookkeeping rows).
  3. flagged_present: rows present in the inventory whose notes carry DOUBT/DIVERGENCE/
     identity flags — the round-2 payload for the divergence register.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_SWEEP = os.path.dirname(_HERE)
_GATE = os.path.dirname(os.path.dirname(_SWEEP))
_ROOT = os.path.dirname(os.path.dirname(_GATE))
ADDITIONS = os.path.join(_ROOT, "corpus", "derived", "post_gorila_additions")
SILVER = os.path.join(_ROOT, "corpus", "silver", "inscriptions_structured.json")

FRAGMENTS = [
    "fragments/delfreo_1996-2000.csv",
    "fragments/delfreo_2001-2005.csv",
    "fragments/delfreo_2006-2010.csv",
    "fragments/delfreo_2011-2015.csv",
]

# designation (verbatim from fragment CSV) -> list of inventory doc_ids that realize it.
# [] = deliberately no inventory identity (undesignated / non-item / identity unverified).
ALIASES = {
    "KH 97": ["KH97a", "KH97b"],
    "PE 6": ["PEZg6"],
    "PO Zf 2": ["PORZf2"],
    "SY Za 8-12": ["SYZa8", "SYZa9", "SYZa10", "SYZa11", "SYZa12"],
    "SY Za 1-12 + SY Zb 7": ["SYZa1", "SYZa2", "SYZa3", "SYZa4", "SYZa5", "SYZa6",
                             "SYZa8", "SYZa9", "SYZa10", "SYZa11", "SYZa12", "SYZb7"],
    "MIL Zb 2-7": ["MILZb2", "MILZb3", "MILZb4"],
    "MIL Zb 2-4 (edition)": ["MILZb2", "MILZb3", "MILZb4"],
    "GO 2": ["GO2r", "GO2v"],
    "THE Zb 14": ["THEZb15"],  # silver follows the editors' numbering for the lamp
    "(KH 97, Zb 98, 99, 100, Wc 2123 published)": ["KH97a", "KH97b", "KHZb98", "KH99",
                                                   "KH100", "KHWc2123"],
    "(Phylakopi handle = MI Zb 3 (?))": ["MIZb3"],
    "HT Zf (HM 767) (gold disc on bull figurine)": ["HTZf(HM767)"],
    "THE 7, THE 8 (and THE Z 9?)": [],   # identity vs THEfr./THEtab. NOT verified
    "THE 7-12": [],                      # identity vs THEfr./THEtab. NOT verified
    "(Zominthos libation table)": [],    # silver ZO1 is a DIFFERENT object (verified)
    "ZA Zb 35 (-> ZA Zb 39)": [],
    "{SA Wc 1} / {SA Wc 2}": [],
    "(COPILA catalogue)": [],
    "(THE numbering)": [],
    "(Troy spindle-whorls)": [],
    "(Rolletmuseum alabastron)": [],
    "(Ithaca Pelikata sherds + Haghios Athanasios tablet)": [],
    "(Miletus new fragments)": [],
    "(Florence nodules republished)": [],
    "(Mochlos Block C fragments)": [],
}

D_KEYS = ("negative verdict", "bookkeeping", "deleted", "anepigraphic",
          "correctly absent", "removal row")  # matched case-insensitively
FLAG_KEYS = ("DOUBT FLAG", "DIVERGENCE FLAG", "divergence-register candidate",
             "identity flag", "ERRATUM", "SUPERSEDED READING", "REMOVAL-CANDIDATE")


def norm(d: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", d.upper())


def load_rows():
    rows = []
    for frag in FRAGMENTS:
        with open(os.path.join(_HERE, frag), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows.append({k.split("(")[0]: v for k, v in r.items()})
    return rows


def diff() -> None:
    inv = {norm(r["doc_id"]) for r in
           csv.DictReader(open(os.path.join(_SWEEP, "corpus_inventory.csv")))}
    rows = load_rows()
    present, missing, flagged, partial_alias = [], [], [], []
    for r in rows:
        des, notes = r["designation"], r["notes"] + " " + r["description"]
        if des in ALIASES:
            ids = ALIASES[des]
            hit = [i for i in ids if norm(i) in inv]
            is_present = bool(ids) and len(hit) == len(ids)
            if ids and hit and not is_present:
                partial_alias.append({"designation": des, "hit": hit, "declared": ids})
        else:
            is_present = norm(des) in inv
        if is_present:
            present.append(des)
            if any(k in notes for k in FLAG_KEYS):
                flagged.append({"designation": des,
                                "flags": [k for k in FLAG_KEYS if k in notes],
                                "channel": r["channel"]})
        else:
            cls = ("d_correctly_absent" if any(k in notes.lower() for k in D_KEYS)
                   else "a_ingestible" if r["translit_printed"].startswith("yes")
                   and r["accessibility"] in ("open", "paywalled")
                   else "c_pending_edition" if r["accessibility"] == "pending_edition"
                   or r["translit_printed"] == "no"
                   else "b_acquisition_gap")
            missing.append({**r, "class": cls})
    with open(os.path.join(_HERE, "missing_round2.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(missing[0].keys()))
        w.writeheader()
        w.writerows(missing)
    out = {"fragment_rows": len(rows),
           "rows_per_fragment": dict(Counter(r["channel"] for r in rows)),
           "present_in_inventory": len(present),
           "present_with_divergence_flag": flagged,
           "n_flagged_present": len(flagged),
           "missing_total": len(missing),
           "missing_by_class": dict(Counter(m["class"] for m in missing)),
           "missing_designations_by_class": {
               c: [m["designation"] for m in missing if m["class"] == c]
               for c in sorted({m["class"] for m in missing})},
           "aliases_declared": {k: v for k, v in ALIASES.items()},
           "partial_alias_hits": partial_alias,
           "note": "round-2 diff of the four pre-2016 rapport fragments vs the frozen "
                   "1,341-item inventory; classifier deltas documented in this script's "
                   "docstring"}
    json.dump(out, open(os.path.join(_HERE, "diff_round2.json"), "w"), indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "aliases_declared"},
                     indent=2))


VERIFY_IDS = [
    "ARKHZc8", "ARKHZf9", "KNZb52", "KNZe56", "KNZb<27>", "KN49",
    "KH97a", "KH97b", "KHZb98", "KHWc2123", "KHWc2124", "KH99", "KH100", "KH101",
    "KH102", "KH103", "KH104", "KH105",
    "MAZb15", "PKZb21", "PKZb23", "PKZb25", "PKZb26", "PKZa27",
    "SYZa3", "SYZa4", "SYZa6", "SYZb7", "SYZa8", "SYZa9", "SYZa10", "SYZa11", "SYZa12",
    "PEZg6", "PEZb7", "PEZb8", "PH54", "PORZf2", "POZc1", "SKOZc1", "INZb1",
    "DRAZg1", "LACHZa1", "TELZb1", "MIZb1", "MI2", "MIZb3",
    "MILZb1", "MILZb2", "MILZb3", "MILZb4", "CRZg4",
    "GO2r", "GO2v", "GOWc1a", "GOWc1b", "HTZf(HM767)", "HTWa1547", "HTZb162",
    "HTWc3024", "ZAZg35", "ZO1",
    "THEZb1", "THEZb2", "THEZb3", "THEZb4", "THEZg5", "THEZb5", "THEZb6", "THEZb7",
    "THEZb13", "THEZb15", "THEZg15", "THEZg16",
    "THEfr.1", "THEfr.2", "THEfr.3", "THEtab.4", "THEtab.5",
    "IOZa16", "VRYZb2", "VRYZb3", "VRYZa4", "PSZa2", "ARZf1", "ARZf2", "KAZf1",
]


def verify() -> None:
    silver = {r["id"]: r for r in json.load(open(SILVER))}
    dump = {}
    for i in VERIFY_IDS:
        r = silver.get(i)
        if r is None:
            dump[i] = "NOT_IN_SILVER"
            continue
        nums = [s["v"] for s in r.get("stream", []) if s.get("t") == "num"]
        dump[i] = {"site": r.get("site", ""), "support": r.get("support", ""),
                   "context": r.get("context", ""), "words": r.get("words", []),
                   "numerals": nums}
    json.dump(dump, open(os.path.join(_HERE, "silver_verify_dump.json"), "w"),
              indent=2, ensure_ascii=False)
    print(json.dumps(dump, indent=2, ensure_ascii=False))


ROUND2_ADDITIONS = ["pse_zb_1.json", "sa_we_3.json", "sa_we_4.json"]


def scan() -> None:
    census = list(csv.DictReader(open(os.path.join(_GATE, "phase2",
                                                   "anchor_census.csv"))))
    words = {}
    for r in census:
        toks = tuple(s.strip().upper() for s in r["covered_signs"].split(",")
                     if s.strip())
        if len(toks) >= 2 and r["class"] in ("toponym", "personal_name",
                                             "gloss_acrophonic"):
            words[toks] = r["anchor_id"]
    new_legs, sign_delta, items = [], Counter(), []
    for fn in ROUND2_ADDITIONS:
        items.append(json.load(open(os.path.join(ADDITIONS, fn))))
    for it in items:
        for w in it.get("words", []):
            toks = tuple(t.upper() for t in w)
            sign_delta.update(toks)
            if toks in words:
                new_legs.append({"anchor_id": words[toks], "word": "-".join(toks),
                                 "item": it["id"]})
    out = {"n_round2_addition_items": len(items),
           "round2_addition_ids": [it["id"] for it in items],
           "new_legs": new_legs, "n_new_legs": len(new_legs),
           "covered_sign_attestation_delta": dict(sign_delta)}
    json.dump(out, open(os.path.join(_HERE, "scan_round2.json"), "w"), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    {"diff": diff, "verify": verify, "scan": scan}[sys.argv[1]]()
