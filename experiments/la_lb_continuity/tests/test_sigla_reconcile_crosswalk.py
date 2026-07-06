"""Integration tests for the crosswalk. Skip if the (gitignored, main-repo) inputs are absent, so the
suite is structurally green without licensed data; run fully when the data is present locally."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "sigla_reconcile"))
import config  # noqa: E402
import reconcile as R  # noqa: E402

_have = all(os.path.exists(p) for p in config.INPUTS.values())
pytestmark = pytest.mark.skipif(not _have, reason="licensed inputs (SigLA/silver) not present in this checkout")


@pytest.fixture(scope="module")
def summary():
    s, _ = R.reconcile()
    return s


def test_partition_sums(summary):
    c = summary["counts"]
    assert c["matched"] + c["only_sigla"] == c["sigla_docs"]
    assert c["matched"] + c["only_silver"] == c["silver_records"]


def test_expected_scale(summary):
    c = summary["counts"]
    assert c["sigla_docs"] == 802 and c["sigla_signs"] == 376
    assert c["silver_records"] == 1341
    assert c["matched"] > 500          # substantial overlap exists


def test_inputs_referenced_not_copied():
    # inputs must live OUTSIDE this worktree (referenced read-only), never committed here
    wt = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    for p in config.INPUTS.values():
        assert not os.path.abspath(p).startswith(wt), f"input {p} is inside the worktree (must be referenced from main)"


def test_learned_ab_map_reproduces_known_syllabary(summary):
    # firewalled AID: if the decode/crosswalk were wrong this would not reproduce the LB grid
    t = summary["learned_ab_value_aid"]["table"]
    for ab, val in {"AB81": "KU", "AB80": "MA", "AB53": "RI", "AB57": "JA", "AB77": "KA"}.items():
        assert t.get(ab) == val


def test_determinism(summary):
    s2, _ = R.reconcile()
    assert s2["counts"] == summary["counts"]
    assert s2["segmentation_delta"] == summary["segmentation_delta"]
