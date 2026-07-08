#!/usr/bin/env python3
"""EPOCH-042 machinery — sign positional-role specialization via ANALYTIC within-word
null (L2/L3, anonymous signs). Supersedes E041 (permutation p-floor removed).

FROZEN ANALYTIC NULL (see prereg.md):
  Under within-word uniform permutation H0, for a word w of length L containing sign
  S exactly k_w times, the probability that a SPECIFIC position p (initial index 0,
  or final index L-1) holds S is k_w / L, INDEPENDENTLY across words. The null count
  of S at position p is therefore a POISSON-BINOMIAL over the per-word Bernoulli
  probabilities p_w = k_w / L_w (words not containing S contribute 0 and are dropped).

  One-sided upper-tail p-value = P(X >= observed_count) under that Poisson-binomial.
  EXACT PMF via DP/convolution when n_bernoulli <= EXACT_CAP; else normal
  approximation with continuity correction. Method recorded per test.

  Holm correction across all (sign x position) tests at family alpha 0.05. A sign is
  POSITION-SPECIALIZED if enriched in INITIAL OR FINAL after Holm.

Signs are ANONYMOUS tokens. No phonetics / meaning / reading. LB is a positive
control benchmark ONLY.
"""
from __future__ import annotations
import json, os, sys, math
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LA_CORPUS = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
EPOCH_DIR = os.path.dirname(os.path.abspath(__file__))

MIN_OCC = 15          # sign must occur >=15 times in len>=2 words to be tested
ALPHA = 0.05          # family-wise (Holm)
EXACT_CAP = 4000      # use exact Poisson-binomial convolution up to this many Bernoullis
RNG_SEED = 42042
POSITIONS = ("initial", "final")


# --------------------------------------------------------------------------- data
def load_la_words(corpus_path: str = LA_CORPUS) -> Tuple[List[List[str]], List[str]]:
    """Return (words, sites) — words are sign lists (len>=2), sites aligned per word."""
    data = json.load(open(corpus_path, encoding="utf-8"))
    words: List[List[str]] = []
    sites: List[str] = []
    for ins in data:
        site = ins.get("site", "") or ""
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", []) or []
                if len(sg) >= 2:
                    words.append(list(sg))
                    sites.append(site)
    return words, sites


def load_lb_words() -> List[List[str]]:
    _scripts = os.path.join(ROOT, "scripts")
    if _scripts not in sys.path:
        sys.path.insert(0, _scripts)
    from cross_script import data as D  # type: ignore
    seqs, _freq, _v2g = D.load_b_damos()
    return [list(s) for s in seqs if len(s) >= 2]


# ----------------------------------------------------------- analytic null core
def poisson_binomial_pmf(probs: List[float]) -> np.ndarray:
    """Exact Poisson-binomial PMF via DP convolution. probs = per-trial success prob.

    Returns array P of length n+1 where P[k] = P(exactly k successes).
    """
    n = len(probs)
    # P[0] = 1; iterate trials. Use float64.
    P = np.zeros(n + 1, dtype=np.float64)
    P[0] = 1.0
    for p in probs:
        # newP[k] = P[k]*(1-p) + P[k-1]*p
        P[1:] = P[1:] * (1.0 - p) + P[:-1] * p
        P[0] = P[0] * (1.0 - p)
    return P


def upper_tail_pvalue(probs: List[float], observed: int) -> Tuple[float, str]:
    """One-sided upper-tail p = P(X >= observed) under Poisson-binomial(probs).

    Returns (pvalue, method). Exact convolution if len(probs) <= EXACT_CAP, else
    normal approximation with continuity correction.
    """
    n = len(probs)
    if n == 0:
        return (1.0, "empty")
    if observed <= 0:
        return (1.0, "trivial_obs0")
    if observed > n:
        return (0.0, "impossible")
    if n <= EXACT_CAP:
        P = poisson_binomial_pmf(probs)
        # P(X >= observed) = sum_{k>=observed} P[k]
        tail = float(np.clip(P[observed:].sum(), 0.0, 1.0))
        return (tail, "exact_convolution")
    # normal approx with continuity correction
    mu = float(sum(probs))
    var = float(sum(p * (1.0 - p) for p in probs))
    if var <= 0.0:
        # degenerate: all p in {0,1}; X deterministic = mu
        x = int(round(mu))
        return (1.0 if observed <= x else 0.0, "normal_degenerate")
    sigma = math.sqrt(var)
    z = (observed - 0.5 - mu) / sigma
    from math import erf
    pval = 0.5 * (1.0 - erf(z / math.sqrt(2.0)))
    return (float(np.clip(pval, 0.0, 1.0)), "normal_cc")


