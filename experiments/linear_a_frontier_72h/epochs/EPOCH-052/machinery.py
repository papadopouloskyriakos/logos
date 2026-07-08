#!/usr/bin/env python3
"""
EPOCH-052 machinery — ZIPF / HEAPS STATISTICAL SIGNATURE.

Pure L2/L3 frequency-distribution statistics on ANONYMOUS forms/signs.
No phonetics, no meaning, no language identification. Linear B is a CONTROL ONLY.

FROZEN FITTERS:
  zipf_fit(counter)  -> (slope, r2)  fitting log(freq) ~ slope*log(rank) over all
                        distinct types (rank 1..R). NL word Zipf slope ~ -1.
  heaps_fit(stream)  -> (beta, r2)  fitting log(V) ~ beta*log(N) over the token
                        stream in order. NL beta ~ 0.4-0.8.

HONEST CAVEAT (Miller 1957): Zipf adherence is NECESSARY-NOT-SUFFICIENT for language.
Even i.i.d. draws from a Zipfian unigram are Zipf-like. The informative baseline is a
UNIFORM-random token stream (slope ~ 0). A STRONG DEVIATION from Zipf/Heaps is more
informative than adherence.

POSITIVE CONTROL (gates the verdict):
  - LB (real language) must recover word Zipf slope in [-1.2,-0.8], R^2>=0.9, AND
    Heaps beta in [0.4,0.8].
  - UNIFORM-random token stream must give |slope|<0.3 (non-Zipfian).
  Failure of either -> MACHINERY_UNINFORMATIVE.
"""
from __future__ import annotations
import json, math, random, sys
from collections import Counter
from typing import List, Tuple, Sequence

import numpy as np


# --------------------------------------------------------------------------- #
# FROZEN FITTERS
# --------------------------------------------------------------------------- #
def zipf_fit(counter: Counter) -> Tuple[float, float]:
    """Fit log(freq) ~ slope*log(rank). Returns (slope, R^2)."""
    freqs = sorted(counter.values(), reverse=True)
    if len(freqs) < 5:
        return float("nan"), float("nan")
    ranks = np.arange(1, len(freqs) + 1, dtype=float)
    x = np.log(ranks)
    y = np.log(np.asarray(freqs, dtype=float))
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    pred = slope * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(slope), float(r2)


