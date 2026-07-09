import json, statistics, random, math

# === GIVEN FUNCTIONS (pasted verbatim) ===
def rows_of(gl):    # top->bottom rows; y-band tol 0.6*median glyph height
    pts=[{"h":g["bbox"][3], "yc":g["bbox"][1]+g["bbox"][3]/2.0, "area":g["bbox"][2]*g["bbox"][3]} for g in gl]
    medh=statistics.median([p["h"] for p in pts]) or 1.0
    ys=sorted(pts,key=lambda p:p["yc"]); rows=[]; cur=[ys[0]]
    for p in ys[1:]:
        if abs(p["yc"]-cur[-1]["yc"])<=0.6*medh: cur.append(p)
        else: rows.append(cur); cur=[p]
    rows.append(cur); return rows

def cv(v):
    if len(v)<2: return None
    m=statistics.mean(v); return statistics.pstdev(v)/m if m else None

def load_HT(path):    # returns list of (total_first_ink, first_count, first_med_area) per HT doc with >=2 rows
    docs=json.load(open(path)); out=[]
    for d in docs:
        if d.get("site")!="Haghia Triada": continue
        gl=[g for g in d["glyphs"] if g.get("bbox") and len(g["bbox"])==4 and not g.get("is_divider")]
        if len(gl)<6: continue
        rows=rows_of(gl)
        if len(rows)<2: continue
        r0=rows[0]; areas=[p["area"] for p in r0]
        out.append((sum(areas), len(r0), statistics.median(areas)))
    return out

def obs_cv(ht):
    return cv([t[0] for t in ht])

def null_cv(ht, rng):    # break the tradeoff: independent random median-area * random count
    meds=[t[2] for t in ht]; counts=[t[1] for t in ht]
    tot=[rng.choice(meds)*rng.choice(counts) for _ in range(len(ht))]
    return cv(tot)

def perm(ht, rng, ndraw=2000):    # BUDGET = obs CV BELOW null; perm_p = frac null CV <= obs CV
    o=obs_cv(ht); nl=[null_cv(ht,rng) for _ in range(ndraw)]
    nm=statistics.median(nl); le=sum(1 for x in nl if x<=o)
    return o, nm, (le+1)/(ndraw+1)
# === END GIVEN FUNCTIONS ===

DATA = "experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json"

# ---- Positive control: synthetic doc builders ----
def synth_detect_docs(rng, n=140):
    """Fixed total header ink C0 (small noise); count random; med_area = C0/count.
    Returns list of (total_first_ink, first_count, first_med_area) like load_HT."""
    C0 = 50000.0
    out = []
    for _ in range(n):
        c = rng.randint(2, 12)
        total = C0 * (1.0 + rng.gauss(0, 0.03))   # small noise around fixed budget
        med = total / c
        out.append((total, c, med))
    return out

def synth_fp_docs(rng, n=140):
    """Independent random median-area and count (no budget)."""
    out = []
    for _ in range(n):
        c = rng.randint(2, 12)
        med = rng.uniform(2000, 8000)              # independent of count
        out.append((med * c, c, med))
    return out

def positive_control(seed=10101):
    rng = random.Random(seed)
    reps = 15
    # DETECT arm
    detect_ps = []
    for _ in range(reps):
        ht = synth_detect_docs(rng, 140)
        o, nm, p = perm(ht, rng, 2000)
        detect_ps.append(p)
    detect_p = statistics.median(detect_ps)
    power_est = sum(1 for p in detect_ps if p <= 0.05) / reps
    # FALSE-POSITIVE arm
    fp_ps = []
    for _ in range(reps):
        ht = synth_fp_docs(rng, 140)
        o, nm, p = perm(ht, rng, 2000)
        fp_ps.append(p)
    false_pos_rate = sum(1 for p in fp_ps if p <= 0.05) / reps
    passed = (power_est >= 0.5) and (false_pos_rate <= 0.10)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": detect_p,
        "power_est": power_est,
        "false_pos_rate": false_pos_rate,
        "pc_is_synthetic": True,
    }

def main():
    rng = random.Random(20240888)
    ht = load_HT(DATA)
    n_docs = len(ht)
    o, nm, p = perm(ht, rng, 2000)
    ratio = o / nm if nm else None
    pc = positive_control(10101)

    # Frozen verdict
    if pc["pc_verdict"] != "PASSED":
        verdict = "MACHINERY_UNINFORMATIVE"
    elif n_docs < 60 or pc["power_est"] < 0.5:
        verdict = "HEADER_INK_BUDGET_UNDERPOWERED"
    elif p <= 0.05:
        verdict = "HEADER_INK_BUDGET_CONSTRAINED"
    else:
        verdict = "HEADER_INK_NOT_BUDGETED"

    out = {
        "task_id": "EPOCH-088",
        "method": "CV of first-row total ink (sum of glyph areas) across HT docs vs independence null (random median-area * random count, 2000 draws). Budget = obs CV significantly BELOW null. Positive control: synthetic fixed-budget docs (detect) + independent size*count docs (false-positive).",
        "result": {
            "obs_cv": o,
            "null_median": nm,
            "perm_p": p,
            "ratio": ratio,
            "n_docs": n_docs,
        },
        "verdict": verdict,
        "numbers": {
            "budget": {
                "obs_cv": o,
                "null_median": nm,
                "perm_p": p,
                "ratio": ratio,
                "n_docs": n_docs,
            },
            "positive_control": pc,
        },
        "key_findings": [],
        "successor_hypotheses": [],
        "layer": "L2",
        "la_touched": True,
        "non_circular": "This epoch tests a spatial mechanism on raw bbox geometry (areas, counts) only; it does not consume E087's correlation as evidence and uses opaque doc IDs with no sign values.",
        "deviations": [],
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
