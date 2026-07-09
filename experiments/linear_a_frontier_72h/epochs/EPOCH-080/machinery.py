"""
EPOCH-080 machinery — Vertical Row-to-Row Spacing (line pitch) Regularity (ruled horizontal lines / page grid), cross-site.
L2 only: signs are OPAQUE catalog IDs; only glyph POSITIONS (row y-positions) matter.
A ROW = y-band (cluster glyphs by y-center within 0.6 x median glyph-height). Each row's y-position = MEDIAN y-center
of its glyphs. Sort rows top-to-bottom; VERTICAL PITCH = consecutive row-position difference. Doc line-pitch-CV =
sd/mean of the doc's vertical pitches. S_obs = MEDIAN doc line-pitch-CV over usable docs (>=6 non-divider glyphs AND
>=3 rows). NULL = random row-allocation: replace the doc's vertical pitches with a uniform-Dirichlet / random-breakpoint
composition summing to the SAME total row-span (preserves row count + column height, destroys only the regularity of
line spacing), CONDITIONED on every pitch exceeding the row-clustering tolerance (so the null rows would be recovered
as distinct rows by the same clustering — keeps the null exchangeable with the observed, since the observed pitches all
exceed tol by construction); recompute S = median doc line-pitch-CV; >=1000 draws; one-sided perm p = frac(null S <= S_obs)
(regular = observed MORE uniform / LOWER CV than random). DISTINCT from E079 (horizontal within-row glyph pitch).

Frozen against prereg.md (see plan_hash.txt).
"""
import json, math, statistics, random, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, "..", ".."))  # experiments/linear_a_frontier_72h
DATA_GLYPHS = os.path.join(CAMP, "data", "sigla_glyphs_bbox.json")

MIN_DOC_GLYPHS = 6      # >=6 non-divider glyphs per doc
MIN_ROWS = 3            # docs need >=3 rows (>=2 vertical pitches)
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


def _row_ypos(row):
    """Row y-position = median y-center of the row's glyphs."""
    yc = [g["bbox"][1] + g["bbox"][3] / 2.0 for g in row]
    return statistics.median(yc)


def doc_vertical_pitches(glyphs):
    """Return list of consecutive row-to-row vertical pitches (rows sorted top-to-bottom)."""
    rows, _ = _rows_of(glyphs)
    if len(rows) < 2:
        return []
    ys = sorted(_row_ypos(r) for r in rows)
    return [ys[k + 1] - ys[k] for k in range(len(ys) - 1)]


def _cv(vals):
    if len(vals) < 2:
        return None
    m = statistics.mean(vals)
    if m == 0:
        return None
    return statistics.pstdev(vals) / m


def doc_line_pitch_cv(glyphs):
    """Doc line-pitch-CV = sd/mean of the doc's vertical (between-row) pitches."""
    return _cv(doc_vertical_pitches(glyphs))


def _row_tol(glyphs):
    """Row-clustering tolerance = 0.6 x median glyph-height of the doc's non-divider glyphs."""
    gs = [g for g in glyphs if not g.get("is_divider")]
    if not gs:
        return 0.0
    return ROW_TOL_FACTOR * statistics.median(g["bbox"][3] for g in gs)


# ---------- random row-allocation null (clustering-conditional) ----------

def _rand_composition(n_parts, total, rng):
    """Random composition of n_parts positive values summing to `total`
    via uniform Dirichlet = random breakpoints on the span."""
    if n_parts <= 0:
        return []
    if n_parts == 1:
        return [float(total)]
    bps = sorted(rng.uniform(0, total) for _ in range(n_parts - 1))
    vals = []
    prev = 0.0
    for b in bps:
        vals.append(b - prev)
        prev = b
    vals.append(total - prev)
    return vals


