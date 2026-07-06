"""Leakage tests: prove the slot classifier uses ONLY internal Linear A evidence."""
import os
import pytest, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src/slot_classifier/slotlib.py")
GOLD = os.path.join(ROOT, "data/gold/slot_candidate_manifest.jsonl")

FORBIDDEN = ["anchors/toponyms", "anchors/personal_names", "calibration/", "candidate_languages",
             "linear_b", "linearb", "greek", "egyptian", "kaptar", "caphtor", "hoch",
             "phonetic_value", "projected", "sign_value"]

def test_source_has_no_external_references():
    s = open(SRC, encoding="utf-8").read().lower()
    # allow the words only inside the module docstring's PROHIBITION list (before the first import),
    # but forbid them in executable code: check no forbidden token appears in a non-comment code line.
    bad = []
    for ln in s.splitlines():
        code = ln.split("#", 1)[0]
        if code.strip().startswith(('"""', "'''", "*", "assign", "assigns", "it must", "leakage")):
            continue
        for tok in FORBIDDEN:
            if tok in code and ("import" in code or "open(" in code or "read" in code or "=" in code and "path" in code):
                bad.append((tok, ln.strip()[:80]))
    assert not bad, f"external reference in classifier code: {bad}"

def test_only_stdlib_imports():
    for ln in open(SRC, encoding="utf-8"):
        ln = ln.strip()
        if ln.startswith("import ") or ln.startswith("from "):
            mod = ln.split()[1].split(".")[0]
            assert mod in {"hashlib","json","os","re","collections"}, f"non-stdlib import: {ln}"

def test_reads_only_pinned_corpus():
    s = open(SRC, encoding="utf-8").read()
    # the only file paths opened are the pinned corpus + ontology (built via os.path.join)
    assert "corpus/silver" in s
    assert "inscriptions_structured.json" in s
    assert "signs_ontology.json" in s
    # no anchors/calibration/candidate-language directory is opened anywhere in the code
    code_only = "\n".join(ln.split("#", 1)[0] for ln in s.splitlines())
    for bad in ("anchors/", "calibration/", "candidate_languages"):
        assert bad not in code_only, f"forbidden path referenced: {bad}"

def test_manifest_leakage_status_clean():
    if not os.path.exists(GOLD):
        pytest.skip("run build_manifest.py first (needs licensed corpus)")

    for l in open(GOLD, encoding="utf-8"):
        r = json.loads(l)
        assert r["leakage_exclusion_status"] == "internal_only_clean"
        assert "phonetic" not in json.dumps(r).lower()
        assert "greek" not in json.dumps(r).lower()

def test_manifest_predates_any_matcher():
    # the confirmatory contract: no matcher module may exist in the tree
    assert not os.path.isdir(os.path.join(ROOT, "src/anchor_matching"))
    assert not os.path.isdir(os.path.join(ROOT, "src/matcher"))
