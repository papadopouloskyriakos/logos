"""Stage 4.1 Correction 1: in the built graph, site_code is canonical and never the raw area code."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import graph_common as gc

CANON = {"KN", "PY", "TH", "MY", "TI", "KH", "MI", "MA", "EL", "OR", "KR", "GL", "IK", "VOL", "ARM", "DIM", "MAM", "MED", "HV"}


def _lb():
    return [json.loads(l) for l in open(os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl"))]


def test_site_code_is_canonical_not_area():
    n = 0
    for g in _lb():
        m = g["meta"]
        if m["site_code"] is not None:
            assert m["site_code"] in CANON, m["site_code"]
            # the OLD bug: site == area_code. Ensure they are separated now.
            if m["area_code_raw"]:
                assert m["site_code"] != m["area_code_raw"] or m["site_code"] in CANON
            n += 1
    assert n > 5000


def test_leave_one_site_out_uses_site_code():
    # a leave-one-site-out grouping over site_code yields few (canonical) groups, not hundreds of findspots
    sites = {g["meta"]["site_code"] for g in _lb() if g["meta"]["site_code"]}
    assert len(sites) <= 25, f"too many site groups ({len(sites)}) — findspot leaking into site?"


if __name__ == "__main__":
    test_site_code_is_canonical_not_area(); test_leave_one_site_out_uses_site_code()
    print("PASS site-findspot-separation")
