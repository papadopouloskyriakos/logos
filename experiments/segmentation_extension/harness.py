#!/usr/bin/env python3
"""harness.py — experiment-local LOSO driver + reconstructed site-clustered bootstrap.

Two jobs, both specified in PREREG.md §2/§4 and gated by §3 before any model class runs:

1. `loso_counts` replicates the leave-one-site-out fold loop of `boundary_recovery`
   (scripts/comparison/morphology.py @ 1aa1249) EXACTLY — fold order (sorted site names),
   train/test construction, and the single sequential `np.random.default_rng(seed)` whose
   draws feed the random baseline in sorted-site order — generalized ONLY to (a) accept
   arbitrary segmenter factories and (b) retain per-site tp/fp/fn (which the original
   discards and which the cluster bootstrap needs).

   Replicated QUIRK, disclosed: the original builds test folds by `ins.site or "(unknown)"`
   but train folds by `ins.site != site`, so the "(unknown)" fold's 3 inscriptions are also
   in their own training set. Reproducing 0.4361/0.3888 exactly requires keeping this; it is
   reported in the revision-queue note.

2. `site_cluster_bootstrap` reconstructs the one-off behind the published CI [0.021, 0.099]
   from its published spec (preprint App. A): resample the 52 sites WITH replacement, B=4,000
   draws; per draw, pool per-site tp/fp/fn for every entry and the random floor over the SAME
   resampled multiset (fully paired); micro-F1 per entry; gap vs a reference; percentile CI.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

from frozen_metric import (
    Inscription, SignCodec, _boundary_rate, _score_random_on, _score_segmenter_on,
)


@dataclass
class FoldCtx:
    """Everything a segmenter factory may condition on for one fold. `train` carries the
    scribe's word divisions (needed by the supervised Class-2 model and by tuning rules);
    `test` is provided for scoring only and MUST NOT be touched by factories."""
    site: str
    fold_idx: int
    train: List[Inscription]
    test: List[Inscription]
    train_utts: List[str]
    codec: SignCodec


def loso_counts(corpus: Sequence[Inscription], codec: SignCodec,
                factories: Dict[str, Callable[[FoldCtx], object]], *,
                seed: int = 0, min_site_size: int = 1,
                score_train: bool = False) -> Dict[str, object]:
    """Leave-one-site-out counts for each named segmenter + the random baseline.

    Returns {"per_site": {site: {"n_test", "train_rate", "entries": {name: counts},
    "random": counts, ("train_entries": ...)}}, "micro": {name: {...}}, "sites": [...]}.
    Counts = {tp, fp, fn, precision, recall, f1} from the frozen metric.
    """
    by_site: Dict[str, List[Inscription]] = {}
    for ins in corpus:
        by_site.setdefault(ins.site or "(unknown)", []).append(ins)
    sites = [s for s, ins in by_site.items() if len(ins) >= min_site_size]

    rng = np.random.default_rng(seed)
    per_site: Dict[str, dict] = {}

    for fold_idx, site in enumerate(sorted(sites)):
        train = [ins for ins in corpus if ins.site != site]      # quirk kept — see docstring
        test = by_site[site]
        train_utts = [codec.enc_word(ins.signs) for ins in train if len(ins.signs) >= 1]
        ctx = FoldCtx(site=site, fold_idx=fold_idx, train=train, test=test,
                      train_utts=train_utts, codec=codec)

        row: Dict[str, object] = {"n_test": len(test), "entries": {}, "train_entries": {}}
        for nm, factory in factories.items():
            seg = factory(ctx)
            row["entries"][nm] = _score_segmenter_on(test, codec, seg)
            if score_train:
                row["train_entries"][nm] = _score_segmenter_on(train, codec, seg)
        # random baseline: TRAIN-fold rate, shared sequential rng — identical construction
        train_rate = _boundary_rate(train)
        row["train_rate"] = train_rate
        row["random"] = _score_random_on(test, codec, train_rate, rng)
        per_site[site] = row

    def _micro(counts_list: List[dict]) -> dict:
        tp = sum(c["tp"] for c in counts_list)
        fp = sum(c["fp"] for c in counts_list)
        fn = sum(c["fn"] for c in counts_list)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        return {"micro_f1": round(f1, 4), "micro_precision": round(prec, 4),
                "micro_recall": round(rec, 4), "tp": tp, "fp": fp, "fn": fn}

    micro = {nm: _micro([per_site[s]["entries"][nm] for s in per_site]) for nm in factories}
    micro["random"] = _micro([per_site[s]["random"] for s in per_site])
    return {"per_site": per_site, "micro": micro, "sites": sorted(sites), "seed": seed}


# --------------------------------------------------------------------------- #
# Reconstructed site-clustered bootstrap (PREREG §4).
# --------------------------------------------------------------------------- #
def _f1_from_pooled(pooled: np.ndarray) -> np.ndarray:
    """pooled: (B, 3) columns tp/fp/fn -> micro-F1 per draw (0 where undefined)."""
    tp, fp, fn = pooled[:, 0], pooled[:, 1], pooled[:, 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        prec = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
        rec = np.where(tp + fn > 0, tp / (tp + fn), 0.0)
        f1 = np.where(prec + rec > 0, 2 * prec * rec / (prec + rec), 0.0)
    return f1


def site_cluster_bootstrap(loso: Dict[str, object], entry_names: Sequence[str], *,
                           reference: str = "random", B: int = 4000,
                           seed: int = 20260703) -> Dict[str, object]:
    """Paired site-cluster bootstrap of the micro-F1 gap (entry - reference) for each entry.

    One draw = one resample-with-replacement of the site list; ALL entries and the reference
    are pooled over the SAME resampled multiset (the published 'paired gap' spec). CIs are
    percentile: 95% ([2.5, 97.5]) and the PREREG Bonferroni family disclosure 98.33%
    ([0.8333, 99.1667], 1 - 0.05/3 for the 3 pre-registered classes).
    """
    sites = loso["sites"]
    per_site = loso["per_site"]
    S = len(sites)

    def counts_array(name: str) -> np.ndarray:
        if name == "random":
            rows = [per_site[s]["random"] for s in sites]
        else:
            rows = [per_site[s]["entries"][name] for s in sites]
        return np.array([[r["tp"], r["fp"], r["fn"]] for r in rows], dtype=float)

    arrays = {nm: counts_array(nm) for nm in set(entry_names) | {reference}}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, S, size=(B, S))

    f1 = {nm: _f1_from_pooled(arr[idx].sum(axis=1)) for nm, arr in arrays.items()}

    out: Dict[str, object] = {"B": B, "seed": seed, "n_sites": S, "reference": reference,
                              "entries": {}}
    for nm in entry_names:
        gap = f1[nm] - f1[reference]
        out["entries"][nm] = {
            "gap_mean": float(gap.mean()),
            "gap_ci95": [float(np.percentile(gap, 2.5)), float(np.percentile(gap, 97.5))],
            "gap_ci9833": [float(np.percentile(gap, 100 * 0.05 / 3 / 2)),
                           float(np.percentile(gap, 100 * (1 - 0.05 / 3 / 2)))],
            "p_gap_gt_0": float(np.mean(gap > 0)),
            "f1_ci95": [float(np.percentile(f1[nm], 2.5)), float(np.percentile(f1[nm], 97.5))],
        }
    return out


def save_json(obj: object, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)
