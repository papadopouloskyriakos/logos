#!/usr/bin/env python3
"""F4 -- LEAVE-ONE-SIGN-OUT correspondence + RELATIVE-CLASS COMPATIBILITY (Const. v2.2 Art. XII/XV).

Four questions, four reports, one data file:

  F4-A  Build LA<->LB evidence SUBSETS (shape-high / paleography-high / function-high /
        multi-channel-high / contested) from the 59 shared-AB correspondence rows
        (crossscript_gate/anchors.csv). LB values are treated as HYPOTHESES, used ONLY to grade.
        -> reports/F_LINEAR_A_LINEAR_B_SUBSETS.md

  F4-B  LEAVE-ONE-SIGN-OUT: for each sign in a subset, HIDE its value, infer its cross-script
        correspondence from its Linear A distributional profile alone (rank LB signs by profile
        cosine, EXCLUDING the same-named LB twin), read off the predicted value-family (vowel /
        consonant series), and grade it against the held-out truth. Compare the distributional
        estimator against (i) a SHAPE-ONLY ceiling (assume the homomorphic twin's value -> the
        circular identity baseline) and (ii) a FREQUENCY baseline (rank-matched by corpus
        frequency). -> reports/F_LEAVE_ONE_SIGN_OUT.md

  F4-C  CYPRO-MINOAN sensitivity: 10 correspondences carry a Cypro-Minoan (CM) sign number in
        their Cypriot detail. Does CM presence ADD independent information, or does it just
        MULTIPLY signs the shape / Cypriot channels already flag? Contingency + LOSO-on-CM.
        -> reports/F_CYPRO_MINOAN_SENSITIVITY.md

  F4-D  RELATIVE-CLASS COMPATIBILITY: do the anonymous C4/C5 substitution rel_classes agree with
        the cross-script value hypotheses? i.e. within a class, do the (hypothesised) LB values
        share a vowel / consonant series MORE than a size-matched (and frequency-matched) random
        LA syllabogram set? This can CONSTRAIN classes (relative same-vowel / same-consonant
        structure) WITHOUT assigning absolute values, but must survive a null + multiplicity.
        -> reports/F_RELATIVE_CLASS_COMPATIBILITY.md

NON-CIRCULAR (Art. XII): every distributional profile is a pure statistic over sign IDENTITIES and
positions; LB/GORILA phonetic values enter ONLY (a) as the graded truth and (b) as the shape-only
ceiling's assumed identity. No value is ever a model input. Earns NO licence (Art. XV).
Deterministic seed 20260708.
"""
from __future__ import annotations

import csv
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from a1_recompute import feature, standardize, X  # noqa: E402 (a1 wires the data loader)

CAMP = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
GATE = "/home/claude-runner/gitlab/n8n/logos-la-lb-continuity/experiments/crossscript_gate"
ANCHORS = os.path.join(GATE, "anchors.csv")
C_LA_GRAPH = os.path.join(DATA, "C_la_graph.json")

SEED = 20260708
VOWELS = set("AEIOU")
FUNC_HIGH_THRESHOLD = 100      # la_attestations >= this => "function-high" (well-attested admin sign)
N_PERM = 5000                  # label-permutation nulls
N_CLASS_NULL = 20000           # random same-size LA-syllabogram-set nulls for rel-class compatibility


# --------------------------------------------------------------------------- value parsing (GRADE ONLY)
def parse_cv(v):
    """LB/GORILA value -> (consonant, vowel). Pure vowel -> ('',V). Strip allograph digit.
    Diphthongs / complex / *NNN -> None (kept out of family grading, apples-to-apples with F2)."""
    if not v:
        return None
    v = v.upper()
    if v.startswith("*") or v[0].isdigit():
        return None
    v = re.sub(r"\d+$", "", v)            # RA2->RA, PA3->PA, TA2->TA
    if v in VOWELS:
        return ("", v)
    if len(v) == 2 and v[0] not in VOWELS and v[1] in VOWELS:
        return (v[0], v[1])
    return None                          # AU, AI, complex, etc.


# --------------------------------------------------------------------------- channel ordinals
def shape_grade(g):
    g = (g or "").lower()
    if "homophone" in g:
        return "homophone"
    if "homomorphic" in g:
        return "homomorphic"
    return "none"


def is_cm(row):
    return bool(re.search(r"CM sign\s*\d+", row.get("cypriot_detail", "") or ""))


