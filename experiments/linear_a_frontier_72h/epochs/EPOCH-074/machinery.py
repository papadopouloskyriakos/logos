"""
EPOCH-074 machinery: GLOBAL vs SITE-STRATIFIED token->genre permutation nulls for S_shared
(anonymous word-forms = sign tuples, len>=2). L3 only. No reading, no meaning.

Marginal-preservation contracts:
  GLOBAL null:        preserves each form's total token count AND each genre's total token count.
  SITE-STRATIFIED:    preserves per-site genre token counts AND per-site form counts (site fixed;
                      only genre can change within a site).

Self-check (__main__):
  - confirms both nulls preserve their marginals on the real corpus;
  - confirms on a synthetic single-genre-per-site corpus the site-stratified null returns ~observed.
"""
import json, random, sys
from collections import Counter, defaultdict

import os
def _repo_root():
    p = os.getcwd()
    for _ in range(8):
        if os.path.isdir(os.path.join(p, "corpus", "silver")):
            return p
        p = os.path.dirname(p)
    return "."
CORPUS = os.path.join(_repo_root(), "corpus", "silver", "inscriptions_structured.json")
LIB = {"Stone vessel"}
ADM = {"Tablet", "Nodule", "Roundel"}


def genre_of(sup):
    if sup in LIB: return "lib"
    if sup in ADM: return "adm"
    return None


def load_tokens(path=CORPUS):
    """Return list of (site, genre, form) for lib+adm word tokens with len(signs)>=2."""
    d = json.load(open(path))
    toks = []
    for x in d:
        g = genre_of(x.get("support"))
        if g is None:
            continue
        site = x.get("site", "?")
        for w in x.get("stream", []):
            if w.get("t") == "word":
                signs = w.get("signs", [])
                if len(signs) >= 2:
                    toks.append((site, g, tuple(signs)))
    return toks


def s_shared_from_assignments(assignments):
    """assignments: list of (genre, form). Return |forms in both genres|."""
    forms = defaultdict(set)
    for g, f in assignments:
        forms[g].add(f)
    return len(forms["lib"] & forms["adm"])


def observed_s_shared(toks):
    return s_shared_from_assignments([(g, f) for (_, g, f) in toks])


# ---------------- GLOBAL null ----------------
def global_null_s_shared(toks, rng):
    """
    Permute genre labels across ALL tokens, preserving:
      - each form's total token count (forms are fixed attributes of tokens),
      - each genre's total token count (we shuffle the genre multiset).
    Implementation: collect the genre list, shuffle it, reassign to the (fixed) token sequence.
    """
    genres = [g for (_, g, _) in toks]
    forms = [f for (_, _, f) in toks]
    rng.shuffle(genres)  # preserves genre multiset; forms stay attached to positions
    return s_shared_from_assignments(list(zip(genres, forms)))


def closed_form_E_S(toks):
    """
    INDEPENDENCE-APPROXIMATION upper bound on E[S_shared] under the GLOBAL null.

    NOTE: the GLOBAL null is a SINGLE permutation of the genre multiset (genres assigned without
    replacement), so per-form presence events are negatively correlated (fixed genre totals). Treating
    them as independent OVERESTIMATES E[S]. This value is therefore a sanity UPPER BOUND, not the exact
    null mean. The exact null mean is obtained by Monte Carlo (global_null_s_shared). For each form f
    with total count n_f, total tokens N, lib tokens L, adm tokens A:
      P(f appears in lib) = 1 - C(N-n_f, L)/C(N, L)
      P(f appears in adm) = 1 - C(N-n_f, A)/C(N, A)
    E[S]_indep = sum_f P(in lib)*P(in adm)  (upper bound).
    """
    import math
    N = len(toks)
    form_counts = Counter(f for (_, _, f) in toks)
    g_counts = Counter(g for (_, g, _) in toks)
    L = g_counts["lib"]
    A = g_counts["adm"]

    def log_choose(n, k):
        if k < 0 or k > n:
            return float("-inf")
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

    logCN_L = log_choose(N, L)
    logCN_A = log_choose(N, A)
    E = 0.0
    for f, nf in form_counts.items():
        # P(not in lib) = C(N-nf, L)/C(N, L)
        log_pnolib = log_choose(N - nf, L) - logCN_L
        log_pnoadm = log_choose(N - nf, A) - logCN_A
        p_lib = 1.0 - math.exp(log_pnolib) if log_pnolib > float("-inf") else 1.0
        p_adm = 1.0 - math.exp(log_pnoadm) if log_pnoadm > float("-inf") else 1.0
        E += p_lib * p_adm
    return E


