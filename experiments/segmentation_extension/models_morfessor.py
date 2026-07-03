#!/usr/bin/env python3
"""models_morfessor.py — Class 3 (PREREG §5.3): Morfessor Baseline with tuned corpusweight.

Bounds whether vanilla Morfessor's published over-segmentation (micro-F1 0.156) is inherent or
a prior artifact. Tuning is TEST-BLIND and deterministic: corpusweight grid
{0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0}; per fold, select the weight whose predicted boundary
rate on the TRAIN streams is closest to the TRAIN-fold scribal boundary rate (ties -> first in
grid order). Training mirrors the frozen wrapper (token counts, stdlib random seeded); seed
20260703.
"""
from __future__ import annotations

from collections import Counter
from typing import List, Sequence

GRID = (0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0)
SEED = 20260703


class TunedMorfessorSegmenter:
    def __init__(self, train_utts: Sequence[str], target_rate: float, seed: int = SEED):
        import logging
        import random as _random
        import morfessor
        import morfessor.utils
        logging.getLogger("morfessor").setLevel(logging.ERROR)
        morfessor.utils.show_progress_bar = False

        utts = [u for u in train_utts if u]
        data = [(c, w) for w, c in Counter(utts).items()]

        best = None                              # (abs diff, grid idx, model, weight, rate)
        for gi, weight in enumerate(GRID):
            _random.seed(seed)                   # per-fit, as the frozen wrapper seeds per fit
            model = morfessor.BaselineModel(corpusweight=weight)
            model.load_data(data)
            try:
                model.train_batch()
            except Exception:
                continue
            bnd = pos = 0
            for u in utts:
                if len(u) <= 1:
                    continue
                morphs, _ = model.viterbi_segment(u)
                bnd += len(morphs) - 1
                pos += len(u) - 1
            rate = bnd / pos if pos else 0.0
            diff = abs(rate - target_rate)
            if best is None or diff < best[0] - 1e-12:
                best = (diff, gi, model, weight, rate)
        if best is None:
            raise RuntimeError("no morfessor fit succeeded")
        self.model = best[2]
        self.corpusweight = best[3]
        self.train_rate = best[4]
        self.target_rate = target_rate

    def segment(self, utterance: str) -> List[str]:
        if not utterance:
            return []
        morphs, _ = self.model.viterbi_segment(utterance)
        return list(morphs)

    def boundaries(self, utterance: str) -> List[int]:
        segs = self.segment(utterance)
        out, pos = [], 0
        for s in segs[:-1]:
            pos += len(s)
            out.append(pos)
        return out
