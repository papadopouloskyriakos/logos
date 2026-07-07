#!/usr/bin/env python3
"""C4 — LINEAR A SUBSTITUTION GRAPH (Constitution v2.2 Art. III/V/VII/XI/XII/XV).

GOAL. Build the Linear A substitution graph over GORILA word units and surface ANONYMOUS
relative classes (REL_CLASS_01, ...) that behave like the ONE axis C3 calibrated as trustworthy
on known-truth Linear B: the CONSONANT-HELD / vocalic-alternation axis (AUC 0.70-0.74, degree-
preserving lift up to 2.5x), which is best recovered when it is WORD-FINAL (morphophonological,
AUC 0.744) and by LONG >=3-sign formulaic frames.

NON-CIRCULAR (Art. XII). Graph construction and class formation consume sign IDENTITY, word-frame
membership, long-frame support, and WORD-FINAL position ONLY. No phonetic value is ever a model
INPUT. The GORILA/Linear-B-homomorphic (C,V) transliteration is read AFTERWARD, to GRADE a
benchmark only, and is heavily caveated (the homomorphy is the very channel the campaign disputes;
it earns no licence). The 5 known LA pure-vowel signs {A,E,I,O,U} likewise grade, never gate.

EDGE TYPES over word units:
  * single_sign_substitution  equal length, differ at exactly one position
  * allographic_candidate     single_sign_substitution whose differing signs are numbered/lettered
                              allographs of one base (RA/RA2, *21F/*21M): a spelling doublet, NOT a
                              phonological alternation (C3: DO NOT rank these by substitution weight)
  * prefix_alternation        one-sign insert/delete at the word-INITIAL boundary  (stem == long[1:])
  * suffix_alternation        one-sign insert/delete at the word-FINAL   boundary  (stem == long[:-1])
  * optional_sign             one-sign insert/delete MEDIALLY (0 < pos < L-1)
  * transposition             equal length, identical multiset, two ADJACENT signs swapped

EDGE WEIGHT = distinct LONG-frame (formulaic) support (C3: long >=3-sign frames are the best
scorer; raw pair count is not). For a single_sign_substitution edge the weight is the number of
DISTINCT >=3-sign word frames licensing the underlying sign substitution; for affix edges it is the
productivity of the affix (distinct long stems taking it); transpositions are counted separately.

DELIVERABLE. (1) graph structure: nodes / typed edges / connected-component ("alternation family")
+ strong-component structure; (2) the sign-substitution graph with anonymous REL_CLASSes, each
audited for the consonant-held signature: high long-frame support + WORD-FINAL concentration +
survival of a degree-preserving (Maslov-Sneppen) null + a permutation test that the weight ranking
actually selects word-final edges. C/V benchmark reported separately, flagged, load-bearing on
NOTHING.

Deterministic seed 20260708, pure stdlib + repo loader. Reuses audited c1 / c3 primitives.
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter, defaultdict
from itertools import combinations

MAIN = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, MAIN)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import c1_substitution_candidates as c1   # noqa: E402  (load_word_units, desub, is_syllabogram,
import c3_lb_calibration as c3             # noqa: E402   is_unidentified, allograph_related, ...)

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
SEED = 20260708
N_NULL = 300
N_PERM = 2000
TOPK = (20, 40, 80, 160)


# ------------------------------------------------------------------ position-aware long-frame edges
def build_frames_pos(types):
    """Return (slots, long_slots_posinfo).
      slots[(L,p,ctx)]      -> set of filler signs (ALL lengths; candidate generation)
      long_slots[(L,p,ctx)] -> set of filler signs for L>=3 only (>=2 real context signs = formula)
    """
    slots = defaultdict(set)
    long_slots = {}
    for t in types:
        L = len(t)
        if L < 2:
            continue
        for p in range(L):
            ctx = t[:p] + ("\x00",) + t[p + 1:]
            slots[(L, p, ctx)].add(t[p])
            if L >= 3:
                long_slots.setdefault((L, p, ctx), set()).add(t[p])
    return slots, long_slots


def edge_weights_pos(long_slots):
    """Per sign-pair: distinct long-frame support, and how many of those frames are WORD-FINAL.
    Returns ew_long{pair->n}, ew_long_final{pair->n_final}."""
    ew = Counter()
    ew_final = Counter()
    for (L, p, ctx), fills in long_slots.items():
        if len(fills) < 2:
            continue
        is_final = (p == L - 1)
        for a, b in combinations(sorted(fills), 2):
            e = frozenset((a, b))
            ew[e] += 1
            if is_final:
                ew_final[e] += 1
    return ew, ew_final


# ------------------------------------------------------------------ word-level typed edges
def transposition_pairs(typeset):
    """Equal-length pairs that are identical except two ADJACENT signs are swapped."""
    out = {}
    for t in typeset:
        L = len(t)
        if L < 2:
            continue
        for i in range(L - 1):
            if t[i] == t[i + 1]:
                continue
            t2 = t[:i] + (t[i + 1], t[i]) + t[i + 2:]
            if t2 in typeset and t2 != t:
                key = frozenset((t, t2))
                if key not in out:
                    out[key] = (t, t2, i)
    return list(out.values())


def affix_edges(indels):
    """Classify INDEL pairs by boundary and compute per-affix productivity (distinct long stems).
    indels: list of (long, short, del_pos, inserted_sign).
    Returns (edges, affix_support) where affix_support[(boundary,affix)] = # distinct long instances."""
    affix_support = defaultdict(set)          # (boundary,affix) -> set of stems (short forms), long only
    tagged = []
    for (tl, ts, p, ins) in indels:
        L = len(tl)
        if p == 0:
            boundary = "prefix"
        elif p == L - 1:
            boundary = "suffix"
        else:
            boundary = "optional"
        if L >= 3:                            # long instance (stem has >=2 signs)
            affix_support[(boundary, ins)].add(ts)
        tagged.append((tl, ts, p, ins, boundary))
    supp = {k: len(v) for k, v in affix_support.items()}
    return tagged, supp


