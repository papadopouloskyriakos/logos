"""Stage 4.1 Correction 2: scribal hand recovered from the populated DAMOS hand field (not vasewriter)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import graph_common as gc


def test_scribe_channel_available():
    gs = [json.loads(l) for l in open(os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl"))]
    with_hand = [g for g in gs if g["meta"]["scribe"]]
    assert len(with_hand) > 1000, "scribe channel should be AVAILABLE (hand_easy), not empty"
    assert all(g["meta"]["scribe"].startswith("HAND_") for g in with_hand)
    assert all(g["meta"]["scribe_source"] in ("hand_easy", "handpreptt3", "newhand") for g in with_hand)
    n_scribes = len({g["meta"]["scribe"] for g in with_hand})
    assert n_scribes > 30, n_scribes


if __name__ == "__main__":
    test_scribe_channel_available(); print("PASS scribe-crosswalk")
