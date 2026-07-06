"""Stage 4.1 Correction 4: cardinality invariants (occurrence semantics; one-parent; no orphans)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import graph_common as gc


def _graphs(fn, limit=1500):
    for i, line in enumerate(open(os.path.join(gc.MODEL_VISIBLE, fn))):
        if i >= limit:
            break
        yield json.loads(line)


def test_each_sign_has_exactly_one_word_form_parent():
    for g in _graphs("lb_graph.jsonl"):
        ids = {n["id"]: n for n in g["nodes"]}
        parents = {}
        for e in g["edges"]:
            if e["type"] == "CONTAINS" and ids.get(e["dst"], {}).get("type") == "SIGN":
                parents.setdefault(e["dst"], set()).add(e["src"])
        for sid, ps in parents.items():
            assert len(ps) == 1, f"{g['graph_id']} sign {sid} has {len(ps)} parents"
            assert ids[next(iter(ps))]["type"] == "WORD_FORM"


def test_each_word_form_in_one_entry():
    for g in _graphs("lb_graph.jsonl"):
        ids = {n["id"]: n for n in g["nodes"]}
        parents = {}
        for e in g["edges"]:
            if e["type"] == "CONTAINS" and ids.get(e["dst"], {}).get("type") == "WORD_FORM":
                parents.setdefault(e["dst"], set()).add(e["src"])
        for wid, ps in parents.items():
            assert len(ps) == 1 and ids[next(iter(ps))]["type"] == "ENTRY"


def test_no_orphan_nodes():
    for g in _graphs("lb_graph.jsonl", 500):
        referenced = {g["graph_id"] + ":DOC"}
        for e in g["edges"]:
            referenced.add(e["src"]); referenced.add(e["dst"])
        orphans = [n["id"] for n in g["nodes"] if n["id"] not in referenced and n["type"] != "DOCUMENT"]
        assert not orphans, f"{g['graph_id']} orphans: {orphans[:3]}"


if __name__ == "__main__":
    test_each_sign_has_exactly_one_word_form_parent(); test_each_word_form_in_one_entry(); test_no_orphan_nodes()
    print("PASS cardinality-invariants")
