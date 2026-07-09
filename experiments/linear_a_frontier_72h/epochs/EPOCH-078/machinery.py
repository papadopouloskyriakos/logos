"""
EPOCH-078 machinery — Glyph-Size Economy of Effort (cross-site, class-controlled).
L2 only: signs are OPAQUE catalog IDs; size = within-doc z-scored log bbox-area;
frequency = corpus glyph count; class control (AB syllabary vs A); frequency-label
shuffle null. size ⊥ frequency by construction.

Frozen against prereg.md (see plan_hash.txt).
"""
import json, math, collections, statistics, random, os

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, "..", ".."))  # experiments/linear_a_frontier_72h
DATA_GLYPHS = os.path.join(CAMP, "data", "sigla_glyphs_bbox.json")
DATA_CLASS = os.path.join(CAMP, "data", "sigla_sign_class.json")

MIN_DOC_GLYPHS = 4      # >=4 non-divider glyphs per doc
MIN_FREQ = 8            # global freq cutoff for kept signs
MIN_SITE_FREQ = 5       # per-site freq cutoff
N_PERM = 2000
PC_REPS = 25
PC_ALPHA = 0.05
PC_FP_MAX = 0.10
PC_POWER_MIN = 0.5


def _zscore(vals):
    m = statistics.mean(vals)
    s = statistics.pstdev(vals)
    if s == 0:
        return [0.0 for _ in vals]
    return [(v - m) / s for v in vals]


def load_data():
    docs = json.load(open(DATA_GLYPHS))
    cls = json.load(open(DATA_CLASS))
    good = [d for d in docs
            if sum(1 for g in d["glyphs"] if not g.get("is_divider")) >= MIN_DOC_GLYPHS]
    return good, cls


def per_sign_table(docs):
    """Global per-sign mean within-doc z-size and corpus frequency."""
    per_sign_z = collections.defaultdict(list)
    freq = collections.Counter()
    for d in docs:
        gs = [g for g in d["glyphs"] if not g.get("is_divider")]
        las = [math.log(g["bbox"][2] * g["bbox"][3]) for g in gs]
        zs = _zscore(las)
        for g, z in zip(gs, zs):
            per_sign_z[g["sign"]].append(z)
            freq[g["sign"]] += 1
    return per_sign_z, freq


def site_per_sign_table(docs, site):
    """Per-sign mean within-doc z-size and freq using ONLY one site's glyphs."""
    per_sign_z = collections.defaultdict(list)
    freq = collections.Counter()
    for d in docs:
        if d.get("site") != site:
            continue
        gs = [g for g in d["glyphs"] if not g.get("is_divider")]
        if len(gs) < MIN_DOC_GLYPHS:
            continue
        las = [math.log(g["bbox"][2] * g["bbox"][3]) for g in gs]
        zs = _zscore(las)
        for g, z in zip(gs, zs):
            per_sign_z[g["sign"]].append(z)
            freq[g["sign"]] += 1
    return per_sign_z, freq


def pearson(x, y):
    if len(x) < 2:
        return float("nan")
    return statistics.correlation(x, y)


def corr_over_signs(signs, per_sign_z, freq):
    signs = [s for s in signs if freq.get(s, 0) > 0]
    if len(signs) < 2:
        return float("nan")
    x = [math.log(freq[s]) for s in signs]
    y = [statistics.mean(per_sign_z[s]) for s in signs]
    return pearson(x, y)


def shuffle_null(signs, per_sign_z, freq, observed, n_perm=N_PERM, seed=12345):
    """Frequency-LABEL shuffle: permute {sign -> log(freq)} over kept signs; one-sided
    perm p = frac(null r <= observed r)."""
    signs = [s for s in signs if freq.get(s, 0) > 0]
    if len(signs) < 2:
        return float("nan")
    lf = [math.log(freq[s]) for s in signs]
    mz = [statistics.mean(per_sign_z[s]) for s in signs]
    rng = random.Random(seed)
    le = 0
    for _ in range(n_perm):
        perm = lf[:]
        rng.shuffle(perm)
        r = pearson(perm, mz)
        if r <= observed:
            le += 1
    return (le + 1) / (n_perm + 1)  # +1 smoothing


# ---------------- POSITIVE CONTROL (synthetic) ----------------

def _synthetic_detect(seed):
    """Plant signs where size decreases with planted freq."""
    rng = random.Random(seed)
    n = 60
    freqs = [rng.randint(8, 400) for _ in range(n)]
    lf = [math.log(f) for f in freqs]
    # true economy: mean_z = -0.35*lf + noise
    mz = [-0.35 * x + rng.gauss(0, 0.45) for x in lf]
    obs = pearson(lf, mz)
    # shuffle null
    le = 0
    for _ in range(500):
        p = lf[:]; rng.shuffle(p)
        if pearson(p, mz) <= obs:
            le += 1
    p = (le + 1) / 501
    return obs, p


def _synthetic_fp(seed):
    """Plant size independent of freq."""
    rng = random.Random(seed + 99999)
    n = 60
    freqs = [rng.randint(8, 400) for _ in range(n)]
    lf = [math.log(f) for f in freqs]
    mz = [rng.gauss(0, 1.0) for _ in range(n)]  # no association
    obs = pearson(lf, mz)
    le = 0
    for _ in range(500):
        p = lf[:]; rng.shuffle(p)
        if pearson(p, mz) <= obs:
            le += 1
    p = (le + 1) / 501
    return obs, p


def positive_control():
    detect_ps = []
    for i in range(PC_REPS):
        _, p = _synthetic_detect(i)
        detect_ps.append(p)
    power_est = statistics.mean(1 if p <= PC_ALPHA else 0 for p in detect_ps)
    detect_p = statistics.median(detect_ps)
    fp_ps = []
    for i in range(PC_REPS):
        _, p = _synthetic_fp(i)
        fp_ps.append(p)
    false_pos_rate = statistics.mean(1 if p <= PC_ALPHA else 0 for p in fp_ps)
    passed = (power_est >= PC_POWER_MIN) and (false_pos_rate <= PC_FP_MAX)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": detect_p,
        "power_est": power_est,
        "false_pos_rate": false_pos_rate,
        "pc_is_synthetic": True,
    }


# ---------------- SELF-CHECK ----------------

def self_check():
    """Frequency-shuffle null must give E[r] ~ 0 on label-shuffled data."""
    rng = random.Random(2024)
    n = 80
    lf = [math.log(rng.randint(8, 400)) for _ in range(n)]
    mz = [rng.gauss(0, 1.0) for _ in range(n)]  # independent
    rs = []
    for _ in range(400):
        p = lf[:]; rng.shuffle(p)
        rs.append(pearson(p, mz))
    mean_r = statistics.mean(rs)
    print(f"[self-check] mean null r on independent data = {mean_r:.4f} (expect ~0)")
    assert abs(mean_r) < 0.10, f"self-check FAILED: mean null r={mean_r}"
    print("[self-check] PASSED")
    return mean_r


if __name__ == "__main__":
    mr = self_check()
    print("self_check mean_r =", round(mr, 4))
