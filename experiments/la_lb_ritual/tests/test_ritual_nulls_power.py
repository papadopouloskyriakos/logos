"""§X ritual nulls + power: exact FP low, permissive-edit FP ~1 (drift uncalibrated), post-hoc penalty
applied, exact power full / drift inadmissible. Deterministic."""
import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sim"))
import simlib as S, nulls_power as NP  # noqa: E402
pytestmark = pytest.mark.skipif(not os.path.exists(f"{S.GOLD}/la_ritual_candidate_packet.jsonl"), reason="packets absent")

@pytest.fixture(scope="module")
def r(): return NP.run()

def test_exact_families_specific(r):
    for k in ("1_random_pairing","2_freqmatched_synth_ritual","3_lenmatched_synth_targets","8_perturbed_equivalence"):
        assert r["null_families"][k]["fp_rate_ge1"] < 0.05

def test_permissive_edit_uncalibrated(r):
    assert r["null_families"]["10_permissive_best_of_edit"]["fp_rate_ge1"] > 0.9   # drift flexibility -> FP ~1

def test_posthoc_penalty_bounds_fp(r):
    p = r["null_families"]["12_posthoc_selection_penalty"]
    assert p["posthoc_bounded_fp"] >= p["nominal_fp"]

def test_power_exact_full_drift_inadmissible(r):
    assert r["power"]["exact_continuity"]["min_detectable_pairs"] == 1
    assert r["power"]["drift_continuity"]["admissible_model"] is False
    assert r["power"]["prob_no_power_realistic"] == 0.6

def test_determinism(r):
    assert NP.run()["power"] == r["power"]
