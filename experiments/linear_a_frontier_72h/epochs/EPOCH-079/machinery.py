"""
EPOCH-079 machinery — Inter-Glyph Spacing Regularity (ruled / monospaced-like), cross-site.
L2 only: signs are OPAQUE catalog IDs; only glyph POSITIONS matter.
A ROW = y-band (cluster by y-center within 0.6 x median glyph-height). Within a row (>=3 glyphs),
sort by x-center; PITCH = consecutive center-to-center distance. Doc pitch-CV = sd/mean of pooled
within-row pitches. S_obs = MEDIAN doc pitch-CV. NULL = random-composition of each row's pitches
(uniform Dirichlet / random breakpoints on the SAME row span), preserving row span + glyph count,
destroying only the regularity. Regular layout => observed pitch-CV << null pitch-CV.

Frozen against prereg.md (see plan_hash.txt).
"""
import json, math, statistics, random, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, "..", ".."))  # experiments/linear_a_frontier_72h
DATA_GLYPHS = os.path.join(CAMP, "data", "sigla_glyphs_bbox.json")

MIN_DOC_GLYPHS = 6      # >=6 non-divider glyphs per doc
MIN_ROW = 3             # rows with >=3 glyphs contribute pitches
ROW_TOL_FACTOR = 0.6    # y-band tolerance = 0.6 x median glyph-height
N_PERM = 1000           # null draws
PC_REPS = 25
PC_ALPHA = 0.05
PC_FP_MAX = 0.10
PC_POWER_MIN = 0.5
MIN_SITE_DOCS = 15


# ---------- geometry helpers ----------

def _rows_of(glyphs):
    """Cluster non-divider glyphs into rows by y-center within 0.6 x median glyph-height.
    Returns list of rows (each a list of glyph dicts) and the median glyph-height."""
    gs = [g for g in glyphs if not g.get("is_divider")]
    if not gs:
        return [], 0.0
    heights = [g["bbox"][3] for g in gs]
    med_h = statistics.median(heights)
    tol = ROW_TOL_FACTOR * med_h
    yc = [g["bbox"][1] + g["bbox"][3] / 2.0 for g in gs]
    order = sorted(range(len(gs)), key=lambda i: yc[i])
    rows_idx = []
    cur = []
    for i in order:
        if not cur:
            cur = [i]
        else:
            my = statistics.mean(yc[j] for j in cur)
            if abs(yc[i] - my) <= tol:
                cur.append(i)
            else:
                rows_idx.append(cur)
                cur = [i]
    if cur:
        rows_idx.append(cur)
    rows = [[gs[i] for i in r] for r in rows_idx]
    return rows, med_h


def _row_pitches(row):
    """Sort row by x-center; return consecutive center-to-center pitches."""
    xc = sorted(g["bbox"][0] + g["bbox"][2] / 2.0 for g in row)
    return [xc[k + 1] - xc[k] for k in range(len(xc) - 1)]


def doc_row_pitches(glyphs):
    """Return list of pitch-lists, one per row with >=3 glyphs."""
    rows, _ = _rows_of(glyphs)
    out = []
    for r in rows:
        if len(r) >= MIN_ROW:
            p = _row_pitches(r)
            if len(p) >= 1:
                out.append(p)
    return out


def _cv(vals):
    if len(vals) < 2:
        return None
    m = statistics.mean(vals)
    if m == 0:
        return None
    return statistics.pstdev(vals) / m


def doc_pitch_cv(glyphs):
    """Doc pitch-CV = sd/mean of pooled within-row pitches."""
    rp = doc_row_pitches(glyphs)
    pool = [p for row in rp for p in row]
    return _cv(pool)


# ---------- random-composition null ----------

