"""Gate-integrity regression tests (second-pass review P0.1-P0.3).

Locks the corrected §E / family-graduation semantics so the latent bugs cannot return:
  1. a family WIN is gate_verdict=='GRADUATE', never result=='match' (a REJECT/INCOMPLETE row with
     result=='match' contributes 0 to win_rate);
  2. DSR is NOT a family graduation clause (a family graduates on win-rate + verdict count even with
     a sub-0.95 / None DSR);
  3. verdict.grade fails CLOSED on an un-instrumented search (no SearchLog -> never GRADUATE, even
     when every substantive clause holds -> INCOMPLETE), and is instrumented when a SearchLog is given.
"""
import os
import sys
from unittest import mock

import pytest  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import family_scores, verdict  # noqa: E402

_VCAND = ["nwy", "brq", "mlk", "ywm", "dn", "qtl", "zkr", "bnh", "hlk", "yqr"]
_VHELD = ["nwy", "brq", "mlk", "ywm", "dn", "qtl"]
_VBASE = dict(confidence=0.6, free_params=3, provenance="embedding_nn",
              lit_index_hit=False, not_indexed_sign_support=0.9, u_floor=8, n_eff=5, n_fake=6, seed=2)


def _rows(*specs):
    # (result, gate_verdict, accuracy, confidence)
    return [(r, gv, acc, 0.6) for (r, gv, acc) in specs]


def test_family_win_is_graduate_not_match():
    """A rejected candidate whose result=='match' must contribute 0 to win_rate (P0.1)."""
    rejected = _rows(*[("match", "REJECT", 0.55)] * 6)      # 6x result=match but gate=REJECT
    sc = family_scores.scorecard("semitic", rejected, n_trials_pool=20, sr_variance=0.0)
    assert sc["win_rate"] == 0.0, sc
    assert sc["graduated"] is False

    mixed = _rows(("match", "GRADUATE", 0.6), ("match", "REJECT", 0.55),
                  ("match", "REJECT", 0.5))
    sc2 = family_scores.scorecard("semitic", mixed, n_trials_pool=20, sr_variance=0.0)
    assert sc2["win_rate"] == pytest.approx(1 / 3, abs=1e-3), sc2   # only the GRADUATE counts


def test_dsr_is_not_a_graduation_clause():
    """A family with a real GRADUATE win-rate + enough verdicts graduates even with a LOW DSR (P0.2).

    Force DSR to 0.10 (far below the old 0.95 gate); under the corrected gate the family still
    graduates on the honest primitives, proving DSR is no longer an operative clause."""
    grad = _rows(("match", "GRADUATE", 0.50), ("match", "GRADUATE", 0.55),
                 ("match", "GRADUATE", 0.60), ("match", "GRADUATE", 0.52),
                 ("match", "GRADUATE", 0.58), ("match", "GRADUATE", 0.61))  # varied -> sharpe defined
    with mock.patch.object(family_scores.logos_stats, "deflated_sharpe", return_value=0.10):
        sc = family_scores.scorecard("semitic", grad, n_trials_pool=5000, sr_variance=1.0)
    assert sc["dsr"] == 0.10                     # DSR is low (would fail an old dsr>=0.95 gate)
    assert sc["win_rate"] == 1.0
    assert sc["graduated"] is True, sc           # graduates anyway -> DSR did NOT gate it


def test_verdict_fails_closed_without_instrumented_search():
    """No SearchLog -> gate can never be GRADUATE; the instrumentation clause flips with a log (P0.3)."""
    base = dict(_VBASE, not_indexed_threshold=0.5)   # let every substantive clause be satisfiable
    g_open = verdict.grade(_VHELD, _VCAND, **base)                       # un-instrumented
    assert g_open["clauses"]["search_multiplicity_instrumented"] is False
    assert g_open["gate_verdict"] != "GRADUATE"                          # fail closed
    assert g_open["n_trials_source"] == "passed"

    class _FakeLog:      # duck-typed instrumented search (exposes .n_eff)
        n_eff = 5
    g_instr = verdict.grade(_VHELD, _VCAND, search_log=_FakeLog(), **base)
    assert g_instr["clauses"]["search_multiplicity_instrumented"] is True
    assert g_instr["n_trials_source"] == "searchlog"
