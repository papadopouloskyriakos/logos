#!/usr/bin/env python3
"""models_pyp.py — Class 1 (PREREG §5.1): Pitman–Yor-process unigram Gibbs segmenter.

The principled generalization of the frozen DP-unigram baseline (PYP discount d=0 recovers the
DP). Boundary-site Gibbs sampling after Goldwater, Griffiths & Johnson (2009), with EXACT
Chinese-restaurant table tracking (the PYP predictive needs per-type table counts, unlike the
DP), vague hyperpriors resampled by slice sampling, inverse-temperature annealing over burn-in,
and a deterministic posterior-mean Viterbi decode for grading.

Frozen by PREREG §5.1: P0 identical in form to the DP baseline (p_boundary=0.5, V = train-fold
sign vocab); d ~ Beta(1,1), alpha ~ Gamma(shape=1, scale=10), slice-resampled every 10 sweeps;
1,000 sweeps / burn-in 500 / sample every 10th post-burn-in sweep; 3 chains, chain seed
20260700 + 1000*chain_id + fold_idx; split-R-hat on the per-sweep joint log-posterior; decode
via posterior-mean sufficient statistics, Viterbi max_len=8.

Choices NOT pinned by PREREG, fixed here before any run and disclosed in the report:
  - initial state: iid random boundaries at p=0.5 (per-chain rng) — the standard Goldwater init;
  - position sweep order: sequential (utterance order, left-to-right);
  - hyperparameter init before the first slice update: d=0.5, alpha=2.0 (the DP baseline's alpha).
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

P_BOUNDARY = 0.5
MAX_LEN_DECODE = 8
SWEEPS = 1000
BURNIN = 500
SAMPLE_EVERY = 10
HYPER_EVERY = 10
N_CHAINS = 3
SEED_BASE = 20260700

D_INIT, ALPHA_INIT = 0.5, 2.0
ALPHA_PRIOR_SCALE = 10.0                      # alpha ~ Gamma(shape=1, scale=10)


def make_p0(vocab_size: int, p_boundary: float = P_BOUNDARY):
    """Base measure identical in form to the frozen DPUnigramSegmenter._p0."""
    V = max(1, vocab_size)

    def p0(w: str) -> float:
        L = len(w)
        if L <= 0:
            return 1e-12
        return p_boundary * ((1.0 - p_boundary) ** (L - 1)) * ((1.0 / V) ** L)

    return p0


class PYPRestaurant:
    """Single Pitman–Yor CRP with exact table tracking.

    tables[w] = list of table sizes for word type w; n[w] = customers of type w;
    N = total customers; T = total tables.
    """

    def __init__(self, d: float, alpha: float):
        self.d = float(d)
        self.alpha = float(alpha)
        self.tables: Dict[str, List[int]] = {}
        self.n: Counter = Counter()
        self.N = 0
        self.T = 0

    def pred(self, w: str, p0w: float) -> float:
        """PYP predictive P(next customer = w | state)."""
        tl = self.tables.get(w)
        nw = self.n[w] if tl else 0
        tw = len(tl) if tl else 0
        num = (nw - self.d * tw) + (self.alpha + self.d * self.T) * p0w
        return num / (self.N + self.alpha)

    def add(self, w: str, p0w: float, rng: np.random.Generator) -> Tuple[str, int, bool]:
        """Seat one customer of type w; returns an undo token (w, table_idx, was_new)."""
        tl = self.tables.setdefault(w, [])
        new_weight = (self.alpha + self.d * self.T) * p0w
        tot = new_weight + sum(sz - self.d for sz in tl)
        r = rng.random() * tot
        acc = 0.0
        for k, sz in enumerate(tl):
            acc += sz - self.d
            if r < acc:
                tl[k] += 1
                self.n[w] += 1
                self.N += 1
                return (w, k, False)
        tl.append(1)
        self.n[w] += 1
        self.N += 1
        self.T += 1
        return (w, len(tl) - 1, True)

    def remove(self, w: str, rng: np.random.Generator) -> None:
        """Unseat one customer of type w (table chosen with prob proportional to its size)."""
        tl = self.tables[w]
        r = rng.random() * self.n[w]
        acc = 0.0
        for k, sz in enumerate(tl):
            acc += sz
            if r < acc:
                if sz == 1:
                    tl.pop(k)
                    self.T -= 1
                    if not tl:
                        del self.tables[w]
                else:
                    tl[k] -= 1
                break
        self.n[w] -= 1
        if self.n[w] == 0:
            del self.n[w]
        self.N -= 1

    def undo_add(self, token: Tuple[str, int, bool]) -> None:
        """Revert exactly one add() (used for the provisional w1 seating in the split factor)."""
        w, k, was_new = token
        tl = self.tables[w]
        if was_new:
            tl.pop(k)
            self.T -= 1
            if not tl:
                del self.tables[w]
        else:
            tl[k] -= 1
        self.n[w] -= 1
        if self.n[w] == 0:
            del self.n[w]
        self.N -= 1

    def log_joint(self, p0, alpha: Optional[float] = None, d: Optional[float] = None) -> float:
        """EPPF log-probability of the current seating + table dishes under (alpha, d), plus the
        hyperpriors. Used for the R-hat trace and as the slice-sampling target."""
        a = self.alpha if alpha is None else float(alpha)
        dd = self.d if d is None else float(d)
        if not (0.0 <= dd < 1.0) or a <= 0.0:
            return -math.inf
        lp = 0.0
        if self.T > 1:
            lp += float(np.log(a + dd * np.arange(1, self.T)).sum())
        lp -= math.lgamma(a + self.N) - math.lgamma(a + 1.0)
        lg1d = math.lgamma(1.0 - dd)
        for w, tl in self.tables.items():
            p0w = p0(w)
            lp += len(tl) * math.log(p0w + 1e-300)
            for sz in tl:
                lp += math.lgamma(sz - dd) - lg1d
        lp += -a / ALPHA_PRIOR_SCALE - math.log(ALPHA_PRIOR_SCALE)   # Gamma(1, 10) prior on alpha
        # Beta(1,1) prior on d contributes 0
        return lp


def _slice_sample(logf, x0: float, lo: float, hi: float, rng: np.random.Generator,
                  w: float = 0.5, n_steps: int = 20) -> float:
    """Univariate slice sampler (Neal 2003) with stepping-out, bounded to (lo, hi)."""
    y = logf(x0) + math.log(rng.random() + 1e-300)
    L = max(lo, x0 - w * rng.random())
    R = min(hi, L + w)
    for _ in range(n_steps):
        if L <= lo or logf(L) < y:
            break
        L = max(lo, L - w)
    for _ in range(n_steps):
        if R >= hi or logf(R) < y:
            break
        R = min(hi, R + w)
    for _ in range(100):
        x1 = L + rng.random() * (R - L)
        if logf(x1) >= y:
            return x1
        if x1 < x0:
            L = x1
        else:
            R = x1
    return x0


def run_chain(utts: Sequence[str], vocab_size: int, seed: int, *,
              sweeps: int = SWEEPS, burnin: int = BURNIN, sample_every: int = SAMPLE_EVERY,
              fix_d_zero: bool = False, fix_hypers: bool = False) -> Dict[str, object]:
    """One Gibbs chain over the training utterances. Returns posterior-sum sufficient
    statistics (for the posterior-mean decode) + the post-burn-in log-joint trace (for R-hat)."""
    rng = np.random.default_rng(seed)
    p0 = make_p0(vocab_size)
    rest = PYPRestaurant(d=0.0 if fix_d_zero else D_INIT, alpha=ALPHA_INIT)

    # initial state: iid boundaries at p=0.5; seat the induced words
    utts = [u for u in utts if u]
    bounds: List[np.ndarray] = []
    for u in utts:
        n = len(u)
        b = np.zeros(n + 1, dtype=bool)          # b[p] True => cut before u[p]; 0/n are ends
        for p in range(1, n):
            b[p] = rng.random() < 0.5
        bounds.append(b)
        l = 0
        for p in range(1, n + 1):
            if p == n or b[p]:
                rest.add(u[l:p], p0(u[l:p]), rng)
                l = p

    sum_n: Counter = Counter()
    sum_t: Counter = Counter()
    sum_N = sum_T = sum_d = sum_alpha = 0.0
    n_samples = 0
    trace: List[float] = []

    for s in range(sweeps):
        gamma = 0.1 + 0.9 * min(1.0, s / max(1, burnin))    # anneal to 1.0 by end of burn-in
        for u, b in zip(utts, bounds):
            n = len(u)
            for p in range(1, n):
                # locate neighbours
                l = p - 1
                while l > 0 and not b[l]:
                    l -= 1
                r = p + 1
                while r < n and not b[r]:
                    r += 1
                w1, w2, w12 = u[l:p], u[p:r], u[l:r]
                if b[p]:
                    rest.remove(w1, rng)
                    rest.remove(w2, rng)
                else:
                    rest.remove(w12, rng)
                p_merge = rest.pred(w12, p0(w12))
                p_w1 = rest.pred(w1, p0(w1))
                tok = rest.add(w1, p0(w1), rng)              # provisional seat for the split factor
                p_w2 = rest.pred(w2, p0(w2))
                rest.undo_add(tok)
                p_split = p_w1 * p_w2
                a = p_split ** gamma
                m = p_merge ** gamma
                tot = a + m
                split = (rng.random() * tot < a) if tot > 0 else (rng.random() < 0.5)
                if split:
                    rest.add(w1, p0(w1), rng)
                    rest.add(w2, p0(w2), rng)
                    b[p] = True
                else:
                    rest.add(w12, p0(w12), rng)
                    b[p] = False
        if (not fix_hypers) and (s % HYPER_EVERY == HYPER_EVERY - 1):
            if not fix_d_zero:
                rest.d = _slice_sample(lambda x: rest.log_joint(p0, d=x), rest.d,
                                       0.0, 1.0 - 1e-6, rng, w=0.2)
            rest.alpha = math.exp(_slice_sample(
                lambda x: rest.log_joint(p0, alpha=math.exp(x)) + x,
                math.log(rest.alpha), math.log(1e-3), math.log(1e4), rng, w=1.0))
        if s >= burnin:
            trace.append(rest.log_joint(p0))
            if (s - burnin) % sample_every == 0:
                for w, c in rest.n.items():
                    sum_n[w] += c
                for w, tl in rest.tables.items():
                    sum_t[w] += len(tl)
                sum_N += rest.N
                sum_T += rest.T
                sum_d += rest.d
                sum_alpha += rest.alpha
                n_samples += 1

    return {"sum_n": sum_n, "sum_t": sum_t, "sum_N": sum_N, "sum_T": sum_T,
            "sum_d": sum_d, "sum_alpha": sum_alpha, "n_samples": n_samples,
            "trace": np.asarray(trace, dtype=float), "seed": seed}


def split_rhat(traces: Sequence[np.ndarray]) -> float:
    """Split-R-hat (Gelman et al.) over per-chain scalar traces (each split in half)."""
    halves = []
    for t in traces:
        h = len(t) // 2
        if h < 2:
            return float("nan")
        halves.append(t[:h])
        halves.append(t[h:2 * h])
    x = np.asarray(halves, dtype=float)
    m, n = x.shape
    means = x.mean(axis=1)
    variances = x.var(axis=1, ddof=1)
    W = variances.mean()
    B = n * means.var(ddof=1)
    if W <= 0:
        return float("nan")
    var_hat = (n - 1) / n * W + B / n
    return float(np.sqrt(var_hat / W))


class PYPPosteriorMeanDecoder:
    """Deterministic Viterbi decode under the PYP predictive with posterior-mean sufficient
    statistics (PREREG §5.1); interface-compatible with the frozen metric (.boundaries)."""

    def __init__(self, chains: Sequence[Dict[str, object]], vocab_size: int,
                 max_len: int = MAX_LEN_DECODE):
        S = sum(c["n_samples"] for c in chains)
        self.mean_n: Dict[str, float] = Counter()
        self.mean_t: Dict[str, float] = Counter()
        for c in chains:
            for w, v in c["sum_n"].items():
                self.mean_n[w] += v
            for w, v in c["sum_t"].items():
                self.mean_t[w] += v
        self.mean_n = {w: v / S for w, v in self.mean_n.items()}
        self.mean_t = {w: v / S for w, v in self.mean_t.items()}
        self.N = sum(c["sum_N"] for c in chains) / S
        self.T = sum(c["sum_T"] for c in chains) / S
        self.d = sum(c["sum_d"] for c in chains) / S
        self.alpha = sum(c["sum_alpha"] for c in chains) / S
        self.p0 = make_p0(vocab_size)
        self.max_len = int(max_len)

    def _logp_word(self, w: str) -> float:
        num = (self.mean_n.get(w, 0.0) - self.d * self.mean_t.get(w, 0.0)
               + (self.alpha + self.d * self.T) * self.p0(w))
        return float(np.log(max(num, 0.0) / (self.N + self.alpha) + 1e-300))

    def segment(self, u: str) -> List[str]:
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
        segs: List[str] = []
        i = n
        while i > 0:
            j = back[i]
            segs.append(u[j:i])
            i = j
        segs.reverse()
        return segs

    def boundaries(self, u: str) -> List[int]:
        segs = self.segment(u)
        out, pos = [], 0
        for s in segs[:-1]:
            pos += len(s)
            out.append(pos)
        return out


def fit_fold(train_utts: Sequence[str], fold_idx: int, *,
             sweeps: int = SWEEPS, burnin: int = BURNIN,
             chain_results: Optional[List[Dict[str, object]]] = None) -> Dict[str, object]:
    """Run the 3 pre-registered chains for one fold (or accept precomputed chain results),
    combine into the posterior-mean decoder, and report convergence."""
    vocab = max(1, len({c for u in train_utts for c in u}))
    if chain_results is None:
        chain_results = [run_chain(train_utts, vocab,
                                   SEED_BASE + 1000 * chain_id + fold_idx,
                                   sweeps=sweeps, burnin=burnin)
                         for chain_id in (1, 2, 3)]
    dec = PYPPosteriorMeanDecoder(chain_results, vocab)
    rhat = split_rhat([c["trace"] for c in chain_results])
    return {"decoder": dec, "rhat": rhat,
            "post_mean": {"d": dec.d, "alpha": dec.alpha, "N": dec.N, "T": dec.T},
            "chain_seeds": [c["seed"] for c in chain_results]}
