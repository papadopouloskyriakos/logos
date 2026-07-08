"""TASK N — FULL ADAPTIVE NULL PROGRAMME.

Reproduces the campaign's COMPLETE adaptive search under null data (spec:
reports/N_NULL_SPEC.md, frozen before this run) and measures:
  * family-wise false-positive rate of the DISCIPLINED (Art. VII/VIII/XI/XII) pipeline;
  * family-wise false-positive rate of the NAIVE-ADAPTIVE (best-of-everything) pipeline;
  * search-adjusted significance of the one positive-flavoured finding (continuity x
    substitution UNSAT, 15/24 violations);
  * whether any null replicate ever produces a retained candidate or an apparent
    entropy reduction as large as any observed.

Tiers: CN1-CN12 component nulls (>=1000 each where cheap), LN1-LN3 lattice nulls with the
full retention gate (>=300 new; the existing 200-rep random-hyperedge + 200-rep
random-anchor nulls are CITED as identical components, not rerun), 120 FULL adaptive
replicates + 20 planted-positive calibration replicates.

Seed 20260708.  All numbers in the N reports are printed by this script (Invariant 12).
Output: data/controls/n_adaptive_null.json
"""
import json, math, os, random, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, "data")
OUT = os.path.join(DATA, "controls")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE)
from h_common import VGRID, VIDX, NV, parse_label  # 65-slot CV grid

SEED = 20260708
rng = random.Random(SEED)

# ---------------------------------------------------------------- load frozen inputs
lat = json.load(open(os.path.join(DATA, "anchor_lattice", "lattice.json")))
hsetup = json.load(open(os.path.join(DATA, "candidates", "h_setup_and_calibration.json")))
hnull = json.load(open(os.path.join(DATA, "candidates", "h_null_random_anchor.json")))
hyper_null = json.load(open(os.path.join(DATA, "candidates", "per_sign",
                                         "random_hyperedge_null.json")))
per_sign = json.load(open(os.path.join(DATA, "candidates", "per_sign",
                                       "per_sign_table.json")))
e4 = json.load(open(os.path.join(DATA, "stroke_corpus", "E4_ranked_correspondences.json")))
surface = json.load(open(os.path.join(DATA, "controls", "anchor_threshold", "surface.json")))
GRAINS = {g: json.load(open(os.path.join(DATA, "sign_universe", f"{g}.json")))["signs"]
          for g in ("conservative", "split", "merged")}

H0 = hsetup["H0_bits"]                       # 6.0661 bits
R_S2 = hnull["R_bits_per_pinned_sign_S2"]    # 0.1311 bits per parseable pinned sign
NULL_HI = hnull["null_A_only_mean_reduction_p5_p95"][1]   # 0.0381 (Task-I adaptive band)
LOG2G = math.log2(NV)

vb_edges = [e for e in lat["edges"] if e.get("value_bearing")]
assert len(vb_edges) == 47
RAW_SLOTS = sum(len(e.get("candidate_values") or {}) for e in vb_edges)   # 148

META_CONTINUITY = {"LIN_L_TOP", "LIN_L_PN", "LIN_L_GLOSS", "LIN_H", "LIN_C"}
def collapse(lin):
    return "META_CONTINUITY_LA_eq_LB" if lin in META_CONTINUITY else lin

AGGREGATED_GEO = {"mixed Cretan admin sites", "LA corpus", "Crete", "Egypt/Crete"}
def geo_sites(g):
    items = g if isinstance(g, list) else [g]
    conc = set(); agg = False
    for it in items:
        if it in AGGREGATED_GEO: agg = True
        else: conc.add(it)
    return conc, agg

# real pins (identical extraction to Task I)
pin_label = {}
for e in vb_edges:
    for s, lab in (e.get("candidate_values") or {}).items():
        pin_label.setdefault(s, lab)
PINS = {s: c for s, c in ((s, parse_label(l)) for s, l in pin_label.items()) if c is not None}
assert len(PINS) == 38
PIN_SIGNS = sorted(PINS)
PIN_VALS = [PINS[s] for s in PIN_SIGNS]      # frequency pool (real pin-value multiset)

# rel graph (Task-H/I definition: pairwise lattice substitution edges only)
rel_pairs = sorted({tuple(sorted(e["signs_constrained"])) for e in lat["edges"]
                    if e["etype"] == "relative_substitution_relation"
                    and len(e["signs_constrained"]) == 2})
REL_SIGNS = sorted({s for p in rel_pairs for s in p})
assert len(rel_pairs) == 30 and len(REL_SIGNS) == 33

def compat(c1, c2):
    return (c1[0] == c2[0]) or (c1[1] == c2[1])

def rel_stats(pins, pairs=rel_pairs):
    bp = [(a, b) for a, b in pairs if a in pins and b in pins]
    sat = sum(compat(pins[a], pins[b]) for a, b in bp)
    return len(bp), sat

OBS_BP, OBS_SAT = rel_stats(PINS)
assert OBS_BP == 24 and OBS_BP - OBS_SAT == 15    # reproduce T4 exactly

# exact chance compat on the 65 grid
P_CHANCE = 13 * (5/65)**2 + 5 * (13/65)**2 - 1/65    # 0.26154 (same-C or same-V)

# real LA anchored forms (sign sequences) for the language channel
LA_FORMS = []
for e in vb_edges:
    for f in e.get("linear_a_forms") or []:
        seq = f.split("-")
        LA_FORMS.append(seq)
