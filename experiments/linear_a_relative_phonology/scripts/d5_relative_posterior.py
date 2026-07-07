#!/usr/bin/env python3
"""D5 — Linear A RELATIVE POSTERIOR.

Combines the D1/D2 multi-view fused-latent features into ANONYMOUS posterior relative classes for
Linear A signs, with explicit per-sign uncertainty (P(class_1), P(class_2), stability), and honours
the D3/D4 seed reality (SEED_A = 0 secure value seeds; the seed-propagation "0.87" is a frequency
artifact). NO phonetic value is ever assigned to any class or sign. Known LB syllabic values (parsed
from the conventional transliteration) are used ONLY as an external grading benchmark for the
anonymous partition — never as a model INPUT feature.

Deliverable per sign:
  - primary anonymous partition (K=2): p_class_1, p_class_2 (bootstrap membership), stability
  - fine anonymous partition (K=6, matching D1): modal class + stability
  - view-ablation agreement (leave-one-view-out)

Uncertainty:
  - BOOTSTRAP: resample the GORILA-word and FORMULA corpora with replacement, rebuild the five
    fused views on the FIXED graded sign set, refit PCA + KMeans, align to the reference partition
    (max-overlap / Hungarian), tally per-sign class assignment across B replicates.
  - VIEW ABLATION: leave-one-view-out refits (D2 family), align, tally agreement.

Honest grading: the reference partition is graded vs the 5-vowel and C/V benchmarks (AMI + perm-p).
The D1 fused-latent-vs-vowel AMI is NULL (p~0.16); D5 reports whether the posterior classes carry
ANY phonetic alignment (expected: none beyond chance) and states explicitly what is NOT determined.

Seed 20260708. Non-circular. Reuses audited primitives from a1_recompute and the D1 view logic.
"""
from __future__ import annotations
import json, math, os, re, sys
from collections import Counter, defaultdict

import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
WT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, WT)
sys.path.insert(0, HERE)
from a1_recompute import standardize  # audited primitive
from d1_multiview import (parse_value, kmeans, ami_perm, macro_vowel_auc,
                          cv_contrast_auc, perm_p, VOWELS)

SEED = 20260708
np.random.seed(SEED)

FUSE_VIEWS = ["POSITION", "SUBSTITUTION", "MORPHOLOGY", "FORMULA", "SITE"]


# ---------------------------------------------------------------------------------------------------
# view construction over an EXPLICIT word list (so we can bootstrap the corpus). Mirrors d1_multiview.
# ---------------------------------------------------------------------------------------------------
def build_views(gwords, fwords, graph):
    init = Counter(); fin = Counter(); tot = Counter(); pos = defaultdict(float); lone = Counter()
    lnb = defaultdict(Counter); rnb = defaultdict(Counter)
    prefix = defaultdict(set); suffix = defaultdict(set); mid = defaultdict(set)
    site_of = defaultdict(Counter)
    for u in gwords:
        w = [s for s in u["signs"] if s]
        L = len(w)
        if L == 0:
            continue
        if L == 1:
            lone[w[0]] += 1
        stem = "".join(w)
        for i, s in enumerate(w):
            tot[s] += 1
            pos[s] += (i / (L - 1)) if L > 1 else 0.5
            site_of[s][u["site"]] += 1
            if i > 0:
                lnb[s][w[i - 1]] += 1
            if i < L - 1:
                rnb[s][w[i + 1]] += 1
        if L >= 2:
            prefix[w[0]].add(stem)
            suffix[w[-1]].add(stem)
            for s in w[1:-1]:
                mid[s].add(stem)
        init[w[0]] += 1
        fin[w[-1]] += 1

    def ent(c):
        n = sum(c.values())
        return -sum((v / n) * math.log(v / n) for v in c.values()) if n else 0.0

    f_init = Counter(); f_fin = Counter(); f_tot = Counter(); f_pos = defaultdict(float)
    for u in fwords:
        w = [s for s in u["signs"] if s]
        L = len(w)
        if L == 0:
            continue
        for i, s in enumerate(w):
            f_tot[s] += 1
            f_pos[s] += (i / (L - 1)) if L > 1 else 0.5
        f_init[w[0]] += 1
        f_fin[w[-1]] += 1

    sub_deg = Counter(); sub_sup = Counter(); sub_finw = defaultdict(float); sub_finn = Counter()
    for e in graph["sign_substitution_graph"]["top_edges"]:
        a, b = e["signs"]
        w = e["w_long_frame"]; ff = e["final_fraction"]
        for x in (a, b):
            sub_deg[x] += 1; sub_sup[x] += w; sub_finw[x] += ff * w; sub_finn[x] += w

    views = {v: {} for v in ["POSITION", "FREQUENCY", "SUBSTITUTION", "MORPHOLOGY", "FORMULA", "SITE"]}
    for s in tot:
        f = tot[s]
        views["POSITION"][s] = [init[s] / f, fin[s] / f, pos[s] / f, lone[s] / f, ent(lnb[s]), ent(rnb[s])]
        views["FREQUENCY"][s] = [math.log(f)]
        views["MORPHOLOGY"][s] = [len(prefix[s]), len(suffix[s]), len(mid[s])]
        sc = site_of[s]
        views["SITE"][s] = [len(sc), ent(sc), (sc.get("Haghia Triada", 0) / f)]
        if f_tot[s]:
            views["FORMULA"][s] = [f_init[s] / f_tot[s], f_fin[s] / f_tot[s], f_pos[s] / f_tot[s]]
        if sub_deg[s]:
            fr = (sub_finw[s] / sub_finn[s]) if sub_finn[s] else 0.0
            views["SUBSTITUTION"][s] = [sub_deg[s], sub_sup[s], fr]
    return views, tot


