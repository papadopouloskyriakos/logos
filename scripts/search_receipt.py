#!/usr/bin/env python3
"""Program-level search receipt (Constitution v2.0/2.1 Art. VII).

Every searched configuration increases the chance of accidental success. `scripts/comparison/searchlog.py`
counts trials for ONE machine scanner (sign-assignment x lexeme x segmentation); THIS aggregates the whole
ADAPTIVE discovery process — candidate languages, feature families, MODEL families, alignment methods,
thresholds, seeds, restarts, subgroups, exclusions, post-hoc decisions, failed branches — partitioned into
the four search types, and produces the multiplicity trial count `N` that feeds the Deflated-Sharpe /
order-statistic deflation in `scripts/logos_stats.py`. "The entire adaptive discovery process — not merely
the final model — must be represented under the null." Deterministic; no DB.

CLI:
    python3 scripts/search_receipt.py   # demo
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

PARTITIONS = ("preregistered_within_model", "cross_model_search", "exploratory", "confirmatory")

DIMENSIONS = ("hypothesis", "candidate_language", "sign_assignment", "root_or_lexeme", "feature_family",
              "model_family", "alignment_method", "threshold", "seed", "restart", "subgroup", "exclusion",
              "post_hoc_decision", "failed_branch")


class SearchReceipt:
    """Append-only log of every evaluated configuration across the adaptive search."""

    def __init__(self, name=""):
        self.name = name
        self.trials = []

    def log(self, partition, config=None, label="", prereg=None, outcome=None):
        """Record one evaluated configuration. `config` maps Art. VII dimensions -> values. A confirmatory
        trial MUST cite a preregistration (`prereg`) — enforced by validate() (Art. II fail-closed)."""
        if partition not in PARTITIONS:
            raise ValueError(f"partition must be one of {PARTITIONS}, got {partition!r}")
        config = config or {}
        bad = [k for k in config if k not in DIMENSIONS]
        if bad:
            raise KeyError(f"not Art. VII search dimensions: {bad}")
        self.trials.append({"partition": partition, "config": config, "label": label,
                            "prereg": prereg, "outcome": outcome})
        return self

    def _sig(self, t):
        return json.dumps(t["config"], sort_keys=True)

    def n_trials(self, partition=None):
        return sum(1 for t in self.trials if partition is None or t["partition"] == partition)

    def multiplicity_n(self):
        """The honest trial count for multiplicity deflation: the number of DISTINCT evaluated
        configurations across ALL partitions (every one was a chance at accidental success — the garden of
        forking paths). Feed this as N to logos_stats deflation / dsr_trial_count."""
        return len({self._sig(t) for t in self.trials})

    def partition_counts(self):
        return {p: self.n_trials(p) for p in PARTITIONS}

    def dimensions_used(self):
        used = {}
        for t in self.trials:
            for k, v in t["config"].items():
                used.setdefault(k, set()).add(json.dumps(v, sort_keys=True))
        return {k: len(v) for k, v in sorted(used.items())}

    def validate(self):
        """Discipline checks (Art. II/VII). Returns a list of violations (empty = OK)."""
        problems = []
        for i, t in enumerate(self.trials):
            if t["partition"] == "confirmatory" and not t["prereg"]:
                problems.append(f"trial {i} ({t['label']}) is confirmatory but cites no preregistration (Art. II)")
        return problems

    def to_dict(self):
        return {"name": self.name, "n_trials_total": self.n_trials(),
                "multiplicity_n": self.multiplicity_n(), "partition_counts": self.partition_counts(),
                "dimensions_used": self.dimensions_used(), "violations": self.validate(),
                "note": "multiplicity_n feeds logos_stats deflation (Art. VII); confirmatory trials must cite a prereg."}

    def save(self, path):
        with open(path, "w") as f:
            json.dump({**self.to_dict(), "trials": self.trials}, f, indent=1)


def _demo():
    r = SearchReceipt("demo")
    r.log("exploratory", {"model_family": "naive_bayes", "feature_family": "sign_bag"}, "exp1")
    r.log("cross_model_search", {"model_family": "nearest_centroid", "feature_family": "sign_bag"}, "exp2")
    r.log("confirmatory", {"model_family": "naive_bayes", "threshold": 0.5}, "gate", prereg="plan_hash:2eab15")
    print(json.dumps(r.to_dict(), indent=1))


if __name__ == "__main__":
    _demo()
