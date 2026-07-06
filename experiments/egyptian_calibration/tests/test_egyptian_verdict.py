"""§XI verdict (post-unblock): COMPLETE / READY_FOR_PREREG_DRAFT, mechanically derived, deterministic,
no Cretan leakage, confirmatory contingent on REQ-01."""
import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "calibration"))
import verdict as V  # noqa: E402

_HAVE = os.path.exists(os.path.join(os.path.dirname(__file__), "..", "results", "gate.json"))
pytestmark = pytest.mark.skipif(not _HAVE, reason="gate results not present (run gate.py first)")


def test_status_complete_and_ready():
    v = V.run()["verdict"]
    assert v["status"] == "COMPLETE"
    assert v["egyptian_channel_readiness"] == "READY_FOR_PREREG_DRAFT"


def test_key_criteria_pass():
    c = V.run()["verdict"]["criteria"]
    assert c["model_beats_baselines_heldout"] is True
    assert c["matched_scarcity_control_pass"] is True
    assert c["end_to_end_fp_acceptable"] is True
    assert c["uncertainty_does_not_reverse"] is True
    assert c["corpus_valid_provenance_complete"] is True


def test_cretan_confirmatory_contingent_on_req01():
    c = V.run()["verdict"]["criteria"]
    assert c["req01_primary_unresolved_cretan_confirmatory_ineligible"] is True
    assert "REQ-01" in V.run()["verdict"]["contingency"]


def test_determinism():
    assert V.run() == V.run()
