#!/usr/bin/env python3
"""Graduation-gate null-calibration (preprint items 1.2 / 1.4).

Realized FALSE-GRADUATION RATE of the §E graduation gate under a null-generating process — the
multiplicity-abuse scenario the gate exists to stop. For each of B trials we draw N_eff random
candidate readings (no real signal), CHERRY-PICK the one with the best held-out recall (the analyst
who tries many maps and submits the best), and grade THAT through the full mechanical gate with the
search multiplicity INSTRUMENTED at N_eff. A calibrated gate refuses these: the deflation machinery
(the L_fake corrected-margin bar + the E[max over N_eff] order-statistic bar) rejects a
best-of-N_eff fluke because the bar is raised to exactly that multiplicity.

Reproduce: python3 scripts/gate_null_calibration.py
"""
from __future__ import annotations
import random, json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import verdict
from scripts.comparison import lexstat

# a ~22-symbol Semitic consonant-skeleton alphabet; HELD = held-out target skeletons (no real map exists)
CONS = "'bgdhwzHTyklmnspcqrsvt"
HELD = ["nwy", "brq", "mlk", "ywm", "dn", "qtl", "zkr", "bnh", "hlk", "yqr",
        "ktb", "smr", "dbr", "rcy", "qdm", "slm", "ntn", "cbd", "gdl", "khn"]


class _Log:                                 # duck-typed instrumented SearchLog (COUNTED N_eff)
    def __init__(self, n): self.n_eff = n; self.eps_grid = None


def _rand_form(rng):
    return "".join(rng.choice(CONS) for _ in range(rng.randint(2, 4)))


def run(B=500, N_EFF=100, seed=0):
    rng = random.Random(seed)
    base = dict(confidence=0.6, free_params=3, provenance="embedding_nn", lit_index_hit=False,
                not_indexed_sign_support=0.9, u_floor=8, n_eff=N_EFF, n_fake=12, seed=1,
                not_indexed_threshold=0.5)       # every NON-deflation clause satisfiable -> isolates deflation
    verdicts = Counter()
    grads = 0
    for _ in range(B):
        best_cand, best_obs = None, -1.0
        for _ in range(N_EFF):              # the multiplicity: try N_eff random maps, keep the best
            cand = [_rand_form(rng) for _ in range(len(HELD) + 4)]
            pf = lexstat.s_lex_per_form(HELD, cand, verdict.EPS_DEFAULT)
            obs = (sum(pf) / len(pf)) if pf else 0.0
            if obs > best_obs:
                best_obs, best_cand = obs, cand
        g = verdict.grade(HELD, best_cand, search_log=_Log(N_EFF), **base)
        verdicts[g["gate_verdict"]] += 1
        grads += (g["gate_verdict"] == "GRADUATE")
    rate = grads / B
    # one-sided exact Clopper-Pearson 95% upper bound (Beta-quantile inversion of the binomial)
    from scipy.stats import beta
    hi = float(beta.ppf(0.95, grads + 1, B - grads)) if grads < B else 1.0
    out = {"B": B, "N_eff": N_EFF, "false_graduations": grads,
           "false_graduation_rate": round(rate, 5),
           "clopper_pearson_onesided_95_upper": round(hi, 5),
           "verdict_breakdown": dict(verdicts)}
    print(f"B={B} trials, each cherry-picking best-of-{N_EFF} random null candidates; N_eff instrumented={N_EFF}")
    print(f"gate_verdict breakdown: {dict(verdicts)}")
    print(f"REALIZED FALSE-GRADUATION RATE = {grads}/{B} = {rate:.4f}  "
          f"(one-sided exact Clopper-Pearson 95% upper = {hi:.5f} = {hi*100:.3f}%)")
    Path("results").mkdir(exist_ok=True)
    json.dump(out, open("results/gate_null_calibration.json", "w"), indent=2)
    print(" -> results/gate_null_calibration.json")
    return out


if __name__ == "__main__":
    run()
