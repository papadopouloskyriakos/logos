"""Program-level search receipt (Art. VII) — regression lock."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.search_receipt import SearchReceipt  # noqa: E402


def test_multiplicity_counts_distinct_configs_across_partitions():
    r = SearchReceipt()
    r.log("exploratory", {"model_family": "nb", "feature_family": "signs"})
    r.log("cross_model_search", {"model_family": "nc", "feature_family": "signs"})
    r.log("exploratory", {"model_family": "nb", "feature_family": "signs"})   # duplicate config
    assert r.n_trials() == 3
    assert r.multiplicity_n() == 2                     # two DISTINCT configs
    assert r.partition_counts()["exploratory"] == 2


def test_confirmatory_without_prereg_is_a_violation():
    r = SearchReceipt()
    r.log("confirmatory", {"threshold": 0.5}, "gate")
    assert r.validate(), "confirmatory trial without prereg must be flagged (Art. II)"
    r2 = SearchReceipt()
    r2.log("confirmatory", {"threshold": 0.5}, "gate", prereg="plan_hash:abc")
    assert r2.validate() == []


def test_rejects_bad_partition_and_dimension():
    r = SearchReceipt()
    with pytest.raises(ValueError):
        r.log("not_a_partition", {})
    with pytest.raises(KeyError):
        r.log("exploratory", {"not_a_dimension": 1})


def test_dimensions_used():
    r = SearchReceipt()
    r.log("exploratory", {"model_family": "nb", "seed": 1})
    r.log("exploratory", {"model_family": "nc", "seed": 2})
    assert r.dimensions_used() == {"model_family": 2, "seed": 2}
