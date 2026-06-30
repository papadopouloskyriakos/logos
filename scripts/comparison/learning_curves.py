#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""learning_curves.py — PSEUDO-DECIPHERMENT LEARNING CURVES (information-sufficiency capstone).

This module REPLACES the withdrawn unicity-distance claim
(docs/findings/2026-06-30-information-floor.md, retracted by the expert red-team). It answers the
sharpened question the unicity claim could not:

    "Is a Linear-A-SCALE corpus large enough to recover a decipherment,
     IF a known cognate language existed?"

by DOWNSAMPLING a KNOWN-ANSWER decipherment task (a published cognate benchmark whose answer is
known) to Linear-A scale and below, and measuring how held-out cognate-ID recovery degrades as the
corpus shrinks. The shape of accuracy-vs-size — and whether the curve is still ABOVE the random-map
chance floor at Linear-A scale — is the result.

==================================================================================================
HONESTY-CRITICAL FRAMING (this is an UPPER BOUND — read before using any number)
==================================================================================================
Every benchmark here is a pair of languages with a KNOWN cognate relationship (Linear B / Greek,
Ugaritic / Hebrew, Phoenician / Ugaritic, Luwian / Hittite, Cypriot / Greek). The recovery
algorithm (Tamburini 2025 CSA_OptMatcher) is handed a real, dense cognate signal. **Linear A has
NO known cognate language.** Therefore:

    For any corpus size, known-answer recovery accuracy is a STRICT UPPER BOUND on Linear A's real
    recoverability at that size. Linear A is *at best* this good and almost certainly much worse
    (the cognate target itself is missing — Luo 2019's limit; see the information-floor finding).

Two honest readings of the curve, and ONLY these two:
  (1) If the upper-bound curve is ALREADY AT THE CHANCE FLOOR at Linear-A scale, then Linear A is
      DEFINITIVELY below the information-sufficiency threshold: even granting it a perfect cognate
      language, the corpus is too small. This is a genuine, publishable null (the insurance policy).
  (2) If the upper-bound curve is still WELL ABOVE chance at Linear-A scale, then size is NOT the
      blocker — the blocker is cognate-absence. This does NOT say Linear A is decipherable; it says
      the obstruction is the missing target, not the byte budget, and relocates the bet to
      "manufacture a cognate-like target" (cross-script transfer), not "find more tablets".

NO phonetic claim is made anywhere in this module. It never imports scripts/verdict.py and produces
no verdict row; it is a corpus-capacity diagnostic, not a decipherment.

==================================================================================================
METHOD
==================================================================================================
1. DOWNSAMPLE  (downsample / size_sweep): for each target size — a sweep of cognate-pair counts from
   the full benchmark down to and BELOW Linear-A scale (fractions {1.0,0.75,0.5,0.3,0.2,0.1} PLUS
   absolute anchors at the Linear-A distinct-word count ~600-700 and below {650,600,400,200,100}) —
   draw a SEEDED random subset of the cognate pairs. Optionally re-weight the draw to match Linear
   A's word-LENGTH distribution (mean ~2.3 signs/word). Site/genre FRAGMENTATION is NOT matched
   (the .cog benchmarks carry no site metadata) — this makes the curve an EVEN MORE optimistic upper
   bound, because real Linear A is split across many small sites/genres, which only hurts recovery.

2. RECOVERY  (recover_*): run the VALIDATED Tamburini 2025 CSA_OptMatcher cognate-ID recovery on each
   downsampled benchmark -> Luo-et-al-2019 cognate-ID accuracy. The full coupled-annealing search is
   expensive (CUDA-grade), so the step budget is parameterized (--steps); reduced-budget runs are
   LOWER BOUNDS on accuracy (under-converged), and are flagged as such. The SHAPE of accuracy-vs-size
   is the deliverable, not any single point. A fast torch-free STUB recovery is provided for the
   build/tests; the real CSA sweep runs on a rented H100 (see compute_placement, below).

3. CHANCE FLOOR  (chance_floor): at each size, the accuracy a RANDOM cognate-ID sign-map achieves,
   measured two ways — (a) analytic 1/n_known (expected accuracy of a uniformly random injective
   lexicon matching) and (b) empirical: R seeded random sign-maps scored by the SAME Luo metric
   (the Packard-style permutation floor; see nulls.py). As the corpus shrinks the candidate pool
   shrinks, so the chance floor RISES — a small corpus is EASIER to match by chance, which is exactly
   why a high match-rate on a tiny corpus is not evidence (the §B multiplicity discipline).

4. LINEAR-A LOCATOR  (linear_a_locator): mark Linear-A scale (~650 distinct word-forms; V=92; ~5792
   sign-tokens) on the size axis and report whether known-answer recovery there is ABOVE chance
   (size is sufficient in principle) or AT FLOOR (below the sufficiency threshold). This is the
   headline number that replaces the withdrawn unicity claim.

5. main(argv) emits a JSON report: per-benchmark accuracy-vs-size curve, the chance floor per size,
   the Linear-A locator + verdict, and the UPPER-BOUND honesty statement.

==================================================================================================
compute_placement
==================================================================================================
EXPENSIVE part -> RENT AN H100 (CUDA): the CSA SWEEP — (benchmarks) x (sizes ~11) x (seeds >=4) x
   full annealing (Tamburini's 100000 steps, 16 coupled annealers). On CPU a single Ugaritic energy
   eval is ~19 s and full annealing is hours/seed; the whole sweep is days. Tamburini's energy
   (EditDistanceWild) is CUDA-capable, so the sweep belongs on a rented H100 (saves hours-to-days).
   Drive it with: this module's downsample -> write_cog -> scripts/baselines/run_tamburini.py per
   subset, with --steps 100000 (or a checkpointed budget) and >=4 seeds.
LOCAL part -> this build + tests: downsampling, the chance floor, the Linear-A locator, the report
   assembly, and a torch-free STUB recovery for smoke-testing the harness. No GPU, no full CSA. Per
   the operator rule: the sweep -> H100; the build/tests -> local.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

# --- robust import: work both as `python3 scripts/comparison/learning_curves.py`
#     and as `python3 -m scripts.comparison.learning_curves` / under pytest. ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir, os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison.lexstat import edit_distance, normalized_edit_distance  # noqa: E402

# NOTE: scripts.verdict is DELIBERATELY never imported here (invariant 1/4; this is a corpus
# diagnostic, not a verdict path). A test asserts the import is absent.

CITATION = (
    "Pseudo-decipherment learning curves (information-sufficiency capstone). Recovery: Tamburini "
    "2025, CSA_OptMatcher (Frontiers in AI 8:1581129). Chance floor: Packard 1974 permutation null "
    "(see nulls.py). Replaces the withdrawn unicity-distance finding "
    "(docs/findings/2026-06-30-information-floor.md)."
)

# --------------------------------------------------------------------------- #
# Linear-A scale anchor (corpus_io_structured.py + the information-floor finding)
# --------------------------------------------------------------------------- #
LINEAR_A = {
    "n_sign_tokens": 5792,        # syllable-sign tokens parsed from lineara.xyz transliterations
    "V_syllabic": 92,             # clean syllabic inventory (logograms/numerals excluded)
    "distinct_words_lo": 600,     # distinct word-forms (lower)
    "distinct_words_hi": 700,     # distinct word-forms (upper)
    "distinct_words": 650,        # midpoint locator on the size axis
    "mean_signs_per_word": 2.3,
}

# The single honest framing string, attached to every report.
UPPER_BOUND_STATEMENT = (
    "UPPER BOUND. Every benchmark here is a KNOWN cognate-language pair; the recovery algorithm is "
    "handed a real cognate signal. Linear A has NO known cognate language, so its real recoverability "
    "at any corpus size is STRICTLY WORSE than these curves. Read only two ways: (1) if the curve is "
    "AT the chance floor at Linear-A scale, Linear A is DEFINITIVELY below the information-sufficiency "
    "threshold (even a perfect cognate would not save it); (2) if the curve is ABOVE chance at "
    "Linear-A scale, size is not the blocker — cognate-absence is — and this is NOT a decipherability "
    "claim. Site/genre fragmentation is NOT matched, making the bound even more generous. No phonetic "
    "claim is made."
)

# Default size sweep: fractions of the full benchmark + absolute Linear-A-scale anchors and below.
DEFAULT_FRACTIONS: Tuple[float, ...] = (1.0, 0.75, 0.5, 0.3, 0.2, 0.1)
DEFAULT_ABSOLUTE: Tuple[int, ...] = (650, 600, 400, 200, 100)
MIN_SIZE = 20  # below this a benchmark is too small to mean anything


# =========================================================================== #
# 1. .cog parsing + benchmark statistics
# =========================================================================== #
@dataclass
class Benchmark:
    """A parsed cognate benchmark. ``rows`` preserves file order; each row is a raw
    (lost, known) pair of strings where ``_`` marks 'no cognate on this side' and ``|``
    separates alternative forms within a word-group (Tamburini .cog format)."""
    lost_label: str
    known_label: str
    rows: List[Tuple[str, str]]

    @property
    def gold_rows(self) -> List[Tuple[str, str]]:
        return [(a, b) for (a, b) in self.rows if a != "_" and b != "_"]

    @property
    def n_gold(self) -> int:
        return len(self.gold_rows)


def parse_cog(path: str) -> Benchmark:
    """Parse a Tamburini .cog file. First line = alphabet labels; remaining lines = (lost, known).

    Uses whitespace tokenization to exactly mirror his ReadLexicon (forms never contain spaces;
    columns are tab-separated). Lines without two columns are skipped."""
    rows: List[Tuple[str, str]] = []
    lost_label = known_label = ""
    with open(path, "r", encoding="utf-8") as f:
        first = True
        for line in f:
            parts = line.split()
            if first:
                if len(parts) >= 2:
                    lost_label, known_label = parts[0], parts[1]
                first = False
                continue
            if len(parts) >= 2:
                rows.append((parts[0], parts[1]))
    return Benchmark(lost_label, known_label, rows)


def _first_alt(group: str) -> str:
    """First alternative form of a ``|``-separated word-group."""
    return group.split("|")[0]


def _signs(form: str) -> List[str]:
    """Tokenize a form into signs the way run_tamburini drives CSA (sep="" -> per-codepoint)."""
    return list(form)


def benchmark_stats(bench: Benchmark) -> Dict[str, float]:
    """Corpus-scale stats on a (sub)benchmark, on the axes Linear-A is located by."""
    gold = bench.gold_rows
    lost_groups = [a for (a, _b) in bench.rows if a != "_"]
    known_groups = [b for (_a, b) in bench.rows if b != "_"]
    lost_inventory = set()
    known_inventory = set()
    sign_tokens = 0
    word_lengths: List[int] = []
    for g in lost_groups:
        f = _first_alt(g)
        s = _signs(f)
        lost_inventory.update(s)
        sign_tokens += len(s)
        word_lengths.append(len(s))
    for g in known_groups:
        known_inventory.update(_signs(_first_alt(g)))
    return {
        "n_gold_pairs": len(gold),
        "n_lost_groups": len(lost_groups),
        "n_known_groups": len(known_groups),
        "V_lost": len(lost_inventory),
        "V_known": len(known_inventory),
        "n_sign_tokens_lost": sign_tokens,
        "mean_signs_per_word": (float(np.mean(word_lengths)) if word_lengths else 0.0),
    }


def length_histogram(groups: Sequence[str]) -> Dict[int, float]:
    """Normalized lost-word-length (in signs) distribution of a set of word-groups."""
    lens = [len(_signs(_first_alt(g))) for g in groups if g != "_"]
    if not lens:
        return {}
    c: Dict[int, int] = {}
    for L in lens:
        c[L] = c.get(L, 0) + 1
    n = float(len(lens))
    return {L: v / n for L, v in c.items()}


# =========================================================================== #
# 2. DOWNSAMPLE
# =========================================================================== #
def size_sweep(n_full: int,
               fractions: Sequence[float] = DEFAULT_FRACTIONS,
               absolute: Sequence[int] = DEFAULT_ABSOLUTE,
               min_size: int = MIN_SIZE) -> List[int]:
    """Build the sorted, de-duplicated list of target gold-pair counts to sweep.

    Combines fraction-of-full points with the absolute Linear-A-scale anchors; clamps to
    [min_size, n_full]; drops anything above the full size (cannot upsample)."""
    pts = set()
    for fr in fractions:
        pts.add(int(round(fr * n_full)))
    for a in absolute:
        pts.add(int(a))
    out = sorted(p for p in pts if min_size <= p <= n_full)
    return out


def _length_match_weights(gold_rows: Sequence[Tuple[str, str]],
                          target: Dict[float, float]) -> np.ndarray:
    """Importance weights that shift the sampled lost-word-LENGTH histogram toward ``target``.

    weight(row) = target_p[len] / empirical_p[len]; rows whose length is absent from the target get
    a tiny weight (so they are deprioritized, not impossible). Normalized to sum 1."""
    emp = length_histogram([a for (a, _b) in gold_rows])
    w = np.empty(len(gold_rows), dtype=float)
    for i, (a, _b) in enumerate(gold_rows):
        L = len(_signs(_first_alt(a)))
        ep = emp.get(L, 1e-9)
        tp = float(target.get(L, 0.0))
        w[i] = (tp / ep) if ep > 0 else 0.0
    if w.sum() <= 0:
        w = np.ones(len(gold_rows), dtype=float)
    # keep every row drawable (tiny epsilon floor) so a size-N sample without replacement never
    # fails when some lengths fall outside the target's support; the shaping still dominates.
    w = w + 1e-12
    return w / w.sum()


def _linear_a_length_target(max_len: int = 8) -> Dict[float, float]:
    """A Linear-A-like word-length target distribution (mean ~2.3 signs/word).

    Geometric-ish mass on lengths 1..max_len with the mean pinned near the Linear A figure. This is
    a stand-in shape (the true LA per-length histogram is not co-registered with these benchmarks);
    it is used only to demonstrate length-matched downsampling, and is reported as such."""
    mean = LINEAR_A["mean_signs_per_word"]
    # geometric on k>=1 with mean m: p = 1/m_shifted; here approximate via decaying weights.
    lengths = list(range(1, max_len + 1))
    # choose decay r so that sum(k * r^{k-1}) / sum(r^{k-1}) ~= mean; small grid search.
    best_r, best_err = 0.5, 1e9
    for r in [x / 100.0 for x in range(5, 96)]:
        wts = np.array([r ** (k - 1) for k in lengths], dtype=float)
        wts /= wts.sum()
        m = float(np.sum(np.array(lengths) * wts))
        if abs(m - mean) < best_err:
            best_err, best_r = abs(m - mean), r
    wts = np.array([best_r ** (k - 1) for k in lengths], dtype=float)
    wts /= wts.sum()
    return {float(k): float(w) for k, w in zip(lengths, wts)}


def downsample(bench: Benchmark, size: int, seed: int,
               length_match: bool = False,
               keep_distractors: bool = True) -> Benchmark:
    """Draw a SEEDED random subset of ``size`` gold cognate pairs (deterministic per seed).

    - ``size`` gold pairs are drawn WITHOUT replacement. With ``length_match`` the draw is weighted
      toward Linear-A-like lost-word lengths (mean ~2.3 signs/word) via importance weights.
    - ``keep_distractors`` keeps a proportional, seeded subset of the non-cognate (``_``) rows so the
      lexicon-noise ratio is preserved; the syllabic benchmarks (LB/Greek, CS/Greek) have none.
    Output row order is sorted by original index for stable, reproducible files."""
    gold = bench.gold_rows
    distract = [(a, b) for (a, b) in bench.rows if a == "_" or b == "_"]
    size = max(0, min(int(size), len(gold)))
    rng = np.random.default_rng(seed)

    if length_match and gold:
        weights = _length_match_weights(gold, _linear_a_length_target())
        idx = rng.choice(len(gold), size=size, replace=False, p=weights)
    else:
        idx = rng.choice(len(gold), size=size, replace=False) if gold else np.array([], dtype=int)
    idx = sorted(int(i) for i in idx)
    sub_gold = [gold[i] for i in idx]

    sub_distract: List[Tuple[str, str]] = []
    if keep_distractors and distract:
        frac = (size / len(gold)) if gold else 0.0
        n_keep = int(round(frac * len(distract)))
        if n_keep > 0:
            didx = sorted(int(i) for i in rng.choice(len(distract), size=n_keep, replace=False))
            sub_distract = [distract[i] for i in didx]

    return Benchmark(bench.lost_label, bench.known_label, sub_gold + sub_distract)


def write_cog(bench: Benchmark, out_path: str) -> str:
    """Write a (sub)benchmark back to .cog so run_tamburini/CSA can consume it directly."""
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"{bench.lost_label}\t{bench.known_label}\n")
        for a, b in bench.rows:
            f.write(f"{a}\t{b}\n")
    return out_path


# =========================================================================== #
# 3. The torch-free Luo scorer (engine for the chance floor AND the test stub)
# =========================================================================== #
def _apply_map(lost_form: str, sign_map: Dict[str, str]) -> str:
    """Map a lost word to a predicted known string by concatenating per-sign images (a sign with no
    image is dropped, matching CSA's -1 'delete' assignment)."""
    return "".join(sign_map.get(s, "") for s in _signs(lost_form))


def luo_accuracy(gold_pairs: Sequence[Tuple[str, str]], sign_map: Dict[str, str],
                 seed: int = 0) -> float:
    """Luo-et-al-2019 cognate-ID accuracy under a given sign map (Tamburini's metric, torch-free).

    Each gold pair is row i; lost_i is mapped through ``sign_map`` and matched to the known lexicon
    by minimum-normalized-edit-distance Hungarian assignment (his lsa step). Accuracy = fraction of
    rows assigned to their own known partner. This is the engine used for the chance floor (random
    maps) and the build/test stub recovery (an inferred map) — the SAME metric the real CSA optimizes,
    so the floor and the stub are scored identically to the real run.

    TIE-BREAK HONESTY: when the sign map carries no information the cost matrix is (near-)constant and
    every assignment is optimal; ``linear_sum_assignment`` would then degenerately return the IDENTITY,
    spuriously reading as 100% correct. We therefore present the columns in a SEEDED random order
    before assignment (and translate back), so a tied/uninformative matching scores ~1/n — its honest
    chance value — while a genuinely-optimal unique matching is invariant to the relabelling."""
    n = len(gold_pairs)
    if n == 0:
        return 0.0
    from scipy.optimize import linear_sum_assignment
    lost = [_first_alt(a) for (a, _b) in gold_pairs]
    known = [_first_alt(b) for (_a, b) in gold_pairs]
    mapped = [_apply_map(w, sign_map) for w in lost]
    perm = np.random.default_rng(seed).permutation(n)          # seeded column order (tie-break)
    cost = np.empty((n, n), dtype=float)
    for i in range(n):
        mi = mapped[i]
        for jj in range(n):
            cost[i, jj] = normalized_edit_distance(mi, known[perm[jj]])
    row_ind, col_ind = linear_sum_assignment(cost)
    col_orig = perm[col_ind]                                    # back to original known indices
    hits = int(np.sum(row_ind == col_orig))
    return hits / n


def _inventories(gold_pairs: Sequence[Tuple[str, str]]) -> Tuple[List[str], List[str]]:
    lost_inv, known_inv = set(), set()
    for a, b in gold_pairs:
        lost_inv.update(_signs(_first_alt(a)))
        known_inv.update(_signs(_first_alt(b)))
    return sorted(lost_inv), sorted(known_inv)


def random_sign_map(lost_inv: Sequence[str], known_inv: Sequence[str],
                    rng: np.random.Generator) -> Dict[str, str]:
    """A random cognate-ID map: each lost sign -> a uniformly random known sign."""
    if not known_inv:
        return {}
    ks = list(known_inv)
    return {s: ks[int(rng.integers(0, len(ks)))] for s in lost_inv}


# =========================================================================== #
# 4. CHANCE FLOOR
# =========================================================================== #
def chance_floor(gold_pairs: Sequence[Tuple[str, str]],
                 n_maps: int = 50, seed: int = 0,
                 empirical: bool = True) -> Dict[str, float]:
    """The accuracy a RANDOM cognate-ID map achieves at this size — the floor each curve point is
    measured against.

    Two measures:
      - ``analytic`` = 1 / n_known_groups: expected accuracy of a uniformly random injective lexicon
        matching (each lost word equally likely to be matched to any of the n_known known words).
        Rises as the corpus shrinks (fewer candidates -> easier to hit by chance).
      - ``empirical_*`` (if ``empirical``): ``n_maps`` seeded random sign-maps scored by ``luo_accuracy``
        — the Packard-style permutation floor; captures the extra structure a random map gets from
        word-length/edit-distance alone, so it is >= the analytic floor and is the CONSERVATIVE bar.
    """
    n = len(gold_pairs)
    n_known = len({_first_alt(b) for (_a, b) in gold_pairs}) or 1
    out: Dict[str, float] = {
        "analytic": 1.0 / n_known,
        "n_known_groups": float(n_known),
        "n_pairs": float(n),
    }
    if not empirical or n == 0:
        out.update({"empirical_mean": out["analytic"], "empirical_std": 0.0,
                    "empirical_p95": out["analytic"], "n_maps": 0})
        return out
    lost_inv, known_inv = _inventories(gold_pairs)
    rng = np.random.default_rng(seed + 777)
    accs = np.array([
        luo_accuracy(gold_pairs, random_sign_map(lost_inv, known_inv, rng), seed=seed + 333 + m)
        for m in range(n_maps)
    ], dtype=float)
    out.update({
        "empirical_mean": float(np.mean(accs)),
        "empirical_std": float(np.std(accs)),
        "empirical_p95": float(np.percentile(accs, 95)),
        "n_maps": int(n_maps),
    })
    return out


def above_chance(acc: Optional[float], floor: Dict[str, float], k_sigma: float = 3.0,
                 min_margin: float = 0.05) -> Optional[bool]:
    """Is a recovery accuracy meaningfully above the empirical random-map floor?

    Requires BOTH a k-sigma separation from the random-map distribution AND an absolute margin (so a
    tiny-but-significant gap on a large benchmark does not read as 'recoverable'). None if no
    recovery was run."""
    if acc is None:
        return None
    mu = floor.get("empirical_mean", floor["analytic"])
    sd = floor.get("empirical_std", 0.0)
    bar = max(mu + k_sigma * sd, mu + min_margin, floor["analytic"] + min_margin)
    return bool(acc >= bar)


# =========================================================================== #
# 5. RECOVERY — stub (local/tests) and CSA (H100)
# =========================================================================== #
def stub_recover(gold_pairs: Sequence[Tuple[str, str]], seed: int = 0,
                 min_votes: int = 1) -> float:
    """A FAST, torch-free recovery PROXY for the build/tests ONLY — NOT the real CSA.

    Infers a sign map by POSITION VOTING over the gold alignment (each lost sign votes for the known
    sign at the same position in same-length pairs), keeps a sign only if it has at least
    ``min_votes`` attestations (a sign too rarely seen cannot be reliably mapped — the data-hunger
    that makes a small corpus UNDERDETERMINED), assigns each kept lost sign its argmax image, then
    scores that map with ``luo_accuracy`` (the same metric as the floor and the real CSA). Because it
    uses the gold alignment it is SUPERVISED — it stands in for 'a competent recovery algorithm' to
    exercise the curve-building harness; it is not a substitute for the unsupervised CSA whose numbers
    are the real result. With ``min_votes`` > 1, sign coverage (hence accuracy) rises with corpus
    size and collapses toward the chance floor when the corpus is too small to attest the inventory —
    which is the very phenomenon the learning curve must surface.
    """
    n = len(gold_pairs)
    if n == 0:
        return 0.0
    votes: Dict[str, Dict[str, int]] = {}
    for a, b in gold_pairs:
        ls, ks = _signs(_first_alt(a)), _signs(_first_alt(b))
        if len(ls) != len(ks):
            continue
        for sl, sk in zip(ls, ks):
            votes.setdefault(sl, {})[sk] = votes.setdefault(sl, {}).get(sk, 0) + 1
    sign_map: Dict[str, str] = {}
    for sl, d in votes.items():
        if sum(d.values()) < min_votes:
            continue  # too few attestations -> sign stays unmapped (underdetermined)
        sign_map[sl] = max(sorted(d), key=lambda k: d[k])  # sorted -> deterministic tie-break
    return luo_accuracy(gold_pairs, sign_map, seed=seed)


def csa_recover(cog_path: str, N: int, M: int, penf: float,
                steps: int = 1000, seed: int = 0, processes: int = 8) -> Dict[str, object]:
    """Run the REAL Tamburini 2025 CSA_OptMatcher recovery on a (downsampled) .cog file.

    Delegates to scripts/baselines/run_tamburini (lazy import — pulls torch). Returns the wrapper's
    result dict (acc/found/total/energy/wall_s). ``steps`` < 100000 is UNDER-CONVERGED: the returned
    accuracy is a LOWER BOUND. This is the H100 path; never called by the tests."""
    from scripts.baselines import run_tamburini as rt  # lazy: imports torch
    module = rt._load_vendor_module()
    key = f"_lc_{os.path.basename(cog_path)}"
    rt.BENCHMARKS[key] = dict(cog=os.path.abspath(cog_path), N=N, M=M, penf=penf,
                              published_csa=float("nan"), published_neuro=None)
    try:
        res = rt.run_one(module, key, seed, steps, processes)
    finally:
        rt.BENCHMARKS.pop(key, None)
    res["under_converged"] = steps < 100000
    return res


# =========================================================================== #
# 6. Build a learning curve for one benchmark
# =========================================================================== #
def _recovery_fn(kind, csa_cfg: Optional[Dict[str, object]], steps: int, tmp_dir: str
                 ) -> Callable[[Benchmark, int], Tuple[Optional[float], bool]]:
    """Resolve a recovery callable: (sub_benchmark, seed) -> (accuracy or None, is_lower_bound).

    ``kind`` may also be a user-supplied callable fn(sub_benchmark, seed) -> float (accuracy) or
    -> (accuracy, is_lower_bound); the build/tests use this to inject a data-hungry stub."""
    if callable(kind):
        def _wrap(sub: Benchmark, seed: int) -> Tuple[Optional[float], bool]:
            r = kind(sub, seed)
            if isinstance(r, tuple):
                return (None if r[0] is None else float(r[0]), bool(r[1]))
            return (None if r is None else float(r), False)
        return _wrap
    if kind == "none":
        return lambda sub, seed: (None, False)
    if kind == "stub":
        return lambda sub, seed: (stub_recover(sub.gold_rows, seed=seed), False)
    if kind == "csa":
        if not csa_cfg:
            raise ValueError("csa recovery requires csa_cfg=dict(N=,M=,penf=)")

        def _run(sub: Benchmark, seed: int) -> Tuple[Optional[float], bool]:
            path = os.path.join(tmp_dir, f"sub_{sub.n_gold}_{seed}.cog")
            write_cog(sub, path)
            res = csa_recover(path, int(csa_cfg["N"]), int(csa_cfg["M"]),
                              float(csa_cfg["penf"]), steps=steps, seed=seed)
            acc = res.get("acc")
            return (float(acc) if acc is not None else None, bool(res.get("under_converged")))
        return _run
    raise ValueError(f"unknown recovery kind: {kind}")


def build_curve(bench: Benchmark,
                sizes: Optional[Sequence[int]] = None,
                seeds: Sequence[int] = (0, 1, 2, 3),
                recovery: str = "stub",
                steps: int = 1000,
                n_floor_maps: int = 50,
                length_match: bool = False,
                csa_cfg: Optional[Dict[str, object]] = None,
                tmp_dir: Optional[str] = None) -> List[Dict[str, object]]:
    """Accuracy-vs-size curve for one benchmark: per size, mean+/-std recovery over seeds and the
    chance floor. Recovery is 'none' | 'stub' | 'csa' (see compute_placement)."""
    if sizes is None:
        sizes = size_sweep(bench.n_gold)
    tmp_dir = tmp_dir or os.path.join(_REPO_ROOT, "runtime", "learning_curves")
    rec = _recovery_fn(recovery, csa_cfg, steps, tmp_dir)

    curve: List[Dict[str, object]] = []
    for size in sizes:
        accs: List[float] = []
        lower_bound = False
        floor_acc: List[Dict[str, float]] = []
        stats_acc: List[Dict[str, float]] = []
        for seed in seeds:
            sub = downsample(bench, size, seed=seed, length_match=length_match)
            gp = sub.gold_rows
            a, lb = rec(sub, seed)
            if a is not None:
                accs.append(a)
            lower_bound = lower_bound or lb
            floor_acc.append(chance_floor(gp, n_maps=n_floor_maps, seed=seed,
                                          empirical=(n_floor_maps > 0)))
            stats_acc.append(benchmark_stats(sub))
        # aggregate the chance floor + stats across seeds (means)
        def _mean_key(dicts, key):
            vals = [d[key] for d in dicts if key in d]
            return float(np.mean(vals)) if vals else None
        floor = {k: _mean_key(floor_acc, k) for k in floor_acc[0]} if floor_acc else {}
        stats = {k: _mean_key(stats_acc, k) for k in stats_acc[0]} if stats_acc else {}
        point = {
            "size": int(size),
            "n_known_groups": stats.get("n_known_groups"),
            "V_lost": stats.get("V_lost"),
            "V_known": stats.get("V_known"),
            "n_sign_tokens_lost": stats.get("n_sign_tokens_lost"),
            "mean_signs_per_word": stats.get("mean_signs_per_word"),
            "recovery_mean": (float(np.mean(accs)) if accs else None),
            "recovery_std": (float(np.std(accs)) if len(accs) > 1 else 0.0 if accs else None),
            "recovery_is_lower_bound": bool(lower_bound),
            "chance_analytic": floor.get("analytic"),
            "chance_empirical_mean": floor.get("empirical_mean"),
            "chance_empirical_std": floor.get("empirical_std"),
            "chance_empirical_p95": floor.get("empirical_p95"),
            "above_chance": above_chance(
                (float(np.mean(accs)) if accs else None), floor) if floor else None,
        }
        curve.append(point)
    return curve


# =========================================================================== #
# 7. LINEAR-A LOCATOR
# =========================================================================== #
def _interp(curve: List[Dict[str, object]], x: float, key: str) -> Optional[float]:
    """Linear-interpolate ``key`` vs ``size`` at x; clamp to the curve's endpoints."""
    pts = [(p["size"], p[key]) for p in curve if p.get(key) is not None]
    if not pts:
        return None
    pts.sort()
    if x <= pts[0][0]:
        return float(pts[0][1])
    if x >= pts[-1][0]:
        return float(pts[-1][1])
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0) if x1 != x0 else 0.0
            return float(y0 + t * (y1 - y0))
    return float(pts[-1][1])


