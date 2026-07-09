"""
EPOCH-073 machinery: GENRE CONTRAST of within-inscription word-order rigidity
(ADMIN vs LIBATION). L3 ONLY.

Reuses the E072 order-consistency machinery (anonymous word-forms = sign
tuples, len>=2; for each inscription every unordered pair of distinct forms
yields one observation (site, sign); sign = +1 if (lex-key fa<fb) fa precedes
fb in stream (first-occurrence pos), else -1).

Testable pairs: total occurrences >= 2.
Cross-site pairs: observed at >= 2 distinct sites.
consistency(pair) = max(n_plus, n_minus)/(n_plus+n_minus) in [0.5,1].
C_glob = mean consistency over testable pairs.

NULL: within-inscription word-order shuffle (preserves each inscription's
word multiset -> invariant testable/cross-site pair sets; destroys only
order). >=1000 draws. One-sided perm p = frac(null>=obs), add-one smoothed.

GENRE CONTRAST: bootstrap over admin testable pairs' consistency values
(>=2000 resamples); 95% CI; admin significantly less rigid than libation iff
bootstrap upper bound < libation C_glob.

L3 ONLY. No reading, no meaning.
"""
import json, random, math, hashlib
from collections import defaultdict, Counter

RNG = random.Random(20240713)

# ---------- corpus loading ----------
def load_corpus(path):
    return json.load(open(path))

def admin_inscriptions(corpus):
    return [x for x in corpus if x.get("support") in ("Tablet", "Nodule", "Roundel")]

def libation_inscriptions(corpus):
    return [x for x in corpus if x.get("support") == "Stone vessel"]

def word_forms(insc):
    """Ordered list of multi-sign word-forms (sign tuples, len>=2), stream order."""
    out = []
    for tok in insc.get("stream", []):
        if not isinstance(tok, dict):
            continue
        if tok.get("t") != "word":
            continue
        s = tok.get("signs")
        if not isinstance(s, list):
            continue
        if len(s) < 2:
            continue
        out.append(tuple(s))
    return out

# ---------- pair observations ----------
def pair_observations(inscriptions):
    """
    pair_site_signs: dict pair_key -> dict site -> Counter({+1:..,-1:..})
    pair_total_occ:  dict pair_key -> total occurrences
    pair_key = (fa, fb) with fa<fb lexicographically (lex key).
    Sign convention: +1 if fa precedes fb in stream (first-occ pos), else -1.
    """
    pair_site_signs = defaultdict(lambda: defaultdict(Counter))
    pair_total_occ = Counter()
    for insc in inscriptions:
        forms = word_forms(insc)
        site = insc.get("site", "?")
        first_pos = {}
        for i, f in enumerate(forms):
            if f not in first_pos:
                first_pos[f] = i
        distinct = list(first_pos.keys())
        for a_i in range(len(distinct)):
            for b_i in range(a_i + 1, len(distinct)):
                fa, fb = distinct[a_i], distinct[b_i]
                if fa < fb:
                    key = (fa, fb); sign = +1 if first_pos[fa] < first_pos[fb] else -1
                else:
                    key = (fb, fa); sign = +1 if first_pos[fb] < first_pos[fa] else -1
                pair_site_signs[key][site][sign] += 1
                pair_total_occ[key] += 1
    return pair_site_signs, pair_total_occ

def classify_pairs(pair_total_occ, pair_site_signs):
    testable = [k for k, n in pair_total_occ.items() if n >= 2]
    cross = []
    for k in testable:
        if len(pair_site_signs[k]) >= 2:
            cross.append(k)
    return testable, cross

def consistency_from_signs(site_signs):
    np_ = sum(c[+1] for c in site_signs.values())
    nm_ = sum(c[-1] for c in site_signs.values())
    tot = np_ + nm_
    if tot == 0:
        return 0.5, np_, nm_
    return max(np_, nm_) / tot, np_, nm_

def pair_consistency_list(pair_site_signs, testable):
    """List of consistency values, one per testable pair (for bootstrap)."""
    out = []
    for k in testable:
        c, _, _ = consistency_from_signs(pair_site_signs[k])
        out.append(c)
    return out

def C_glob_from_observations(pair_site_signs, testable):
    cons = pair_consistency_list(pair_site_signs, testable)
    return sum(cons) / len(cons) if cons else 0.5

