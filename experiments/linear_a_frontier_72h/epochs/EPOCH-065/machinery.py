"""
EPOCH-065 machinery: stratified site-register test for word-length (L2, structural).

word-length = len(word) (number of signs). document class = corpus 'support' field.
STRATIFIED null: permute SITE labels WITHIN each class (preserves class word-length
multiset AND each site's n-in-class). Tie-corrected Kruskal-Wallis H.

Self-check (__main__): validates tie-corrected KW + stratified permutation on a synthetic
with a planted residual site-register effect, and a class-only (no-residual) synthetic.
"""
import json
import math
import random
from collections import defaultdict


def kruskal_wallallis_tiecorrected(groups):
    """Tie-corrected Kruskal-Wallis H. groups: list of lists of values.
    Returns (H_corr, H_raw). NaN if degenerate."""
    allvals = []
    for g in groups:
        allvals.extend(g)
    N = len(allvals)
    if N == 0:
        return float('nan'), float('nan')
    # need >=2 non-empty groups and >=2 distinct values for meaningful H
    n_nonempty = sum(1 for g in groups if len(g) > 0)
    if n_nonempty < 2:
        return float('nan'), float('nan')
    # rank with average ranks for ties
    indexed = sorted(range(N), key=lambda i: allvals[i])
    ranks = [0.0] * N
    i = 0
    tie_term = 0.0
    while i < N:
        j = i
        while j + 1 < N and allvals[indexed[j + 1]] == allvals[indexed[i]]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        t = j - i + 1
        if t > 1:
            tie_term += (t ** 3 - t)
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    H_raw = 0.0
    idx = 0
    for g in groups:
        n_i = len(g)
        s = sum(ranks[idx:idx + n_i])
        H_raw += (s * s) / n_i
        idx += n_i
    H_raw = (12.0 / (N * (N + 1.0))) * H_raw - 3.0 * (N + 1.0)
    denom = (N ** 3 - N)
    C = 1.0 - (tie_term / denom) if denom != 0 else 1.0
    if C == 0:
        return float('nan'), float('nan')
    H_corr = H_raw / C
    return H_corr, H_raw


def perm_p_ge(obs, null_samples):
    """One-sided p = frac(null >= obs)."""
    null_samples = list(null_samples)
    if len(null_samples) == 0:
        return float('nan')
    ge = sum(1 for s in null_samples if s >= obs - 1e-9)
    return ge / len(null_samples)


def stratified_perm_test(class_site_words, n_draws=1000, seed=12345):
    """class_site_words: {class: {site: [wordlengths]}} restricted to ELIGIBLE sites.
    Returns per-class obs_H, per-class perm_p, combined obs_sum, combined perm_p."""
    rng = random.Random(seed)
    classes = sorted(class_site_words.keys())

    # observed
    obs_H = {}
    for c in classes:
        sites = sorted(class_site_words[c].keys())
        groups = [class_site_words[c][s] for s in sites]
        Hc, _ = kruskal_wallallis_tiecorrected(groups)
        obs_H[c] = Hc
    obs_sum = sum(obs_H[c] for c in classes)

    # per-class null distributions + combined null distribution
    null_per_class = {c: [] for c in classes}
    null_combined = []
    # precompute per-class pooled layout: pooled word-lengths + site sizes
    class_layout = {}
    for c in classes:
        sites = sorted(class_site_words[c].keys())
        pooled = []
        sizes = []
        for s in sites:
            pooled.extend(class_site_words[c][s])
            sizes.append(len(class_site_words[c][s]))
        class_layout[c] = (pooled, sizes)

    for _ in range(n_draws):
        draw_sum = 0.0
        for c in classes:
            pooled, sizes = class_layout[c]
            perm = list(pooled)
            rng.shuffle(perm)
            # carve into groups of given sizes
            groups = []
            idx = 0
            for sz in sizes:
                groups.append(perm[idx:idx + sz])
                idx += sz
            Hc, _ = kruskal_wallallis_tiecorrected(groups)
            null_per_class[c].append(Hc)
            if not math.isnan(Hc):
                draw_sum += Hc
        null_combined.append(draw_sum)

    per_class_p = {}
    for c in classes:
        per_class_p[c] = perm_p_ge(obs_H[c], null_per_class[c])
    combined_p = perm_p_ge(obs_sum, null_combined)
    return {
        'obs_H': obs_H,
        'per_class_p': per_class_p,
        'obs_sum': obs_sum,
        'combined_p': combined_p,
    }