def linear_a_locator(curve: List[Dict[str, object]],
                     la_words: int = LINEAR_A["distinct_words"]) -> Dict[str, object]:
    """Place Linear-A scale on the size axis and read off the verdict.

    Interpolates recovery accuracy + the chance floor at ``la_words`` distinct word-forms (the LA
    scale). Verdict:
      - PENDING_CSA_SWEEP : no recovery was run (stub/none) — locate only.
      - ABOVE_CHANCE      : known-answer recovery clears the random-map floor at LA scale -> size is
                            sufficient IN PRINCIPLE (for a KNOWN cognate; UPPER BOUND).
      - AT_FLOOR          : recovery == chance at LA scale -> below the sufficiency threshold; if even
                            this upper bound is at floor, Linear A is definitively below it. ONLY
                            emitted from a FULLY-CONVERGED recovery (see AT_FLOOR_LOWER_BOUND).
      - AT_FLOOR_LOWER_BOUND : recovery is at floor BUT was under-converged (recovery_is_lower_bound),
                            so a fuller CSA budget could lift it above floor -> NOT a definitive
                            sufficiency verdict; re-run at full convergence before reading it.
    Also flags whether LA scale is INSIDE the benchmark's swept range or an EXTRAPOLATION."""
    sizes = sorted(p["size"] for p in curve)
    in_range = bool(sizes) and (sizes[0] <= la_words <= sizes[-1])
    acc = _interp(curve, la_words, "recovery_mean")
    ch_emp = _interp(curve, la_words, "chance_empirical_mean")
    ch_ana = _interp(curve, la_words, "chance_analytic")
    floor = {"empirical_mean": ch_emp if ch_emp is not None else (ch_ana or 0.0),
             "empirical_std": _interp(curve, la_words, "chance_empirical_std") or 0.0,
             "analytic": ch_ana or 0.0}
    ab = above_chance(acc, floor)
    # HIGH-defect guard: an under-converged CSA run yields a LOWER BOUND on accuracy, so an at-floor
    # reading from it is NOT definitive — more annealing budget could lift it above the floor. Only
    # ABOVE_CHANCE is safe from a lower bound (true acc >= measured >= floor). Interpolate the
    # lower-bound flag (True->1.0) at LA scale; any contamination downgrades a would-be AT_FLOOR to a
    # non-definitive AT_FLOOR_LOWER_BOUND. Never claim "Linear A is below sufficiency" off a lower bound.
    lb_at_la = (_interp(curve, la_words, "recovery_is_lower_bound") or 0.0) > 0.0
    if acc is None:
        verdict = "PENDING_CSA_SWEEP"
    elif ab:
        verdict = "ABOVE_CHANCE"
    elif lb_at_la:
        verdict = "AT_FLOOR_LOWER_BOUND"
    else:
        verdict = "AT_FLOOR"
    if verdict == "PENDING_CSA_SWEEP":
        reading = ("Locator placed; run the CSA sweep on an H100 to fill recovery accuracy (see "
                   "compute_placement). " + UPPER_BOUND_STATEMENT)
    elif verdict == "AT_FLOOR_LOWER_BOUND":
        reading = ("At floor, but the recovery is a LOWER BOUND (under-converged CSA) — NOT a "
                   "definitive sufficiency verdict; re-run at full annealing budget before reading "
                   "it. " + UPPER_BOUND_STATEMENT)
    else:
        reading = UPPER_BOUND_STATEMENT
    return {
        "la_distinct_words": int(la_words),
        "la_scale_in_swept_range": in_range,
        "interp_recovery_acc": acc,
        "interp_chance_empirical": floor["empirical_mean"],
        "interp_chance_analytic": floor["analytic"],
        "above_chance": ab,
        "recovery_is_lower_bound": lb_at_la,
        "verdict": verdict,
        "reading": reading,
    }