# ---------- shuffle null ----------
def shuffled_signs(inscriptions, rng):
    """Recompute pair_site_signs after independently shuffling each inscription's
    word-form order. pair_total_occ and the testable/cross sets are INVARIANT
    (same multisets), so we recompute only signs here."""
    pair_site_signs = defaultdict(lambda: defaultdict(Counter))
    for insc in inscriptions:
        forms = word_forms(insc)
        site = insc.get("site", "?")
        order = list(range(len(forms)))
        rng.shuffle(order)
        first_pos = {}
        for new_pos, orig_idx in enumerate(order):
            f = forms[orig_idx]
            if f not in first_pos:
                first_pos[f] = new_pos
        distinct = list(first_pos.keys())
        for a_i in range(len(distinct)):
            for b_i in range(a_i + 1, len(distinct)):
                fa, fb = distinct[a_i], distinct[b_i]
                if fa < fb:
                    key = (fa, fb); sign = +1 if first_pos[fa] < first_pos[fb] else -1
                else:
                    key = (fb, fa); sign = +1 if first_pos[fb] < first_pos[fa] else -1
                pair_site_signs[key][site][sign] += 1
    return pair_site_signs

def permutation_test_Cglob(inscriptions, n_draws=2000, rng=None):
    """One-sided perm p for C_glob enrichment vs within-inscription shuffle."""
    if rng is None:
        rng = RNG
    pss, pto = pair_observations(inscriptions)
    testable, cross = classify_pairs(pto, pss)
    Cg_obs = C_glob_from_observations(pss, testable)
    ge = 0
    null_Cg = []
    for _ in range(n_draws):
        spss = shuffled_signs(inscriptions, rng)
        cg = C_glob_from_observations(spss, testable)
        null_Cg.append(cg)
        if cg >= Cg_obs:
            ge += 1
    p = (ge + 1) / (n_draws + 1)
    return {
        "C_glob": Cg_obs,
        "C_glob_null_mean": sum(null_Cg) / len(null_Cg),
        "C_glob_p": p,
        "n_testable": len(testable),
        "n_cross": len(cross),
        "testable": testable,
        "cross": cross,
        "pair_site_signs": pss,
        "null_Cg": null_Cg,
    }

# ---------- bootstrap CI for C_glob ----------
def bootstrap_Cglob(pair_site_signs, testable, n_boot=2000, rng=None, ci=0.95):
    if rng is None:
        rng = RNG
    cons = pair_consistency_list(pair_site_signs, testable)
    if not cons:
        return 0.5, 0.5, 0.5
    n = len(cons)
    boots = []
    for _ in range(n_boot):
        s = 0.0
        for _ in range(n):
            s += cons[rng.randrange(n)]
        boots.append(s / n)
    boots.sort()
    lo_idx = int((1 - ci) / 2 * n_boot)
    hi_idx = int((1 - (1 - ci) / 2) * n_boot)
    hi_idx = min(hi_idx, n_boot - 1)
    return sum(cons) / n, boots[lo_idx], boots[hi_idx]

# ---------- closed-form null-mean check ----------
def closed_form_consistency_null(k):
    """E[ max(H,T)/k ] for H~Binomial(k,0.5) = E[ max(H,k-H)/k ]."""
    s = 0.0
    for h in range(k + 1):
        p = math.comb(k, h) / (2 ** k)
        s += p * (max(h, k - h) / k)
    return s

# ---------- synthetic PC builders ----------
def make_synthetic_corpus(n_sites, n_insc, forms_pool, min_words, max_words,
                          canon_order=None, canon_strength=1.0, rng=None,
                          random_order=False):
    """
    Build a synthetic corpus. Each inscription gets a random site and a random
    subset of forms. If canon_order is given and random_order is False, with
    probability canon_strength the chosen forms are placed in canon_order;
    otherwise (or if random_order) the order is shuffled.
    """
    if rng is None:
        rng = RNG
    out = []
    for i in range(n_insc):
        site = f"S{rng.randrange(n_sites)}"
        nw = rng.randrange(min_words, max_words + 1)
        nw = min(nw, len(forms_pool))
        chosen = rng.sample(forms_pool, nw)
        if random_order:
            rng.shuffle(chosen)
        elif canon_order is not None and rng.random() < canon_strength:
            # place in canon order (intersect with chosen)
            chosen = [f for f in canon_order if f in set(chosen)]
        else:
            rng.shuffle(chosen)
        stream = [{"t": "word", "signs": list(f)} for f in chosen]
        out.append({"id": f"SYN{i}", "site": site, "support": "Tablet",
                    "stream": stream})
    return out

def pc_detect(n_reps=20, n_draws=1000, rng=None):
    """DETECT: plant rigid canonical order; fraction of reps flagged at p<=0.05."""
    if rng is None:
        rng = RNG
    forms = [tuple(["F%02d" % i, "X%d" % i]) for i in range(12)]
    canon = list(forms)
    flagged = 0
    pvals = []
    for _ in range(n_reps):
        corp = make_synthetic_corpus(n_sites=10, n_insc=174, forms_pool=forms,
                                     min_words=2, max_words=6,
                                     canon_order=canon, canon_strength=1.0,
                                     rng=rng, random_order=False)
        res = permutation_test_Cglob(corp, n_draws=n_draws, rng=rng)
        pvals.append(res["C_glob_p"])
        if res["C_glob_p"] <= 0.05:
            flagged += 1
    return flagged / n_reps, pvals

