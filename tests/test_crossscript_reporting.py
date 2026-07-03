"""Regression tests for the cross-script gate's REPORTING interface (housekeeping §4).

Both one-shot runs crashed in their reporting paths, post-computation / pre-observation
(disclosed in PHASE1_REPORT.md and PHASE2_REPORT.md):
  Phase 1: numpy bool_ leaked into the JSON payload -> TypeError at json.dump;
  Phase 2: `_nn_preds`'s second return (the similarity MATRIX) was consumed as a rank ORDER
           -> empty np.where -> IndexError.
`power_precheck.nn_report` is the canonical fix; these tests pin both historical crash shapes.
Recorded artifacts and statistics are untouched by the fix (additive function only).
"""
import json
import os
import sys

import numpy as np

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
_GATE = os.path.join(_REPO_ROOT, "experiments", "crossscript_gate")
for p in (_REPO_ROOT, _GATE):
    if p not in sys.path:
        sys.path.insert(0, p)

from power_precheck import _nn_preds, nn_report  # noqa: E402


def _toy():
    rng = np.random.default_rng(7)
    n, m, d = 12, 9, 5                       # 12 "anchors", 9 candidate "values"
    U = rng.normal(size=(m, d))
    U /= np.linalg.norm(U, axis=1, keepdims=True)
    assign = np.array([i % m for i in range(n)])
    X = U[assign] + 0.1 * rng.normal(size=(n, d))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    held = np.array([1, 4, 7, 10])
    train = np.array(sorted(set(range(n)) - set(held.tolist())))
    return X, U, assign, train, held


def test_rank_lookup_never_empty_and_1_indexed():
    """Phase-2 crash shape: rank lookup must return a valid int rank for EVERY held sign."""
    X, U, assign, train, held = _toy()
    rep = nn_report(X, U, assign, train, held)
    for x in held:
        r = rep["ranks_of"][int(x)]
        assert isinstance(r, int) and 1 <= r <= U.shape[0]
    # the misuse that crashed Phase 2: matching an assignment index against SIMILARITIES
    _, S = _nn_preds(X, U, assign, train, held)
    assert np.where(S[held][0] == int(assign[held[0]]))[0].size == 0  # stays empty -> proof of
    # why nn_report (which sorts to an ORDER first) is the required path


def test_report_payload_is_json_serializable():
    """Phase-1 crash shape: a per-sign payload built from the interface must json.dump clean."""
    X, U, assign, train, held = _toy()
    rep = nn_report(X, U, assign, train, held)
    rows = [{"held": int(x),
             "pred": rep["preds"][j],
             "rank_of_true": rep["ranks_of"][int(x)],
             "hit": bool(rep["preds"][j] == int(assign[x]))}   # native bool by construction
            for j, x in enumerate(held)]
    dumped = json.dumps({"rows": rows})                        # would raise on numpy types
    assert json.loads(dumped)["rows"][0]["rank_of_true"] >= 1


def test_ranks_consistent_with_preds():
    """Top-1 prediction correct  <=>  rank of the true value == 1."""
    X, U, assign, train, held = _toy()
    rep = nn_report(X, U, assign, train, held)
    for j, x in enumerate(held):
        assert (rep["preds"][j] == int(assign[x])) == (rep["ranks_of"][int(x)] == 1)
