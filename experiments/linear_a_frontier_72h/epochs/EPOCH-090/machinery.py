import json, statistics, random, math

def rows_of(gl):
    pts=[{"h":g["bbox"][3], "yc":g["bbox"][1]+g["bbox"][3]/2.0, "w":g["bbox"][2],
          "left":g["bbox"][0], "right":g["bbox"][0]+g["bbox"][2], "xc":g["bbox"][0]+g["bbox"][2]/2.0} for g in gl]
    medh=statistics.median([p["h"] for p in pts]) or 1.0
    ys=sorted(pts,key=lambda p:p["yc"]); rows=[]; cur=[ys[0]]
    for p in ys[1:]:
        if abs(p["yc"]-cur[-1]["yc"])<=0.6*medh: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur); return rows

def cv(v):
    if len(v)<2: return None
    m=statistics.mean(v); return statistics.pstdev(v)/m if m else None

def row_extent(r):
    r=sorted(r,key=lambda p:p["xc"]); return max(p["right"] for p in r)-min(p["left"] for p in r)

def load_HT_rows(path):    # returns header_rows[], body_rows[] ; each row = {"extent","count","widths","gaps"}
    docs=json.load(open(path)); hdr=[]; bod=[]
    for d in docs:
        if d.get("site")!="Haghia Triada": continue
        gl=[g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"])==4 and not g.get("is_divider")]
        if len(gl)<6: continue
        rows=rows_of(gl)
        if len(rows)<2: continue
        for idx,r in enumerate(rows):
            rr=sorted(r,key=lambda p:p["xc"])
            widths=[p["w"] for p in rr]; gaps=[max(0.0, rr[i+1]["left"]-rr[i]["right"]) for i in range(len(rr)-1)]
            rec={"extent":row_extent(rr),"count":len(rr),"widths":widths,"gaps":gaps}
            (hdr if idx==0 else bod).append(rec)
    return hdr, bod

def assembly_null_median(rows, rng, ndraw=1000):    # pool this group's widths+gaps; rebuild each row's extent
    pw=[w for r in rows for w in r["widths"]]; pg=[g for r in rows for g in r["gaps"]]
    counts=[r["count"] for r in rows]; nl=[]
    for _ in range(ndraw):
        syn=[sum(rng.choice(pw) for _ in range(c))+sum(rng.choice(pg) for _ in range(max(0,c-1))) for c in counts]
        nl.append(cv(syn))
    return statistics.median(nl)

def ratio(rows, null_med):
    return cv([r["extent"] for r in rows]) / null_med

def bootstrap_D(hdr, bod, null_h, null_b, rng, nboot=2000):    # D = ratio_h - ratio_b, CI via doc-free row resample
    Ds=[]
    for _ in range(nboot):
        rh=[rng.choice(hdr) for _ in range(len(hdr))]; rb=[rng.choice(bod) for _ in range(len(bod))]
        ch=cv([r["extent"] for r in rh]); cb=cv([r["extent"] for r in rb])
        if ch is None or cb is None: continue
        Ds.append(ch/null_h - cb/null_b)
    Ds.sort(); n=len(Ds)
    return Ds[int(0.025*n)], Ds[int(0.975*n)], statistics.median(Ds)

# ===================== POSITIVE CONTROL (synthetic) =====================
def synth_doc_rows(rng, n_rows, n_glyphs_per_row, width_pool, gap_pool, header_constrained, body_constrained, target_ext):
    """Build a synthetic doc's rows. constrained=True -> extent pinned near target_ext (low CV across docs);
    constrained=False -> extent = sum of random widths+gaps (free assembly)."""
    rows=[]
    for ri in range(n_rows):
        c=n_glyphs_per_row
        if (ri==0 and header_constrained) or (ri>0 and body_constrained):
            # constrained: extent pinned near target_ext with small jitter
            ext=target_ext + rng.gauss(0, target_ext*0.03)
            # build widths/gaps that sum ~ ext (use pool, then scale)
            ws=[rng.choice(width_pool) for _ in range(c)]
            gs=[rng.choice(gap_pool) for _ in range(c-1)]
            cur=sum(ws)+sum(gs)
            if cur<=0: cur=1.0
            scale=ext/cur
            ws=[w*scale for w in ws]; gs=[g*scale for g in gs]
            ext=sum(ws)+sum(gs)
        else:
            # free assembly
            ws=[rng.choice(width_pool) for _ in range(c)]
            gs=[rng.choice(gap_pool) for _ in range(c-1)]
            ext=sum(ws)+sum(gs)
        rows.append({"extent":ext,"count":c,"widths":ws,"gaps":gs})
    return rows

def build_synth_corpus(rng, n_docs, header_constrained, body_constrained, width_pool, gap_pool, target_ext):
    hdr=[]; bod=[]
    for _ in range(n_docs):
        n_rows=rng.randint(2,5)
        n_glyphs=rng.randint(4,9)
        rows=synth_doc_rows(rng, n_rows, n_glyphs, width_pool, gap_pool, header_constrained, body_constrained, target_ext)
        hdr.append(rows[0]); bod.extend(rows[1:])
    return hdr, bod

def pc_one_arm(rng, header_constrained, body_constrained, width_pool, gap_pool, target_ext, n_docs=140):
    hdr, bod = build_synth_corpus(rng, n_docs, header_constrained, body_constrained, width_pool, gap_pool, target_ext)
    null_h=assembly_null_median(hdr, rng, 1000); null_b=assembly_null_median(bod, rng, 1000)
    rh=ratio(hdr,null_h); rb=ratio(bod,null_b); D_obs=rh-rb
    lo,hi,med=bootstrap_D(hdr,bod,null_h,null_b,rng,2000)
    includes_zero = (lo<=0<=hi)
    return D_obs, lo, hi, includes_zero

def run_positive_control(master_rng):
    # pools derived from realistic geometry ranges
    width_pool=[40.0,60.0,80.0,100.0,120.0,150.0]
    gap_pool=[10.0,20.0,30.0,40.0,50.0]
    target_ext=400.0
    # (a) DETECT: header constrained, body free -> expect D<0, CI excludes 0
    detect_hits=0; detect_n=15
    for rep in range(detect_n):
        rng=random.Random(master_rng.randrange(10**9))
        D_obs,lo,hi,inc=pc_one_arm(rng, True, False, width_pool, gap_pool, target_ext)
        if (D_obs<0) and (not inc): detect_hits+=1
    detect_power=detect_hits/detect_n
    # (b) FALSE-POSITIVE: both constrained equally -> expect CI includes 0
    fp_hits=0; fp_n=15
    for rep in range(fp_n):
        rng=random.Random(master_rng.randrange(10**9))
        D_obs,lo,hi,inc=pc_one_arm(rng, True, True, width_pool, gap_pool, target_ext)
        # "fire" = falsely declares header-specific = CI excludes 0 AND D<0
        if (D_obs<0) and (not inc): fp_hits+=1
    false_pos_rate=fp_hits/fp_n
    pc_passed = (detect_power>=0.5) and (false_pos_rate<=0.10)
    return {"pc_verdict":"PASSED" if pc_passed else "FAILED",
            "detect_power":detect_power, "false_pos_rate":false_pos_rate,
            "pc_is_synthetic":True}

def main():
    DATA="experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"
    SEED=90210
    master_rng=random.Random(SEED)
    hdr, bod = load_HT_rows(DATA)
    n_h=len(hdr); n_b=len(bod)
    # fixed assembly-null medians from full data
    rng_h=random.Random(master_rng.randrange(10**9))
    rng_b=random.Random(master_rng.randrange(10**9))
    null_h=assembly_null_median(hdr, rng_h, 1000)
    null_b=assembly_null_median(bod, rng_b, 1000)
    ratio_h=ratio(hdr, null_h)
    ratio_b=ratio(bod, null_b)
    D_obs=ratio_h-ratio_b
    rng_boot=random.Random(master_rng.randrange(10**9))
    ci_lo, ci_hi, ci_med = bootstrap_D(hdr, bod, null_h, null_b, rng_boot, 2000)
    ci_includes_0 = (ci_lo<=0<=ci_hi)
    # positive control
    pc=run_positive_control(master_rng)
    # verdict (frozen)
    underpowered = (n_h<60) or (n_b<60) or (pc["detect_power"]<0.5)
    if pc["pc_verdict"]=="FAILED":
        verdict="MACHINERY_UNINFORMATIVE"
    elif underpowered:
        verdict="WIDTH_CONSTRAINT_DIFF_UNDERPOWERED"
    elif ci_includes_0:
        verdict="WIDTH_CONSTRAINT_DOC_WIDE"
    elif (not ci_includes_0) and D_obs<0:
        verdict="WIDTH_CONSTRAINT_HEADER_SPECIFIC"
    else:
        # CI excludes 0 but D>=0 -> header LESS constrained; not header-specific -> treat as DOC_WIDE (no header-specific constraint)
        verdict="WIDTH_CONSTRAINT_DOC_WIDE"
    out={
      "task_id":"EPOCH-090",
      "n_header":n_h, "n_body":n_b,
      "null_h":null_h, "null_b":null_b,
      "ratio_header":ratio_h, "ratio_body":ratio_b,
      "D_obs":D_obs,
      "ci_lo":ci_lo, "ci_hi":ci_hi, "ci_med":ci_med,
      "ci_includes_0":ci_includes_0,
      "verdict":verdict,
      "positive_control":pc
    }
    print(json.dumps(out, indent=2))

if __name__=="__main__":
    main()