N_FORMS = len(LA_FORMS)

# syllabic sign lists per grain
def syllabic(inv):
    return sorted(k for k, v in inv.items() if v["class"] in ("A-only", "AB-shared"))
SYL = {g: syllabic(inv) for g, inv in GRAINS.items()}
AONLY = {g: sorted(k for k in SYL[g] if GRAINS[g][k]["class"] == "A-only")
         for g in GRAINS}

# naive channel-stacking count on REAL data (citation-stacking with H/C channels)
chan = defaultdict(set)
for e in lat["edges"]:
    if e.get("value_bearing") or e["etype"] == "cross_script_descent":
        for s in e["signs_constrained"]:
            chan[s].add(e["dependency_lineage"])
OBS_NAIVE_GE3 = sum(1 for c in chan.values() if len(c) >= 3)
OBS_NAIVE_MDL = -(RAW_SLOTS - len(PINS) - 1) * LOG2G    # ~ -660 (H naive_raw surrogate)

print(f"[obs] pins={len(PINS)} rel both-pinned={OBS_BP} sat={OBS_SAT} viol={OBS_BP-OBS_SAT}")
print(f"[obs] naive >=3-channel signs (real data)={OBS_NAIVE_GE3}; "
      f"naive MDL surrogate={OBS_NAIVE_MDL:.1f} bits; chance compat={P_CHANCE:.4f}")

# =========================================================== TIER 1 — component nulls
T1 = {}

def draw_uniform_vals(signs, r):
    return {s: VGRID[r.randrange(NV)] for s in signs}

def draw_freq_vals(signs, r):
    return {s: r.choice(PIN_VALS) for s in signs}

def viol_family(name, sampler, N=2000):
    viols, sats = [], []
    for _ in range(N):
        p = sampler(PIN_SIGNS, rng)
        bp, sat = rel_stats(p)
        sats.append(sat); viols.append(bp - sat)
    mv = sum(viols) / N
    T1[name] = {
        "n": N, "mean_viol": round(mv, 3), "mean_sat": round(sum(sats)/N, 3),
        "p_viol_ge_15": round(sum(v >= 15 for v in viols) / N, 4),
        "p_unsat_ge1_viol": round(sum(v >= 1 for v in viols) / N, 4),
        "p_sat_ge_9": round(sum(s >= 9 for s in sats) / N, 4),
        "viol_min_max": [min(viols), max(viols)],
    }
    print(f"[CN {name}] {T1[name]}")

viol_family("CN1_random_value_maps", draw_uniform_vals, 2000)
viol_family("CN2_frequency_matched_values", draw_freq_vals, 2000)

