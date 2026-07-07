#!/usr/bin/env python3
"""C3 — LINEAR B SUBSTITUTION CALIBRATION (Constitution v2.2 Art. III/VII/VIII/XII).

QUESTION. The C1 candidate-generation (word-level one-sign minimal pairs in matched contexts)
plus a substitution-GRAPH weight (how many independent word-frames license a given sign
substitution) is a RELATIVE-STRUCTURE detector. Before trusting any relation type it surfaces on
Linear A, we must know WHICH relation types it can actually recover on a KNOWN script. So we run the
identical machinery on opaque Linear B (DĀMOS, 13,562 syllabic wordforms) and ask, per relation
type, how well the method separates the true relation from controls — using Linear B phonetic VALUES
ONLY to GRADE (never as a detector input; Art. XII).

RELATION TYPES graded from LB values:
  * same_vowel      — differing signs share the VOWEL, differ in consonant (PA/TA, RO/TO): a
                      consonantal contrast in a fixed vocalic slot.
  * same_consonant  — differing signs share the CONSONANT, differ in vowel (RO/RA, TO/TA):
                      the vocalic-alternation slot (Greek inflection lives here).
  * spelling_variant— differing signs are the SAME value modulo an allograph digit (RA/RA2,
                      A/A2, PA/PA3, PU/PU2): a known orthographic doublet, not a new value.
  * morphophonological — same_consonant AND word-FINAL: the classic Mycenaean case/gender
                      endings (-jo/-ja/-je, -to/-ta, -no/-na, -o/-a).
  * scribal_error / cross — differing signs share NEITHER feature and are not allographs: a
                      minimal pair that is either a scribal slip or two unrelated lexemes. This is
                      the class the method SHOULD NOT be able to promote (an honesty check).

BASELINES (each a rival scorer over the SAME universe):
  * frequency-matched random  — score = freq[a]*freq[b] (chance co-incidence of two signs); the
                      "did the method just recover frequency?" control. Also the negative pool for
                      the word-pair analysis is frequency-matched random word pairs.
  * edit-distance    — unweighted candidate generation: does the pair substitute in ANY frame
                      (binary edge existence, weight>=1); no graph weighting.
  * context-only     — pure distributional similarity (cosine of the two signs' in-word neighbour
                      vectors); ignores minimal-pair structure entirely.
  * formula-only     — restrict the substitution weight to LONG (context length>=2) frames only:
                      substitutions licensed by an extended fixed (formulaic) context.

METHOD = substitution-graph context WEIGHT (distinct word-frames licensing the substitution).

NULL = degree-preserving double-edge-swap (Maslov–Sneppen) on the sign substitution graph: rewire
preserving each sign's degree, recompute the same-relation rate among the strong edges -> lift, z, p.
Controls for hubbiness / base rate.

Deterministic, seed 20260708, pure stdlib + the repo data loader.
"""
from __future__ import annotations

import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations

MAIN = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
DAMOS_ITEMS = os.path.join(MAIN, "corpus", "bronze", "linearb", "damos", "items.jsonl")

SEED = 20260708
N_NULL = 300           # >= 200 mandated
VOW = set("AEIOU")
TOPK = (20, 40, 80, 160, 320)   # strong-edge cutoffs for the degree-preserving-null sweep


# --------------------------------------------------------------------------- value parse (GRADE ONLY)
def parse_cv(v):
    """Standard LB value -> (consonant, vowel). Pure vowel -> ('',V). *NN/non-standard -> None."""
    if v.startswith("*"):
        return None
    if v in VOW:
        return ("", v)
    if len(v) >= 2 and v[-1] in VOW and v[:-1].isalpha():
        return (v[:-1], v[-1])
    if len(v) >= 2 and v[-1].isdigit():          # allograph digit: RA2, A2, PA3
        core = v[:-1]
        if core in VOW:
            return ("", core)
        if len(core) >= 2 and core[-1] in VOW and core[:-1].isalpha():
            return (core[:-1], core[-1])
    return None


