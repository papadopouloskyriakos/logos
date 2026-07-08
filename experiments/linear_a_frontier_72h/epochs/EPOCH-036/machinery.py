#!/usr/bin/env python3
"""
EPOCH-036 machinery — CROSS-SITE SIGN-FREQUENCY CONCORDANCE (shared writing-system fingerprint).

Pure L2/L3 DISTRIBUTIONAL sign-usage statistics on ANONYMOUS sign ids. No phonetics, no sound,
no meaning, no reading. "Concordance" = mean pairwise Spearman rank correlation of per-site
sign-frequency vectors. It is a distributional statistic, NOT evidence of shared language.

FROZEN METRIC: CONCORDANCE = mean pairwise Spearman of per-site sign-frequency vectors over the
union inventory.

FROZEN NULL — WITHIN-SITE SIGN-LABEL SHUFFLE (calibrated by construction): for each site,
permute which count attaches to which sign id (full permutation over the union inventory on that
site's vector); recompute mean pairwise Spearman; >=1000 draws; one-sided p = frac draws with
shuffled concordance >= observed. Under H0 (no shared sign-IDENTITY fingerprint) shuffled
concordance ~ 0 (each site's frequency SHAPE preserved, identity alignment destroyed).

POSITIVE CONTROL (gates verdict) on LB (DĀMOS; NO site metadata -> SEEDED pseudo-site partition,
stated explicitly):
  - DETECT: LB is ONE shared script -> concordance MUST be significantly ABOVE shuffle null
    (p <= 0.05).
  - FALSE-POSITIVE: pseudo-sites with INDEPENDENT random-permutation frequency vectors (no shared
    fingerprint) -> rejection rate (frac p <= 0.05) MUST be <= 0.10 across >=20 control sets.
  Failure of either -> MACHINERY_UNINFORMATIVE.

Self-check: `python3 machinery.py` runs the full pipeline + PC and prints a JSON summary.
"""
import json, os, sys, random
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
from scipy.stats import spearmanr

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = .../experiments/linear_a_frontier_72h/epochs/EPOCH-036
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

# ---------- seeds / knobs (FROZEN) ----------
SEED_GLOBAL       = 20240760
SEED_NULL         = 20240761
SEED_PC_DETECT    = 20240762
SEED_PC_FP        = 20240763
SEED_LB_PARTITION = 20240764
SEED_FP_BASE      = 20240765
N_DRAWS           = 1000       # >=1000  (shuffle null)
PC_DETECT_DRAWS   = 1000
PC_FP_DRAWS       = 1000       # per control set
N_FP_SETS         = 20         # >=20
MIN_SITE_TOKENS   = 100        # qualifying-site threshold
N_LB_PSEUDOSITES  = 5          # >=5 seeded pseudo-sites
LB_CHUNK          = 1200       # wordforms per LB pseudo-site (seeded partition)
FP_PSEUDOSITES    = 5          # independent-permutation control pseudo-sites
FP_INVENTORY      = 60         # sign inventory size for FP control
FP_TOTAL          = 400        # total sign tokens per FP pseudo-site

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_b_damos():
    """Linear B positive-control benchmark. DĀMOS has NO site/inscription metadata.
    Returns a flat list of wordforms (each a list of signs)."""
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return seqs

# ---------- per-site sign frequencies ----------
def site_sign_frequencies(corpus):
    """site -> Counter(sign) over all word-token signs."""
    sf = defaultdict(Counter)
    for ins in corpus:
        site = ins.get("site")
        if not site:
            continue
        for tok in ins.get("stream", []) or []:
            if tok.get("t") == "word":
                for s in (tok.get("signs") or []):
                    sf[site][s] += 1
    return sf

def qualifying_sites(sf, min_tokens=MIN_SITE_TOKENS):
    return {s: c for s, c in sf.items() if sum(c.values()) >= min_tokens}

# ---------- concordance metric ----------
def build_vectors(qual):
    """Return (sites_sorted, union_inventory, {site: np.ndarray freq vector})."""
    sites = sorted(qual)
    union = sorted(set().union(*[set(qual[s]) for s in sites]))
    U = len(union)
    idx = {s: i for i, s in enumerate(union)}
    V = {}
    for s in sites:
        v = np.zeros(U, dtype=float)
        for sg, c in qual[s].items():
            v[idx[sg]] = c
        V[s] = v
    return sites, union, V

def mean_pair_spearman(vecs):
    """Mean pairwise Spearman over a list of vectors; also returns the list of pair rs."""
    rs = []
    for a, b in combinations(vecs, 2):
        r = spearmanr(a, b).correlation
        if r is None or (isinstance(r, float) and np.isnan(r)):
            r = 0.0
        rs.append(float(r))
    if not rs:
        return 0.0, []
    return float(np.mean(rs)), rs

