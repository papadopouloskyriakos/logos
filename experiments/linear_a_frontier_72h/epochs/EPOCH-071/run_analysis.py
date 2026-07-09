"""
EPOCH-071 main analysis runner.
Computes S for libation (Stone vessel) and admin (Tablet+Nodule+Roundel) corpora,
runs the marginal-preserving reassignment null, and runs the PC protocol
(detect power + false-positive rate) on synthetic corpora matching real structure.
"""

import json
import sys
import os
import random
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from machinery import (
    tokens_of, corpus_summary, S_stat, null_distribution, _sample_table
)

CORPUS = os.path.join(HERE, "..", "..", "..", "..", "corpus", "silver", "inscriptions_structured.json")
CORPUS = os.path.normpath(CORPUS)


def load():
    d = json.load(open(CORPUS))
    sv = [x for x in d if x["support"] == "Stone vessel"]
    admin = [x for x in d if x["support"] in ("Tablet", "Nodule", "Roundel")]
    return sv, admin


def analyze_corpus(inscs, name, n_draws=2000, seed=71071):
    st, fs, fc = corpus_summary(inscs)
    S = S_stat(fs)
    mean, p, Ss = null_distribution(fc, st, S, n_draws=n_draws, seed=seed)
    ratio = S / mean if mean > 0 else float("inf")
    # multisite forms
    multisite = [(f, len(fs[f]), fc[f]) for f in fc if len(fs[f]) >= 2]
    multisite.sort(key=lambda t: (-t[1], -t[2]))
    res = {
        "name": name,
        "n_inscriptions": len(inscs),
        "n_sites": len(st),
        "total_tokens": int(sum(st.values())),
        "n_forms": len(fc),
        "S_obs": float(S),
        "null_mean": float(mean),
        "perm_p": float(p),
        "ratio": float(ratio),
        "n_multisite_forms": len(multisite),
        "null_S_min": float(min(Ss)),
        "null_S_max": float(max(Ss)),
        "sites_ge20_tokens": int(sum(1 for c in st.values() if c >= 20)),
        "top_forms": [("-".join(f), nsites, cnt) for f, nsites, cnt in multisite[:12]],
    }
    return res


# ---------- PC synthetic generators ----------

def make_formula_corpus(n_sites, site_size, n_formula, formula_count,
                        n_singletons_per_site, rng):
    """Synthetic with a genuine formula: n_formula forms each at ALL n_sites
    (count = formula_count, distributed one-per-site), rest singletons."""
    fc = {}
    fs = {}
    for k in range(n_formula):
        f = ("F", k)
        fc[f] = formula_count
        fs[f] = set(range(n_sites))
    st = {s: 0 for s in range(n_sites)}
    for f in fc:
        c = fc[f]
        sl = list(fs[f])
        for i in range(c):
            st[sl[i % len(sl)]] += 1
    sid = 0
    for s in range(n_sites):
        for _ in range(n_singletons_per_site):
            f = ("S", sid); sid += 1
            fc[f] = 1; fs[f] = {s}; st[s] += 1
        while st[s] < site_size:
            f = ("S", sid); sid += 1
            fc[f] = 1; fs[f] = {s}; st[s] += 1
    return fc, fs, st


def make_freqonly_corpus(n_sites, site_size, n_forms, form_count, rng):
    """Synthetic with NO formula: each form's tokens assigned to sites
    proportional to site size (pure frequency-driven overlap)."""
    fc = {}
    fs = {}
    site_tot = np.array([site_size] * n_sites, dtype=float)
    site_p = site_tot / site_tot.sum()
    # track per-site token placement to build exact site totals
    placement = Counter()  # (form, site) -> count
    for k in range(n_forms):
        f = ("L", k)
        c = form_count
        fc[f] = c
        sites_used = set()
        for _ in range(c):
            s = int(rng.choice(n_sites, p=site_p))
            placement[(f, s)] += 1
            sites_used.add(s)
        fs[f] = sites_used
    st = {s: 0 for s in range(n_sites)}
    for (f, s), c in placement.items():
        st[s] += c
    sid = 0
    for s in range(n_sites):
        while st[s] < site_size:
            f = ("S", sid); sid += 1
            fc[f] = 1; fs[f] = {s}; st[s] += 1
    return fc, fs, st


def run_pc(n_draws_null=500, seed0=9001):
    rng = np.random.default_rng(seed0)
    # (a) DETECT: genuine formula -> enriched. Power over N_DET draws.
    N_DET = 25
    detect_pvals = []
    for t in range(N_DET):
        fc, fs, st = make_formula_corpus(
            n_sites=5, site_size=25, n_formula=5, formula_count=5,
            n_singletons_per_site=4, rng=rng)
        S = S_stat(fs)
        m, p, _ = null_distribution(fc, st, S, n_draws=n_draws_null,
                                    seed=int(rng.integers(0, 10**9)))
        detect_pvals.append(p)
    detect_p = float(np.median(detect_pvals))
    power = float(np.mean([1 if p <= 0.05 else 0 for p in detect_pvals]))

    # (b) FALSE POSITIVE: frequency-only -> NOT enriched. Rate over N_FP draws.
    N_FP = 25
    fp_pvals = []
    for t in range(N_FP):
        fc, fs, st = make_freqonly_corpus(
            n_sites=5, site_size=25, n_forms=20, form_count=4, rng=rng)
        S = S_stat(fs)
        m, p, _ = null_distribution(fc, st, S, n_draws=n_draws_null,
                                    seed=int(rng.integers(0, 10**9)))
        fp_pvals.append(p)
    false_pos_rate = float(np.mean([1 if p <= 0.05 else 0 for p in fp_pvals]))

    pc_pass = (power >= 0.5) and (false_pos_rate <= 0.10)
    return {
        "pc_verdict": "PASSED" if pc_pass else "FAILED",
        "detect_p": detect_p,
        "detect_power": power,
        "false_pos_rate": false_pos_rate,
        "power_est": power,
        "pc_is_synthetic": True,
        "n_detect_draws": N_DET,
        "n_falsepos_draws": N_FP,
        "detect_pvals_min": float(min(detect_pvals)),
        "fp_pvals": [float(x) for x in fp_pvals],
    }


def main():
    sv, admin = load()
    lib = analyze_corpus(sv, "LIBATION", n_draws=2000, seed=71071)
    adm = analyze_corpus(admin, "ADMIN", n_draws=2000, seed=71072)
    pc = run_pc(n_draws_null=500, seed0=9001)

    out = {"libation": lib, "admin": adm, "positive_control": pc}
    print(json.dumps(out, indent=2, default=str))
    # save raw to data dir
    data_dir = os.path.join(HERE, "..", "..", "data", "epoch_071")
    data_dir = os.path.normpath(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    json.dump(out, open(os.path.join(data_dir, "analysis_raw.json"), "w"),
              indent=2, default=str)
    print("\nSaved raw analysis to", os.path.join(data_dir, "analysis_raw.json"))


if __name__ == "__main__":
    main()
