#!/usr/bin/env python3
"""TASK H — Joint anchor-lattice inference with 3 genuinely-different solvers.

H_MODEL_1: Bayesian factor graph (Gibbs) over sign-value variables.
H_MODEL_2: CP / exact arc-consistency + model counting (SIS) + backbone + gauge quotient.
H_MODEL_3: MDL penalized beam search over lattice-consistent systems,
           with naive / dedup / Art.-XII-discounted evidence accounting.

All numbers are computed from data/anchor_lattice/lattice.json + sign_universe/*.json
+ substitution_bridge/*.json + stroke_corpus/E_summary.json. Seed 20260708.
Constitution v2.2: Art. VIII/XI/XII/XV enforced structurally (see SPEC).
"""
import json, math, os, sys, itertools
import numpy as np
from collections import Counter, defaultdict

SEED = 20260708
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(DATA, "candidates")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- domain
CONS = ["0", "d", "j", "k", "m", "n", "p", "q", "r", "s", "t", "w", "z"]  # '0' = vowel-only
VOWS = ["a", "e", "i", "o", "u"]
DOM = [(c, v, 0) for c in CONS for v in VOWS] + [("p", "u", 2), ("r", "a", 2)]
ND = len(DOM)  # 67
D_IDX = {d: i for i, d in enumerate(DOM)}
H0 = math.log2(ND)  # 6.066 bits baseline per sign

def parse_label(lab):
    """Parse an LB-convention label to a domain cell; None if non-phonetic."""
    if lab is None or lab.startswith("*") or lab.startswith("LOGO"):
        return None
    lab = lab.strip()
    series = 0
    if lab and lab[-1] in "23":
        series = int(lab[-1]); lab = lab[:-1]
    lab = lab.lower()
    if lab in VOWS:
        cell = ("0", lab, series)
    elif len(lab) == 2 and lab[0] in CONS and lab[1] in VOWS:
        cell = (lab[0], lab[1], series)
    else:
        return None
    if cell in D_IDX:
        return cell
    # series cell not in domain (e.g. PA3): fall back to base cell for C/V grading only
    base = (cell[0], cell[1], 0)
    return base if base in D_IDX else None

C_OF = np.array([CONS.index(d[0]) for d in DOM])
V_OF = np.array([VOWS.index(d[1]) for d in DOM])
COMPAT = (C_OF[:, None] == C_OF[None, :]) | (V_OF[:, None] == V_OF[None, :])  # same-C OR same-V

# ---------------------------------------------------------------- load lattice
lat = json.load(open(os.path.join(DATA, "anchor_lattice", "lattice.json")))
SIGNS = [n["key"] for n in lat["nodes"] if n["type"] == "SIGN"]
SIGN_CLASS = {n["key"]: n.get("sign_class") for n in lat["nodes"] if n["type"] == "SIGN"}
A_ONLY = sorted([s for s in SIGNS if SIGN_CLASS[s] == "A-only"])
assert len(SIGNS) == 163 and len(A_ONLY) == 69

vb_edges = [e for e in lat["edges"] if e.get("value_bearing")]
# dependency-collapsed pins: sign -> label (clone edges never stack; Art. XI)
pin_label, pin_edges, pin_lineages = {}, Counter(), defaultdict(set)
raw_slots = 0
for e in vb_edges:
    for s, lab in (e.get("candidate_values") or {}).items():
        raw_slots += 1
        pin_label.setdefault(s, lab)
        pin_edges[s] += 1
        pin_lineages[s].add(e["dependency_lineage"])
PINS = {s: parse_label(l) for s, l in pin_label.items()}
VACUOUS_PINS = sorted([s for s, c in PINS.items() if c is None])   # ['*49']
PINS = {s: c for s, c in PINS.items() if c is not None}            # 38 signs
N_PIN = len(PINS)

rel_pairs = set()
for e in lat["edges"]:
    if e["etype"] == "relative_substitution_relation" and len(e["signs_constrained"]) == 2:
        rel_pairs.add(tuple(sorted(e["signs_constrained"])))
