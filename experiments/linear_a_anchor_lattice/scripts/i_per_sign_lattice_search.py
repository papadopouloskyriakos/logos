"""TASK I — EXHAUSTIVE UNRESOLVED-SIGN LATTICE SEARCH.

For EACH of the 151 value-unresolved signs in the conservative universe
(esp. the 69 A-only):
  (1) enumerate the preregistered candidate-value domain;
  (2) list every lattice hyperedge touching it;
  (3) count independent channels + dependency lineages (Art. XI collapse:
      LIN_L_TOP / LIN_L_PN / LIN_L_GLOSS / LIN_H / LIN_C all descend from
      META_CONTINUITY_LA_eq_LB -> ONE value-bearing meta-lineage; LIN_EG has
      SEED_A = 0; LIN_REL / LIN_MORPH / LIN_FORMULA are value-free);
  (4) propagate constraints jointly — REUSE Task H solver artifacts
      (M1 Bayes marginals S2, M2 arc-consistent domains, M3 tie diversity)
      plus a fresh per-sign rel-consistency recomputation (COMPAT rule);
  (5) rank values ONLY if >=2 INDEPENDENT channels contribute;
  (6) held-out prediction: the sign's continuity candidate must satisfy the
      corpus-internal substitution channel (rel pairs, both-pinned), which was
      NOT used to derive the pins — graded vs a permutation null;
  (7) compare vs matched random values (permutation of pin labels) and
      matched random hyperedges (value-bearing edges re-targeted at random
      signs, sizes/lineages preserved).

RETENTION GATE (all mechanically evaluated, fail CLOSED):
  branch A: >=3 independent overlapping anchors (distinct COLLAPSED
            value-bearing lineages pinning this sign);
  branch B: >=2 independent value channels AND validated substitution/stroke
            support (stroke = SOURCE_BLOCKED (Task E); substitution counts
            only if the sign's held-out rel record beats the permutation null
            at p<0.05 with >=3 pairs);
  branch C: one >=4-slot anchor AND independent held-out recurrence
            (an edge with derivation_vs_heldout not DERIVATION* — the lattice
            has none that is non-vacuous);
  AND leave-one-anchor + leave-one-lineage + leave-one-site + adaptive-null
  survival.  A candidate is NOT retained for producing a recognizable word.

Outputs:
  data/candidates/per_sign/per_sign_table.json
  data/candidates/per_sign/random_hyperedge_null.json
  (report written separately)

Seed 20260708.  No new value claims; L2 accounting only (Art. V/XV/XXII).
"""
import json, math, os, random, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, "data")
OUT = os.path.join(DATA, "candidates", "per_sign")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE)
from h_common import VGRID, VIDX, NV, parse_label  # 65-slot CV grid

SEED = 20260708
rng = random.Random(SEED)

# ---------------------------------------------------------------- load inputs
inv = json.load(open(os.path.join(DATA, "sign_universe", "conservative.json")))["signs"]
lat = json.load(open(os.path.join(DATA, "anchor_lattice", "lattice.json")))
m1 = json.load(open(os.path.join(DATA, "candidates", "h_model1_bayes_marginals.json")))
m2 = json.load(open(os.path.join(DATA, "candidates", "h_model2_cp_domains.json")))
m3 = json.load(open(os.path.join(DATA, "candidates", "h_model3_mdl_systems.json")))
hsetup = json.load(open(os.path.join(DATA, "candidates", "h_setup_and_calibration.json")))
hnull = json.load(open(os.path.join(DATA, "candidates", "h_null_random_anchor.json")))

H0 = hsetup["H0_bits"]

UNRESOLVED = sorted([k for k, v in inv.items() if v["class"] != "numeral"])
A_ONLY = sorted([k for k in UNRESOLVED if inv[k]["class"] == "A-only"])
assert len(UNRESOLVED) == 151 and len(A_ONLY) == 69, (len(UNRESOLVED), len(A_ONLY))

# preregistered candidate-value domains (from sign universe, Task B)
DOM_SIZE = {
    "syllabic_CV_or_V": NV,                       # 65-slot LB CV grid (h_common)
    "commodity_ideogram_semantic": None,          # semantic class, not enumerated as grid
    "fractional_quantity": None,
    "numeric_quantity": None,
    "unknown": None,
}

