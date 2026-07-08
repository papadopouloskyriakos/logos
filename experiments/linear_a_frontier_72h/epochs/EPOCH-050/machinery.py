#!/usr/bin/env python3
"""EPOCH-050 — A-PREFIX CONTINUATION SELECTIVITY (machinery).

Question (L2/L3): is the word-initial sign token 'A' SELECTIONAL over its continuation
(2nd-sign entropy significantly below a frequency-matched null), or does it attach freely?

Discipline: signs ANONYMOUS; 'A' = word-initial sign token 'A' ONLY (no phonetic value, no
morpheme, no meaning). L2/L3 ONLY. LB control-only. Pure continuation-distribution structure.

Frozen metric: selectivity = observed H_after_A significantly LOWER than a bootstrap null
(2nd-signs drawn from the global 2nd-position distribution, same N). One-sided p = fraction of
bootstrap H <= observed H.

Pure stdlib. Seed 20260708. Synchronous.
"""
from __future__ import annotations
import json, math, os, sys, random
from collections import Counter

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
CAMP = os.path.join(ROOT, "experiments", "linear_a_frontier_72h")
CORPUS = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
SEED = 20260708
B_BOOT = 2000          # bootstrap realizations for null H
ALPHA = 0.05
FP_N = 300             # number of free-continuation synthetic prefixes for FP rate
FP_THRESH = 0.10
PLANT_K = 5            # restricted-continuation set size for DETECT synthetic


# ----------------------------------------------------------------- helpers
def H(counter: Counter) -> float:
    n = sum(counter.values())
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in counter.values())


def load_la():
    d = json.load(open(CORPUS, encoding="utf-8"))
    words = []  # list of (site, signs)
    for ins in d:
        site = ins.get("site", "?")
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                words.append((site, list(tok.get("signs", []))))
    return words


def second_after(words, first):
    c = Counter()
    for _site, sg in words:
        if len(sg) >= 2 and sg[0] == first:
            c[sg[1]] += 1
    return c


def global_second(words):
    c = Counter()
    for _site, sg in words:
        if len(sg) >= 2:
            c[sg[1]] += 1
    return c


def bootstrap_null_H(pool_counter, n_obs, rng, B=B_BOOT):
    """Bootstrap: draw n_obs 2nd-signs from pool distribution, compute H, repeat B times.
    Returns (mean_null_H, list_of_H)."""
    items = list(pool_counter.keys())
    weights = [pool_counter[k] for k in items]
    tot = sum(weights)
    probs = [w / tot for w in weights]
    # cumulative for manual sampling
    import bisect
    cum = []
    s = 0.0
    for p in probs:
        s += p
        cum.append(s)
    hs = []
    for _ in range(B):
        c = Counter()
        r = rng.random()
        # sample n_obs
        for _i in range(n_obs):
            u = rng.random()
            idx = bisect.bisect_left(cum, u)
            if idx >= len(items):
                idx = len(items) - 1
            c[items[idx]] += 1
        hs.append(H(c))
    return sum(hs) / len(hs), hs


def selectivity_test(obs_counter, pool_counter, rng, B=B_BOOT):
    """One-sided test: is observed H significantly LOWER than null?
    Returns (obs_H, null_H_mean, p) where p = P(null_H <= obs_H)."""
    n_obs = sum(obs_counter.values())
    obs_H = H(obs_counter)
    null_mean, hs = bootstrap_null_H(pool_counter, n_obs, rng, B=B)
    p = sum(1 for h in hs if h <= obs_H) / len(hs)
    return obs_H, null_mean, p


# ----------------------------------------------------------------- positive control
def pc_detect_restricted(rng):
    """Synthetic prefix with a KNOWN restricted continuation set (K signs). Confirm the test
    flags it selectional. Build a pool (global-like, many signs) and a restricted obs drawn
    from only K of them."""
    # global-like pool: 40 signs, zipf-ish
    signs = [f"S{i}" for i in range(40)]
    pool = Counter()
    for i, s in enumerate(signs):
        pool[s] = max(1, int(100 / (i + 1)))
    # restricted obs: only first K signs, n=155
    n = 155
    restr = signs[:PLANT_K]
    obs = Counter()
    for _ in range(n):
        obs[rng.choice(restr)] += 1
    obs_H, null_H, p = selectivity_test(obs, pool, rng)
    return obs_H, null_H, p


def pc_free_continuation(rng):
    """One free-continuation synthetic prefix: obs drawn from the SAME pool as null.
    Should NOT be flagged (p > 0.05 ideally). Returns p."""
    signs = [f"S{i}" for i in range(40)]
    pool = Counter()
    for i, s in enumerate(signs):
        pool[s] = max(1, int(100 / (i + 1)))
    n = 155
    items = list(pool.keys())
    weights = [pool[k] for k in items]
    tot = sum(weights)
    import bisect
    cum = []
    s = 0.0
    for w in weights:
        s += w / tot
        cum.append(s)
    obs = Counter()
    for _ in range(n):
        u = rng.random()
        idx = bisect.bisect_left(cum, u)
        if idx >= len(items):
            idx = len(items) - 1
        obs[items[idx]] += 1
    _oH, _nH, p = selectivity_test(obs, pool, rng)
    return p