def cm_number(row):
    m = re.search(r"CM sign\s*(\d+)", row.get("cypriot_detail", "") or "")
    return m.group(1) if m else None


def is_contested(row):
    """A correspondence with a documented value tension."""
    reasons = []
    if row["cypriot_stable"] == "candidate":
        reasons.append("cypriot_candidate")
    if (row.get("disagreement_notes") or "").strip():
        reasons.append("disagreement_note")
    d = row.get("cypriot_detail", "") or ""
    m = re.search(r"=\s*(\w+)\s+in the Cypriot", d)
    if m and m.group(1).lower() != row["conventional_value"].lower():
        reasons.append("cypriot_value_conflict:" + m.group(1))
    if "?" in (row.get("sm2017_tier") or ""):
        reasons.append("sm2017_uncertain")
    return reasons


# --------------------------------------------------------------------------- cross-script cosine
def zprofiles(words, sign_set):
    """Standardize the 7-feature profile over sign_set only. Returns {sign: np.array(7)}."""
    F = feature(words)
    signs = [s for s in sign_set if s in F]
    M = np.array([F[s] for s in signs], dtype=float)
    Z, _, _ = standardize(M)
    return {s: Z[i] for i, s in enumerate(signs)}, F


def cos(u, v):
    d = float(np.linalg.norm(u) * np.linalg.norm(v))
    return float(u @ v / d) if d else 0.0


# =========================================================================== load
def load_anchors():
    rows = list(csv.DictReader(open(ANCHORS)))
    return rows


def build_subsets(rows):
    def sid(r):
        return r["sign_id"]
    shape_high = [sid(r) for r in rows if shape_grade(r["homomorphy_grade"]) == "homophone"]
    paleo_high = [sid(r) for r in rows if r["cypriot_stable"] == "true"]
    func_high = [sid(r) for r in rows if int(r["la_attestations"] or 0) >= FUNC_HIGH_THRESHOLD]
    # multi-channel = high on >=2 of {shape homophone, cypriot true, function-high}
    S, P, Fh = set(shape_high), set(paleo_high), set(func_high)
    multi = sorted(s for s in {r["sign_id"] for r in rows}
                   if (int(s in S) + int(s in P) + int(s in Fh)) >= 2)
    contested = [sid(r) for r in rows if is_contested(r)]
    cm = [sid(r) for r in rows if is_cm(r)]
    return {
        "all": sorted(r["sign_id"] for r in rows),
        "shape_high": sorted(shape_high),
        "paleography_high": sorted(paleo_high),
        "function_high": sorted(func_high),
        "multi_channel_high": sorted(multi),
        "contested": sorted(contested),
        "cypro_minoan": sorted(cm),
    }


