"""
EPOCH-072 machinery: libation formula-as-ordered-sequence (L3).

Anonymous word-forms (sign tuples, len>=2). For each inscription, every
unordered pair of distinct forms present yields one observation (site, sign).
Sign = +1 if (lex-key fa<fb) fa precedes fb in stream (first-occurrence pos),
else -1.

Testable pairs: total occurrences >= 2.
Cross-site pairs: observed at >= 2 distinct sites.
consistency(pair) = max(n_plus, n_minus)/(n_plus+n_minus) in [0.5,1].
C_glob  = mean consistency over testable pairs.
C_cross = mean consistency over cross-site pairs.
A_cross = # cross-site pairs whose dominant order is the SAME in EVERY site
          that has >=1 occurrence (full cross-site agreement).
agree_frac = A_cross / n_cross_pairs.

NULL: within-inscription word-order shuffle (preserves each inscription's
word multiset -> invariant testable/cross-site pair sets; destroys only
order). >=1000 draws. One-sided perm p = frac(null>=obs), add-one smoothed.

L3 ONLY. No reading, no meaning.
"""
import json, random, hashlib, math
from collections import defaultdict, Counter

RNG = random.Random(20240712)

# ---------- corpus loading ----------
def load_corpus(path):
    return json.load(open(path))

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
    Returns:
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
        # first occurrence position
        first_pos = {}
        for i, f in enumerate(forms):
            if f not in first_pos:
                first_pos[f] = i
        distinct = list(first_pos.keys())
        for a_i in range(len(distinct)):
            for b_i in range(a_i + 1, len(distinct)):
                fa, fb = distinct[a_i], distinct[b_i]
                # lex key
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

def stats_from_observations(pair_site_signs, testable, cross):
    # C_glob
    cons_list = []
    for k in testable:
        c, _, _ = consistency_from_signs(pair_site_signs[k])
        cons_list.append(c)
    C_glob = sum(cons_list) / len(cons_list) if cons_list else 0.5
    # C_cross
    cross_cons = []
    for k in cross:
        c, _, _ = consistency_from_signs(pair_site_signs[k])
        cross_cons.append(c)
    C_cross = sum(cross_cons) / len(cross_cons) if cross_cons else 0.5
    # A_cross: # cross pairs where every site agrees on dominant order
    A = 0
    for k in cross:
        site_dominants = []
        ok = True
        for site, c in pair_site_signs[k].items():
            np_ = c[+1]; nm_ = c[-1]
            if np_ == nm_:
                # tie -> no dominant; treat as not-agreeing
                ok = False
                break
            site_dominants.append(+1 if np_ > nm_ else -1)
        if ok and len(set(site_dominants)) == 1:
            A += 1
    n_cross = len(cross)
    agree_frac = A / n_cross if n_cross else 0.0
    return C_glob, C_cross, A, agree_frac, n_cross

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
        # position of each distinct form = its first index in the SHUFFLED stream
        # (enumerate position in the new order, not the original index value)
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

def permutation_test(inscriptions, n_draws=2000, rng=None):
    if rng is None:
        rng = RNG
    pss, pto = pair_observations(inscriptions)
    testable, cross = classify_pairs(pto, pss)
    Cg, Cc, A, af, nc = stats_from_observations(pss, testable, cross)
    obs = (Cg, Cc, A, af, nc, len(testable))
    ge_Cg = ge_Cc = ge_A = 0
    null_Cg = []; null_Cc = []; null_A = []
    for _ in range(n_draws):
        spss = shuffled_signs(inscriptions, rng)
        cg, cc, a, _, _ = stats_from_observations(spss, testable, cross)
        null_Cg.append(cg); null_Cc.append(cc); null_A.append(a)
        if cg >= Cg: ge_Cg += 1
        if cc >= Cc: ge_Cc += 1
        if a  >= A:  ge_A  += 1
    p_Cg = (ge_Cg + 1) / (n_draws + 1)
    p_Cc = (ge_Cc + 1) / (n_draws + 1)
    p_A  = (ge_A  + 1) / (n_draws + 1)
    return {
        "obs": {"C_glob": Cg, "C_cross": Cc, "A_cross": A, "agree_frac": af,
                "n_cross": nc, "n_testable": len(testable)},
        "null_mean": {"C_glob": sum(null_Cg)/len(null_Cg),
                      "C_cross": sum(null_Cc)/len(null_Cc),
                      "A_cross": sum(null_A)/len(null_A)},
        "p": {"C_glob": p_Cg, "C_cross": p_Cc, "A_cross": p_A},
        "n_draws": n_draws,
        "testable": testable, "cross": cross, "pair_total_occ": dict(pto),
        "pair_site_signs": {k: {s: dict(c) for s, c in v.items()} for k, v in pss.items()},
    }

