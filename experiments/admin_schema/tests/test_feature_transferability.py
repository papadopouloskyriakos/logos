"""Stage 4 acceptance #4: every feature has exactly one valid transferability class; forbidden EXCLUDED."""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.normpath(os.path.join(HERE, "..", "data", "schema", "feature_transferability.csv"))
VALID = {"TRANSFERABLE", "LB_ONLY_DIAGNOSTIC", "AB_SHARED_SENSITIVITY", "EXCLUDED"}


def _rows():
    return list(csv.DictReader(open(CSV)))


def test_every_feature_has_valid_class():
    rows = _rows()
    assert len(rows) >= 20
    for r in rows:
        assert r["transferability_class"] in VALID, r


def test_forbidden_features_are_excluded():
    rows = {r["feature"]: r["transferability_class"] for r in _rows()}
    for f in ("phonetic_transliteration", "greek_lemma_gloss_translation", "known_role_or_entity"):
        assert rows.get(f) == "EXCLUDED", f


def test_scribe_is_lb_only_diagnostic():
    rows = {r["feature"]: r["transferability_class"] for r in _rows()}
    assert rows.get("scribe") == "LB_ONLY_DIAGNOSTIC"


def test_ab_shared_bridge_is_sensitivity_not_transferable():
    rows = {r["feature"]: r["transferability_class"] for r in _rows()}
    assert rows.get("ab_shared_sign_bridge") == "AB_SHARED_SENSITIVITY"


if __name__ == "__main__":
    test_every_feature_has_valid_class(); test_forbidden_features_are_excluded()
    test_scribe_is_lb_only_diagnostic(); test_ab_shared_bridge_is_sensitivity_not_transferable()
    print("PASS feature-transferability")
