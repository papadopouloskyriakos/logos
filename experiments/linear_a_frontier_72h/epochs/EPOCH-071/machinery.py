"""
EPOCH-071 machinery: cross-site word-form recurrence (S statistic) with a
token->site reassignment null that preserves BOTH each word-form's total count
AND each site's total token count (so any cross-site recurrence is BEYOND
frequency + site-size).

L2/L3 ONLY. Anonymous word-forms = sign tuples, len>=2. NO reading, NO phonetic
value, NO meaning. Genre = the physical 'support' field (given).

Frozen metric:
    S = sum over multi-sign word-TYPES of max(0, n_distinct_sites - 1)

Frozen null (per corpus):
    Reassign word-TOKENS to sites preserving BOTH marginals exactly:
      - each word-form keeps its total count
      - each site keeps its total token count
    Implemented as a sequential hypergeometric sample of the r x c contingency
    table with fixed margins (exact marginal-preserving; equivalent in
    distribution to Patefield/AS159). This breaks the form<->site association
    but keeps both marginals, so any cross-site recurrence in S is BEYOND
    word-form frequency + per-site token totals.

    perm p = frac(null S >= observed S), one-sided, >=1000 draws.
"""

import json
import random
from collections import Counter, defaultdict

import numpy as np


# ---------- data extraction ----------

def tokens_of(insc):
    """Return list of anonymous word-forms (sign tuples) with len>=2."""
    toks = []
    for w in insc.get("words", []):
        if isinstance(w, list):
            signs = tuple(w)
        elif isinstance(w, dict):
            signs = tuple(w.get("signs", []))
        else:
            continue
        if len(signs) >= 2:
            toks.append(signs)
    return toks


def corpus_summary(inscs):
    """Build per-site token counts, form->sites, form->count."""
    site_tokens = Counter()
    form_sites = defaultdict(set)
    form_count = Counter()
    for x in inscs:
        s = x["site"]
        for tok in tokens_of(x):
            site_tokens[s] += 1
            form_sites[tok].add(s)
            form_count[tok] += 1
    return site_tokens, form_sites, form_count


def S_stat(form_sites):
    """S = sum over forms of max(0, n_distinct_sites - 1)."""
    return float(sum(max(0, len(sites) - 1) for sites in form_sites.values()))


# ---------- reassignment null (marginal-preserving) ----------

def _sample_table(rows, cols, rng):
    """
    Sample an r x c nonnegative integer table with the given row and column
    totals, via sequential hypergeometric sampling (exact marginal-preserving).

    Invariant (guaranteed by margin consistency sum(rows)==sum(cols)): when we
    start row i, sum(jwork) == sum(rows[i:]). So row_left <= sum(jwork) always.
    For columns 0..nc-2 of a non-last row we draw hypergeometrically; the LAST
    column of the row absorbs the row remainder (which is <= its remaining
    mass by the invariant). The last row absorbs all column remainders.

    Returns numpy int array shape (len(rows), len(cols)).
    """
    nr = len(rows)
    nc = len(cols)
    tab = np.zeros((nr, nc), dtype=np.int64)
    jwork = [int(x) for x in cols]
    for i in range(nr):
        row_left = int(rows[i])
        if i == nr - 1:
            for j in range(nc):
                tab[i, j] = jwork[j]
                jwork[j] = 0
            break
        if row_left == 0:
            continue
        for j in range(nc):
            if j == nc - 1:
                # last column absorbs the row remainder
                tab[i, j] = row_left
                jwork[j] -= row_left
                row_left = 0
                break
            if row_left <= 0:
                break
            if jwork[j] <= 0:
                continue
            M = sum(jwork)              # remaining column mass == sum(rows[i:])
            good = jwork[j]
            bad = M - good
            if bad < 0:
                bad = 0
            draws = row_left if row_left <= M else M
            k = rng.hypergeometric(good, bad, draws)
            k = int(max(0, min(k, good, row_left)))
            tab[i, j] = k
            jwork[j] -= k
            row_left -= k
        # row complete
    return tab


def null_distribution(form_count, site_tokens, observed_S, n_draws=2000, seed=71071):
    """Return (null_mean, perm_p, list_of_S)."""
    rng = np.random.default_rng(seed)
    ge = 0
    Ss = []
    forms = list(form_count.keys())
    sites = list(site_tokens.keys())
    r = [form_count[f] for f in forms]
    c = [site_tokens[s] for s in sites]
    nform = len(forms)
    for _ in range(n_draws):
        tab = _sample_table(r, c, rng)
        s = 0.0
        for i in range(nform):
            nz = int(np.count_nonzero(tab[i, :]))
            if nz > 1:
                s += (nz - 1)
        Ss.append(s)
        if s >= observed_S:
            ge += 1
    mean = sum(Ss) / len(Ss)
    perm_p = (ge + 1) / (n_draws + 1)
    return mean, perm_p, Ss


