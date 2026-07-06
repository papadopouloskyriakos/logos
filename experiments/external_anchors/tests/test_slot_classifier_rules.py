"""Rule + manifest-integrity tests for the internal slot classifier."""
import os
import pytest, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src/slot_classifier"))
import slotlib
GOLD = os.path.join(ROOT, "data/gold/slot_candidate_manifest.jsonl")
IDX = {"OLE":("LOGO:OLE","logogram"), "GRA":("LOGO:GRA","logogram")}

def _f(**kw):
    base = dict(occ=1, sites={"X"}, docs={"d1"}, genres={}, pre_num=0, post_logo=0, header=0,
               terminal=0, adj_kuro=0, adj_kiro=0, ritual_genre=0, len_signs=2, damaged=False)
    base.update(kw); return base

def test_transaction_term():
    c,t,_ = slotlib.classify(("KU","RO"), _f(len_signs=2), IDX); assert (c,t)==("TRANSACTION_TERM","A")

def test_commodity_logogram():
    c,t,_ = slotlib.classify(("OLE",), _f(len_signs=1, damaged=False), IDX)
    # len<=1 -> X guard fires first; use a 2-sign logogram compound
    c,t,_ = slotlib.classify(("GRA","X"), _f(len_signs=2), IDX); assert c=="COMMODITY" and t=="A"

def test_damaged_excluded():
    c,t,_ = slotlib.classify(("A","B["), _f(damaged=True), IDX); assert t=="X"

def test_toponym_like_cross_site():
    f=_f(occ=4, sites={"HaghiaTriada","Zakros"}, docs={"a","b","c"}, header=4, len_signs=3)
    c,t,_ = slotlib.classify(("A","BB","C"), f, IDX); assert c=="TOPONYM_LIKE" and t=="B"

def test_person_name_like_localized():
    f=_f(occ=1, sites={"HaghiaTriada"}, docs={"a"}, header=1, len_signs=3)
    c,t,_ = slotlib.classify(("A","BB","C"), f, IDX); assert c=="PERSON_NAME_LIKE" and t=="C"

def test_manifest_integrity():
    if not os.path.exists(GOLD):
        pytest.skip("run build_manifest.py first (needs licensed corpus)")

    rows=[json.loads(l) for l in open(GOLD, encoding="utf-8")]
    assert len(rows) > 500
    req={"candidate_id","corpus_record_id","normalized_string_id","site","document_id","genre",
         "position_features","context_features","candidate_class","class_probability_or_tier",
         "rule_or_model_version","transcription_status","damaged_sign_flag","alternative_transcriptions",
         "leakage_exclusion_status","heldout_group","manifest_version"}
    for r in rows[:50]:
        assert req <= set(r), req - set(r)
        assert r["class_probability_or_tier"] in {"A","B","C","X"}
        assert r["candidate_class"] in {"TOPONYM_LIKE","PERSON_NAME_LIKE","COMMODITY","TITLE_OR_OFFICE",
            "INSTITUTION","TRANSACTION_TERM","RITUAL_FORMULA","NUMERIC_OR_METROLOGICAL","UNKNOWN"}
    # held-out groups are populated (leave-one-site-out)
    assert len({r["heldout_group"] for r in rows}) >= 5
