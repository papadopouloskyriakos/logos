import json, statistics, random, math

def doc_scores(gl):    # returns (justif, h_size, h_len) or None
    pts=[{"left":g["bbox"][0], "right":g["bbox"][0]+g["bbox"][2], "h":g["bbox"][3],
          "yc":g["bbox"][1]+g["bbox"][3]/2.0, "area":g["bbox"][2]*g["bbox"][3]} for g in gl]
    medh=statistics.median([p["h"] for p in pts]) or 1.0
    ys=sorted(pts,key=lambda p:p["yc"]); rows=[]; cur=[ys[0]]
    for p in ys[1:]:
        if abs(p["yc"]-cur[-1]["yc"])<=0.6*medh: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur)
    if len(rows)<2: return None
    lefts=[min(p["left"] for p in r) for r in rows]; rights=[max(p["right"] for p in r) for r in rows]
    lsd=statistics.pstdev(lefts) if len(lefts)>1 else 0.0
    rsd=statistics.pstdev(rights) if len(rights)>1 else 0.0
    justif=(rsd-lsd)/((rsd+lsd)/2.0+1.0)                       # + = left-justified (right edge more ragged)
    first=[p["area"] for p in rows[0]]; rest=[p["area"] for r in rows[1:] for p in r]
    if len(first)<2 or len(rest)<3: return None
    h_size=math.log(statistics.median(first)/statistics.median(rest))
    h_len=math.log(len(rows[0])/(sum(len(r) for r in rows[1:])/(len(rows)-1)))
    return (justif, h_size, h_len)

def rankavg(x):                                                # average ranks (tie-aware) for Spearman
    order=sorted(range(len(x)), key=lambda i:x[i]); ranks=[0.0]*len(x); i=0
    while i<len(x):
        j=i
        while j+1<len(x) and x[order[j+1]]==x[order[i]]: j+=1
        r=(i+j)/2.0+1.0
        for k in range(i,j+1): ranks[order[k]]=r
        i=j+1
    return ranks

def spearman(x,y):
    n=len(x); rx=rankavg(x); ry=rankavg(y)
    mx=sum(rx)/n; my=sum(ry)/n
    num=sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    den=math.sqrt(sum((rx[i]-mx)**2 for i in range(n))*sum((ry[i]-my)**2 for i in range(n))) or 1.0
    return num/den

def coherence(cols):                                           # cols = [justif[], h_size[], h_len[]]; mean |pairwise r|
    rs=[abs(spearman(cols[a],cols[b])) for a in range(3) for b in range(a+1,3)]
    return sum(rs)/len(rs)

def indep_null(cols, C_obs, rng, ndraw=1000):                  # permute each column independently
    ge=0
    for _ in range(ndraw):
        perm=[c[:] for c in cols]
        for c in perm: rng.shuffle(c)
        if coherence(perm)>=C_obs: ge+=1
    return (ge+1)/(ndraw+1)

def residualize(y, x):                                          # residuals of y on x (simple OLS), for size-control
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    b=sum((x[i]-mx)*(y[i]-my) for i in range(n))/(sum((x[i]-mx)**2 for i in range(n)) or 1.0)
    a=my-b*mx
    return [y[i]-(a+b*x[i]) for i in range(n)]

# ===================== ASSEMBLY (main) =====================

DATA = "experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"
SEED = 870087

def load_ht_docs():
    raw = json.load(open(DATA))
    docs = []
    for idx, d in enumerate(raw):
        if d.get("site") != "Haghia Triada":
            continue
        gl = [g for g in d.get("glyphs", []) if (not g.get("is_divider", False)) and "bbox" in g]
        if len(gl) < 6:
            continue
        sc = doc_scores(gl)
        if sc is None:
            continue
        # additional prereq: >=2 rows AND first row >=2 glyphs AND rest >=3 glyphs (enforced inside doc_scores
        # via the len(first)<2 / len(rest)<3 guard, plus len(rows)<2 guard). n_glyphs for size control:
        docs.append({"id": "HT%03d" % idx, "n_glyphs": len(gl), "scores": sc})
    return docs

