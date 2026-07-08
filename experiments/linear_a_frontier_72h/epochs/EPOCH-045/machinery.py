"""
EPOCH-045 machinery — ACCOUNTING-INTENSITY: NUMERAL-DENSITY AS A DOCUMENT-CLASS DISCRIMINANT.

Token-composition structure ONLY (L2/L3). No phonetics, no numeral-value arithmetic
(the `v` field is NEVER read; only the token TYPE 'num' is counted).

Self-check: run `python3 machinery.py` -> prints PC + global + within-site + verdict.
"""
import json, os, sys, hashlib
from collections import defaultdict
import numpy as np
from scipy.stats import kruskal, mannwhitneyu

RNG_SEED = 20240545  # frozen

# ---------- data loading ----------
def load_corpus():
    here = os.path.dirname(os.path.abspath(__file__))
    # repo root is 4 levels up from epochs/EPOCH-045/machinery.py
    root = here
    for _ in range(4):
        root = os.path.dirname(root)
    cand = [
        os.path.join(root, "corpus", "silver", "inscriptions_structured.json"),
        os.path.join(root, "..", "corpus", "silver", "inscriptions_structured.json"),
    ]
    path = next(p for p in cand if os.path.exists(p))
    with open(path) as f:
        return json.load(f), path

def content_counts(insc):
    nw = nn = 0
    for tok in insc.get("stream", []):
        t = tok.get("t")
        if t == "word":
            nw += 1
        elif t == "num":
            nn += 1
    return nw, nn

def qualifying(corpus, min_content=2):
    rows = []
    for x in corpus:
        nw, nn = content_counts(x)
        cont = nw + nn
        if cont >= min_content:
            rows.append({
                "support": x.get("support"),
                "site": x.get("site"),
                "density": nn / cont,
                "nword": nw, "nnum": nn,
            })
    return rows

# ---------- global test ----------
def global_kruskal(rows, min_support_n=20):
    by = defaultdict(list)
    for r in rows:
        by[r["support"]].append(r["density"])
    kept = {s: v for s, v in by.items() if len(v) >= min_support_n}
    supports = sorted(kept, key=lambda s: -len(kept[s]))
    H, p = kruskal(*[kept[s] for s in supports])
    return supports, kept, float(H), float(p)

# ---------- positive control ----------
def positive_control(rows, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    densities = np.array([r["density"] for r in rows], dtype=float)
    n = len(densities)
    half = n // 2

    # (a) DETECT: plant a density difference. Class A: densities shifted up by adding
    #     extra num-fraction; Class B: shifted down. Use a clear but modest planted gap.
    #     Build two synthetic classes by sampling baseline densities and applying a shift.
    base = rng.choice(densities, size=n, replace=True)
    shift = 0.20
    A = np.clip(base[:half] + shift, 0, 1)
    B = np.clip(base[half:] - shift, 0, 1)
    try:
        _, detect_p = mannwhitneyu(A, B, alternative="two-sided")
    except ValueError:
        detect_p = 1.0
    detect_p = float(detect_p)

    # (b) FALSE-POSITIVE: two classes from the SAME distribution; rejection rate over splits.
    rejections = 0
    S = 25
    for i in range(S):
        r = np.random.default_rng(seed + 1000 + i)
        perm = r.permutation(n)
        g1 = densities[perm[:half]]
        g2 = densities[perm[half:2*half]]
        try:
            _, pp = mannwhitneyu(g1, g2, alternative="two-sided")
        except ValueError:
            pp = 1.0
        if pp <= 0.05:
            rejections += 1
    fp_rate = rejections / S

    passed = (detect_p <= 0.05) and (fp_rate <= 0.10)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": detect_p,
        "false_pos_rate": float(fp_rate),
        "n_splits": S,
    }

# ---------- within-site ----------
def within_site(rows, min_support_n=10, seed=RNG_SEED):
    by_site = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_site[r["site"]][r["support"]].append(r["density"])
    per_site = {}
    testable_sites = []
    for site, sups in by_site.items():
        big = {s: v for s, v in sups.items() if len(v) >= min_support_n}
        if len(big) < 2:
            continue
        testable_sites.append(site)
        # two largest supports
        ordered = sorted(big, key=lambda s: -len(big[s]))[:2]
        a, b = ordered
        try:
            _, p = mannwhitneyu(big[a], big[b], alternative="two-sided")
        except ValueError:
            p = 1.0
        p = float(p)
        denser = a if np.mean(big[a]) > np.mean(big[b]) else b
        per_site[site] = {
            "supports": ordered,
            "n": {a: len(big[a]), b: len(big[b])},
            "p": p,
            "denser": denser,
            "mean": {a: float(np.mean(big[a])), b: float(np.mean(big[b]))},
        }
    n_testable = len(testable_sites)
    sig_sites = [s for s in testable_sites if per_site[s]["p"] <= 0.05]
    # direction consistency among SIGNIFICANT sites (which support is denser)
    if sig_sites:
        denser_set = {per_site[s]["denser"] for s in sig_sites}
        # consistent = the denser support is the same named support across sig sites
        # (when different support pairs, check the denser one is the more-accounting-like;
        #  here we just require a single denser identity OR all denser are 'Tablet'-type)
        direction_consistent = len(denser_set) == 1
    else:
        direction_consistent = True  # vacuously

    # pooled within-site permutation test (stratified by site): permute support labels
    # within each testable site, recompute sum of -log(p) (or a combined statistic).
    pooled_p = pooled_within_site_p(rows, testable_sites, min_support_n, seed)
    return {
        "n_sites_testable": n_testable,
        "n_sites_sig": len(sig_sites),
        "direction_consistent": bool(direction_consistent),
        "pooled_p": float(pooled_p),
        "per_site": per_site,
        "sig_sites": sig_sites,
    }

