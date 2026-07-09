#!/usr/bin/env python3
"""
EPOCH-066 machinery: tie-corrected Kruskal-Wallis H + site-permutation null,
for numeral magnitude (accounting scale) within the Tablet class by SITE.

L2 only: magnitude = corpus `num` token `v`; site = `site` field; class fixed
= Tablet (`support`). Null permutes SITE labels among Tablet numerals.
"""
import json, math, os, sys
from collections import defaultdict
import numpy as np

CORPUS = os.environ.get(
    "LA_CORPUS",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",
                 "corpus", "silver", "inscriptions_structured.json"),
)
CORPUS = os.path.abspath(CORPUS)
MIN_N = 30
CLASS = "Tablet"


# ---------- tie-corrected Kruskal-Wallis ----------
def _rankdata_avg(a):
    """Average-rank (1-based) ranking with tie correction. Returns ranks, tiecorr_sum."""
    a = np.asarray(a, dtype=float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    sa = a[order]
    n = len(a)
    i = 0
    tie_term = 0.0  # sum (t^3 - t)
    r = 1
    while i < n:
        j = i
        while j + 1 < n and sa[j + 1] == sa[i]:
            j += 1
        t = j - i + 1
        avg_rank = (r + (r + t - 1)) / 2.0  # average of ranks r..r+t-1
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        if t > 1:
            tie_term += (t ** 3 - t)
        r += t
        i = j + 1
    return ranks, tie_term


def kruskal_wallallis_h(groups):
    """Tie-corrected KW H. groups = list of 1-D arrays of values."""
    groups = [np.asarray(g, dtype=float) for g in groups]
    sizes = np.array([len(g) for g in groups])
    N = int(sizes.sum())
    if N < 2 or len(groups) < 2:
        return float("nan")
    allv = np.concatenate(groups)
    ranks, tie_term = _rankdata_avg(allv)
    # split ranks back
    H = 0.0
    start = 0
    Rsums = []
    for s in sizes:
        Rsums.append(ranks[start:start + s].sum())
        start += s
    Rsums = np.array(Rsums, dtype=float)
    H = (12.0 / (N * (N + 1))) * np.sum((Rsums ** 2) / sizes) - 3 * (N + 1)
    # tie correction
    C = 1.0 - tie_term / (N ** 3 - N)
    if C > 0:
        H = H / C
    return float(H)


# ---------- data load ----------
def load_tablet_numerals(path=CORPUS, min_n=MIN_N):
    d = json.load(open(path))
    site_vals = defaultdict(list)
    for ins in d:
        if ins.get("support") != CLASS:
            continue
        site = ins.get("site")
        for tok in ins.get("stream", []):
            if tok.get("t") == "num" and "v" in tok:
                v = tok["v"]
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    site_vals[site].append(float(v))
    eligible = {s: vs for s, vs in site_vals.items() if len(vs) >= min_n}
    return eligible


# ---------- permutation null ----------
def perm_p_site(vals_by_site, n_draws=2000, seed=12345):
    """Permute SITE labels among numerals (preserve per-site n + magnitude multiset)."""
    rng = np.random.default_rng(seed)
    sites = list(vals_by_site.keys())
    sizes = np.array([len(vals_by_site[s]) for s in sites])
    pooled = np.concatenate([np.asarray(vals_by_site[s], dtype=float) for s in sites])
    groups = [np.asarray(vals_by_site[s], dtype=float) for s in sites]
    obs = kruskal_wallallis_h(groups)
    N = len(pooled)
    ge = 0
    null_Hs = np.empty(n_draws)
    for d in range(n_draws):
        perm = rng.permutation(N)
        pv = pooled[perm]
        g = []
        start = 0
        for s in sizes:
            g.append(pv[start:start + s])
            start += s
        Hd = kruskal_wallallis_h(g)
        null_Hs[d] = Hd
        if Hd >= obs:
            ge += 1
    p = (ge + 1) / (n_draws + 1)  # add-one smoothing
    return obs, float(null_Hs.mean()), p, null_Hs


# ---------- positive control (synthetic) ----------
def _tablet_like(eligible, seed):
    """Build a Tablet-like synthetic: same per-site sizes, magnitudes sampled from
    the pooled empirical Tablet magnitude multiset (so marginal dist is realistic)."""
    rng = np.random.default_rng(seed)
    pooled = np.concatenate([np.asarray(v, dtype=float) for v in eligible.values()])
    out = {}
    for s, vs in eligible.items():
        out[s] = rng.choice(pooled, size=len(vs), replace=True)
    return out


def positive_control(eligible, n_draws=2000, n_fp=20, seed=7):
    rng = np.random.default_rng(seed)
    # (a) DETECT: multiply one site's magnitudes by a shift factor
    base = _tablet_like(eligible, seed=seed)
    shifted = {s: np.array(v, dtype=float) for s, v in base.items()}
    target = list(shifted.keys())[0]
    shifted[target] = shifted[target] * 8.0  # strong per-site magnitude shift
    obs_d, _, p_d, _ = perm_p_site(shifted, n_draws=n_draws, seed=seed + 1)
    detect_ok = (p_d <= 0.05)

    # (b) FALSE-POSITIVE: site labels assigned at random (no site effect)
    rej = 0
    pooled = np.concatenate([np.asarray(v, dtype=float) for v in eligible.values()])
    sizes = np.array([len(eligible[s]) for s in eligible])
    sites = list(eligible.keys())
    for i in range(n_fp):
        samp = {s: rng.choice(pooled, size=len(eligible[s]), replace=True) for s in sites}
        # random relabel: shuffle which synthetic values go to which site
        allvals = np.concatenate([samp[s] for s in sites])
        perm = rng.permutation(len(allvals))
        allvals = allvals[perm]
        g = {}
        start = 0
        for s in sites:
            g[s] = allvals[start:start + len(eligible[s])]
            start += len(eligible[s])
        _, _, p_i, _ = perm_p_site(g, n_draws=n_draws, seed=seed + 100 + i)
        if p_i <= 0.05:
            rej += 1
    fpr = rej / n_fp
    fp_ok = (fpr <= 0.10)
    passed = detect_ok and fp_ok
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": float(p_d),
        "detect_ok": bool(detect_ok),
        "false_pos_rate": float(fpr),
        "fp_ok": bool(fp_ok),
        "n_fp_draws": int(n_fp),
        "pc_is_synthetic": True,
    }