# ---------------------------------------------------------------- lineage collapse
META_CONTINUITY = {"LIN_L_TOP", "LIN_L_PN", "LIN_L_GLOSS", "LIN_H", "LIN_C"}
def collapse(lin):
    return "META_CONTINUITY_LA_eq_LB" if lin in META_CONTINUITY else lin

AGGREGATED_GEO = {"mixed Cretan admin sites", "LA corpus", "Crete", "Egypt/Crete"}
def geo_sites(g):
    """Return (concrete_sites:set, aggregated:bool)."""
    items = g if isinstance(g, list) else [g]
    conc, agg = set(), False
    for it in items:
        if it in AGGREGATED_GEO:
            agg = True
        else:
            conc.add(it)
    return conc, agg

# ---------------------------------------------------------------- edge index
edges_by_sign = defaultdict(list)
for e in lat["edges"]:
    for s in e.get("signs_constrained", []):
        edges_by_sign[s].append(e)

# dependency-collapsed continuity pins (identical to Task H accounting)
vb_edges = [e for e in lat["edges"] if e.get("value_bearing")]
pin_label = {}
for e in vb_edges:
    for s, lab in (e.get("candidate_values") or {}).items():
        pin_label.setdefault(s, lab)
PINS = {s: parse_label(l) for s, l in pin_label.items()}
VACUOUS = sorted([s for s, c in PINS.items() if c is None])
PINS = {s: c for s, c in PINS.items() if c is not None}

# ---------------------------------------------------------------- rel graph (value-free channel)
# EXACTLY the Task H definition: pairwise lattice substitution edges only
# (no rel_class clique expansion — that would assume coordinate transitivity).
rel_pairs = set()
for e in lat["edges"]:
    if e["etype"] == "relative_substitution_relation" and len(e["signs_constrained"]) == 2:
        rel_pairs.add(tuple(sorted(e["signs_constrained"])))
rel_pairs = sorted(rel_pairs)

def compat(c1, c2):
    return (c1[0] == c2[0]) or (c1[1] == c2[1])   # same-C OR same-V

both_pinned = [(a, b) for a, b in rel_pairs if a in PINS and b in PINS]
sat_real = {p: compat(PINS[p[0]], PINS[p[1]]) for p in both_pinned}
n_bp, n_sat = len(both_pinned), sum(sat_real.values())
print(f"[rel] both-pinned pairs={n_bp} sat={n_sat} violated={n_bp - n_sat} "
      f"(H reported UNSAT 15/24)")
assert n_bp == 24 and (n_bp - n_sat) == 15, "must reproduce Task H M2 exactly"

# permutation null for the rel held-out check (labels shuffled among pinned signs)
NPERM = 2000
pin_signs = sorted(PINS)
pin_vals = [PINS[s] for s in pin_signs]
per_sign_pairs = defaultdict(list)
for p in both_pinned:
    per_sign_pairs[p[0]].append(p); per_sign_pairs[p[1]].append(p)
perm_global = []
perm_sign_ge = Counter()   # per-sign: #perms with sat_count >= real
real_sign_sat = {s: sum(sat_real[p] for p in per_sign_pairs[s]) for s in per_sign_pairs}
for it in range(NPERM):
    vals = pin_vals[:]; rng.shuffle(vals)
    P = dict(zip(pin_signs, vals))
    satp = {p: compat(P[p[0]], P[p[1]]) for p in both_pinned}
    perm_global.append(sum(satp.values()))
    for s in per_sign_pairs:
        if sum(satp[p] for p in per_sign_pairs[s]) >= real_sign_sat[s]:
            perm_sign_ge[s] += 1
p_global = (1 + sum(1 for x in perm_global if x >= n_sat)) / (1 + NPERM)
perm_mean = sum(perm_global) / NPERM
print(f"[rel-null] perm mean sat={perm_mean:.2f}/{n_bp}, real={n_sat}, "
      f"one-sided p(real>=null)={p_global:.4f}")

