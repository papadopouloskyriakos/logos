#!/usr/bin/env python3
"""Stage 4: deterministic labeling functions (LFs) for programmatic weak supervision (NO LLM, NO eval gold).

Each LF votes a coarse role or ABSTAINs, from a source index OR an observable structural rule. Structural LFs
are kept SEPARATE from lexical/philological reference LFs (dependency class recorded). LFs never read the
REFERENCE_GOLD_A eval answers directly for the vote; index LFs cite the published index rule. No Linear A, no
model predictions, no candidate-language info.
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "source_labels"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "admin_schema", "src", "corpus"))
import graph_common as gc
import lb_indexes as IDX

ABSTAIN = None
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
VOCAB = os.path.join(gc.EVAL_ONLY, "lb_dephon_vocab.json")

# LF -> dependency/independence class (for WS3 + LF_CROSS_SOURCE_CONCORDANCE gating)
LF_CLASS = {
    "LF_TOPONYM_INDEX": "SHARED_DECIPHERMENT", "LF_TITLE_INDEX": "SHARED_DECIPHERMENT",
    "LF_PERSON_NAME_INDEX": "SHARED_DECIPHERMENT", "LF_OPERATOR_INDEX": "SHARED_DECIPHERMENT",
    "LF_QUALIFIER_INDEX": "SHARED_DECIPHERMENT",
    "LF_LOGOGRAM_ADJACENCY": "EDITION_INDEPENDENT", "LF_NUMERAL_POSITION": "EDITION_INDEPENDENT",
    "LF_ENTRY_POSITION": "EDITION_INDEPENDENT", "LF_DOCUMENT_SERIES": "EDITION_INDEPENDENT",
    "LF_RECURRENCE_PATTERN": "EDITION_INDEPENDENT", "LF_HEADER_POSITION": "EDITION_INDEPENDENT",
    "LF_TOTAL_POSITION": "EDITION_INDEPENDENT", "LF_NEGATIVE_EXCLUSION": "EDITION_INDEPENDENT",
    "LF_CROSS_SOURCE_CONCORDANCE": "CROSS_CLASS",
}


def features():
    """Per distinct content WORD_FORM: translit + structural stats (edition-independent)."""
    sign_map = json.load(open(VOCAB))["B_SIGN"]
    def tr(fo):
        return "-".join(sign_map.get(s, "?") for s in fo.split("+"))
    F = defaultdict(lambda: {"occ": 0, "before_logo": 0, "before_num": 0, "entry_initial": 0,
                             "row_initial": 0, "series": set(), "sites": set()})
    for line in open(LB):
        g = json.loads(line)
        ids = {n["id"]: n for n in g["nodes"]}
        prec_logo = {e["src"] for e in g["edges"] if e["type"] == "PRECEDES_LOGOGRAM"}
        prec_num = {e["src"] for e in g["edges"] if e["type"] == "PRECEDES_NUMERAL"}
        # first WORD_FORM per entry / row
        entry_first, row_first = {}, {}
        for e in g["edges"]:
            if e["type"] == "CONTAINS" and ids.get(e["dst"], {}).get("type") == "WORD_FORM":
                pos = ids[e["dst"]].get("position", 99)
                if e["src"].startswith(g["graph_id"] + ":E"):
                    if e["src"] not in entry_first or pos < entry_first[e["src"]][1]:
                        entry_first[e["src"]] = (e["dst"], pos)
        first_ids = {v[0] for v in entry_first.values()}
        for n in g["nodes"]:
            if n["type"] != "WORD_FORM" or n["opaque_id"].count("+") < 1:
                continue
            f = F[n["opaque_id"]]; f["occ"] += 1
            f["series"].add(g["meta"]["document_series"]); f["sites"].add(g["meta"]["site_code"])
            if n["id"] in prec_logo: f["before_logo"] += 1
            if n["id"] in prec_num: f["before_num"] += 1
            if n["id"] in first_ids: f["entry_initial"] += 1
    return {fo: dict(d, translit=tr(fo)) for fo, d in F.items()}


# ---- Labeling functions: (form_opaque, feat) -> coarse role or ABSTAIN --------------------------
def _idx(name):
    def lf(fo, ft):
        for n, coarse, *_ in IDX.lookup(ft["translit"]):
            if n == name:
                return coarse
        return ABSTAIN
    return lf


LF_TOPONYM_INDEX = _idx("LF_TOPONYM_INDEX")
LF_TITLE_INDEX = _idx("LF_TITLE_INDEX")
LF_OPERATOR_INDEX = _idx("LF_OPERATOR_INDEX")
LF_QUALIFIER_INDEX = _idx("LF_QUALIFIER_INDEX")


def LF_PERSON_NAME_INDEX(fo, ft):
    # NO machine-readable PN index -> abstain (honest; do not fabricate PN labels)
    return ABSTAIN


def LF_LOGOGRAM_ADJACENCY(fo, ft):
    # a form that (almost) always immediately precedes a logogram behaves like a counted/recipient head
    return "COMMODITY_OR_COUNTED_CATEGORY" if ft["occ"] >= 3 and ft["before_logo"] / ft["occ"] > 0.6 else ABSTAIN


def LF_NUMERAL_POSITION(fo, ft):
    return "HUMAN_OR_INSTITUTION" if ft["occ"] >= 3 and ft["before_num"] / ft["occ"] > 0.7 else ABSTAIN


def LF_ENTRY_POSITION(fo, ft):
    return "HUMAN_OR_INSTITUTION" if ft["occ"] >= 3 and ft["entry_initial"] / ft["occ"] > 0.8 else ABSTAIN


def LF_DOCUMENT_SERIES(fo, ft):
    return ABSTAIN                                     # diagnostic only (§: series is a shortcut) -> abstain in WS


def LF_RECURRENCE_PATTERN(fo, ft):
    # forms recurring across many sites behave like place/institution rather than individual persons
    return "PLACE" if len(ft["sites"]) >= 3 else ABSTAIN


def LF_HEADER_POSITION(fo, ft):
    return "DOCUMENT_STRUCTURE" if ft["occ"] >= 4 and ft["entry_initial"] / ft["occ"] > 0.9 and ft["before_num"] == 0 else ABSTAIN


def LF_TOTAL_POSITION(fo, ft):
    return "DOCUMENT_STRUCTURE" if ft["translit"] in IDX.TOTALS else ABSTAIN


def LF_NEGATIVE_EXCLUSION(fo, ft):
    # explicit NOT-a-content-role signal: pure notation-adjacent hapax with no index hit -> UNKNOWN vote
    return "UNKNOWN" if ft["occ"] == 1 and not IDX.lookup(ft["translit"]) and ft["before_num"] == 0 else ABSTAIN


def LF_CROSS_SOURCE_CONCORDANCE(fo, ft):
    # independent evidence ONLY across independence classes: index (SHARED_DECIPHERMENT) AND a structural LF agree
    idx_vote = LF_TOPONYM_INDEX(fo, ft) or LF_TITLE_INDEX(fo, ft)
    struct_vote = LF_RECURRENCE_PATTERN(fo, ft) or LF_NUMERAL_POSITION(fo, ft)
    return idx_vote if (idx_vote and struct_vote and idx_vote == struct_vote) else ABSTAIN


LFS = {n: g for n, g in globals().items() if n.startswith("LF_") and callable(g)}
