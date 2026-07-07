"""Task 8 tests: human-submission validation/ingestion. Uses SYNTHETIC fixtures in a TEMP dir so no fake
'completed' submission is ever written to the real data/human_pilot/completed/ path."""
import csv, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "annotation")))
import validate_human_submission as V

TMPL = ["anon_item_id"] + V.TEMPLATE_FIELDS[1:]


def _write(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); [w.writerow(r) for r in rows]


def _setup(tmp, done_rows):
    hp = os.path.join(tmp, "hp"); os.makedirs(os.path.join(hp, "completed"), exist_ok=True)
    ids = ["HP-0000", "HP-0001", "HP-0002"]
    _write(os.path.join(hp, "annotator_A_response_template.csv"),
           [{**{k: "" for k in TMPL}, "anon_item_id": i} for i in ids], TMPL)
    _write(os.path.join(hp, "completed", "annotator_A_completed.csv"), done_rows, TMPL)
    V.HP = hp
    return V.validate("A")


def _row(i, role="PLACE", tier="GOLD_B", conf="0.7", cite="Aura Jorro DMic s.v.", **kw):
    r = {k: "" for k in TMPL}; r.update({"anon_item_id": i, "coarse_role": role, "gold_tier": tier,
                                         "confidence": conf, "source_citation": cite, "rationale": "x"}); r.update(kw)
    return r


def test_no_submission():
    real = os.path.normpath(os.path.join(HERE, "..", "src", "annotation"))
    sys.path.insert(0, real); import importlib; importlib.reload(V)
    assert V.validate("A")["status"] == "NO_SUBMISSION"


def test_valid():
    with tempfile.TemporaryDirectory() as t:
        r = _setup(t, [_row("HP-0000"), _row("HP-0001", role="HUMAN_OR_INSTITUTION"), _row("HP-0002", role="UNKNOWN", tier="GOLD_X", cite="")])
        assert r["status"] == "VALID", r["errors"]


def test_missing_rows():
    with tempfile.TemporaryDirectory() as t:
        r = _setup(t, [_row("HP-0000"), _row("HP-0001")])
        assert r["status"] == "INVALID" and any("MISSING" in e for e in r["errors"])


def test_duplicate_rows():
    with tempfile.TemporaryDirectory() as t:
        r = _setup(t, [_row("HP-0000"), _row("HP-0000"), _row("HP-0001"), _row("HP-0002")])
        assert r["status"] == "INVALID" and any("DUPLICATE" in e for e in r["errors"])


def test_invalid_label():
    with tempfile.TemporaryDirectory() as t:
        r = _setup(t, [_row("HP-0000", role="MONSTER"), _row("HP-0001"), _row("HP-0002")])
        assert r["status"] == "INVALID" and any("invalid coarse_role" in e for e in r["errors"])


def test_changed_order():
    with tempfile.TemporaryDirectory() as t:
        r = _setup(t, [_row("HP-0002"), _row("HP-0001"), _row("HP-0000")])
        assert any("ORDER changed" in e for e in r["errors"])


def test_gold_a_requires_citation():
    with tempfile.TemporaryDirectory() as t:
        r = _setup(t, [_row("HP-0000", tier="GOLD_A", cite=""), _row("HP-0001"), _row("HP-0002")])
        assert any("requires source_citation" in e for e in r["errors"])


def test_model_generated_marker_warns():
    with tempfile.TemporaryDirectory() as t:
        rows = [_row("HP-0000", cite="model generated"), _row("HP-0001"), _row("HP-0002")]
        rows[0]["rationale"] = "auto model generated"
        r = _setup(t, rows)
        assert any("model" in w.lower() for w in r["provenance_warnings"])


def test_hash_manifest_matches_templates():
    import json
    man = os.path.normpath(os.path.join(HERE, "..", "data", "human_pilot", "human_pilot_manifest.json"))
    hp = os.path.normpath(os.path.join(HERE, "..", "data", "human_pilot"))
    if not os.path.exists(man):
        return
    import hashlib
    m = json.load(open(man))
    for fn in ("annotator_A_response_template.csv", "annotator_B_response_template.csv"):
        p = os.path.join(hp, fn)
        if os.path.exists(p):
            assert hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] == m["file_sha256_16"][fn]


if __name__ == "__main__":
    for fn in list(globals()):
        if fn.startswith("test_"):
            globals()[fn]()
    print("PASS human-annotation-pipeline")
