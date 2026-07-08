#!/usr/bin/env python3
"""
EPOCH-046 machinery — WORD-LENGTH DISTRIBUTION SHAPE / GENERATIVE PROCESS.

Pure L2/L3 length-distribution statistics on ANONYMOUS sign ids. No phonetics, no sound, no
meaning, no reading. "Shape" = whether the word-length histogram is GEOMETRIC (memoryless,
monotone-decreasing from k=1) or PEAKED (mode >= 2, templatic). It is a distributional statistic,
NOT evidence of any language family or reading.

FROZEN MODELS:
  - GEOMETRIC: P(L=k) = (1-p)^(k-1) p, k=1,2,...  MLE p_hat = 1/mean.
  - PEAKED   : shifted-Poisson on support k=1,2,... with mode >= 2 (lambda >= 1 forced so the
               fitted mode is >= 2). MLE lambda = max(1.0, mean-1).

FROZEN DECISION (per unit):
  - GEOMETRIC iff observed mode == 1 (monotone-decreasing from k=1) AND geometric chi-square
    GoF p > 0.05.
  - PEAKED   iff observed mode >= 2 AND peaked_BIC < geometric_BIC.
  - else INCONCLUSIVE.

Binning for GoF/BIC: bins over support 1,2,... where each finite bin has geometric-expected
count >= 5 and the FINAL bin is open-ended [lo, inf) absorbing the full geometric tail mass, so
total expected == n exactly. Identical bins used for both models so BIC is comparable.

POSITIVE CONTROL (gates verdict):
  - DETECT both directions: synthetic GEOMETRIC data -> 'geometric'; synthetic PEAKED
    (mode>=2) data -> 'peaked'. Mislabel -> MACHINERY_UNINFORMATIVE.
  - LB (DĀMOS) word lengths classified + reported (sanity; expected geometric-ish).

Self-check: `python3 machinery.py` runs PC + global + cross-site and prints a JSON summary.
"""
import json, os, sys, random, math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chisquare, chi2 as chi2dist, poisson

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

# ---------- seeds (frozen) ----------
SEED_SYNTH_GEOM   = 20240770
SEED_SYNTH_PEAKED = 20240771
SEED_LB           = 20240772

MIN_SITE_WORDS = 50   # qualifying-site threshold for cross-site
MIN_N_FOR_GOF  = 30   # below this, do not trust GoF -> INCONCLUSIVE

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def la_word_lengths(corpus):
    out = []
    for ins in corpus:
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs") or []
                if len(sg) >= 1:
                    out.append(len(sg))
    return out

def la_per_site_lengths(corpus):
    per = defaultdict(list)
    for ins in corpus:
        s = ins.get("site", "") or "UNKNOWN"
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs") or []
                if len(sg) >= 1:
                    per[s].append(len(sg))
    return dict(per)

def lb_word_lengths():
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return [len(w) for w in seqs if len(w) >= 1]

# ---------- models ----------
def hist_dict(lengths):
    return dict(sorted(Counter(lengths).items()))

def mode_of(lengths):
    return max(Counter(lengths).items(), key=lambda kv: (kv[1], -kv[0]))[0]

def mean_of(lengths):
    return float(np.mean(lengths)) if lengths else float("nan")

def geom_pmf(k, p):
    return (1.0 - p) ** (k - 1) * p

def geom_tail(k, p):
    """P(L >= k) = (1-p)^(k-1)."""
    return (1.0 - p) ** (k - 1)

def shifted_poisson_pmf(k, lam):
    from scipy.stats import poisson
    return float(poisson.pmf(k - 1, lam))

def shifted_poisson_tail(k, lam):
    """P(L >= k) = P(Y >= k-1) for Y~Poisson(lam) = poisson.sf(k-2, lam)."""
    from scipy.stats import poisson
    return float(poisson.sf(k - 2, lam))

def build_bins(p, n, min_exp=5.0):
    """Geometric-driven binning over support 1,2,...: each finite bin has geometric-expected
    count >= min_exp; the FINAL bin is open-ended [lo, inf) absorbing the full tail so total
    expected == n exactly. Returns list of (lo, hi) with hi=None for the open tail."""
    bins = []
    lo = 1
    while True:
        e_first = n * geom_pmf(lo, p)
        if e_first < min_exp:
            # close as open tail bin [lo, inf)
            bins.append((lo, None))
            break
        acc = 0.0
        hi = lo
        while True:
            acc += n * geom_pmf(hi, p)
            if acc >= min_exp:
                break
            hi += 1
        bins.append((lo, hi))
        lo = hi + 1
        # safety
        if lo > 100000:
            break
    return bins

def expected_for_bin(lo, hi, model, param, n):
    """Expected count in bin [lo, hi] (hi=None => open tail) under the given model."""
    if model == "geom":
        p = param
        if hi is None:
            return n * geom_tail(lo, p)
        return n * sum(geom_pmf(k, p) for k in range(lo, hi + 1))
    else:  # shifted poisson
        lam = param
        if hi is None:
            return n * shifted_poisson_tail(lo, lam)
        return n * sum(shifted_poisson_pmf(k, lam) for k in range(lo, hi + 1))