# ---------------------------------------------------------------- M1/M2/M3 lookups
pe_S2 = m1["S2_heldout_calibrated"]["per_sign_entropy"]
m2_backbone = set(m2["arc_consistent_domains_anchorhard"]["backbone_signs"])
m2_reduced = m2["arc_consistent_domains_anchorhard"]["reduced_nonpinned"]
m3_div = {}
for seedsign, entry in m3.get("tied_system_enumeration_naiveL1", {}).items():
    for s, d in entry.get("per_sign_value_diversity", {}).items():
        m3_div[s] = max(m3_div.get(s, 0), d)

# ---------------------------------------------------------------- per-sign accounting
def sign_row(s):
    meta = inv[s]
    es = edges_by_sign.get(s, [])
    vb = [e for e in es if e.get("value_bearing")]
    etype_counts = Counter(e["etype"] for e in es)
    ch_all = sorted({c for e in es for c in e.get("evidence_channels", [])})
    ch_val = sorted({c for e in vb for c in e.get("evidence_channels", [])})
    lin_raw = sorted({e["dependency_lineage"] for e in es})
    lin_val_raw = sorted({e["dependency_lineage"] for e in vb})
    lin_val_col = sorted({collapse(l) for l in lin_val_raw})
    n_indep_anchors = len(lin_val_col)              # dependency-collapsed
    # candidate domain
    dom = meta.get("candidate_value_domain")
    # anchors detail
    slots = [e.get("slots") for e in vb if isinstance(e.get("slots"), int)]
    max_slots = max(slots) if slots else 0
    sites = set(); any_agg = False
    for e in vb:
        c, a = geo_sites(e.get("geography"))
        sites |= c; any_agg = any_agg or a
    heldout_edges = [e for e in es
                     if not str(e.get("derivation_vs_heldout", "")).startswith("DERIVATION")]
    heldout_nonvacuous = [e for e in heldout_edges if "VACUOUS" not in
                          str(e.get("derivation_vs_heldout", ""))]
    # pre-gate candidate = modal candidate value over value-bearing edges
    val_votes = Counter()
    for e in vb:
        lab = (e.get("candidate_values") or {}).get(s)
        if lab:
            val_votes[lab] += 1
    pre_gate = val_votes.most_common(1)[0][0] if val_votes else None
    pre_gate_parseable = parse_label(pre_gate) is not None if pre_gate else False
    n_edges_supporting_candidate = val_votes.most_common(1)[0][1] if val_votes else 0
    n_lineages_supporting_candidate = len({collapse(e["dependency_lineage"]) for e in vb
        if (e.get("candidate_values") or {}).get(s) == pre_gate}) if pre_gate else 0
    # joint propagation (reused)
    ent_S2 = pe_S2.get(s)
    red_S2 = (H0 - ent_S2) if ent_S2 is not None else None
    if s in m2_backbone:
        m2_state = "PINNED_SINGLETON(conditional on single continuity meta-lineage)"
        m2_domain = 1
    elif s in m2_reduced:
        m2_state = f"REDUCED:{m2_reduced[s]}(conditional, anchor-hard; global rel UNSAT)"
        m2_domain = m2_reduced[s]
    else:
        m2_domain = DOM_SIZE.get(dom)
        m2_state = f"FULL:{m2_domain}" if m2_domain else "FULL(domain not grid-enumerable)"
    # ranking allowed?
    ranking_allowed = n_indep_anchors >= 2
    # held-out rel record
    n_pairs = len(per_sign_pairs.get(s, []))
    n_viol = n_pairs - real_sign_sat.get(s, 0)
    p_rel = ((1 + perm_sign_ge[s]) / (1 + NPERM)) if n_pairs else None
    rel_support_validated = bool(n_pairs >= 3 and p_rel is not None and p_rel < 0.05)
    # ------------- retention gate -------------
    gA = n_indep_anchors >= 3
    stroke_support = False                     # Task E: SOURCE_BLOCKED
    gB = (n_indep_anchors >= 2) and (rel_support_validated or stroke_support)
    gC = (max_slots >= 4) and (len(heldout_nonvacuous) >= 1)
    loo_anchor = n_edges_supporting_candidate >= 2 and n_lineages_supporting_candidate >= 1
    loo_lineage = n_lineages_supporting_candidate >= 2
    loo_site = len(sites) >= 2                 # aggregated descriptors don't count
    # adaptive null: sign's S2 reduction must exceed the random-anchor null band
    null_hi = hnull["null_A_only_mean_reduction_p5_p95"][1]
    adaptive_null = (red_S2 is not None and red_S2 > null_hi
                     and n_indep_anchors >= 2)  # reduction from ONE collapsed lineage
                                                # is not evidence (Art. XI/XII)
    gate_any = gA or gB or gC
    retained = bool(gate_any and loo_anchor and loo_lineage and loo_site and adaptive_null)
    return {
        "sign": s, "class": meta["class"], "occurrences": meta.get("occurrence_count"),
        "n_corpus_sites": len(meta.get("site_distribution") or {}),
        "domain_label": dom, "domain_size": DOM_SIZE.get(dom),
        "n_edges_total": len(es), "edges_by_type": dict(etype_counts),
        "n_value_bearing_edges": len(vb),
        "channels_all": ch_all, "channels_value_bearing": ch_val,
        "lineages_raw": lin_raw, "value_lineages_raw": lin_val_raw,
        "value_lineages_collapsed": lin_val_col,
        "n_independent_anchors_collapsed": n_indep_anchors,
        "anchor_max_slots": max_slots,
        "anchor_concrete_sites": sorted(sites),
        "anchor_geography_aggregated": any_agg,
        "n_heldout_capable_edges_nonvacuous": len(heldout_nonvacuous),
        "entropy_H0_bits": round(H0, 4),
        "entropy_S2_bits": round(ent_S2, 4) if ent_S2 is not None else None,
        "reduction_S2_bits": round(red_S2, 4) if red_S2 is not None else None,
        "m2_domain_state": m2_state, "m2_domain_size": m2_domain,
        "m3_tie_value_diversity": m3_div.get(s),
        "pre_gate_candidate_NOT_A_RANKING": pre_gate,
        "pre_gate_candidate_parseable": pre_gate_parseable,
        "n_edges_supporting_candidate": n_edges_supporting_candidate,
        "n_collapsed_lineages_supporting_candidate": n_lineages_supporting_candidate,
        "ranking_allowed_ge2_independent_channels": ranking_allowed,
        "ranked_candidates": [],   # populated ONLY if ranking_allowed (none expected)
        "heldout_rel_pairs": n_pairs, "heldout_rel_violated": n_viol,
        "heldout_rel_perm_p": round(p_rel, 4) if p_rel is not None else None,
        "rel_support_validated": rel_support_validated,
        "gate": {"A_ge3_independent_overlapping_anchors": gA,
                 "B_ge2_channels_plus_validated_sub_or_stroke": gB,
                 "C_ge4slot_anchor_plus_heldout_recurrence": gC,
                 "leave_one_anchor": loo_anchor, "leave_one_lineage": loo_lineage,
                 "leave_one_site": loo_site, "adaptive_null": adaptive_null,
                 "RETAINED": retained},
    }

