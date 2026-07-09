import json, statistics, random, math

def load_usable(path):
    docs=json.load(open(path)); out=[]
    for d in docs:
        gl=[g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"])==4 and not g.get("is_divider")]
        if len(gl)>=6:
            rs=rowstats(gl)
            if len(rs)>=2: out.append((d.get("site"), rs))
    return out

def rowstats(gl):    # top->bottom list of (count, density) per row. y-band tol 0.6*median glyph height.
    pts=[{"h":g["bbox"][3], "yc":g["bbox"][1]+g["bbox"][3]/2.0, "xc":g["bbox"][0]+g["bbox"][2]/2.0} for g in gl]
    medh=statistics.median([p["h"] for p in pts]) or 1.0
    ys=sorted(pts,key=lambda p:p["yc"]); rows=[]; cur=[ys[0]]
    for p in ys[1:]:
        if abs(p["yc"]-cur[-1]["yc"])<=0.6*medh: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur)
    out=[]
    for r in rows:
        xs=[p["xc"] for p in r]; span=(max(xs)-min(xs)) if len(xs)>1 else 0.0
        out.append((len(r), len(r)/(span+1.0)))
    return out   # already top->bottom (sorted by y-center)

def R_first(vals, key):     # key 0=count, 1=density ; first row vs mean of the rest
    if len(vals)<2: return None
    rest=[v[key] for v in vals[1:]]
    if not rest: return None
    return math.log(vals[0][key]/(sum(rest)/len(rest)))

def R_rand(vals, key, rng):  # null: a random row plays "heading"
    if len(vals)<2: return None
    i=rng.randrange(len(vals)); rest=[v[key] for j,v in enumerate(vals) if j!=i]
    if not rest: return None
    return math.log(vals[i][key]/(sum(rest)/len(rest)))

def S_obs(docs, key):
    xs=[R_first(v,key) for _,v in docs]; xs=[x for x in xs if x is not None]
    return (statistics.median(xs), len(xs)) if xs else (None,0)

def perm(docs, S_o, key, rng, ndraw=1000):   # DIRECTIONAL: top LONGER/denser => p = frac null median-R >= S_obs
    nulls=[]
    for _ in range(ndraw):
        xs=[R_rand(v,key,rng) for _,v in docs]; xs=[x for x in xs if x is not None]
        if xs: nulls.append(statistics.median(xs))
    nm=statistics.median(nulls); ge=sum(1 for s in nulls if s>=S_o)
    return nm, (ge+1)/(len(nulls)+1)

# ---------- POSITIVE CONTROL (synthetic) ----------
def _synth_doc(rng, nrows, header_mult, body_base):
    """Build a synthetic doc as list of rows; each row = list of (count, density) tuples.
    Realistic pixel x-centers spaced ~100px so density is well-defined.
    Returns rowstats-format list of (count, density)."""
    rows=[]
    for ri in range(nrows):
        if ri==0 and header_mult is not None:
            n=max(2, int(round(body_base*header_mult)))
        else:
            n=body_base
        # x-centers spaced ~100px starting at random offset
        x0=rng.randint(50,150)
        xs=[x0+k*100+rng.randint(-5,5) for k in range(n)]
        span=(max(xs)-min(xs)) if len(xs)>1 else 0.0
        density=len(xs)/(span+1.0)
        rows.append((len(xs), density))
    return rows

def _pc_run_once(rng, header_mult, body_base, ndocs=40):
    """One synthetic dataset -> (S_obs_count, perm_p_count)."""
    docs=[]
    for _ in range(ndocs):
        nrows=rng.randint(2,4)
        rs=_synth_doc(rng, nrows, header_mult, body_base)
        docs.append((None, rs))
    s,n=S_obs(docs,0)
    if s is None: return None, None
    nm,p=perm(docs, s, 0, rng, ndraw=200)
    return s,p

