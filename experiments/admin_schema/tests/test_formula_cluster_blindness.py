"""Stage 4.1 Correction 5: formula cluster ids depend ONLY on opaque form ids (no semantic input)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import formula_clustering as fc


def test_cluster_id_rejects_non_opaque_input():
    ok = fc.cluster_id(["B_SIGN_007+B_SIGN_081", "B_SIGN_012"])
    assert ok.startswith("FC_") and len(ok) == 19
    for bad in (["ko-no-so"], ["Knossos"], ["PLACE"], ["gloss:oil"]):
        try:
            fc.cluster_id(bad); raise SystemExit(f"accepted non-opaque input {bad}")
        except AssertionError:
            pass


def test_deterministic_and_order_sensitive():
    a = fc.cluster_id(["B_SIGN_007", "B_SIGN_012"])
    assert a == fc.cluster_id(["B_SIGN_007", "B_SIGN_012"])
    assert a != fc.cluster_id(["B_SIGN_012", "B_SIGN_007"])


def test_classification_is_grouping_only():
    assert fc.CLASSIFICATION == "GROUPING_ONLY"


if __name__ == "__main__":
    test_cluster_id_rejects_non_opaque_input(); test_deterministic_and_order_sensitive(); test_classification_is_grouping_only()
    print("PASS formula-cluster-blindness")