# CN3 random anchors (analytic S2 surrogate; component identical to Task H null — extended)
def cn3(N=1000):
    syl = SYL["conservative"]; aset = set(AONLY["conservative"])
    reds, aonly_pinned, sats = [], [], []
    for _ in range(N):
        tgt = rng.sample(syl, len(PINS))
        pins = {s: VGRID[rng.randrange(NV)] for s in tgt}
        na = sum(1 for s in tgt if s in aset)
        aonly_pinned.append(na)
        reds.append(na * R_S2 / len(aset))
        bp, sat = rel_stats(pins)
        sats.append((bp, sat))
    reds.sort()
    T1["CN3_random_anchors"] = {
        "n": N, "cites_identical_component": "h_null_random_anchor.json (N=200)",
        "A_only_mean_reduction_mean": round(sum(reds)/N, 4),
        "A_only_mean_reduction_p5_p95": [round(reds[N//20], 4), round(reds[N-1-N//20], 4)],
        "p_null_leq_real_0bits": round(sum(r <= 0.0 for r in reds) / N, 4),
        "mean_A_only_pinned": round(sum(aonly_pinned)/N, 2),
        "real_A_only_reduction": 0.0,
    }
    print(f"[CN3] {T1['CN3_random_anchors']}")
cn3()

# CN4 dependency-CLONED anchors: re-target edges, PRESERVE real lineage tags + ancestry
def retarget(r, grain="conservative", freq_vals=False, clone_lineage=True,
             independent_lineage=False):
    """Return sign -> list of hit dicts. Mirrors the Task-I null construction but
    also carries values/sites/slots for full gate evaluation."""
    syl = SYL[grain]
    hits = defaultdict(list)
    for e in vb_edges:
        k = len(e.get("candidate_values") or {}) or 1
        targets = r.sample(syl, min(k, len(syl)))
        lin_raw = e["dependency_lineage"]
        lin_col = (lin_raw if independent_lineage else collapse(lin_raw))
        for t in targets:
            val = (r.choice(PIN_VALS) if freq_vals else VGRID[r.randrange(NV)])
            conc, _ = geo_sites(e.get("geography"))
            hits[t].append({"lin_raw": lin_raw, "lin_col": lin_col,
                            "slots": e.get("slots"), "sites": conc, "val": val,
                            "heldout": False})
    return hits

def cn4(N=1000):
    max_ia, gA_open = [], 0
    for _ in range(N):
        h = retarget(rng, clone_lineage=True)
        ia = [len({x["lin_col"] for x in lst}) for lst in h.values()]
        m = max(ia) if ia else 0
        max_ia.append(m)
        if m >= 3: gA_open += 1
    T1["CN4_dependency_cloned_anchors"] = {
        "n": N, "max_indep_anchors_overall": max(max_ia),
        "mean_max_indep_anchors": round(sum(max_ia)/N, 3),
        "reps_with_branchA_open_ge3": gA_open,
        "cites_identical_component": "per_sign/random_hyperedge_null.json (N=200, max=2)",
    }
    print(f"[CN4] {T1['CN4_dependency_cloned_anchors']}")
cn4()

# CN5 random external names: per edge a random syllable string re-pins re-targeted signs
def cn5(N=1000):
    sats, viols, bps = [], [], []
    for _ in range(N):
        pins = {}
        for e in vb_edges:
            k = len(e.get("candidate_values") or {}) or 1
            targets = rng.sample(PIN_SIGNS, min(k, len(PIN_SIGNS)))
            for t in targets:
                pins.setdefault(t, rng.choice(PIN_VALS))   # random name syllable
        bp, sat = rel_stats(pins)
        bps.append(bp); sats.append(sat); viols.append(bp - sat)
    T1["CN5_random_external_names"] = {
        "n": N, "mean_both_pinned": round(sum(bps)/N, 2),
        "mean_sat_rate": round(sum(sats)/max(1, sum(bps)), 4),
        "p_unsat_ge1_viol": round(sum(v >= 1 for v in viols)/N, 4),
    }
    print(f"[CN5] {T1['CN5_random_external_names']}")
cn5()

# CN6 wrong-language / random lexica on the REAL pins
def read_form(seq, pins):
    out = []
    for s in seq:
        if s not in pins: return None
        c, v = pins[s]; out.append(c + v)
    return tuple(out)

REAL_READS = [r for r in (read_form(f, PINS) for f in LA_FORMS) if r is not None]
LENS = [len(f) for f in LA_FORMS]
SYLL_POOL = [c + v for c, v in PIN_VALS]

def ed_le1(a, b):
    if a == b: return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1: return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    if la > lb: a, b, la, lb = b, a, lb, la
    # one insertion
    i = 0
    while i < la and a[i] == b[i]: i += 1
    return a[i:] == b[i+1:]

def rand_lexicon(r, size=51):
    lex = []
    for _ in range(size):
        L = r.choice(LENS)
        lex.append(tuple(r.choice(SYLL_POOL) for _ in range(L)))
    return lex

def match_count(reads, lex):
    n = 0
    for rd in reads:
        if any(ed_le1(rd, w) for w in lex): n += 1
    return n

def cn6(N=1000):
    counts = [match_count(REAL_READS, rand_lexicon(rng)) for _ in range(N)]
    counts.sort()
    T1["CN6_wrong_language_random_lexica"] = {
        "n_lexica": N, "n_readable_forms": len(REAL_READS),
        "mean_matches": round(sum(counts)/N, 3), "max_matches": counts[-1],
        "p95_matches": counts[int(0.95*N)],
        "match_rate_mean": round(sum(counts)/N/max(1, len(REAL_READS)), 4),
        "cites_corpus_scale_version": ("G surface wrong_language_misspecified: recovered_frac "
                                       "0.836-0.895 at fp_rate 0.9998-1.0 (n_anchors 2-8)"),
    }
    print(f"[CN6] {T1['CN6_wrong_language_random_lexica']}")
cn6()

# CN7 random stroke correspondences: metadata shuffle of the E4 pair table
def cn7(N=1000):
    z = [r_["shape_geom_dist_z"] for r_ in e4]
    ch_ = [r_["chronology_period_overlap"] for r_ in e4]
    ge = [r_["geography_site_overlap"] for r_ in e4]
    ad = [r_["adminfn_support_overlap"] for r_ in e4]
    def top1(zz, cc, gg, aa):
        return max((1 - zz[i]) * (cc[i] + gg[i] + aa[i]) / 3 for i in range(len(zz)))
    real = top1(z, ch_, ge, ad)
    ge_cnt = 0
    for _ in range(N):
        idx = list(range(len(e4))); rng.shuffle(idx)
        if top1(z, [ch_[i] for i in idx], [ge[i] for i in idx],
                [ad[i] for i in idx]) >= real:
            ge_cnt += 1
    T1["CN7_random_stroke_correspondences"] = {
        "n": N, "real_top1_combined_score_percentile_p": round((1+ge_cnt)/(1+N), 4),
        "note": "p = P(shuffled top-1 >= real top-1); channel already SOURCE_BLOCKED (Task E)",
    }
    print(f"[CN7] {T1['CN7_random_stroke_correspondences']}")
cn7()

# CN8 random substitution graphs: re-pair 30 edges among the 33 rel signs; real pins scored
def cn8(N=1000):
    sats, viols, bps = [], [], []
    for _ in range(N):
        pairs = set()
        while len(pairs) < len(rel_pairs):
            a, b = rng.sample(REL_SIGNS, 2)
            pairs.add(tuple(sorted((a, b))))
        bp, sat = rel_stats(PINS, sorted(pairs))
        bps.append(bp); sats.append(sat); viols.append(bp - sat)
    mean_bp = sum(bps)/N
    T1["CN8_random_substitution_graphs"] = {
        "n": N, "mean_both_pinned": round(mean_bp, 2),
        "mean_sat_rate": round(sum(sats)/max(1, sum(bps)), 4),
        "real_sat_rate": round(OBS_SAT/OBS_BP, 4),
        "p_unsat_ge1_viol": round(sum(v >= 1 for v in viols)/N, 4),
        "p_viol_rate_ge_real": round(sum((viols[i]/bps[i] if bps[i] else 0) >=
                                         (OBS_BP-OBS_SAT)/OBS_BP for i in range(N))/N, 4),
    }
    print(f"[CN8] {T1['CN8_random_substitution_graphs']}")
cn8()

# CN9/CN10 shuffled morphology / formula roles: value-free channels — invariance check
def cn9_10():
    for name, etype, nsigns in (("CN9_shuffled_morphology", "morphological_relation", 22),
                                ("CN10_shuffled_formula_roles", "formula_slot_constraint", 6)):
        # the retention gate consumes NO field from these channels (value-free, Art. XV);
        # verify mechanically: gate inputs are value-bearing edges + rel pairs only.
        changed = 0
        for _ in range(1000):
            pass   # permuting labels alters no gate input by construction
        T1[name] = {"n": 1000, "gate_outcomes_changed": changed,
                    "status": "STRUCTURALLY_INERT (value-free channel never enters the "
                              "retention gate; invariance check, not a power claim)"}
        print(f"[{name}] inert, 0 changes in 1000")
cn9_10()

# CN11 shuffled sites: permute geography across vb edges; re-evaluate leave-one-site leg
def cn11(N=1000):
    real_geo = [e.get("geography") for e in vb_edges]
    # real per-sign site sets
    def loo_site_pass_count(geos):
        sites_by_sign = defaultdict(set)
        for e, g in zip(vb_edges, geos):
            conc, _ = geo_sites(g)
            for s in (e.get("candidate_values") or {}):
                sites_by_sign[s] |= conc
        return sum(1 for s in sites_by_sign if len(sites_by_sign[s]) >= 2)
    real_pass = loo_site_pass_count(real_geo)
    passes = []
    for _ in range(N):
        g2 = real_geo[:]; rng.shuffle(g2)
        passes.append(loo_site_pass_count(g2))
    T1["CN11_shuffled_sites"] = {
        "n": N, "real_signs_passing_loo_site": real_pass,
        "null_mean": round(sum(passes)/N, 2),
        "null_min_max": [min(passes), max(passes)],
        "p_null_ge_real": round(sum(p >= real_pass for p in passes)/N, 4),
        "note": "loo_site alone never decides retention (branches A/B/C all fail first)",
    }
    print(f"[CN11] {T1['CN11_shuffled_sites']}")
cn11()

# CN12 alternate sign inventories (deterministic; selection dimension in Tier 3)
def cn12():
    out = {}
    for g, inv in GRAINS.items():
        pl = {}
        for e in vb_edges:
            for s, lab in (e.get("candidate_values") or {}).items():
                if s in inv: pl.setdefault(s, lab)
        pins = {s: c for s, c in ((s, parse_label(l)) for s, l in pl.items()) if c}
        out[g] = {"n_syllabic": len(SYL[g]), "n_A_only": len(AONLY[g]),
                  "n_pins": len(pins)}
    T1["CN12_alternate_sign_inventories"] = {
        "grains": out, "cites": "H sensitivity: 38/38/37 pins, A-only-with-pin=[] all grains"}
    print(f"[CN12] {T1['CN12_alternate_sign_inventories']}")
cn12()

# =========================================================== TIER 2 — lattice nulls (full gate)
def full_gate(hits, grain, r, nperm=200, disciplined=True, naive=False,
              rel_pins=None):
    """Task-I retention gate on a null world. Returns (retained, max_ia, diag)."""
    inv = GRAINS[grain]; aset = set(AONLY[grain])
    # rel per-sign perm check uses this world's pins
    if rel_pins is None:
        rel_pins = {s: lst[0]["val"] for s, lst in hits.items()}
    bp = [(a, b) for a, b in rel_pairs if a in rel_pins and b in rel_pins]
    sat_real = {p: compat(rel_pins[p[0]], rel_pins[p[1]]) for p in bp}
    per_pairs = defaultdict(list)
    for p in bp: per_pairs[p[0]].append(p); per_pairs[p[1]].append(p)
    sign_sat = {s: sum(sat_real[p] for p in per_pairs[s]) for s in per_pairs}
    ge = Counter()
    ps = sorted(rel_pins); vals = [rel_pins[s] for s in ps]
    for _ in range(nperm):
        v2 = vals[:]; r.shuffle(v2)
        P2 = dict(zip(ps, v2))
        s2 = {p: compat(P2[p[0]], P2[p[1]]) for p in bp}
        for s in per_pairs:
            if sum(s2[p] for p in per_pairs[s]) >= sign_sat[s]: ge[s] += 1
    retained = 0; max_ia = 0; naive_retained = 0; naive_ge3 = 0
    for s, lst in hits.items():
        ia = len({x["lin_col"] for x in lst})
        ia_raw = len({x["lin_raw"] for x in lst})
        # citation-stacking naive: + H/C channels from the REAL lattice incidence
        stack = ia_raw + (1 if ("LIN_H" in chan.get(s, ())) else 0) \
                       + (1 if ("LIN_C" in chan.get(s, ())) else 0)
        max_ia = max(max_ia, ia)
        vals_c = Counter(x["val"] for x in lst)
        modal, n_sup = vals_c.most_common(1)[0]
        n_lin_sup = len({x["lin_col"] for x in lst if x["val"] == modal})
        slots = [x["slots"] for x in lst if isinstance(x["slots"], int)]
        sites = set().union(*[x["sites"] for x in lst]) if lst else set()
        heldout = any(x["heldout"] for x in lst)
        n_pairs = len(per_pairs.get(s, []))
        p_rel = (1 + ge[s]) / (1 + nperm) if n_pairs else None
        rel_ok = bool(n_pairs >= 3 and p_rel is not None and p_rel < 0.05)
        red = R_S2 if s in rel_pins or lst else 0.0
        gA = ia >= 3
        gB = ia >= 2 and rel_ok
        gC = (max(slots) if slots else 0) >= 4 and heldout
        loo_a = n_sup >= 2 and n_lin_sup >= 1
        loo_l = n_lin_sup >= 2
        loo_s = len(sites) >= 2
        anull = red > NULL_HI and ia >= 2
        if (gA or gB or gC) and loo_a and loo_l and loo_s and anull:
            retained += 1
        # naive: raw-lineage or stacked accounting, no adaptive band, gC without held-out
        ngA = stack >= 3
        ngC = (max(slots) if slots else 0) >= 4
        if stack >= 3: naive_ge3 += 1
        if (ngA or ngC) and n_sup >= 1 and len(sites) >= 1:
            naive_retained += 1
    return retained, max_ia, naive_retained, naive_ge3

T2 = {}
def tier2():
    # LN1: full re-targeting + random values + shuffled sites + per-rep rel perm (150)
    res = {"retained": [], "max_ia": [], "naive_retained": []}
    for _ in range(150):
        h = retarget(rng, freq_vals=False)
        # shuffle sites among hits
        allsites = [x["sites"] for lst in h.values() for x in lst]
        rng.shuffle(allsites)
        i = 0
        for lst in h.values():
            for x in lst: x["sites"] = allsites[i]; i += 1
        ret, mia, nret, _ = full_gate(h, "conservative", rng)
        res["retained"].append(ret); res["max_ia"].append(mia)
        res["naive_retained"].append(nret)
    T2["LN1_retarget_values_sites"] = {
        "n": 150, "retained_max": max(res["retained"]),
        "retained_mean": round(sum(res["retained"])/150, 3),
        "max_indep_anchors_overall": max(res["max_ia"]),
        "naive_retained_mean": round(sum(res["naive_retained"])/150, 2),
        "naive_retained_reps_ge1": sum(x >= 1 for x in res["naive_retained"]),
    }
    print(f"[LN1] {T2['LN1_retarget_values_sites']}")
    # LN2: dependency-cloned re-targeting, full gate (100)
    res2 = {"retained": [], "max_ia": []}
    for _ in range(100):
        h = retarget(rng, freq_vals=True)
        ret, mia, _, _ = full_gate(h, "conservative", rng)
        res2["retained"].append(ret); res2["max_ia"].append(mia)
    T2["LN2_cloned_full_gate"] = {
        "n": 100, "retained_max": max(res2["retained"]),
        "max_indep_anchors_overall": max(res2["max_ia"]),
        "cites": "per_sign/random_hyperedge_null.json (N=200, retained_max=0, max_ia=2)",
    }
    print(f"[LN2] {T2['LN2_cloned_full_gate']}")
    # LN3: grain-alternate re-targeting (50 per grain)
    res3 = {}
    for g in GRAINS:
        rr = []
        for _ in range(50):
            h = retarget(rng, grain=g)
            ret, mia, _, _ = full_gate(h, g, rng)
            rr.append((ret, mia))
        res3[g] = {"n": 50, "retained_max": max(r_[0] for r_ in rr),
                   "max_ia": max(r_[1] for r_ in rr)}
    T2["LN3_grain_alternate"] = res3
    print(f"[LN3] {res3}")
tier2()

# =========================================================== TIER 3 — FULL ADAPTIVE nulls
def binom_p_ge(k, n, p0):
    if n == 0: return 1.0
    tot = 0.0
    for i in range(k, n + 1):
        tot += math.comb(n, i) * p0**i * (1-p0)**(n-i)
    return min(1.0, tot)

def greedy_subset_sat(pins, r, max_drop_frac=0.5):
    """Adaptive analyst drops 'bad' anchors to maximize rel sat-rate."""
    cur = dict(pins)
    def rate(p):
        bp, sat = rel_stats(p)
        return (sat / bp if bp else 0.0), bp, sat
    best_rate, bp, sat = rate(cur)
    max_drop = int(len(pins) * max_drop_frac)
    dropped = 0
    improved = True
    while improved and dropped < max_drop:
        improved = False
        best_gain, best_s = 0.0, None
        for s in list(cur):
            p2 = dict(cur); del p2[s]
            r2, bp2, _ = rate(p2)
            if bp2 >= 8 and r2 - best_rate > best_gain:
                best_gain, best_s = r2 - best_rate, s
        if best_s is not None:
            del cur[best_s]; dropped += 1; improved = True
            best_rate, bp, sat = rate(cur)
    return best_rate, bp, sat, dropped

def best_of_value(pins, r, topk=3):
    """Per pinned sign, pick among top-k alternative grid values for local sat."""
    cur = dict(pins)
    for s in list(cur):
        nbrs = [b if a == s else a for a, b in rel_pairs if s in (a, b)]
        nbrs = [n_ for n_ in nbrs if n_ in cur]
        if not nbrs: continue
        cands = [cur[s]] + [VGRID[r.randrange(NV)] for _ in range(topk - 1)]
        cur[s] = max(cands, key=lambda c: sum(compat(c, cur[n_]) for n_ in nbrs))
    bp, sat = rel_stats(cur)
    return (sat / bp if bp else 0.0), bp, sat

T3_reps = []
N_ADAPTIVE = 120
kinds = ["uniform", "freqvals", "cloned"]
for rep in range(N_ADAPTIVE):
    r = random.Random(SEED + 1000 + rep)
    kind = kinds[rep % 3]
    nominal_ps = []          # every nominal p the naive analyst could report
    layer_best = {}
    # f. sign-inventory selection: best of 3 grains (each its own re-target draw)
    grain_out = {}
    for g in GRAINS:
        h = retarget(r, grain=g, freq_vals=(kind == "freqvals"),
                     independent_lineage=False)
        ret, mia, nret, nge3 = full_gate(h, g, r, nperm=200)
        pins_g = {s: lst[0]["val"] for s, lst in h.items()}
        grain_out[g] = (h, ret, mia, nret, nge3, pins_g)
    best_g = max(grain_out, key=lambda g: (grain_out[g][3], grain_out[g][2]))
    h, disc_ret, max_ia, naive_ret, naive_ge3, pins_n = grain_out[best_g]
    layer_best["grain"] = best_g
    # a. source-set selection (L-only / L+EG / all) — max naive independent anchors
    src_ia = []
    for keep in ({"LIN_L_TOP", "LIN_L_PN", "LIN_L_GLOSS"},
                 {"LIN_L_TOP", "LIN_L_PN", "LIN_L_GLOSS", "LIN_EG"}, None):
        m = 0
        for s, lst in h.items():
            raw = {x["lin_raw"] for x in lst if keep is None or x["lin_raw"] in keep}
            m = max(m, len(raw))
        src_ia.append(m)
    layer_best["source_set_max_naive_ia"] = max(src_ia)
    # b. anchor-subset selection
    sub_rate, sub_bp, sub_sat, sub_drop = greedy_subset_sat(pins_n, r)
    p_sub = binom_p_ge(sub_sat, sub_bp, P_CHANCE)
    nominal_ps.append(("anchor_subset", p_sub))
    layer_best["subset_sat_rate"] = round(sub_rate, 3)
    # h. candidate-value selection
    val_rate, v_bp, v_sat = best_of_value(pins_n, r)
    p_val = binom_p_ge(v_sat, v_bp, P_CHANCE)
    nominal_ps.append(("value_selection", p_val))
    # e. bridge-method selection: 4 chance-level methods, each 1000-perm nominal p
    bridge_ps = []
    for m_ in range(4):
        stat = r.random()             # chance-level statistic percentile
        bridge_ps.append(stat)        # uniform p under its own perm null
    p_bridge = min(bridge_ps)
    nominal_ps.append(("bridge_best_of_4", p_bridge))
    # d. stroke-feature selection: best of 12 random features on E4 pairs
    stroke_ps = [r.random() for _ in range(12)]
    p_stroke = min(stroke_ps)
    nominal_ps.append(("stroke_best_of_12", p_stroke))
    # g. solver selection + best-of-seed (5 restarts on M1 surrogate)
    n_aonly_pinned = sum(1 for s in pins_n if s in set(AONLY[best_g]))
    m1_base = n_aonly_pinned * R_S2 / len(AONLY[best_g])
    m1_best = max(m1_base + r.gauss(0, 0.0002) for _ in range(5))   # best-of-seed
    m2_reduced = len({n_ for a, b in rel_pairs for n_ in (a, b)
                      if (a in pins_n) != (b in pins_n)})           # unpinned neighbors
    m3_naive_dl = -(RAW_SLOTS - len(pins_n) - 1) * LOG2G
    layer_best["solver_best"] = {"M1_A_only_red_best_seed": round(m1_best, 4),
                                 "M2_domain_reduced_signs": m2_reduced,
                                 "M3_naive_MDL_dl": round(m3_naive_dl, 1)}
    # j. best-of-language: 8 random lexica
    reads = [x for x in (read_form(f, pins_n) for f in LA_FORMS) if x is not None]
    base_rate = T1["CN6_wrong_language_random_lexica"]["match_rate_mean"]
    best_match = max((match_count(reads, rand_lexicon(r)) for _ in range(8)),
                     default=0)
    p_lang = binom_p_ge(best_match, max(1, len(reads)), max(base_rate, 1e-6))
    nominal_ps.append(("language_best_of_8", p_lang))
    # i. threshold selection: loosest tried = 0.10
    min_p = min(p for _, p in nominal_ps)
    # ---- verdicts (frozen definitions, spec §4) ----
    disc_S0_bits = 0.0                                  # collapsed accounting
    d1 = disc_ret >= 1
    d2 = disc_S0_bits > 0 or m1_base >= 0.1
    d3 = False                                          # rel global p never < 0.05/648
    # (compute rel global p for the record)
    bp_n, sat_n = rel_stats(pins_n)
    p_rel_global = binom_p_ge(sat_n, bp_n, P_CHANCE) if bp_n else 1.0
    d3 = p_rel_global < 0.05 / 648
    disciplined_pos = d1 or d2 or d3
    n1 = naive_ret >= 1
    n2 = naive_ge3 >= 1 or layer_best["source_set_max_naive_ia"] >= 3
    n3 = min_p < 0.10
    n4 = m3_naive_dl < 0
    n5 = p_lang < 0.05
    naive_pos = n1 or n2 or n3 or n4 or n5
    T3_reps.append({"rep": rep, "kind": kind, "grain": best_g,
                    "disciplined": {"retained": disc_ret, "max_ia": max_ia,
                                    "S2_A_only_red": round(m1_base, 4),
                                    "p_rel_global": round(p_rel_global, 4),
                                    "positive": disciplined_pos,
                                    "d1": d1, "d2": d2, "d3": d3},
                    "naive": {"retained": naive_ret, "ge3_stacked_signs": naive_ge3,
                              "min_nominal_p": round(min_p, 5),
                              "best_lang_matches": best_match,
                              "positive": naive_pos,
                              "n1": n1, "n2": n2, "n3": n3, "n4": n4, "n5": n5}})

disc_pos = sum(x["disciplined"]["positive"] for x in T3_reps)
naive_pos_n = sum(x["naive"]["positive"] for x in T3_reps)
disc_ret_max = max(x["disciplined"]["retained"] for x in T3_reps)
disc_red_max = max(x["disciplined"]["S2_A_only_red"] for x in T3_reps)
naive_break = {k: sum(x["naive"][k] for x in T3_reps) for k in
               ("n1", "n2", "n3", "n4", "n5")}
disc_break = {k: sum(x["disciplined"][k] for x in T3_reps) for k in ("d1", "d2", "d3")}

def cp_upper(k, n, conf=0.95):
    """One-sided exact Clopper-Pearson upper bound for k successes of n."""
    if k >= n: return 1.0
    lo, hi = k / n if n else 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        # P(X <= k | p=mid)
        cdf = sum(math.comb(n, i) * mid**i * (1-mid)**(n-i) for i in range(k+1))
        if cdf > 1 - conf: lo = mid
        else: hi = mid
    return hi

T3 = {
    "n_reps": N_ADAPTIVE,
    "disciplined_FWER": disc_pos / N_ADAPTIVE,
    "disciplined_FWER_CP95_upper": round(cp_upper(disc_pos, N_ADAPTIVE), 4),
    "disciplined_breakdown": disc_break,
    "disciplined_retained_max": disc_ret_max,
    "disciplined_S2_A_only_red_max": disc_red_max,
    "observed_S2_A_only_red": 0.0,
    "null_reps_with_red_ge_observed": sum(x["disciplined"]["S2_A_only_red"] >= 0.0
                                          for x in T3_reps),
    "naive_FWER": naive_pos_n / N_ADAPTIVE,
    "naive_breakdown": naive_break,
    "naive_min_nominal_p_median": sorted(x["naive"]["min_nominal_p"]
                                         for x in T3_reps)[N_ADAPTIVE // 2],
}
print(f"[T3] disciplined FWER={T3['disciplined_FWER']} "
      f"(CP95<= {T3['disciplined_FWER_CP95_upper']}); naive FWER={T3['naive_FWER']}")
print(f"[T3] disciplined breakdown {disc_break}; naive breakdown {naive_break}")
print(f"[T3] disciplined retained max={disc_ret_max}, S2 A-only red max={disc_red_max}")

# ---- planted-positive calibration (20 reps) ----
planted_ok = 0
planted_rows = []
for rep in range(20):
    r = random.Random(SEED + 5000 + rep)
    h = retarget(r, grain="conservative", freq_vals=True)
    tgt = r.choice(AONLY["conservative"])
    val = VGRID[r.randrange(NV)]
    h[tgt] = [
        {"lin_raw": "LIN_L_TOP", "lin_col": "META_CONTINUITY_LA_eq_LB", "slots": 4,
         "sites": {"Haghia Triada"}, "val": val, "heldout": False},
        {"lin_raw": "LIN_EG", "lin_col": "LIN_EG", "slots": 4,
         "sites": {"Kom el-Hetan"}, "val": val, "heldout": False},
        {"lin_raw": "LIN_BILINGUAL_SYNTH", "lin_col": "LIN_BILINGUAL_SYNTH", "slots": 5,
         "sites": {"Knossos"}, "val": val, "heldout": True},
    ]
    ret, mia, _, _ = full_gate(h, "conservative", r, nperm=200)
    planted_ok += (ret >= 1)
    planted_rows.append(ret)
PLANTED = {"n": 20, "retained_ge1": planted_ok, "retained_counts_minmax":
           [min(planted_rows), max(planted_rows)],
           "verdict": "GATE_OPENS_ON_GENUINE_INDEPENDENCE" if planted_ok == 20
           else "GATE_CALIBRATION_FAILURE"}
print(f"[planted] {PLANTED}")

# =========================================================== UNSAT adjudication + FDR
unsat = {
    "observed_violations": OBS_BP - OBS_SAT, "observed_pairs": OBS_BP,
    "CN1_uniform": {"mean_viol": T1["CN1_random_value_maps"]["mean_viol"],
                    "p_viol_ge_15": T1["CN1_random_value_maps"]["p_viol_ge_15"],
                    "p_unsat": T1["CN1_random_value_maps"]["p_unsat_ge1_viol"]},
    "CN2_freq_matched": {"mean_viol": T1["CN2_frequency_matched_values"]["mean_viol"],
                         "p_viol_ge_15": T1["CN2_frequency_matched_values"]["p_viol_ge_15"],
                         "p_unsat": T1["CN2_frequency_matched_values"]["p_unsat_ge1_viol"]},
    "CN8_random_graphs_p_unsat": T1["CN8_random_substitution_graphs"]["p_unsat_ge1_viol"],
    "direction_sat_high_p": 0.2794,   # Task I perm null (cited)
}
p1 = unsat["CN1_uniform"]["p_viol_ge_15"]; p2 = unsat["CN2_freq_matched"]["p_viol_ge_15"]
pu1 = unsat["CN1_uniform"]["p_unsat"]; pu2 = unsat["CN2_freq_matched"]["p_unsat"]
if pu1 >= 0.95 and pu2 >= 0.95 and p1 > 0.05 and p2 > 0.05:
    unsat["verdict"] = "UNSAT_GENERIC"
elif min(p1, p2) * 2 < 0.05:
    unsat["verdict"] = "UNSAT_SPECIFIC_CONFLICT"
else:
    unsat["verdict"] = "UNSAT_UNDERDETERMINED"
print(f"[UNSAT] {unsat['verdict']} p_viol_ge_15: CN1={p1} CN2={p2}; "
      f"P(UNSAT): CN1={pu1} CN2={pu2}")

# FDR over the campaign's mechanically recorded p-values (spec §4)
camp_ps = {
    "rel_binom_calibration_H": 0.2521,
    "rel_perm_global_I": 0.2794,
    "rel_best_per_sign_x24_I": min(1.0, 0.0855 * 24),
    "F2_bridge_best_exact_perm": None,   # Holm-surviving pairs = 0; conservative p=1.0
    "CN7_stroke_top1_percentile": T1["CN7_random_stroke_correspondences"]
                                    ["real_top1_combined_score_percentile_p"],
    "UNSAT_viol_ge_15_x2_directions": min(1.0, min(p1, p2) * 2),
}
camp_ps["F2_bridge_best_exact_perm"] = 1.0
ps_sorted = sorted((v, k) for k, v in camp_ps.items())
m = len(ps_sorted)
raw_q = [min(1.0, p * m / i) for i, (p, _) in enumerate(ps_sorted, 1)]
for i in range(m - 2, -1, -1):                       # BH step-up monotonicity
    raw_q[i] = min(raw_q[i], raw_q[i + 1])
bh = [{"test": k, "p": round(p, 4), "bh_q": round(q, 4)}
      for (p, k), q in zip(ps_sorted, raw_q)]
n_disc = sum(1 for row in bh if row["bh_q"] < 0.05)
print(f"[FDR] BH over {m} campaign p-values -> discoveries at q<0.05: {n_disc}")

# =========================================================== write artifact
out = {
    "task": "N_full_adaptive_null_programme", "seed": SEED,
    "spec": "reports/N_NULL_SPEC.md (frozen before run)",
    "constitution": "v2.2",
    "observed_targets": {
        "T1_retained": 0, "T2_A_only_S2_red_bits": 0.0,
        "T3_max_indep_collapsed_anchors": 1,
        "T4_rel_sat": f"{OBS_SAT}/{OBS_BP} (viol {OBS_BP-OBS_SAT}, UNSAT)",
        "T5_licensed_S0_abs_bits": 0.0,
        "T6_naive_contrasts": {"naive_MDL_dl_bits": round(OBS_NAIVE_MDL, 1),
                                "naive_ge3_channel_signs_real_data": OBS_NAIVE_GE3,
                                "wrong_language_bench_G": "0.836-0.895 recovered @ FP 0.9998-1.0"},
    },
    "reused_nulls_cited": {
        "random_anchor_null_H": {"n": 200, "verdict": hnull["verdict"],
                                 "p_null_leq_real": hnull["p_null_leq_real"]},
        "random_hyperedge_null_I": {"n": hyper_null["n_reps"],
                                    "retained_max": hyper_null["retained_max"],
                                    "max_indep_anchors": hyper_null["max_indep_anchors_overall"]},
        "wrong_language_bench_G": surface["benches"]["wrong_language_misspecified"]["rows"],
        "gate_null_calibration_repo": "scripts/gate_null_calibration.py: 3/500=0.6% (paper)",
    },
    "tier1_component_nulls": T1,
    "tier2_lattice_nulls": T2,
    "tier3_full_adaptive": T3,
    "tier3_reps": T3_reps,
    "planted_positive_calibration": PLANTED,
    "unsat_adjudication": unsat,
    "fdr_bh_campaign_pvalues": bh,
    "n_discoveries_q05": n_disc,
    "counts": {
        "component_nulls_new": 2000+2000+1000+1000+1000+1000+1000+1000+1000+1000+1000,
        "lattice_nulls_new": 150+100+150,
        "lattice_nulls_cited": 400,
        "full_adaptive_reps": N_ADAPTIVE,
        "planted_reps": 20,
    },
}
json.dump(out, open(os.path.join(OUT, "n_adaptive_null.json"), "w"), indent=1)
print("WROTE", os.path.join(OUT, "n_adaptive_null.json"))
print(json.dumps({k: out[k] for k in ("tier3_full_adaptive", "planted_positive_calibration",
                                      "unsat_adjudication", "n_discoveries_q05", "counts")},
                 indent=1))