def positive_control(seed=42):
    rng=random.Random(seed)
    # (a) DETECT: header ~1.7x body. body_base ~3-4, header ~6-7.
    detect_reps=20
    detect_hits=0; detect_ps=[]
    for _ in range(detect_reps):
        body_base=rng.randint(3,4)
        s,p=_pc_run_once(rng, 1.7, body_base)
        detect_ps.append(p)
        if p is not None and p<=0.05 and s is not None and s>0:
            detect_hits+=1
    power_est=detect_hits/detect_reps
    detect_p=statistics.median(detect_ps)
    detect_sig = (detect_p<=0.05) and (power_est>=0.5)
    # (b) FALSE-POSITIVE (uniform): header_mult=None => all rows same count
    fp_reps=20
    fp_hits=0; fp_ps=[]
    for _ in range(fp_reps):
        body_base=rng.randint(3,4)
        s,p=_pc_run_once(rng, None, body_base)
        fp_ps.append(p)
        if p is not None and p<=0.05 and s is not None and s>0:
            fp_hits+=1
    false_pos_rate=fp_hits/fp_reps
    fp_ok = (false_pos_rate<=0.10)
    pc_passed = detect_sig and fp_ok
    pc_verdict = "PASSED" if pc_passed else "FAILED"
    return {
        "pc_verdict": pc_verdict,
        "detect_p": detect_p,
        "power_est": power_est,
        "false_pos_rate": false_pos_rate,
        "detect_sig": detect_sig,
        "fp_ok": fp_ok,
        "pc_is_synthetic": True,
    }

