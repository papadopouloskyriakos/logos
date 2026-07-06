"""§X final verdict: COMPLETE / NO_POWER / CIRCULARITY_LOW, mechanically derived, deterministic."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "continuity"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "common"))
import cfg  # noqa: E402
import verdict as V  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(cfg.LA_PACKET), reason="frozen packet absent")


@pytest.fixture(scope="module")
def v():
    return V.run()["verdict"]


def test_status_complete(v):
    assert v["status"] == "COMPLETE"


def test_readiness_no_power(v):
    assert v["channel_readiness"] == "NO_POWER"
    # NO_POWER because the drifted control is unrecoverable and held-out sits at null
    assert v["criteria"]["pc_drifted_recovered"] is False
    assert v["criteria"]["held_out_exceeds_null"] is False
    assert v["criteria"]["recovery_needs_flexible_mapping_for_realistic"] is True


def test_not_ready_and_not_incomplete(v):
    assert v["channel_readiness"] != "READY_FOR_PREREG_DRAFT"   # no signal above null
    assert v["status"] != "INCOMPLETE"                          # not used to dodge NO_POWER


def test_circularity_low(v):
    assert v["circularity"] == "CIRCULARITY_LOW"


def test_determinism(v):
    assert V.run()["verdict"] == v
