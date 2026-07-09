"""
EPOCH-075 machinery: HARDEN the E072 libation-order cross-site positive.

Reuses the E072 metric EXACTLY (order-consistency of co-occurring
word-form pairs; within-inscription order-shuffle null; testable pairs
>=2 occ; cross-site pairs >=2 sites). Robustness = recompute the SAME
statistic on leave-one-out subsets.

Distinguishes SIGNAL-LOSS (fragility) from POWER-LOSS (underpowered):
a leave-out with n_cross<3 is UNDERPOWERED, not fragile. Only a leave-out
that keeps n_cross>=3 but loses significance (perm p>0.05) or drops
C_cross toward the null is FRAGILE.

L3 ONLY. Anonymous sign-tuples. No reading, no meaning.
"""
import json, random, hashlib, math, sys
from collections import defaultdict, Counter

RNG = random.Random(20250715)

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

# ---------- pair observations (IDENTICAL to E072) ----------
def pair_observations(inscriptions):
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

def stats_from_observations(pair_site_signs, testable, cross):
    cross_cons = []
    for k in cross:
        c, _, _ = consistency_from_signs(pair_site_signs[k])
        cross_cons.append(c)
    C_cross = sum(cross_cons) / len(cross_cons) if cross_cons else 0.5
    A = 0
    for k in cross:
        site_dominants = []
        ok = True
        for site, c in pair_site_signs[k].items():
            np_ = c[+1]; nm_ = c[-1]
            if np_ == nm_:
                ok = False
                break
            site_dominants.append(+1 if np_ > nm_ else -1)
        if ok and len(set(site_dominants)) == 1:
            A += 1
    n_cross = len(cross)
    return C_cross, A, n_cross

# ---------- shuffle null (IDENTICAL to E072) ----------
def shuffled_signs(inscriptions, rng):
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

def permutation_test(inscriptions, n_draws=1000, rng=None, stat="C_cross"):
    """One-sided perm p for the chosen stat over the subset's own invariant sets."""
    if rng is None:
        rng = RNG
    pss, pto = pair_observations(inscriptions)
    testable, cross = classify_pairs(pto, pss)
    Cc, A, nc = stats_from_observations(pss, testable, cross)
    obs = Cc if stat == "C_cross" else A
    ge = 0
    null_vals = []
    for _ in range(n_draws):
        spss = shuffled_signs(inscriptions, rng)
        cc2, a2, _ = stats_from_observations(spss, testable, cross)
        v = cc2 if stat == "C_cross" else a2
        null_vals.append(v)
        if v >= obs:
            ge += 1
    p = (ge + 1) / (n_draws + 1)
    null_mean = sum(null_vals) / len(null_vals) if null_vals else 0.0
    return {"C_cross": Cc, "A_cross": A, "n_cross": nc, "n_testable": len(testable),
            "perm_p": p, "null_mean_C_cross": null_mean, "n_draws": n_draws}

# ---------- carrier analysis ----------
def carrier_analysis(lib, cross_keys):
    """For each cross pair, list inscription indices that carry it."""
    pair_insc = {k: [] for k in cross_keys}
    for idx, insc in enumerate(lib):
        forms = word_forms(insc)
        if len(forms) < 2:
            continue
        first_pos = {}
        for i, f in enumerate(forms):
            if f not in first_pos:
                first_pos[f] = i
        distinct = list(first_pos.keys())
        for a_i in range(len(distinct)):
            for b_i in range(a_i + 1, len(distinct)):
                fa, fb = distinct[a_i], distinct[b_i]
                key = (fa, fb) if fa < fb else (fb, fa)
                if key in pair_insc:
                    pair_insc[key].append(idx)
    return pair_insc

# ---------- robustness status ----------
def robustness_status(n_cross, perm_p, C_cross, null_mean, floor=3, alpha=0.05):
    if n_cross < floor:
        return "UNDERPOWERED"
    # powered: fragile if non-significant OR C_cross collapses toward null
    if perm_p > alpha:
        return "FRAGILE"
    # C_cross "collapses toward null" if within 0.05 of null_mean
    if C_cross - null_mean < 0.05:
        return "FRAGILE"
    return "ROBUST"