# =========================================================================== #
# 8. main + JSON report
# =========================================================================== #
# Registry of the known-answer benchmarks (cog filename + CSA N/M/penf per Tamburini 2025 §3.3).
# linear-b-greek is the PRIMARY Linear-A analog: a syllabary -> a known language, exactly Linear A's
# situation but WITH a known cognate. Counts (n_gold) are computed at runtime, not hand-written.
_DATA_DIR = os.path.join(_REPO_ROOT, "corpus", "bronze", "code", "CSA_OptMatcher", "data")
KNOWN_ANSWER_BENCHMARKS = {
    "linearb-greek":       dict(cog="linear_b-greek.cog",   N=2, M=1, penf=4.0, syllabic=True),
    "cypriot-greek":       dict(cog="csyl-greek.cog",       N=2, M=1, penf=4.0, syllabic=True),
    "ugaritic-noiseless":  dict(cog="uga-heb.no_speNL.cog", N=1, M=2, penf=4.0, syllabic=False),
    "phoenician-ugaritic": dict(cog="StarlingDB_Ph-Ug.cog", N=2, M=1, penf=4.0, syllabic=False),
    "luvian-hittite":      dict(cog="RWT2002_Luv-Hit.cog",  N=2, M=1, penf=4.0, syllabic=False),
}