def raw_site_perm_test(site_words, n_draws=1000, seed=99999):
    """Uncontrolled site KW over all words (ignore class). site_words: {site: [wls]}."""
    rng = random.Random(seed)
    sites = sorted(site_words.keys())
    groups = [site_words[s] for s in sites]
    Hc, _ = kruskal_wallallis_tiecorrected(groups)
    pooled = []
    sizes = []
    for s in sites:
        pooled.extend(site_words[s])
        sizes.append(len(site_words[s]))
    null_H = []
    for _ in range(n_draws):
        perm = list(pooled)
        rng.shuffle(perm)
        g = []
        idx = 0
        for sz in sizes:
            g.append(perm[idx:idx + sz])
            idx += sz
        Hc2, _ = kruskal_wallallis_tiecorrected(g)
        null_H.append(Hc2)
    p = perm_p_ge(Hc, null_H)
    return Hc, p


def load_corpus(path):
    return json.load(open(path))


def build_class_site_words(data):
    cs = defaultdict(lambda: defaultdict(list))
    for x in data:
        cls = x['support']
        site = x['site']
        if not site or not cls:
            continue
        for w in x['words']:
            cs[cls][site].append(len(w))
    return cs


def eligible_testable(class_site_words, min_words=30, min_sites=2):
    """Return {class: {site: [wls]}} restricted to sites with >=min_words, classes with
    >=min_sites such sites."""
    out = {}
    for cls, sites in class_site_words.items():
        elig = {s: wl for s, wl in sites.items() if len(wl) >= min_words}
        if len(elig) >= min_sites:
            out[cls] = elig
    return out


# ---------------- POSITIVE CONTROL SYNTHETICS ----------------

def synth_detect(min_words=30, seed=4242):
    """Plant a residual SITE-REGISTER effect: one site's word-lengths shifted +1 within
    a class, holding class distributions otherwise equal. Two sites in one class."""
    rng = random.Random(seed)
    # base word-length pool (small integers, heavy ties, like real data)
    base = [rng.choice([1, 1, 1, 2, 2, 2, 3, 3]) for _ in range(2 * min_words + 20)]
    half = len(base) // 2
    siteA = list(base[:half])
    siteB = list(base[half:])
    # PLANT residual site effect: shift siteB by +1
    siteB = [v + 1 for v in siteB]
    return {'SYNTH_CLASS': {'SiteA': siteA, 'SiteB': siteB}}


def synth_falsepos(min_words=30, seed=7777, n_classes=3):
    """Class-only data: word-lengths depend ONLY on class; site labels random within class.
    No residual site effect. Multiple classes each with 2 sites."""
    rng = random.Random(seed)
    out = {}
    class_pools = {
        'C_short': [1, 1, 1, 2, 2],
        'C_mid': [2, 2, 3, 3, 3],
        'C_long': [3, 3, 4, 4, 4],
    }
    keys = list(class_pools.keys())[:n_classes]
    for k in keys:
        pool = class_pools[k]
        total = 2 * min_words + 10
        vals = [rng.choice(pool) for _ in range(total)]
        half = len(vals) // 2
        out[k] = {'SiteX': list(vals[:half]), 'SiteY': list(vals[half:])}
    return out


def _self_check():
    """Validate tie-corrected KW + stratified permutation on synthetics."""
    results = {}

    # (a) DETECT: planted residual site effect should be flagged
    synth = synth_detect()
    res = stratified_perm_test(synth, n_draws=500, seed=101)
    detect_p = res['combined_p']
    results['detect_combined_p'] = detect_p
    results['detect_flags'] = detect_p <= 0.05

    # (b) FALSE-POSITIVE: class-only data should NOT be flagged across >=20 draws
    rejections = 0
    n_draws_trials = 20
    for t in range(n_draws_trials):
        synth = synth_falsepos(seed=1000 + t)
        res = stratified_perm_test(synth, n_draws=300, seed=2000 + t)
        if res['combined_p'] <= 0.05:
            rejections += 1
    fpr = rejections / n_draws_trials
    results['false_pos_rate'] = fpr
    results['false_pos_ok'] = fpr <= 0.10

    # sanity: KW on identical groups -> H ~ 0
    Hc, _ = kruskal_wallallis_tiecorrected([[1, 2, 3, 2, 1], [1, 2, 3, 2, 1], [1, 2, 3, 2, 1]])
    results['identical_H_near0'] = Hc < 0.5

    # sanity: KW on perfectly separated groups -> large H
    Hc2, _ = kruskal_wallallis_tiecorrected([[1, 1, 1, 1, 1], [5, 5, 5, 5, 5], [9, 9, 9, 9, 9]])
    results['separated_H_large'] = Hc2 > 5.0

    passed = (results['detect_flags'] and results['false_pos_ok']
              and results['identical_H_near0'] and results['separated_H_large'])
    results['pc_passed'] = passed
    return results


if __name__ == '__main__':
    print("=== EPOCH-065 machinery self-check ===")
    r = _self_check()
    for k, v in r.items():
        print(f"  {k}: {v}")
    print(f"\nPC PASSED: {r['pc_passed']}")
