"""§IV/§V frozen design: schema validity, Cretan-exclusion, corpus-blocked state, model-freeze determinism."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "calibration"))
import schema as SC  # noqa: E402

def test_schema_shape():
    assert len(SC.REQUIRED_FIELDS) == 27
    assert set(SC.ELIGIBILITY_TIERS) == {"A", "B", "C", "X"}
    assert "TOPONYM" in SC.ITEM_CLASSES and "PERSONAL_NAME" in SC.ITEM_CLASSES

def test_cretan_target_is_rejected():
    rec = {f: "x" for f in SC.REQUIRED_FIELDS}
    rec.update(item_class="TOPONYM", calibration_eligibility="A", source_id="kom_el_hetan_list", citation="Cretan")
    ok, why = SC.validate_record(rec)
    assert ok is False and "cretan" in why.lower()

def test_corpus_is_blocked_not_silently_empty():
    recs, blocker = SC.build_corpus()
    assert recs == [] and blocker["buildable"] is False
    assert "Hoch" in blocker["reason"] and "Muchiki" in blocker["unblock"]

def test_model_freeze_present_and_frozen():
    cfg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "configs", "egyptian_model_freeze.json")))
    assert cfg["status"] == "SPEC_FROZEN_AWAITING_CORPUS"
    assert set(cfg["model_families"]) == {f"M{i}" for i in range(10)}
    assert cfg["no_change_after_positive_control_visible"] is True
