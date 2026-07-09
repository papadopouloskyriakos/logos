import json, statistics, random

def load_usable(path):
    docs=json.load(open(path)); out=[]
    for d in docs:
        gl=[g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"])==4 and not g.get("is_divider")]
        if len(gl)>=6: out.append((d.get("site"), gl))
    return out

def rows_of(gl):    # y-band rows (tol 0.6 x median glyph height); item = (top,h,xcen,ycen)
    pts=[(g["bbox"][1], g["bbox"][3], g["bbox"][0]+g["bbox"][2]/2.0, g["bbox"][1]+g["bbox"][3]/2.0) for g in gl]
    medh=statistics.median([p[1] for p in pts]) or 1.0
    ys=sorted(pts,key=lambda p:p[3]); rows=[]; cur=[ys[0]]
    for p in ys[1:]:
        if abs(p[3]-cur[-1][3])<=0.6*medh: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur); return rows

def row_center_height(gl):   # sorted list of (row_ycenter, row_height) ; row_height = median glyph height in row
    rc=[(statistics.median([p[3] for p in r]), statistics.median([p[1] for p in r])) for r in rows_of(gl)]
    rc.sort(); return rc

def cv(v):
    if len(v)<2: return None
    m=statistics.mean(v); return statistics.pstdev(v)/m if m else None

def obs_linepitch_cv(gl):
    rc=row_center_height(gl)
    if len(rc)<3: return None
    cens=[c[0] for c in rc]
    return cv([cens[i+1]-cens[i] for i in range(len(cens)-1)])

def null_linepitch_cv(gl, rng):   # HEIGHT-PRESERVING random-gap null: keep row heights + span, randomize gaps
    rc=row_center_height(gl)
    if len(rc)<3: return None
    cens=[c[0] for c in rc]; hts=[c[1] for c in rc]; k=len(rc)-1
    span=cens[-1]-cens[0]; halfsum=sum(hts[i]/2.0+hts[i+1]/2.0 for i in range(k))
    gapspace=span-halfsum
    if gapspace<=0:
        pitches=[hts[i]/2.0+hts[i+1]/2.0 for i in range(k)]
    else:
        cuts=sorted(rng.uniform(0,gapspace) for _ in range(k-1)); b=[0.0]+cuts+[gapspace]
        gaps=[b[i+1]-b[i] for i in range(k)]
        pitches=[hts[i]/2.0+gaps[i]+hts[i+1]/2.0 for i in range(k)]
    return cv(pitches)

def S_obs(docs):
    xs=[obs_linepitch_cv(gl) for _,gl in docs]; xs=[x for x in xs if x is not None]
    return statistics.median(xs), len(xs)

def perm(docs, S_o, rng, ndraw=500):   # deliberate = observed BELOW the height-preserving null
    nulls=[]
    for _ in range(ndraw):
        xs=[null_linepitch_cv(gl,rng) for _,gl in docs]; xs=[x for x in xs if x is not None]
        nulls.append(statistics.median(xs))
    nm=statistics.median(nulls); ge=sum(1 for s in nulls if s<=S_o)
    return nm, (ge+1)/(ndraw+1)

# ---------- Positive Control (synthetic) ----------
def synth_doc(rng, equal_gaps, nrows=4, nglyphs_per_row=6, h_lo=6.0, h_hi=12.0, gap=8.0):
    """Build a synthetic doc with given row heights; gaps either equal (deliberate) or random."""
    hts=[rng.uniform(h_lo,h_hi) for _ in range(nrows)]
    if equal_gaps:
        gaps=[gap for _ in range(nrows-1)]
    else:
        # random gaps, same total span budget as equal-gaps arm for fairness
        total=gap*(nrows-1)
        cuts=sorted(rng.uniform(0,total) for _ in range(nrows-2))
        b=[0.0]+cuts+[total]
        gaps=[b[i+1]-b[i] for i in range(nrows-1)]
    # row centers
    y0=0.0
    centers=[y0+hts[0]/2.0]
    for i in range(nrows-1):
        centers.append(centers[-1]+hts[i]/2.0+gaps[i]+hts[i+1]/2.0)
    # glyphs: bbox = [x, top, w, h]; place nglyphs_per_row across each row at the row center
    gl=[]
    for r in range(nrows):
        h=hts[r]; yc=centers[r]; top=yc-h/2.0
        for j in range(nglyphs_per_row):
            x=10.0+j*15.0; w=rng.uniform(6,10)
            gl.append({"sign":"X","bbox":[x,top,w,h],"is_divider":False})
    return gl

def pc_arm(rng, equal_gaps, ndocs=40, ndraw=500):
    docs=[("SYN", synth_doc(rng, equal_gaps)) for _ in range(ndocs)]
    S_o,n=S_obs(docs)
    nm,p=perm(docs,S_o,rng,ndraw=ndraw)
    return S_o,nm,p