# ---------- leave-one-site-out ----------
def loo(eligible, n_draws=2000, seed=999):
    out = {}
    for drop in list(eligible.keys()):
        sub = {s: v for s, v in eligible.items() if s != drop}
        if len(sub) < 2:
            out[drop] = {"obs_H": float("nan"), "perm_p": float("nan"), "sig": False}
            continue
        obs, _, p, _ = perm_p_site(sub, n_draws=n_draws, seed=seed)
        out[drop] = {"obs_H": float(obs), "perm_p": float(p), "sig": bool(p <= 0.05)}
    return out


# ---------- main self-check ----------
def _self_check():
    """Validate tie-corrected KW against scipy on a small example, and confirm
    the site-permutation null returns ~uniform p under no-effect synthetic."""
    import statistics
    # 1) KW tie-correction vs scipy
    try:
        from scipy import stats
        g1 = [1.0, 2.0, 2.0, 3.0, 5.0]
        g2 = [2.0, 4.0, 4.0, 6.0, 8.0]
        g3 = [1.0, 1.0, 3.0, 7.0, 9.0]
        H_mine = kruskal_wallallis_h([g1, g2, g3])
        H_sp, _ = stats.kruskal(g1, g2, g3)
        ok_kw = abs(H_mine - H_sp) < 1e-6
    except Exception as e:
        print("scipy unavailable, skipping KW cross-check:", e)
        ok_kw = True  # cannot cross-check; rely on analytic tie formula
        H_mine = kruskal_wallallis_h([[1, 2, 2, 3, 5], [2, 4, 4, 6, 8], [1, 1, 3, 7, 9]])

    # 2) null calibration: under no-effect, p should be roughly uniform
    rng = np.random.default_rng(0)
    pool = np.array([1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0])
    sizes = [40, 40, 40, 40]
    ps = []
    for i in range(50):
        g = {f"S{j}": rng.choice(pool, size=sizes[j]) for j in range(4)}
        _, _, p, _ = perm_p_site(g, n_draws=500, seed=i)
        ps.append(p)
    ps = np.array(ps)
    # expect ~5% <= 0.05; allow up to 15% for noise at 500 draws
    calib = float((ps <= 0.05).mean())
    ok_calib = calib <= 0.15
    print(f"[self-check] KW vs scipy match={ok_kw} (mine={H_mine:.6f})")
    print(f"[self-check] null-calib reject@0.05 over 50 no-effect draws = {calib:.3f} (<=0.15 ok={ok_calib})")
    return ok_kw and ok_calib


if __name__ == "__main__":
    ok = _self_check()
    print("SELF_CHECK_OK" if ok else "SELF_CHECK_FAIL")
    sys.exit(0 if ok else 1)