def fit_models(lengths):
    """Fit geometric + peaked on identical (geometric-driven) bins. Returns dict."""
    n = len(lengths)
    mean = mean_of(lengths)
    p_hat = 1.0 / mean
    lam = max(1.0, mean - 1.0)
    bins = build_bins(p_hat, n, min_exp=5.0)
    cnt = Counter(lengths)
    obs_g, exp_g, exp_p = [], [], []
    for (lo, hi) in bins:
        o = sum(cnt.get(k, 0) for k in range(lo, (hi if hi is not None else max(lengths)) + 1))
        obs_g.append(float(o))
        exp_g.append(expected_for_bin(lo, hi, "geom", p_hat, n))
        exp_p.append(expected_for_bin(lo, hi, "pois", lam, n))
    obs_g = np.array(obs_g, float)
    exp_g = np.array(exp_g, float)
    exp_p = np.array(exp_p, float)
    # chi-square GoF for geometric (1 param estimated)
    nbins = len(bins)
    dof = max(1, nbins - 1 - 1)
    chi2_stat = float(np.sum((obs_g - exp_g) ** 2 / np.maximum(exp_g, 1e-12)))
    gof_p = float(1.0 - chi2dist.cdf(chi2_stat, dof))
    # BIC via binned multinomial log-likelihood (k_params=1 each)
    def ll(obs, exp):
        s = 0.0
        for o, e in zip(obs, exp):
            if o > 0 and e > 0:
                s += o * math.log(e / n)
        return s
    ll_g = ll(obs_g, exp_g)
    ll_p = ll(obs_g, exp_p)
    bic_g = -2.0 * ll_g + 1 * math.log(n)
    bic_p = -2.0 * ll_p + 1 * math.log(n)
    return {
        "n": n, "p_hat": p_hat, "lam": lam, "bins": bins,
        "obs": obs_g, "exp_g": exp_g, "exp_p": exp_p,
        "gof_chi2": chi2_stat, "gof_p": gof_p,
        "bic_g": bic_g, "bic_p": bic_p,
    }

def classify(lengths):
    """FROZEN per-unit classification."""
    if len(lengths) < MIN_N_FOR_GOF:
        return "INCONCLUSIVE"
    mode = mode_of(lengths)
    f = fit_models(lengths)
    monotone_from_1 = (mode == 1)
    if monotone_from_1 and f["gof_p"] > 0.05:
        return "geometric"
    if mode >= 2 and f["bic_p"] < f["bic_g"]:
        return "peaked"
    return "INCONCLUSIVE"

def full_stats(lengths):
    h = hist_dict(lengths)
    mode = mode_of(lengths)
    mean = mean_of(lengths)
    f = fit_models(lengths)
    cls = classify(lengths)
    return {
        "length_hist": {str(k): int(v) for k, v in h.items()},
        "mode": int(mode),
        "mean": round(float(mean), 4),
        "geometric_p_hat": round(float(f["p_hat"]), 6),
        "geometric_gof_p": round(float(f["gof_p"]), 6),
        "peaked_bic_minus_geom_bic": round(float(f["bic_p"] - f["bic_g"]), 4),
        "classification": cls,
        "_bic_g": float(f["bic_g"]),
        "_bic_p": float(f["bic_p"]),
        "_gof_chi2": float(f["gof_chi2"]),
    }

# ---------- synthetic generators (for PC) ----------
def synth_geometric(n, p, seed):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        k = 1
        while rng.random() > p:  # continuation prob = 1-p
            k += 1
            if k > 200:
                break
        out.append(k)
    return out[:n]

def synth_peaked(n, lam, seed):
    rng = np.random.default_rng(seed)
    y = rng.poisson(lam, size=n)
    return [int(yi) + 1 for yi in y]

# ---------- self-check / main ----------
def _selfcheck():
    g_data = synth_geometric(5000, p=0.55, seed=SEED_SYNTH_GEOM)
    g_label = classify(g_data)
    p_data = synth_peaked(5000, lam=3.0, seed=SEED_SYNTH_PEAKED)
    p_label = classify(p_data)
    return g_data, g_label, p_data, p_label

def main():
    corpus = load_corpus()
    la = la_word_lengths(corpus)
    per_site = la_per_site_lengths(corpus)

    g_data, g_label, p_data, p_label = _selfcheck()
    pc_pass = (g_label == "geometric") and (p_label == "peaked")
    lb = lb_word_lengths()
    lb_stats = full_stats(lb)

    glob = full_stats(la)

    site_results = {}
    for s, lens in sorted(per_site.items()):
        if len(lens) >= MIN_SITE_WORDS:
            site_results[s] = full_stats(lens)
    shape_counts = Counter(v["classification"] for v in site_results.values())

    loo_excluded = "Haghia Triada"
    loo_lens = [l for s, ls in per_site.items() if s != loo_excluded for l in ls]
    loo_cls = classify(loo_lens) if len(loo_lens) >= MIN_N_FOR_GOF else "INCONCLUSIVE"

    summary = {
        "positive_control": {
            "pc_verdict": "PASSED" if pc_pass else "FAILED",
            "synth_geometric_labeled": g_label,
            "synth_peaked_labeled": p_label,
            "lb_classification": lb_stats["classification"],
            "lb_mode": lb_stats["mode"],
            "lb_mean": lb_stats["mean"],
            "lb_geometric_gof_p": lb_stats["geometric_gof_p"],
        },
        "global": {k: v for k, v in glob.items() if not k.startswith("_")},
        "cross_site": {
            "n_sites": len(site_results),
            "shape_counts": dict(shape_counts),
            "loo_excluded": loo_excluded,
            "loo_classification": loo_cls,
            "per_site": {s: {k: v for k, v in r.items() if not k.startswith("_")}
                         for s, r in site_results.items()},
        },
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary

if __name__ == "__main__":
    main()