def fuse(views, graded, use_views=FUSE_VIEWS):
    """Replicate D1 fusion on a FIXED graded sign set -> latent scores. Returns (scores, K, var)."""
    cols = []; masks = []
    for vn in use_views:
        d = views[vn]
        present = np.array([1.0 if s in d else 0.0 for s in graded])
        # dimension from any present sign, else skip robustly
        anyv = next((v for v in d.values()), None)
        if anyv is None:
            continue
        dim = len(anyv)
        M = np.zeros((len(graded), dim))
        for i, s in enumerate(graded):
            if s in d:
                M[i] = d[s]
        if present.sum() > 1:
            pr = present.astype(bool)
            mu = M[pr].mean(0); sd = M[pr].std(0) + 1e-9
            Mz = (M - mu) / sd
            Mz[~pr] = 0.0
        else:
            Mz = M * 0.0
        cols.append(Mz)
        masks.append(present.reshape(-1, 1))
    Xfused = np.hstack(cols + masks)
    Xc = Xfused - Xfused.mean(0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = (S ** 2) / (S ** 2).sum()
    K = int(np.searchsorted(np.cumsum(var), 0.80) + 1)
    K = max(3, min(K, 8))
    scores = U[:, :K] * S[:K]
    return scores, K, var


def align(lab, ref, k):
    """Return a relabeling of `lab` maximally overlapping `ref` (Hungarian on -overlap)."""
    C = np.zeros((k, k))
    for a in range(k):
        for b in range(k):
            C[a, b] = np.sum((lab == a) & (ref == b))
    ri, ci = linear_sum_assignment(-C)
    mp = {int(a): int(b) for a, b in zip(ri, ci)}
    return np.array([mp[int(x)] for x in lab])


# ---------------------------------------------------------------------------------------------------
def run():
    gwords = json.load(open(os.path.join(DATA, "segmentations", "SEG_GORILA_WORD.json")))["units"]
    fwords = json.load(open(os.path.join(DATA, "segmentations", "SEG_FORMULA.json")))["units"]
    graph = json.load(open(os.path.join(DATA, "C_la_graph.json")))

    views, tot = build_views(gwords, fwords, graph)

    THRESH = 8
    graded = sorted(s for s in views["POSITION"] if parse_value(s) and tot[s] >= THRESH)
    cons = {s: parse_value(s)[0] for s in graded}
    vow = {s: parse_value(s)[1] for s in graded}
    vowels = [vow[s] for s in graded]
    is_vsign = [cons[s] == "" for s in graded]
    n = len(graded)

    # ---- REFERENCE fused latent + partitions (K=2 primary, K=6 fine matching D1) ----
    scores, K, var = fuse(views, graded)
    Sz, _, _ = standardize(scores)
    ref2 = kmeans(Sz, 2)
    ref6 = kmeans(Sz, 6)

    # grade reference partitions vs phonetic benchmarks (benchmark ONLY; classes stay anonymous)
    vowel_int = [VOWELS.index(v) for v in vowels]
    cv_int = [1 if b else 0 for b in is_vsign]
    grade2 = {"vs_vowel": ami_perm(ref2, vowel_int), "vs_CV": ami_perm(ref2, cv_int)}
    grade6 = {"vs_vowel": ami_perm(ref6, vowel_int), "vs_CV": ami_perm(ref6, cv_int)}
    # fused latent phonetic recoverability (carried from D1 spirit): macro vowel AUC + perm-p
    fused_vowel_auc = macro_vowel_auc(scores, vowels)
    fused_vowel_p = perm_p(fused_vowel_auc, lambda vv: macro_vowel_auc(scores, vv), vowels)
    fused_cv_auc = cv_contrast_auc(scores, is_vsign)

    # ---- BOOTSTRAP posterior: resample corpora with replacement, rebuild, refit, align, tally ----
    B = 400
    rng = np.random.RandomState(SEED)
    cnt2 = np.zeros((n, 2))
    cnt6 = np.zeros((n, 6))
    coassign2 = np.zeros((n, n))  # how often signs land in the same K=2 class (label-free stability)
    coassign6 = np.zeros((n, n))
    ng, nf = len(gwords), len(fwords)
    b_used = 0
    for bi in range(B):
        gi = rng.randint(0, ng, ng)
        fi = rng.randint(0, nf, nf)
        gb = [gwords[i] for i in gi]
        fb = [fwords[i] for i in fi]
        vb, tb = build_views(gb, fb, graph)
        # graded sign set is FIXED; if a sign vanished from POSITION view (impossible at this freq but guard)
        if any(s not in vb["POSITION"] for s in graded):
            # keep signs; missing ones imputed inside fuse via masks (POSITION dim). Fill absent with {} handled.
            pass
        try:
            sc_b, _, _ = fuse(vb, graded)
        except Exception:
            continue
        Szb, _, _ = standardize(sc_b)
        lab2 = align(kmeans(Szb, 2, seed=SEED + bi), ref2, 2)
        lab6 = align(kmeans(Szb, 6, seed=SEED + bi), ref6, 6)
        for i in range(n):
            cnt2[i, lab2[i]] += 1
            cnt6[i, lab6[i]] += 1
        # co-assignment (label-free)
        for i in range(n):
            coassign2[i] += (lab2 == lab2[i])
            coassign6[i] += (lab6 == lab6[i])
        b_used += 1

    p2 = cnt2 / b_used
    p6 = cnt6 / b_used
    coassign2 /= b_used
    coassign6 /= b_used

    # ---- VIEW-ABLATION agreement: leave-one-view-out (D2 family), align to reference ----
    loo = {}
    loo_agree2 = np.zeros(n)
    for drop in FUSE_VIEWS:
        uv = [v for v in FUSE_VIEWS if v != drop]
        sc_l, _, _ = fuse(views, graded, use_views=uv)
        Szl, _, _ = standardize(sc_l)
        lab2 = align(kmeans(Szl, 2), ref2, 2)
        agree = (lab2 == ref2).astype(float)
        loo[f"minus_{drop}"] = round(float(agree.mean()), 4)
        loo_agree2 += agree
    loo_agree2 /= len(FUSE_VIEWS)

    # ---- structural descriptors of each anonymous class (L2/L3 interpretation, NO values) ----
    # raw (unstandardized) view means per reference class -> what distinguishes the class structurally
    def class_profile(labels, kk):
        prof = []
        for j in range(kk):
            members = [graded[i] for i in range(n) if labels[i] == j]
            idx = [i for i in range(n) if labels[i] == j]
            # descriptive structural loadings (means of interpretable raw features)
            def vmean(view, col):
                vals = [views[view][graded[i]][col] for i in idx if graded[i] in views[view]]
                return round(float(np.mean(vals)), 4) if vals else None
            prof.append({
                "anon_class": f"C{kk}_{j}",
                "n": len(members),
                "signs": members,
                "struct": {
                    "initial_rate": vmean("POSITION", 0),
                    "final_rate": vmean("POSITION", 1),
                    "mean_pos": vmean("POSITION", 2),
                    "lone_rate": vmean("POSITION", 3),
                    "prefix_stems": vmean("MORPHOLOGY", 0),
                    "suffix_stems": vmean("MORPHOLOGY", 1),
                    "mid_stems": vmean("MORPHOLOGY", 2),
                    "n_sites": vmean("SITE", 0),
                },
                # benchmark composition (grading only; class stays anonymous)
                "benchmark_vowel_composition": dict(Counter(vow[s] for s in members)),
                "benchmark_pure_vowel_signs": sum(1 for s in members if cons[s] == ""),
            })
        return prof

    prof2 = class_profile(ref2, 2)
    prof6 = class_profile(ref6, 6)

    # ---- anonymous affixation paradigm (L2/L3) : per-sign relative role, NO phonetic value ----
    # role = argmax of (prefix, suffix, mid) stem counts, normalised; anonymous "edge vs interior" structure
    affix = []
    for s in graded:
        pf, sf, md = views["MORPHOLOGY"][s]
        tot_role = pf + sf + md
        init_rate = views["POSITION"][s][0]
        fin_rate = views["POSITION"][s][1]
        role = "MID_INTERIOR"
        if tot_role > 0:
            if pf >= sf and pf >= md:
                role = "PREFIX_EDGE"
            elif sf >= pf and sf >= md:
                role = "SUFFIX_EDGE"
        affix.append({
            "sign": s, "role_anonymous": role,
            "prefix_stems": pf, "suffix_stems": sf, "mid_stems": md,
            "initial_rate": round(init_rate, 4), "final_rate": round(fin_rate, 4),
        })

    # ---- per-sign posterior record ----
    signs_out = []
    for i, s in enumerate(graded):
        signs_out.append({
            "sign": s,
            "primary_partition_K2": {
                "p_class_1": round(float(p2[i, 0]), 4),
                "p_class_2": round(float(p2[i, 1]), 4),
                "modal_class": f"C2_{int(np.argmax(p2[i]))}",
                "stability": round(float(np.max(p2[i])), 4),               # bootstrap modal fraction
                "coassign_stability": round(float(np.sort(coassign2[i])[::-1][:max(1, int((ref2==ref2[i]).sum()))].mean()), 4),
                "loo_view_agreement": round(float(loo_agree2[i]), 4),      # LOVO agreement w/ reference
            },
            "fine_partition_K6": {
                "posterior": {f"C6_{j}": round(float(p6[i, j]), 4) for j in range(6)},
                "modal_class": f"C6_{int(np.argmax(p6[i]))}",
                "stability": round(float(np.max(p6[i])), 4),
            },
            # benchmark truth (REPORTED, never an input) — lets a reader audit non-circularity
            "benchmark_value_LB_grading_only": {"consonant": cons[s] or "(vowel-sign)", "vowel": vow[s]},
        })

    # sign-level stability distribution
    stab2 = np.array([np.max(p2[i]) for i in range(n)])
    stab6 = np.array([np.max(p6[i]) for i in range(n)])

    out = {
        "task": "D5_linear_a_relative_posterior",
        "seed": SEED, "as_of": "2026-07-07",
        "highest_layer": "L2/L3 (anonymous relative structure)",
        "phonetic_value_assigned": False,
        "non_circular": "known LB syllabic values used ONLY to grade the anonymous partition; every model "
                        "input is a distributional/structural statistic over sign identities. No class or "
                        "sign is given any phonetic value.",
        "seed_reality_D3_D4": {
            "secure_value_seeds_SEED_A": 0,
            "seed_propagation_verdict": "SEED_PROPAGATION_FREQUENCY_ARTIFACT (D3): pure frequency ranking "
                "AUC=0.872 >= seed-prop kv4 pos+sub AUC=0.784; initial-rate ranking alone AUC=0.759, no seeds.",
            "frontier_D4": "LA sits at k=0 SECURE seeds (pre-frontier origin); only value-blind channels "
                "(random/shape) available, which the LB control measures at the null floor; anchor-derived "
                "seeds cap at <=2 on paper and 0 after LOTO. No phonetic decoding is unlocked.",
            "consequence_for_D5": "posterior classes are ANONYMOUS RELATIVE partitions only; no seed exists "
                "to attach any class to a phonetic value, and D1 shows the partition does not align with "
                "vowel/CV beyond chance.",
        },
        "graded_sign_set": {
            "threshold_freq_ge": THRESH, "n_signs": n,
            "n_pure_vowel_signs": sum(is_vsign),
            "vowel_counts_benchmark": dict(Counter(vowels)),
            "signs": graded,
        },
        "fused_latent": {
            "fused_views": FUSE_VIEWS,
            "K_latent_used": int(K),
            "explained_variance_top": [round(float(v), 4) for v in var[:K]],
            "fused_vowel_macro_auc": round(fused_vowel_auc, 4) if fused_vowel_auc else None,
            "fused_vowel_perm_p": round(float(fused_vowel_p), 4),
            "fused_cv_contrast_auc": round(fused_cv_auc, 4) if fused_cv_auc else None,
        },
        "bootstrap": {"B_requested": B, "B_used": b_used,
                      "resample": "GORILA-word + FORMULA corpora with replacement; graded sign set fixed"},
        "reference_partition_K2": {
            "grade_vs_phonetic_benchmark": grade2,
            "classes": prof2,
            "posterior_alignment_note": "class labels C2_0/C2_1 are anonymous; bootstrap posteriors aligned "
                                        "to this reference by max-overlap (Hungarian).",
        },
        "reference_partition_K6": {
            "grade_vs_phonetic_benchmark": grade6,
            "classes": prof6,
        },
        "view_ablation_loo_agreement_K2": loo,
        "affixation_paradigm_L2_L3_anonymous": {
            "role_counts": dict(Counter(a["role_anonymous"] for a in affix)),
            "note": "anonymous edge/interior roles from stem-affixation profiles; the LA-real axis is "
                    "word-INITIAL affixation (wave-2). NO phonetic value implied by any role.",
            "signs": affix,
        },
        "stability_summary": {
            "K2_modal_fraction": {"mean": round(float(stab2.mean()), 4), "min": round(float(stab2.min()), 4),
                                  "median": round(float(np.median(stab2)), 4),
                                  "frac_signs_ge_0.8": round(float((stab2 >= 0.8).mean()), 4),
                                  "frac_signs_ge_0.9": round(float((stab2 >= 0.9).mean()), 4)},
            "K6_modal_fraction": {"mean": round(float(stab6.mean()), 4), "min": round(float(stab6.min()), 4),
                                  "median": round(float(np.median(stab6)), 4),
                                  "frac_signs_ge_0.5": round(float((stab6 >= 0.5).mean()), 4)},
        },
        "signs": signs_out,
        "NOT_DETERMINED": [
            "No phonetic value (no A_SIGN=/a/, no vowel, no consonant) is assigned to any sign or class.",
            "Vowel identity is NOT recoverable: fused-latent macro vowel AUC=%.3f (perm-p=%.3f); K=2 and "
            "K=6 partitions do not align with the vowel benchmark beyond chance (see grade_vs_phonetic_benchmark)."
            % (fused_vowel_auc, fused_vowel_p),
            "C/V split is NOT recoverable value-independently: the wave-1 position->C/V axis is REFUTED "
            "(multiplicity + oriented null); any C/V AUC here is reported, not credited.",
            "No secure value seed exists (SEED_A=0); seed-propagation gains are a frequency artifact (D3).",
            "Cross-script value transfer is NULL; the classes are relative structure internal to Linear A.",
            "Class labels are ANONYMOUS; C2_0/C2_1/C6_j carry ordering only from KMeans, no external meaning.",
        ],
    }

    def _ser(o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        raise TypeError(str(type(o)))

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "D_la_posterior.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=_ser, ensure_ascii=False)

    # compact console summary
    print("D5 RELATIVE POSTERIOR")
    print("n_signs=%d  K_latent=%d  B_used=%d" % (n, K, b_used))
    print("fused_vowel_auc=%.4f perm_p=%.4f  fused_cv_auc=%.4f" % (fused_vowel_auc, fused_vowel_p, fused_cv_auc))
    print("K2 grade vs vowel: adjMI=%.4f p=%.4f | vs CV: adjMI=%.4f p=%.4f"
          % (grade2["vs_vowel"]["adjusted_mi"], grade2["vs_vowel"]["perm_p"],
             grade2["vs_CV"]["adjusted_mi"], grade2["vs_CV"]["perm_p"]))
    print("K6 grade vs vowel: adjMI=%.4f p=%.4f | vs CV: adjMI=%.4f p=%.4f"
          % (grade6["vs_vowel"]["adjusted_mi"], grade6["vs_vowel"]["perm_p"],
             grade6["vs_CV"]["adjusted_mi"], grade6["vs_CV"]["perm_p"]))
    print("K2 stability mean=%.3f median=%.3f min=%.3f  >=0.8: %.2f  >=0.9: %.2f"
          % (stab2.mean(), np.median(stab2), stab2.min(), (stab2 >= 0.8).mean(), (stab2 >= 0.9).mean()))
    print("K6 stability mean=%.3f  >=0.5: %.2f" % (stab6.mean(), (stab6 >= 0.5).mean()))
    print("LOO K2 agreement:", loo)
    print("K2 class sizes:", [(p["anon_class"], p["n"]) for p in prof2])
    print("affix roles:", dict(Counter(a["role_anonymous"] for a in affix)))
    return out


if __name__ == "__main__":
    run()
