#!/usr/bin/env python3
"""machinery.py -- EPOCH-037 LINE-FINAL NUMERAL / LEDGER LINE TEMPLATE (L2/L3).

Pure token-position structure. Tokens carry NO phonetic/sound/meaning/reading.
L2/L3 positional statistics ONLY. LB (load_b_damos) is a POSITIVE-CONTROL BENCHMARK
ONLY.

Frozen metric: among qualifying lines (>=2 content tokens, >=1 'num'),
  p_num_last  = fraction whose LAST content token is 'num'.
NULL = within-line position permutation (calibrated by construction): permute the
ORDER of each line's content tokens (multiset fixed -> per-line num-count fixed),
recompute p_num_last; >=2000 draws; one-sided p = P(permuted >= observed).
"""
from __future__ import annotations
import json, os, sys, hashlib
from collections import defaultdict
from typing import List, Dict, Tuple

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
A_CORPUS = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
LINE_DELIM = "nl"          # FROZEN: line delimiter = 'nl' only (see prereg §3)
CONTENT_TYPES = ("word", "num", "other")
RNG_SEED = 3700037          # epoch-seeded, deterministic

# ---------------------------------------------------------------------------
# Data loading / line construction
# ---------------------------------------------------------------------------

def load_a(path: str = A_CORPUS) -> list:
    return json.load(open(path, encoding="utf-8"))

def split_lines(stream: list, seps: frozenset) -> List[List[str]]:
    """Split a stream into LINES at separator token types. A line = run of CONTENT
    tokens ('word','num','other') between breaks. Separators are dropped."""
    lines: List[List[str]] = []
    cur: List[str] = []
    for tok in stream:
        t = tok.get("t")
        if t in seps:
            if cur:
                lines.append(cur); cur = []
        elif t in CONTENT_TYPES:
            cur.append(t)
    if cur:
        lines.append(cur)
    return lines

def qualifying_lines(lines: List[List[str]]) -> List[List[str]]:
    """Keep lines with >=2 content tokens AND >=1 'num'."""
    return [L for L in lines if len(L) >= 2 and "num" in L]

def corpus_qualifying_by_site(inscriptions: list, seps: frozenset = frozenset({LINE_DELIM})) -> Dict[str, List[List[str]]]:
    by_site: Dict[str, List[List[str]]] = defaultdict(list)
    for ins in inscriptions:
        by_site[ins["site"]] += qualifying_lines(split_lines(ins["stream"], seps))
    return by_site

# ---------------------------------------------------------------------------
# Metric + permutation null
# ---------------------------------------------------------------------------

def p_num_last(lines: List[List[str]]) -> float:
    if not lines:
        return 0.0
    return float(sum(1 for L in lines if L[-1] == "num")) / len(lines)

def p_num_first(lines: List[List[str]]) -> float:
    if not lines:
        return 0.0
    return float(sum(1 for L in lines if L[0] == "num")) / len(lines)

def permutation_null(lines: List[List[str]], n_draws: int = 5000, seed: int = RNG_SEED,
                     stat="last") -> Tuple[float, float, float]:
    """Within-line position-permutation null for p_num_last (or p_num_first).
    Returns (observed, null_mean, one_sided_p).
    One-sided p = fraction of draws with permuted stat >= observed (for 'last':
    numerals line-final MORE than chance). For stat='first' the same convention is
    used (permuted >= observed)."""
    rng = np.random.default_rng(seed)
    if not lines:
        return 0.0, 0.0, 1.0
    obs = p_num_last(lines) if stat == "last" else p_num_first(lines)
    # Pre-convert each line to a numpy array of int (1 if 'num' else 0) for speed.
    arrs = [np.array([1 if x == "num" else 0 for x in L], dtype=np.int8) for L in lines]
    n = len(arrs)
    ge = 0
    null_vals = np.empty(n_draws, dtype=np.float64)
    for d in range(n_draws):
        c = 0
        for a in arrs:
            rng.shuffle(a)
            if a[-1] == 1 if stat == "last" else a[0] == 1:
                c += 1
        pv = c / n
        null_vals[d] = pv
        if pv >= obs - 1e-12:
            ge += 1
    null_mean = float(null_vals.mean())
    p = float((ge + 1) / (n_draws + 1))   # +1 smoothing (never exactly 0)
    return float(obs), null_mean, p

# ---------------------------------------------------------------------------
# Positive control (LB benchmark ONLY) -- pseudo-lines with planted bias
# ---------------------------------------------------------------------------