# =========================================================================== F4-B  LOSO
def loso(rows, subsets, za, zb, Fa_raw, Fb_raw, lb_pool):
    """Per subset, per sign: distributional correspondence -> predicted (C,V) vs baselines."""
    val = {r["sign_id"]: r["conventional_value"] for r in rows}
    # LA & LB frequency ranks over the anchor set / LB pool (for the frequency baseline)
    def logfreq(F, s):
        return F[s][6] if s in F else None
    # LB pool candidates that parse to CV
    lb_cv = {c: parse_cv(c) for c in lb_pool}
    lb_cv = {c: v for c, v in lb_cv.items() if v is not None and c in zb}
    lb_candidates = sorted(lb_cv)
    lb_logfreq = {c: logfreq(Fb_raw, c) for c in lb_candidates}
    # rank of each LB candidate by frequency
    lb_by_freq = sorted(lb_candidates, key=lambda c: lb_logfreq[c])
    lb_freq_rank = {c: i / max(1, len(lb_by_freq) - 1) for i, c in enumerate(lb_by_freq)}

    results = {}
    per_sign_all = []
    for name, signs in subsets.items():
        graded = []
        for s in signs:
            truth = parse_cv(val[s])
            if truth is None or s not in za:
                continue
            tc, tv = truth
            # candidate pool EXCLUDES the same-named LB twin  (leave-one-sign-out)
            pool = [c for c in lb_candidates if c != s]
            if not pool:
                continue
            # (1) DISTRIBUTIONAL: top-1 LB sign by LA-profile cosine
            sims = [(cos(za[s], zb[c]), c) for c in pool]
            sims.sort(reverse=True)
            d_top = sims[0][1]
            d_cv = lb_cv[d_top]
            # (1b) CENTROID estimator: predict the vowel / consonant whose LB-sign centroid
            #      profile is nearest s's LA profile (excl twin). Robustness vs the noisy top-1.
            vgroups = defaultdict(list)
            cgroups = defaultdict(list)
            for c in pool:
                vgroups[lb_cv[c][1]].append(zb[c])
                if lb_cv[c][0] != "":
                    cgroups[lb_cv[c][0]].append(zb[c])
            def nearest_group(groups):
                best, bd = None, 1e9
                for lab, vecs in groups.items():
                    cen = np.mean(vecs, axis=0)
                    d = float(np.linalg.norm(za[s] - cen))
                    if d < bd:
                        bd, best = d, lab
                return best
            cen_vowel = nearest_group(vgroups)
            cen_cons = nearest_group(cgroups) if cgroups else None
            # (2) FREQUENCY baseline: LB sign whose freq-rank is nearest s's LA freq-rank
            #     (rank-matched to be corpus-size agnostic)
            la_ranks = {t: i for i, t in enumerate(sorted(
                [x for x in za if parse_cv(val.get(x, "")) is not None or x in Fa_raw],
                key=lambda t: Fa_raw[t][6]))}
            s_rank = la_ranks.get(s, 0) / max(1, len(la_ranks) - 1)
            f_top = min(pool, key=lambda c: abs(lb_freq_rank[c] - s_rank))
            f_cv = lb_cv[f_top]
            # (3) SHAPE-ONLY ceiling: assume the homomorphic twin -> the true value (identity)
            #     -> vowel/cons always correct by construction (circular; that is the point).
            row = {
                "sign": s, "true_value": val[s], "true_cv": [tc, tv],
                "distributional_top": d_top, "distributional_cv": list(d_cv),
                "dist_vowel_correct": d_cv[1] == tv,
                "dist_cons_correct": (d_cv[0] == tc) and tc != "",
                "dist_exact_correct": (d_cv == (tc, tv)),
                "centroid_vowel": cen_vowel, "centroid_cons": cen_cons,
                "cent_vowel_correct": cen_vowel == tv,
                "cent_cons_correct": (cen_cons == tc) and tc != "",
                "frequency_top": f_top, "frequency_cv": list(f_cv),
                "freq_vowel_correct": f_cv[1] == tv,
                "freq_cons_correct": (f_cv[0] == tc) and tc != "",
                "shape_vowel_correct": True, "shape_cons_correct": True,  # identity ceiling
                "subset": name,
            }
            graded.append(row)
            if name == "all":
                per_sign_all.append(row)
        n = len(graded)
        cons_gradeable = [g for g in graded if g["true_cv"][0] != ""]  # signs with a consonant
        def acc(key, items=None):
            it = items if items is not None else graded
            return round(sum(1 for g in it if g[key]) / len(it), 4) if it else None
        # chance: modal vowel / modal consonant base-rate within the subset's true labels
        vow_counts = Counter(g["true_cv"][1] for g in graded)
        con_counts = Counter(g["true_cv"][0] for g in cons_gradeable)
        chance_vowel = round(max(vow_counts.values()) / n, 4) if n else None
        chance_cons = (round(max(con_counts.values()) / len(cons_gradeable), 4)
                       if cons_gradeable else None)
        results[name] = {
            "n_signs_in_subset": len(signs),
            "n_gradeable": n,
            "n_cons_gradeable": len(cons_gradeable),
            "vowel_accuracy": {
                "distributional_top1": acc("dist_vowel_correct"),
                "distributional_centroid": acc("cent_vowel_correct"),
                "frequency": acc("freq_vowel_correct"),
                "shape_ceiling_circular": 1.0,
                "chance_modal": chance_vowel,
            },
            "consonant_accuracy": {
                "distributional_top1": acc("dist_cons_correct", cons_gradeable),
                "distributional_centroid": acc("cent_cons_correct", cons_gradeable),
                "frequency": acc("freq_cons_correct", cons_gradeable),
                "shape_ceiling_circular": 1.0,
                "chance_modal": chance_cons,
            },
            "exact_cell_accuracy_distributional": acc("dist_exact_correct"),
        }
    return results, per_sign_all, {"n_lb_candidates": len(lb_candidates)}