def per_site_mean_corr(V, sites):
    """For each site, mean Spearman to all other sites."""
    out = {}
    for s in sites:
        rs = []
        for o in sites:
            if o == s:
                continue
            r = spearmanr(V[s], V[o]).correlation
            if r is None or (isinstance(r, float) and np.isnan(r)):
                r = 0.0
            rs.append(float(r))
        out[s] = float(np.mean(rs)) if rs else 0.0
    return out

# ---------- FROZEN NULL: within-site sign-label shuffle ----------
def shuffle_null(V, sites, n_draws, seed):
    """For each site, permute which count attaches to which union-inventory sign id
    (full permutation over the inventory on that site's vector). Recompute mean pairwise
    Spearman. One-sided p = frac draws with shuffled >= observed."""
    rng = random.Random(seed)
    U = len(V[sites[0]])
    observed, _ = mean_pair_spearman([V[s] for s in sites])
    nulls = []
    for _ in range(n_draws):
        perm_vecs = []
        for s in sites:
            v = V[s].copy()
            perm = rng.sample(range(U), U)
            v2 = np.zeros(U, dtype=float)
            for i in range(U):
                v2[perm[i]] = v[i]
            perm_vecs.append(v2)
        m, _ = mean_pair_spearman(perm_vecs)
        nulls.append(m)
    nulls = np.array(nulls)
    p = float((nulls >= observed).mean())
    return observed, float(nulls.mean()), float(nulls.std()), p, nulls

# ---------- LB positive control ----------
def lb_pseudo_sites(seqs, n_sites=N_LB_PSEUDOSITES, chunk=LB_CHUNK, seed=SEED_LB_PARTITION):
    """SEEDED partition of LB wordforms into n_sites pseudo-sites (chunk wordforms each).
    Returns {pseudo_site_id: Counter(sign)}."""
    rng = random.Random(seed)
    seqs = list(seqs)
    rng.shuffle(seqs)
    sf = {}
    for k in range(n_sites):
        slab = seqs[k * chunk:(k + 1) * chunk]
        c = Counter()
        for w in slab:
            for s in w:
                c[s] += 1
        sf[f"LB_{k}"] = c
    return sf

def independent_perm_pseudo_sites(n_sites=FP_PSEUDOSITES, inventory=FP_INVENTORY,
                                  total=FP_TOTAL, seed=SEED_FP_BASE):
    """Pseudo-sites whose frequency vectors are INDEPENDENT random permutations of independent
    random frequency multisets -> NO shared fingerprint (exact H0 for the false-positive arm)."""
    rng = random.Random(seed)
    sf = {}
    for k in range(n_sites):
        # independent random frequency multiset (Zipf-ish via random weights) over the inventory
        weights = np.array([rng.random() for _ in range(inventory)])
        weights = weights / weights.sum()
        counts = np.random.default_rng(rng.randint(0, 2**31 - 1)).multinomial(total, weights)
        # then INDEPENDENTLY permute which sign each count lands on
        perm = list(range(inventory))
        rng.shuffle(perm)
        c = Counter()
        for i, cnt in enumerate(counts):
            if cnt > 0:
                c[f"S{perm[i]}"] = int(cnt)
        sf[f"FP_{k}"] = c
    return sf

def concordance_test(sf, n_draws, seed):
    """Run the concordance metric + shuffle null on a site->Counter map. Returns dict."""
    qual = {s: c for s, c in sf.items() if sum(c.values()) > 0}
    sites, union, V = build_vectors(qual)
    if len(sites) < 2:
        return {"mean_spearman": None, "null_mean": None, "null_p": None, "n_sites": len(sites)}
    obs, nmean, nstd, p, _ = shuffle_null(V, sites, n_draws, seed)
    return {"mean_spearman": obs, "null_mean": nmean, "null_std": nstd, "null_p": p,
            "n_sites": len(sites), "union_inventory": len(union)}

def positive_control(lb_seqs):
    """(a) DETECT on LB seeded pseudo-sites; (b) FALSE-POSITIVE on independent-perm controls."""
    # (a) DETECT
    lb_sf = lb_pseudo_sites(lb_seqs)
    det = concordance_test(lb_sf, PC_DETECT_DRAWS, SEED_PC_DETECT)
    detect_p = det["null_p"]
    detect_ok = (detect_p is not None) and (detect_p <= 0.05) and (det["mean_spearman"] is not None)

    # (b) FALSE-POSITIVE: across N_FP_SETS independent control sets, fraction with p <= 0.05
    fps = []
    for k in range(N_FP_SETS):
        sf = independent_perm_pseudo_sites(seed=SEED_FP_BASE + 1000 * k)
        r = concordance_test(sf, PC_FP_DRAWS, SEED_PC_FP + k)
        fps.append(r["null_p"])
    fps = [p for p in fps if p is not None]
    fpr = float(np.mean([1.0 if p <= 0.05 else 0.0 for p in fps])) if fps else 1.0
    fp_ok = fpr <= 0.10

    passed = bool(detect_ok and fp_ok)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "lb_detect_p": detect_p,
        "lb_detect_mean_spearman": det.get("mean_spearman"),
        "lb_detect_null_mean": det.get("null_mean"),
        "false_pos_rate": fpr,
        "n_fp_sets": len(fps),
    }

