"""§VII known ritual pair ledger: all quarantined CONFIRMATORY_INELIGIBLE, drift characterized."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "inventory"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "la_lb_continuity", "src", "common"))
import build_known_ritual_ledger as L  # noqa: E402


def test_all_quarantined_ineligible():
    for r in L.build():
        assert r["development_role"] == "KNOWN_PAIR_DEVELOPMENT"
        assert r["confirmatory_eligibility"] == "CONFIRMATORY_INELIGIBLE"
        assert r["posthoc_risk"] == "HIGH"
        assert r["channel_class"] == "EXPLORATORY_POSTHOC_CHANNEL"


def test_drift_characterization():
    rows = L.build()
    exact = [r for r in rows if r["exact_identity"]]
    drift = [r for r in rows if r["drift_required"]]
    assert len(exact) == 2 and len(drift) == 3
    for r in drift:
        assert r["number_of_edit_operations"] >= 1


def test_determinism():
    assert L.build() == L.build()
