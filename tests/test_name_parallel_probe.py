"""Locked properties of the NAME-PARALLEL-01 gated probe (experiments/name_parallel_probe/):

(a) fail-CLOSED refusals: absent calibration, RED calibration, fast-run calibration, and a
    plan_hash mismatch each refuse with verdict INVALID BEFORE any statistic is computed;
(b) prereg integrity: plan_hash.txt equals sha256(prereg.md) byte-for-byte;
(c) the committed result.json is internally consistent: allowed verdict, pinned M_obs=12 and
    DATA-LIMITED under bar v2, bar dominated by the lfake floor, S2 (toponym-excluded) = 0.
"""
import hashlib
import importlib.util
import json
import os
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

PROBE_DIR = os.path.join(_REPO_ROOT, "experiments", "name_parallel_probe")
DRIVER = os.path.join(PROBE_DIR, "run_probe.py")


def _load_driver():
    spec = importlib.util.spec_from_file_location("np_run_probe", DRIVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def rp(tmp_path, monkeypatch):
    mod = _load_driver()
    monkeypatch.setattr(mod, "RESULT", str(tmp_path / "result.json"))
    return mod


class TestFailClosed:
    def test_refuses_absent_calibration(self, rp, tmp_path, monkeypatch):
        monkeypatch.setattr(rp, "CALIBRATION", str(tmp_path / "nope.json"))
        assert rp.main([]) == 2
        assert json.load(open(rp.RESULT))["verdict"] == "INVALID"

    def test_refuses_red_calibration(self, rp, tmp_path, monkeypatch):
        cal = tmp_path / "cal.json"
        json.dump({"fast": False, "calibration_green": False,
                   "false_fire": {"clopper_pearson_onesided_95_upper": 0.242}}, open(cal, "w"))
        monkeypatch.setattr(rp, "CALIBRATION", str(cal))
        assert rp.main([]) == 2
        out = json.load(open(rp.RESULT))
        assert out["verdict"] == "INVALID"
        assert "RED" in out["numbers"]["gate_refusal"]

    def test_refuses_fast_calibration(self, rp, tmp_path, monkeypatch):
        cal = tmp_path / "cal.json"
        json.dump({"fast": True, "calibration_green": True}, open(cal, "w"))
        monkeypatch.setattr(rp, "CALIBRATION", str(cal))
        assert rp.main([]) == 2
        assert "fast" in json.load(open(rp.RESULT))["numbers"]["gate_refusal"]

    def test_refuses_plan_hash_mismatch(self, rp, tmp_path, monkeypatch):
        cal = tmp_path / "cal.json"
        json.dump({"fast": False, "calibration_green": True}, open(cal, "w"))
        prereg = tmp_path / "prereg.md"
        prereg.write_text("frozen text")
        bad = tmp_path / "plan_hash.txt"
        bad.write_text("0" * 64 + "  prereg.md\n")
        monkeypatch.setattr(rp, "CALIBRATION", str(cal))
        monkeypatch.setattr(rp, "PREREG", str(prereg))
        monkeypatch.setattr(rp, "PLAN_HASH", str(bad))
        assert rp.main([]) == 2
        assert "plan_hash" in json.load(open(rp.RESULT))["numbers"]["gate_refusal"]


class TestPreregIntegrity:
    def test_plan_hash_matches_prereg(self):
        want = open(os.path.join(PROBE_DIR, "plan_hash.txt")).read().split()[0]
        got = hashlib.sha256(open(os.path.join(PROBE_DIR, "prereg.md"), "rb").read()).hexdigest()
        assert want == got


class TestCommittedResult:
    @pytest.fixture(scope="class")
    def result(self):
        return json.load(open(os.path.join(PROBE_DIR, "result.json")))

    def test_verdict_allowed_and_pinned(self, result):
        assert result["verdict"] == "DATA-LIMITED"
        assert result["task_id"] == "NAME-PARALLEL-01"

    def test_pinned_numbers(self, result):
        n = result["numbers"]
        assert n["m_obs"] == 12
        assert n["n_la_pool_decodable_types"] == 501
        assert n["n_kn_names"] == 155
        assert n["augmented_bar"] == n["lfake_floor"]  # floor-dominated bar
        assert n["m_obs"] <= n["augmented_bar"]
        assert n["power"]["k_min_detectable"] > n["power"]["plausible_onomastic_band"]

    def test_s2_toponym_stratum_is_zero(self, result):
        assert result["numbers"]["strata"]["s2_toponym_excluded"]["m"] == 0

    def test_n2_shows_no_knossos_specificity(self, result):
        n2 = result["numbers"]["n2_doc_permutation"]
        assert n2["empirical_p"] >= 0.5  # pseudo-Knossos matches at least as well
