import json, statistics, random, math

def rows_of(gl):    # top->bottom rows; y-band tol 0.6*median glyph height
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

def load_HT(path):    # returns (extents[], counts[], pool_widths[], pool_gaps[])
    docs=json.load(open(path)); extents=[]; counts=[]; pw=[]; pg=[]
    for d in docs:
        if d.get("site")!="Haghia Triada": continue
        gl=[g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"])==4 and not g.get("is_divider")]
        if len(gl)<6: continue
        rows=rows_of(gl)
        if len(rows)<2: continue
        r0=sorted(rows[0], key=lambda p:p["xc"])
        extents.append(max(p["right"] for p in r0)-min(p["left"] for p in r0)); counts.append(len(r0))
        for p in r0: pw.append(p["w"])
        for i in range(len(r0)-1): pg.append(max(0.0, r0[i+1]["left"]-r0[i]["right"]))
    return extents, counts, pw, pg

def assembly_extent(cnt, pw, pg, rng):
    w=sum(rng.choice(pw) for _ in range(cnt)); g=sum(rng.choice(pg) for _ in range(max(0,cnt-1))); return w+g

def perm(extents, counts, pw, pg, rng, ndraw=2000):    # CONSTRAINED = obs CV BELOW null; perm_p = frac null CV <= obs
    o=cv(extents); nl=[cv([assembly_extent(c,pw,pg,rng) for c in counts]) for _ in range(ndraw)]
    nm=statistics.median(nl); le=sum(1 for x in nl if x<=o)
    return o, nm, (le+1)/(ndraw+1)

# ---------- doc x-extent (for extent/doc ratio) ----------
def doc_x_extents(path):
    docs=json.load(open(path)); out=[]
    for d in docs:
        if d.get("site")!="Haghia Triada": continue
        gl=[g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"])==4 and not g.get("is_divider")]
        if len(gl)<6: continue
        rows=rows_of(gl)
        if len(rows)<2: continue
        rights=[g["bbox"][0]+g["bbox"][2] for g in gl]; lefts=[g["bbox"][0] for g in gl]
        out.append(max(rights)-min(lefts))
    return out

# ---------- POSITIVE CONTROL ----------
def pc_detect(extents, counts, pw, pg, rng, reps=30, ndraw=2000):
    # build ~140 synthetic docs with FIXED target extent (independent of count)
    E0=statistics.median(extents) if extents else 1000.0
    sig=0.03*E0  # small noise ~3% of target
    ps=[]
    for _ in range(reps):
        synth=[E0+rng.gauss(0,sig) for _ in extents]
        o,nm,pp=perm(synth, counts, pw, pg, rng, ndraw)
        ps.append(pp)
    detect_p=statistics.median(ps)
    power_est=sum(1 for p in ps if p<=0.05)/len(ps)
    return detect_p, power_est

def pc_falsepos(extents, counts, pw, pg, rng, reps=30, ndraw=2000):
    # build ~140 docs whose extent IS random assembly at a random count
    cnt_lo, cnt_hi = min(counts), max(counts)
    if cnt_hi<=cnt_lo: cnt_hi=cnt_lo+1
    fires=0; ps=[]
    for _ in range(reps):
        rc=[rng.randint(cnt_lo, cnt_hi) for _ in extents]
        synth=[assembly_extent(c, pw, pg, rng) for c in rc]
        o,nm,pp=perm(synth, rc, pw, pg, rng, ndraw)
        ps.append(pp)
        if pp<=0.05: fires+=1
    false_pos_rate=fires/len(ps)
    return false_pos_rate

def main():
    rng=random.Random(20240809)
    path="experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"
    extents, counts, pw, pg = load_HT(path)
    n_docs=len(extents)
    obs_cv, null_median, perm_p = perm(extents, counts, pw, pg, rng, 2000)
    ratio = obs_cv/null_median if null_median else None
    # extent / doc x-extent
    dxe=doc_x_extents(path)
    extent_over_doc = statistics.median([e/de for e,de in zip(extents, dxe)]) if dxe else None
    # PC -- independent RNG per arm to avoid cross-arm RNG-state coupling (math unchanged)
    rng_det = random.Random(424242)
    rng_fp  = random.Random(909090)
    detect_p, power_est = pc_detect(extents, counts, pw, pg, rng_det, reps=30, ndraw=2000)
    fpr = pc_falsepos(extents, counts, pw, pg, rng_fp, reps=30, ndraw=2000)
    pc_passed = (power_est>=0.5) and (fpr<=0.10)
    pc_verdict = "PASSED" if pc_passed else "FAILED"
    # verdict
    if not pc_passed:
        verdict="MACHINERY_UNINFORMATIVE"
    elif n_docs<60 or power_est<0.5:
        verdict="HEADER_WIDTH_UNDERPOWERED"
    elif perm_p<=0.05:
        verdict="HEADER_WIDTH_CONSTRAINED"
    else:
        verdict="HEADER_WIDTH_NOT_CONSTRAINED"
    out={
        "task_id":"EPOCH-089",
        "method":"CV of first-row x-extent vs assembly null (pooled widths+gaps at actual counts); perm_p=frac(null CV<=obs CV); positive control fixed-extent detect + random-assembly false-positive.",
        "result": verdict,
        "verdict": verdict,
        "numbers":{
            "width":{"obs_cv":obs_cv, "null_median":null_median, "perm_p":perm_p,
                     "ratio":ratio, "n_docs":n_docs, "extent_over_doc":extent_over_doc},
            "positive_control":{"pc_verdict":pc_verdict, "detect_p":detect_p,
                                "power_est":power_est, "false_pos_rate":fpr, "pc_is_synthetic":True},
            "pool_sizes":{"n_widths":len(pw), "n_gaps":len(pg)},
            "count_stats":{"min":min(counts), "max":max(counts), "median":statistics.median(counts)}
        },
        "key_findings":[
            f"obs first-row x-extent CV={obs_cv:.4f} vs assembly-null median {null_median:.4f} (ratio {ratio:.3f}), perm_p={perm_p:.5f}.",
            f"extent/doc-x-extent median ratio = {extent_over_doc:.3f} (header occupies ~{extent_over_doc*100:.0f}% of document writing width).",
            f"Positive control: detect_p={detect_p:.4f} (power_est={power_est:.2f}), false-positive rate={fpr:.3f} -> {pc_verdict}.",
            f"n_docs={n_docs} usable HT docs (>=6 non-divider bbox glyphs, >=2 rows).",
            f"Verdict={verdict}: {'extent is MORE constant than random assembly -> writing width regularized.' if verdict=='HEADER_WIDTH_CONSTRAINED' else ('extent NOT more constant than random assembly.' if verdict=='HEADER_WIDTH_NOT_CONSTRAINED' else 'machinery/calibration issue.')}"
        ],
        "successor_hypotheses":[
            "E090: Does the constrained extent scale with TABLET support width (compare Tablet vs other supports) to separate tablet-dimension from scribal-convention explanations.",
            "E091: Within fixed-extent docs, is per-glyph width the free variable (count*width ~ const) or is count fixed and width absorbs slack.",
            "E092: Does the same width constraint hold for non-header (body) rows, or is it header-specific.",
            "E093: Combine width-constraint with E087 size<->count: predict header count from (target_extent / mean_glyph_width) and test residual structure.",
            "E094: Test whether inter-glyph gaps shrink as glyph count rises (compression to fit fixed width) vs gaps staying constant.",
            "E095: Cross-site replication of the extent-CV-below-null signature on non-HT Linear A corpora."
        ],
        "layer":"L2",
        "la_touched":True,
        "non_circular":"Geometry-only (bbox positions/widths); opaque doc IDs; no semantic sign values used; metric and null derived from spatial extent, independent of E087's size<->count correlation.",
        "deviations":[
            "Doc x-extent computed from all non-divider glyph bboxes (no doc-level width field present in source JSON); used for extent/doc ratio only, not for the verdict metric.",
            "PC false-positive arm draws random counts in [min,max] of observed counts (random-assembly definition per protocol)."
        ]
    }
    print(json.dumps(out, indent=2))

if __name__=="__main__":
    main()