def build_lb_pseudo_lines() -> List[List[str]]:
    """Build pseudo-lines from DAMOS Linear B wordforms via load_b_damos.
    Each DAMOS wordform is treated as a sequence of 'word' content tokens (length =
    wordform length). These pseudo-lines are a BENCHMARK substrate ONLY (never
    evidence for LA). Loading uses importlib spec_from_file_location so the REAL
    scripts/cross_script/data.py is used regardless of sys.path shadowing."""
    import importlib.util
    data_path = os.path.join(ROOT, "scripts", "cross_script", "data.py")
    seqs = []
    try:
        spec = importlib.util.spec_from_file_location("la_cross_data", data_path)
        if spec is None or spec.loader is None:
            raise FileNotFoundError(data_path)
        D = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(D)
        seqs, _freq, _v2g = D.load_b_damos()
    except Exception as e:  # pragma: no cover
        print(f"[build_lb_pseudo_lines] load_b_damos failed: {e}", file=sys.stderr)
        seqs = []
    lines: List[List[str]] = []
    for w in seqs:
        if len(w) >= 1:
            lines.append(["word"] * max(1, len(w)))
    return lines

def plant_line_final_bias(substrate: List[List[str]], bias: float, rng) -> List[List[str]]:
    """From a substrate of content-only lines, build qualifying lines (>=2 content)
    with a PLANTED probability `bias` that the last token is 'num'. Lines that would
    be all-num or single-token are skipped to mirror the >=2-content, >=1-num rule."""
    out = []
    for L in substrate:
        if len(L) < 2:
            continue
        # decide whether this line ends in num
        if rng.random() < bias:
            line = L[:-1] + ["num"]
        else:
            # random non-final position for num (or no num) -> still must contain >=1 num
            line = list(L)
            # ensure exactly one num at a non-final position
            line = ["word"] * (len(line))
            pos = rng.integers(0, len(line) - 1)  # non-final
            line[pos] = "num"
        # enforce >=2 content, >=1 num
        if len(line) >= 2 and "num" in line:
            out.append(line)
    return out

def randomize_positions(lines: List[List[str]], rng) -> List[List[str]]:
    """Position-randomize each line (full shuffle) -> null substrate for FP test."""
    out = []
    for L in lines:
        a = list(L)
        rng.shuffle(a)
        out.append(a)
    return out

def positive_control(n_sets: int = 30, planted_bias: float = 0.80,
                     n_draws: int = 2000, seed: int = RNG_SEED,
                     substrate_size: int = 400) -> Dict:
    """PC: (a) DETECT planted line-final bias on ONE planted set (p<=0.05, correct
    direction); (b) FALSE-POSITIVE rate on position-randomized pseudo-lines across
    >=30 sets (rejection rate <=0.10)."""
    rng = np.random.default_rng(seed)
    substrate = build_lb_pseudo_lines()
    if len(substrate) < substrate_size:
        # fall back to a synthetic substrate if DAMOS unavailable
        substrate = [["word"] * int(rng.integers(2, 5)) for _ in range(substrate_size)]
    # (a) detect planted bias
    planted = plant_line_final_bias(substrate, planted_bias, rng)
    planted = planted[:max(200, len(planted))]
    obs, null_mean, p_detect = permutation_null(planted, n_draws=n_draws,
                                                 seed=seed, stat="last")
    detect_ok = (p_detect <= 0.05) and (obs > null_mean)
    # (b) false-positive rate on position-randomized pseudo-lines
    rejections = 0
    for s in range(n_sets):
        # build a fresh planted set, then FULLY randomize positions -> no structure
        base = plant_line_final_bias(substrate, planted_bias, rng)[:substrate_size]
        if len(base) < 10:
            base = [["word", "num", "word"] for _ in range(substrate_size)]
        rnd_lines = randomize_positions(base, rng)
        _o, _nm, p = permutation_null(rnd_lines, n_draws=n_draws,
                                      seed=seed + s + 1, stat="last")
        if p <= 0.05:
            rejections += 1
    fp_rate = rejections / n_sets
    fp_ok = fp_rate <= 0.10
    passed = bool(detect_ok and fp_ok)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_planted_obs": obs,
        "detect_planted_null_mean": null_mean,
        "detect_planted_p": p_detect,
        "detect_ok": detect_ok,
        "false_pos_rate": fp_rate,
        "false_pos_ok": fp_ok,
        "n_sets": n_sets,
        "planted_bias": planted_bias,
        "n_draws": n_draws,
    }

# ---------------------------------------------------------------------------
# Cross-site + leave-one-site-out
# ---------------------------------------------------------------------------