rel_pairs = sorted(rel_pairs)
REL_SIGNS = sorted({s for p in rel_pairs for s in p})

# ---------------------------------------------------------------- calibration
# rel-pair semantics graded on the LB benchmark labels (graded-only; Art. XII note)
bench_pairs = [(a, b) for a, b in rel_pairs if parse_label(a) and parse_label(b)]
bench_sat = [bool(COMPAT[D_IDX[parse_label(a)], D_IDX[parse_label(b)]]) for a, b in bench_pairs]
rate_bench = float(np.mean(bench_sat)) if bench_sat else 0.0
rate_chance = float(COMPAT.mean())  # over ordered pairs incl. diagonal-free? use full mean
# exclude self-pairs from chance
rate_chance = float((COMPAT.sum() - ND) / (ND * (ND - 1)))
w1 = math.log(max(rate_bench, 1e-9) / rate_chance)             # nats, compat=1
w0 = math.log(max(1 - rate_bench, 1e-9) / (1 - rate_chance))   # nats, compat=0
rel_bits_per_edge = (math.log2(max(rate_bench, 1e-9) / rate_chance)) if rate_bench > rate_chance else 0.0
# exact one-sided binomial test: is the LA rel channel above chance on the graded benchmark?
_k = int(sum(bench_sat)); _n = len(bench_pairs)
rel_binom_p = float(sum(math.comb(_n, i) * rate_chance**i * (1 - rate_chance)**(_n - i)
                        for i in range(_k, _n + 1)))

# stroke / bridge channel weights from the calibration artifacts (mechanical)
f4 = json.load(open(os.path.join(DATA, "substitution_bridge", "F4_la_relative_constraints.json")))
bridge_bits_per_sign = (1.0 - f4["mean_normalized_uncertainty"]) * math.log2(51)
stroke = json.load(open(os.path.join(DATA, "stroke_corpus", "E_summary.json")))
CAL = dict(rate_bench=rate_bench, rate_chance=rate_chance, n_bench_pairs=len(bench_pairs),
           rel_binom_k_sat=_k, rel_binom_p_one_sided=rel_binom_p,
           w1_nats=w1, w0_nats=w0, rel_bits_per_edge=rel_bits_per_edge,
           bridge_bits_per_sign=bridge_bits_per_sign,
           bridge_top1_rate=f4["geometry_top1_equals_homomorph_rate"])

# scenarios: source-lineage reliability rho for META_CONTINUITY (explicit variable)
RHO = {"S0_collapse_compliant": 0.0,
       "S2_heldout_calibrated": 2.0 / 26.0,
       "S3_truthlayer_cap": 0.75,
       "S1_conditional_continuity": 0.999999}

def mixture_entropy(rho):
    """Marginal entropy of a pinned sign under mixture rho*delta + (1-rho)*uniform."""
    p_pin = rho + (1 - rho) / ND
    p_oth = (1 - rho) / ND
    h = -p_pin * math.log2(p_pin) - (ND - 1) * p_oth * math.log2(p_oth) if p_oth > 0 else 0.0
    return h

