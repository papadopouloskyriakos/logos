"""
EPOCH-076 machinery: cross-site normalized glyph-size profile correlation.

L2 ONLY. Signs are OPAQUE catalog IDs (no value/reading/meaning used).
Glyph size = bbox area; within-document z-scored log-area removes per-photo scale.
Null = sign-label shuffle (destroys sign->size association).
"""
import json, math, os, random
from collections import defaultdict
import itertools

DATA = "experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"

# ---------- data loading ----------
def usable_glyphs(doc):
    """Return list of (sign, area) for non-divider bbox glyphs with w,h>0."""
    out = []
    for gg in doc.get("glyphs", []):
        if gg.get("is_divider"):
            continue
        b = gg.get("bbox")
        if not b or len(b) < 4:
            continue
        try:
            x, y, w, h = float(b[0]), float(b[1]), float(b[2]), float(b[3])
        except (TypeError, ValueError):
            continue
        if w <= 0 or h <= 0:
            continue
        out.append((gg.get("sign"), w * h))
    return out

def load_docs(path=DATA):
    return json.load(open(path))

def normalized_sizes(docs):
    """
    For each doc with >=4 non-divider bbox glyphs:
      log-area = log(max(1, area)); within-doc z-score (population sd; sd=0 -> 1).
    Returns list of (site, sign, norm_size) with sign filtered to non-None strings.
    """
    recs = []
    for doc in docs:
        ug = usable_glyphs(doc)
        if len(ug) < 4:
            continue
        las = [math.log(max(1.0, a)) for (_, a) in ug]
        mu = sum(las) / len(las)
        var = sum((v - mu) ** 2 for v in las) / len(las)
        sd = math.sqrt(var) if var > 0 else 1.0
        if sd == 0:
            sd = 1.0
        for (sign, a), la in zip(ug, las):
            if sign is None or not isinstance(sign, str):
                continue
            recs.append((doc.get("site"), sign, (la - mu) / sd))
    return recs

def site_doc_counts(docs):
    cnt = defaultdict(int)
    for doc in docs:
        ug = usable_glyphs(doc)
        if len(ug) >= 4:
            cnt[doc.get("site")] += 1
    return cnt

def build_profiles(recs, big, min_obs=5):
    """
    Per (site, sign) mean norm size over signs with >=min_obs glyphs at that site.
    Returns {site: {sign: mean_norm_size}} restricted to big sites.
    """
    agg = defaultdict(lambda: defaultdict(list))
    for site, sign, z in recs:
        if site in big:
            agg[site][sign].append(z)
    profiles = {}
    for s in big:
        profiles[s] = {sign: sum(v) / len(v) for sign, v in agg[s].items() if len(v) >= min_obs}
    return profiles

# ---------- correlation ----------
def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx <= 0 or syy <= 0:
        return float("nan")
    return sxy / math.sqrt(sxx * syy)

def pair_r(prof_a, prof_b, min_common=8):
    common = sorted(set(prof_a) & set(prof_b))
    if len(common) < min_common:
        return None, common
    xs = [prof_a[s] for s in common]
    ys = [prof_b[s] for s in common]
    return pearson(xs, ys), common

# ---------- null: sign-label shuffle ----------
def perm_p(prof_a, prof_b, r_obs, min_common=8, n_draws=2000, rng=None):
    """
    Permute sign->size assignment in ONE site's profile (site b) over common signs;
    one-sided p = frac(null r >= observed).
    """
    if rng is None:
        rng = random.Random(0)
    common = sorted(set(prof_a) & set(prof_b))
    if len(common) < min_common:
        return None
    xs = [prof_a[s] for s in common]
    ys_orig = [prof_b[s] for s in common]
    ge = 0
    valid = 0
    for _ in range(n_draws):
        ys = ys_orig[:]
        rng.shuffle(ys)
        r = pearson(xs, ys)
        if r != r:  # nan
            continue
        valid += 1
        if r >= r_obs:
            ge += 1
    if valid == 0:
        return None
    return ge / valid

# ---------- positive control (synthetic) ----------
def synth_shared(n_sites=5, n_signs=30, n_docs_per_site=20, glyphs_per_doc=12,
                 noise=0.6, seed=0):
    """Each sign has a FIXED intrinsic size across sites + per-glyph noise."""
    rng = random.Random(seed)
    intrinsic = {f"S{i}": rng.gauss(0, 1) for i in range(n_signs)}
    docs = []
    for site in range(n_sites):
        for di in range(n_docs_per_site):
            glyphs = []
            for _ in range(glyphs_per_doc):
                sign = rng.choice(list(intrinsic))
                z = intrinsic[sign] + rng.gauss(0, noise)
                a = math.exp(z)
                glyphs.append({"sign": sign, "bbox": [0, 0, a, 1.0], "is_divider": False})
            docs.append({"site": f"site{site}", "glyphs": glyphs})
    return docs

def synth_idiosyncratic(n_sites=5, n_signs=30, n_docs_per_site=20, glyphs_per_doc=12,
                        seed=0):
    """Each site assigns sizes to signs INDEPENDENTLY at random (site-local)."""
    rng = random.Random(seed)
    site_size = {}
    for site in range(n_sites):
        site_size[site] = {f"S{i}": rng.gauss(0, 1) for i in range(n_signs)}
    docs = []
    for site in range(n_sites):
        for di in range(n_docs_per_site):
            glyphs = []
            for _ in range(glyphs_per_doc):
                sign = rng.choice(list(site_size[site]))
                z = site_size[site][sign] + rng.gauss(0, 0.6)
                a = math.exp(z)
                glyphs.append({"sign": sign, "bbox": [0, 0, a, 1.0], "is_divider": False})
            docs.append({"site": f"site{site}", "glyphs": glyphs})
    return docs