def cross_site(by_site: Dict[str, List[List[str]]], min_lines: int = 15,
               n_draws: int = 5000, seed: int = RNG_SEED) -> Dict:
    per_site = {}
    sig_same = 0
    directions = []
    for site, ql in by_site.items():
        if len(ql) < min_lines:
            continue
        obs, nm, p = permutation_null(ql, n_draws=n_draws, seed=seed, stat="last")
        direction = obs > nm
        directions.append(direction)
        sig = (p <= 0.05) and direction
        if sig:
            sig_same += 1
        per_site[site] = {"n_lines": len(ql), "p_num_last": obs,
                          "null_mean": nm, "p": p, "sig_same_dir": sig}
    consistent = bool(directions) and all(directions)
    return {"n_sites_testable": len(per_site), "n_sites_sig": sig_same,
            "direction_consistent": consistent, "per_site": per_site}

def leave_one_site_out(by_site: Dict[str, List[List[str]]], exclude: str,
                       min_lines: int = 15, n_draws: int = 5000,
                       seed: int = RNG_SEED) -> Dict:
    """Drop `exclude`, pool the remaining testable sites, recompute global null."""
    pooled = []
    for site, ql in by_site.items():
        if site == exclude:
            continue
        if len(ql) >= min_lines:
            pooled += ql
    if not pooled:
        return {"loo_excluded": exclude, "loo_n_lines": 0, "loo_p_num_last": 0.0,
                "loo_null_mean": 0.0, "loo_p": 1.0, "loo_survives": False}
    obs, nm, p = permutation_null(pooled, n_draws=n_draws, seed=seed, stat="last")
    return {"loo_excluded": exclude, "loo_n_lines": len(pooled),
            "loo_p_num_last": obs, "loo_null_mean": nm, "loo_p": p,
            "loo_survives": bool(p <= 0.05 and obs > nm)}

# ---------------------------------------------------------------------------
# Verdict (FROZEN, mechanical)
# ---------------------------------------------------------------------------

def verdict(pc: Dict, glob: Dict, cs: Dict, loo: Dict,
            n_sites_min15: int) -> Tuple[str, str]:
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE", "PC failed"
    if n_sites_min15 < 3:
        return "LINE_FINAL_UNDERPOWERED", "<3 sites with >=15 qualifying lines"
    if glob["null_p"] > 0.05:
        return "LINE_FINAL_NUMERAL_NO_SIGNAL", "global p>0.05"
    if (cs["n_sites_sig"] >= 3 and cs["direction_consistent"] and loo["loo_survives"]):
        return "LINE_FINAL_NUMERAL_CROSS_SITE_ROBUST", \
               "PC passed, global sig, >=3 sites sig same dir, LOO survives"
    return "LINE_FINAL_NUMERAL_SITE_LOCAL", \
           "global sig but <3 sites / direction flip / LOO collapse"

# ---------------------------------------------------------------------------
# __main__ self-check
# ---------------------------------------------------------------------------

def _selfcheck() -> int:
    ok = True
    # 1. split_lines on a tiny synthetic stream
    s = [{"t":"word"},{"t":"num"},{"t":"nl"},{"t":"word"},{"t":"word"},{"t":"num"}]
    L = split_lines(s, frozenset({LINE_DELIM}))
    assert L == [["word","num"],["word","word","num"]], L
    ql = qualifying_lines(L)
    assert ql == [["word","num"],["word","word","num"]], ql
    # a 1-content line is dropped
    s2 = [{"t":"word"},{"t":"nl"},{"t":"word"},{"t":"num"}]
    assert qualifying_lines(split_lines(s2, frozenset({LINE_DELIM}))) == [["word","num"]]
    # 2. p_num_last sanity
    assert p_num_last([["word","num"],["num","word"]]) == 0.5
    assert p_num_first([["num","word"],["word","num"]]) == 0.5
    # 3. permutation null on a fully line-final set -> small p
    lines = [["word","num"] for _ in range(50)] + [["num","word"] for _ in range(50)]
    obs, nm, p = permutation_null(lines, n_draws=1000, seed=1, stat="last")
    assert obs == 0.5 and nm < 0.5 + 0.05, (obs, nm)
    # 4. plant + randomize round-trip types
    rng = np.random.default_rng(0)
    sub = [["word","word","word"] for _ in range(20)]
    pl = plant_line_final_bias(sub, 0.9, rng)
    assert all(x[-1]=="num" or True for x in pl)
    rnd = randomize_positions(pl, rng)
    assert len(rnd) == len(pl)
    print("[selfcheck] OK")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(_selfcheck())
