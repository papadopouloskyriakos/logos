"""Stage 4 acceptance #1: every graph validates against the canonical schema (node/edge/provenance)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "src", "corpus"))
sys.path.insert(0, SRC)
import validate_admin_graph as V
import graph_common as gc


def test_lb_graph_validates():
    r = V.validate_file(os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl"))
    assert r["invalid"] == 0, r["errors"]
    assert r["graphs_checked"] > 5000


def test_la_graph_validates():
    r = V.validate_file(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl"))
    assert r["invalid"] == 0, r["errors"]
    assert r["graphs_checked"] > 1000


def test_example_matches_schema():
    import json
    ex = json.load(open(os.path.join(gc.EXP, "data", "schema", "admin_document_graph.example.json")))
    assert V.validate_graph(ex) == []


if __name__ == "__main__":
    test_lb_graph_validates(); test_la_graph_validates(); test_example_matches_schema()
    print("PASS schema")