def analyze_docs(docs, min_docs=15, min_obs=5, min_common=8, n_draws=2000, rng=None):
    """Run full pipeline on a doc list; return summary dict."""
    if rng is None:
        rng = random.Random(12345)
    sdc = site_doc_counts(docs)
    big = [s for s, c in sdc.items() if c >= min_docs]
    recs = normalized_sizes(docs)
    profiles = build_profiles(recs, set(big), min_obs=min_obs)
    pairs = []
    for a, b in itertools.combinations(sorted(big), 2):
        r, common = pair_r(profiles[a], profiles[b], min_common=min_common)
        if r is None:
            continue
        p = perm_p(profiles[a], profiles[b], r, min_common=min_common, n_draws=n_draws, rng=rng)
        pairs.append({"site_a": a, "site_b": b, "n_common": len(common),
                      "r": r, "perm_p": p, "sig": bool(p is not None and p <= 0.05 and r > 0)})
    rs = [pp["r"] for pp in pairs]
    med = sorted(rs)[len(rs) // 2] if rs else float("nan")
    return {"pairs": pairs, "n_pairs_testable": len(pairs),
            "n_pairs_sig": sum(1 for pp in pairs if pp["sig"]),
            "median_r": med, "profiles": profiles}

def run_positive_control(n_reps=20, n_draws=2000):
    """
    Canonical PC. IMPORTANT: data-generation seed and permutation RNG seed are
    FULLY DECOUPLED (independent streams) to avoid seed-coupling artifacts.
    Returns dict with detect_power, detect_r, false_pos_rate, pc_verdict.
    """
    sh_hits = 0; sh_r = []; id_hits = 0; id_r = []
    for rep in range(n_reps):
        docs = synth_shared(seed=1000 + rep * 7)
        res = analyze_docs(docs, min_docs=15, min_obs=5, min_common=8,
                           n_draws=n_draws, rng=random.Random(9000 + rep * 13))
        if res["n_pairs_sig"] >= 2:
            sh_hits += 1
        sh_r.append(res["median_r"])
        docs = synth_idiosyncratic(seed=2000 + rep * 7)
        res = analyze_docs(docs, min_docs=15, min_obs=5, min_common=8,
                           n_draws=n_draws, rng=random.Random(8000 + rep * 13))
        if res["n_pairs_sig"] >= 2:
            id_hits += 1
        id_r.append(res["median_r"])
    power = sh_hits / n_reps
    fpr = id_hits / n_reps
    detect_r = sum(sh_r) / n_reps
    pc_pass = (power >= 0.5) and (fpr <= 0.10)
    return {"pc_verdict": "PASSED" if pc_pass else "FAILED",
            "detect_power": power, "detect_r": detect_r,
            "false_pos_rate": fpr, "idio_r_mean": sum(id_r) / n_reps,
            "n_reps": n_reps, "pc_is_synthetic": True}

# ---------- self-check ----------
def self_check():
    print("=== SELF-CHECK ===")
    docs = load_docs()
    max_abs_mean = 0.0
    n_checked = 0
    for doc in docs:
        ug = usable_glyphs(doc)
        if len(ug) < 4:
            continue
        las = [math.log(max(1.0, a)) for (_, a) in ug]
        mu = sum(las) / len(las)
        var = sum((v - mu) ** 2 for v in las) / len(las)
        sd = math.sqrt(var) if var > 0 else 1.0
        zs = [(la - mu) / sd for la in las]
        m = sum(zs) / len(zs)
        max_abs_mean = max(max_abs_mean, abs(m))
        n_checked += 1
    print(f"within-doc z-score: max|mean| over {n_checked} docs = {max_abs_mean:.2e} (should be ~0)")
    assert max_abs_mean < 1e-9, "z-score mean not ~0"

    rng = random.Random(7)
    rs_null = []
    for _ in range(50):
        n = 20
        xs = [rng.gauss(0, 1) for _ in range(n)]
        ys = [rng.gauss(0, 1) for _ in range(n)]
        rs_null.append(pearson(xs, ys))
    mean_r = sum(rs_null) / len(rs_null)
    print(f"null Pearson E[r] over 50 random pairs (n=20) = {mean_r:.4f} (should be ~0)")
    assert abs(mean_r) < 0.2, "null E[r] not ~0"

    rng2 = random.Random(11)
    prof_a = {f"S{i}": rng2.gauss(0, 1) for i in range(15)}
    prof_b = {f"S{i}": rng2.gauss(0, 1) for i in range(15)}
    r_obs, _ = pair_r(prof_a, prof_b, min_common=8)
    p = perm_p(prof_a, prof_b, r_obs, min_common=8, n_draws=2000, rng=random.Random(3))
    print(f"null-data observed r={r_obs:.4f}, perm_p={p:.4f} (should be high)")
    print("=== SELF-CHECK PASSED ===")

if __name__ == "__main__":
    self_check()
