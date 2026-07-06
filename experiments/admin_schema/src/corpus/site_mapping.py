#!/usr/bin/env python3
"""Stage 4.1 Correction 1+2: canonical SITE (heading prefix) vs FINDSPOT (area_code), + scribal hand.

The Stage-4 bug mapped DĀMOS `area_code` (a room/area findspot code) into `meta.site`. The canonical
archaeological site is the DĀMOS heading PREFIX (KN/PY/TH/MY/TI/KH/…). This module derives, deterministically:
  site_code (prefix)  site_name (crosswalk)  findspot_code (area_code)  area_code_raw (preserved)
  document identifiers (current) ; scribe from the populated hand field (hand_easy), NOT vasewriter (empty).
Never infers site/scribe from lexical content or model behaviour.
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.normpath(os.path.join(HERE, "..", ".."))
CROSSWALK = os.path.join(EXP, "data", "reference", "site_crosswalk.csv")
SITE_MAPPING_VERSION = "site-crosswalk-v1-2026-07-07"
SCRIBE_CROSSWALK_VERSION = "scribe-crosswalk-v1-2026-07-07"
PREFIX_RE = re.compile(r"^\s*([A-Z]{2,3})\b")


def load_crosswalk():
    cw = {}
    if os.path.exists(CROSSWALK):
        for r in csv.DictReader(open(CROSSWALK)):
            cw[r["site_code"]] = (r["site_name"], r["confidence"])
    return cw


_CW = None


def site_meta(heading, area_code_raw):
    global _CW
    if _CW is None:
        _CW = load_crosswalk()
    m = PREFIX_RE.match(heading or "")
    code = m.group(1) if m else None
    name, conf = _CW.get(code, (None, "UNMAPPED" if code else "NO_PREFIX"))
    return {
        "site_code": code,
        "site_name": name,
        "site_mapping_source": "DAMOS heading prefix + data/reference/site_crosswalk.csv",
        "site_mapping_confidence": conf,
        "site_mapping_version": SITE_MAPPING_VERSION,
        "findspot_code": area_code_raw or None,        # the OLD (wrong) 'site' value, now correctly a findspot
        "area_code_raw": area_code_raw,                 # preserved exactly
        "document_identifier_prefix": code,
        "current_document_identifier": (heading or "").strip() or None,
    }


# DĀMOS hand fields ranked by coverage (Stage-4.1 audit): hand_easy (5712 non-null) is the operative field;
# vasewriter is empty. '-' means 'no hand assigned' -> scribe None.
def scribe_id(item):
    for field in ("hand_easy", "handpreptt3", "newhand"):
        v = item.get(field)
        if v not in (None, "", "-", 0, "0"):
            return f"HAND_{str(v).strip()}", field
    return None, None
