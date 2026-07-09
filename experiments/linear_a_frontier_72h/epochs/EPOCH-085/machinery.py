import json, statistics, random, math, hashlib, os

# ============ GIVEN TESTED FUNCTIONS (VERBATIM) ============
def load_usable(path):
    docs=json.load(open(path)); out=[]
    for d in docs:
        gl=[g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"])==4 and not g.get("is_divider")]
        if len(gl)>=6:
            ra=doc_rows_areas(gl)
            if len(ra)>=2: out.append((d.get("site"), ra))
    return out

def doc_rows_areas(gl):    # top->bottom list of rows, each = list of glyph AREAS (w*h). y-band tol 0.6*median height.
    pts=[{"h":g["bbox"][3], "yc":g["bbox"][1]+g["bbox"][3]/2.0, "area":g["bbox"][2]*g["bbox"][3]} for g in gl]
    medh=statistics.median([p["h"] for p in pts]) or 1.0
    ys=sorted(pts,key=lambda p:p["yc"]); rows=[]; cur=[ys[0]]
    for p in ys[1:]:
        if abs(p["yc"]-cur[-1]["yc"])<=0.6*medh: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur)
    return [[q["area"] for q in r] for r in rows]   # already top->bottom (sorted by y-center)

def R_first_vs_rest(rowsA):
    if len(rowsA)<2: return None
    first=rowsA[0]; rest=[a for r in rowsA[1:] for a in r]
    if len(first)<2 or len(rest)<3: return None
    return math.log(statistics.median(first)/statistics.median(rest))

def R_randrow(rowsA, rng):   # null: a random row plays "heading"
    if len(rowsA)<2: return None
    idx=rng.randrange(len(rowsA)); pick=rowsA[idx]
    rest=[a for j,r in enumerate(rowsA) if j!=idx for a in r]
    if len(pick)<2 or len(rest)<3: return None
    return math.log(statistics.median(pick)/statistics.median(rest))

def S_obs(docs):
    xs=[R_first_vs_rest(ra) for _,ra in docs]; xs=[x for x in xs if x is not None]
    return (statistics.median(xs), len(xs)) if xs else (None,0)

def perm(docs, S_o, rng, ndraw=1000):   # DIRECTIONAL: heading LARGER => p = frac null median-R >= S_obs
    nulls=[]
    for _ in range(ndraw):
        xs=[R_randrow(ra,rng) for _,ra in docs]; xs=[x for x in xs if x is not None]
        if xs: nulls.append(statistics.median(xs))
    nm=statistics.median(nulls); ge=sum(1 for s in nulls if s>=S_o)
    return nm, (ge+1)/(len(nulls)+1)
# ============ END GIVEN FUNCTIONS ============

DATA_PATH = "experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"
SEED = 85085

# ---------- Positive control: synthetic docs ----------
def make_synthetic_docs(n_docs, inflate_first, rng):
    """Each doc: 2-4 rows, ~4-6 glyphs/row. Body areas ~ Uniform; first row x1.7 if inflate_first."""
    docs = []
    for _ in range(n_docs):
        nrows = rng.randint(2, 4)
        rowsA = []
        for ri in range(nrows):
            ng = rng.randint(4, 6)
            base = [rng.uniform(5000.0, 15000.0) for _ in range(ng)]
            if ri == 0 and inflate_first:
                base = [a * 1.7 for a in base]
            rowsA.append(base)
        docs.append(("SYNTH", rowsA))
    return docs

def pc_detect_once(rng, ndraw=1000):
    docs = make_synthetic_docs(40, True, rng)
    s, n = S_obs(docs)
    nm, p = perm(docs, s, rng, ndraw=ndraw)
    return s, nm, p

def pc_uniform_once(rng, ndraw=1000):
    docs = make_synthetic_docs(40, False, rng)
    s, n = S_obs(docs)
    nm, p = perm(docs, s, rng, ndraw=ndraw)
    return s, nm, p

def run_positive_control(rng):
    # DETECT: power over 15 reps
    detect_ps = []
    detect_s = None
    for _ in range(20):
        s, nm, p = pc_detect_once(rng, ndraw=1000)
        detect_ps.append(p)
        detect_s = s
    power_est = sum(1 for p in detect_ps if p <= 0.05) / len(detect_ps)
    detect_p = statistics.median(detect_ps)

    # FALSE-POSITIVE: fire-rate over 15 reps on uniform
    uni_ps = []
    for _ in range(20):
        s, nm, p = pc_uniform_once(rng, ndraw=1000)
        uni_ps.append(p)
    false_pos_rate = sum(1 for p in uni_ps if p <= 0.05) / len(uni_ps)

    # PC verdict: PASSED iff can detect (power>=0.5) AND doesn't fire on uniform (fpr<=0.10)
    pc_passed = (power_est >= 0.5) and (false_pos_rate <= 0.10)
    return {
        "pc_verdict": "PASSED" if pc_passed else "FAILED",
        "detect_p": float(detect_p),
        "power_est": float(power_est),
        "false_pos_rate": float(false_pos_rate),
        "pc_is_synthetic": True,
    }