# ================================================================ H_MODEL_1: Gibbs
def gibbs(rho, stack_clones=False, sweeps=3000, burn=1000, chains=3):
    nodes = sorted(set(PINS) | set(REL_SIGNS))
    idx = {s: i for i, s in enumerate(nodes)}
    nb = defaultdict(list)
    for a, b in rel_pairs:
        if a in idx and b in idx:
            nb[a].append(b); nb[b].append(a)
    log_anchor = np.zeros((len(nodes), ND))
    for s, cell in PINS.items():
        f = np.full(ND, (1 - rho) / ND)
        f[D_IDX[cell]] += rho
        la = np.log(f)
        if stack_clones:
            la = la * pin_edges[s]  # Art.-XI VIOLATION variant (for quantifying the error)
        log_anchor[idx[s]] = la
    counts = np.zeros((len(nodes), ND))
    for ch in range(chains):
        r = np.random.default_rng(SEED + ch)
        state = r.integers(0, ND, len(nodes))
        for it in range(sweeps):
            for s in nodes:
                i = idx[s]
                lp = log_anchor[i].copy()
                for t in nb[s]:
                    cvec = COMPAT[:, state[idx[t]]]
                    lp += np.where(cvec, w1, w0)
                lp -= lp.max()
                p = np.exp(lp); p /= p.sum()
                state[i] = r.choice(ND, p=p)
            if it >= burn:
                counts[np.arange(len(nodes)), state] += 1
    n_samp = chains * (sweeps - burn)
    P = counts / n_samp
    ent = {}
    for s in nodes:
        p = P[idx[s]]
        nz = p[p > 0]
        h = -(nz * np.log2(nz)).sum()
        h = min(H0, h + (len(nz) - 1) / (2 * n_samp * math.log(2)))  # Miller–Madow
        ent[s] = float(h)
    return ent

M1 = {}
for scen, rho in RHO.items():
    ent = gibbs(rho)
    full = {s: (ent.get(s, H0)) for s in SIGNS}
    M1[scen] = {"rho": rho,
                "analytic_pinned_entropy": mixture_entropy(rho),
                "per_sign_entropy": full,
                "mean_reduction_all": float(np.mean([H0 - full[s] for s in SIGNS])),
                "mean_reduction_A_only": float(np.mean([H0 - full[s] for s in A_ONLY])),
                "n_signs_reduced_gt_0p1": sum(1 for s in SIGNS if H0 - full[s] > 0.1),
                "A_only_reduced_gt_0p1": sorted([s for s in A_ONLY if H0 - full[s] > 0.1])}
# Art.-XI clone-stacking error, quantified at S2
ent_stacked = gibbs(RHO["S2_heldout_calibrated"], stack_clones=True)
M1["S2_naive_clone_stacked_VIOLATION"] = {
    "example_sign_A": {"n_clone_edges": pin_edges.get("A", 0),
                       "entropy_collapsed": M1["S2_heldout_calibrated"]["per_sign_entropy"]["A"],
                       "entropy_stacked": float(ent_stacked.get("A", H0))},
    "mean_pinned_entropy_stacked": float(np.mean([ent_stacked[s] for s in PINS])),
    "mean_pinned_entropy_collapsed": float(np.mean(
        [M1["S2_heldout_calibrated"]["per_sign_entropy"][s] for s in PINS]))}

# ================================================================ H_MODEL_2: CP
# (a) mutual-consistency audit: hard anchors + hard rel
viol = []
for a, b in rel_pairs:
    if a in PINS and b in PINS and not COMPAT[D_IDX[PINS[a]], D_IDX[PINS[b]]]:
        viol.append((a, b))
# (b) arc-consistent domains, anchors hard, violated rel edges dropped (else UNSAT)
dom = {s: (np.zeros(ND, bool) if s in PINS else np.ones(ND, bool)) for s in SIGNS}
for s, c in PINS.items():
    dom[s][D_IDX[c]] = True
active = [p for p in rel_pairs if p not in set(map(tuple, viol))]
changed = True
while changed:
    changed = False
    for a, b in active:
        for x, y in ((a, b), (b, a)):
            sup = COMPAT[:, dom[y]].any(axis=1)
            nd = dom[x] & sup
            if nd.sum() != dom[x].sum():
                dom[x] = nd; changed = True
dom_sizes = {s: int(dom[s].sum()) for s in SIGNS}
backbone = sorted([s for s, n in dom_sizes.items() if n == 1])
# (c) S0 model counting (rel hard only, no pins) via SIS on components
adj = defaultdict(set)
for a, b in rel_pairs:
    adj[a].add(b); adj[b].add(a)
comps, seen = [], set()
for s in REL_SIGNS:
    if s in seen: continue
    stack, comp = [s], set()
    while stack:
        x = stack.pop()
        if x in comp: continue
        comp.add(x); stack.extend(adj[x] - comp)
    seen |= comp
    comps.append(sorted(comp))