# ---------- closed-form null-mean check ----------
def closed_form_consistency_null(k):
    """E[ max(H,T)/k ] for H~Binomial(k,0.5) = E[ max(H,k-H)/k ]."""
    s = 0.0
    for h in range(k + 1):
        # P(H=h) = C(k,h)/2^k
        p = math.comb(k, h) / (2 ** k)
        s += p * (max(h, k - h) / k)
    return s

# ---------- synthetic PC builders ----------
def make_synthetic_corpus(n_sites, forms_canon, n_canon_insc, n_random_insc,
                          canon_strength=1.0, rng=None, random_order=False):
    """
    Build a synthetic stone-vessel-like corpus.
    forms_canon: list of forms that (when planted) appear in fixed canonical order.
    canon_strength: fraction of canon inscriptions that follow the order
                    (rest random) -- 1.0 = always ordered.
    random_order=True -> co-occurrences present but order randomized (FP arm).
    """
    if rng is None:
        rng = RNG
    sites = [f"SITE{i}" for i in range(n_sites)]
    inscs = []
    for i in range(n_canon_insc):
        site = sites[i % n_sites]
        if random_order:
            order = list(forms_canon); rng.shuffle(order)
        else:
            if rng.random() < canon_strength:
                order = list(forms_canon)
            else:
                order = list(forms_canon); rng.shuffle(order)
        inscs.append({"site": site, "stream": [{"t": "word", "signs": list(f)} for f in order]})
    # random filler inscriptions (single-form or unrelated) to add noise
    for i in range(n_random_insc):
        site = rng.choice(sites)
        k = rng.randint(2, 4)
        forms = [tuple(f"F{j}_{rng.randint(0,9)}" for j in range(2)) for _ in range(k)]
        rng.shuffle(forms)
        inscs.append({"site": site, "stream": [{"t": "word", "signs": list(f)} for f in forms]})
    return inscs

# ---------- self-check ----------
def self_check():
    print("=== SELF CHECK ===")
    # 1) closed-form vs empirical null mean of consistency for k=2,3,4
    # Build a corpus where a single pair co-occurs k times, each in its own
    # inscription, with random order each time. Empirical null mean of that
    # pair's consistency should match closed_form_consistency_null(k).
    for k in [2, 3, 4]:
        # k inscriptions, each with the SAME two forms in random order
        rng = random.Random(100 + k)
        inscs = []
        for i in range(k):
            forms = [("A1", "B1"), ("C2", "D2")]
            rng.shuffle(forms)
            inscs.append({"site": f"S{i}", "stream": [{"t": "word", "signs": list(f)} for f in forms]})
        # empirical null mean of consistency for this pair over many shuffles
        pss, pto = pair_observations(inscs)
        testable, cross = classify_pairs(pto, pss)
        assert len(testable) == 1, (k, len(testable))
        nd = 4000
        rng2 = random.Random(7 + k)
        cons_null = []
        for _ in range(nd):
            spss = shuffled_signs(inscs, rng2)
            c, _, _ = consistency_from_signs(spss[testable[0]])
            cons_null.append(c)
        emp = sum(cons_null) / len(cons_null)
        cf = closed_form_consistency_null(k)
        print(f"k={k}: empirical null mean consistency={emp:.4f}  closed-form={cf:.4f}  (both >0.5: {emp>0.5 and cf>0.5})")
        assert emp > 0.5, emp
        assert cf > 0.5, cf
        assert abs(emp - cf) < 0.03, (emp, cf)
    # 2) invariance: shuffle preserves pair_total_occ and the testable/cross sets
    rng = random.Random(999)
    inscs = make_synthetic_corpus(3, [("X","X"),("Y","Y"),("Z","Z")], 10, 5, rng=rng)
    pss, pto = pair_observations(inscs)
    testable, cross = classify_pairs(pto, pss)
    for _ in range(50):
        spss = shuffled_signs(inscs, rng)
        spto = Counter()
        for k, sites in spss.items():
            for s, c in sites.items():
                spto[k] += c[+1] + c[-1]
        assert dict(spto) == dict(pto), "shuffle changed total occ (not invariant!)"
        stest, scross = classify_pairs(spto, spss)
        assert set(stest) == set(testable), "testable set changed"
        assert set(scross) == set(cross), "cross set changed"
    print("invariance OK: shuffle preserves total occ, testable set, cross set")
    print("=== SELF CHECK PASSED ===")

if __name__ == "__main__":
    self_check()
