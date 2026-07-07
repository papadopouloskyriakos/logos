#!/usr/bin/env python3
"""B6 — DOWNSTREAM CAUSAL SEGMENTATION TEST (Constitution v2.2 Art. VII/VIII/XII/XV).

QUESTION. Five candidate LINEAR A segmentations exist (GORILA word, ENTRY, FORMULA,
B5 probabilistic-boundary ensemble, INSCRIPTION_CONTEXT). Which one should downstream
relative-structure work FREEZE? We refuse to decide by LINEAR A internal fit — that is
circular (the segmentation search would be graded by the very corpus it was tuned on, and
LA carries no ground truth to catch over-fitting). Instead we CHARGE the segmentation search
against a HELD-OUT KNOWN SCRIPT: Linear B (DĀMOS), where the true (C,V) values and the true
word boundaries are known and can GRADE recovery (never an input — Art. XII).

CAUSAL DESIGN.
  * Each LA candidate embodies a segmentation STRATEGY (granularity + boundary placement).
  * We build the matched LB ANALOGUE of every strategy from the gold DĀMOS wordform streams:
        LB_WORD      (gold word boundaries)          <-> GORILA_WORD   (finest, editorial words)
        LB_ENTRY     (merge consecutive word pairs)  <-> ENTRY         (numeral-delimited groups)
        LB_FORMULA   (merge only RECURRENT pairs)    <-> FORMULA       (recurrent-sequence chunks)
        LB_ENSEMBLE  (branching-entropy induced)     <-> B5 ensemble   (unsupervised boundary vote)
        LB_CONTEXT   (whole-tablet, no word cuts)    <-> INSCRIPTION_CONTEXT (unsegmented)
  * On each LB analogue we run the SAME two downstream channels and GRADE against LB truth:
        (a) SUBSTITUTION / relative-class recovery — substitution-graph frame-weight AUC for
            same_consonant (the vocalic-alternation slot Greek inflection lives in) and for the
            word-final morphophonological class.
        (b) MORPHOLOGY recovery — paradigm-induction suffix precision against the TRUE inflectional
            ending signs (defined once from gold LB word-final same_consonant alternations).
  * The segmentation strategy that MAXIMISES held-out LB recovery is the causally-endorsed one;
    its LA counterpart is what LA work should freeze. Multiplicity: 5 candidates searched.
  * On the LA side we ALSO run both channels per segmentation, but only as ANONYMOUS descriptors
    (n edges, edge weight, affix productivity, freq-null p, cross-family agreement). These are
    LA-internal fit and DO NOT select — we report them and test whether LA-internal ranking would
    have picked the same segmentation LB recovery endorses (if not, LA-internal fit is untrustworthy).

NON-CIRCULAR. Every channel input is a pure distributional statistic over ANONYMOUS sign IDs.
LB values / true endings and LA pure-vowel identities are read AFTERWARD to GRADE only. No phonetic
value is assigned; highest layer L2/L3; licences NOT_EARNED. Deterministic seed 20260708.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
MAIN = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, MAIN)
sys.path.insert(0, CAMP)

from scripts.cross_script import data as X  # noqa: E402

# reuse the audited primitives from the sibling channel scripts (no re-implementation)
import importlib.util as _il


def _load(name, path):
    spec = _il.spec_from_file_location(name, path)
    mod = _il.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C3 = _load("c3mod", os.path.join(HERE, "c3_lb_calibration.py"))
E1 = _load("e1mod", os.path.join(HERE, "e1_morphology_models.py"))

SEGDIR = os.path.join(CAMP, "data", "segmentations")
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
SEED = 20260708
N_NULL = 200
PURE_VOWELS = {"A", "E", "I", "O", "U"}

# LA candidate segmentation files -> the LB analogue-strategy key they map to
LA_CANDIDATES = {
    "GORILA_WORD": ("SEG_GORILA_WORD.json", "LB_WORD"),
    "ENTRY": ("SEG_ENTRY.json", "LB_ENTRY"),
    "FORMULA": ("SEG_FORMULA.json", "LB_FORMULA"),
    "B5_ENSEMBLE": ("SEG_PROBABILISTIC_BOUNDARY.json", "LB_ENSEMBLE"),
    "INSCRIPTION_CONTEXT": ("SEG_INSCRIPTION_CONTEXT.json", "LB_CONTEXT"),
}


# ===================================================================== shared channel primitives
def subst_metrics(types):
    """Anonymous substitution-graph descriptors over a set/list of word-tuples (len>=2 used)."""
    types = list(dict.fromkeys(types))          # dedup, preserve order
    slots, long_slots = C3.build_frames(types)
    ew = C3.edge_weights(slots)
    ew_long = C3.edge_weights(long_slots)
    wmp = C3.word_minimal_pairs(types)
    weights = list(ew.values())
    return {
        "n_types": len(types),
        "n_types_ge2": sum(1 for t in types if len(t) >= 2),
        "n_subst_edges": len(ew),
        "n_longframe_edges": len(ew_long),
        "n_word_minimal_pairs": len(wmp),
        "mean_edge_weight": round(sum(weights) / len(weights), 3) if weights else 0.0,
        "n_strong_edges_ge2": sum(1 for w in weights if w >= 2),
        "_ew": ew, "_slots": slots, "_wmp": wmp, "_types": types,
    }


def subst_recovery_lb(types):
    """GRADED (LB values) substitution recovery: analysis-A method AUC for same_consonant &
    same_vowel & spelling_variant, plus word-final morphophonological method AUC vs cross pairs."""
    sm = subst_metrics(types)
    ew = sm["_ew"]
    # sign universe: signs that parse to a standard (C,V)
    sign_freq = Counter()
    for t in sm["_types"]:
        for s in set(t):
            sign_freq[s] += 1
    scorable = sorted(s for s in sign_freq if C3.parse_cv(s) is not None)
    from itertools import combinations
    rel_of = {}
    for a, b in combinations(scorable, 2):
        r = C3.relation(a, b)
        if r is not None:
            rel_of[frozenset((a, b))] = r
    # analysis-A: method weight AUC per relation (pos=relation, neg=every other scorable relation)
    def auc_for(target):
        pos, neg = [], []
        for e, r in rel_of.items():
            sc = ew.get(e, 0)
            if r == target:
                pos.append(sc)
            else:
                neg.append(sc)
        a = C3.auc(pos, neg)
        return (round(a, 4) if a is not None else None, len(pos), len(neg))
    reco = {}
    for t in ("same_consonant", "same_vowel", "spelling_variant"):
        a, npos, nneg = auc_for(t)
        reco[t + "_auc"] = a
        reco[t + "_npos"] = npos
    # word-final morphophonological: class vs cross among word minimal pairs, method = edge weight
    pos, neg = [], []
    for (t1, t2, p, sa, sb) in sm["_wmp"]:
        r = C3.relation(sa, sb)
        if r is None:
            continue
        w = ew.get(frozenset((sa, sb)), 0)
        final = (p == len(t1) - 1)
        if r == "same_consonant" and final:
            pos.append(w)
        elif r == "cross":
            neg.append(w)
    a = C3.auc(pos, neg)
    reco["morphophonological_final_auc"] = round(a, 4) if a is not None else None
    reco["morphophonological_final_npos"] = len(pos)
    reco["morphophonological_final_nneg"] = len(neg)
    reco["n_subst_edges"] = sm["n_subst_edges"]
    reco["n_word_minimal_pairs"] = sm["n_word_minimal_pairs"]
    return reco


def morph_recovery(words, true_endings):
    """paradigm-induction suffix precision@k against TRUE inflectional ending signs (grade only)."""
    para = E1.paradigm_induction(list(words))
    top_suf = list(para["suffixes"].keys())          # sorted by recurrent-stem productivity desc
    top_pre = list(para["prefixes"].keys())
    def prec_at(k):
        top = top_suf[:k]
        return round(sum(1 for s in top if s in true_endings) / k, 4) if top else 0.0
    return {
        "n_true_endings": len(true_endings),
        "top10_suffixes": top_suf[:10],
        "suffix_precision_at5": prec_at(5),
        "suffix_precision_at10": prec_at(10),
        "n_recovered_in_top10": sum(1 for s in top_suf[:10] if s in true_endings),
        "n_stem_families": para["n_stem_families"],
        "n_initial_alternation_stems": para["n_initial_alternation_stems"],
        "n_final_alternation_stems": para["n_final_alternation_stems"],
        "_top_suf": top_suf, "_top_pre": top_pre,
    }


# ===================================================================== LB analogue construction
def load_lb_tablets_ordered():
    """[(doc, [wordform_tuple,...]), ...] ordered wordforms per tablet."""
    occ, type_occ = C3.load_lb_tablets()
    by_doc = defaultdict(list)
    for o in occ:
        by_doc[o["doc"]].append((o["pos"], o["type"]))
    tablets = []
    for doc, lst in by_doc.items():
        lst.sort()
        tablets.append((doc, [w for _, w in lst]))
    return tablets


def lb_word(tablets):
    return [w for _, ws in tablets for w in ws]


def lb_entry(tablets):
    """merge consecutive wordform pairs (under-segmentation, ~x2 length)."""
    out = []
    for _, ws in tablets:
        i = 0
        while i < len(ws):
            if i + 1 < len(ws):
                out.append(tuple(ws[i]) + tuple(ws[i + 1]))
                i += 2
            else:
                out.append(tuple(ws[i]))
                i += 1
    return out


def lb_formula(tablets):
    """merge a consecutive pair only if that ordered wordform-bigram RECURS across >=2 tablets."""
    bigram_docs = defaultdict(set)
    for doc, ws in tablets:
        for i in range(len(ws) - 1):
            bigram_docs[(tuple(ws[i]), tuple(ws[i + 1]))].add(doc)
    recurrent = {b for b, docs in bigram_docs.items() if len(docs) >= 2}
    out = []
    for _, ws in tablets:
        i = 0
        while i < len(ws):
            if i + 1 < len(ws) and (tuple(ws[i]), tuple(ws[i + 1])) in recurrent:
                out.append(tuple(ws[i]) + tuple(ws[i + 1]))
                i += 2
            else:
                out.append(tuple(ws[i]))
                i += 1
    return out


def lb_context(tablets):
    """whole-tablet concatenation: one unit per tablet (max under-segmentation)."""
    return [tuple(s for w in ws for s in w) for _, ws in tablets if ws]


def lb_ensemble(tablets, target_mean_len=2.5):
    """Harris branching-entropy unsupervised re-segmentation of the concatenated tablet sign stream.

    Score every inter-sign gap by the forward branching entropy of its preceding context
    (Harris/Tanaka-Ishii); cut the highest-entropy gaps until the induced mean word length hits
    `target_mean_len`. target=2.5 places this in the SAME slightly-over-segmenting regime as LA's
    B5 probabilistic-boundary segmentation (which cuts finer than gold words), so the analogue is
    faithful in DIRECTION (unsupervised, over-cutting) not just in name. No truth used."""
    streams = [[s for w in ws for s in w] for _, ws in tablets if ws]
    succ = defaultdict(Counter)
    for st in streams:
        for i in range(len(st)):
            for k in (1, 2):
                if i - k >= 0:
                    ctx = tuple(st[i - k:i])
                    succ[ctx][st[i]] += 1
    def fwd_ent(ctx):
        c = succ.get(ctx)
        if not c:
            return None
        n = sum(c.values())
        return -sum((v / n) * math.log(v / n) for v in c.values())
    # collect every internal gap with a deterministic (entropy, tie-break) key
    gaps = []
    for si, st in enumerate(streams):
        for i in range(1, len(st)):
            ctx = tuple(st[max(0, i - 2):i])
            e = fwd_ent(ctx)
            if e is None:
                e = fwd_ent((st[i - 1],)) or 0.0
            gaps.append((e, si, i))
    total_signs = sum(len(st) for st in streams)
    target_units = max(len(streams), round(total_signs / target_mean_len))
    n_cuts = max(0, target_units - len(streams))
    gaps.sort(key=lambda g: (-g[0], g[1], g[2]))          # deterministic
    cut_at = defaultdict(set)
    for _, si, i in gaps[:n_cuts]:
        cut_at[si].add(i)
    words = []
    for si, st in enumerate(streams):
        cur = [st[0]] if st else []
        for i in range(1, len(st)):
            if i in cut_at[si]:
                words.append(tuple(cur)); cur = [st[i]]
            else:
                cur.append(st[i])
        if cur:
            words.append(tuple(cur))
    return words


def true_lb_endings(word_types):
    """signs appearing as the FINAL sign of a word-final same_consonant minimal pair (gold WORD).
    This is the set of genuine Mycenaean inflectional ending signs — GRADING TARGET ONLY."""
    wmp = C3.word_minimal_pairs(list(dict.fromkeys(word_types)))
    endings = set()
    for (t1, t2, p, sa, sb) in wmp:
        if p == len(t1) - 1 and C3.relation(sa, sb) == "same_consonant":
            endings.add(sa); endings.add(sb)
    return endings


# ===================================================================== LA descriptors
def la_words(segfile):
    units = json.load(open(os.path.join(SEGDIR, segfile)))["units"]
    return [tuple(u["signs"]) for u in units]


def la_descriptors(words):
    sm = subst_metrics(words)
    para = E1.paradigm_induction(list(words))
    # freq-matched null for the wave-2 headline affixes A- prefix and -JA suffix
    null = E1.freq_matched_null(list(words), ["A", "I"], ["JA"], n_null=N_NULL)
    mdl = E1.Morfessor(list(words)).train().emit()
    bayes = E1.bayesian_pss(list(words))
    agr = E1.agreement(mdl, bayes, para)
    top_pre = list(para["prefixes"].keys())[:6]
    return {
        "n_words": len(words),
        "n_types": len(set(words)),
        "subst": {k: v for k, v in sm.items() if not k.startswith("_")},
        "morph": {
            "top_prefixes": list(para["prefixes"].items())[:6],
            "top_suffixes": list(para["suffixes"].items())[:6],
            "A_prefix_productivity": para["prefixes"].get("A", 0),
            "I_prefix_productivity": para["prefixes"].get("I", 0),
            "JA_suffix_productivity": para["suffixes"].get("JA", 0),
            "A_prefix_null_p": null["prefix"]["A"]["p_ge"],
            "I_prefix_null_p": null["prefix"]["I"]["p_ge"],
            "JA_suffix_null_p": null["suffix"]["JA"]["p_ge"],
            "A_prefix_null_mean": null["prefix"]["A"]["null_mean"],
            "n_stem_families": para["n_stem_families"],
            "n_initial_alternation_stems": para["n_initial_alternation_stems"],
            "n_final_alternation_stems": para["n_final_alternation_stems"],
            "jaccard_bayes_para_prefixes": agr["prefixes"]["jaccard_bayes_para"],
            "jaccard_mdl_para_suffixes": agr["suffixes"]["jaccard_mdl_para"],
        },
        # GRADING (non-input): are the top induced prefixes pure vowels? (wave-2 signature check)
        "grading_noninput": {
            "top6_prefixes": top_pre,
            "frac_pure_vowel_prefix": round(sum(1 for s in top_pre if s in PURE_VOWELS) / len(top_pre), 3)
            if top_pre else 0.0,
        },
    }


# ===================================================================== main
def main():
    print("=== B6 downstream causal test ===")
    tablets = load_lb_tablets_ordered()
    print("LB tablets:", len(tablets), "wordform tokens:", sum(len(ws) for _, ws in tablets))

    lb_builders = {
        "LB_WORD": lb_word, "LB_ENTRY": lb_entry, "LB_FORMULA": lb_formula,
        "LB_ENSEMBLE": lb_ensemble, "LB_CONTEXT": lb_context,
    }
    lb_sets = {k: fn(tablets) for k, fn in lb_builders.items()}
    # TRUE endings defined ONCE from the gold WORD segmentation (grading constant)
    TRUE_ENDINGS = true_lb_endings(lb_sets["LB_WORD"])
    print("TRUE inflectional-ending signs (gold WORD):", len(TRUE_ENDINGS), sorted(TRUE_ENDINGS)[:20])

    lb_results = {}
    for k, words in lb_sets.items():
        mean_len = round(sum(len(w) for w in words) / len(words), 3) if words else 0.0
        reco_s = subst_recovery_lb(words)
        reco_m = morph_recovery(words, TRUE_ENDINGS)
        lb_results[k] = {
            "n_units": len(words), "n_types": len(set(words)), "mean_len_signs": mean_len,
            "substitution_recovery": reco_s,
            "morphology_recovery": {kk: vv for kk, vv in reco_m.items() if not kk.startswith("_")},
        }
        print(f"[LB] {k:12s} units={len(words):6d} types={len(set(words)):5d} meanlen={mean_len:5.2f} "
              f"sameC_auc={reco_s['same_consonant_auc']}(npos={reco_s['same_consonant_npos']}) "
              f"morphfin_auc={reco_s['morphophonological_final_auc']} "
              f"n_ma_final={reco_s['morphophonological_final_npos']} suf_p@10={reco_m['suffix_precision_at10']}")

    # ------------- LB recovery ranking + combined score (the CAUSAL CHARGE) -------------
    # PRIMARY recovery metric = DISCRIMINATION x STRUCTURE-VOLUME.
    #   discrimination = same_consonant analysis-A AUC (large, stable n_pos across segmentations:
    #                    the vocalic-alternation relative class the whole campaign turns on).
    #   volume         = # word-final morphophonological minimal pairs the segmentation still exposes,
    #                    normalised to the gold-WORD count. A segmentation that dissolves word
    #                    boundaries dissolves the known inflectional channel -> volume -> 0.
    # We deliberately DROP the word-final morphophonological AUC from the score (its n_pos swings
    # 116..788, so cross-segmentation AUC comparison is small-n-noise-inflated) and DROP suffix
    # precision@10 (58 true-ending signs ~= most of the syllabary -> non-discriminating). Both are
    # kept as reported diagnostics.
    vol_ref = lb_results["LB_WORD"]["substitution_recovery"]["morphophonological_final_npos"] or 1

    def score(r):
        s = r["substitution_recovery"]
        sc = s["same_consonant_auc"]
        sc = 0.5 if sc is None else sc
        vol = s["morphophonological_final_npos"] / vol_ref
        return round((sc - 0.5) * vol, 5)
    lb_score = {k: score(v) for k, v in lb_results.items()}
    lb_rank = sorted(lb_score, key=lambda k: -lb_score[k])
    endorsed_lb = lb_rank[0]

    # ------------- LA descriptors (anonymous, non-selecting) -------------
    la_results = {}
    for la_name, (segfile, _analogue) in LA_CANDIDATES.items():
        words = la_words(segfile)
        la_results[la_name] = la_descriptors(words)
        d = la_results[la_name]
        print(f"[LA] {la_name:20s} n={d['n_words']:5d} edges={d['subst']['n_subst_edges']:4d} "
              f"A_prod={d['morph']['A_prefix_productivity']:3d}(p={d['morph']['A_prefix_null_p']}) "
              f"JA_suf={d['morph']['JA_suffix_productivity']:3d} "
              f"frac_vowel_pre={d['grading_noninput']['frac_pure_vowel_prefix']}")

    # ------------- would LA-internal ranking pick the same segmentation? -------------
    # LA-internal candidate "quality" proxies (the kind of number an over-fitter would maximise):
    la_internal_proxy = {
        name: {
            "n_subst_edges": d["subst"]["n_subst_edges"],
            "A_prefix_productivity": d["morph"]["A_prefix_productivity"],
            "A_prefix_significant": d["morph"]["A_prefix_null_p"] < 0.05,
            "n_final_alternation_stems": d["morph"]["n_final_alternation_stems"],
        } for name, d in la_results.items()
    }
    la_rank_by_edges = sorted(la_results, key=lambda n: -la_results[n]["subst"]["n_subst_edges"])
    la_rank_by_Aprod = sorted(la_results, key=lambda n: -la_results[n]["morph"]["A_prefix_productivity"])

    analogue_of = {v[1]: k for k, v in LA_CANDIDATES.items()}
    endorsed_la = analogue_of[endorsed_lb]

    # spearman-ish agreement: does LB-recovery rank order match LA-internal edge-count order?
    lb_order = [analogue_of[k] for k in lb_rank]
    def rank_index(order):
        return {name: i for i, name in enumerate(order)}
    ri_lb = rank_index(lb_order)
    ri_edges = rank_index(la_rank_by_edges)
    ri_Aprod = rank_index(la_rank_by_Aprod)
    names = list(la_results)
    def spearman(a, b):
        import statistics
        n = len(names)
        d2 = sum((a[x] - b[x]) ** 2 for x in names)
        return round(1 - 6 * d2 / (n * (n * n - 1)), 4)
    rho_edges = spearman(ri_lb, ri_edges)
    rho_Aprod = spearman(ri_lb, ri_Aprod)

    verdict = {
        "endorsed_lb_strategy": endorsed_lb,
        "endorsed_la_segmentation": endorsed_la,
        "lb_recovery_rank": lb_rank,
        "lb_recovery_score": lb_score,
        "la_rank_by_edges": la_rank_by_edges,
        "la_rank_by_A_prefix_productivity": la_rank_by_Aprod,
        "spearman_lbrecovery_vs_la_edges": rho_edges,
        "spearman_lbrecovery_vs_la_Aprod": rho_Aprod,
        "segmentation_search_multiplicity": len(LA_CANDIDATES),
        "recovery_components": {
            k: {
                "same_consonant_auc": lb_results[k]["substitution_recovery"]["same_consonant_auc"],
                "n_morphophonological_final_pairs": lb_results[k]["substitution_recovery"]["morphophonological_final_npos"],
                "mean_len_signs": lb_results[k]["mean_len_signs"],
            } for k in lb_rank
        },
        "interpretation": (
            "The held-out KNOWN-SCRIPT (LB) recovery endorses "
            f"'{endorsed_lb}' -> LA '{endorsed_la}'. LA-internal edge-count and A-prefix "
            "productivity are reported as anonymous descriptors ONLY; their rank agreement with the "
            "LB-recovery ranking (spearman above) says whether an LA-internal search would have "
            "reached the same choice. Because C/V is refuted and LA carries no ground truth, the "
            "LA-internal peaks are NOT evidence; the segmentation to freeze is the one LB recovery "
            "charges."
        ),
    }

    out = {
        "experiment": "B6_downstream_causal_segmentation_test",
        "seed": SEED, "n_null": N_NULL,
        "non_circular": ("channel inputs are anonymous sign-distribution statistics; LB values / true "
                         "endings and LA pure-vowel identities grade recovery only, never an input."),
        "lb_analogue_recovery": lb_results,
        "la_internal_descriptors": la_results,
        "la_internal_proxy": la_internal_proxy,
        "true_lb_endings": sorted(TRUE_ENDINGS),
        "causal_verdict": verdict,
    }
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "B6.json"), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("\nWROTE", os.path.join(DATA, "B6.json"))
    print("\n=== CAUSAL VERDICT ===")
    print("LB recovery rank:", lb_rank, "scores:", lb_score)
    print("ENDORSED LB strategy:", endorsed_lb, "-> LA segmentation:", endorsed_la)
    print("LA rank by edges:", la_rank_by_edges)
    print("LA rank by A-prefix prod:", la_rank_by_Aprod)
    print("spearman(LBrecovery, LA edges):", rho_edges, " (LBrecovery, LA Aprod):", rho_Aprod)
    return out


if __name__ == "__main__":
    main()