def sis_count(comp, pins=None, n_part=20000, seed=SEED):
    """Sequential-importance-sampling estimate of #assignments satisfying all pair edges."""
    r = np.random.default_rng(seed)
    order = comp[:]
    logw = np.zeros(n_part)
    state = np.zeros((n_part, len(order)), int)
    dead = np.zeros(n_part, bool)
    pos = {s: i for i, s in enumerate(order)}
    for i, s in enumerate(order):
        allowed = np.ones((n_part, ND), bool)
        if pins and s in pins:
            allowed[:] = False; allowed[:, D_IDX[pins[s]]] = True
        for t in adj[s]:
            if t in pos and pos[t] < i:
                allowed &= COMPAT[state[:, pos[t]]]
        cnt = allowed.sum(axis=1)
        dead |= cnt == 0
        cnt_safe = np.maximum(cnt, 1)
        logw += np.where(dead, -np.inf, np.log(cnt_safe))
        # sample uniformly from allowed
        u = r.random(n_part)
        cum = np.cumsum(allowed, axis=1)
        tgt = np.ceil(u * cnt_safe).astype(int)
        state[:, i] = np.argmax(cum >= tgt[:, None], axis=1)
    w = np.exp(logw - logw[~dead].max()) if (~dead).any() else np.zeros(n_part)
    mean_w = w.mean()
    est_log10 = (math.log10(mean_w) + logw[~dead].max() / math.log(10)) if mean_w > 0 else -np.inf
    se_rel = float(w.std() / (w.mean() * math.sqrt(n_part))) if mean_w > 0 else float("nan")
    return est_log10, se_rel

comp_counts = []
for comp in comps:
    lg, se = sis_count(comp)
    comp_counts.append({"signs": comp, "n": len(comp),
                        "log10_solutions_relhard": lg, "rel_se": se,
                        "log10_free": len(comp) * math.log10(ND)})
log10_joint_constrained = sum(c["log10_solutions_relhard"] for c in comp_counts)
log10_gauge = math.log10(math.factorial(12)) + math.log10(math.factorial(5))
n_uncon = len(SIGNS) - len(REL_SIGNS)
M2 = {"hard_anchor_hard_rel_consistency": {
        "n_rel_pairs_both_pinned": sum(1 for a, b in rel_pairs if a in PINS and b in PINS),
        "n_violated": len(viol), "violated_pairs": viol,
        "verdict": "UNSAT" if viol else "SAT"},
      "arc_consistent_domains_anchorhard": {
        "n_pinned_singleton": sum(1 for s in PINS if dom_sizes[s] == 1),
        "backbone_signs": backbone,
        "n_signs_domain_reduced": sum(1 for s in SIGNS if dom_sizes[s] < ND),
        "A_only_domain_reduced": {s: dom_sizes[s] for s in A_ONLY if dom_sizes[s] < ND},
        "reduced_nonpinned": {s: dom_sizes[s] for s in SIGNS
                              if s not in PINS and dom_sizes[s] < ND}},
      "S0_model_counting": {
        "components": comp_counts,
        "log10_solutions_rel_subgraph": log10_joint_constrained,
        "log10_solutions_total": log10_joint_constrained + n_uncon * math.log10(ND),
        "log10_gauge_group": log10_gauge,
        "log10_equivalence_classes_lower_bound":
            log10_joint_constrained + n_uncon * math.log10(ND) - log10_gauge,
        "joint_bits_removed_by_rel_hard":
            (len(REL_SIGNS) * math.log2(ND)) - log10_joint_constrained * math.log2(10),
        "note": "joint reduction only; per-sign marginals stay uniform (gauge symmetry); "
                "absolute per-sign bits earned = 0 (Art. XV)"}}
# S1 counting (anchors hard): strict (all rel edges) and relaxed (violated edges dropped)
comp_counts_s1 = []
adj_strict = {k: set(v) for k, v in adj.items()}
adj_relaxed = defaultdict(set)
for a, b in active:
    adj_relaxed[a].add(b); adj_relaxed[b].add(a)
