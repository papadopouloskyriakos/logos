import json, statistics, random

def load_docs(path):
    docs = json.load(open(path))
    out = []
    for d in docs:
        gl = [g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"]) == 4 and not g.get("is_divider")]
        if len(gl) >= 6:
            out.append((d.get("site"), gl))
    return out

def rows_threshold(gl, thr):
    pts = [(g["bbox"][0]+g["bbox"][2]/2.0, g["bbox"][1]+g["bbox"][3]/2.0, g["bbox"][3]) for g in gl]
    medh = statistics.median([p[2] for p in pts]) or 1.0
    ys = sorted(pts, key=lambda p: p[1]); rows=[]; cur=[ys[0]]
    for p in ys[1:]:
        if abs(p[1]-cur[-1][1]) <= thr*medh: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur)
    return rows, thr*medh          # (rows, merge_tolerance)

def rows_altgap(gl):
    pts = [(g["bbox"][0]+g["bbox"][2]/2.0, g["bbox"][1]+g["bbox"][3]/2.0, g["bbox"][3]) for g in gl]
    ys = sorted(pts, key=lambda p: p[1])
    if len(ys) < 2:
        return [ys], 1.0
    gaps = [ys[i+1][1]-ys[i][1] for i in range(len(ys)-1)]
    medg = statistics.median(gaps) or 1.0
    tol = 1.5*medg
    rows=[]; cur=[ys[0]]
    for i,p in enumerate(ys[1:]):
        if gaps[i] <= tol: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur)
    return rows, tol

def cv(v):
    if len(v) < 2: return None
    m = statistics.mean(v)
    return statistics.pstdev(v)/m if m else None

def h_pitch_cv(rows):                         # E079 metric for one doc
    ps=[]
    for r in rows:
        if len(r) < 3: continue
        xs = sorted(p[0] for p in r)
        ps += [b-a for a,b in zip(xs, xs[1:])]
    return cv(ps) if len(ps) >= 3 else None

def v_line_cv(rows):                           # E080 metric for one doc
    rc = sorted(statistics.median([q[1] for q in r]) for r in rows)
    if len(rc) < 3: return None
    return cv([b-a for a,b in zip(rc, rc[1:])])

def S_h(docs_rows):                            # corpus statistic (list of per-doc rows)
    xs=[h_pitch_cv(r) for r in docs_rows]; xs=[x for x in xs if x is not None]
    return statistics.median(xs), len(xs)

def S_v(docs_rows):
    xs=[v_line_cv(r) for r in docs_rows]; xs=[x for x in xs if x is not None]
    return statistics.median(xs), len(xs)

def rand_comp(n, total, rng):                  # uniform-breakpoint composition
    if n <= 1: return [float(total)]
    bps = sorted(rng.uniform(0, total) for _ in range(n-1))
    prev=0.0; v=[]
    for b in bps: v.append(b-prev); prev=b
    v.append(total-prev); return v

def rand_comp_above(n, total, rng, floor, tries=200):   # E080 clustering-conditional
    if n <= 1: return [float(total)]
    for _ in range(tries):
        c = rand_comp(n, total, rng)
        if all(x > floor for x in c): return c
    return rand_comp(n, total, rng)

def null_h_doc(rows, rng):                      # E079 null: random-composition of each row's pitches
    ps=[]
    for r in rows:
        if len(r) < 3: continue
        xs = sorted(p[0] for p in r)
        obs = [b-a for a,b in zip(xs, xs[1:])]
        ps += rand_comp(len(obs), sum(obs), rng)
    return cv(ps) if len(ps) >= 3 else None

def null_v_doc(rows, tol, rng):                 # E080 null: clustering-conditional random row-allocation
    rc = sorted(statistics.median([q[1] for q in r]) for r in rows)
    if len(rc) < 3: return None
    total = rc[-1]-rc[0]; k=len(rc)-1
    return cv(rand_comp_above(k, total, rng, tol))

def perm_p(docs_rows_tol, kind, S_obs, rng, ndraw=500):
    # docs_rows_tol: list of (rows, tol) per doc.  kind: 'h' or 'v'.
    nulls=[]
    for _ in range(ndraw):
        vals=[]
        for rows,tol in docs_rows_tol:
            x = null_h_doc(rows, rng) if kind=='h' else null_v_doc(rows, tol, rng)
            if x is not None: vals.append(x)
        nulls.append(statistics.median(vals))
    ge = sum(1 for s in nulls if s <= S_obs)
    return statistics.median(nulls), (ge+1)/(ndraw+1)