def _site_stat(site_rows):
    """combined statistic for a site: -log of Mann-Whitney p on two largest supports."""
    by = defaultdict(list)
    for r in site_rows:
        by[r["support"]].append(r["density"])
    big = {s: v for s, v in by.items() if len(v) >= 10}
    if len(big) < 2:
        return None
    ordered = sorted(big, key=lambda s: -len(big[s]))[:2]
    a, b = ordered
    try:
        _, p = mannwhitneyu(big[a], big[b], alternative="two-sided")
    except ValueError:
        p = 1.0
    return -np.log(p + 1e-300)

def pooled_within_site_p(rows, testable_sites, min_support_n, seed, n_perm=2000):
    rng = np.random.default_rng(seed + 7)
    by_site = defaultdict(list)
    for r in rows:
        if r["site"] in testable_sites:
            by_site[r["site"]].append(r)
    obs = sum((_site_stat(by_site[s]) or 0.0) for s in testable_sites)
    count = 0
    for _ in range(n_perm):
        perm_stat = 0.0
        for s in testable_sites:
            sr = by_site[s]
            sups = [r["support"] for r in sr]
            dens = [r["density"] for r in sr]
            perm = rng.permutation(len(sups))
            shuffled = [{"support": sups[perm[i]], "site": s, "density": dens[i]} for i in range(len(sups))]
            perm_stat += (_site_stat(shuffled) or 0.0)
        if perm_stat >= obs:
            count += 1
    return (count + 1) / (n_perm + 1)

# ---------- verdict ----------
def verdict(pc, glob, within):
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    if glob["kruskal_p"] > 0.05:
        return "NO_DOCCLASS_ACCOUNTING_DIFFERENCE"
    if within["n_sites_testable"] < 2:
        return "ACCOUNTING_UNDERPOWERED"
    if within["n_sites_sig"] >= 2 and within["direction_consistent"] and within["pooled_p"] <= 0.05:
        return "ACCOUNTING_INTENSITY_DOCCLASS_ROBUST"
    # global differs but within-site vanishes (<2 sig) or direction flips
    return "ACCOUNTING_INTENSITY_SITE_CONFOUNDED"

# ---------- driver ----------
def run():
    corpus, path = load_corpus()
    rows = qualifying(corpus)
    supports, kept, H, p = global_kruskal(rows)
    pc = positive_control(rows)
    within = within_site(rows)
    import statistics
    support_density = {}
    for s in supports:
        v = kept[s]
        support_density[s] = {
            "n_insc": int(len(v)),
            "mean_density": float(sum(v)/len(v)),
            "median_density": float(statistics.median(v)),
        }
    glob = {"kruskal_H": H, "kruskal_p": p, "n_supports": int(len(supports))}
    v = verdict(pc, glob, within)
    return {
        "corpus_path": path,
        "n_qualifying": len(rows),
        "supports": supports,
        "support_density": support_density,
        "global": glob,
        "positive_control": pc,
        "within_site": {k: within[k] for k in
                        ["n_sites_testable", "n_sites_sig", "direction_consistent",
                         "pooled_p", "per_site"]},
        "verdict": v,
    }

if __name__ == "__main__":
    res = run()
    print("=== EPOCH-045 machinery self-check ===")
    print("corpus:", res["corpus_path"])
    print("n_qualifying:", res["n_qualifying"])
    print("supports kept:", res["supports"])
    for s, d in res["support_density"].items():
        print(f"  {s:15s} n={d['n_insc']:4d} mean={d['mean_density']:.3f} median={d['median_density']:.3f}")
    g = res["global"]
    print(f"GLOBAL Kruskal-Wallis: H={g['kruskal_H']:.3f} p={g['kruskal_p']:.5g} n_supports={g['n_supports']}")
    pc = res["positive_control"]
    print(f"PC: {pc['pc_verdict']}  detect_p={pc['detect_p']:.5g}  fp_rate={pc['false_pos_rate']:.3f}")
    w = res["within_site"]
    print(f"WITHIN-SITE: testable={w['n_sites_testable']} sig={w['n_sites_sig']} "
          f"dir_consistent={w['direction_consistent']} pooled_p={w['pooled_p']:.5g}")
    for s, d in w["per_site"].items():
        print(f"  site {s}: supports={d['supports']} p={d['p']:.5g} denser={d['denser']}")
    print("VERDICT:", res["verdict"])
