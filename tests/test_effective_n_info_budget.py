"""Art. VIII effective_n + Art. IX information-budget panel — regression lock."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import effective_n as en  # noqa: E402
from scripts import info_budget as ib  # noqa: E402


# ---- Art. VIII effective_n ----

ITEMS = [
    {"id": "a", "lexical_family": "F1", "site": "KN", "document_id": "D1"},
    {"id": "b", "lexical_family": "F1", "site": "KN", "document_id": "D1"},
    {"id": "c", "lexical_family": "F2", "site": "KN", "document_id": "D2"},
    {"id": "d", "lexical_family": "F3", "site": "PY", "document_id": "D3"},
]


def test_effective_n_bottleneck_is_min_dimension():
    r = en.effective_n(ITEMS, ["lexical_family", "site", "document_id"])
    assert r["raw_n"] == 4
    assert r["by_dim"] == {"lexical_family": 3, "site": 2, "document_id": 3}
    assert r["effective_n"] == 2 and r["bottleneck_dim"] == "site"   # site is the tightest constraint


def test_effective_n_folds_source_lineage():
    """Two shared-decipherment sources collapse to ONE lineage in the effective_n (Art. XI)."""
    items = [{"id": "a", "lexical_family": "F1", "source_id": "SRC-DAMOS"},
             {"id": "b", "lexical_family": "F2", "source_id": "SRC-DMIC"}]
    r = en.effective_n(items, ["lexical_family"])
    assert r["by_dim"]["lexical_family"] == 2
    assert r["by_dim"]["source_lineage"] == 1        # DAMOS + DMic = one L_LB_DECIPHERMENT vote
    assert r["effective_n"] == 1                     # the source-lineage bottleneck dominates


def test_dependency_components_union_find():
    # a,b share F1 -> one component; c (F2) and d (F3) separate -> 3 components
    assert en.dependency_components(ITEMS, ["lexical_family"]) == 3
    # sharing site KN links a,b,c -> {a,b,c},{d} = 2
    assert en.dependency_components(ITEMS, ["site"]) == 2


def test_unknown_source_fails_loud():
    with pytest.raises(KeyError):
        en.effective_n([{"id": "x", "site": "KN", "source_id": "SRC-FAKE"}], ["site"])


# ---- Art. IX information-budget panel ----

def test_panel_has_all_13_fields_missing_are_unknown():
    p = ib.build_panel(raw_corpus_size=100)
    assert len(p) == 13
    assert p["raw_corpus_size"] == 100
    assert p["parameter_count"] == ib.UNKNOWN


def test_build_panel_rejects_non_fields():
    with pytest.raises(KeyError):
        ib.build_panel(not_a_field=1)


def test_underdetermined_when_params_exceed_evidence():
    p = ib.build_panel(parameter_count=57, effective_independent_evidence=19)
    assert ib.underdetermined(p) is True
    p2 = ib.build_panel(parameter_count=5, effective_independent_evidence=40)
    assert ib.underdetermined(p2) is False
    assert ib.underdetermined(ib.build_panel(parameter_count=5)) is None   # evidence UNKNOWN


def test_b7_scope():
    assert ib.requires_panel("L4", None) is True
    assert ib.requires_panel("L1", None) is False
    assert ib.requires_panel(None, "SUPPORTED") is True
    assert ib.requires_panel("L0", "EXPLORATORY") is False


def test_certify_fails_closed_on_unknown_and_underdetermination():
    # L1 observation is exempt
    assert ib.certify(ib.build_panel(), "L1", None)["certified"] is True
    # graduating claim missing load-bearing fields -> not certified
    c = ib.certify(ib.build_panel(raw_corpus_size=100), "L3", "SUPPORTED")
    assert c["certified"] is False and any("UNKNOWN" in r for r in c["reasons"])
    # graduating claim, all present but underdetermined -> not certified
    p = ib.build_panel(effective_independent_evidence=19, parameter_count=57,
                       minimum_detectable_effect=0.92, estimated_power=0.0)
    c2 = ib.certify(p, "L4", "SUPPORTED")
    assert c2["certified"] is False and c2["underdetermined"] is True
    # all present, not underdetermined -> certified
    p2 = ib.build_panel(effective_independent_evidence=400, parameter_count=8,
                        minimum_detectable_effect=0.05, estimated_power=0.9)
    assert ib.certify(p2, "L2", "SUPPORTED")["certified"] is True
