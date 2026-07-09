import json, statistics, random

def load_usable(path):
    docs = json.load(open(path)); out=[]
    for d in docs:
        gl=[g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"])==4 and not g.get("is_divider")]
        if len(gl)>=6: out.append((d.get("site"), gl))
    return out

def rows_of(gl):                        # y-band rows (tol 0.6 x median glyph height), each item (left,width,ycen,h)
    pts=[(g["bbox"][0], g["bbox"][2], g["bbox"][1]+g["bbox"][3]/2.0, g["bbox"][3]) for g in gl]
    medh=statistics.median([p[3] for p in pts]) or 1.0
    ys=sorted(pts,key=lambda p:p[2]); rows=[]; cur=[ys[0]]
    for p in ys[1:]:
        if abs(p[2]-cur[-1][2])<=0.6*medh: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur); return rows

def cv(v):
    if len(v)<2: return None
    m=statistics.mean(v); return statistics.pstdev(v)/m if m else None

def obs_pitch_cv(gl):                   # E079 observed center-to-center pitch CV
    ps=[]
    for r in rows_of(gl):
        if len(r)<3: continue
        rr=sorted(r,key=lambda p:p[0]); cens=[p[0]+p[1]/2.0 for p in rr]
        ps+=[b-a for a,b in zip(cens,cens[1:])]
    return cv(ps) if len(ps)>=3 else None

def null_pitch_cv(gl, rng):             # WIDTH-PRESERVING random-gap null: keep widths + span, randomize gaps
    ps=[]
    for r in rows_of(gl):
        if len(r)<3: continue
        rr=sorted(r,key=lambda p:p[0]); w=[p[1] for p in rr]; cens=[p[0]+p[1]/2.0 for p in rr]
        span=cens[-1]-cens[0]; k=len(rr)-1
        halfsum=sum(w[i]/2.0+w[i+1]/2.0 for i in range(k))   # width contribution to the span
        gapspace=span-halfsum
        if gapspace<=0:
            gaps=[0.0]*k
        else:
            cuts=sorted(rng.uniform(0,gapspace) for _ in range(k-1)); b=[0.0]+cuts+[gapspace]
            gaps=[b[i+1]-b[i] for i in range(k)]
        ps += [w[i]/2.0+gaps[i]+w[i+1]/2.0 for i in range(k)]   # reconstruct pitch = halfw+gap+halfw
    return cv(ps) if len(ps)>=3 else None

def S_obs(docs):                        # median doc obs pitch-CV
    xs=[obs_pitch_cv(gl) for _,gl in docs]; xs=[x for x in xs if x is not None]
    return statistics.median(xs), len(xs)

def perm(docs, S_o, rng, ndraw=500):    # one-sided: deliberate spacing = observed BELOW the width-preserving null
    nulls=[]
    for _ in range(ndraw):
        xs=[null_pitch_cv(gl,rng) for _,gl in docs]; xs=[x for x in xs if x is not None]
        nulls.append(statistics.median(xs))
    nm=statistics.median(nulls)
    ge=sum(1 for s in nulls if s<=S_o)              # frac null <= observed  (LOW => observed is low => deliberate)
    return nm, (ge+1)/(ndraw+1)

# ===================== POSITIVE CONTROL (synthetic) =====================

def _synth_doc(rng, mode, n_glyphs=None, width_lo=4.0, width_hi=9.0):
    """Build a synthetic doc as a list of glyph dicts with bbox, single row.
    mode='equal' -> equal gaps (deliberate even spacing); mode='random' -> random gaps.
    Variable widths ~ Uniform[width_lo,width_hi]."""
    n = n_glyphs or rng.randint(6, 12)
    widths = [rng.uniform(width_lo, width_hi) for _ in range(n)]
    # gap budget
    total_gap = rng.uniform(20.0, 80.0)
    k = n - 1
    if mode == "equal":
        gaps = [total_gap / k] * k
    else:  # random
        cuts = sorted(rng.uniform(0, total_gap) for _ in range(k - 1))
        b = [0.0] + cuts + [total_gap]
        gaps = [b[i + 1] - b[i] for i in range(k)]
    # lay out left->right; bbox = [left, top, width, height]
    left = 10.0
    top = 50.0
    gl = []
    x = left
    for i in range(n):
        h = rng.uniform(width_lo, width_hi)  # height ~ similar scale (irrelevant to pitch)
        gl.append({"sign": "SYN", "bbox": [x, top, widths[i], h], "is_divider": False})
        if i < k:
            x = x + widths[i] + gaps[i]
    return gl

def _synth_docs(rng, mode, ndocs=40):
    out = []
    for _ in range(ndocs):
        gl = _synth_doc(rng, mode)
        out.append(("SYN", gl))
    return out

