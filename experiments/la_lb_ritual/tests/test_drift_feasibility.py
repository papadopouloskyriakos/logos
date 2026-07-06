"""§VIII drift feasibility: D3 not independently admissible; only D0/D1/D2 feasible; deterministic."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "drift_feasibility"))
import drift_feasibility as DF  # noqa: E402


def test_d3_not_admissible():
    d3 = DF.d3_admissibility()
    assert d3["D3_admissible"] is False
    assert "transformations_estimated_from_independent_data" in d3["blocking_criteria"]
    assert "target_pairs_absent_from_training" in d3["blocking_criteria"]


def test_only_exact_and_uncertainty_families_feasible():
    r = DF.run()
    assert r["feasible_families"] == ["D0_exact_identity", "D1_tierA_equivalence", "D2_source_grounded_uncertainty"]
    assert r["drift_model_feasible"] is False


def test_determinism():
    assert DF.run() == DF.run()