# ---------- self-check ----------

def _self_check():
    rng = np.random.default_rng(12345)
    form_count = {("A",): 10, ("B",): 6, ("C",): 4}
    site_tokens = {"S1": 8, "S2": 7, "S3": 5}
    assert sum(form_count.values()) == sum(site_tokens.values())
    r = [form_count[f] for f in form_count]
    c = [site_tokens[s] for s in site_tokens]
    margin_ok = True
    for _ in range(2000):
        tab = _sample_table(r, c, rng)
        if list(tab.sum(axis=1)) != r or list(tab.sum(axis=0)) != c:
            margin_ok = False
            print("FAIL draw:"); print(tab)
            break
    assert margin_ok, "NULL MARGIN PRESERVATION FAILED"
    print("[self-check] reassignment null preserves both marginals exactly: OK")

    # bigger random margin test
    ok2 = True
    for trial in range(200):
        rr = [int(x) for x in rng.integers(1, 15, size=4)]
        cc = [int(x) for x in rng.integers(1, 15, size=5)]
        # adjust to match totals
        diff = sum(rr) - sum(cc)
        cc[0] = max(1, cc[0] + diff)
        if sum(rr) != sum(cc):
            continue
        for _ in range(20):
            tab = _sample_table(rr, cc, rng)
            if list(tab.sum(axis=1)) != rr or list(tab.sum(axis=0)) != cc:
                ok2 = False
                break
        if not ok2:
            break
    assert ok2, "RANDOM MARGIN TEST FAILED"
    print("[self-check] random-margin preservation: OK")

    fs = {("X",): {"a", "b", "c"}, ("Y",): {"a"}, ("Z",): {"a", "b"}}
    assert S_stat(fs) == (2 + 0 + 1)
    print("[self-check] S_stat correct: OK")

    # planted formula -> enriched S.
    # Design matches real-corpus structure: a few formula forms (count = n_sites,
    # one token per site, at ALL sites) plus singleton filler. A genuine
    # cross-site formula is a fixed sequence appearing once at many sites,
    # which frequency+site-size alone cannot produce. (A high-count form spread
    # across sites is NOT a formula beyond frequency, since the null also
    # spreads it; the detect signal requires low-count-per-site, all-site
    # recurrence.)
    n_sites = 5
    site_size = 25
    n_formula = 5
    fc_formula = {}
    fs_obs = {}
    st_formula = {s: 0 for s in range(n_sites)}
    for k in range(n_formula):
        f = ("F", k)
        fc_formula[f] = n_sites          # one token per site
        fs_obs[f] = set(range(n_sites))
        for s in range(n_sites):
            st_formula[s] += 1
    sid = 0
    for s in range(n_sites):
        # add a few singletons per site, then pad to site_size
        for _ in range(4):
            f = ("S", sid); sid += 1
            fc_formula[f] = 1; fs_obs[f] = {s}; st_formula[s] += 1
        while st_formula[s] < site_size:
            f = ("S", sid); sid += 1
            fc_formula[f] = 1; fs_obs[f] = {s}; st_formula[s] += 1
    S_formula = S_stat(fs_obs)
    mean_f, p_f, _ = null_distribution(fc_formula, st_formula, S_formula, n_draws=500, seed=99)
    print(f"[self-check] planted formula: S_obs={S_formula}, null_mean={mean_f:.2f}, p={p_f:.4f}")
    assert p_f <= 0.05, "PC detect failed in self-check"

    # frequency-only (site-local) -> NOT enriched.
    # Each form's tokens assigned to sites proportional to site size (pure
    # frequency-driven overlap, no real formula).
    fc_freq = {}
    fs_obs2 = {}
    st_freq = {s: 0 for s in range(n_sites)}
    site_p = np.array([site_size] * n_sites, dtype=float)
    site_p = site_p / site_p.sum()
    for k in range(20):
        f = ("L", k)
        c = 4
        fc_freq[f] = c
        sites_used = set()
        for _ in range(c):
            s = int(rng.choice(n_sites, p=site_p))
            sites_used.add(s)
            st_freq[s] += 1          # one token per draw -> margins stay consistent
        fs_obs2[f] = sites_used
    sid = 0
    for s in range(n_sites):
        while st_freq[s] < site_size:
            f = ("S", sid); sid += 1
            fc_freq[f] = 1; fs_obs2[f] = {s}; st_freq[s] += 1
    S_freq = S_stat(fs_obs2)
    mean_fr, p_fr, _ = null_distribution(fc_freq, st_freq, S_freq, n_draws=500, seed=88)
    print(f"[self-check] frequency-only/site-local: S_obs={S_freq}, null_mean={mean_fr:.2f}, p={p_fr:.4f}")
    assert p_fr > 0.05, "PC false-positive fired in self-check"
    print("[self-check] ALL OK")


if __name__ == "__main__":
    _self_check()