# ---------- synthetic PC builders ----------
def make_synthetic_corpus(n_sites, forms_canon, n_canon_insc, n_random_insc,
                          hub_concentrated=False, rng=None):
    """
    Build a synthetic libation-scale corpus.
    - forms_canon: list of canonical word-forms (sign tuples).
    - n_canon_insc: inscriptions that carry the canonical ORDER.
    - n_random_insc: inscriptions with random multi-sign forms (noise).
    If hub_concentrated: ALL canon inscriptions share ONE hub site + one
        partner site (concentration). Else: canon inscriptions spread
        across MANY sites.
    Order: canon inscriptions place forms_canon in canonical order;
    random inscriptions place random subsets in random order.
    """
    if rng is None:
        rng = RNG
    site_names = [f"S{i}" for i in range(n_sites)]
    corpus = []
    for j in range(n_canon_insc):
        if hub_concentrated:
            # all canon inscriptions at hub site S0 or partner S1
            site = "S0" if (j % 2 == 0) else "S1"
        else:
            site = site_names[j % n_sites]
        forms = list(forms_canon)
        stream = [{"t": "word", "signs": list(f)} for f in forms]
        corpus.append({"id": f"CAN{j}", "site": site, "support": "Stone vessel",
                       "stream": stream, "words": [list(f) for f in forms]})
    # random noise inscriptions
    pool = forms_canon + [tuple(["X", f"R{k}"]) for k in range(n_random_insc)]
    for j in range(n_random_insc):
        site = site_names[rng.randrange(n_sites)]
        k = rng.randint(2, min(4, len(pool)))
        chosen = rng.sample(pool, k)
        rng.shuffle(chosen)
        stream = [{"t": "word", "signs": list(f)} for f in chosen]
        corpus.append({"id": f"RND{j}", "site": site, "support": "Stone vessel",
                       "stream": stream, "words": [list(f) for f in chosen]})
    return corpus

# ---------- self-check ----------
def self_check():
    failures = []
    corpus = load_corpus("corpus/silver/inscriptions_structured.json")
    lib = libation_inscriptions(corpus)
    assert len(lib) == 99, f"libation count {len(lib)} != 99"
    multi = [x for x in lib if len(word_forms(x)) >= 2]
    assert len(multi) == 56, f"multiword {len(multi)} != 56"
    pss, pto = pair_observations(lib)
    testable, cross = classify_pairs(pto, pss)
    assert len(testable) == 13, f"n_testable {len(testable)} != 13"
    assert len(cross) == 10, f"n_cross {len(cross)} != 10"
    Cc, A, nc = stats_from_observations(pss, testable, cross)
    assert abs(Cc - 1.0) < 1e-9, f"C_cross {Cc} != 1.0"
    assert A == 10, f"A_cross {A} != 10"
    # carrier: hub is endpoint of all 10
    pi = carrier_analysis(lib, cross)
    all_carriers = []
    for k in pi:
        all_carriers.extend(pi[k])
    cc = Counter(all_carriers)
    top_idx, top_n = cc.most_common(1)[0]
    assert top_n == 10, f"hub pair count {top_n} != 10"
    assert len(cc) == 8, f"distinct carriers {len(cc)} != 8"
    distinct_sites = len(set(lib[i].get("site") for i in all_carriers))
    assert distinct_sites == 6, f"distinct carrier sites {distinct_sites} != 6"
    # LOSO pre-counts
    for drop, exp in [("Zakros",10),("Iouktas",3),("Palaikastro",9),("Syme",10)]:
        sub = [x for x in lib if x.get("site")!=drop]
        _, pto2 = pair_observations(sub)
        _, cross2 = classify_pairs(pto2, {k:v for k,v in pair_observations(sub)[0].items()})
        # recompute cleanly
        s_pss, s_pto = pair_observations(sub)
        _, s_cross = classify_pairs(s_pto, s_pss)
        assert len(s_cross) == exp, f"LOSO drop {drop}: n_cross {len(s_cross)} != {exp}"
    # LHIO pre-counts
    for label, drops, exp in [("top1",[top_idx],4),("top2",[top_idx],3),("top3",[top_idx],2)]:
        # find top2, top3 by carrier count
        pass
    # closed-form null-mean sanity (E[max(H,T)/k])
    def cf(k):
        s=0.0
        for h in range(k+1):
            s += (math.comb(k,h)/(2**k)) * (max(h,k-h)/k)
        return s
    assert abs(cf(2)-0.75)<1e-9 and abs(cf(3)-0.75)<1e-9 and abs(cf(4)-0.6875)<1e-9
    print("SELF-CHECK PASSED: baseline C_cross=1.0, A_cross=10, n_cross=10, hub=endpoint of 10, 8 carriers / 6 sites, LOSO pre-counts match, closed-form null OK")

if __name__ == "__main__":
    self_check()
