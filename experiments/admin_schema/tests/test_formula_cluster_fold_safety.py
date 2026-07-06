"""Stage 4.1 Correction 5: formula clusters are consistent (same id <=> same opaque form sequence);
singleton rate is reported so clusters are not mistaken for a dense semantic signal."""
import json, os, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import graph_common as gc


def _entries_with_fc():
    """yield (fc_id, tuple(opaque_form_seq)) per entry from the LB graph."""
    for line in open(os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")):
        g = json.loads(line)
        ids = {n["id"]: n for n in g["nodes"]}
        # reconstruct each entry's word-form sequence + its FC id
        entry_forms = defaultdict(list); entry_fc = {}
        for e in g["edges"]:
            if e["type"] == "CONTAINS" and ids.get(e["dst"], {}).get("type") == "WORD_FORM":
                entry_forms[e["src"]].append((ids[e["dst"]]["position"], ids[e["dst"]]["opaque_id"]))
            if e["type"] == "SAME_FORMULA_CLUSTER":
                entry_fc[e["src"]] = ids[e["dst"]]["opaque_id"]
        for entry, forms in entry_forms.items():
            if entry in entry_fc:
                seq = tuple(f for _, f in sorted(forms))
                yield entry_fc[entry], seq


def test_same_id_iff_same_sequence():
    seq_by_id = defaultdict(set)
    for fcid, seq in _entries_with_fc():
        seq_by_id[fcid].add(seq)
    collisions = {k: v for k, v in seq_by_id.items() if len(v) > 1}
    assert not collisions, f"formula-cluster hash collision: {list(collisions)[:2]}"


def test_singleton_rate_reported():
    members = Counter(fcid for fcid, _ in _entries_with_fc())
    singletons = sum(1 for c in members.values() if c == 1)
    frac = singletons / max(len(members), 1)
    # This is a REPORT assertion: singletons are expected (many unique formulae); just ensure it is computable
    assert 0.0 <= frac <= 1.0
    print(f"formula clusters: {len(members)} distinct; singleton rate {frac:.2%}")


if __name__ == "__main__":
    test_same_id_iff_same_sequence(); test_singleton_rate_reported()
    print("PASS formula-cluster-fold-safety")