def _rand_composition_above(n_parts, total, rng, floor, max_tries=300):
    """Random composition of n_parts positive values summing to `total`, conditioned on every
    part > floor (so the rows would be recovered as distinct by the same clustering). Uniform over
    the truncated simplex via rejection. Falls back to the unconditional composition if rejection
    fails (e.g. floor too large relative to total)."""
    if n_parts <= 0:
        return []
    if n_parts == 1:
        return [float(total)]
    for _ in range(max_tries):
        comp = _rand_composition(n_parts, total, rng)
        if all(v > floor for v in comp):
            return comp
    return _rand_composition(n_parts, total, rng)


def null_doc_line_pitch_cv(glyphs, rng):
    """Replace the doc's vertical pitches with a random composition of the SAME total row-span
    (same number of rows, same top-to-bottom extent), per prereg.md §5: uniform Dirichlet /
    random breakpoints on the column height, CONDITIONED on every pitch exceeding the
    row-clustering tolerance (0.6 x median glyph-height) so the null rows would be recovered
    as distinct by the SAME clustering that recovered the observed rows. This keeps the null
    exchangeable with the observed (whose pitches all exceed tol by construction); without the
    floor the unconditional null is NOT exchangeable and the positive-control false-positive
    rate is ~0.72 (random-rows synth flagged as regular). Recompute doc line-pitch-CV."""
    pitches = doc_vertical_pitches(glyphs)
    if len(pitches) < 2:
        return None
    total = sum(pitches)          # total row-span (top row -> bottom row)
    n = len(pitches)              # n_rows - 1
    floor = _row_tol(glyphs)      # row-clustering tolerance (exchangeability condition)
    rand_pitches = _rand_composition_above(n, total, rng, floor)
    return _cv(rand_pitches)


# ---------- corpus statistic ----------

def corpus_S(docs_glyphs):
    """S = median doc line-pitch-CV over docs (glyphs lists)."""
    cvs = [doc_line_pitch_cv(g) for g in docs_glyphs]
    cvs = [c for c in cvs if c is not None]
    if not cvs:
        return None
    return statistics.median(cvs)


def null_corpus_S(docs_glyphs, rng):
    """One null draw of S: per-doc random row-allocation null (prereg.md §5), then median."""
    cvs = [null_doc_line_pitch_cv(g, rng) for g in docs_glyphs]
    cvs = [c for c in cvs if c is not None]
    if not cvs:
        return None
    return statistics.median(cvs)


def perm_test(docs_glyphs, n_perm=N_PERM, seed=80):
    """One-sided perm p = frac(null S <= S_obs). Returns (S_obs, null_median, nulls, perm_p)."""
    rng = random.Random(seed)
    S_obs = corpus_S(docs_glyphs)
    nulls = []
    for _ in range(n_perm):
        nulls.append(null_corpus_S(docs_glyphs, rng))
    nulls = [s for s in nulls if s is not None]
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
        if len(rows) >= MIN_ROWS:
            usable.append(d)
    return usable


# ---------- synthetic PC builders ----------

def _synth_doc_regular_rows(n_rows, glyphs_per_row, pitch, jitter_frac, rng, h=100, w=80):
    """Build a doc with EVENLY-SPACED rows (low vertical pitch CV): rows at near-equal vertical pitch.
    Each row has glyphs_per_row glyphs (so the doc has >=6 glyphs and >=3 rows)."""
    glyphs = []
    y = 0.0
    for r in range(n_rows):
        x = rng.uniform(20, 60)
        xs = [x + k * (w + 10) for k in range(glyphs_per_row)]
        for xx in xs:
            glyphs.append({"sign": "X", "bbox": [xx, y - h / 2.0, w, h], "is_divider": False})
        if r < n_rows - 1:
            j = pitch * jitter_frac
            y += pitch + rng.uniform(-j, j)
    return glyphs


def _synth_doc_random_rows(n_rows, glyphs_per_row, span, rng, h=100, w=80):
    """Build a doc with RANDOM-composition row spacings (vertical pitch CV ~ null): the row-to-row
    pitches are a random composition of `span` (the total column height)."""
    n_p = n_rows - 1
    pitches = _rand_composition(n_p, span, rng)
    glyphs = []
    y = 0.0
    for r in range(n_rows):
        x = rng.uniform(20, 60)
        xs = [x + k * (w + 10) for k in range(glyphs_per_row)]
        for xx in xs:
            glyphs.append({"sign": "X", "bbox": [xx, y - h / 2.0, w, h], "is_divider": False})
        if r < n_rows - 1:
            y += pitches[r]
    return glyphs