def sign_position_data(words: List[List[str]], sign: str):
    """For a sign, return per-position (observed_count, bernoulli_probs).

    For each word w containing the sign k_w times with length L_w:
      - contributes to INITIAL observed count: 1 if w[0]==sign else 0.
      - contributes to FINAL observed count: 1 if w[-1]==sign else 0.
      - bernoulli prob for BOTH positions = k_w / L_w (same for initial and final
        under H0, since each is one specific slot).
    Words not containing the sign contribute 0 to the count and 0 prob (dropped).
    """
    obs_init = 0
    obs_final = 0
    probs: List[float] = []
    for w in words:
        L = len(w)
        if L < 2:
            continue
        k = 0
        for s in w:
            if s == sign:
                k += 1
        if k == 0:
            continue
        probs.append(k / L)
        if w[0] == sign:
            obs_init += 1
        if w[-1] == sign:
            obs_final += 1
    return obs_init, obs_final, probs


def holm_correct(pvals: List[float], alpha: float = ALPHA) -> List[bool]:
    """Return boolean list (reject H0 after Holm) aligned to pvals."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    reject = [False] * m
    running_thresh = alpha
    for rank, idx in enumerate(order):
        thresh = alpha / (m - rank)
        if pvals[idx] <= thresh:
            reject[idx] = True
        else:
            break  # Holm step-down stops at first non-rejection
    return reject


def analyze(words: List[List[str]], min_occ: int = MIN_OCC):
    """Run the full analytic positional-specialization analysis on `words`.

    Returns a dict with per-sign results, Holm rejections, and aggregates.
    """
    # sign occurrence counts in len>=2 words
    occ = Counter()
    for w in words:
        if len(w) >= 2:
            occ.update(set(w))  # count words containing the sign (presence), but
    # NOTE: spec says ">=15 occurrences (counted in len>=2 words)". Use total token
    # occurrences (not presence) to match E041 convention and the spec wording.
    occ_tokens = Counter()
    for w in words:
        if len(w) >= 2:
            occ_tokens.update(w)
    testable = [s for s, n in occ_tokens.items() if n >= min_occ]
    testable.sort()

    records = []
    for s in testable:
        oi, of, probs = sign_position_data(words, s)
        p_init, m_init = upper_tail_pvalue(probs, oi)
        p_fin, m_fin = upper_tail_pvalue(probs, of)
        n_words_with = len(probs)
        init_rate = oi / n_words_with if n_words_with else 0.0
        final_rate = of / n_words_with if n_words_with else 0.0
        records.append({
            "sign": s,
            "obs_init": oi, "obs_final": of,
            "n_words_with": n_words_with,
            "init_rate": init_rate, "final_rate": final_rate,
            "p_init": p_init, "p_final": p_fin,
            "method_init": m_init, "method_final": m_fin,
            "n_occ": occ_tokens[s],
        })

    # Holm across all (sign x position) tests = 2 * len(records)
    pvals = []
    for r in records:
        pvals.append(r["p_init"]); pvals.append(r["p_final"])
    reject = holm_correct(pvals, ALPHA)
    adj_pvals = holm_adjusted_pvals(pvals)

    specialized = []
    n_init_spec = 0
    n_final_spec = 0
    for i, r in enumerate(records):
        ri = reject[2 * i]
        rf = reject[2 * i + 1]
        r["holm_reject_init"] = ri
        r["holm_reject_final"] = rf
        r["holm_p_init"] = adj_pvals[2 * i]
        r["holm_p_final"] = adj_pvals[2 * i + 1]
        if ri or rf:
            # preferred position: smaller adjusted p; tie -> larger rate excess
            if ri and rf:
                if r["holm_p_init"] <= r["holm_p_final"]:
                    pref = "initial"
                else:
                    pref = "final"
            elif ri:
                pref = "initial"
            else:
                pref = "final"
            specialized.append({
                "sign": r["sign"],
                "preferred": pref,
                "init_rate": r["init_rate"],
                "final_rate": r["final_rate"],
                "holm_p": min(r["holm_p_init"], r["holm_p_final"]),
            })
            if pref == "initial":
                n_init_spec += 1
            else:
                n_final_spec += 1

    n_tested = len(records)
    specialized_fraction = (len(specialized) / n_tested) if n_tested else 0.0
    return {
        "n_tested": n_tested,
        "n_specialized": len(specialized),
        "specialized_fraction": specialized_fraction,
        "n_initial_spec": n_init_spec,
        "n_final_spec": n_final_spec,
        "specialized": specialized,
        "records": records,
    }


def holm_adjusted_pvals(pvals: List[float]) -> List[float]:
    """Holm-adjusted (family-wise) p-values, monotone, clipped to 1.

    Sort ascending p_(0) <= ... <= p_(m-1); raw adj q_(k) = p_(k) * (m - k);
    enforce monotonicity q_(k) = max(q_(k), q_(k-1)); clip to 1. Return in
    ORIGINAL index order.
    """
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    sorted_p = [pvals[i] for i in order]
    q = [min(1.0, sorted_p[k] * (m - k)) for k in range(m)]
    for k in range(1, m):
        q[k] = max(q[k], q[k - 1])
    adj = [0.0] * m
    for k, idx in enumerate(order):
        adj[idx] = float(min(q[k], 1.0))
    return adj


def _holm_adj_pval(pvals: List[float], idx: int, alpha: float = ALPHA) -> float:
    """Holm-adjusted p-value for a single test idx (family-wise)."""
    return holm_adjusted_pvals(pvals)[idx]


# ----------------------------------------------------------- false-positive PC
def shuffle_within_words(words: List[List[str]], rng: np.random.Generator) -> List[List[str]]:
    """Return a copy of words with signs permuted WITHIN each word (destroys real
    positional structure while preserving word lengths + per-word multisets)."""
    out = []
    for w in words:
        if len(w) <= 1:
            out.append(list(w)); continue
        perm = rng.permutation(len(w))
        out.append([w[j] for j in perm])
    return out


# --------------------------------------------------------------------------- main
def _selfcheck():
    """Validate the analytic Poisson-binomial upper tail against a brute-force
    within-word permutation on a small synthetic case."""
    rng = np.random.default_rng(12345)
    # synthetic corpus: a few signs, varied word lengths, one sign heavily initial.
    synth = [
        ["A", "B", "C"],
        ["A", "C", "D"],
        ["A", "B"],
        ["A", "D", "E", "B"],
        ["A", "C"],
        ["B", "A", "C"],   # A not initial here
        ["A", "E", "B", "C"],
        ["A", "B", "D"],
        ["C", "A", "B"],
        ["A", "D"],
    ]
    sign = "A"
    oi, of, probs = sign_position_data(synth, sign)
    p_analytic, method = upper_tail_pvalue(probs, oi)
    # brute-force: enumerate ALL within-word permutations equally likely.
    # For exactness use random draws (large) since full enumeration is complex with
    # repeated signs; use 400000 draws for tight tolerance.
    ND = 400000
    cnt_ge = 0
    for _ in range(ND):
        c = 0
        for w in synth:
            ww = list(w)
            rng.shuffle(ww)
            if ww[0] == sign:
                c += 1
        if c >= oi:
            cnt_ge += 1
    p_brute = cnt_ge / ND
    tol = 0.01
    ok = abs(p_analytic - p_brute) < tol
    print(f"[selfcheck] sign={sign} obs_init={oi} n_words_with={len(probs)}")
    print(f"[selfcheck] analytic upper-tail p = {p_analytic:.5f} ({method})")
    print(f"[selfcheck] brute-force  p = {p_brute:.5f} (ND={ND})")
    print(f"[selfcheck] |diff| = {abs(p_analytic-p_brute):.5f}  tol={tol}  -> {'PASS' if ok else 'FAIL'}")
    assert ok, f"Analytic Poisson-binomial tail disagrees with brute force: {p_analytic} vs {p_brute}"

    # also sanity-check the PMF sums to 1
    P = poisson_binomial_pmf([0.3, 0.5, 0.7])
    assert abs(P.sum() - 1.0) < 1e-9, P.sum()
    # known: P(X=0) = 0.7*0.5*0.3 = 0.105
    assert abs(P[0] - 0.105) < 1e-9, P[0]
    print("[selfcheck] PMF normalization + known-value check PASS")
    print("[selfcheck] ALL CHECKS PASSED")


if __name__ == "__main__":
    _selfcheck()