def positive_control(rng_seed=12345, reps=15, ndraw=200):
    """Return dict with pc_verdict, detect_p, power_est, false_pos_rate."""
    # (a) DETECT arm: single representative run for detect_p
    rng_a = random.Random(rng_seed)
    docs_a = _synth_docs(rng_a, "equal")
    S_o_a, _ = S_obs(docs_a)
    nm_a, p_a = perm(docs_a, S_o_a, rng_a, ndraw=ndraw)
    detect_p = p_a

    # power_est over reps: fraction of reps where detect arm yields perm_p<=0.05
    detects = 0
    for r in range(reps):
        rng = random.Random(rng_seed + 1000 + r)
        docs = _synth_docs(rng, "equal")
        S_o, _ = S_obs(docs)
        _, p = perm(docs, S_o, rng, ndraw=ndraw)
        if p <= 0.05:
            detects += 1
    power_est = detects / reps

    # (b) FALSE-POSITIVE arm over reps: fraction where random-gap docs yield perm_p<=0.05
    fps = 0
    for r in range(reps):
        rng = random.Random(rng_seed + 5000 + r)
        docs = _synth_docs(rng, "random")
        S_o, _ = S_obs(docs)
        _, p = perm(docs, S_o, rng, ndraw=ndraw)
        if p <= 0.05:
            fps += 1
    false_pos_rate = fps / reps

    passed = (detect_p <= 0.05) and (power_est >= 0.5) and (false_pos_rate <= 0.10)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": detect_p,
        "power_est": power_est,
        "false_pos_rate": false_pos_rate,
        "pc_is_synthetic": True,
        "_detect_S_obs": S_o_a,
        "_detect_null_median": nm_a,
    }

# ===================== MAIN =====================

def main():
    path = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h/experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"
    docs = load_usable(path)

    # sites with >=15 usable docs
    from collections import defaultdict
    by_site = defaultdict(list)
    for site, gl in docs:
        by_site[site].append((site, gl))
    qualifying = {s: v for s, v in by_site.items() if len(v) >= 15}

    rng = random.Random(20240607)

    # POSITIVE CONTROL FIRST
    pc = positive_control()

    # Global
    S_o, n_docs = S_obs(docs)
    nm, p = perm(docs, S_o, rng, ndraw=500)
    ratio = S_o / nm if nm else None

    # Per-site
    per_site = []
    for site in sorted(qualifying):
        sdocs = qualifying[site]
        s_So, s_n = S_obs(sdocs)
        s_nm, s_p = perm(sdocs, s_So, random.Random(rng.randint(0, 10**9)), ndraw=500)
        per_site.append({
            "site": site,
            "S_obs": s_So,
            "null_median": s_nm,
            "perm_p": s_p,
            "deliberate": bool(s_p <= 0.05),
            "n_docs": s_n,
        })

    n_sig_sites = sum(1 for s in per_site if s["deliberate"])

    # FROZEN VERDICT
    if pc["pc_verdict"] != "PASSED":
        verdict = "MACHINERY_UNINFORMATIVE"
    elif len(per_site) < 2 or pc["power_est"] < 0.5:
        verdict = "HORIZONTAL_SPACING_UNDERPOWERED"
    elif p <= 0.05 and n_sig_sites >= 2:
        verdict = "HORIZONTAL_SPACING_DELIBERATE_CROSS_SITE"
    elif p <= 0.05:
        verdict = "HORIZONTAL_SPACING_DELIBERATE_SITE_LOCAL"
    else:
        verdict = "HORIZONTAL_REGULARITY_WIDTH_DRIVEN"

    out = {
        "task_id": "EPOCH-083",
        "method": "width-preserving random-gap permutation test on horizontal pitch-CV (E079 qualification)",
        "result": {
            "global_S_obs": S_o,
            "global_null_median": nm,
            "global_perm_p": p,
            "global_ratio": ratio,
            "n_docs": n_docs,
            "n_qualifying_sites": len(per_site),
            "n_significant_sites": n_sig_sites,
            "pc_verdict": pc["pc_verdict"],
        },
        "verdict": verdict,
        "numbers": {
            "global": {
                "S_obs": S_o,
                "null_median": nm,
                "perm_p": p,
                "ratio": ratio,
                "n_docs": n_docs,
            },
            "per_site": per_site,
            "positive_control": {
                "pc_verdict": pc["pc_verdict"],
                "detect_p": pc["detect_p"],
                "power_est": pc["power_est"],
                "false_pos_rate": pc["false_pos_rate"],
                "pc_is_synthetic": True,
            },
        },
        "key_findings": [],
        "successor_hypotheses": [],
        "layer": "L2",
        "la_touched": True,
        "non_circular": "Width-preserving null reuses each glyph's actual width and the row center-span; only gap allocation is randomized, isolating gap-regularity from width-regularity. No sign identities used; bbox geometry only.",
        "deviations": [],
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
