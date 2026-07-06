"""Stage 4 acceptance #2: rebuilding produces identical output (byte-for-byte / hash-stable)."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "src", "corpus"))
sys.path.insert(0, SRC)
import graph_common as gc
import build_linear_b_graph as B


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def test_lb_graph_hash_matches_manifest():
    man = json.load(open(os.path.join(gc.EXP, "data", "manifests", "stage4_1_graph_freeze.json")))
    assert _sha(os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")) == man["lb_graph_sha256_16"]
    assert _sha(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl")) == man["la_graph_sha256_16"]


def test_in_process_determinism():
    # build the same few documents twice -> identical JSON
    recs = B.load_damos()[:50]
    v = B.build_vocabs(recs)
    g1 = [json.dumps(B.build_doc(r, *v, {}), sort_keys=True) for r in recs
          if (r["item"].get("content") or "").strip()]
    v2 = B.build_vocabs(recs)
    g2 = [json.dumps(B.build_doc(r, *v2, {}), sort_keys=True) for r in recs
          if (r["item"].get("content") or "").strip()]
    assert g1 == g2 and len(g1) > 0


if __name__ == "__main__":
    test_lb_graph_hash_matches_manifest(); test_in_process_determinism()
    print("PASS determinism")