for comp in comps:
    lg_strict, se_s = sis_count(comp, pins=PINS)
    adj_save = dict(adj)
    adj.clear(); adj.update(adj_relaxed)
    lg_relax, se_r = sis_count(comp, pins=PINS)
    adj.clear(); adj.update(adj_save)
    comp_counts_s1.append({"signs": comp, "log10_solutions_strict": lg_strict,
                           "log10_solutions_violated_dropped": lg_relax})
tot_strict = sum(c["log10_solutions_strict"] for c in comp_counts_s1)
M2["S1_model_counting_anchorhard"] = {
    "components": comp_counts_s1,
    "log10_solutions_strict": tot_strict,
    "strict_verdict": "UNSAT (0 solutions)" if tot_strict == -float("inf") else "SAT",
    "log10_solutions_violated_dropped":
        sum(c["log10_solutions_violated_dropped"] for c in comp_counts_s1),
    "note": "strict = anchors hard + ALL rel edges hard; relaxed drops the 15 "
            "benchmark-violated pinned pairs; unpinned signs outside the rel graph stay free"}

# ================================================================ H_MODEL_3: MDL
dedup_slots = N_PIN
mdl_rows = []
for accounting, credit_slots in [("naive_raw", raw_slots - len([1 for e in vb_edges for s, l in (e.get('candidate_values') or {}).items() if parse_label(l) is None])),
                                 ("dedup_unique_signpins", dedup_slots),
                                 ("art12_discounted", 0)]:
    # anchored system: flag L=1 (1 bit) + assign 38 pins (38*H0) - data credit (credit*H0)
    dl_anch = 1 + N_PIN * H0 - credit_slots * H0
    dl_unanch = 0.0
    mdl_rows.append({"accounting": accounting, "credit_slots": credit_slots,
                     "DL_anchored_minus_unanchored_bits": dl_anch - dl_unanch,
                     "winner": "ANCHORED" if dl_anch < dl_unanch else
                               ("TIE" if abs(dl_anch - dl_unanch) < 1e-9 else "UNANCHORED")})
# REL channel MDL: does adding rel structure pay?
rel_gain = len(bench_pairs) * rel_bits_per_edge  # best case: all edges explained
mdl_rel = {"rel_bits_per_edge_calibrated": rel_bits_per_edge,
           "n_edges": len(rel_pairs),
           "max_data_credit_bits": rel_gain,
           "cost_to_assign_rel_subgraph_bits": len(REL_SIGNS) * H0,
           "winner": "REL_STRUCTURE" if rel_gain > len(REL_SIGNS) * H0 + 1 else "UNSTRUCTURED"}
# beam enumeration of tied systems under the naive winner (L=1, REL soft), tie window 1 bit
def beam_ties(comp, pins, K=500, delta_bits=1.0):
    order = comp[:]
    beams = [({}, 0.0)]
    for s in order:
        newb = []
        for asg, sc in beams:
            forced = pins.get(s)
            cand = [D_IDX[forced]] if forced else range(ND)
            for vi in cand:
                d = 0.0
                for t in adj[s]:
                    if t in asg:
                        d += (rel_bits_per_edge if COMPAT[vi, asg[t]] else
                              -math.log2((1 - rate_chance) / max(1e-9, 1 - rate_bench)))
                a2 = dict(asg); a2[s] = vi
                newb.append((a2, sc + d))
        newb.sort(key=lambda x: -x[1])
        beams = newb[:K]
    best = beams[0][1]
    tied = [b for b in beams if best - b[1] <= delta_bits]
    # collapse by relabeling signature: (C-partition, V-partition, absolute pinned values)
    sigs = set()
    for asg, _ in tied:
        cpart, vpart, cmap, vmap = [], [], {}, {}
        for s in comp:
            c, v = C_OF[asg[s]], V_OF[asg[s]]
            cpart.append(cmap.setdefault(c, len(cmap)))
            vpart.append(vmap.setdefault(v, len(vmap)))
        pinned_abs = tuple((s, asg[s]) for s in comp if s in pins)
        sigs.add((tuple(cpart), tuple(vpart), pinned_abs))
    div = {s: len({asg[s] for asg, _ in tied}) for s in comp}
    return {"n_tied_in_beam": len(tied), "n_equivalence_classes_in_beam": len(sigs),
            "beam_truncated": len(beams) == K, "per_sign_value_diversity": div}

