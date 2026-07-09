"""
EPOCH-081 machinery: row left-anchoring (left-justified layout) test.
L2 only — opaque glyph IDs; only bbox positions matter.

Frozen metric:
  per doc: lsd = pstdev(row LEFT-edges)/medw ; rsd = pstdev(row RIGHT-edges)/medw ; a = rsd - lsd
  S_obs = median(a) over usable docs
  NULL (edge-exchangeability, sign-symmetric): per doc sample s in {+1,-1}; contribute s*(rsd-lsd); S=median.
  one-sided perm p = frac(null S >= S_obs)
"""
import json, statistics as st, random, math
from collections import defaultdict

DATA_PATH = "experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"

# ---------- row clustering ----------
def cluster_rows(glyphs, ytol_factor=0.6):
    """Single-linkage cluster non-divider glyphs by y-center within tol = ytol_factor*median(height)."""
    gs = [g for g in glyphs if not g.get("is_divider") and g.get("bbox") is not None]
    if len(gs) < 6:
        return None, None
    heights = [g["bbox"][3] for g in gs]
    medh = st.median(heights)
    tol = ytol_factor * medh
    def yc(g):
        return g["bbox"][1] + g["bbox"][3] / 2.0
    gs_sorted = sorted(gs, key=yc)
    rows = []
    cur = [gs_sorted[0]]
    cur_y = yc(gs_sorted[0])
    for g in gs_sorted[1:]:
        y = yc(g)
        if abs(y - cur_y) <= tol:
            cur.append(g)
            cur_y = sum(yc(x) for x in cur) / len(cur)
        else:
            rows.append(cur)
            cur = [g]
            cur_y = y
    if cur:
        rows.append(cur)
    return rows, medh

def doc_metrics(doc):
    rows, medh = cluster_rows(doc["glyphs"])
    if rows is None or len(rows) < 3:
        return None
    widths = [g["bbox"][2] for r in rows for g in r]
    medw = st.median(widths)
    if medw <= 0:
        return None
    lefts = [min(g["bbox"][0] for g in r) for r in rows]
    rights = [max(g["bbox"][0] + g["bbox"][2] for g in r) for r in rows]
    lsd = st.pstdev(lefts) / medw
    rsd = st.pstdev(rights) / medw
    return dict(lsd=lsd, rsd=rsd, a=rsd - lsd, n_rows=len(rows), medw=medw, medh=medh)

def usable_docs(docs):
    out = []
    for doc in docs:
        m = doc_metrics(doc)
        if m is not None:
            out.append((doc, m))
    return out

# ---------- null ----------
def swap_null_p(asymmetries, S_obs, n_draws=5000, seed=20250801):
    """Edge-exchangeability sign-symmetric null. asymmetries = list of (rsd-lsd) per doc.
    Per draw: per doc sample s in {+1,-1}; contribute s*a; S = median(contributions).
    one-sided p = frac(null S >= S_obs)."""
    rng = random.Random(seed)
    n = len(asymmetries)
    ge = 0
    vals = []
    for _ in range(n_draws):
        contrib = []
        for a in asymmetries:
            s = 1 if rng.random() < 0.5 else -1
            contrib.append(s * a)
        S = st.median(contrib)
        vals.append(S)
        if S >= S_obs:
            ge += 1
    p = (ge + 1) / (n_draws + 1)  # add-one for finite-sample safety
    return p, st.median(vals)

def analyze(docs, n_draws=5000, seed=20250801):
    """Return dict of analysis for a doc-set."""
    ud = usable_docs(docs)
    if not ud:
        return None
    ms = [m for _, m in ud]
    asym = [m["a"] for m in ms]
    S_obs = st.median(asym)
    p, null_med = swap_null_p(asym, S_obs, n_draws=n_draws, seed=seed)
    return dict(
        n_docs=len(ud),
        S_obs=S_obs,
        null_median=null_med,
        perm_p=p,
        median_lsd=st.median(m["lsd"] for m in ms),
        median_rsd=st.median(m["rsd"] for m in ms),
        frac_left_tighter=sum(1 for m in ms if m["lsd"] < m["rsd"]) / len(ms),
        sig_left_anchored=(p <= 0.05 and S_obs > 0),
    )

