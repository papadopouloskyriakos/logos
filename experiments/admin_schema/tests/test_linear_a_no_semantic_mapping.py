"""Stage 4.1 Correction 3: LA carries NO semantic mapping and NO cross-script sign/logogram equivalence."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import graph_common as gc
import validate_admin_graph as V


def test_no_forbidden_fields_in_la():
    for line in open(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl")):
        assert V._forbidden_hit(json.loads(line)) is None


def test_la_signs_are_separate_vocab():
    # LA opaque ids must be A_* ; never a B_* id (no vocab merge)
    for i, line in enumerate(open(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl"))):
        if i >= 400:
            break
        for n in json.loads(line)["nodes"]:
            oid = n.get("opaque_id")
            if oid:
                assert not oid.startswith("B_"), f"LB id leaked into LA: {oid}"


def test_la_logogram_fraction_are_opaque_not_lb_meaning():
    # Stage 4.2: LA logograms/fractions are opaque A_LOGO_/A_FRAC_ (never an LB commodity name/value)
    seen_logo = seen_frac = False
    for line in open(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl")):
        for n in json.loads(line)["nodes"]:
            if n["type"] == "LOGOGRAM":
                assert n["opaque_id"].startswith("A_LOGO_"); seen_logo = True
            if n["type"] == "FRACTION":
                assert n["opaque_id"].startswith("A_FRAC_"); seen_frac = True
    assert seen_logo and seen_frac


def test_la_vocab_files_are_disjoint():
    a = set(json.load(open(os.path.join(gc.EVAL_ONLY, "la_dephon_vocab.json")))["A_SIGN"].keys())
    b = set(json.load(open(os.path.join(gc.EVAL_ONLY, "lb_dephon_vocab.json")))["B_SIGN"].keys())
    assert a.isdisjoint(b), "A_SIGN and B_SIGN opaque-id namespaces overlap"


if __name__ == "__main__":
    test_no_forbidden_fields_in_la(); test_la_signs_are_separate_vocab()
    test_la_logogram_fraction_are_opaque_not_lb_meaning(); test_la_vocab_files_are_disjoint()
    print("PASS la-no-semantic-mapping")