def signed_pairwise(cols):
    return {
        "justif_hsize": spearman(cols[0], cols[1]),
        "justif_hlen":  spearman(cols[0], cols[2]),
        "hsize_hlen":   spearman(cols[1], cols[2]),
    }

# ---- Positive control (synthetic) ----
def synth_coherent(n, rng):
    cols = [[], [], []]
    for _ in range(n):
        f = rng.gauss(0, 1)
        cols[0].append(f + rng.gauss(0, 1))
        cols[1].append(f + rng.gauss(0, 1))
        cols[2].append(f + rng.gauss(0, 1))
    return cols

def synth_independent(n, rng):
    cols = [[], [], []]
    for _ in range(n):
        cols[0].append(rng.gauss(0, 1))
        cols[1].append(rng.gauss(0, 1))
        cols[2].append(rng.gauss(0, 1))
    return cols

def pc_one(cols, rng, ndraw=1000):
    C = coherence(cols)
    p = indep_null(cols, C, rng, ndraw=ndraw)
    return C, p

def positive_control(n_target, rng, n_reps=15, ndraw=1000):
    detect_ps = []
    for _ in range(n_reps):
        cols = synth_coherent(n_target, rng)
        _, p = pc_one(cols, rng, ndraw=ndraw)
        detect_ps.append(p)
    power_est = sum(1 for p in detect_ps if p <= 0.05) / n_reps
    detect_p = statistics.median(detect_ps)

    fp_ps = []
    for _ in range(n_reps):
        cols = synth_independent(n_target, rng)
        _, p = pc_one(cols, rng, ndraw=ndraw)
        fp_ps.append(p)
    false_pos_rate = sum(1 for p in fp_ps if p <= 0.05) / n_reps

    passed = (power_est >= 0.5) and (false_pos_rate <= 0.10)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": detect_p,
        "power_est": power_est,
        "false_pos_rate": false_pos_rate,
        "pc_is_synthetic": True,
    }

def main():
    rng = random.Random(SEED)
    docs = load_ht_docs()
    n_docs = len(docs)
    cols = [
        [d["scores"][0] for d in docs],
        [d["scores"][1] for d in docs],
        [d["scores"][2] for d in docs],
    ]
    logn = [math.log(d["n_glyphs"]) for d in docs]

    C_obs = coherence(cols)
    perm_p = indep_null(cols, C_obs, rng, ndraw=1000)
    pw = signed_pairwise(cols)

    # size-controlled
    cols_sc = [residualize(cols[i], logn) for i in range(3)]
    C_sc = coherence(cols_sc)
    perm_p_sc = indep_null(cols_sc, C_sc, rng, ndraw=1000)

    # positive control
    pc = positive_control(n_target=max(n_docs, 128), rng=rng, n_reps=15, ndraw=1000)

    # verdict
    if n_docs < 60 or pc["power_est"] < 0.5:
        verdict = "REGISTER_COHERENCE_UNDERPOWERED"
    elif pc["pc_verdict"] != "PASSED":
        verdict = "MACHINERY_UNINFORMATIVE"
    elif perm_p <= 0.05:
        verdict = "LAYOUT_REGISTERS_DEPENDENT_HT"
    else:
        verdict = "LAYOUT_REGISTERS_INDEPENDENT_HT"

    out = {
        "task_id": "EPOCH-087",
        "method": "Per-doc HT register scores (justif, h_size, h_len); coherence C = mean|pairwise Spearman|; "
                  "independence null = permute each column independently (1000 draws, tie-aware); "
                  "size-controlled via OLS residualization on log(n_glyphs); synthetic positive control "
                  "(coherent-template DETECT arm + independent FALSE-POSITIVE arm, 15 reps each).",
        "result": {
            "C_obs": C_obs,
            "perm_p": perm_p,
            "n_docs": n_docs,
            "pairwise_signed": pw,
            "size_controlled": {"C_obs": C_sc, "perm_p": perm_p_sc},
            "positive_control": pc,
            "verdict": verdict,
        },
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
