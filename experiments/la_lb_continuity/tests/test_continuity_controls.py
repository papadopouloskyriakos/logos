"""§IV positive controls: the detector recovers implanted / degraded / LB-internal persistence at the
real scarcity, and is specific (no incidental false matches). Skips without frozen packets."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "continuity"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "common"))
import cfg  # noqa: E402
import controls as C  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(cfg.LA_PACKET), reason="frozen packet absent")


def test_pc1_recovers_exact_implants_without_incidental_fp():
    for K in (1, 2, 3):
        r = C.pc1_synthetic_implant(K, cfg.SEED + K)["A1"]
        assert r["recovery_rate"] == 1.0            # exact implants always recovered
        assert r["incidental_fp_pairs"] == 0        # and no spurious matches


def test_pc2_a3_tolerance_recovers_degraded_a1_does_not():
    r = C.pc2_degraded_implant(3, cfg.SEED + 103)
    assert r["A1"]["recovered"] == 0                 # 1-mismatch breaks exact identity
    assert r["A3"]["recovered"] == r["A3"]["implanted"]   # prespecified wildcard recovers it


def test_pc3_lb_internal_self_persistence_specific():
    r = C.pc3_lb_internal(cfg.SEED + 7)
    assert r["recovery_rate"] == 1.0                 # true persistence recovered at matched scarcity
    assert r["cross_toponym_fp"] == 0                # distinct toponyms never falsely match


def test_determinism():
    assert C.pc1_synthetic_implant(3, 123) == C.pc1_synthetic_implant(3, 123)
    assert C.pc3_lb_internal(7) == C.pc3_lb_internal(7)