rows = [sign_row(s) for s in UNRESOLVED]

# ranking pass (only where allowed — expected empty)
for r in rows:
    if r["ranking_allowed_ge2_independent_channels"]:
        r["ranked_candidates"] = [r["pre_gate_candidate_NOT_A_RANKING"]]

# ---------------------------------------------------------------- random-hyperedge null
# Matched control: keep the 47 value-bearing edges (sizes, slots, lineage tags,
# geography); re-target each at random unresolved signs with random grid values.
NREP = 200
null_summary = {"n_reps": NREP, "retained_counts": [], "max_indep_anchors": [],
                "signs_with_ge1_anchor_mean": 0.0}
syllabic = [s for s in UNRESOLVED if inv[s]["class"] in ("A-only", "AB-shared")]
tot_ge1 = 0
for rep in range(NREP):
    # rebuild per-sign value-bearing incidence at random
    fake = defaultdict(list)   # sign -> list of (collapsed_lineage, slots, geo)
    for e in vb_edges:
        k = len(e.get("candidate_values") or {}) or 1
        targets = rng.sample(syllabic, min(k, len(syllabic)))
        for t in targets:
            fake[t].append((collapse(e["dependency_lineage"]),
                            e.get("slots"), e.get("geography")))
    retained = 0; max_ia = 0
    for s, lst in fake.items():
        ia = len({l for l, _, _ in lst})
        max_ia = max(max_ia, ia)
        slots = [sl for _, sl, _ in lst if isinstance(sl, int)]
        sites = set();
        for _, _, g in lst:
            c, _a = geo_sites(g); sites |= c
        gA = ia >= 3
        gC = (max(slots) if slots else 0) >= 4 and False   # still no held-out edges
        gB = False                                          # stroke blocked; rel not re-run
        loo = (len(lst) >= 2) and (ia >= 2) and (len(sites) >= 2)
        if (gA or gB or gC) and loo:
            retained += 1
    null_summary["retained_counts"].append(retained)
    null_summary["max_indep_anchors"].append(max_ia)
    tot_ge1 += len(fake)