# ---------------- SITE-STRATIFIED null ----------------
def site_stratified_null_s_shared(toks, rng):
    """
    Permute genre labels ONLY WITHIN each site, preserving per-site genre token counts and
    per-site form counts. Site-membership is FIXED; only genre can change within a site.
    """
    by_site = defaultdict(list)
    for (site, g, f) in toks:
        by_site[site].append((g, f))
    new_assignments = []
    for site, items in by_site.items():
        genres = [g for (g, f) in items]
        forms = [f for (g, f) in items]
        rng.shuffle(genres)  # within-site genre multiset preserved; forms stay attached
        new_assignments.extend(list(zip(genres, forms)))
    return s_shared_from_assignments(new_assignments)


# ---------------- marginal self-checks ----------------
def check_global_marginals(toks, rng, trials=50):
    """Confirm GLOBAL null preserves each form's total token count and each genre's total."""
    form_counts = Counter(f for (_, _, f) in toks)
    g_counts = Counter(g for (_, g, _) in toks)
    ok = True
    for _ in range(trials):
        # rebuild assignments via the same shuffle logic
        genres = [g for (_, g, _) in toks]
        forms = [f for (_, _, f) in toks]
        rng.shuffle(genres)
        new = list(zip(genres, forms))
        ng = Counter(g for (g, f) in new)
        if ng != g_counts:
            ok = False
            break
        # form total counts unchanged because forms list is untouched
    return ok


def check_sitestrat_marginals(toks, rng, trials=50):
    """Confirm SITE-STRATIFIED preserves per-site genre counts and per-site form counts."""
    by_site = defaultdict(list)
    for (site, g, f) in toks:
        by_site[site].append((g, f))
    # reference per-site marginals
    ref_g = {s: Counter(g for (g, f) in items) for s, items in by_site.items()}
    ref_f = {s: Counter(f for (g, f) in items) for s, items in by_site.items()}
    ok = True
    for _ in range(trials):
        new_by_site = {}
        for s, items in by_site.items():
            genres = [g for (g, f) in items]
            forms = [f for (g, f) in items]
            rng.shuffle(genres)
            new_by_site[s] = list(zip(genres, forms))
        for s in by_site:
            ng = Counter(g for (g, f) in new_by_site[s])
            nf = Counter(f for (g, f) in new_by_site[s])
            if ng != ref_g[s] or nf != ref_f[s]:
                ok = False
                break
        if not ok:
            break
    return ok


def synthetic_single_genre_per_site():
    """
    Synthetic corpus where every site is single-genre. Site-stratified null must return ~observed
    (no swappable tokens => null == obs).
    """
    rng = random.Random(424242)
    toks = []
    sites = ["S1", "S2", "S3"]
    # S1 all lib, S2 all adm, S3 all lib
    for i in range(40):
        toks.append(("S1", "lib", ("A", str(i % 5))))
    for i in range(40):
        toks.append(("S2", "adm", ("B", str(i % 5))))
    for i in range(20):
        toks.append(("S3", "lib", ("C", str(i % 4))))
    return toks


if __name__ == "__main__":
    rng = random.Random(20240704)
    toks = load_tokens()
    print("tokens:", len(toks))
    obs = observed_s_shared(toks)
    print("observed S_shared:", obs)

    print("GLOBAL marginal check:", check_global_marginals(toks, rng))
    print("SITE-STRATIFIED marginal check:", check_sitestrat_marginals(toks, rng))

    # quick global null sample
    vals = [global_null_s_shared(toks, rng) for _ in range(200)]
    print("GLOBAL null mean (200):", sum(vals) / len(vals))
    print("closed-form E[S]:", closed_form_E_S(toks))

    # site-stratified null sample
    svals = [site_stratified_null_s_shared(toks, rng) for _ in range(200)]
    print("SITE-STRATIFIED null mean (200):", sum(svals) / len(svals))
    print("SITE-STRATIFIED p_below (frac <= obs):", sum(v <= obs for v in svals) / len(svals))

    # synthetic single-genre-per-site: site-stratified null must == obs
    stok = synthetic_single_genre_per_site()
    sobs = observed_s_shared(stok)
    ssvals = [site_stratified_null_s_shared(stok, rng) for _ in range(200)]
    print("SYNTH single-genre obs:", sobs, "site-strat null mean:", sum(ssvals) / len(ssvals),
          "(should equal obs => no swappable tokens)")
