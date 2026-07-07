"""Source-dependency lineage-collapse (Constitution v2.0 Art. XI) — regression lock.

Proves scripts/source_dependency correctly refuses to count dependent sources as independent replication:
the shared-decipherment cluster collapses to one vote; cross-lineage agreement stays independent; unknown
sources fail loud; the shipped governance graph is self-consistent.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import source_dependency as sd  # noqa: E402


def test_graph_is_self_consistent():
    assert sd.validate() == [], "governance/source_dependency_graph.json failed self-consistency"


def test_shared_decipherment_collapses_to_one():
    """DAMOS + Ventris-Chadwick + DMic all descend from the 1952 decipherment -> ONE evidentiary vote."""
    r = sd.concordance(["SRC-DAMOS", "SRC-VC-DOCS2", "SRC-DMIC"])
    assert r["raw_n"] == 3 and r["effective_n"] == 1
    assert r["independent"] is False and r["verdict"] == "SINGLE_LINEAGE"
    assert set(r["collapsed_lineages"]) == {"L_LB_DECIPHERMENT"}


def test_structural_rules_are_cross_lineage_independent():
    """Edition-independent structural rules agreeing with a lexicon IS genuine cross-lineage evidence."""
    r = sd.concordance(["SRC-STRUCTURAL-RULES", "SRC-DMIC"])
    assert r["effective_n"] == 2 and r["independent"] is True
    assert r["verdict"] == "INDEPENDENT_REPLICATION"


def test_linear_a_corpus_collapses():
    """GORILA + SigLA + silver share the GORILA transcription -> one lineage."""
    assert sd.effective_sources(["SRC-GORILA", "SRC-SIGLA", "SRC-SILVER"]) == 1


def test_b4_mechanical_collapse_ignores_label_when_derived():
    """Salgarella has a DIFFERENT lineage label (L_SIGN_HOMOMORPHY) but derives_from GORILA with
    independence_demonstrated=false -> mechanical B4 collapses them to ONE vote (not 2)."""
    r = sd.concordance(["SRC-GORILA", "SRC-SALGARELLA-2020"])
    assert r["effective_n"] == 1 and r["independent"] is False


def test_structural_rules_stay_independent_despite_deriving_from_damos():
    """STRUCTURAL_RULES derives_from DAMOS but independence_demonstrated=true -> stays a distinct vote."""
    assert sd.effective_sources(["SRC-STRUCTURAL-RULES", "SRC-DAMOS"]) == 2


def test_egyptian_is_independent_of_aegean():
    """Cross-domain: an Egyptian edition is independent of the Aegean decipherment lineage."""
    r = sd.concordance(["SRC-EDEL-GORG-2005", "SRC-DMIC"])
    assert r["effective_n"] == 2 and r["independent"] is True


def test_partial_dependence():
    """A mix: two shared-decipherment sources + one independent -> 2 votes, PARTIALLY_DEPENDENT."""
    r = sd.concordance(["SRC-DAMOS", "SRC-DMIC", "SRC-STRUCTURAL-RULES"])
    assert r["raw_n"] == 3 and r["effective_n"] == 2 and r["verdict"] == "PARTIALLY_DEPENDENT"


def test_unknown_source_fails_loud():
    with pytest.raises(KeyError):
        sd.effective_sources(["SRC-DAMOS", "SRC-NOT-A-REAL-SOURCE"])