def core_value(v):
    """Strip a trailing allograph digit: RA2->RA, A2->A, PA3->PA. Identity otherwise."""
    if v.startswith("*"):
        return v
    return re.sub(r"\d+$", "", v)


def relation(a, b):
    """Graded relation of an ORDERED-agnostic sign pair (a!=b). None if unscorable."""
    pa, pb = parse_cv(a), parse_cv(b)
    if pa is None or pb is None:
        return None                              # damage / *NN -> excluded (like C1 damage tag)
    if core_value(a) == core_value(b):
        return "spelling_variant"                # allograph doublet (same value)
    ca, va = pa
    cb, vb = pb
    if va == vb:
        return "same_vowel"                      # vowel held, consonant differs
    if ca and cb and ca == cb:
        return "same_consonant"                  # consonant held, vowel differs
    return "cross"                               # scribal-error / unrelated candidate


# --------------------------------------------------------------------------- load LB with structure
def load_lb_tablets():
    """Per-tablet ORDERED syllabic wordform streams -> occurrences with neighbour context."""
    occ = []
    type_occ = defaultdict(list)
    with open(DAMOS_ITEMS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            did = rec.get("_id")
            content = (rec.get("item", {}) or {}).get("content", "") or ""
            words = X._damos_wordforms(content)          # ordered wordforms (value lists)
            words = [tuple(w) for w in words]
            for i, w in enumerate(words):
                prev = words[i - 1] if i > 0 else None
                nxt = words[i + 1] if i + 1 < len(words) else None
                o = {"type": w, "doc": did, "pos": i, "prev": prev, "next": nxt}
                occ.append(o)
                type_occ[w].append(len(occ) - 1)
    return occ, type_occ


# --------------------------------------------------------------------------- substitution frames / graph
def build_frames(types):
    """slots[(len,pos,ctx)] = set of filler signs; also flag long frames (ctx has >=2 real signs)."""
    slots = defaultdict(set)
    long_slots = defaultdict(set)
    for t in types:
        L = len(t)
        if L < 2:
            continue
        for p in range(L):
            ctx = t[:p] + ("\x00",) + t[p + 1:]
            slots[(L, p, ctx)].add(t[p])
            if L >= 3:                              # >=2 real context signs => "formula" frame
                long_slots[(L, p, ctx)].add(t[p])
    return slots, long_slots


def edge_weights(slots):
    """edge{a,b} -> number of DISTINCT frames licensing the a/b substitution."""
    ew = Counter()
    for fills in slots.values():
        if len(fills) < 2:
            continue
        for a, b in combinations(sorted(fills), 2):
            ew[frozenset((a, b))] += 1
    return ew


def word_minimal_pairs(types):
    """All equal-length word-type pairs differing at exactly one position.
    Returns list of (t1,t2,pos,signA,signB)."""
    by_key = defaultdict(list)
    for t in types:
        L = len(t)
        if L < 2:
            continue
        for p in range(L):
            ctx = t[:p] + ("\x00",) + t[p + 1:]
            by_key[(L, p, ctx)].append((t, t[p]))
    seen = set()
    out = []
    for (L, p, ctx), members in by_key.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                t1, f1 = members[i]
                t2, f2 = members[j]
                if f1 == f2:
                    continue
                key = frozenset((t1, t2))
                if key in seen:
                    continue
                seen.add(key)
                out.append((t1, t2, p, f1, f2))
    return out


# --------------------------------------------------------------------------- context vectors (context-only baseline)
def sign_neighbour_vectors(type_occ):
    """sign -> Counter of in-word immediate-neighbour signs (token-weighted)."""
    vec = defaultdict(Counter)
    for t, idxs in type_occ.items():
        n = len(idxs)                              # token multiplicity of this type
        for k in range(len(t)):
            s = t[k]
            if k > 0:
                vec[s][t[k - 1]] += n
            if k + 1 < len(t):
                vec[s][t[k + 1]] += n
    norm = {s: math.sqrt(sum(v * v for v in c.values())) for s, c in vec.items()}
    return vec, norm


def cosine(vec, norm, a, b):
    if a not in vec or b not in vec or norm.get(a, 0) == 0 or norm.get(b, 0) == 0:
        return 0.0
    ca, cb = vec[a], vec[b]
    small, big = (ca, cb) if len(ca) <= len(cb) else (cb, ca)
    dot = sum(v * big.get(k, 0) for k, v in small.items())
    return dot / (norm[a] * norm[b])


# --------------------------------------------------------------------------- AUC
def auc(pos_scores, neg_scores):
    """Mann–Whitney AUC = P(score(pos) > score(neg)) + 0.5 ties. O((n+m) log)."""
    if not pos_scores or not neg_scores:
        return None
    allv = sorted(set(pos_scores) | set(neg_scores))
    # rank via counts
    neg_sorted = sorted(neg_scores)
    import bisect
    m = len(neg_scores)
    tot = 0.0
    for s in pos_scores:
        lo = bisect.bisect_left(neg_sorted, s)
        hi = bisect.bisect_right(neg_sorted, s)
        less = lo                     # negatives strictly below s
        eq = hi - lo
        tot += less + 0.5 * eq
    return tot / (len(pos_scores) * m)


# --------------------------------------------------------------------------- degree-preserving null
def rewire(edge_list, rng, mult=8):
    edges = [list(e) for e in edge_list]
    eset = set(frozenset(e) for e in edges)
    E = len(edges)
    if E < 2:
        return eset
    target = mult * E
    swaps = attempts = 0
    while swaps < target and attempts < target * 12:
        attempts += 1
        i = rng.randrange(E); j = rng.randrange(E)
        if i == j:
            continue
        a, b = edges[i]; c, d = edges[j]
        if rng.random() < 0.5:
            c, d = d, c
        if len({a, b, c, d}) < 4:
            continue
        if frozenset((a, d)) in eset or frozenset((c, b)) in eset:
            continue
        eset.discard(frozenset((a, b))); eset.discard(frozenset((c, d)))
        edges[i] = [a, d]; edges[j] = [c, b]
        eset.add(frozenset((a, d))); eset.add(frozenset((c, b)))
        swaps += 1
    return eset


def rel_rate(edge_set, rel_of, target):
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


# =========================================================================== run
def run():
    os.makedirs(DATA, exist_ok=True)
    rng = random.Random(SEED)

    occ, type_occ = load_lb_tablets()
    types = list(type_occ)
    type_freq = {t: len(type_occ[t]) for t in types}
    sign_freq = Counter()
    for t in types:
        for s in set(t):
            sign_freq[s] += type_freq[t]
    n_tokens = sum(type_freq.values())

    slots, long_slots = build_frames(types)
    ew = edge_weights(slots)                 # method weight
    ew_long = edge_weights(long_slots)       # formula-only weight
    exist = {e: 1 for e in ew}               # edit-distance / candidate-generation baseline
    vec, norm = sign_neighbour_vectors(type_occ)

    # -------- scorable sign universe: both signs parse to a standard (C,V) --------
    scorable_signs = sorted(s for s in sign_freq if parse_cv(s) is not None)
    sign_pairs = list(combinations(scorable_signs, 2))
    rel_of = {}
    for a, b in sign_pairs:
        r = relation(a, b)
        if r is not None:
            rel_of[frozenset((a, b))] = r

    # -------- Analysis A: sign-pair recovery AUC per scorer per relation --------
    scorers = {
        "method_substgraph_weight": lambda e, a, b: ew.get(e, 0),
        "baseline_frequency": lambda e, a, b: sign_freq[a] * sign_freq[b],
        "baseline_editdistance_exist": lambda e, a, b: exist.get(e, 0),
        "baseline_context_cosine": lambda e, a, b: cosine(vec, norm, a, b),
        "baseline_formula_longframe": lambda e, a, b: ew_long.get(e, 0),
    }
    rel_targets = ["same_vowel", "same_consonant", "spelling_variant", "any_phon"]
    # precompute per-pair scores
    pair_scores = {name: {} for name in scorers}
    pair_rel = {}
    for a, b in sign_pairs:
        e = frozenset((a, b))
        r = rel_of.get(e)
        pair_rel[e] = r
        for name, fn in scorers.items():
            pair_scores[name][e] = fn(e, a, b)

    def is_pos(r, target):
        if r is None:
            return None
        if target == "any_phon":
            if r in ("same_vowel", "same_consonant", "spelling_variant"):
                return True
            if r == "cross":
                return False
            return None
        if r == target:
            return True
        # negatives = every OTHER scorable relation (incl. cross)
        return False

    counts_rel = Counter(r for r in rel_of.values())
    analysisA = {"scorable_signs": len(scorable_signs),
                 "scorable_sign_pairs": len(rel_of),
                 "relation_counts": dict(counts_rel),
                 "auc": {}}
    for target in rel_targets:
        analysisA["auc"][target] = {}
        for name in scorers:
            pos = [pair_scores[name][e] for e, r in pair_rel.items()
                   if is_pos(r, target) is True]
            neg = [pair_scores[name][e] for e, r in pair_rel.items()
                   if is_pos(r, target) is False]
            a = auc(pos, neg)
            analysisA["auc"][target][name] = {
                "auc": round(a, 4) if a is not None else None,
                "n_pos": len(pos), "n_neg": len(neg)}

    # -------- degree-preserving null: strong-edge lift per relation --------
    graded_edges = [tuple(e) for e in rel_of]           # scorable sign edges that EXIST as substitutions
    graded_edges = [e for e in graded_edges if frozenset(e) in ew]
    # rank by method weight
    ranked = sorted(graded_edges, key=lambda e: -ew[frozenset(e)])
    null_sweep = []
    for k in TOPK:
        if k > len(ranked):
            continue
        top = set(frozenset(e) for e in ranked[:k])
        row = {"top_k_edges": k}
        el = [tuple(e) for e in top]
        null_sets = [rewire(el, rng) for _ in range(N_NULL)]
        for target in ["any_phon", "same_vowel", "same_consonant"]:
            obs, tot = rel_rate(top, rel_of, target)
            nulls = [rel_rate(ns, rel_of, target)[0] for ns in null_sets]
            mu = sum(nulls) / len(nulls)
            sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
            p = (sum(1 for x in nulls if x >= obs) + 1) / (len(nulls) + 1)
            row[target] = {"obs_rate": round(obs, 4), "null_mean": round(mu, 4),
                           "null_sd": round(sd, 4),
                           "lift": round(obs / mu, 3) if mu else None,
                           "z": round((obs - mu) / sd, 2) if sd > 0 else None,
                           "p": round(p, 4), "n_scored": tot}
        null_sweep.append(row)

    # -------- Analysis B: WORD-pair recovery vs frequency-matched random --------
    wmp = word_minimal_pairs(types)
    # grade each minimal pair by its differing-sign relation + word-final flag
    graded_wmp = []
    for (t1, t2, p, sa, sb) in wmp:
        r = relation(sa, sb)
        if r is None:
            continue
        final = (p == len(t1) - 1)
        graded_wmp.append({"t1": t1, "t2": t2, "pos": p, "sa": sa, "sb": sb,
                           "rel": r, "final": final})
    # word-pair scorers
    def w_method(t1, t2, sa, sb):
        return ew.get(frozenset((sa, sb)), 0)

    def w_context(t1, t2):
        # neighbour-word Jaccard (external context overlap, C1-style)
        def ctx(t):
            s = set()
            for i in type_occ[t]:
                o = occ[i]
                if o["prev"]:
                    s.add(("P", o["prev"]))
                if o["next"]:
                    s.add(("N", o["next"]))
            return s
        A, B = ctx(t1), ctx(t2)
        u = A | B
        return len(A & B) / len(u) if u else 0.0

    def w_formula(t1, t2):
        # shared specific neighbour-word slot count (formula)
        def ctx(t):
            c = Counter()
            for i in type_occ[t]:
                o = occ[i]
                if o["prev"]:
                    c[("P", o["prev"])] += 1
                if o["next"]:
                    c[("N", o["next"])] += 1
            return c
        A, B = ctx(t1), ctx(t2)
        return sum(1 for k in A if k in B)

    # frequency-matched random negatives: sample word-type pairs whose (min,max) freq
    # bin-distribution matches the positive minimal pairs. Common negative pool.
    def fbin(f):
        return min(6, int(math.log2(f)) if f > 0 else 0)
    pos_bins = Counter()
    for g in graded_wmp:
        fa, fb = type_freq[g["t1"]], type_freq[g["t2"]]
        pos_bins[(min(fbin(fa), fbin(fb)), max(fbin(fa), fbin(fb)))] += 1
    # build random pairs, bucket them, keep to match pos_bins proportions (x3 negatives)
    types_ge2 = [t for t in types if len(t) >= 2]
    want_total = 3 * len(graded_wmp)
    scale = want_total / max(1, sum(pos_bins.values()))
    want = {k: int(round(v * scale)) for k, v in pos_bins.items()}
    neg_pairs = []
    got = Counter()
    minimal_set = set(frozenset((g["t1"], g["t2"])) for g in graded_wmp)
    tries = 0
    maxtries = want_total * 400
    while sum(got.values()) < want_total and tries < maxtries:
        tries += 1
        x, y = rng.sample(types_ge2, 2)
        key = frozenset((x, y))
        if key in minimal_set:
            continue
        b = (min(fbin(type_freq[x]), fbin(type_freq[y])),
             max(fbin(type_freq[x]), fbin(type_freq[y])))
        if got[b] >= want.get(b, 0):
            continue
        got[b] += 1
        neg_pairs.append((x, y))

    # score positives (per class) and the common negative pool with each scorer
    wclasses = {
        "spelling_variant": [g for g in graded_wmp if g["rel"] == "spelling_variant"],
        "same_vowel": [g for g in graded_wmp if g["rel"] == "same_vowel"],
        "same_consonant": [g for g in graded_wmp if g["rel"] == "same_consonant"],
        "morphophonological_final_sameC": [g for g in graded_wmp
                                           if g["rel"] == "same_consonant" and g["final"]],
        "scribal_error_cross": [g for g in graded_wmp if g["rel"] == "cross"],
    }
    wscorers = ["method_substgraph_weight", "baseline_editdistance",
                "baseline_context_jaccard", "baseline_formula_sharedslot"]
    # precompute negative scores once
    neg_scores = {"method_substgraph_weight": [], "baseline_editdistance": [],
                  "baseline_context_jaccard": [], "baseline_formula_sharedslot": []}
    for (x, y) in neg_pairs:
        # differing signs undefined for non-minimal -> method/editdist see no substitution edge
        neg_scores["method_substgraph_weight"].append(0)
        neg_scores["baseline_editdistance"].append(0)
        neg_scores["baseline_context_jaccard"].append(w_context(x, y))
        neg_scores["baseline_formula_sharedslot"].append(w_formula(x, y))

    analysisB = {"n_word_minimal_pairs": len(wmp),
                 "n_graded_word_minimal_pairs": len(graded_wmp),
                 "n_freq_matched_random_negatives": len(neg_pairs),
                 "class_counts": {k: len(v) for k, v in wclasses.items()},
                 "auc_vs_freqmatched_random": {}}
    for cname, members in wclasses.items():
        analysisB["auc_vs_freqmatched_random"][cname] = {}
        for sc in wscorers:
            if sc == "method_substgraph_weight":
                pos = [w_method(g["t1"], g["t2"], g["sa"], g["sb"]) for g in members]
            elif sc == "baseline_editdistance":
                pos = [1 for _ in members]           # all are edit-distance-1 minimal pairs
            elif sc == "baseline_context_jaccard":
                pos = [w_context(g["t1"], g["t2"]) for g in members]
            else:
                pos = [w_formula(g["t1"], g["t2"]) for g in members]
            a = auc(pos, neg_scores[sc])
            analysisB["auc_vs_freqmatched_random"][cname][sc] = {
                "auc": round(a, 4) if a is not None else None,
                "n_pos": len(pos)}

    # within-minimal-pair discrimination: can the method tell relation types APART
    # (positives=class, negatives=cross minimal pairs)? edit-distance is flat here.
    cross_members = wclasses["scribal_error_cross"]
    analysisB["auc_class_vs_cross_minimalpairs"] = {}
    for cname in ["spelling_variant", "same_vowel", "same_consonant",
                  "morphophonological_final_sameC"]:
        members = wclasses[cname]
        analysisB["auc_class_vs_cross_minimalpairs"][cname] = {}
        for sc in wscorers:
            if sc == "method_substgraph_weight":
                pos = [w_method(g["t1"], g["t2"], g["sa"], g["sb"]) for g in members]
                neg = [w_method(g["t1"], g["t2"], g["sa"], g["sb"]) for g in cross_members]
            elif sc == "baseline_editdistance":
                pos = [1 for _ in members]; neg = [1 for _ in cross_members]
            elif sc == "baseline_context_jaccard":
                pos = [w_context(g["t1"], g["t2"]) for g in members]
                neg = [w_context(g["t1"], g["t2"]) for g in cross_members]
            else:
                pos = [w_formula(g["t1"], g["t2"]) for g in members]
                neg = [w_formula(g["t1"], g["t2"]) for g in cross_members]
            a = auc(pos, neg)
            analysisB["auc_class_vs_cross_minimalpairs"][cname][sc] = {
                "auc": round(a, 4) if a is not None else None,
                "n_pos": len(pos), "n_neg": len(neg)}

    # top recovered examples per relation (by method weight) for the report
    def top_examples(rel_name, k=10):
        cand = [(ew.get(frozenset((a, b)), 0), a, b)
                for (a, b), r in ((tuple(e), rr) for e, rr in rel_of.items())
                if r == rel_name]
        cand.sort(key=lambda x: -x[0])
        return [{"pair": [a, b], "weight": w} for w, a, b in cand[:k]]

    examples = {r: top_examples(r) for r in ["same_vowel", "same_consonant",
                                             "spelling_variant", "cross"]}

    out = {
        "experiment": "C3_linear_b_substitution_calibration",
        "seed": SEED, "n_null": N_NULL,
        "non_circular": "generation + graph use sign IDENTITY only; LB (C,V) values used solely to GRADE.",
        "corpus": {"source": "DĀMOS Mycenaean (items.jsonl)",
                   "wordform_tokens": n_tokens,
                   "wordform_types": len(types),
                   "types_len_ge2": sum(1 for t in types if len(t) >= 2),
                   "scorable_signs": len(scorable_signs),
                   "sign_pairs_graded": len(rel_of)},
        "analysis_A_signpair_recovery": analysisA,
        "degree_preserving_null_sweep": null_sweep,
        "analysis_B_wordpair_recovery": analysisB,
        "top_recovered_examples": examples,
        "relation_definitions": {
            "same_vowel": "differing signs share vowel, differ in consonant",
            "same_consonant": "differing signs share consonant, differ in vowel",
            "spelling_variant": "allograph doublet (same value modulo trailing digit)",
            "morphophonological_final_sameC": "same_consonant substitution in the WORD-FINAL slot",
            "scribal_error_cross": "minimal pair sharing no feature and not an allograph (slip/unrelated)",
        },
    }
    outpath = os.path.join(DATA, "C3_lb_calibration.json")
    json.dump(out, open(outpath, "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("top_recovered_examples",)}, indent=1)[:6000])
    print("\nWROTE", outpath, "(", os.path.getsize(outpath), "bytes )")
    return out


if __name__ == "__main__":
    run()