null_summary["signs_with_ge1_anchor_mean"] = tot_ge1 / NREP
null_summary["retained_max"] = max(null_summary["retained_counts"])
null_summary["max_indep_anchors_overall"] = max(null_summary["max_indep_anchors"])
null_summary["note"] = ("All value-bearing lineages collapse to META_CONTINUITY_LA_eq_LB "
                        "(+LIN_EG with SEED_A=0), so independent-anchor count is <=2 in "
                        "ANY re-targeting; the gate retains 0 under the null as well — "
                        "the real-data zero is structural (lineage accounting), and the "
                        "real lattice is NOT distinguishable from random re-targetings "
                        "at gate level.")
del null_summary["retained_counts"]; del null_summary["max_indep_anchors"]

# ---------------------------------------------------------------- global summary
n_ret = sum(r["gate"]["RETAINED"] for r in rows)
by_class = Counter(r["class"] for r in rows)
zero_edge = [r["sign"] for r in rows if r["n_edges_total"] == 0]
a_zero_edge = [s for s in zero_edge if inv[s]["class"] == "A-only"]
a_dark = [r["sign"] for r in rows if r["class"] == "A-only"
          and r["n_value_bearing_edges"] == 0]
rank_allowed = [r["sign"] for r in rows if r["ranking_allowed_ge2_independent_channels"]]
ge1_anchor = [r for r in rows if r["n_independent_anchors_collapsed"] >= 1]
summary = {
    "seed": SEED, "grain": "conservative",
    "n_unresolved": len(rows), "by_class": dict(by_class),
    "n_A_only": len(A_ONLY),
    "domain": {"syllabic_grid_slots": NV, "H0_bits_used_by_H": round(H0, 4),
               "H_max_grid_bits": round(math.log2(NV), 4)},
    "signs_with_zero_lattice_edges": len(zero_edge),
    "A_only_zero_edges": len(a_zero_edge),
    "A_only_value_dark": len(a_dark),
    "signs_with_ge1_collapsed_anchor": len(ge1_anchor),
    "max_independent_anchors_any_sign": max(r["n_independent_anchors_collapsed"]
                                            for r in rows),
    "ranking_allowed_signs": rank_allowed,
    "heldout_rel": {"both_pinned_pairs": n_bp, "satisfied": n_sat,
                    "violated": n_bp - n_sat, "perm_null_mean_sat": round(perm_mean, 2),
                    "perm_p_one_sided": round(p_global, 4), "n_perm": NPERM},
    "vacuous_pins": VACUOUS,
    "random_anchor_null_reused": hnull,
    "random_hyperedge_null": null_summary,
    "retained_candidates": n_ret,
}
json.dump({"summary": summary, "rows": rows},
          open(os.path.join(OUT, "per_sign_table.json"), "w"), indent=1)
json.dump(null_summary, open(os.path.join(OUT, "random_hyperedge_null.json"), "w"),
          indent=1)
print(json.dumps({k: v for k, v in summary.items()
                  if k not in ("random_anchor_null_reused",)}, indent=1))
print("RETAINED:", n_ret)
