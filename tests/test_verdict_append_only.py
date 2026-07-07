"""Append-only verdict ledger (Constitution v2.0 Art. XVII) — regression lock.

Proves scripts/verdict.write_verdict:
  1. inserts a single current row on first grade;
  2. is a NO-OP on identical replay (content-addressed via verdict_hash — invariant 6);
  3. APPENDS a superseding row on a changed re-grade, flips the prior to status='superseded' (setting
     only its lifecycle pointer — never the graded content), and writes one correction_ledger row;
  4. never issues DELETE or ON DUPLICATE KEY UPDATE (the pre-v2.0 in-place-overwrite anti-pattern).

Runs without a live DB via a minimal in-memory FakeCursor that pattern-matches verdict.py's SQL and
raises on any unexpected statement — so a regression to the overwrite path fails loudly.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import verdict  # noqa: E402


def _g(result="match", gate_verdict="GRADUATE", accuracy=0.62):
    """A grade dict with every key write_verdict / verdict_content_hash / _notes read."""
    return {"result": result, "gate_verdict": gate_verdict, "gate_version": "gate-e2",
            "accuracy": accuracy, "brier": 0.12, "dsr": 0.5, "dsr_order": 0.4,
            "s_morph_powered": False, "u_floor": 8.0, "free_params": 3, "order_stat_bar": 0.4,
            "lfake_bar": 0.3, "failing_clauses": [],
            "clauses": {"generalizes_to_not_indexed": True}}


class FakeCursor:
    """Emulates just enough of verdicts + correction_ledger for write_verdict. Raises on any SQL it
    does not recognise — so a stray DELETE / ON DUPLICATE / UPDATE-of-content regression fails."""

    def __init__(self):
        self.verdicts = []
        self.ledger = []
        self._id = 0
        self.lastrowid = None
        self._fetch = []

    def execute(self, sql, args=()):
        s = " ".join(sql.split())
        assert not any(f in s.upper() for f in ("ON DUPLICATE KEY", "DELETE FROM")), \
            f"forbidden in-place/overwrite SQL: {s[:80]}"
        if s.startswith("SELECT id, verdict_hash, status, gate_verdict, result FROM verdicts"):
            ph = args[0]
            self._fetch = [(r["id"], r["verdict_hash"], r["status"], r["gate_verdict"], r["result"])
                           for r in self.verdicts if r["plan_hash"] == ph]
        elif s.startswith("UPDATE verdicts SET status='superseded'"):
            rid = args[0]
            for r in self.verdicts:
                if r["id"] == rid and r["status"] == "current":
                    r["status"] = "superseded"
                    r["current_key"] = None
        elif s.startswith("INSERT INTO verdicts"):
            (ph, result, current_key, gv, gver, clauses, held, acc, brier, notes, prov, vh,
             sup_id, ctype, creason) = args
            self._id += 1
            self.verdicts.append({"id": self._id, "plan_hash": ph, "result": result, "status": "current",
                                  "current_key": current_key, "gate_verdict": gv, "accuracy": acc,
                                  "verdict_hash": vh, "supersedes_id": sup_id, "superseded_by_id": None,
                                  "correction_type": ctype, "correction_reason": creason})
            self.lastrowid = self._id
        elif s.startswith("UPDATE verdicts SET superseded_by_id"):
            new_id, rid = args
            for r in self.verdicts:
                if r["id"] == rid:
                    r["superseded_by_id"] = new_id
        elif s.startswith("INSERT INTO correction_ledger"):
            self.ledger.append(args)
        else:
            raise AssertionError("unexpected SQL: " + s[:80])

    def fetchall(self):
        return self._fetch


def test_first_grade_inserts_one_current():
    cur = FakeCursor()
    verdict.write_verdict(cur, "ph1", "semitic", _g())
    assert len(cur.verdicts) == 1
    row = cur.verdicts[0]
    assert row["status"] == "current" and row["verdict_hash"] and row["supersedes_id"] is None
    assert cur.ledger == []


def test_identical_replay_is_noop():
    cur = FakeCursor()
    verdict.write_verdict(cur, "ph1", "semitic", _g())
    verdict.write_verdict(cur, "ph1", "semitic", _g())          # byte-identical grade
    assert len(cur.verdicts) == 1, "idempotent replay must not append"
    assert cur.ledger == []


def test_changed_regrade_appends_and_supersedes():
    cur = FakeCursor()
    verdict.write_verdict(cur, "ph1", "semitic", _g(result="match", gate_verdict="GRADUATE"))
    verdict.write_verdict(cur, "ph1", "semitic", _g(result="deviation", gate_verdict="REJECT"))
    assert len(cur.verdicts) == 2, "a changed re-grade must APPEND, not overwrite"
    old = next(r for r in cur.verdicts if r["id"] == 1)
    new = next(r for r in cur.verdicts if r["id"] == 2)
    # prior preserved, only lifecycle pointers touched
    assert old["status"] == "superseded" and old["superseded_by_id"] == 2
    assert old["result"] == "match" and old["gate_verdict"] == "GRADUATE", "prior content must be immutable"
    # successor is the single current row, pointing back
    assert new["status"] == "current" and new["supersedes_id"] == 1
    assert new["result"] == "deviation" and new["correction_type"] == "SUPERSEDING_ANALYSIS"
    # exactly one ledger row recording the supersession
    assert len(cur.ledger) == 1
    ref, ctype, orig_status, cur_status, superseded_by, reason, artifact = cur.ledger[0]
    assert ref == "ph1" and ctype == "SUPERSEDING_ANALYSIS"
    assert orig_status == "GRADUATE" and cur_status == "REJECT" and superseded_by == new["verdict_hash"]


def test_content_hash_sensitivity():
    h = verdict.verdict_content_hash("ph1", _g(accuracy=0.62))
    assert h == verdict.verdict_content_hash("ph1", _g(accuracy=0.62))     # deterministic
    assert h != verdict.verdict_content_hash("ph1", _g(accuracy=0.71))     # changed score -> new hash
    assert h != verdict.verdict_content_hash("ph2", _g(accuracy=0.62))     # different hypothesis
