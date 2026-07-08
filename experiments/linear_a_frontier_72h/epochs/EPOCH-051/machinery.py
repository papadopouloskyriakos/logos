"""
EPOCH-051 machinery: A-HEADING x ACCOUNTING-INTENSITY interaction (L2/L3).

Anonymous positional token 'A' (first sign of first word) vs numeral-density.
Mann-Whitney U based. Includes positive control (detect + false-positive) and
self-check under __main__.

NO phonetics, NO semantics, NO sign values. Token composition only.
"""
import json, os, math
from collections import Counter

import numpy as np
from scipy.stats import mannwhitneyu

CORPUS_DEFAULT = "corpus/silver/inscriptions_structured.json"
A_SIGN = "A"  # anonymous positional token; literal sign string only


# ---------- feature extraction ----------
def inscription_features(ins):
    """Return (a_headed_bool, density_float, n_word, n_num, site, support) or None."""
    st = ins.get("stream", []) or []
    n_word = 0
    n_num = 0
    first_sign = None
    seen_first = False
    for tok in st:
        t = tok.get("t")
        if t == "word":
            n_word += 1
            if not seen_first:
                sg = tok.get("signs", []) or []
                if sg:
                    first_sign = sg[0]
                seen_first = True
        elif t == "num":
            n_num += 1
    content = n_word + n_num
    if content < 2 or n_word < 1:
        return None
    density = n_num / content
    a_headed = (first_sign == A_SIGN)
    return (a_headed, density, n_word, n_num,
            ins.get("site"), ins.get("support"))


def load_rows(path=CORPUS_DEFAULT):
    with open(path) as f:
        data = json.load(f)
    rows = []
    for ins in data:
        ft = inscription_features(ins)
        if ft is not None:
            rows.append(ft)
    return rows


# ---------- stats helpers ----------
def mw_p(a, b):
    """Two-sided Mann-Whitney U p-value. Returns 1.0 if either side empty/too small."""
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    if len(a) < 1 or len(b) < 1:
        return 1.0
    try:
        with np.errstate(divide="ignore", invalid="ignore"):
            u, p = mannwhitneyu(a, b, alternative="two-sided")
        if math.isnan(p):
            p = 1.0
        return float(p)
    except ValueError:
        return 1.0


def direction(a, b):
    """'A_headed_higher_density' | 'A_headed_lower_density' | 'tie'."""
    ma = float(np.mean(a)) if len(a) else 0.0
    mb = float(np.mean(b)) if len(b) else 0.0
    if ma > mb:
        return "A_headed_higher_density"
    if ma < mb:
        return "A_headed_lower_density"
    return "tie"


# ---------- positive control ----------
def positive_control(rows, n_splits=25, seed=0):
    """
    (a) DETECT: plant a density shift (+0.20, clipped) on a random half of eligible
        inscriptions -> require p<=0.05 in the correct direction (planted higher).
    (b) FALSE-POSITIVE: two groups drawn from the SAME density distribution; require
        rejection rate (p<=0.05) <= 0.10 across >=20 random splits.
    """
    rng = np.random.default_rng(seed)
    densities = np.array([r[1] for r in rows], dtype=float)
    n = len(densities)

    # (a) DETECT
    idx = rng.permutation(n)
    half = n // 2
    planted = densities.copy()
    planted[idx[:half]] = np.clip(planted[idx[:half]] + 0.20, 0.0, 1.0)
    a_group = planted[idx[:half]]
    b_group = planted[idx[half:]]
    detect_p = mw_p(a_group, b_group)
    detect_ok = (detect_p <= 0.05) and (np.mean(a_group) > np.mean(b_group))

    # (b) FALSE-POSITIVE
    rejections = 0
    for s in range(n_splits):
        r = np.random.default_rng(1000 + s)
        perm = r.permutation(n)
        h = n // 2
        p = mw_p(densities[perm[:h]], densities[perm[h:]])
        if p <= 0.05:
            rejections += 1
    fp_rate = rejections / n_splits
    fp_ok = (fp_rate <= 0.10)

    verdict = "PASSED" if (detect_ok and fp_ok) else "FAILED"
    return {
        "pc_verdict": verdict,
        "detect_p": float(detect_p),
        "detect_ok": bool(detect_ok),
        "false_pos_rate": float(fp_rate),
        "false_pos_ok": bool(fp_ok),
        "n_splits": int(n_splits),
    }