# ===================== ASSEMBLY =====================

SITES = ["Haghia Triada", "Khania", "Zakros"]

def build_settings(docs):
    """Return dict: setting_name -> list of (rows, tol) per doc."""
    settings = {}
    for thr, name in [(0.5, "tol=0.5"), (0.6, "tol=0.6"), (0.7, "tol=0.7")]:
        settings[name] = [rows_threshold(gl, thr) for (_s, gl) in docs]
    settings["alt_gap"] = [rows_altgap(gl) for (_s, gl) in docs]
    return settings

def eval_setting(docs_rows_tol, rng):
    docs_rows = [r for (r, _t) in docs_rows_tol]
    sh, nh = S_h(docs_rows)
    null_h, pp_h = perm_p(docs_rows_tol, 'h', sh, rng)
    sv, nv = S_v(docs_rows)
    null_v, pp_v = perm_p(docs_rows_tol, 'v', sv, rng)
    return {"S_h": sh, "null_h": null_h, "perm_p_h": pp_h,
            "S_v": sv, "null_v": null_v, "perm_p_v": pp_v,
            "n_h": nh, "n_v": nv}

# ===================== POSITIVE CONTROL =====================

def make_regular_doc(rng, n_rows=6, glyphs_per_row=8, row_pitch=10.0, col_pitch=6.0, jitter=0.05):
    """Regular grid: evenly spaced rows, evenly spaced glyphs per row, small jitter."""
    glyphs = []
    y0 = rng.uniform(0, 5)
    for ri in range(n_rows):
        y = y0 + ri*row_pitch + rng.uniform(-jitter, jitter)*row_pitch
        x0 = rng.uniform(0, 5)
        for gi in range(glyphs_per_row):
            x = x0 + gi*col_pitch + rng.uniform(-jitter, jitter)*col_pitch
            h = 4.0
            glyphs.append({"bbox": [x - h/2.0, y - h/2.0, h, h], "is_divider": False})
    return glyphs

def make_random_doc(rng, n_rows=6, glyphs_per_row=8, col_span=120.0, row_span=80.0):
    """Random placement: rows at random y via rand_comp of row_span; glyphs at random x via rand_comp of col_span
    (kept left-to-right)."""
    glyphs = []
    row_ys = [0.0]
    acc = 0.0
    for gap in rand_comp(n_rows, row_span, rng):
        acc += gap
        row_ys.append(acc)
    for ri in range(n_rows):
        y = row_ys[ri]
        xs = rand_comp(glyphs_per_row, col_span, rng)
        accx = 0.0
        for gap in xs:
            accx += gap
            h = 4.0
            glyphs.append({"bbox": [accx - h/2.0, y - h/2.0, h, h], "is_divider": False})
    return glyphs

def docs_from_glyphlists(lists):
    return [("<synthetic>", gl) for gl in lists]

def pc_one_arm(rng, make_fn, n_docs=40):
    """Build n_docs synthetic docs, evaluate under tol=0.6 and alt. Return dict of perm_p values."""
    gls = [make_fn(rng) for _ in range(n_docs)]
    docs = docs_from_glyphlists(gls)
    out = {}
    for thr, name in [(0.6, "tol=0.6")]:
        s = [rows_threshold(gl, thr) for (_s, gl) in docs]
        sh, _ = S_h([r for (r, _t) in s])
        _, pp_h = perm_p(s, 'h', sh, rng)
        sv, _ = S_v([r for (r, _t) in s])
        _, pp_v = perm_p(s, 'v', sv, rng)
        out[name] = {"perm_p_h": pp_h, "perm_p_v": pp_v}
    s_alt = [rows_altgap(gl) for (_s, gl) in docs]
    sh, _ = S_h([r for (r, _t) in s_alt])
    _, pp_h = perm_p(s_alt, 'h', sh, rng)
    sv, _ = S_v([r for (r, _t) in s_alt])
    _, pp_v = perm_p(s_alt, 'v', sv, rng)
    out["alt_gap"] = {"perm_p_h": pp_h, "perm_p_v": pp_v}
    return out