def _rand_composition(n_parts, total, rng):
    """Random composition of n_parts positive values summing to `total`
    via uniform Dirichlet = random breakpoints on the span."""
    if n_parts <= 0:
        return []
    if n_parts == 1:
        return [float(total)]
    # n_parts-1 random breakpoints in (0, total), sorted
    bps = sorted(rng.uniform(0, total) for _ in range(n_parts - 1))
    vals = []
    prev = 0.0
    for b in bps:
        vals.append(b - prev)
        prev = b
    vals.append(total - prev)
    return vals


def null_doc_pitch_cv(glyphs, rng):
    """Replace each row's pitches with a random composition of the SAME row pitch-total,
    recompute doc pitch-CV."""
    rp = doc_row_pitches(glyphs)
    pool = []
    for row in rp:
        total = sum(row)
        n = len(row)  # n_row - 1 pitches
        pool.extend(_rand_composition(n, total, rng))
    return _cv(pool)


# ---------- corpus statistic ----------

def corpus_S(docs_glyphs):
    """S = median doc pitch-CV over docs (glyphs lists)."""
    cvs = [doc_pitch_cv(g) for g in docs_glyphs]
    cvs = [c for c in cvs if c is not None]
    if not cvs:
        return None
    return statistics.median(cvs)


def null_corpus_S(docs_glyphs, rng):
    """One null draw of S: per-doc random-composition null, then median."""
    cvs = [null_doc_pitch_cv(g, rng) for g in docs_glyphs]
    cvs = [c for c in cvs if c is not None]
    if not cvs:
        return None
    return statistics.median(cvs)


def perm_test(docs_glyphs, n_perm=N_PERM, seed=79):
    """One-sided perm p = frac(null S <= S_obs). Returns (S_obs, null_draws, perm_p)."""
    rng = random.Random(seed)
    S_obs = corpus_S(docs_glyphs)
    nulls = []
    for _ in range(n_perm):
        nulls.append(null_corpus_S(docs_glyphs, rng))
    null_med = statistics.median(nulls)
    perm_p = sum(1 for s in nulls if s <= S_obs) / len(nulls)
    return S_obs, null_med, nulls, perm_p


# ---------- data loading ----------

def load_usable():
    docs = json.load(open(DATA_GLYPHS))
    usable = []
    for d in docs:
        gs = [g for g in d["glyphs"] if not g.get("is_divider")]
        if len(gs) < MIN_DOC_GLYPHS:
            continue
        rows, _ = _rows_of(d["glyphs"])
        if any(len(r) >= MIN_ROW for r in rows):
            usable.append(d)
    return usable


# ---------- synthetic PC builders ----------

def _synth_doc_regular(n_rows, glyphs_per_row, pitch, jitter_frac, rng, h=100, w=80):
    """Build a doc with REGULAR pitches (low CV): each row has glyphs_per_row glyphs at near-equal pitch."""
    glyphs = []
    y = 0
    for r in range(n_rows):
        y += h + 40
        # start x
        x = rng.uniform(20, 60)
        xs = [x]
        for k in range(glyphs_per_row - 1):
            j = pitch * jitter_frac
            xs.append(xs[-1] + pitch + rng.uniform(-j, j))
        for xx in xs:
            glyphs.append({"sign": "X", "bbox": [xx, y, w, h], "is_divider": False})
    return glyphs


def _synth_doc_random(n_rows, glyphs_per_row, span, rng, h=100, w=80):
    """Build a doc with RANDOM-composition pitches (CV ~ null): each row's pitches are a random
    composition of `span`."""
    glyphs = []
    y = 0
    for r in range(n_rows):
        y += h + 40
        n_p = glyphs_per_row - 1
        pitches = _rand_composition(n_p, span, rng)
        x = rng.uniform(20, 60)
        xs = [x]
        for p in pitches:
            xs.append(xs[-1] + p)
        for xx in xs:
            glyphs.append({"sign": "X", "bbox": [xx, y, w, h], "is_divider": False})
    return glyphs


