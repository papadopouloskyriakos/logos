"""
EPOCH-055 machinery — Numeral Magnitude (Accounting Scale) by Document Class.

L2/L3 ONLY: numeral magnitudes ('v'). NO sign values, NO readings, NO phonetics.

Frozen metric: per-support distribution of numeral magnitudes (median + mean);
GLOBAL = Kruskal-Wallis across supports on magnitude.
PC FIRST; mechanical verdict from frozen rule.
"""
import json, hashlib, statistics
from collections import defaultdict
from scipy import stats


# ---------- data loading ----------
def load_corpus(path="corpus/silver/inscriptions_structured.json"):
    with open(path) as f:
        return json.load(f)


def extract_numerals(inscriptions, min_v=1, min_class_n=30):
    """Return (per_support: {support: [v,...]}, per_site_support: {(support,site): [v,...]}).
    Keep support classes with >=min_class_n numerals overall."""
    raw_sup = defaultdict(list)
    raw_ss = defaultdict(list)
    for ins in inscriptions:
        sup = ins.get("support")
        site = ins.get("site")
        if not sup:
            continue
        for tok in ins.get("stream", []):
            if isinstance(tok, dict) and tok.get("t") == "num":
                v = tok.get("v")
                if isinstance(v, int) and v >= min_v:
                    raw_sup[sup].append(v)
                    if site:
                        raw_ss[(sup, site)].append(v)
    keep = {s for s, v in raw_sup.items() if len(v) >= min_class_n}
    per_support = {s: raw_sup[s] for s in keep}
    per_ss = {k: v for k, v in raw_ss.items() if k[0] in keep}
    return per_support, per_ss


# ---------- global Kruskal-Wallis ----------
def global_kruskal(per_support):
    groups = [v for v in per_support.values() if len(v) >= 1]
    if len(groups) < 2:
        return float("nan"), float("nan"), len(groups)
    H, p = stats.kruskal(*groups)
    return float(H), float(p), len(groups)


# ---------- positive control ----------
def positive_control(seed=55, n_detect=200, n_fp_splits=25, fp_n=120):
    """(a) DETECT: two synthetic groups with planted magnitude-scale difference must be detected.
       (b) FALSE-POSITIVE: two groups from SAME distribution -> rejection rate <=0.10."""
    import numpy as np
    rng = np.random.default_rng(seed)

    # (a) DETECT: heavy-tailed magnitudes; group B shifted up (scale ~3x).
    # Model magnitudes as lognormal (heavy-tailed, like real accounting quantities).
    A = rng.lognormal(mean=2.0, sigma=1.2, size=n_detect).astype(int) + 1
    B = rng.lognormal(mean=2.0 + 1.1, sigma=1.2, size=n_detect).astype(int) + 1  # ~3x scale
    H_det, p_det = stats.kruskal(A, B)

    # (b) FALSE-POSITIVE: same distribution, two draws; rejection rate over splits.
    rej = 0
    for i in range(n_fp_splits):
        r = np.random.default_rng(seed * 1000 + i)
        base = r.lognormal(mean=2.0, sigma=1.2, size=fp_n * 2).astype(int) + 1
        g1 = base[:fp_n]
        g2 = base[fp_n:]
        _, p = stats.kruskal(g1, g2)
        if p <= 0.05:
            rej += 1
    fp_rate = rej / n_fp_splits

    detect_ok = p_det <= 0.05
    fp_ok = fp_rate <= 0.10
    passed = bool(detect_ok and fp_ok)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": float(p_det),
        "false_pos_rate": float(fp_rate),
        "detect_ok": detect_ok,
        "fp_ok": fp_ok,
    }


# ---------- within-site (LA MAIN) ----------
def within_site_tests(per_ss, min_cell=15):
    """For each site with >=2 support classes each >=min_cell numerals, run Kruskal-Wallis
    (or Mann-Whitney for 2). Return per-site results + counts."""
    by_site = defaultdict(dict)
    for (sup, site), vals in per_ss.items():
        if len(vals) >= min_cell:
            by_site[site][sup] = vals

    per_site = {}
    testable_sites = []
    for site, sups in by_site.items():
        if len(sups) < 2:
            continue
        testable_sites.append(site)
        groups = list(sups.values())
        names = list(sups.keys())
        if len(groups) == 2:
            U, p = stats.mannwhitneyu(groups[0], groups[1], alternative="two-sided")
            med = {n: statistics.median(v) for n, v in sups.items()}
            larger = max(med, key=med.get)
            per_site[site] = {"p": float(p), "larger": larger, "medians": med, "test": "mannwhitney"}
        else:
            H, p = stats.kruskal(*groups)
            med = {n: statistics.median(v) for n, v in sups.items()}
            larger = max(med, key=med.get)
            per_site[site] = {"p": float(p), "larger": larger, "medians": med, "test": "kruskal"}

    n_testable = len(testable_sites)
    n_sig = sum(1 for r in per_site.values() if r["p"] <= 0.05)
    # direction consistency: among sig sites, is the 'larger' support the same?
    sig_larger = [r["larger"] for r in per_site.values() if r["p"] <= 0.05]
    direction_consistent = len(set(sig_larger)) <= 1 if sig_larger else False
    return {
        "n_sites_testable": n_testable,
        "n_sites_sig": n_sig,
        "direction_consistent": bool(direction_consistent),
        "per_site": per_site,
    }


# ---------- frozen mechanical verdict ----------
def mechanical_verdict(pc, global_res, within):
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    if within["n_sites_testable"] < 2:
        return "SCALE_UNDERPOWERED"
    if global_res["kruskal_p"] > 0.05:
        return "NO_DOCCLASS_SCALE_DIFFERENCE"
    if within["n_sites_sig"] < 2 or not within["direction_consistent"]:
        return "ACCOUNTING_SCALE_SITE_CONFOUNDED"
    return "ACCOUNTING_SCALE_DOCCLASS_ROBUST"


# ---------- self-check ----------
def _self_check():
    # synthetic: two supports with different magnitudes -> global should detect
    import numpy as np
    rng = np.random.default_rng(1)
    fake = [
        {"support": "A", "site": "S1", "stream": [{"t": "num", "v": int(x)} for x in rng.lognormal(2, 1, 60)]},
        {"support": "B", "site": "S1", "stream": [{"t": "num", "v": int(x)} for x in rng.lognormal(3, 1, 60)]},
    ]
    ps, pss = extract_numerals(fake, min_class_n=30)
    assert len(ps) == 2, f"expected 2 supports, got {len(ps)}"
    H, p, n = global_kruskal(ps)
    assert p <= 0.05, f"self-check global should detect, p={p}"
    pc = positive_control(seed=55)
    assert pc["pc_verdict"] == "PASSED", f"PC should pass: {pc}"
    print("SELF-CHECK OK | global p=%.4g | PC=%s" % (p, pc["pc_verdict"]))


if __name__ == "__main__":
    _self_check()