def positive_control(seed=12345, reps=15, ndraw=500):
    rng=random.Random(seed)
    # (a) DETECT arm
    detect_ps=[]
    for _ in range(reps):
        S_o,nm,p=pc_arm(rng, equal_gaps=True, ndraw=ndraw)
        detect_ps.append(p)
    detect_p=statistics.median(detect_ps)
    power_est=sum(1 for p in detect_ps if p<=0.05)/len(detect_ps)
    # (b) FALSE-POSITIVE arm
    fp_ps=[]
    for _ in range(reps):
        S_o,nm,p=pc_arm(rng, equal_gaps=False, ndraw=ndraw)
        fp_ps.append(p)
    false_pos_rate=sum(1 for p in fp_ps if p<=0.05)/len(fp_ps)
    passed = (power_est>=0.5) and (false_pos_rate<=0.10)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": detect_p,
        "power_est": power_est,
        "false_pos_rate": false_pos_rate,
        "pc_is_synthetic": True,
    }

# ---------- main ----------
def main():
    path="experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"
    docs=load_usable(path)
    # filter to docs with >=3 rows
    docs=[(s,gl) for s,gl in docs if len(rows_of(gl))>=3]
    # site counts
    from collections import Counter
    sc=Counter(s for s,_ in docs)
    target_sites=["Haghia Triada","Khania","Zakros"]
    rng=random.Random(20240804)

    # global
    S_o,n=S_obs(docs)
    nm,p=perm(docs,S_o,rng,ndraw=500)
    ratio=S_o/nm if nm else None
    glob={"S_obs":S_o,"null_median":nm,"perm_p":p,"ratio":ratio,"n_docs":n}

    # per-site
    per_site=[]
    for site in target_sites:
        sdocs=[(s,gl) for s,gl in docs if s==site]
        if len(sdocs)<15:
            per_site.append({"site":site,"n_docs":len(sdocs),"S_obs":None,"null_median":None,"perm_p":None,"deliberate":False,"skipped":True})
            continue
        so,ns=S_obs(sdocs)
        snm,sp=perm(sdocs,so,rng,ndraw=500)
        per_site.append({"site":site,"n_docs":ns,"S_obs":so,"null_median":snm,"perm_p":sp,"deliberate":bool(sp<=0.05),"skipped":False})

    # PC
    pc=positive_control()

    # verdict
    pc_passed = pc["pc_verdict"]=="PASSED"
    n_sites_sig=sum(1 for s in per_site if (not s.get("skipped")) and s["deliberate"])
    n_sites_usable=sum(1 for s in per_site if (not s.get("skipped")))
    if not pc_passed:
        verdict="MACHINERY_UNINFORMATIVE"
    elif n_sites_usable<2 or pc["power_est"]<0.5:
        verdict="LINE_SPACING_UNDERPOWERED"
    elif p<=0.05 and n_sites_sig>=2:
        verdict="LINE_SPACING_DELIBERATE_CROSS_SITE"
    elif p<=0.05:
        verdict="LINE_SPACING_DELIBERATE_SITE_LOCAL"
    else:
        verdict="LINE_REGULARITY_HEIGHT_DRIVEN"

    out={
        "task_id":"EPOCH-084",
        "method":"vertical line-pitch-CV vs HEIGHT-PRESERVING random-gap null (per-doc median, 500-draw permutation); deliberate = observed BELOW null",
        "result":verdict,
        "verdict":verdict,
        "numbers":{
            "global":glob,
            "per_site":per_site,
            "positive_control":pc,
            "site_counts":dict(sc),
        },
        "key_findings":[
            f"Global observed line-pitch-CV {S_o:.4f} vs height-preserving null median {nm:.4f} (perm_p={p:.4f}, ratio={ratio:.3f}).",
            f"Per-site significance: {n_sites_sig}/{n_sites_usable} usable sites show deliberate line-spacing (observed below null).",
            f"Positive control: power_est={pc['power_est']:.2f}, false_pos_rate={pc['false_pos_rate']:.2f} -> {pc['pc_verdict']}.",
            f"Verdict: {verdict}.",
        ],
        "successor_hypotheses":[
            "E085: If deliberate, test whether inter-line gaps follow a fixed module (integer multiple of a base unit) cross-site.",
            "E086: Compare vertical line-spacing regularity against horizontal column-spacing regularity within the same docs (E083 vs E084 contrast).",
            "E087: Test whether deliberate line-spacing correlates with document support type (tablet vs other) or period.",
            "E088: If height-driven, decompose pitch variance into height-variance vs gap-variance contributions per site.",
            "E089: Examine whether row-height uniformity itself is deliberate (test row-height-CV against a glyph-height null).",
        ],
        "layer":"L2",
        "la_touched":True,
        "non_circular":"Opaque IDs; geometry only (positions, heights); null preserves row heights so any deliberate signal must come from the gaps; no semantic/phonetic content used.",
        "deviations":[],
    }
    print(json.dumps(out,indent=2,default=str))

if __name__=="__main__":
    main()