# ---------- Main ----------
def main():
    rng = random.Random(SEED)
    docs = load_usable(DATA_PATH)

    # Global
    g_s, g_n = S_obs(docs)
    g_nm, g_p = perm(docs, g_s, rng, ndraw=1000)

    # Per-site
    sites_of_interest = ["Haghia Triada", "Khania", "Zakros"]
    per_site = []
    site_sig_count = 0
    for site in sites_of_interest:
        sdocs = [(s, ra) for (s, ra) in docs if s == site]
        if len(sdocs) < 15:
            per_site.append({"site": site, "n_docs": len(sdocs), "skipped": True})
            continue
        ss, sn = S_obs(sdocs)
        snm, sp = perm(sdocs, ss, rng, ndraw=1000)
        sig = bool(sp <= 0.05 and ss > 0)
        if sig:
            site_sig_count += 1
        per_site.append({
            "site": site,
            "S_obs": float(ss),
            "null_median": float(snm),
            "perm_p": float(sp),
            "n_docs": int(sn),
            "significant": sig,
        })

    # Positive control
    pc = run_positive_control(rng)
    pc_passed = (pc["pc_verdict"] == "PASSED")

    # Count sites with >=15 usable docs
    sites_with_15 = sum(1 for site in sites_of_interest
                        for sdocs in [[d for d in docs if d[0] == site]]
                        if len(sdocs) >= 15)

    # FROZEN VERDICT
    global_sig = (g_p <= 0.05 and g_s > 0)
    any_site_sig = site_sig_count >= 1

    if not pc_passed or pc["power_est"] < 0.5:
        verdict = "MACHINERY_UNINFORMATIVE" if not pc_passed else "HEADING_SIZE_UNDERPOWERED"
        # Distinguish: if PC failed calibration -> UNINFORMATIVE; if power<0.5 -> UNDERPOWERED
        if not pc_passed:
            verdict = "MACHINERY_UNINFORMATIVE"
        else:
            verdict = "HEADING_SIZE_UNDERPOWERED"
    elif sites_with_15 < 2:
        verdict = "HEADING_SIZE_UNDERPOWERED"
    elif pc_passed and global_sig and site_sig_count >= 2:
        verdict = "HEADING_SIZE_HIERARCHY_CROSS_SITE"
    elif pc_passed and (global_sig or any_site_sig) and site_sig_count < 2:
        verdict = "HEADING_SIZE_HIERARCHY_SITE_LOCAL"
    elif pc_passed and (not global_sig) and site_sig_count == 0:
        verdict = "NO_HEADING_SIZE_HIERARCHY"
    else:
        # Fallback: ambiguous middle cases -> site_local if any signal, else no hierarchy
        verdict = "HEADING_SIZE_HIERARCHY_SITE_LOCAL" if any_site_sig else "NO_HEADING_SIZE_HIERARCHY"

    out = {
        "task_id": "EPOCH-085",
        "method": "per-doc log area-ratio (first/top row median area vs all remaining rows); random-row-as-heading null; directional perm_p (frac null median-R >= S_obs); per-site + global + synthetic positive control.",
        "result": {
            "global": {"S_obs": float(g_s), "null_median": float(g_nm), "perm_p": float(g_p), "n_docs": int(g_n)},
            "per_site": per_site,
            "positive_control": pc,
            "sites_with_15_usable": sites_with_15,
            "site_sig_count": site_sig_count,
        },
        "verdict": verdict,
        "numbers": {
            "global": {"S_obs": float(g_s), "null_median": float(g_nm), "perm_p": float(g_p), "n_docs": int(g_n)},
            "per_site": per_site,
            "positive_control": pc,
        },
        "key_findings": [],
        "successor_hypotheses": [],
        "layer": "L2",
        "la_touched": True,
        "non_circular": "Geometry only (bbox areas, row y-positions). No sign/phonetic/semantic labels. Verdict mechanically derived from frozen rule on S_obs and perm_p.",
        "deviations": [],
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