def perm_test_vowel(per_sign_all, rng, n_perm=N_PERM):
    """Label-permutation null for distributional vowel accuracy over the FULL anchor set:
    shuffle the true vowels across signs, recompute how often the distributional top-1's vowel
    matches the (shuffled) truth. p = P(null_acc >= observed)."""
    obs = sum(1 for g in per_sign_all if g["dist_vowel_correct"]) / len(per_sign_all)
    pred_vowels = [g["distributional_cv"][1] for g in per_sign_all]
    true_vowels = [g["true_cv"][1] for g in per_sign_all]
    nulls = []
    for _ in range(n_perm):
        sh = true_vowels[:]
        rng.shuffle(sh)
        nulls.append(sum(1 for p, t in zip(pred_vowels, sh) if p == t) / len(sh))
    p = (sum(1 for x in nulls if x >= obs) + 1) / (n_perm + 1)
    return {"observed_vowel_acc": round(obs, 4), "null_mean": round(sum(nulls) / len(nulls), 4),
            "null_p95": round(sorted(nulls)[int(0.95 * n_perm)], 4), "p_value": round(p, 4)}


# =========================================================================== F4-C  Cypro-Minoan
def fisher_exact(a, b, c, d):
    """Two-sided Fisher exact p for a 2x2 [[a,b],[c,d]] (small tables)."""
    from math import lgamma

    def logC(n, k):
        return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    def prob(x):
        return math.exp(logC(r1, x) + logC(r2, c1 - x) - logC(n, c1))
    p_obs = prob(a)
    tot = 0.0
    lo, hi = max(0, c1 - r2), min(r1, c1)
    for x in range(lo, hi + 1):
        px = prob(x)
        if px <= p_obs * (1 + 1e-9):
            tot += px
    return min(1.0, tot)


def cm_sensitivity(rows, loso_results, za, zb, lb_pool, Fb_raw):
    val = {r["sign_id"]: r["conventional_value"] for r in rows}
    cm_set = {r["sign_id"] for r in rows if is_cm(r)}
    homophone = {r["sign_id"] for r in rows if shape_grade(r["homomorphy_grade"]) == "homophone"}
    homomorphic_plus = {r["sign_id"] for r in rows
                        if shape_grade(r["homomorphy_grade"]) in ("homophone", "homomorphic")}
    cyp_true = {r["sign_id"] for r in rows if r["cypriot_stable"] == "true"}
    allsigns = {r["sign_id"] for r in rows}

    def contingency(chan_set, label):
        a = len(cm_set & chan_set)                       # CM & channel
        b = len(cm_set - chan_set)                       # CM & not-channel
        c = len(chan_set - cm_set)                       # not-CM & channel
        d = len((allsigns - cm_set) - chan_set)          # neither
        p = fisher_exact(a, b, c, d)
        # is CM a SUBSET of the channel (redundant) ?
        subset = (b == 0)
        return {"channel": label, "cm_and_channel": a, "cm_not_channel": b,
                "channel_not_cm": c, "neither": d, "fisher_p_two_sided": round(p, 6),
                "cm_is_subset_of_channel": subset,
                "cm_coverage_of_channel": round(a / len(chan_set), 4) if chan_set else None}

    cont = [contingency(homophone, "shape_homophone"),
            contingency(homomorphic_plus, "shape_homomorphic_or_better"),
            contingency(cyp_true, "cypriot_stable_true")]

    # Independent-information probe: does CM restriction change LOSO value recovery beyond
    # what cypriot_stable already delivers?  Compare CM subset vs cypriot_stable_true subset.
    cm_loso = loso_results.get("cypro_minoan")
    cyp_loso = loso_results.get("paleography_high")
    return {
        "n_cm_correspondences": len(cm_set),
        "cm_signs": sorted(cm_set),
        "contingency_vs_channels": cont,
        "cm_subset_of_cypriot_stable": cm_set.issubset(cyp_true),
        "cm_signs_not_in_cypriot_stable": sorted(cm_set - cyp_true),
        "cypriot_stable_signs_not_cm": sorted(cyp_true - cm_set),
        "loso_cm_vs_cypriot_stable": {
            "cypro_minoan": cm_loso["vowel_accuracy"] if cm_loso else None,
            "paleography_high_cypriot_stable": cyp_loso["vowel_accuracy"] if cyp_loso else None,
        },
        "interpretation_key": (
            "If CM is a strict subset of an existing channel (b=0) and its Fisher p is tiny, CM MULTIPLIES "
            "already-flagged signs rather than adding an independent evidence axis."),
    }