# =========================================================================== run
def run():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(REPORTS, exist_ok=True)
    rng = random.Random(SEED)

    docs, occ, type_occ = c1.load_word_units()
    types = list(type_occ)
    typeset = set(types)
    type_freq = {t: len(type_occ[t]) for t in types}
    n_tokens = sum(type_freq.values())

    # ---- frames + long-frame edge weights (the C3-endorsed scorer) ----
    slots, long_slots = build_frames_pos(types)
    ew_long, ew_long_final = edge_weights_pos(long_slots)
    # raw pair count (any-length distinct frames) for comparison only
    ew_any = Counter()
    for (L, p, ctx), fills in slots.items():
        if len(fills) < 2:
            continue
        for a, b in combinations(sorted(fills), 2):
            ew_any[frozenset((a, b))] += 1

    # ---- word-level typed edges ----
    sub = c1.substitution_pairs(types)                 # (t1,t2,pos)
    ind = c1.indel_pairs(types)                        # (long,short,del_pos,inserted)
    trans = transposition_pairs(typeset)               # (t1,t2,i)
    aff_tagged, aff_supp = affix_edges(ind)

    word_edges = []
    edge_type_counts = Counter()
    allographic_count = 0
    for (t1, t2, p) in sub:
        sa, sb = t1[p], t2[p]
        allo = c1.allograph_related(sa, sb)
        etype = "allographic_candidate" if allo else "single_sign_substitution"
        edge_type_counts[etype] += 1
        allographic_count += int(allo)
        e = frozenset((sa, sb))
        word_edges.append({
            "type": etype, "A": list(t1), "B": list(t2), "pos": p,
            "diff_signs": [sa, sb],
            "w_long_frame": ew_long.get(e, 0),
            "w_long_frame_final": ew_long_final.get(e, 0),
            "w_raw_paircount": ew_any.get(e, 0),
            "both_clean": bool(c1.is_syllabogram(sa) and c1.is_syllabogram(sb)),
            "word_final": (p == len(t1) - 1),
        })
    for (tl, ts, p, ins, boundary) in aff_tagged:
        etype = {"prefix": "prefix_alternation", "suffix": "suffix_alternation",
                 "optional": "optional_sign"}[boundary]
        edge_type_counts[etype] += 1
        word_edges.append({
            "type": etype, "long": list(tl), "short": list(ts), "pos": p,
            "affix": ins, "boundary": boundary,
            "w_affix_productivity": aff_supp.get((boundary, ins), 0),
            "affix_clean": bool(c1.is_syllabogram(ins)),
        })
    for (t1, t2, i) in trans:
        edge_type_counts["transposition"] += 1
        word_edges.append({"type": "transposition", "A": list(t1), "B": list(t2),
                           "swap_pos": i, "freq": [type_freq[t1], type_freq[t2]]})

    # ---- WORD-level graph: connected components over single-sign-substitution edges ----
    adj = defaultdict(set)
    for (t1, t2, p) in sub:
        adj[t1].add(t2)
        adj[t2].add(t1)
    seen = set()
    families = []
    for node in adj:
        if node in seen:
            continue
        stack = [node]
        comp = []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adj[x] - seen)
        cs = set(comp)
        n_edges = sum(1 for (a, b, _) in sub if a in cs and b in cs)
        families.append({
            "size_forms": len(comp),
            "n_substitution_edges": n_edges,
            "total_tokens": sum(type_freq[c] for c in comp),
            "forms": ["-".join(c) for c in sorted(comp, key=lambda z: (-type_freq[z], z))][:24],
        })
    families.sort(key=lambda f: (-f["size_forms"], -f["total_tokens"]))
    singleton_nodes = sum(1 for t in types if len(t) >= 2 and t not in adj)
    comp_sizes = Counter(f["size_forms"] for f in families)

    # ====================================================================== SIGN graph -> REL_CLASSES
    # Nodes = clean syllabogram signs that participate in >=1 substitution frame.
    # Edges = sign-pairs that substitute in >=1 LONG frame, weighted by distinct long-frame support.
    sign_freq = Counter()
    for t in types:
        for s in set(t):
            sign_freq[s] += type_freq[t]

    sign_edges = {}          # frozenset(pair) -> dict
    for e, w in ew_long.items():
        a, b = sorted(e)
        clean = c1.is_syllabogram(a) and c1.is_syllabogram(b)
        allo = c1.allograph_related(a, b)
        nf = ew_long_final.get(e, 0)
        sign_edges[e] = {
            "signs": [a, b], "w_long_frame": w, "n_final_frames": nf,
            "final_fraction": round(nf / w, 4) if w else 0.0,
            "w_raw_paircount": ew_any.get(e, 0),
            "clean_syllabograms": bool(clean),
            "allographic": bool(allo),
        }
    # analysis restricts to CLEAN, non-allographic sign edges = the phonological-slot candidates
    phon_edges = {e: d for e, d in sign_edges.items()
                  if d["clean_syllabograms"] and not d["allographic"]}

    # ---- REL_CLASSES: connected components of the sign graph on edges with distinct long-frame
    #      support >= T (>=2 distinct long/formulaic frames = the C3 promotion rule) ----
    T = 2
    strong_phon = {e: d for e, d in phon_edges.items() if d["w_long_frame"] >= T}
    sadj = defaultdict(set)
    for e in strong_phon:
        a, b = sorted(e)
        sadj[a].add(b)
        sadj[b].add(a)
    seen = set()
    raw_classes = []
    for node in sadj:
        if node in seen:
            continue
        stack = [node]
        comp = []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(sadj[x] - seen)
        raw_classes.append(sorted(comp))

    def class_stats(signs):
        S = set(signs)
        ces = [d for e, d in strong_phon.items() if set(d["signs"]) <= S]
        tot_w = sum(d["w_long_frame"] for d in ces)
        tot_final = sum(d["n_final_frames"] for d in ces)
        return ces, tot_w, tot_final

    # order classes by aggregate long-frame support then word-final fraction; assign anon labels
    scored = []
    for signs in raw_classes:
        ces, tot_w, tot_final = class_stats(signs)
        ff = tot_final / tot_w if tot_w else 0.0
        scored.append((signs, ces, tot_w, tot_final, ff))
    scored.sort(key=lambda z: (-z[2], -z[4], -len(z[0])))

    # ---- degree-preserving null (benchmark same_consonant enrichment) + value-free final permutation
    # C/V benchmark grading (FLAGGED, non-circular): read the disputed GORILA homomorphic values.
    def rel_bench(a, b):
        r = c3.relation(c1.desub(a), c1.desub(b))
        return r

    rel_of = {}
    for e, d in phon_edges.items():
        a, b = d["signs"]
        r = rel_bench(a, b)
        if r is not None:
            rel_of[e] = r
    bench_counts = Counter(rel_of.values())

    # strong-edge lists ranked by long-frame weight (the promotion rule under audit)
    ranked = sorted(phon_edges, key=lambda e: -phon_edges[e]["w_long_frame"])

    # ---------- (1) degree-preserving Maslov-Sneppen null : same_consonant benchmark enrichment ----
    def rel_rate_bench(edge_set, target):
        hit = tot = 0
        for e in edge_set:
            r = rel_of.get(e)
            if r is None:
                continue
            tot += 1
            if target == "any_phon":
                hit += (r in ("same_vowel", "same_consonant", "spelling_variant"))
            else:
                hit += (r == target)
        return (hit / tot if tot else 0.0), tot

    graded_edges = [tuple(e) for e in rel_of]
    null_sweep = []
    for k in TOPK:
        top_ranked = [e for e in ranked if e in rel_of][:k]
        if len(top_ranked) < k:
            continue
        top = set(top_ranked)
        el = [tuple(e) for e in top]
        null_sets = [c3.rewire(el, rng) for _ in range(N_NULL)]
        row = {"top_k_edges": k}
        for target in ["any_phon", "same_vowel", "same_consonant"]:
            obs, tot = rel_rate_bench(top, target)
            nulls = [rel_rate_bench(ns, target)[0] for ns in null_sets]
            mu = sum(nulls) / len(nulls)
            sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
            p = (sum(1 for x in nulls if x >= obs) + 1) / (len(nulls) + 1)
            row[target] = {"obs_rate": round(obs, 4), "null_mean": round(mu, 4),
                           "null_sd": round(sd, 4),
                           "lift": round(obs / mu, 3) if mu else None,
                           "z": round((obs - mu) / sd, 2) if sd > 0 else None,
                           "p": round(p, 4), "n_scored": tot}
        null_sweep.append(row)

    # ---------- (2) VALUE-FREE permutation: does the weight ranking select WORD-FINAL edges? ----
    # positives = top-k edges by long-frame weight; statistic = mean final_fraction; null = shuffle
    # final_fraction labels across ALL clean phon edges. Tests the promotion rule structurally.
    all_ff = [phon_edges[e]["final_fraction"] for e in phon_edges]
    weight_perm = []
    perm_rng = random.Random(SEED + 1)
    for k in TOPK:
        if k > len(ranked):
            continue
        obs = sum(phon_edges[e]["final_fraction"] for e in ranked[:k]) / k
        cnt = 0
        for _ in range(N_PERM):
            samp = perm_rng.sample(all_ff, k)
            if (sum(samp) / k) >= obs:
                cnt += 1
        p = (cnt + 1) / (N_PERM + 1)
        weight_perm.append({"top_k_edges": k, "obs_mean_final_fraction": round(obs, 4),
                            "null_mean_final_fraction": round(sum(all_ff) / len(all_ff), 4),
                            "p_value": round(p, 4)})

    # ---------- assemble REL_CLASSES with per-class audit ----------
    # per-class degree-preserving lift for the class's own edges: is the class's word-final
    # concentration above a within-graph rewired null of the same edge count?
    def class_final_lift(ces):
        if not ces:
            return None
        el = [tuple(frozenset(d["signs"])) for d in ces]
        obs = sum(d["n_final_frames"] for d in ces) / max(1, sum(d["w_long_frame"] for d in ces))
        # null: sample same number of edges from full phon graph, weight-matched final fraction
        pool = list(phon_edges.values())
        nrng = random.Random(SEED + 7)
        nulls = []
        for _ in range(N_NULL):
            samp = nrng.sample(pool, min(len(ces), len(pool)))
            w = sum(d["w_long_frame"] for d in samp)
            f = sum(d["n_final_frames"] for d in samp)
            nulls.append(f / w if w else 0.0)
        mu = sum(nulls) / len(nulls)
        sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
        p = (sum(1 for x in nulls if x >= obs) + 1) / (len(nulls) + 1)
        return {"obs_final_fraction": round(obs, 4), "null_mean": round(mu, 4),
                "lift": round(obs / mu, 3) if mu else None,
                "z": round((obs - mu) / sd, 2) if sd > 0 else None, "p": round(p, 4)}

    rel_classes = []
    for i, (signs, ces, tot_w, tot_final, ff) in enumerate(scored, 1):
        edges_out = sorted(ces, key=lambda d: -d["w_long_frame"])
        # benchmark composition (FLAGGED, grading only)
        bc = Counter()
        for d in ces:
            r = rel_of.get(frozenset(d["signs"]))
            bc[r if r else "unscored"] += 1
        involves_vowel = sorted(s for s in signs if c1.desub(s) in {"A", "E", "I", "O", "U"})
        lift = class_final_lift(ces) if tot_w > 0 else None
        # verdict: consonant-held ANALOGUE signature = strong long-frame support + word-final
        #          concentration that beats the within-graph null (value-free)
        if tot_w >= 4 and ff >= 0.5 and lift and lift["p"] <= 0.10:
            verdict = "CANDIDATE_CONSONANT_HELD_ANALOGUE"
        elif tot_w >= 4 and ff >= 0.5:
            verdict = "WORD_FINAL_BUT_NULL_NOT_BEATEN"
        elif tot_w < 4:
            verdict = "UNDERPOWERED"
        else:
            verdict = "NOT_WORD_FINAL_DOMINANT"
        rel_classes.append({
            "rel_class": "REL_CLASS_%02d" % i,
            "signs": signs, "n_signs": len(signs), "n_edges": len(ces),
            "aggregate_long_frame_support": tot_w,
            "final_frame_support": tot_final,
            "word_final_fraction": round(ff, 4),
            "edges": [{"signs": d["signs"], "w_long_frame": d["w_long_frame"],
                       "n_final_frames": d["n_final_frames"],
                       "final_fraction": d["final_fraction"]} for d in edges_out],
            "within_graph_final_null": lift,
            "verdict": verdict,
            "BENCHMARK_cv_composition_FLAGGED": dict(bc),
            "BENCHMARK_involves_known_vowel_sign": involves_vowel,
        })

    # top strong sign-substitution edges overall (for the report)
    top_edges = [dict(rank=r + 1, **{k: sign_edges[e][k] for k in
                 ("signs", "w_long_frame", "n_final_frames", "final_fraction",
                  "w_raw_paircount", "clean_syllabograms", "allographic")},
                 BENCHMARK_relation_FLAGGED=rel_bench(*sign_edges[e]["signs"]))
                 for r, e in enumerate(sorted(sign_edges, key=lambda e: -sign_edges[e]["w_long_frame"])[:30])]

    # productive affixes (secondary structure)
    prod_affix = sorted(({"boundary": b, "affix": a, "distinct_long_stems": n,
                          "clean": bool(c1.is_syllabogram(a))}
                         for (b, a), n in aff_supp.items() if n >= 3),
                        key=lambda z: -z["distinct_long_stems"])

    out = {
        "experiment": "C4_linear_a_substitution_graph",
        "seed": SEED, "n_null": N_NULL, "n_perm": N_PERM,
        "non_circular": ("graph + REL_CLASS formation use sign identity, frame membership, long-frame "
                         "support and WORD-FINAL position only; GORILA/LB homomorphic (C,V) values "
                         "read AFTERWARD to GRADE a flagged benchmark, never as an input; earns no licence."),
        "corpus": {"word_tokens": n_tokens, "word_types": len(types),
                   "types_len_ge2": sum(1 for t in types if len(t) >= 2),
                   "documents": len(docs),
                   "distinct_signs": len(sign_freq),
                   "clean_syllabogram_signs": sum(1 for s in sign_freq if c1.is_syllabogram(s))},
        "word_graph": {
            "edge_type_counts": dict(edge_type_counts),
            "n_word_edges": len(word_edges),
            "single_sign_substitution_pairs": len(sub),
            "of_which_allographic": allographic_count,
            "indel_pairs": len(ind),
            "transposition_pairs": len(trans),
            "connected_components_over_substitution": len(families),
            "component_size_distribution": dict(sorted(comp_sizes.items())),
            "singleton_len_ge2_nodes_no_sub_edge": singleton_nodes,
            "largest_components": families[:20],
        },
        "sign_substitution_graph": {
            "n_sign_edges_long": len(sign_edges),
            "n_clean_nonallographic_edges": len(phon_edges),
            "n_strong_edges_ge2_longframes": len(strong_phon),
            "top_edges": top_edges,
            "benchmark_relation_counts_FLAGGED": dict(bench_counts),
        },
        "rel_classes": rel_classes,
        "audits": {
            "degree_preserving_null_sweep_BENCHMARK_cv": null_sweep,
            "weight_selects_wordfinal_permutation_VALUEFREE": weight_perm,
        },
        "productive_affixes_secondary": prod_affix[:25],
        "caveats": [
            "L2/L3 relative structure only; no phonetic value assigned or transferred (Art. XV; "
            "SEMANTIC+ NOT_AUTHORIZED).",
            "The C/V benchmark reads the GORILA Linear-B-homomorphic transliteration, the exact "
            "channel this campaign disputes; it GRADES, never gates, and earns no licence.",
            "C3 flagged INDEL/affix edges as affixation-confounded and allographs as anti-recovered "
            "by weight; REL_CLASSes are built ONLY from clean non-allographic sign substitutions.",
            "Single dependency cluster L_GORILA_VENTRIS: signs and segmentation both descend from one "
            "transliteration lineage; no independent channel corroborates these contrasts.",
        ],
    }
    outpath = os.path.join(DATA, "C_la_graph.json")
    json.dump(out, open(outpath, "w"), indent=1, ensure_ascii=False)
    printable = {k: v for k, v in out.items() if k not in ("rel_classes",)}
    printable["rel_classes_summary"] = [
        {"rel_class": r["rel_class"], "signs": r["signs"], "agg_w": r["aggregate_long_frame_support"],
         "wf_frac": r["word_final_fraction"], "verdict": r["verdict"],
         "null": r["within_graph_final_null"]} for r in rel_classes]
    print(json.dumps(printable, indent=1, ensure_ascii=False)[:9000])
    print("\nWROTE", outpath, "(", os.path.getsize(outpath), "bytes )")
    return out


if __name__ == "__main__":
    run()
