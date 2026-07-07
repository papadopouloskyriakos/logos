#!/usr/bin/env python3
"""C5 — STABILITY + INFORMATION GAIN of the C4 Linear A substitution graph (Constitution v2.2).

Subjects the C4 LA sign-substitution graph (clean non-allographic sign edges licensed by >=1 LONG
>=3-sign frame; strong edges = >=2 long frames; REL_CLASSes = connected components of the strong
graph) to a brutal stability audit, then estimates the information gain of its anonymous relations.

STABILITY BATTERY
  1. bootstrap        — resample DOCUMENTS with replacement (n_boot); recompute the graph; edge and
                        class-co-membership recurrence.
  2. site_holdout     — leave-one-site-out (each of the 52 sites, incl. the dominant Haghia Triada);
                        strong-edge / class survival.
  3. segmentation     — rebuild the sign graph on ALTERNATE segmentations (GORILA word vs B1
                        SEG_ENTRY / SEG_ROW / SEG_FORMULA / SEG_PROBABILISTIC_BOUNDARY units);
                        edge-set Jaccard vs the GORILA-word baseline.
  4. encoding         — collapse numbered/lettered allographs to their base sign (RA/RA2 -> RA,
                        *21F/*21M -> *21) before building; edge / class overlap.
  5. damage_exclusion — drop every word TYPE containing a *NNN / measure (unidentified) sign; rebuild;
                        strong-edge survival.
  6. formula_family   — remove the single giant substitution component (the KU/SA/KI/A-RO deficit/
                        total ledger paradigm) and rebuild; does ANY strong sign-edge survive outside
                        the one dominant administrative family?

INFORMATION GAIN.  N clean syllabogram signs start as N singleton value-equivalence classes. IF each
anonymous REL_CLASS of k signs is a TRUE shared-feature series (one consonant-series or one vowel-
series), it merges k signs into 1 class, reducing the class count by (k-1). ΔEqClasses = n_covered -
n_classes, reported at both graph thresholds, with a bootstrap CI, and DEFLATED by the fraction of
edges that actually grade as feature-sharing on the disputed GORILA benchmark (honest expectation).

NON-CIRCULAR (Art. XII). Every rebuild consumes sign identity + frame membership + word-final
position ONLY. GORILA/LB (C,V) values are read AFTERWARD to GRADE the deflation, never as an input;
they earn no licence. Seed 20260708, pure stdlib + audited c1/c3/c4 primitives.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

MAIN_WT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, MAIN_WT)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import c1_substitution_candidates as c1   # noqa: E402
import c3_lb_calibration as c3            # noqa: E402
import c4_la_substitution_graph as c4     # noqa: E402

CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
SEGDIR = os.path.join(DATA, "segmentations")
SEED = 20260708
N_BOOT = 500
T_STRONG = 2          # C3 promotion rule: >=2 distinct long frames


# ============================================================ core graph builder (mirrors C4 exactly)
def build_sign_graph(types, sign_map=None):
    """From an iterable of word TYPES (tuples of sign tokens), build the C4 sign-substitution graph.

    sign_map: optional token->token remap applied to EVERY sign before analysis (encoding variant).
    Returns dict with:
      phon_edges  : {frozenset(a,b): {'w':long_frame_support,'nf':final_frames}}  (clean, non-allo)
      strong      : set(frozenset(a,b)) with w>=T_STRONG
      classes     : list[sorted list of signs]  (connected components of the strong graph)
      clean_signs : set of clean syllabogram signs present in >=1 word of length>=2
    """
    if sign_map is not None:
        types = [tuple(sign_map(s) for s in t) for t in types]
    types = list({t for t in types})            # distinct types (frames are over the type set)
    slots, long_slots = c4.build_frames_pos(types)
    ew_long, ew_long_final = c4.edge_weights_pos(long_slots)

    phon_edges = {}
    for e, w in ew_long.items():
        a, b = sorted(e)
        if not (c1.is_syllabogram(a) and c1.is_syllabogram(b)):
            continue
        if c1.allograph_related(a, b):
            continue
        phon_edges[e] = {"w": w, "nf": ew_long_final.get(e, 0)}

    strong = {e for e, d in phon_edges.items() if d["w"] >= T_STRONG}
    adj = defaultdict(set)
    for e in strong:
        a, b = sorted(e)
        adj[a].add(b)
        adj[b].add(a)
    seen, classes = set(), []
    for node in adj:
        if node in seen:
            continue
        stack, comp = [node], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adj[x] - seen)
        classes.append(sorted(comp))

    clean_signs = set()
    for t in types:
        if len(t) >= 2:
            for s in set(t):
                if c1.is_syllabogram(s):
                    clean_signs.add(s)
    return {"phon_edges": phon_edges, "strong": strong, "classes": classes,
            "clean_signs": clean_signs}


def class_of(classes):
    """sign -> frozenset(class members) map, for co-membership tests."""
    m = {}
    for c in classes:
        cs = frozenset(c)
        for s in c:
            m[s] = cs
    return m


def eqclass_reduction(classes):
    """ΔEqClasses if every REL_CLASS is a true shared-feature series: n_covered - n_classes."""
    n_cov = sum(len(c) for c in classes)
    n_cls = len(classes)
    return {"n_signs_covered": n_cov, "n_classes": n_cls, "delta_eqclasses": n_cov - n_cls}


# ============================================================ segmentation loaders
def seg_types(seg_name):
    """Load a B1 segmentation representation -> list of sign-tuples (units of length>=2 usable)."""
    path = os.path.join(SEGDIR, seg_name + ".json")
    d = json.load(open(path))
    out = []
    for u in d["units"]:
        sg = u.get("signs") or []
        out.append(tuple(sg))
    return out


# ============================================================ run
def run():
    os.makedirs(DATA, exist_ok=True)
    rng = random.Random(SEED)

    docs, occ, type_occ = c1.load_word_units()
    # per-document word-type inventory (bootstrap unit = document)
    doc_types = defaultdict(set)
    doc_site = {}
    for o in occ:
        doc_types[o["doc"]].add(o["type"])
        doc_site[o["doc"]] = o["site"]
    doc_ids = sorted(doc_types)
    all_types = list(type_occ)

    # ---- baseline graph (GORILA words, as-is encoding) ----
    base = build_sign_graph(all_types)
    base_edges = set(base["phon_edges"])
    base_strong = set(base["strong"])
    base_classes = base["classes"]
    N_clean = len(base["clean_signs"])
    base_red = eqclass_reduction(base_classes)
    # benchmark grading of baseline edges (FLAGGED, deflation only)
    def grade(e):
        a, b = sorted(e)
        return c3.relation(c1.desub(a), c1.desub(b))
    bench_all = Counter(grade(e) for e in base_edges)
    feat_all = sum(v for k, v in bench_all.items() if k in ("same_vowel", "same_consonant", "spelling_variant"))
    cross_all = bench_all.get("cross", 0)
    prec_feat = feat_all / (feat_all + cross_all) if (feat_all + cross_all) else 0.0
    bench_strong = Counter(grade(e) for e in base_strong)
    feat_strong = sum(v for k, v in bench_strong.items() if k in ("same_vowel", "same_consonant", "spelling_variant"))
    cross_strong = bench_strong.get("cross", 0)
    prec_feat_strong = feat_strong / (feat_strong + cross_strong) if (feat_strong + cross_strong) else 0.0

    # =========================================================== 1. BOOTSTRAP (documents)
    edge_hits = Counter()          # baseline clean edge -> # boot appearances
    strong_hits = Counter()        # baseline strong edge -> # boot appearances
    n_docs = len(doc_ids)
    # co-membership of baseline strong-classed sign pairs
    base_cls = class_of(base_classes)
    co_pairs = []
    for c in base_classes:
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                co_pairs.append(frozenset((c[i], c[j])))
    co_hits = Counter()
    boot_red_strong = []           # ΔEqClasses per bootstrap (strong graph)
    boot_n_strong = []
    for _ in range(N_BOOT):
        samp = [doc_ids[rng.randrange(n_docs)] for _ in range(n_docs)]
        tset = set()
        for did in set(samp):
            tset |= doc_types[did]
        g = build_sign_graph(list(tset))
        for e in g["phon_edges"]:
            if e in base_edges:
                edge_hits[e] += 1
        gstrong = g["strong"]
        for e in gstrong:
            if e in base_strong:
                strong_hits[e] += 1
        cm = class_of(g["classes"])
        for pr in co_pairs:
            a, b = tuple(pr)
            if cm.get(a) is not None and cm.get(a) == cm.get(b):
                co_hits[pr] += 1
        boot_red_strong.append(eqclass_reduction(g["classes"])["delta_eqclasses"])
        boot_n_strong.append(len(gstrong))

    def frac(cnt):
        return round(cnt / N_BOOT, 4)

    edge_recur = sorted(((round(edge_hits[e] / N_BOOT, 4), sorted(e)) for e in base_edges),
                        key=lambda z: -z[0])
    strong_recur = sorted((({"signs": sorted(e), "recurrence": frac(strong_hits[e]),
                             "w_long_frame": base["phon_edges"][e]["w"],
                             "benchmark_FLAGGED": grade(e)}) for e in base_strong),
                          key=lambda z: -z["recurrence"])
    co_recur = sorted(({"pair": sorted(pr), "co_membership_recurrence": frac(co_hits[pr])}
                       for pr in co_pairs), key=lambda z: -z["co_membership_recurrence"])
    # bootstrap CI of ΔEqClasses (strong graph)
    bs = sorted(boot_red_strong)
    ci = (bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1])
    boot_summary = {
        "n_boot": N_BOOT,
        "baseline_n_clean_edges": len(base_edges),
        "baseline_n_strong_edges": len(base_strong),
        "clean_edge_recurrence_ge_0.50": sum(1 for r, _ in edge_recur if r >= 0.50),
        "clean_edge_recurrence_ge_0.90": sum(1 for r, _ in edge_recur if r >= 0.90),
        "strong_edge_recurrence_ge_0.50": sum(1 for e in base_strong if strong_hits[e] / N_BOOT >= 0.50),
        "strong_edge_recurrence_ge_0.90": sum(1 for e in base_strong if strong_hits[e] / N_BOOT >= 0.90),
        "mean_strong_edge_recurrence": round(sum(strong_hits[e] for e in base_strong) / (N_BOOT * max(1, len(base_strong))), 4),
        "mean_co_membership_recurrence": round(sum(co_hits.values()) / (N_BOOT * max(1, len(co_pairs))), 4),
        "co_membership_recurrence_ge_0.50": sum(1 for pr in co_pairs if co_hits[pr] / N_BOOT >= 0.50),
        "n_co_pairs": len(co_pairs),
        "delta_eqclasses_baseline_strong": base_red["delta_eqclasses"],
        "delta_eqclasses_boot_mean": round(sum(boot_red_strong) / len(boot_red_strong), 3),
        "delta_eqclasses_boot_95CI": [ci[0], ci[1]],
        "n_strong_edges_boot_mean": round(sum(boot_n_strong) / len(boot_n_strong), 2),
    }

    # =========================================================== 2. SITE HOLDOUT (leave-one-site-out)
    sites = sorted(set(doc_site.values()))
    site_docs = defaultdict(list)
    for did, st in doc_site.items():
        site_docs[st].append(did)
    site_survive = Counter()       # baseline strong edge -> # LOSO runs it survives
    site_rows = []
    for st in sites:
        keep = [d for d in doc_ids if doc_site[d] != st]
        tset = set()
        for did in keep:
            tset |= doc_types[did]
        g = build_sign_graph(list(tset))
        surv = base_strong & g["strong"]
        for e in surv:
            site_survive[e] += 1
        site_rows.append({"held_out_site": st,
                          "docs_removed": len(site_docs[st]),
                          "n_strong_edges_remaining": len(g["strong"]),
                          "baseline_strong_edges_surviving": len(surv),
                          "delta_eqclasses": eqclass_reduction(g["classes"])["delta_eqclasses"]})
    site_rows.sort(key=lambda z: z["baseline_strong_edges_surviving"])
    n_sites = len(sites)
    site_summary = {
        "n_sites": n_sites,
        "strong_edge_survival_all_LOSO": sum(1 for e in base_strong if site_survive[e] == n_sites),
        "strong_edge_survival_ge_90pct_LOSO": sum(1 for e in base_strong if site_survive[e] >= 0.9 * n_sites),
        "mean_strong_survival_fraction": round(sum(site_survive[e] for e in base_strong) / (n_sites * max(1, len(base_strong))), 4),
        "worst_holdouts": site_rows[:5],
        "dominant_site_holdout": next(r for r in site_rows if r["held_out_site"] == "Haghia Triada"),
        "per_edge_survival": sorted(({"signs": sorted(e), "survives_n_of": site_survive[e],
                                      "of_sites": n_sites} for e in base_strong),
                                    key=lambda z: z["survives_n_of"]),
    }

    # =========================================================== 3. SEGMENTATION SENSITIVITY
    seg_names = ["SEG_GORILA_WORD", "SEG_ENTRY", "SEG_ROW", "SEG_FORMULA", "SEG_PROBABILISTIC_BOUNDARY"]
    seg_rows = []
    for nm in seg_names:
        try:
            types_seg = seg_types(nm)
        except FileNotFoundError:
            continue
        g = build_sign_graph(types_seg)
        e_seg = set(g["phon_edges"])
        s_seg = set(g["strong"])
        jac_clean = len(base_edges & e_seg) / len(base_edges | e_seg) if (base_edges | e_seg) else 0.0
        jac_strong = len(base_strong & s_seg) / len(base_strong | s_seg) if (base_strong | s_seg) else 0.0
        seg_rows.append({
            "segmentation": nm,
            "n_units": len(types_seg),
            "n_clean_edges": len(e_seg),
            "n_strong_edges": len(s_seg),
            "clean_edge_jaccard_vs_gorila": round(jac_clean, 4),
            "strong_edge_jaccard_vs_gorila": round(jac_strong, 4),
            "baseline_strong_edges_recovered": len(base_strong & s_seg),
            "delta_eqclasses": eqclass_reduction(g["classes"])["delta_eqclasses"],
        })

    # =========================================================== 4. ENCODING SENSITIVITY (allograph collapse)
    def collapse(s):
        return c1.allograph_base(s)
    g_enc = build_sign_graph(all_types, sign_map=collapse)
    # remap baseline edges to collapsed space to compare fairly
    def remap_edge(e):
        a, b = sorted(e)
        ca, cb = collapse(a), collapse(b)
        return frozenset((ca, cb)) if ca != cb else None
    base_edges_c = {re for re in (remap_edge(e) for e in base_edges) if re}
    base_strong_c = {re for re in (remap_edge(e) for e in base_strong) if re}
    enc_edges = set(g_enc["phon_edges"])
    enc_strong = set(g_enc["strong"])
    enc_summary = {
        "variant": "collapse numbered/lettered allographs to base sign before building",
        "n_clean_edges_collapsed": len(enc_edges),
        "n_strong_edges_collapsed": len(enc_strong),
        "baseline_clean_edges_after_remap": len(base_edges_c),
        "baseline_strong_edges_after_remap": len(base_strong_c),
        "clean_edge_jaccard": round(len(base_edges_c & enc_edges) / len(base_edges_c | enc_edges), 4) if (base_edges_c | enc_edges) else 0.0,
        "strong_edge_jaccard": round(len(base_strong_c & enc_strong) / len(base_strong_c | enc_strong), 4) if (base_strong_c | enc_strong) else 0.0,
        "strong_edges_preserved": len(base_strong_c & enc_strong),
        "delta_eqclasses_collapsed": eqclass_reduction(g_enc["classes"])["delta_eqclasses"],
    }

    # =========================================================== 5. DAMAGE EXCLUSION
    clean_types = [t for t in all_types if not any(c1.is_unidentified(s) for s in t)]
    g_dmg = build_sign_graph(clean_types)
    dmg_survive = base_strong & g_dmg["strong"]
    damage_summary = {
        "rule": "drop every word TYPE containing a *NNN / measure (unidentified) sign",
        "n_types_before": len(all_types),
        "n_types_after": len(clean_types),
        "n_types_dropped": len(all_types) - len(clean_types),
        "n_strong_edges_after": len(g_dmg["strong"]),
        "baseline_strong_edges_surviving": len(dmg_survive),
        "surviving_edges": [sorted(e) for e in sorted(dmg_survive, key=lambda z: sorted(z))],
        "lost_edges": [sorted(e) for e in sorted(base_strong - g_dmg["strong"], key=lambda z: sorted(z))],
        "delta_eqclasses": eqclass_reduction(g_dmg["classes"])["delta_eqclasses"],
    }

    # =========================================================== 6. FORMULA-FAMILY EXCLUSION
    # identify the single giant connected component over ALL single-sign substitution edges (C1 family)
    sub = c1.substitution_pairs(all_types)
    adj = defaultdict(set)
    for (t1, t2, _p) in sub:
        adj[t1].add(t2)
        adj[t2].add(t1)
    seen, comps = set(), []
    for node in adj:
        if node in seen:
            continue
        stack, comp = [node], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adj[x] - seen)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    giant = set(comps[0]) if comps else set()
    types_no_giant = [t for t in all_types if t not in giant]
    g_nf = build_sign_graph(types_no_giant)
    nf_survive = base_strong & g_nf["strong"]
    formula_summary = {
        "rule": "remove the single largest substitution component (the KU/SA/KI/A-RO deficit/total "
                "ledger paradigm) and rebuild",
        "giant_component_size_forms": len(giant),
        "n_types_after_removal": len(types_no_giant),
        "n_strong_edges_after": len(g_nf["strong"]),
        "baseline_strong_edges_surviving_outside_giant": len(nf_survive),
        "surviving_edges": [sorted(e) for e in sorted(nf_survive, key=lambda z: sorted(z))],
        "delta_eqclasses_outside_giant": eqclass_reduction(g_nf["classes"])["delta_eqclasses"],
    }

    # =========================================================== INFORMATION GAIN
    # loose graph = clean non-allo edges with w>=1 long frame (connected components)
    adjL = defaultdict(set)
    for e in base_edges:
        a, b = sorted(e)
        adjL[a].add(b)
        adjL[b].add(a)
    seen, loose_classes = set(), []
    for node in adjL:
        if node in seen:
            continue
        stack, comp = [node], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adjL[x] - seen)
        loose_classes.append(sorted(comp))
    loose_red = eqclass_reduction(loose_classes)

    def bits_model(delta, N, syllabary):
        """Toy value-assignment model: N signs each assigned a value from a syllabary of `syllabary`.
        Merging `delta` signs into shared-feature series removes `delta` free value choices among the
        covered signs (each merged sign is determined up to the vowel slot ~5). Report an OPTIMISTIC
        upper bound in bits: delta * log2(syllabary) fully-resolved, and a within-series residual
        (delta * log2(V=5) still free)."""
        upper = delta * math.log2(syllabary)
        residual_vowel = delta * math.log2(5)
        return {"optimistic_bits_upper": round(upper, 2),
                "within_series_residual_bits": round(residual_vowel, 2),
                "net_bits_if_series_fully_typed": round(upper - residual_vowel, 2)}

    N_syll = 92          # real working syllabary (memory: corrects the 259 category error)
    infogain = {
        "model": ("N clean syllabogram signs begin as N singleton value-equivalence classes. IF an "
                  "anonymous REL_CLASS of k signs is one TRUE shared-feature series it merges k signs "
                  "into 1 class: ΔEqClasses = n_signs_covered - n_classes. Reported at both graph "
                  "thresholds, bootstrap-CI'd, and DEFLATED by the fraction of edges that actually "
                  "grade as feature-sharing on the disputed GORILA benchmark."),
        "denominators": {
            "clean_syllabogram_signs_present": N_clean,
            "working_syllabary_estimate": N_syll,
        },
        "strong_graph_w_ge_2": {
            **base_red,
            "remaining_eqclasses_if_true": N_clean - base_red["delta_eqclasses"],
            "bootstrap_95CI_delta": boot_summary["delta_eqclasses_boot_95CI"],
            "bootstrap_mean_delta": boot_summary["delta_eqclasses_boot_mean"],
        },
        "loose_graph_w_ge_1": {
            **loose_red,
            "remaining_eqclasses_if_true": N_clean - loose_red["delta_eqclasses"],
        },
        "benchmark_deflation_FLAGGED": {
            "note": ("fraction of edges grading as feature-sharing (same_vowel/same_consonant/"
                     "spelling) vs cross, on the GORILA homomorphy this campaign DISPUTES; grades "
                     "only, earns no licence."),
            "strong_edges_composition": dict(bench_strong),
            "strong_edges_feature_precision": round(prec_feat_strong, 4),
            "all_clean_edges_composition": dict(bench_all),
            "all_clean_edges_feature_precision": round(prec_feat, 4),
            "deflated_expected_delta_strong": round(base_red["delta_eqclasses"] * prec_feat_strong, 3),
            "deflated_expected_delta_loose": round(loose_red["delta_eqclasses"] * prec_feat, 3),
        },
        "toy_bits_strong_optimistic": bits_model(base_red["delta_eqclasses"], N_clean, N_syll),
        "honesty": [
            "The C4 within-graph word-final null was NOT beaten by ANY REL_CLASS (best p=0.67); the "
            "graph shows no enrichment for the ONE axis C3 certified recoverable. ΔEqClasses is an "
            "'IF the relations are true' UPPER bound, not an earned reduction.",
            "The benchmark feature-precision is at/near the chance rate, so the DEFLATED expected "
            "gain is the honest figure; the optimistic ΔEqClasses assumes every edge is a real series.",
            "All edges descend from the single L_GORILA_VENTRIS transliteration lineage; the info "
            "gain is not independently corroborated (Art. XI single dependency cluster).",
        ],
    }

    # =========================================================== VERDICT
    stab_strong_recur = boot_summary["mean_strong_edge_recurrence"]
    stab_site = site_summary["mean_strong_survival_fraction"]
    seg_worst_strong = min((r["strong_edge_jaccard_vs_gorila"] for r in seg_rows
                            if r["segmentation"] != "SEG_GORILA_WORD"), default=None)
    verdict = {
        "stability": ("FRAGILE" if (stab_strong_recur < 0.5 or stab_site < 0.5) else
                      ("MODERATE" if stab_strong_recur < 0.8 else "STABLE")),
        "dominant_site_dependency": (
            "SEVERE (Haghia Triada holdout collapses the graph)"
            if site_summary["dominant_site_holdout"]["baseline_strong_edges_surviving"]
            <= 0.25 * len(base_strong) else "moderate"),
        "segmentation_robustness": ("FRAGILE" if (seg_worst_strong is not None and seg_worst_strong < 0.3)
                                    else "moderate"),
        "formula_family_dependency": (
            "TOTAL (no strong edge survives outside the one giant ledger paradigm)"
            if formula_summary["baseline_strong_edges_surviving_outside_giant"] == 0 else "partial"),
        "information_gain_if_true": base_red["delta_eqclasses"],
        "information_gain_deflated_honest": round(base_red["delta_eqclasses"] * prec_feat_strong, 3),
    }

    out = {
        "experiment": "C5_stability_and_information_gain",
        "seed": SEED, "n_boot": N_BOOT, "strong_threshold_long_frames": T_STRONG,
        "non_circular": ("every rebuild uses sign identity + frame membership + word-final position "
                         "only; GORILA/LB (C,V) values GRADE the deflation afterward, never an input."),
        "baseline": {
            "n_clean_syllabogram_signs": N_clean,
            "n_clean_edges": len(base_edges),
            "n_strong_edges": len(base_strong),
            "n_rel_classes": len(base_classes),
            "rel_classes": base_classes,
            "delta_eqclasses_if_true": base_red["delta_eqclasses"],
        },
        "stability_1_bootstrap": {**boot_summary,
                                  "strong_edge_recurrence": strong_recur,
                                  "co_membership_recurrence": co_recur,
                                  "clean_edge_recurrence_top": [{"recurrence": r, "signs": s}
                                                                for r, s in edge_recur[:25]]},
        "stability_2_site_holdout": site_summary,
        "stability_3_segmentation": seg_rows,
        "stability_4_encoding": enc_summary,
        "stability_5_damage_exclusion": damage_summary,
        "stability_6_formula_family_exclusion": formula_summary,
        "information_gain": infogain,
        "verdict": verdict,
    }
    outpath = os.path.join(DATA, "C5_stability.json")
    json.dump(out, open(outpath, "w"), indent=1, ensure_ascii=False)
    printable = {k: v for k, v in out.items()
                 if k not in ("stability_1_bootstrap", "stability_2_site_holdout")}
    printable["stability_1_bootstrap"] = boot_summary
    printable["stability_2_site_holdout"] = {k: v for k, v in site_summary.items()
                                             if k != "per_edge_survival"}
    print(json.dumps(printable, indent=1, ensure_ascii=False))
    print("\nWROTE", outpath, "(", os.path.getsize(outpath), "bytes )")
    return out


if __name__ == "__main__":
    run()