# ---------- LA main: leave-one-out + outlier ----------
def leave_one_out(V, sites):
    """Recompute concordance with each site removed in turn."""
    loo = {}
    for s in sites:
        rest = [o for o in sites if o != s]
        m, _ = mean_pair_spearman([V[o] for o in rest])
        loo[s] = m
    return loo

def detect_outlier(per_site):
    """Flag a low outlier: >2 SD below the across-site mean, OR clear min with a gap to next.
    Returns (site_or_None, mean_corr, gap_to_next)."""
    items = sorted(per_site.items(), key=lambda kv: kv[1])
    vals = np.array([v for _, v in items])
    mu = float(vals.mean()); sd = float(vals.std(ddof=0)) or 1e-9
    lowest_site, lowest_val = items[0]
    next_val = items[1][1] if len(items) > 1 else lowest_val
    gap = float(lowest_val - next_val)  # <= 0 means lowest is below next
    # outlier if >2 SD below mean OR (clear min: gap to next >= 1 SD of the per-site values)
    is_outlier = (lowest_val < mu - 2 * sd) or (gap <= -sd)
    if is_outlier:
        return lowest_site, lowest_val, abs(gap)
    return None, lowest_val, abs(gap)

# ---------- full pipeline ----------
def run():
    out = {"task_id": "EPOCH-036"}
    corpus = load_corpus()
    sf = site_sign_frequencies(corpus)
    qual = qualifying_sites(sf)
    n_sites = len(qual)

    # UNDERPOWERED gate
    if n_sites < 4:
        out["verdict"] = "SIGN_FREQ_UNDERPOWERED"
        out["numbers"] = {"global": {"n_sites": n_sites, "union_inventory": 0,
                                     "mean_spearman": None, "null_mean": None, "null_p": None}}
        return out

    sites, union, V = build_vectors(qual)

    # POSITIVE CONTROL FIRST (gates verdict)
    lb_seqs = load_b_damos()
    pc = positive_control(lb_seqs)
    out["positive_control"] = pc
    if pc["pc_verdict"] != "PASSED":
        out["verdict"] = "MACHINERY_UNINFORMATIVE"
        # still report global for transparency
        obs, nmean, nstd, p, _ = shuffle_null(V, sites, N_DRAWS, SEED_NULL)
        out["numbers"] = {"global": {"n_sites": n_sites, "union_inventory": len(union),
                                     "mean_spearman": obs, "null_mean": nmean, "null_p": p}}
        return out

    # GLOBAL
    obs, nmean, nstd, p, _ = shuffle_null(V, sites, N_DRAWS, SEED_NULL)
    global_ = {"n_sites": n_sites, "union_inventory": len(union),
               "mean_spearman": obs, "null_mean": nmean, "null_p": p}

    # LA MAIN
    loo = leave_one_out(V, sites)
    psm = per_site_mean_corr(V, sites)
    out_site, out_val, out_gap = detect_outlier(psm)

    # FROZEN VERDICT
    significant = (p is not None) and (p <= 0.05)
    # survives LOO: every LOO concordance still clearly above the null mean
    survives_loo = all(v > nmean + 3 * nstd for v in loo.values())
    has_outlier = out_site is not None

    if significant and survives_loo and not has_outlier:
        verdict = "SIGN_FREQ_CONCORDANCE_CROSS_SITE"
    elif significant and has_outlier:
        verdict = "SIGN_FREQ_CONCORDANCE_WITH_OUTLIER"
    else:
        verdict = "SIGN_FREQ_NO_CONCORDANCE"

    out["verdict"] = verdict
    out["numbers"] = {
        "global": global_,
        "positive_control": {"pc_verdict": pc["pc_verdict"], "lb_detect_p": pc["lb_detect_p"],
                             "false_pos_rate": pc["false_pos_rate"]},
        "per_site_mean_corr": psm,
        "outlier": {"site": out_site, "mean_corr": out_val, "gap_to_next": out_gap},
        "leave_one_out": loo,
    }
    return out

if __name__ == "__main__":
    res = run()
    print(json.dumps(res, ensure_ascii=False, indent=2))
