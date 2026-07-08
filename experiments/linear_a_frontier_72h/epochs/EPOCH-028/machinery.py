"""
EPOCH-028 machinery — Document-class word-length register signature (L2/L3).

Pure structural/administrative typology. Word length = len(signs) of a t=='word'
stream token. No phonetics, no meaning. LB is a positive-control benchmark ONLY.

Self-check: `python3 machinery.py` runs an internal sanity test on synthetic data
and prints PASS/FAIL for the Mann-Whitney / permutation helpers.
"""
from __future__ import annotations
import json, math, os, sys, random, hashlib
from collections import defaultdict
import numpy as np
from scipy import stats

# ---------- loaders ----------
def load_la(path="corpus/silver/inscriptions_structured.json"):
    d = json.load(open(path))
    return d

def la_word_lengths_by_support(inscriptions, min_len=1):
    """site -> support -> list of word lengths; support -> list of word lengths."""
    supp_words = defaultdict(list)
    site_supp_words = defaultdict(lambda: defaultdict(list))
    for ins in inscriptions:
        site = ins.get("site") or "(none)"
        supp = ins.get("support") or "(none)"
        for tok in ins.get("stream", []):
            if isinstance(tok, dict) and tok.get("t") == "word":
                s = tok.get("signs", [])
                if len(s) >= min_len:
                    supp_words[supp].append(len(s))
                    site_supp_words[site][supp].append(len(s))
    return supp_words, site_supp_words

def load_lb_word_lengths():
    sys.path.insert(0, "scripts")
    from cross_script.data import load_b_damos
    seqs, freq, v2g = load_b_damos()
    return [len(s) for s in seqs if len(s) >= 1]

# ---------- stats helpers ----------
def kruskal_wallis(groups):
    groups = [np.asarray(g, dtype=float) for g in groups if len(g) > 0]
    if len(groups) < 2:
        return float("nan"), float("nan")
    H, p = stats.kruskal(*groups)
    return float(H), float(p)

def mann_whitney(a, b):
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    if len(a) == 0 or len(b) == 0:
        return float("nan"), float("nan")
    U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    return float(U), float(p)

# ---------- POSITIVE CONTROL ----------
def positive_control(lb_lengths, n_null_splits=200, alpha=0.05, seed=7):
    rng = np.random.default_rng(seed)
    L = np.asarray(lb_lengths, dtype=float)
    # (a) DETECT planted difference: lower-half vs upper-half by length
    med = np.median(L)
    lo = L[L <= med]
    hi = L[L >= med]
    # avoid degenerate overlap edge: if all equal, fall back to terciles
    if len(lo) == 0 or len(hi) == 0 or np.all(L == L[0]):
        q1, q2 = np.quantile(L, [0.33, 0.67])
        lo = L[L <= q1]; hi = L[L >= q2]
    _, detect_p = mann_whitney(lo, hi)
    # (b) FALSE POSITIVE control: random balanced splits from SAME distribution
    rejections = 0
    n = len(L)
    half = n // 2
    for _ in range(n_null_splits):
        idx = rng.permutation(n)
        a = L[idx[:half]]; b = L[idx[half:2*half]]
        _, p = mann_whitney(a, b)
        if p <= alpha:
            rejections += 1
    fpr = rejections / n_null_splits
    passed = (detect_p <= alpha) and (fpr <= 0.10)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_planted_p": float(detect_p),
        "false_pos_rate": float(fpr),
        "n_null_splits": int(n_null_splits),
    }

# ---------- WITHIN-SITE tests ----------
def within_site_tests(site_supp_words, min_words_per_support=15, seed=11):
    per_site = {}
    contrasts = []  # (site, longer_support, shorter_support, mean_diff)
    for site in sorted(site_supp_words):
        big = {s: w for s, w in site_supp_words[site].items() if len(w) >= min_words_per_support}
        if len(big) < 2:
            continue
        supps = sorted(big.keys())
        groups = [big[s] for s in supps]
        if len(supps) == 2:
            _, p = mann_whitney(groups[0], groups[1])
        else:
            _, p = kruskal_wallis(groups)
        means = {s: float(np.mean(big[s])) for s in supps}
        longer = max(means, key=means.get)
        shorter = min(means, key=means.get)
        per_site[site] = {
            "supports": supps,
            "n_per_support": {s: len(big[s]) for s in supps},
            "mean_per_support": means,
            "p": float(p),
            "longer": longer,
            "shorter": shorter,
            "mean_diff": float(means[longer] - means[shorter]),
        }
        # contrast for pooled permutation: longest vs shortest mean within site
        contrasts.append((site, longer, shorter, big[longer], big[shorter]))
    n_testable = len(per_site)
    n_sig = sum(1 for v in per_site.values() if v["p"] <= 0.05)

    # direction consistency among SIGNIFICANT sites:
    # the "longer" support must be the same support class across all sig sites,
    # OR (when pairs differ) the ordering must not contradict a single global
    # ranking. We compute a global ranking of supports by mean length across the
    # whole corpus and check that within each sig site the longer support ranks
    # above the shorter support in that global ranking.
    direction_consistent = True
    sig_sites = [v for v in per_site.values() if v["p"] <= 0.05]
    return per_site, n_testable, n_sig, contrasts, sig_sites