# =========================================================================== F4-D  rel-class compat
def rel_class_compatibility(rows, rng):
    graph = json.load(open(C_LA_GRAPH))
    rel_classes = graph["rel_classes"]
    val = {r["sign_id"]: r["conventional_value"] for r in rows}
    # LA syllabogram universe = anchor signs that parse to a (C,V): the null draw pool
    universe = [s for s in val if parse_cv(val[s]) is not None]
    uni_cv = {s: parse_cv(val[s]) for s in universe}
    # frequency of each universe sign (LA corpus) for the frequency-matched null
    _, a_words, _ = X.load_a()
    Fa = feature(a_words)
    uni_freq = {s: (Fa[s][6] if s in Fa else 0.0) for s in universe}
    def fbin(s):
        f = math.exp(uni_freq[s]) if uni_freq[s] else 1
        return min(5, int(math.log2(f)) if f > 0 else 0)
    universe_by_bin = defaultdict(list)
    for s in universe:
        universe_by_bin[fbin(s)].append(s)

    def modal_frac(signs, axis):
        cvs = [uni_cv[s] for s in signs if s in uni_cv]
        if len(cvs) < 2:
            return None, 0
        if axis == "vowel":
            c = Counter(v for (_, v) in cvs)
        else:
            c = Counter(cc for (cc, _) in cvs if cc != "")
        if not c:
            return None, len(cvs)
        return max(c.values()) / len(cvs), len(cvs)

    out_classes = []
    all_tests = []           # for multiplicity
    for rc in rel_classes:
        signs = [s for s in rc["signs"] if s in uni_cv]
        if len(signs) < 2:
            out_classes.append({"rel_class": rc["rel_class"], "signs": rc["signs"],
                                "n_valued": len(signs), "note": "too few valued signs"})
            continue
        entry = {"rel_class": rc["rel_class"], "signs": rc["signs"],
                 "n_valued": len(signs),
                 "values": {s: val[s] for s in signs}}
        for axis in ("vowel", "consonant"):
            obs, k = modal_frac(signs, axis)
            if obs is None:
                entry[axis] = {"note": "no consonantal members" if axis == "consonant" else "n/a"}
                continue
            # unconditioned null: random same-size subset of universe
            nulls = []
            for _ in range(N_CLASS_NULL):
                samp = rng.sample(universe, len(signs))
                mf, _kk = modal_frac(samp, axis)
                nulls.append(mf if mf is not None else 0.0)
            p_uncond = (sum(1 for x in nulls if x >= obs) + 1) / (N_CLASS_NULL + 1)
            # frequency-matched null: draw one sign per class-member from its own freq bin
            fnulls = []
            bins = [fbin(s) for s in signs]
            ok = 0
            for _ in range(N_CLASS_NULL):
                samp = []
                bad = False
                used = set()
                for b in bins:
                    pool = [x for x in universe_by_bin[b] if x not in used]
                    if not pool:
                        bad = True
                        break
                    x = rng.choice(pool)
                    used.add(x)
                    samp.append(x)
                if bad:
                    continue
                ok += 1
                mf, _kk = modal_frac(samp, axis)
                fnulls.append(mf if mf is not None else 0.0)
            p_freq = ((sum(1 for x in fnulls if x >= obs) + 1) / (len(fnulls) + 1)
                      if fnulls else None)
            entry[axis] = {
                "observed_modal_fraction": round(obs, 4),
                "modal_value": Counter(uni_cv[s][1] if axis == "vowel" else uni_cv[s][0]
                                       for s in signs if (axis == "vowel" or uni_cv[s][0] != "")
                                       ).most_common(1)[0][0],
                "null_mean_uncond": round(sum(nulls) / len(nulls), 4),
                "p_uncond": round(p_uncond, 4),
                "null_mean_freqmatched": round(sum(fnulls) / len(fnulls), 4) if fnulls else None,
                "p_freqmatched": round(p_freq, 4) if p_freq is not None else None,
                "n_freqmatched_valid": ok,
            }
            all_tests.append((rc["rel_class"], axis, p_uncond,
                              p_freq if p_freq is not None else 1.0))
        out_classes.append(entry)

    n_tests = len(all_tests)
    survivors_uncond = [(c, a) for (c, a, pu, pf) in all_tests if pu * n_tests < 0.05]
    survivors_freq = [(c, a) for (c, a, pu, pf) in all_tests if pf * n_tests < 0.05]
    return {
        "n_rel_classes": len(rel_classes),
        "n_tests": n_tests,
        "bonferroni_factor": n_tests,
        "per_class": out_classes,
        "survivors_bonferroni_uncond": survivors_uncond,
        "survivors_bonferroni_freqmatched": survivors_freq,
        "note": ("A class is COMPATIBLE with a shared value-family only if its modal-fraction beats "
                 "the size-matched null AND the frequency-matched null AND survives Bonferroni across "
                 f"{n_tests} class x axis tests."),
    }