# ---------- main analysis ----------
def analyze(rows):
    ah = [r[1] for r in rows if r[0]]
    nah = [r[1] for r in rows if not r[0]]
    global_p = mw_p(ah, nah)
    global_dir = direction(ah, nah)

    # confound: within Tablet (largest document class)
    tab_ah = [r[1] for r in rows if r[0] and r[5] == "Tablet"]
    tab_nah = [r[1] for r in rows if (not r[0]) and r[5] == "Tablet"]
    within_tablet_p = mw_p(tab_ah, tab_nah)
    within_tablet_dir = direction(tab_ah, tab_nah)

    # confound: within Haghia Triada (largest site)
    ht_ah = [r[1] for r in rows if r[0] and r[4] == "Haghia Triada"]
    ht_nah = [r[1] for r in rows if (not r[0]) and r[4] == "Haghia Triada"]
    within_ht_p = mw_p(ht_ah, ht_nah)
    within_ht_dir = direction(ht_ah, ht_nah)

    # cross-site: per site with >=15 in each group
    sites = sorted(set(r[4] for r in rows if r[4] is not None))
    per_site = []
    for s in sites:
        a = [r[1] for r in rows if r[0] and r[4] == s]
        b = [r[1] for r in rows if (not r[0]) and r[4] == s]
        if len(a) >= 15 and len(b) >= 15:
            p = mw_p(a, b)
            per_site.append({
                "site": s, "n_ah": len(a), "n_nah": len(b),
                "mean_ah": float(np.mean(a)), "mean_nah": float(np.mean(b)),
                "p": float(p), "direction": direction(a, b),
                "sig": bool(p <= 0.05),
            })
    n_testable = len(per_site)
    n_sig = sum(1 for x in per_site if x["sig"])
    sig_dirs = [x["direction"] for x in per_site if x["sig"]]
    ref = sig_dirs if sig_dirs else [x["direction"] for x in per_site]
    consistent = bool(ref) and len(set(ref)) == 1

    # leave-one-site-out on HT
    not_ht_ah = [r[1] for r in rows if r[0] and r[4] != "Haghia Triada"]
    not_ht_nah = [r[1] for r in rows if (not r[0]) and r[4] != "Haghia Triada"]
    loo_p = mw_p(not_ht_ah, not_ht_nah)

    return {
        "global": {
            "n_a_headed": len(ah), "n_non_a_headed": len(nah),
            "density_a_headed": float(np.mean(ah)) if ah else 0.0,
            "density_non": float(np.mean(nah)) if nah else 0.0,
            "mw_p": float(global_p), "direction": global_dir,
        },
        "confound_control": {
            "within_tablet_p": float(within_tablet_p),
            "within_tablet_direction": within_tablet_dir,
            "within_tablet_n_ah": len(tab_ah), "within_tablet_n_nah": len(tab_nah),
            "within_HT_p": float(within_ht_p),
            "within_HT_direction": within_ht_dir,
            "within_HT_n_ah": len(ht_ah), "within_HT_n_nah": len(ht_nah),
        },
        "cross_site": {
            "n_sites_testable": int(n_testable),
            "n_sites_sig": int(n_sig),
            "direction_consistent": bool(consistent),
            "loo_p": float(loo_p),
            "per_site": per_site,
        },
    }


# ---------- verdict (FROZEN, mechanical) ----------
# Precedence (most specific / informative first):
#   1. PC failed                         -> MACHINERY_UNINFORMATIVE
#   2. global not significant            -> A_HEADING_NO_FUNCTION_DIFFERENCE
#   3. global sig AND survives within-Tablet AND within-HT (same dir)
#      AND >=2 sig sites same direction  -> A_HEADING_MARKS_DOC_FUNCTION_CROSS_SITE
#   4. global sig AND confound control SURVIVES (within-Tablet & within-HT sig,
#      same dir) BUT <2 testable sites   -> A_HEADING_FUNCTION_UNDERPOWERED
#      (effect is real within strata but cross-site robustness cannot be assessed)
#   5. otherwise (global sig but vanishes under confound control,
#      or <2 sig sites, or direction flips) -> A_HEADING_FUNCTION_SITE_LOCAL
def verdict(pc, an):
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    g = an["global"]
    if g["mw_p"] > 0.05:
        return "A_HEADING_NO_FUNCTION_DIFFERENCE"
    cc = an["confound_control"]
    cs = an["cross_site"]
    survives = (
        cc["within_tablet_p"] <= 0.05
        and cc["within_tablet_direction"] == g["direction"]
        and cc["within_HT_p"] <= 0.05
        and cc["within_HT_direction"] == g["direction"]
    )
    cross_ok = (cs["n_sites_sig"] >= 2 and cs["direction_consistent"]
                and all(x["direction"] == g["direction"] for x in cs["per_site"] if x["sig"]))
    if survives and cross_ok:
        return "A_HEADING_MARKS_DOC_FUNCTION_CROSS_SITE"
    if survives and cs["n_sites_testable"] < 2:
        return "A_HEADING_FUNCTION_UNDERPOWERED"
    return "A_HEADING_FUNCTION_SITE_LOCAL"


# ---------- self-check ----------
def _self_check():
    rows = load_rows()
    assert len(rows) > 0, "no rows loaded"
    pc = positive_control(rows)
    an = analyze(rows)
    v = verdict(pc, an)
    g = an["global"]
    assert g["n_a_headed"] + g["n_non_a_headed"] == len(rows)
    assert 0.0 <= g["density_a_headed"] <= 1.0
    assert 0.0 <= g["density_non"] <= 1.0
    assert pc["pc_verdict"] in ("PASSED", "FAILED")
    print("SELF-CHECK OK")
    print("  eligible rows:", len(rows))
    print("  A-headed:", g["n_a_headed"], " non-A-headed:", g["n_non_a_headed"])
    print("  global p:", round(g["mw_p"], 5), " dir:", g["direction"])
    print("  PC:", pc["pc_verdict"],
          "detect_p=", round(pc["detect_p"], 5),
          "fp_rate=", round(pc["false_pos_rate"], 4))
    print("  within-Tablet p:", round(an["confound_control"]["within_tablet_p"], 5),
          "dir:", an["confound_control"]["within_tablet_direction"])
    print("  within-HT p:", round(an["confound_control"]["within_HT_p"], 5),
          "dir:", an["confound_control"]["within_HT_direction"])
    print("  testable sites:", an["cross_site"]["n_sites_testable"],
          " sig:", an["cross_site"]["n_sites_sig"],
          " consistent:", an["cross_site"]["direction_consistent"])
    print("  LOO-HT p:", round(an["cross_site"]["loo_p"], 5))
    print("  VERDICT:", v)
    return rows, pc, an, v


if __name__ == "__main__":
    _self_check()