m3_comp = {tuple(c[0:1])[0]: beam_ties(c, PINS) for c in comps}
M3 = {"anchored_vs_unanchored": mdl_rows, "rel_channel": mdl_rel,
      "tied_system_enumeration_naiveL1": {str(k): v for k, v in m3_comp.items()},
      "note": "beam ties are LOWER bounds on the tie set; exact tie counts are the M2 "
              "solution counts (10^x scale)"}

# ================================================================ NULL: random anchors
R_S2 = H0 - mixture_entropy(RHO["S2_heldout_calibrated"])
null_means, null_counts = [], []
real_Aonly_mean = 0.0  # 0 parseable pins on A-only signs (only *49, vacuous)
for i in range(200):
    r = np.random.default_rng(SEED + 1000 + i)
    targets = r.choice(len(SIGNS), size=N_PIN, replace=False)
    hit = sum(1 for t in targets if SIGNS[t] in set(A_ONLY))
    null_counts.append(hit)
    null_means.append(hit * R_S2 / len(A_ONLY))
null_means = np.array(null_means)
NULL = {"R_bits_per_pinned_sign_S2": R_S2,
        "real_A_only_mean_reduction": real_Aonly_mean,
        "real_A_only_signs_pinned_parseable": 0,
        "vacuous_A_only_pin": VACUOUS_PINS,
        "null_A_only_mean_reduction_mean": float(null_means.mean()),
        "null_A_only_mean_reduction_p5_p95": [float(np.percentile(null_means, 5)),
                                              float(np.percentile(null_means, 95))],
        "null_A_only_pinned_count_mean": float(np.mean(null_counts)),
        "p_null_leq_real": float((null_means <= real_Aonly_mean).mean()),
        "verdict": "REAL_BELOW_NULL" if (null_means <= real_Aonly_mean).mean() < 0.05
                   else "REAL_NOT_ABOVE_NULL"}

# ================================================================ grain sensitivity
def grain_view(grain):
    u = json.load(open(os.path.join(DATA, "sign_universe", f"{grain}.json")))
    cons = json.load(open(os.path.join(DATA, "sign_universe", "conservative.json")))
    if grain == "conservative":
        mapping = {k: [k] for k in SIGNS}
    elif grain == "merged":
        # conservative sign -> its merged_id (forward map; detects RA/RA2-type merges)
        mapping = {k: [v.get("merged_id") or k] for k, v in cons["signs"].items()}
    else:  # split: conservative -> all split signs claiming it as conservative_id
        mapping = {}
        for k, v in u["signs"].items():
            cid = v.get("conservative_id")
            if cid:
                mapping.setdefault(cid, []).append(k)
        mapping = {c: sorted(ks) for c, ks in mapping.items()}
    pin_targets = {}
    merged_conflicts = []
    for s, cell in PINS.items():
        tg = mapping.get(s, [s]) if grain != "conservative" else [s]
        tg = tg if isinstance(tg, list) else [tg]
        for t in tg:
            if t in pin_targets and pin_targets[t] != cell:
                merged_conflicts.append((t, str(pin_targets[t]), str(cell)))
            pin_targets[t] = cell
    a_only = [k for k, v in u["signs"].items() if v["class"] == "A-only"]
    a_pinned = [s for s in a_only if s in pin_targets]
    return {"n_signs": len(u["signs"]), "n_pinned_signs": len(pin_targets),
            "n_A_only": len(a_only), "A_only_pinned_parseable": a_pinned,
            "merged_pin_conflicts": merged_conflicts}