# ---------- synthetic PC ----------
def make_synthetic(arm, n_docs=40, seed=0):
    """Build synthetic docs mimicking real geometry.
    arm: 'left' (left-justified), 'center' (centered, edges EXCHANGEABLE by construction),
         'right' (right-justified).
    Each doc: 6-12 rows; per row 3-8 glyphs; glyph w,h ~ real medians; rows y-spaced ~ real median height.

    CENTER arm is constructed so left/right edges are mirror-symmetric around each row's center
    (draw one half-width deviation d; left=center-d, right=center+d) => edges genuinely exchangeable,
    giving S_obs ~ 0 in expectation (a fair false-positive target).
    LEFT/RIGHT arms have a TIGHT margin on one edge and a RAGGED (variable) edge on the other.
    """
    rng = random.Random(seed)
    MEDW, MEDH = 120.0, 160.0  # ~ real medians
    ROW_GAP = MEDH * 1.2
    PAGE_CX = 450.0
    docs = []
    for di in range(n_docs):
        n_rows = rng.randint(6, 12)
        rows = []
        for ri in range(n_rows):
            n_g = rng.randint(3, 8)
            y_top = 50 + ri * ROW_GAP + rng.uniform(-5, 5)
            if arm == "left":
                # tight left margin, ragged right (variable row half-width)
                left_x = 60.0 + rng.uniform(-3, 3)
                half = n_g * MEDW / 2.0 * rng.uniform(0.85, 1.15)
                right_x = left_x + 2 * half
                cx = (left_x + right_x) / 2.0
            elif arm == "right":
                right_x = (PAGE_CX * 2 - 60.0) + rng.uniform(-3, 3)
                half = n_g * MEDW / 2.0 * rng.uniform(0.85, 1.15)
                left_x = right_x - 2 * half
                cx = (left_x + right_x) / 2.0
            else:  # center: EXCHANGEABLE edges
                # draw a single half-width deviation d; left=cx-d, right=cx+d (mirror-symmetric)
                cx = PAGE_CX + rng.uniform(-30, 30)
                d = n_g * MEDW / 2.0 * rng.uniform(0.85, 1.15)
                left_x = cx - d
                right_x = cx + d
            # place glyphs evenly between left_x and right_x
            glyphs = []
            span = right_x - left_x
            step = span / n_g
            for gi in range(n_g):
                w = MEDW * rng.uniform(0.8, 1.2)
                h = MEDH * rng.uniform(0.8, 1.2)
                gx = left_x + gi * step + rng.uniform(-2, 2)
                glyphs.append({"sign": "SYN", "bbox": [round(gx, 1), round(y_top, 1), round(w, 1), round(h, 1)],
                               "is_divider": False})
            rows.append(glyphs)
        allg = [g for r in rows for g in r]
        docs.append({"designation": f"SYN-{arm}-{di}", "site": "SYN", "support": "Tablet",
                     "period": "LM I", "glyphs": allg})
    return docs