# =========================================================================== run
def run():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(REPORTS, exist_ok=True)
    rng = random.Random(SEED)
    rows = load_anchors()
    subsets = build_subsets(rows)

    # cross-script profiles
    a_ids, a_words, _ = X.load_a()
    b_words, _, _ = X.load_b_damos()
    anchor_signs = [r["sign_id"] for r in rows]
    Fa_all = feature(a_words)
    Fb_all = feature(b_words)
    # standardize LA profiles over the anchor set; LB profiles over the LB CV-parseable inventory
    za, Fa_raw = zprofiles(a_words, anchor_signs)
    lb_pool = [s for s in Fb_all if parse_cv(s) is not None]
    zb, Fb_raw = zprofiles(b_words, lb_pool)

    loso_results, per_sign_all, loso_meta = loso(rows, subsets, za, zb, Fa_raw, Fb_raw, lb_pool)
    perm = perm_test_vowel(per_sign_all, rng)
    cm = cm_sensitivity(rows, loso_results, za, zb, lb_pool, Fb_raw)
    relcompat = rel_class_compatibility(rows, rng)

    out = {
        "experiment": "F4_loso_and_relative_class_compatibility",
        "seed": SEED, "constitution": "v2.2 (Art. XII no-grade-by-creating-rule, Art. XV licences)",
        "non_circular": ("distributional profiles use sign identity + position only; LB values grade "
                         "the held-out truth and define the circular shape-ceiling; never a model input."),
        "func_high_threshold_la_attestations": FUNC_HIGH_THRESHOLD,
        "subsets": {k: {"n": len(v), "signs": v} for k, v in subsets.items()},
        "loso": loso_results,
        "loso_meta": loso_meta,
        "loso_permutation_vowel_null": perm,
        "cypro_minoan_sensitivity": cm,
        "relative_class_compatibility": relcompat,
        "per_sign_all_subset": per_sign_all,
    }
    path = os.path.join(DATA, "F4_loso.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
    print("WROTE", path, os.path.getsize(path), "bytes")
    # console digest
    print("\n== subsets ==")
    for k, v in subsets.items():
        print(f"  {k:20s} n={len(v):2d}  {v}")
    print("\n== LOSO vowel accuracy (distributional / frequency / chance) ==")
    for k, r in loso_results.items():
        va = r["vowel_accuracy"]
        print(f"  {k:20s} n={r['n_gradeable']:2d}  dist_top1={va['distributional_top1']} "
              f"dist_cent={va['distributional_centroid']} freq={va['frequency']} "
              f"chance={va['chance_modal']} (shape ceiling=1.0, circular)")
    print("\n== permutation vowel null (all):", perm)
    print("\n== CM sensitivity ==")
    for c in cm["contingency_vs_channels"]:
        print(f"  vs {c['channel']:28s} CM&ch={c['cm_and_channel']} CM_not_ch={c['cm_not_channel']} "
              f"subset={c['cm_is_subset_of_channel']} fisher_p={c['fisher_p_two_sided']}")
    print("  CM subset of cypriot_stable:", cm["cm_subset_of_cypriot_stable"],
          "| cypriot-only signs:", cm["cypriot_stable_signs_not_cm"])
    print("\n== rel-class compatibility (Bonferroni x", relcompat["n_tests"], ") ==")
    for e in relcompat["per_class"]:
        if "vowel" in e and isinstance(e["vowel"], dict) and "observed_modal_fraction" in e["vowel"]:
            v = e["vowel"]
            print(f"  {e['rel_class']} {e['signs']}")
            print(f"     vowel modal={v['modal_value']} frac={v['observed_modal_fraction']} "
                  f"p_uncond={v['p_uncond']} p_freq={v['p_freqmatched']}")
            if isinstance(e.get("consonant"), dict) and "observed_modal_fraction" in e["consonant"]:
                c = e["consonant"]
                print(f"     cons  modal={c['modal_value']} frac={c['observed_modal_fraction']} "
                      f"p_uncond={c['p_uncond']} p_freq={c['p_freqmatched']}")
    print("  survivors (uncond Bonf):", relcompat["survivors_bonferroni_uncond"])
    print("  survivors (freq  Bonf):", relcompat["survivors_bonferroni_freqmatched"])
    return out


if __name__ == "__main__":
    run()
