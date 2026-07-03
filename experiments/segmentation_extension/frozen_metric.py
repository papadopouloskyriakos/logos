#!/usr/bin/env python3
"""frozen_metric.py — FROZEN copy-in snapshot of the segmentation metric + baseline segmenters.

Source: scripts/comparison/morphology.py @ commit 1aa12496a9d9e84f1906b1a40c4089335a51b3d1
Copied: 2026-07-03, per the operator-approved copy-in refactor (PREREG.md §2).

Every class/function below is copied VERBATIM from the source (identical grading is the whole
point; see PREREG.md §3 Gate A for the exact-reproduction check). The ONLY changes are:
  - this module lives two directories below the repo root (path bootstrap adjusted), and
  - the source's affix-panel / null-falsification machinery is NOT copied (out of scope).

DO NOT EDIT the copied bodies. New model classes live in separate modules and are scored by
these functions.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))

DEFAULT_SILVER = os.path.join(_ROOT, "corpus", "silver", "inscriptions_structured.json")

SOURCE_COMMIT = "1aa12496a9d9e84f1906b1a40c4089335a51b3d1"
SOURCE_PATH = "scripts/comparison/morphology.py"


# --------------------------------------------------------------------------- #
# The corpus record + loader
# --------------------------------------------------------------------------- #
@dataclass
class Inscription:
    """One inscription: a list of words, each a list of GORILA sign labels (the scribe's divisions)."""
    iid: str
    site: str
    words: List[List[str]]

    @property
    def signs(self) -> List[str]:
        return [s for w in self.words for s in w]


def load_corpus(path: str = DEFAULT_SILVER) -> List[Inscription]:
    """Load the structured silver (scripts/corpus_io_structured.py output). Each record's `words`
    field is the scribe's word division = the segmentation ground truth."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out: List[Inscription] = []
    for d in data:
        words = [[str(s) for s in w] for w in d.get("words", []) if w]
        if not words:
            continue
        out.append(Inscription(iid=str(d.get("id", "")), site=str(d.get("site", "")), words=words))
    return out


# --------------------------------------------------------------------------- #
# Sign <-> private-use-char codec.
# --------------------------------------------------------------------------- #
_PUA_BASE = 0xE000


class SignCodec:
    def __init__(self, signs: Sequence[str]):
        uniq = sorted(set(signs))
        if len(uniq) > 6000:                      # PUA block safety (we never approach this)
            raise ValueError("too many distinct signs for the PUA codec")
        self.to_char: Dict[str, str] = {s: chr(_PUA_BASE + i) for i, s in enumerate(uniq)}
        self.to_sign: Dict[str, str] = {c: s for s, c in self.to_char.items()}

    def enc_word(self, word: Sequence[str]) -> str:
        return "".join(self.to_char[s] for s in word if s in self.to_char)

    def dec_word(self, s: str) -> List[str]:
        return [self.to_sign[c] for c in s if c in self.to_sign]

    @classmethod
    def from_corpus(cls, corpus: Sequence[Inscription]) -> "SignCodec":
        return cls([s for ins in corpus for s in ins.signs])


# --------------------------------------------------------------------------- #
# SEGMENTERS — the published ensemble.
# --------------------------------------------------------------------------- #
class DPUnigramSegmenter:
    """Dirichlet-process unigram word segmenter (Goldwater et al. 2009), deterministic Viterbi-MAP
    variant. A word w has DP-smoothed probability  P(w) = (count[w] + alpha * P0(w)) / (N + alpha),
    with a base measure P0(w) = p_boundary * prod_char (1 - p_boundary)^(len-1) * (1/V)^len that
    penalises long / many morphs (the prior that prevents the trivial all-one-word or all-singletons
    solutions). Inference: iterate Viterbi segmentation of every utterance under the current lexicon,
    re-estimating counts (a hard-EM / MAP approximation to the Gibbs sampler — deterministic, fast)."""

    def __init__(self, alpha: float = 2.0, p_boundary: float = 0.5, max_len: int = 8,
                 iters: int = 8, seed: int = 0):
        self.alpha = float(alpha)
        self.p_boundary = float(p_boundary)
        self.max_len = int(max_len)
        self.iters = int(iters)
        self.seed = int(seed)
        self.counts: Counter = Counter()
        self.total = 0
        self.vocab = 1

    def _p0(self, w: str) -> float:
        L = len(w)
        if L <= 0:
            return 1e-12
        return self.p_boundary * ((1.0 - self.p_boundary) ** (L - 1)) * ((1.0 / self.vocab) ** L)

    def _logp_word(self, w: str) -> float:
        p = (self.counts.get(w, 0) + self.alpha * self._p0(w)) / (self.total + self.alpha)
        return float(np.log(p + 1e-300))

    def _viterbi(self, u: str) -> List[str]:
        n = len(u)
        if n == 0:
            return []
        best = [-1e300] * (n + 1)
        back = [0] * (n + 1)
        best[0] = 0.0
        for i in range(1, n + 1):
            lo = max(0, i - self.max_len)
            for j in range(lo, i):
                cand = best[j] + self._logp_word(u[j:i])
                if cand > best[i]:
                    best[i] = cand
                    back[i] = j
        # backtrace
        segs: List[str] = []
        i = n
        while i > 0:
            j = back[i]
            segs.append(u[j:i])
            i = j
        segs.reverse()
        return segs

    def fit(self, utterances: Sequence[str]) -> "DPUnigramSegmenter":
        utts = [u for u in utterances if u]
        self.vocab = max(1, len({c for u in utts for c in u}))
        # init: every utterance is one whole word (conservative under-segmentation)
        self.counts = Counter(utts)
        self.total = sum(self.counts.values())
        for _ in range(self.iters):
            new: Counter = Counter()
            for u in utts:
                for w in self._viterbi(u):
                    new[w] += 1
            if new == self.counts:
                break
            self.counts = new
            self.total = sum(self.counts.values())
        return self

    def segment(self, utterance: str) -> List[str]:
        return self._viterbi(utterance)

    def boundaries(self, utterance: str) -> List[int]:
        """Internal boundary positions (cut after index p-1, i.e. between morph[k-1] and morph[k])."""
        segs = self.segment(utterance)
        out, pos = [], 0
        for s in segs[:-1]:
            pos += len(s)
            out.append(pos)
        return out


class MorfessorSegmenter:
    """Thin wrapper over Morfessor Baseline for boundary recovery (graceful if morfessor absent)."""

    def __init__(self, seed: int = 0):
        self.seed = int(seed)
        self.model = None
        self.available = False

    def fit(self, utterances: Sequence[str]) -> "MorfessorSegmenter":
        try:
            import morfessor
            import morfessor.utils
        except Exception:
            self.available = False
            return self
        utts = [u for u in utterances if u]
        if not utts:
            self.available = False
            return self
        data = [(c, w) for w, c in Counter(utts).items()]
        model = morfessor.BaselineModel()
        model.load_data(data)
        # deterministic batch training; silence the progress bar (dots) + logging.
        # Morfessor's train_batch shuffles compounds via the stdlib `random` module, so its
        # segmentation is NOT reproducible unless we seed that module here (the wrapper's `seed`
        # was previously stored but never applied — the source of ±0.01-0.02 drift in the
        # descriptive boundary-recovery / morpheme-inventory numbers across identical re-runs).
        import logging
        import random as _random
        _random.seed(self.seed)
        logging.getLogger("morfessor").setLevel(logging.ERROR)
        morfessor.utils.show_progress_bar = False
        try:
            model.train_batch()
        except Exception:
            self.available = False
            return self
        self.model = model
        self.available = True
        return self

    def segment(self, utterance: str) -> List[str]:
        if not self.available or self.model is None or not utterance:
            return [utterance] if utterance else []
        morphs, _ = self.model.viterbi_segment(utterance)
        return list(morphs)

    def boundaries(self, utterance: str) -> List[int]:
        segs = self.segment(utterance)
        out, pos = [], 0
        for s in segs[:-1]:
            pos += len(s)
            out.append(pos)
        return out


def random_boundaries(utterance: str, rate: float, rng: np.random.Generator) -> List[int]:
    """Random-boundary baseline: each of the (len-1) internal positions is a boundary w.p. `rate`."""
    n = len(utterance)
    return [p for p in range(1, n) if rng.random() < rate]


# --------------------------------------------------------------------------- #
# WORD-BOUNDARY RECOVERY metric pieces.
# --------------------------------------------------------------------------- #
def true_boundaries(words: Sequence[Sequence[str]]) -> Tuple[str, List[int]]:
    """Return (encoded-stream-length-as-stream, true internal boundary positions). Positions are cut
    points after the cumulative sign count of each word except the last."""
    bnds, pos = [], 0
    for w in words[:-1]:
        pos += len(w)
        bnds.append(pos)
    return bnds, sum(len(w) for w in words)


def _prf(pred: set, true: set) -> Tuple[float, float, float, int, int, int]:
    tp = len(pred & true)
    fp = len(pred - true)
    fn = len(true - pred)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return prec, rec, f1, tp, fp, fn


def _boundary_rate(corpus: Sequence[Inscription]) -> float:
    """Empirical fraction of internal stream positions that are scribe word-boundaries (for the
    random baseline + as the natural under/over-segmentation reference)."""
    bnd = pos = 0
    for ins in corpus:
        n = len(ins.signs)
        if n <= 1:
            continue
        bnd += len(ins.words) - 1
        pos += n - 1
    return bnd / pos if pos else 0.0


def _score_segmenter_on(test: Sequence[Inscription], codec: SignCodec, segmenter) -> Dict[str, float]:
    tp = fp = fn = 0
    for ins in test:
        stream = codec.enc_word(ins.signs)
        if len(stream) <= 1:
            continue
        true_b, _ = true_boundaries(ins.words)
        pred_b = segmenter.boundaries(stream)
        _, _, _, a, b, c = _prf(set(pred_b), set(true_b))
        tp += a; fp += b; fn += c
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def _score_random_on(test: Sequence[Inscription], codec: SignCodec, rate: float,
                     rng: np.random.Generator) -> Dict[str, float]:
    tp = fp = fn = 0
    for ins in test:
        stream = codec.enc_word(ins.signs)
        if len(stream) <= 1:
            continue
        true_b, _ = true_boundaries(ins.words)
        pred_b = random_boundaries(stream, rate, rng)
        _, _, _, a, b, c = _prf(set(pred_b), set(true_b))
        tp += a; fp += b; fn += c
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "tp": tp, "fp": fp, "fn": fn}