def _synth_corpus_regular_rows(n_docs, rng):
    docs = []
    for _ in range(n_docs):
        nr = rng.randint(3, 6)          # >=3 rows
        gp = rng.randint(2, 5)          # enough glyphs (>=6 total)
        pitch = rng.uniform(180, 320)
        jf = rng.uniform(0.02, 0.08)    # small jitter => low vertical pitch CV
        docs.append(_synth_doc_regular_rows(nr, gp, pitch, jf, rng))
    return docs


def _synth_corpus_random_rows(n_docs, rng):
    docs = []
    for _ in range(n_docs):
        nr = rng.randint(3, 6)
        gp = rng.randint(2, 5)
        span = rng.uniform(700, 1500)
        docs.append(_synth_doc_random_rows(nr, gp, span, rng))
    return docs


def positive_control(n_docs=40, reps=PC_REPS, seed=8000):
    """(a) DETECT: regular-rows synth should be flagged (perm p<=0.05). power_est = frac flagged.
       (b) FALSE-POSITIVE: random-rows synth should NOT be flagged. fp_rate = frac flagged."""
    rng = random.Random(seed)
    detect_ps = []
    for _ in range(reps):
        docs = _synth_corpus_regular_rows(n_docs, rng)
        S_obs, null_med, nulls, p = perm_test(docs, n_perm=200, seed=rng.randint(0, 10**9))
        detect_ps.append(p)
    power_est = sum(1 for p in detect_ps if p <= PC_ALPHA) / len(detect_ps)
    detect_p_med = statistics.median(detect_ps)

    fp_ps = []
    for _ in range(reps):
        docs = _synth_corpus_random_rows(n_docs, rng)
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
    """Confirm: (a) on REGULAR-rows synthetic, observed CV << null CV (null higher);
    (b) on RANDOM-rows synthetic, observed CV ~ null CV (null calibrated)."""
    rng = random.Random(12345)
    # (a) regular rows
    docs_r = _synth_corpus_regular_rows(40, rng)
    S_r = corpus_S(docs_r)
    nulls_r = [null_corpus_S(docs_r, rng) for _ in range(200)]
    nulls_r = [s for s in nulls_r if s is not None]
    nm_r = statistics.median(nulls_r)
    # (b) random rows
    docs_x = _synth_corpus_random_rows(40, rng)
    S_x = corpus_S(docs_x)
    nulls_x = [null_corpus_S(docs_x, rng) for _ in range(200)]
    nulls_x = [s for s in nulls_x if s is not None]
    nm_x = statistics.median(nulls_x)
    ok_a = S_r < nm_r  # regular observed below null
    ok_b = abs(S_x - nm_x) / max(nm_x, 1e-9) < 0.25  # random ~ null (within 25%)
    print("SELF-CHECK")
    print(f"  (a) REGULAR-rows synth: S_obs={S_r:.4f}  null_median={nm_r:.4f}  ratio={S_r/nm_r:.3f}  "
          f"{'OK (obs<<null)' if ok_a else 'FAIL'}")
    print(f"  (b) RANDOM-rows  synth: S_obs={S_x:.4f}  null_median={nm_x:.4f}  ratio={S_x/nm_x:.3f}  "
          f"{'OK (~null)' if ok_b else 'FAIL'}")
    return ok_a and ok_b


if __name__ == "__main__":
    print("=== EPOCH-080 machinery self-check ===")
    ok = self_check()
    print(f"  self_check_overall: {'PASS' if ok else 'FAIL'}")
    print()
    print("=== Positive control (synthetic) ===")
    pc = positive_control()
    print(f"  detect_p_med={pc['detect_p_med']:.4f}  power_est={pc['power_est']:.3f}  "
          f"fp_rate={pc['fp_rate']:.3f}  passed={pc['passed']}")
