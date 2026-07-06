"""Pure unit tests for designation normalization — no data required, always run."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sigla_reconcile"))
import reconcile as R


def test_strict_norm_spaces_and_case():
    assert R.norm_desig("HT 24a") == "HT24A"
    assert R.norm_desig("HT24a") == "HT24A"
    assert R.norm_desig("KH Wc 2026") == "KHWC2026"
    # strict must NOT merge faces or joins
    assert R.norm_desig("HTWA1019Α") != R.norm_desig("HTWA1019")   # Greek face kept distinct
    assert R.norm_desig("HT123+124A") == "HT123+124A"


def test_base_key_collapses_faces_joins_cruft():
    assert R.base_key("HTWA1019Α") == "HTWA1019"      # Greek face -> stripped
    assert R.base_key("HTWA1019Γ") == "HTWA1019"
    assert R.base_key("HT24a") == "HT24"              # latin face -> stripped
    assert R.base_key("HT123+124A") == "HT123"        # join -> first member
    assert R.base_key("APZA<3>") == "APZA3"           # brackets stripped, number kept
    assert R.base_key("HT154.") == "HT154"            # trailing dot


def test_base_key_is_idempotent():
    for d in ("HT 24a", "HTWA1019Α", "HT123+124A", "KH Wc 2026"):
        assert R.base_key(R.base_key(d)) == R.base_key(d)


def test_period_norm():
    assert R.norm_period("LM IB") == R.norm_period("LMIB") == "LMIB"
    assert R.norm_period(None) == ""