GRAIN = {g: grain_view(g) for g in ["conservative", "split", "merged"]}

# ================================================================ solver agreement
c1 = {s for s in SIGNS if H0 - M1["S2_heldout_calibrated"]["per_sign_entropy"][s] > 0.1}
c2 = {s for s in SIGNS if dom_sizes[s] < ND}
c3 = set()
for cinfo in m3_comp.values():
    for s, ndiv in cinfo["per_sign_value_diversity"].items():
        if ndiv == 1:
            c3.add(s)
c3 |= set(PINS)
def jac(a, b): return len(a & b) / len(a | b) if a | b else 1.0
AGREE = {"M1_constrained_S2_gt0.1bit": sorted(c1),
         "M2_domain_reduced_anchorhard": sorted(c2),
         "M3_value_stable_in_ties": sorted(c3),
         "jaccard_M1_M2": jac(c1, c2), "jaccard_M1_M3": jac(c1, c3),
         "jaccard_M2_M3": jac(c2, c3),
         "A_only_in_any": sorted((c1 | c2 | c3) & set(A_ONLY))}

# ================================================================ dump
res = {"seed": SEED, "domain_size": ND, "H0_bits": H0,
       "n_signs": len(SIGNS), "n_A_only": len(A_ONLY),
       "n_value_bearing_edges": len(vb_edges), "raw_pin_slots": raw_slots,
       "n_pinned_signs_parseable": N_PIN, "vacuous_pins": VACUOUS_PINS,
       "n_rel_pairs": len(rel_pairs), "n_rel_signs": len(REL_SIGNS),
       "calibration": CAL, "scenarios": RHO}
json.dump(res, open(os.path.join(OUT, "h_setup_and_calibration.json"), "w"), indent=1)
json.dump(M1, open(os.path.join(OUT, "h_model1_bayes_marginals.json"), "w"), indent=1)
json.dump(M2, open(os.path.join(OUT, "h_model2_cp_domains.json"), "w"), indent=1, default=str)
json.dump(M3, open(os.path.join(OUT, "h_model3_mdl_systems.json"), "w"), indent=1)
json.dump(NULL, open(os.path.join(OUT, "h_null_random_anchor.json"), "w"), indent=1)
json.dump(GRAIN, open(os.path.join(OUT, "h_grain_sensitivity.json"), "w"), indent=1)
json.dump(AGREE, open(os.path.join(OUT, "h_solver_agreement.json"), "w"), indent=1)

print("== SETUP =="); print(json.dumps(res, indent=1)[:1200])
print("== M1 summary ==")
for k, v in M1.items():
    if k.startswith("S"):
        try:
            print(f" {k}: rho={v['rho']:.3f} analytic_pinned_H={v['analytic_pinned_entropy']:.3f} "
                  f"meanRed_all={v['mean_reduction_all']:.4f} meanRed_Aonly={v['mean_reduction_A_only']:.5f} "
                  f"n>0.1bit={v['n_signs_reduced_gt_0p1']} Aonly>0.1={v['A_only_reduced_gt_0p1']}")
        except (KeyError, TypeError):
            print(f" {k}: {json.dumps(v)[:400]}")
print("== M2 =="); print(json.dumps({k: v for k, v in M2.items() if k != 'arc_consistent_domains_anchorhard'}, indent=1, default=str)[:2000])
print("AC:", json.dumps(M2["arc_consistent_domains_anchorhard"], indent=1)[:900])
print("== M3 =="); print(json.dumps(M3["anchored_vs_unanchored"], indent=1))
print(json.dumps(M3["rel_channel"], indent=1))
print("ties:", json.dumps(M3["tied_system_enumeration_naiveL1"], indent=1)[:1200])
print("== NULL =="); print(json.dumps(NULL, indent=1))
print("== GRAIN =="); print(json.dumps(GRAIN, indent=1))
print("== AGREEMENT =="); print(json.dumps(AGREE, indent=1)[:1500])
