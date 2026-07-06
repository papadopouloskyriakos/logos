"""Stage 4.1 Correction 1: canonical site mapping (heading prefix -> site), deterministic."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import site_mapping as sm

EXPECT = {"KN": "Knossos", "PY": "Pylos", "TH": "Thebes", "MY": "Mycenae", "TI": "Tiryns", "KH": "Khania"}


def test_canonical_prefixes():
    for code, name in EXPECT.items():
        m = sm.site_meta(f"{code} Fp 1", "SomeRoom")
        assert m["site_code"] == code and m["site_name"] == name, m


def test_findspot_preserved_and_separate():
    m = sm.site_meta("KN Fp 1", "Room 8")
    assert m["site_code"] == "KN"
    assert m["findspot_code"] == "Room 8" and m["area_code_raw"] == "Room 8"
    assert m["site_code"] != m["area_code_raw"]           # site is NOT the findspot


def test_deterministic():
    a = sm.site_meta("PY Ta 641", "X")
    b = sm.site_meta("PY Ta 641", "X")
    assert a == b


def test_missing_prefix_flagged():
    m = sm.site_meta("weird-no-prefix", None)
    assert m["site_code"] is None and m["site_mapping_confidence"] in ("NO_PREFIX", "UNMAPPED")


if __name__ == "__main__":
    test_canonical_prefixes(); test_findspot_preserved_and_separate(); test_deterministic(); test_missing_prefix_flagged()
    print("PASS site-mapping")