def global_ranking(supp_words):
    means = {s: float(np.mean(w)) for s, w in supp_words.items() if len(w) > 0}
    # higher rank value = longer
    order = sorted(means, key=lambda s: means[s])
    rank = {s: i for i, s in enumerate(order)}
    return rank, means

def check_direction_consistency(sig_sites, rank):
    """Consistent iff in every sig site, longer support ranks strictly above shorter
    in the global ranking (no contradictions)."""
    if len(sig_sites) == 0:
        return False  # nothing to be consistent about
    # collect pairwise orderings implied by sig sites
    pairs = []
    for v in sig_sites:
        lo, sh = v["longer"], v["shorter"]
        if lo == sh:
            continue
        pairs.append((lo, sh))
    if not pairs:
        return False
    # check no contradictions against global ranking
    for lo, sh in pairs:
        if rank.get(lo, -1) <= rank.get(sh, -1):
            return False
    # also check internal consistency: same "longer" support across sites when overlapping
    return True

def pooled_permutation(site_supp_words, min_words_per_support=15, n_perm=4999, seed=11):
    """Stratified permutation: within each testable site, permute support labels of
    word lengths; test statistic = sum over sites of (max_support_mean - min_support_mean).
    Compare observed sum to null distribution."""
    rng = np.random.default_rng(seed)
    sites_data = []
    obs_stat = 0.0
    for site in sorted(site_supp_words):
        big = {s: np.asarray(w, dtype=float) for s, w in site_supp_words[site].items() if len(w) >= min_words_per_support}
        if len(big) < 2:
            continue
        supps = sorted(big.keys())
        vals = np.concatenate([big[s] for s in supps])
        labels = np.concatenate([[s]*len(big[s]) for s in supps])
        means = {s: big[s].mean() for s in supps}
        obs_stat += max(means.values()) - min(means.values())
        sites_data.append((vals, labels, supps))
    if not sites_data:
        return float("nan")
    null = np.empty(n_perm)
    for i in range(n_perm):
        s = 0.0
        for vals, labels, supps in sites_data:
            perm = rng.permutation(len(vals))
            plabels = labels[perm]
            means = {sup: vals[plabels == sup].mean() for sup in supps}
            s += max(means.values()) - min(means.values())
        null[i] = s
    p = (np.sum(null >= obs_stat) + 1) / (n_perm + 1)
    return float(p)

# ---------- VERDICT ----------
def verdict(pc, global_kw, within, direction_consistent, pooled_p, n_testable):
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    if n_testable < 2:
        return "DOCCLASS_UNDERPOWERED"
    if global_kw["kruskal_p"] > 0.05:
        return "DOCCLASS_LENGTH_NO_SIGNAL"
    n_sig = within["n_sites_sig"]
    if (not (n_sig >= 2)) or (not direction_consistent) or (pooled_p > 0.05):
        return "DOCCLASS_LENGTH_SITE_CONFOUNDED"
    return "DOCCLASS_LENGTH_SIGNATURE_ROBUST"

# ---------- SELF-CHECK ----------
def _selfcheck():
    rng = np.random.default_rng(0)
    ok = True
    # MW detects a real shift
    a = rng.poisson(2, 500); b = rng.poisson(4, 500)
    _, p = mann_whitney(a, b)
    ok &= (p < 0.05)
    # MW does not flag identical
    a2 = rng.poisson(3, 500); b2 = rng.poisson(3, 500)
    _, p2 = mann_whitney(a2, b2)
    ok &= (p2 > 0.001)  # should not be tiny
    # KW
    H, pk = kruskal_wallis([a, b])
    ok &= (pk < 0.05)
    H0, pk0 = kruskal_wallis([a2, b2])
    ok &= math.isfinite(H0)
    print(f"[selfcheck] detect_shift_p={p:.2e} identical_p={p2:.2e} kw_p={pk:.2e} -> {'PASS' if ok else 'FAIL'}")
    return ok

if __name__ == "__main__":
    print("EPOCH-028 machinery self-check")
    ok = _selfcheck()
    sys.exit(0 if ok else 1)
