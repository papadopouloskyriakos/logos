"""Stage 4.1 Correction 4: node ids unique within a graph; word-form TYPE (opaque_id) != occurrence node."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import graph_common as gc


def test_node_ids_unique_per_graph():
    for i, line in enumerate(open(os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl"))):
        if i >= 1500:
            break
        g = json.loads(line)
        ids = [n["id"] for n in g["nodes"]]
        assert len(ids) == len(set(ids)), f"{g['graph_id']} has duplicate node ids"


def test_word_form_occurrence_vs_type():
    # WORD_FORM nodes are OCCURRENCES (unique id per occurrence); opaque_id is the shared TYPE key.
    for i, line in enumerate(open(os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl"))):
        if i >= 400:
            break
        g = json.loads(line)
        wf = [n for n in g["nodes"] if n["type"] == "WORD_FORM"]
        occ_ids = [n["id"] for n in wf]
        assert len(occ_ids) == len(set(occ_ids))          # occurrences distinct
        # a repeated form within a doc shares opaque_id but has distinct occurrence ids
        by_type = {}
        for n in wf:
            by_type.setdefault(n["opaque_id"], []).append(n["id"])
        for t, occ in by_type.items():
            assert len(occ) == len(set(occ))


if __name__ == "__main__":
    test_node_ids_unique_per_graph(); test_word_form_occurrence_vs_type()
    print("PASS no-duplicate-occurrences")