def _synth_corpus_regular(n_docs, rng):
    docs = []
    for _ in range(n_docs):
        nr = rng.randint(2, 4)
        gp = rng.randint(3, 6)
        pitch = rng.uniform(120, 200)
        jf = rng.uniform(0.02, 0.08)  # small jitter => low CV
        docs.append(_synth_doc_regular(nr, gp, pitch, jf, rng))
    return docs


def _synth_corpus_random(n_docs, rng):
    docs = []
    for _ in range(n_docs):
        nr = rng.randint(2, 4)
        gp = rng.randint(3, 6)
        span = rng.uniform(500, 900)
        docs.append(_synth_doc_random(nr, gp, span, rng))
    return docs


def positive_control(n_docs=40, reps=PC_REPS, seed=7900):
    """(a) DETECT: regular synth should be flagged (perm p<=0.05). power_est = frac flagged.
       (b) FALSE-POSITIVE: random synth should NOT be flagged. fp_rate = frac flagged."""
    rng = random.Random(seed)
    detect_ps = []
    for _ in range(reps):
        docs = _synth_corpus_regular(n_docs, rng)
        S_obs, null_med, nulls, p = perm_test(docs, n_perm=200, seed=rng.randint(0, 10**9))
        detect_ps.append(p)
    power_est = sum(1 for p in detect_ps if p <= PC_ALPHA) / len(detect_ps)
    detect_p_med = statistics.median(detect_ps)

    fp_ps = []
    for _ in range(reps):
        docs = _synth_corpus_random(n_docs, rng)
        S_obs, null_med, nulls, p = perm_test(docs, n_perm=200, seed=rng.randint(0, 10**9))
        fp_ps.append(p)
    fp_rate = sum(1 for p in fp_ps if p <= PC_ALPHA) / len(fp_ps)
    return {
        "detect_p_med": detect_p_med,
        "power_est": power_est,
        "fp_rate": fp_rate,
        "passed": (power_est >= PC_POWER_MIN) and (fp_rate <= PC_FP_MAX),
    }


# ---------- self-check ----------

def self_check():
    """Confirm: (a) on REGULAR synthetic, observed CV << null CV (null higher);
    (b) on RANDOM synthetic, observed CV ~ null CV."""
    rng = random.Random(12345)
    # (a) regular
    docs_r = _synth_corpus_regular(40, rng)
    S_r = corpus_S(docs_r)
    nulls_r = [null_corpus_S(docs_r, rng) for _ in range(200)]
    nm_r = statistics.median(nulls_r)
    # (b) random
    docs_x = _synth_corpus_random(40, rng)
    S_x = corpus_S(docs_x)
    nulls_x = [null_corpus_S(docs_x, rng) for _ in range(200)]
    nm_x = statistics.median(nulls_x)
    ok_a = S_r < nm_r  # regular observed below null
    ok_b = abs(S_x - nm_x) / max(nm_x, 1e-9) < 0.20  # random ~ null (within 20%)
    print("SELF-CHECK")
    print(f"  (a) REGULAR synth: S_obs={S_r:.4f}  null_median={nm_r:.4f}  ratio={S_r/nm_r:.3f}  "
          f"{'OK (obs<<null)' if ok_a else 'FAIL'}")
    print(f"  (b) RANDOM  synth: S_obs={S_x:.4f}  null_median={nm_x:.4f}  ratio={S_x/nm_x:.3f}  "
          f"{'OK (~null)' if ok_b else 'FAIL'}")
    return ok_a and ok_b


if __name__ == "__main__":
    print("=== EPOCH-079 machinery self-check ===")
    ok = self_check()
    print(f"  self_check_overall: {'PASS' if ok else 'FAIL'}")
    print()
    print("=== Positive control (synthetic) ===")
    pc = positive_control()
    print(f"  detect_p_med={pc['detect_p_med']:.4f}  power_est={pc['power_est']:.3f}  "
          f"fp_rate={pc['fp_rate']:.3f}  passed={pc['passed']}")