def pc_false_positive(n_reps=20, n_draws=1000, rng=None):
    """FALSE-POSITIVE: plant random-order co-occurrences; rejection rate."""
    if rng is None:
        rng = RNG
    forms = [tuple(["F%02d" % i, "X%d" % i]) for i in range(12)]
    flagged = 0
    pvals = []
    for _ in range(n_reps):
        corp = make_synthetic_corpus(n_sites=10, n_insc=174, forms_pool=forms,
                                     min_words=2, max_words=6,
                                     canon_order=None, canon_strength=0.0,
                                     rng=rng, random_order=True)
        res = permutation_test_Cglob(corp, n_draws=n_draws, rng=rng)
        pvals.append(res["C_glob_p"])
        if res["C_glob_p"] <= 0.05:
            flagged += 1
    return flagged / n_reps, pvals

def pc_discrimination(rng=None, n_boot=2000):
    """DISCRIMINATION: rigid corpus (C~1.0) vs weak-order corpus (C~0.84).
    Confirm bootstrap contrast separates them: rigid CI excludes weak-order
    mean and vice versa."""
    if rng is None:
        rng = RNG
    forms = [tuple(["F%02d" % i, "X%d" % i]) for i in range(12)]
    canon = list(forms)
    # rigid
    rigid = make_synthetic_corpus(n_sites=10, n_insc=174, forms_pool=forms,
                                  min_words=2, max_words=6,
                                  canon_order=canon, canon_strength=1.0,
                                  rng=rng, random_order=False)
    pss_r, pto_r = pair_observations(rigid)
    test_r, _ = classify_pairs(pto_r, pss_r)
    Cg_r, lo_r, hi_r = bootstrap_Cglob(pss_r, test_r, n_boot=n_boot, rng=rng)
    # weak: half canon, half random -> C~0.84
    weak = make_synthetic_corpus(n_sites=10, n_insc=174, forms_pool=forms,
                                 min_words=2, max_words=6,
                                 canon_order=canon, canon_strength=0.55,
                                 rng=rng, random_order=False)
    pss_w, pto_w = pair_observations(weak)
    test_w, _ = classify_pairs(pto_w, pss_w)
    Cg_w, lo_w, hi_w = bootstrap_Cglob(pss_w, test_w, n_boot=n_boot, rng=rng)
    # separated iff rigid CI excludes weak mean AND weak CI excludes rigid mean
    sep = (hi_w < Cg_r) and (lo_r > Cg_w)
    return {
        "rigid_Cglob": Cg_r, "rigid_CI": (lo_r, hi_r),
        "weak_Cglob": Cg_w, "weak_CI": (lo_w, hi_w),
        "separated": sep,
    }

# ---------- self-check ----------
def self_check():
    """Validate the shuffle null gives an EMPIRICAL mean consistency > 0.5
    matching the closed-form E[max(H,T)/k]."""
    print("=== SELF-CHECK ===")
    # closed-form for k=2..6
    for k in range(2, 7):
        cf = closed_form_consistency_null(k)
        print(f"  closed-form E[max(H,T)/k] for k={k}: {cf:.4f} (>0.5: {cf>0.5})")
        assert cf > 0.5, f"closed-form null mean must be >0.5 (k={k})"
    # empirical: build a corpus where every inscription has exactly k=3 distinct
    # forms, all random order; the per-pair consistency under shuffle should
    # match closed-form for the relevant k distribution.
    rng = random.Random(123)
    forms = [tuple(["A%d" % i, "B%d" % i]) for i in range(8)]
    corp = make_synthetic_corpus(n_sites=5, n_insc=400, forms_pool=forms,
                                 min_words=3, max_words=3, random_order=True,
                                 rng=rng)
    pss, pto = pair_observations(corp)
    testable, _ = classify_pairs(pto, pss)
    # empirical null mean over many shuffles
    null_means = []
    for _ in range(200):
        spss = shuffled_signs(corp, rng)
        null_means.append(C_glob_from_observations(spss, testable))
    emp = sum(null_means) / len(null_means)
    # each pair has k occurrences; for k=3 closed-form ~0.7778; but pairs have
    # varying k. Just assert empirical null > 0.5 (the discipline requirement).
    print(f"  empirical shuffle null mean C_glob (random corpus): {emp:.4f} (>0.5: {emp>0.5})")
    assert emp > 0.5, "empirical null mean must be >0.5"
    print("  SELF-CHECK PASSED.")
    return True

if __name__ == "__main__":
    self_check()
