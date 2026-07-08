#!/usr/bin/env python3
"""EPOCH-043 machinery — CROSS-SITE CERTIFICATION of positional specialization
(L2/L3, anonymous signs). Successor of E042.

FROZEN ANALYTIC NULL (reused from E042; see prereg.md):
  Under within-word uniform permutation H0, for a word w of length L containing
  sign S exactly k_w times, the probability that a SPECIFIC position p (initial
  index 0, or final index L-1) holds S is k_w / L_w, INDEPENDENTLY across words.
  The null count of S at position p is therefore a POISSON-BINOMIAL over the
  per-word Bernoulli probabilities p_w = k_w / L_w (words not containing S
  contribute 0 and are dropped).

  One-sided upper-tail p-value = P(X >= observed_count) under that
  Poisson-binomial. EXACT PMF via DP/convolution when n_bernoulli <= EXACT_CAP;
  else normal approximation with continuity correction. Method recorded per test.

  Holm correction across all (sign x position) tests WITHIN A SCOPE at family
  alpha 0.05. A sign is POSITION-SPECIALIZED (in a site or globally) if enriched
  in INITIAL OR FINAL after Holm within that scope.

Signs are ANONYMOUS tokens. No phonetics / meaning / reading. LB is a positive
control benchmark ONLY.
"""
from __future__ import annotations
import json, os, sys, math, random
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LA_CORPUS = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
EPOCH_DIR = os.path.dirname(os.path.abspath(__file__))

ALPHA = 0.05          # family-wise (Holm)
EXACT_CAP = 4000      # exact Poisson-binomial convolution up to this many Bernoullis
TOKEN_THRESHOLD = 80  # site qualifies for cross-site iff >=80 sign-tokens
GLOBAL_MIN_OCC = 15   # global test threshold (reproduce E042)
SITE_MIN_OCC = 8      # per-site test threshold
RNG_SEED = 43043
POSITIONS = ("initial", "final")


# --------------------------------------------------------------------------- data
def load_la_words(corpus_path: str = LA_CORPUS) -> Tuple[List[List[str]], List[str]]:
    """Return (words, sites) — words are sign lists (len>=2), sites aligned."""
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
    """Exact Poisson-binomial PMF via DP convolution. P[k] = P(exactly k successes)."""
    n = len(probs)
    P = np.zeros(n + 1, dtype=np.float64)
    P[0] = 1.0
    for p in probs:
        P[1:] = P[1:] * (1.0 - p) + P[:-1] * p
        P[0] = P[0] * (1.0 - p)
    return P


def upper_tail_pvalue(probs: List[float], observed: int) -> Tuple[float, str]:
    """One-sided upper-tail p = P(X >= observed) under Poisson-binomial(probs)."""
    n = len(probs)
    if n == 0:
        return (1.0, "empty")
    if observed <= 0:
        return (1.0, "trivial_obs0")
    if observed > n:
        return (0.0, "impossible")
    if n <= EXACT_CAP:
        P = poisson_binomial_pmf(probs)
        tail = float(np.clip(P[observed:].sum(), 0.0, 1.0))
        return (tail, "exact_convolution")
    mu = float(sum(probs))
    var = float(sum(p * (1.0 - p) for p in probs))
    if var <= 0.0:
        x = int(round(mu))
        return (1.0 if observed <= x else 0.0, "normal_degenerate")
    sigma = math.sqrt(var)
    z = (observed - 0.5 - mu) / sigma
    from math import erf
    pval = 0.5 * (1.0 - erf(z / math.sqrt(2.0)))
    return (float(np.clip(pval, 0.0, 1.0)), "normal_cc")


def sign_position_data(words: List[List[str]], sign: str):
    """For a sign: (obs_init, obs_final, bernoulli_probs) over words containing it."""
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
    """Holm step-down reject booleans aligned to pvals."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    reject = [False] * m
    for rank, idx in enumerate(order):
        thresh = alpha / (m - rank)
        if pvals[idx] <= thresh:
            reject[idx] = True
        else:
            break
    return reject


def holm_adjusted_pvals(pvals: List[float]) -> List[float]:
    """Holm-adjusted p-values (monotone) aligned to input."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        a = pvals[idx] * (m - rank)
        if a > running:
            running = a
        adj[idx] = min(running, 1.0)
    return adj