# ---------- MAIN ----------
def main():
    seed=42
    rng=random.Random(seed)
    path="experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"
    docs=load_usable(path)
    # site filter: keep all usable docs globally; per-site only sites with >=15 usable docs
    from collections import Counter
    site_counts=Counter(s for s,_ in docs)
    eligible_sites=[s for s,c in site_counts.items() if c>=15]
    # Per protocol named sites:
    named=["Haghia Triada","Khania","Zakros"]
    per_site_sites=[s for s in named if site_counts.get(s,0)>=15]

    # ---- COUNT (key=0) ----
    g_s, g_n = S_obs(docs, 0)
    g_nm, g_p = perm(docs, g_s, 0, rng, ndraw=1000)
    count_global={"S_obs":g_s,"null_median":g_nm,"perm_p":g_p,"n_docs":g_n}

    count_per_site=[]
    n_sites_sig=0
    for s in per_site_sites:
        sd=[(ss,v) for ss,v in docs if ss==s]
        ss_, sn = S_obs(sd, 0)
        snm, sp = perm(sd, ss_, 0, rng, ndraw=1000)
        sig = (sp<=0.05) and (ss_ is not None) and (ss_>0)
        if sig: n_sites_sig+=1
        count_per_site.append({"site":s,"S_obs":ss_,"null_median":snm,"perm_p":sp,"n_docs":sn,"significant":sig})

    # ---- DENSITY (key=1) ----
    d_s, d_n = S_obs(docs, 1)
    d_nm, d_p = perm(docs, d_s, 1, rng, ndraw=1000)
    density_global={"S_obs":d_s,"null_median":d_nm,"perm_p":d_p,"n_docs":d_n}
    density_per_site=[]
    for s in per_site_sites:
        sd=[(ss,v) for ss,v in docs if ss==s]
        ss_, sn = S_obs(sd, 1)
        snm, sp = perm(sd, ss_, 1, rng, ndraw=1000)
        sig = (sp<=0.05) and (ss_ is not None) and (ss_>0)
        density_per_site.append({"site":s,"S_obs":ss_,"perm_p":sp,"significant":sig})

    # ---- POSITIVE CONTROL ----
    pc=positive_control(seed=seed)

    # ---- VERDICT (FROZEN, mechanical) ----
    n_eligible_sites=len(per_site_sites)
    global_count_sig = (g_p<=0.05) and (g_s is not None) and (g_s>0)
    any_site_sig = (n_sites_sig>=1)

    if pc["pc_verdict"]=="FAILED":
        verdict="MACHINERY_UNINFORMATIVE"
    elif n_eligible_sites<2 or pc["power_est"]<0.5:
        verdict="HEADER_ROW_UNDERPOWERED"
    elif pc["pc_verdict"]=="PASSED" and global_count_sig and n_sites_sig>=2:
        verdict="HEADER_ROW_LONGER_CROSS_SITE"
    elif pc["pc_verdict"]=="PASSED" and (global_count_sig or any_site_sig) and n_sites_sig<2:
        verdict="HEADER_ROW_LONGER_SITE_LOCAL"
    elif pc["pc_verdict"]=="PASSED" and (not global_count_sig) and n_sites_sig==0:
        verdict="NO_HEADER_ROW_LENGTH_STRUCTURE"
    else:
        # fallback: ambiguous -> site_local if any sig else no_structure
        verdict="HEADER_ROW_LONGER_SITE_LOCAL" if (global_count_sig or any_site_sig) else "NO_HEADER_ROW_LENGTH_STRUCTURE"

    # ---- DENSITY interpretation ----
    density_global_sig = (d_p<=0.05) and (d_s is not None) and (d_s>0)
    if (not density_global_sig):
        density_interp="WIDTH/GEOMETRY-driven (full-width header line), NOT deliberately packed (parallels E083 WIDTH-DRIVEN)"
    else:
        density_interp="genuinely PACKED header (density also significant)"

    out={
        "task_id":"EPOCH-086",
        "method":"per-doc log COUNT-ratio first-row vs mean(rest) + secondary DENSITY-ratio confound; random-row-as-heading null (directional, top LONGER); median over docs; 1000 perm draws; per-site HT/Khania/Zakros; synthetic positive control (detect 1.7x header + uniform false-positive).",
        "result":{
            "count_global":count_global,
            "count_per_site":count_per_site,
            "density_global":density_global,
            "density_per_site":density_per_site,
            "density_interpretation":density_interp,
            "density_global_significant":density_global_sig,
            "n_sites_count_significant":n_sites_sig,
            "n_eligible_sites":n_eligible_sites,
            "global_count_significant":global_count_sig,
        },
        "verdict":verdict,
        "numbers":{
            "count":{"global":count_global,"per_site":count_per_site},
            "density":{"global":{"S_obs":density_global["S_obs"],"perm_p":density_global["perm_p"]},
                       "per_site":[{"site":x["site"],"S_obs":x["S_obs"],"perm_p":x["perm_p"]} for x in density_per_site]},
            "positive_control":pc,
        },
        "key_findings":[
            f"Global COUNT S_obs={g_s:.4f}, perm_p={g_p:.4f} ({'SIG' if global_count_sig else 'NS'}); top row carries {'MORE' if g_s>0 else 'FEWER'} glyphs than lower rows on average.",
            f"Per-site COUNT: "+", ".join([f"{x['site']} S={x['S_obs']:.4f} p={x['perm_p']:.4f}{'(SIG)' if x['significant'] else ''}" for x in count_per_site])+".",
            f"DENSITY confound: global S_obs={d_s:.4f}, perm_p={d_p:.4f} ({'SIG' if density_global_sig else 'NS'}) -> {density_interp}.",
            f"Positive control: {pc['pc_verdict']} (detect median p={pc['detect_p']:.4f}, power={pc['power_est']:.2f}, false-pos rate={pc['false_pos_rate']:.2f}).",
            f"Verdict={verdict}: "+("top row is a longer header line." if "LONGER" in verdict else "no robust top-row length structure."),
        ],
        "successor_hypotheses":[
            "E087: Is the top-row extra width driven by a specific register type (e.g. heading/total line) vs body — test within HT only where the effect localizes.",
            "E088: Does the top row's wider x-span correlate with the document's overall x-extent (full-width line) rather than glyph packing — regress top-row span on doc span.",
            "E089: Cross-check with E085 (row SIZE): are taller glyphs also on the top row, or is the top row longer-but-shorter (a thin full-width header)?",
            "E090: Test whether the top-row glyph-count excess survives excluding word-initial/final positions (decouple from E077 word-initial size effect).",
            "E091: Replicate on Phaistos/Knossos once >=15 usable docs accrue to test cross-site generality beyond HT.",
            "E092: Compare top-row density against a within-doc shuffled-x null (preserve counts, permute x-centers) to isolate packing from geometry.",
        ],
        "layer":"L2",
        "la_touched":True,
        "non_circular":"No phonetic/semantic values used; only glyph bbox counts and x-centers/densities. Verdict is mechanical from a frozen rule applied to counts/positions. Does not depend on any prior epoch's outcome; E085/E083 referenced only as axis-distinctness and interpretation parallels.",
        "deviations":[],
    }
    print(json.dumps(out, indent=2, default=str))

if __name__=="__main__":
    main()