def heaps_fit(token_stream: Sequence) -> Tuple[float, float]:
    """Fit log(V) ~ beta*log(N) over the token stream in order. Returns (beta, R^2)."""
    seen = set()
    ns, vs = [], []
    for i, tok in enumerate(token_stream, start=1):
        seen.add(tok)
        # sample to keep arrays small but capture the curve shape
        if i <= 200 or i % max(1, len(token_stream) // 400) == 0 or i == len(token_stream):
            ns.append(i)
            vs.append(len(seen))
    ns = np.asarray(ns, dtype=float)
    vs = np.asarray(vs, dtype=float)
    if len(ns) < 5:
        return float("nan"), float("nan")
    x = np.log(ns)
    y = np.log(vs)
    A = np.vstack([x, np.ones_like(x)]).T
    beta, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    pred = beta * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(beta), float(r2)


# --------------------------------------------------------------------------- #
# DATA LOADERS
# --------------------------------------------------------------------------- #
def load_la() -> Tuple[List[Tuple[str, ...]], List[str]]:
    """Return (word_forms, sign_tokens) for Linear A."""
    d = json.load(open("corpus/silver/inscriptions_structured.json"))
    words, signs = [], []
    for ins in d:
        for s in ins.get("stream", []):
            if s.get("t") == "word" and "signs" in s:
                sg = tuple(s["signs"])
                words.append(sg)
                signs.extend(s["signs"])
    return words, signs


def load_lb() -> Tuple[List[Tuple[str, ...]], List[str]]:
    """Return (word_forms, sign_tokens) for Linear B (DAMOS). Control only."""
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    from scripts.cross_script.data import load_b_damos
    toks, _cnt, _map = load_b_damos()  # list of per-word sign-tuples
    words = [tuple(w) for w in toks]
    signs = [s for w in words for s in w]
    return words, signs


def uniform_random_stream(vocab: Sequence, n: int, seed: int = 1729) -> List:
    rng = random.Random(seed)
    v = list(vocab)
    return [rng.choice(v) for _ in range(n)]


# --------------------------------------------------------------------------- #
# POSITIVE CONTROL + MECHANICAL VERDICT
# --------------------------------------------------------------------------- #
def positive_control(lb_words, lb_signs) -> dict:
    lb_word_c = Counter(lb_words)
    lb_slope, lb_r2 = zipf_fit(lb_word_c)
    lb_beta, lb_beta_r2 = heaps_fit(lb_words)
    # uniform-random stream from LA-like vocab size, same length as LB
    vocab = list(range(len(lb_word_c)))
    uni = uniform_random_stream(vocab, len(lb_words), seed=1729)
    uni_slope, uni_r2 = zipf_fit(Counter(uni))

    lb_recovered_ok = (
        not math.isnan(lb_slope) and -1.2 <= lb_slope <= -0.8 and lb_r2 >= 0.9
        and not math.isnan(lb_beta) and 0.4 <= lb_beta <= 0.8
    )
    uniform_distinguished = (not math.isnan(uni_slope)) and abs(uni_slope) < 0.3
    pc_passed = bool(lb_recovered_ok and uniform_distinguished)
    return {
        "pc_verdict": "PASSED" if pc_passed else "FAILED",
        "lb_recovered_ok": bool(lb_recovered_ok),
        "uniform_distinguished": bool(uniform_distinguished),
        "lb_word_zipf_slope": lb_slope, "lb_word_zipf_r2": lb_r2,
        "lb_heaps_beta": lb_beta, "lb_heaps_r2": lb_beta_r2,
        "uniform_zipf_slope": uni_slope, "uniform_zipf_r2": uni_r2,
    }


def mechanical_verdict(pc: dict, la_word_slope, la_word_r2, la_heaps_beta,
                       la_heaps_r2, n_tokens, n_forms) -> str:
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    if n_tokens < 300 or n_forms < 100:
        return "ZIPF_UNDERPOWERED"
    # poor fits -> inconclusive
    if (math.isnan(la_word_r2) or la_word_r2 < 0.9 or math.isnan(la_heaps_r2)
            or la_heaps_r2 < 0.9):
        return "ZIPF_HEAPS_INCONCLUSIVE"
    # atypical: clearly outside language-typical ranges
    lang_slope = -1.3 <= la_word_slope <= -0.6
    lang_beta = 0.35 <= la_heaps_beta <= 0.85
    if lang_slope and lang_beta:
        return "ZIPF_HEAPS_LANGUAGELIKE"
    # if clearly outside -> atypical; if borderline near edges -> inconclusive
    def outside(lo, hi, v):
        return v < lo - 0.1 or v > hi + 0.1
    if outside(-1.3, -0.6, la_word_slope) or outside(0.35, 0.85, la_heaps_beta):
        return "ZIPF_HEAPS_ATYPICAL"
    return "ZIPF_HEAPS_INCONCLUSIVE"


# --------------------------------------------------------------------------- #
# SELF-CHECK (validates fitters on synthetic Zipf of known slope)
# --------------------------------------------------------------------------- #
def _self_check() -> None:
    rng = random.Random(2024)
    ok = True
    for planted in (-1.0, -0.9, -1.2):
        # synthetic Zipf: freq(r) ~ r^planted ; sample tokens accordingly
        R = 500
        ranks = np.arange(1, R + 1)
        probs = ranks.astype(float) ** planted
        probs /= probs.sum()
        types = [f"t{i}" for i in range(R)]
        N = 200000
        idx = rng.choices(range(R), weights=probs, k=N)
        stream = [types[i] for i in idx]
        slope, r2 = zipf_fit(Counter(stream))
        rec = abs(slope - planted)
        print(f"  [self-check] planted={planted} recovered_slope={slope:.3f} R2={r2:.3f} |diff|={rec:.3f}")
        if not (rec < 0.08 and r2 > 0.95):
            ok = False
    # heaps sanity: a fixed-vocabulary uniform stream -> beta -> 0 as N grows large;
    # a power-law vocab -> beta in (0,1). Just check it runs and is finite.
    beta, br2 = heaps_fit(stream)
    print(f"  [self-check] heaps on synthetic Zipf stream: beta={beta:.3f} R2={br2:.3f}")
    if not (0.0 < beta < 1.0 and br2 > 0.9):
        ok = False
    if not ok:
        print("SELF-CHECK FAILED"); sys.exit(1)
    print("SELF-CHECK PASSED")


if __name__ == "__main__":
    _self_check()