def build_report(benchmarks: Sequence[str],
                 recovery: str = "none",
                 seeds: Sequence[int] = (0, 1, 2, 3),
                 steps: int = 1000,
                 n_floor_maps: int = 50,
                 length_match: bool = False,
                 data_dir: str = _DATA_DIR) -> Dict[str, object]:
    """Assemble the full JSON report across benchmarks."""
    report: Dict[str, object] = {
        "kind": "pseudo_decipherment_learning_curves",
        "citation": CITATION,
        "honest_framing": UPPER_BOUND_STATEMENT,
        "no_phonetic_claim": True,
        "linear_a_scale": LINEAR_A,
        "recovery_method": recovery,
        "recovery_steps": steps if recovery == "csa" else None,
        "compute_placement": (
            "EXPENSIVE CSA sweep (benchmarks x ~11 sizes x >=4 seeds x full annealing) -> rent an "
            "H100 (CUDA EditDistanceWild; CPU is days). LOCAL: downsample + chance floor + locator + "
            "report + stub. Operator rule: sweep -> H100; build/tests -> local."),
        "benchmarks": {},
    }
    for key in benchmarks:
        cfg = KNOWN_ANSWER_BENCHMARKS[key]
        path = os.path.join(data_dir, cfg["cog"])
        if not os.path.isfile(path):
            report["benchmarks"][key] = {"error": f"cog not found: {path} (corpus is gitignored)"}
            continue
        bench = parse_cog(path)
        sizes = size_sweep(bench.n_gold)
        curve = build_curve(
            bench, sizes=sizes, seeds=seeds, recovery=recovery, steps=steps,
            n_floor_maps=n_floor_maps, length_match=length_match,
            csa_cfg=(dict(N=cfg["N"], M=cfg["M"], penf=cfg["penf"]) if recovery == "csa" else None))
        locator = linear_a_locator(curve)
        report["benchmarks"][key] = {
            "syllabic_analog": bool(cfg["syllabic"]),
            "is_primary_linear_a_analog": key == "linearb-greek",
            "full_n_gold": bench.n_gold,
            "full_above_linear_a_scale": bench.n_gold >= LINEAR_A["distinct_words"],
            "sizes_swept": sizes,
            "curve": curve,
            "linear_a_locator": locator,
        }
    # headline = the primary syllabic analog if present
    primary = "linearb-greek" if "linearb-greek" in benchmarks else (benchmarks[0] if benchmarks else None)
    if primary and "linear_a_locator" in report["benchmarks"].get(primary, {}):
        report["headline"] = {
            "primary_benchmark": primary,
            "linear_a_locator": report["benchmarks"][primary]["linear_a_locator"],
            "note": (
                "Headline = the syllabary->known-language analog (Linear B -> Greek): the closest "
                "structural match to Linear A's situation, but WITH a known cognate. Its verdict is "
                "the UPPER BOUND for Linear A at the same scale."),
        }
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    import json
    p = argparse.ArgumentParser(
        description="Pseudo-decipherment learning curves (information-sufficiency capstone).")
    p.add_argument("--benchmarks", nargs="*", default=list(KNOWN_ANSWER_BENCHMARKS),
                   choices=list(KNOWN_ANSWER_BENCHMARKS),
                   help="known-answer benchmarks to sweep (default: all)")
    p.add_argument("--recovery", choices=["none", "stub", "csa"], default="none",
                   help="none=locate+floor only (cheap); stub=fast torch-free proxy (build/tests); "
                        "csa=real Tamburini CSA (H100). default: none")
    p.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3])
    p.add_argument("--steps", type=int, default=1000,
                   help="CSA step budget (his GPU artifact: 100000). <100000 = LOWER BOUND.")
    p.add_argument("--floor-maps", type=int, default=50,
                   help="random sign-maps for the empirical chance floor (0 = analytic only)")
    p.add_argument("--length-match", action="store_true",
                   help="re-weight the downsample toward Linear-A word lengths (mean ~2.3 signs/word)")
    p.add_argument("--out", default=None, help="write JSON report to this path")
    args = p.parse_args(argv)

    report = build_report(
        args.benchmarks, recovery=args.recovery, seeds=tuple(args.seeds),
        steps=args.steps, n_floor_maps=args.floor_maps, length_match=args.length_match)

    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