def analyze_scope(words: List[List[str]], min_occ: int) -> Dict:
    """Run analytic positional-specialization on `words` at the given min_occ.

    Returns dict: testable signs, records (with p_init/p_final, holm booleans,
    preferred position), specialized set, fractions.
    """
    occ_tokens = Counter()
    for w in words:
        if len(w) >= 2:
            occ_tokens.update(w)
    testable = sorted([s for s, n in occ_tokens.items() if n >= min_occ])

    records = []
    for s in testable:
        oi, of, probs = sign_position_data(words, s)
        p_init, m_init = upper_tail_pvalue(probs, oi)
        p_fin, m_fin = upper_tail_pvalue(probs, of)
        nww = len(probs)
        records.append({
            "sign": s,
            "obs_init": oi, "obs_final": of,
            "n_words_with": nww,
            "init_rate": (oi / nww if nww else 0.0),
            "final_rate": (of / nww if nww else 0.0),
            "p_init": p_init, "p_final": p_fin,
            "method_init": m_init, "method_final": m_fin,
            "n_occ": occ_tokens[s],
        })

    pvals = []
    for r in records:
        pvals.append(r["p_init"]); pvals.append(r["p_final"])
    reject = holm_correct(pvals, ALPHA)
    adj = holm_adjusted_pvals(pvals)

    specialized = []
    n_init_spec = 0
    n_final_spec = 0
    for i, r in enumerate(records):
        ri = reject[2 * i]
        rf = reject[2 * i + 1]
        r["holm_reject_init"] = ri
        r["holm_reject_final"] = rf
        r["holm_adj_p_init"] = adj[2 * i]
        r["holm_adj_p_final"] = adj[2 * i + 1]
        if ri or rf:
            # preferred position: smaller adjusted p; tie -> larger rate excess
            if ri and rf:
                if r["holm_adj_p_init"] < r["holm_adj_p_final"]:
                    pref = "initial"
                elif r["holm_adj_p_final"] < r["holm_adj_p_init"]:
                    pref = "final"
                else:
                    pref = "initial" if r["init_rate"] >= r["final_rate"] else "final"
            elif ri:
                pref = "initial"
            else:
                pref = "final"
            r["preferred"] = pref
            specialized.append(r)
            if pref == "initial":
                n_init_spec += 1
            else:
                n_final_spec += 1
        else:
            r["preferred"] = None

    n_tested = len(records)
    frac = (len(specialized) / n_tested) if n_tested else 0.0
    return {
        "n_tested": n_tested,
        "n_specialized": len(specialized),
        "specialized_fraction": frac,
        "n_initial_spec": n_init_spec,
        "n_final_spec": n_final_spec,
        "records": records,
        "specialized": specialized,
    }


# ----------------------------------------------------------- shuffling control
def shuffle_within_words(words: List[List[str]], rng: random.Random) -> List[List[str]]:
    """Destroy positional structure by permuting signs within each word."""
    out = []
    for w in words:
        ww = list(w)
        rng.shuffle(ww)
        out.append(ww)
    return out


def seed_pseudo_sites(words: List[List[str]], n_sites: int, rng: random.Random) -> List[List[List[str]]]:
    """Partition `words` into n_sites pseudo-sites of (near-)equal size by random
    assignment, preserving word integrity. Used to seed LB into comparable sites."""
    idx = list(range(len(words)))
    rng.shuffle(idx)
    chunks = [[] for _ in range(n_sites)]
    for j, i in enumerate(idx):
        chunks[j % n_sites].append(words[i])
    return chunks


# ----------------------------------------------------------------- self-check
def _bruteforce_upper_tail(words: List[List[str]], sign: str, position: str,
                           n_draws: int = 200000, seed: int = 12345) -> float:
    """Brute-force permutation upper-tail p for a sign at a position.

    Under H0 (within-word uniform permutation), re-draw positions by permuting
    each word's signs and count how often the sign lands at `position` >= observed.
    """
    rng = random.Random(seed)
    # observed count
    obs = 0
    contrib_words = []
    for w in words:
        if len(w) < 2:
            continue
        k = sum(1 for s in w if s == sign)
        if k == 0:
            continue
        contrib_words.append(list(w))
        if position == "initial" and w[0] == sign:
            obs += 1
        if position == "final" and w[-1] == sign:
            obs += 1
    if obs == 0:
        return 1.0
    ge = 0
    for _ in range(n_draws):
        c = 0
        for w in contrib_words:
            ww = list(w)
            rng.shuffle(ww)
            if position == "initial" and ww[0] == sign:
                c += 1
            elif position == "final" and ww[-1] == sign:
                c += 1
            if c >= obs:
                ge += 1
                break
    return ge / n_draws


def self_check() -> None:
    """Validate Poisson-binomial upper tail vs brute-force permutation on a small
    synthetic case. Assert agreement within tolerance."""
    # synthetic: a sign that is strongly final-specialized
    rng = random.Random(7)
    words = []
    target = "ZZ"
    # 40 words of length 3, target placed at final in 30 of them (excess)
    for i in range(40):
        w = [f"x{i%5}", f"y{i%4}", target] if i < 30 else [target, f"a{i%3}", f"b{i%6}"]
        # ensure length 3 distinct-ish; rebuild to guarantee target count
        words.append(w)
    # analytic
    oi, of, probs = sign_position_data(words, target)
    p_an_init, _ = upper_tail_pvalue(probs, oi)
    p_an_fin, _ = upper_tail_pvalue(probs, of)
    # brute force
    p_bf_init = _bruteforce_upper_tail(words, target, "initial", n_draws=100000, seed=91)
    p_bf_fin = _bruteforce_upper_tail(words, target, "final", n_draws=100000, seed=92)
    # tolerance: analytic exact vs monte carlo (SE ~ sqrt(p(1-p)/n))
    def close(a, b, tol=0.01):
        return abs(a - b) <= max(tol, 3 * math.sqrt(max(a, 0.0001) * (1 - max(a, 0.0001)) / 100000 + 1e-9))
    assert close(p_an_init, p_bf_init), f"INIT mismatch analytic={p_an_init} bf={p_bf_init}"
    assert close(p_an_fin, p_bf_fin), f"FIN mismatch analytic={p_an_fin} bf={p_bf_fin}"
    # sanity: final should be much smaller p than initial here
    assert p_an_fin < p_an_init, "expected final enrichment"
    # PMF sums to 1
    P = poisson_binomial_pmf([0.1, 0.3, 0.5, 0.9])
    assert abs(float(P.sum()) - 1.0) < 1e-9, "PMF must sum to 1"
    print(f"[self-check OK] analytic vs brute-force: init {p_an_init:.5f}~{p_bf_init:.5f}, "
          f"final {p_an_fin:.5f}~{p_bf_fin:.5f}; PMF sum=1.")


if __name__ == "__main__":
    self_check()
    print("EPOCH-043 machinery self-check PASSED.")