def run_positive_control(seed0=12345, n_reps=15, n_docs=40):
    """power_est = fraction of reps where DETECT arm flags BOTH metrics regular under BOTH 0.6 and alt.
    false_pos_rate = fraction of reps where FP arm flags EITHER metric regular under 0.6 or alt."""
    detect_flag = 0
    detect_total = 0
    fp_flag_any = 0
    fp_total = 0
    for rep in range(n_reps):
        rng = random.Random(seed0 + rep)
        # DETECT
        d = pc_one_arm(rng, make_regular_doc, n_docs=n_docs)
        detect_total += 1
        # both metrics regular (perm_p<=0.05) under both 0.6 and alt
        ok = (d["tol=0.6"]["perm_p_h"] <= 0.05 and d["tol=0.6"]["perm_p_v"] <= 0.05 and
              d["alt_gap"]["perm_p_h"] <= 0.05 and d["alt_gap"]["perm_p_v"] <= 0.05)
        if ok:
            detect_flag += 1
        # FALSE POSITIVE
        rng2 = random.Random(seed0 + 1000 + rep)
        f = pc_one_arm(rng2, make_random_doc, n_docs=n_docs)
        fp_total += 1
        fp_ok = (f["tol=0.6"]["perm_p_h"] <= 0.05 or f["tol=0.6"]["perm_p_v"] <= 0.05 or
                 f["alt_gap"]["perm_p_h"] <= 0.05 or f["alt_gap"]["perm_p_v"] <= 0.05)
        if fp_ok:
            fp_flag_any += 1
    power_est = detect_flag / detect_total
    false_pos_rate = fp_flag_any / fp_total
    # PC passed iff power_est >= 0.8 (detect reliably flags) AND false_pos_rate <= 0.10
    pc_passed = (power_est >= 0.80 and false_pos_rate <= 0.10)
    return {"pc_verdict": "PASSED" if pc_passed else "FAILED",
            "power_est": power_est, "false_pos_rate": false_pos_rate,
            "pc_is_synthetic": True}

# ===================== MAIN =====================

def main():
    rng = random.Random(20240709)
    docs = load_docs("experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json")
    settings = build_settings(docs)

    # Global sweep
    sweep = []
    for name in ["tol=0.5", "tol=0.6", "tol=0.7", "alt_gap"]:
        r = eval_setting(settings[name], rng)
        r["setting"] = name
        sweep.append(r)

    canonical = {k: sweep[1][k] for k in ["S_h", "null_h", "perm_p_h", "S_v", "null_v", "perm_p_v"]}

    # Per-site at canonical tol=0.6
    per_site = []
    for site in SITES:
        sdocs = [(s, gl) for (s, gl) in docs if s == site]
        sset = build_settings(sdocs)["tol=0.6"]
        r = eval_setting(sset, rng)
        per_site.append({"site": site, "perm_p_h": r["perm_p_h"], "perm_p_v": r["perm_p_v"],
                         "S_h": r["S_h"], "S_v": r["S_v"], "n_docs": len(sdocs)})

    # Robustness flags
    h_sig_all4 = all(s["perm_p_h"] <= 0.05 and s["S_h"] < s["null_h"] for s in sweep)
    v_sig_all4 = all(s["perm_p_v"] <= 0.05 and s["S_v"] < s["null_v"] for s in sweep)

    # Positive control
    pc = run_positive_control()

    # Site legs at canonical
    h_sites_sig = sum(1 for s in per_site if s["perm_p_h"] <= 0.05)
    v_sites_sig = sum(1 for s in per_site if s["perm_p_v"] <= 0.05)

    # FROZEN VERDICT
    if pc["pc_verdict"] == "FAILED":
        verdict = "MACHINERY_UNINFORMATIVE"
    else:
        # threshold sensitive if either metric loses global sig / flips direction at any setting
        thresh_sensitive = not (h_sig_all4 and v_sig_all4)
        if thresh_sensitive:
            verdict = "GRID_REGULARITY_THRESHOLD_SENSITIVE"
        else:
            # robust requires both metrics sig all 4 AND each retains >=2/3 sites sig at 0.6
            site_ok = (h_sites_sig >= 2 and v_sites_sig >= 2)
            if site_ok:
                verdict = "GRID_REGULARITY_ROBUST_TO_ROW_DETECTION"
            else:
                verdict = "GRID_REGULARITY_PARTIALLY_SENSITIVE"

    out = {
        "task_id": "EPOCH-082",
        "verdict": verdict,
        "canonical": canonical,
        "sweep": sweep,
        "per_site_canonical": per_site,
        "robustness": {"h_sig_all4": h_sig_all4, "v_sig_all4": v_sig_all4, "n_settings": 4,
                       "h_sites_sig_at_0.6": h_sites_sig, "v_sites_sig_at_0.6": v_sites_sig},
        "positive_control": pc,
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