def pc_run(n_reps=20, n_docs_per_rep=40, n_draws=2000, seed_base=100):
    """Three-arm PC. Returns dict."""
    # (a) DETECT: left-justified -> flagged, power_est
    detect_flags = 0
    detect_ps = []
    for r in range(n_reps):
        docs = make_synthetic("left", n_docs=n_docs_per_rep, seed=seed_base + r)
        res = analyze(docs, n_draws=n_draws, seed=seed_base + r)
        detect_ps.append(res["perm_p"])
        if res["perm_p"] <= 0.05 and res["S_obs"] > 0:
            detect_flags += 1
    power_est = detect_flags / n_reps
    detect_p = st.median(detect_ps)

    # (b) FALSE-POSITIVE: centered -> NOT flagged (reject <=0.10)
    center_flags = 0
    for r in range(n_reps):
        docs = make_synthetic("center", n_docs=n_docs_per_rep, seed=seed_base + 100 + r)
        res = analyze(docs, n_draws=n_draws, seed=seed_base + 100 + r)
        if res["perm_p"] <= 0.10:
            center_flags += 1
    centered_false_pos_rate = center_flags / n_reps

    # (c) DIRECTION: right-justified -> S_obs<0 and NOT flagged as left-anchored
    right_flagged_left = False
    right_S_neg = True
    for r in range(n_reps):
        docs = make_synthetic("right", n_docs=n_docs_per_rep, seed=seed_base + 200 + r)
        res = analyze(docs, n_draws=n_draws, seed=seed_base + 200 + r)
        if res["perm_p"] <= 0.05 and res["S_obs"] > 0:
            right_flagged_left = True
        if res["S_obs"] >= 0:
            right_S_neg = False

    detect_ok = (power_est >= 0.5)
    center_ok = (centered_false_pos_rate <= 0.10)  # reject <=0.10 means FP rate must be low
    direction_ok = (not right_flagged_left) and right_S_neg
    passed = detect_ok and center_ok and direction_ok
    return dict(
        pc_verdict="PASSED" if passed else "FAILED",
        detect_p=detect_p,
        power_est=power_est,
        centered_false_pos_rate=centered_false_pos_rate,
        right_just_flagged_left=right_flagged_left,
        right_S_neg=right_S_neg,
        detect_ok=detect_ok,
        center_ok=center_ok,
        direction_ok=direction_ok,
        pc_is_synthetic=True,
    )

# ---------- main ----------
def main_real():
    docs = json.load(open(DATA_PATH))
    glob = analyze(docs, n_draws=5000, seed=20250801)
    print("GLOBAL:", json.dumps(glob, indent=2))
    # per site
    by_site = defaultdict(list)
    for doc in docs:
        by_site[doc.get("site", "?")].append(doc)
    sites_res = []
    for s in ["Haghia Triada", "Khania", "Zakros"]:
        if len(by_site[s]) >= 15:
            r = analyze(by_site[s], n_draws=5000, seed=20250801 + hash(s) % 1000)
            r["site"] = s
            sites_res.append(r)
            print(f"SITE {s}:", json.dumps(r, indent=2))
    return glob, sites_res

if __name__ == "__main__":
    import sys
    print("=== EPOCH-081 machinery self-check ===")
    # SELF-CHECK: three synthetic arms
    print("\n[1] LEFT-justified synthetic (should flag S_obs>0, p<=0.05):")
    d = make_synthetic("left", n_docs=40, seed=7)
    r = analyze(d, n_draws=2000, seed=7)
    print(f"    S_obs={r['S_obs']:.3f} perm_p={r['perm_p']:.4f} median_lsd={r['median_lsd']:.3f} median_rsd={r['median_rsd']:.3f}")
    assert r["S_obs"] > 0 and r["perm_p"] <= 0.05, "LEFT-justified should be flagged"
    print("    OK: left-justified flagged.")

    print("\n[2] CENTERED synthetic (should NOT flag, S_obs~0):")
    d = make_synthetic("center", n_docs=40, seed=11)
    r = analyze(d, n_draws=2000, seed=11)
    print(f"    S_obs={r['S_obs']:.3f} perm_p={r['perm_p']:.4f}")
    assert abs(r["S_obs"]) < 0.3, "CENTERED should have S_obs~0"
    print("    OK: centered not strongly left-anchored.")

    print("\n[3] RIGHT-justified synthetic (should have S_obs<0, NOT flagged left):")
    d = make_synthetic("right", n_docs=40, seed=13)
    r = analyze(d, n_draws=2000, seed=13)
    print(f"    S_obs={r['S_obs']:.3f} perm_p={r['perm_p']:.4f}")
    assert r["S_obs"] < 0, "RIGHT-justified should have S_obs<0"
    assert not (r["perm_p"] <= 0.05 and r["S_obs"] > 0), "RIGHT-justified must not be flagged left-anchored"
    print("    OK: right-justified has S_obs<0, not flagged left.")

    print("\n[4] Full PC (3 arms, 20 reps):")
    pc = pc_run(n_reps=20, n_docs_per_rep=40, n_draws=2000)
    print("   ", json.dumps(pc, indent=2))
    print("\nSELF-CHECK PASSED" if pc["pc_verdict"] == "PASSED" else "\nSELF-CHECK: PC FAILED")
