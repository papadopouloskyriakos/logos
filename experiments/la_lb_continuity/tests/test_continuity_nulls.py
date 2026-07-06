"""§V nulls: end-to-end false-positive rates are low (channel is specific), real-data controls give
zero, best-of-search combined FP is bounded, and the whole thing is deterministic."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "continuity"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "common"))
import cfg  # noqa: E402
import nulls as N  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(cfg.LA_PACKET), reason="frozen packet absent")


@pytest.fixture(scope="module")
def r():
    return N.run()


def test_mc_family_fp_rates_low(r):
    for k in ("1_random_pairing", "2_freqmatched_synth_LA", "3_lenmatched_synth_LB", "8_perturbed_equivalence"):
        assert r[k]["fp_rate_ge1"] < 0.05           # specific: chance rarely fabricates a match


def test_real_data_controls_zero(r):
    assert r["6_nontoponym_LA_controls"]["matches"] == 0
    assert r["7_false_LB_targets"]["matches"] == 0
    assert r["9_wrong_projected_values"]["matches"] == 0


def test_best_of_search_bounded(r):
    assert r["10_best_of_search"]["combined_fp_upper_bound"] < 0.10
    assert r["_observed_primary_matches"] == 0


def test_determinism():
    a = N.run()["2_freqmatched_synth_LA"]
    b = N.run()["2_freqmatched_synth_LA"]
    assert a == b