def positive_control(rng):
    """Returns dict: pc_verdict, detect_p, false_pos_rate."""
    # DETECT (restricted)
    det_H, det_null, det_p = pc_detect_restricted(rng)
    detect_ok = det_p <= ALPHA
    # FP rate over many free-continuation synthetics
    fps = []
    for _ in range(FP_N):
        p = pc_free_continuation(rng)
        fps.append(1 if p <= ALPHA else 0)
    fpr = sum(fps) / len(fps)
    fp_ok = fpr <= FP_THRESH
    verdict = "PASSED" if (detect_ok and fp_ok) else "FAILED"
    return {
        "pc_verdict": verdict,
        "detect_p": det_p,
        "detect_obs_H": det_H,
        "detect_null_H": det_null,
        "false_pos_rate": fpr,
        "fp_n": FP_N,
    }


# ----------------------------------------------------------------- LB sanity
def lb_sanity(rng):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from cross_script import data as D
    seqs, _freq, _v2g = D.load_b_damos()
    # words with len>=2
    words = [w for w in seqs if len(w) >= 2]
    # most frequent initial sign
    init = Counter(w[0] for w in words)
    first = init.most_common(1)[0][0]
    obs = Counter(w[1] for w in words if w[0] == first)
    pool = Counter(w[1] for w in words)
    oH, nH, p = selectivity_test(obs, pool, rng)
    return {"lb_initial": first, "lb_n": sum(obs.values()), "lb_H_2nd": oH, "lb_null_H": nH, "lb_p": p}


# ----------------------------------------------------------------- main
def run():
    rng = random.Random(SEED)
    words = load_la()

    # GLOBAL
    a2 = second_after(words, "A")
    g2 = global_second(words)
    obs_H, null_H, p = selectivity_test(a2, g2, rng)
    top = a2.most_common(10)
    top_share = sum(c for _s, c in top) / sum(a2.values())

    # COMPARATORS
    init = Counter(sg[0] for _s, sg in words if len(sg) >= 1)
    comparators = {}
    for first, _c in init.most_common(6):
        if first == "A":
            continue
        cc = second_after(words, first)
        if sum(cc.values()) < 10:
            continue
        cH = H(cc)
        comparators[first] = {"n": sum(cc.values()), "H_2nd_bits": round(cH, 4)}

    # POSITIVE CONTROL
    pc = positive_control(rng)

    # LB sanity
    lb = lb_sanity(rng)

    # CROSS-SITE
    # per-site A-initial ge2 counts
    siteA = Counter()
    site_pool = {}  # site -> global 2nd-position Counter for that site
    for site, sg in words:
        if len(sg) >= 2:
            site_pool.setdefault(site, Counter())[sg[1]] += 1
            if sg[0] == "A":
                siteA[site] += 1
    testable = [(s, c) for s, c in siteA.items() if c >= 15]
    n_sites_testable = len(testable)
    site_results = {}
    n_restricted = 0
    for s, c in testable:
        obs_s = Counter()
        for site, sg in words:
            if site == s and len(sg) >= 2 and sg[0] == "A":
                obs_s[sg[1]] += 1
        pool_s = site_pool.get(s, Counter())
        if sum(pool_s.values()) < 5:
            oH, nH, sp = float("nan"), float("nan"), 1.0
        else:
            oH, nH, sp = selectivity_test(obs_s, pool_s, rng)
        restricted = (sp <= ALPHA)
        if restricted:
            n_restricted += 1
        site_results[s] = {"n": c, "H_after_A": round(oH, 4), "null_H": round(nH, 4), "p": sp, "restricted": restricted}

    # LEAVE-ONE-SITE-OUT on HT (largest site): recompute global restricted test excluding HT
    words_noHT = [(s, sg) for s, sg in words if s != "Haghia Triada"]
    a2_noHT = second_after(words_noHT, "A")
    g2_noHT = global_second(words_noHT)
    oH_loo, nH_loo, p_loo = selectivity_test(a2_noHT, g2_noHT, rng)

    return {
        "global": {
            "n_A_initial_ge2": sum(a2.values()),
            "H_after_A_bits": round(obs_H, 4),
            "null_H_bits": round(null_H, 4),
            "H_p": p,
            "top_continuations": [[s, c] for s, c in top],
            "top_share": round(top_share, 4),
            "n_distinct_2nd": len(a2),
        },
        "comparators": comparators,
        "positive_control": pc,
        "lb_sanity": lb,
        "cross_site": {
            "n_sites_testable": n_sites_testable,
            "n_sites_restricted": n_restricted,
            "site_results": site_results,
            "loo_excluded": "Haghia Triada",
            "loo_n": sum(a2_noHT.values()),
            "loo_H_after_A": round(oH_loo, 4),
            "loo_null_H": round(nH_loo, 4),
            "loo_p": p_loo,
        },
    }


# ----------------------------------------------------------------- verdict (mechanical)
def verdict(res):
    pc = res["positive_control"]["pc_verdict"]
    if pc != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    g = res["global"]
    cs = res["cross_site"]
    if cs["n_sites_testable"] < 2:
        return "A_SELECTIVITY_UNDERPOWERED"
    global_restricted = (g["H_p"] <= ALPHA)
    if not global_restricted:
        return "A_PREFIX_NON_SELECTIONAL"
    # global restricted
    loo_survives = (cs["loo_p"] <= ALPHA)
    if cs["n_sites_restricted"] >= 2 and loo_survives:
        return "A_PREFIX_SELECTIONAL_CROSS_SITE"
    return "A_PREFIX_SELECTIONAL_SITE_LOCAL"


if __name__ == "__main__":
    res = run()
    v = verdict(res)
    print("VERDICT:", v)
    print(json.dumps(res, indent=2, ensure_ascii=False))
