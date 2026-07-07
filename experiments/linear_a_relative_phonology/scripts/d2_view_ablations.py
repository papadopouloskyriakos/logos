#!/usr/bin/env python3
"""D2 — VIEW ABLATIONS of the D1 multi-view channels.

Ablate the D1 channels (POSITION, FREQUENCY, MORPHOLOGY, SUBSTITUTION, plus the LA-only FORMULA/SITE,
plus the capped SHAPE) and measure each ablation's CONTRIBUTION to the ANONYMOUS relative partition,
on Linear A AND on a Linear B known-truth control. No phonetic value is ever assigned to a class:
known LB syllabic values are used ONLY as an external grading benchmark (vowel identity, C/V split),
never as a model input. Seed 20260708. Imports audited primitives from a1_recompute and the exact D1
channel builder + grading machinery from d1_multiview (single source of truth, no re-implementation).

Two ablation families per script:
  SINGLE      include ONLY that channel  -> the channel's standalone partition signal
  LEAVE_ONE_OUT drop that channel from the full fused set -> the channel's UNIQUE marginal contribution
plus named COMBINATIONS (structural-3 = POSITION+MORPHOLOGY+SUBSTITUTION, the two wave-2 axes, etc.)
and a RANDOM-feature floor.

Metrics per ablation (all reuse D1 machinery verbatim):
  fused_vowel_macro_auc            one-vs-rest 5-vowel CV-AUC on PCA(fused) latent scores
  fused_vowel_perm_p               label-permutation p for that AUC
  fused_vowel_auc_freq_resid       same AUC after regressing latent scores on log_freq (exposes freq artifact)
  partition_ami_vowel              adjusted-MI of the KMeans anonymous partition vs the vowel benchmark (+perm_p)
  partition_ami_cv                 adjusted-MI vs the (already-REFUTED) pure-vowel-sign/consonantal split

Shape stays CAPPED: its grade IS an LB-homophony (identity) judgment (F1: circular), so it can carry no
independent anonymous-partition signal and is reported, not value-graded.
"""
from __future__ import annotations
import json, math, os, sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
WT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, WT); sys.path.insert(0, MAIN); sys.path.insert(0, HERE)

from a1_recompute import standardize                                    # audited primitive
from d1_multiview import (build_channels, parse_value, macro_vowel_auc, cv_contrast_auc,
                          residualize_on_freq, perm_p, perm_p_cv, kmeans, ami_perm, VOWELS)
from scripts.cross_script import data as X

SEED = 20260708
np.random.seed(SEED)
VP = 300      # vowel-AUC permutation reps
CVP = 300     # C/V-AUC permutation reps
AMIP = 300    # AMI permutation reps
NCLASS = 6

# ---------------------------------------------------------------------------------------------------
# generic channel builder (used for the LB control; LA reuses D1 build_channels verbatim)
# ---------------------------------------------------------------------------------------------------
def ent(c):
    n = sum(c.values())
    return -sum((v / n) * math.log(v / n) for v in c.values()) if n else 0.0

def build_generic(words):
    """POSITION / FREQUENCY / MORPHOLOGY / SUBSTITUTION channels over a wordform corpus (sign-lists)."""
    init = Counter(); fin = Counter(); tot = Counter(); pos = defaultdict(float); lone = Counter()
    lnb = defaultdict(Counter); rnb = defaultdict(Counter)
    prefix = defaultdict(set); suffix = defaultdict(set); mid = defaultdict(set)
    frames = defaultdict(set)          # (left,right) context frame -> set of middle signs (substitution)
    for u in words:
        w = [s for s in u if s]
        L = len(w)
        if L == 0:
            continue
        if L == 1:
            lone[w[0]] += 1
        stem = "".join(w)
        for i, s in enumerate(w):
            tot[s] += 1
            pos[s] += (i / (L - 1)) if L > 1 else 0.5
            l = w[i - 1] if i > 0 else "^"
            r = w[i + 1] if i < L - 1 else "$"
            frames[(l, r)].add(s)
            if i > 0:
                lnb[s][w[i - 1]] += 1
            if i < L - 1:
                rnb[s][w[i + 1]] += 1
        if L >= 2:
            prefix[w[0]].add(stem); suffix[w[-1]].add(stem)
            for s in w[1:-1]:
                mid[s].add(stem)
        init[w[0]] += 1; fin[w[-1]] += 1

    # frame-based substitution graph: signs sharing a (left,right) frame substitute
    sub_deg = defaultdict(set); sub_sup = Counter()
    for (l, r), sset in frames.items():
        if len(sset) < 2:
            continue
        for s in sset:
            for t in sset:
                if t != s:
                    sub_deg[s].add(t)
            sub_sup[s] += len(sset) - 1

    views = {"POSITION": {}, "FREQUENCY": {}, "MORPHOLOGY": {}, "SUBSTITUTION": {}}
    for s in tot:
        f = tot[s]
        views["POSITION"][s] = [init[s] / f, fin[s] / f, pos[s] / f, lone[s] / f, ent(lnb[s]), ent(rnb[s])]
        views["FREQUENCY"][s] = [math.log(f)]
        views["MORPHOLOGY"][s] = [len(prefix[s]), len(suffix[s]), len(mid[s])]
        if s in sub_deg:
            views["SUBSTITUTION"][s] = [len(sub_deg[s]), sub_sup[s], fin[s] / f]
    return views, tot

# ---------------------------------------------------------------------------------------------------
# fusion (mirrors D1 exactly: within-view standardize present rows, impute 0, + present-mask columns)
# ---------------------------------------------------------------------------------------------------
def fuse(views, config, graded):
    cols = []; masks = []
    for vn in config:
        d = views[vn]
        present = np.array([1.0 if s in d else 0.0 for s in graded])
        dim = len(next(iter(d.values())))
        M = np.zeros((len(graded), dim))
        for i, s in enumerate(graded):
            if s in d:
                M[i] = d[s]
        if present.sum() > 1:
            pr = present.astype(bool)
            mu = M[pr].mean(0); sd = M[pr].std(0) + 1e-9
            Mz = (M - mu) / sd; Mz[~pr] = 0.0
        else:
            Mz = M * 0.0
        cols.append(Mz); masks.append(present.reshape(-1, 1))
    return np.hstack(cols + masks)

def pca_scores(Xfused):
    Xc = Xfused - Xfused.mean(0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = (S ** 2) / (S ** 2).sum()
    K = int(np.searchsorted(np.cumsum(var), 0.80) + 1)
    K = max(3, min(K, 8))
    return U[:, :K] * S[:K], K

def grade_config(views, config, graded, vowels, is_vsign, logf, do_perm=True):
    X_ = fuse(views, config, graded)
    scores, K = pca_scores(X_)
    va = macro_vowel_auc(scores, vowels)
    vp = perm_p(va, lambda vv: macro_vowel_auc(scores, vv), vowels, n=VP) if (va and do_perm) else None
    sr = residualize_on_freq(scores, logf)
    var_ = macro_vowel_auc(sr, vowels)
    cva = cv_contrast_auc(scores, is_vsign)
    cvp = perm_p_cv(cva, scores, is_vsign, n=CVP) if (cva and do_perm) else None
    Sz, _, _ = standardize(scores)
    lab = kmeans(Sz, NCLASS)
    vowel_int = [VOWELS.index(v) for v in vowels]
    cv_int = [1 if b else 0 for b in is_vsign]
    ami_v = ami_perm(lab, vowel_int, n=AMIP) if do_perm else None
    ami_c = ami_perm(lab, cv_int, n=AMIP) if do_perm else None
    return {
        "channels": list(config), "fused_dim": int(X_.shape[1]), "K_latent": K,
        "fused_vowel_macro_auc": round(va, 4) if va else None,
        "fused_vowel_perm_p": round(vp, 4) if vp is not None else None,
        "fused_vowel_auc_freq_resid": round(var_, 4) if var_ else None,
        "fused_cv_contrast_auc": round(cva, 4) if cva else None,
        "fused_cv_contrast_perm_p": round(cvp, 4) if cvp is not None else None,
        "partition_ami_vowel": ami_v,
        "partition_ami_cv": ami_c,
    }

def verdict_of(m):
    """Anonymous-partition signal verdict from vowel AUC perm-p + freq-robustness + AMI perm-p."""
    va = m["fused_vowel_macro_auc"]; vp = m["fused_vowel_perm_p"]; vr = m["fused_vowel_auc_freq_resid"]
    ami = m["partition_ami_vowel"]
    ami_p = ami["perm_p"] if ami else 1.0
    ami_adj = ami["adjusted_mi"] if ami else 0.0
    sig_auc = (va is not None and vp is not None and vp <= 0.05)
    sig_ami = (ami_p <= 0.05 and ami_adj > 0)
    freq_robust = (vr is not None and vr >= 0.55)
    if not (sig_auc or sig_ami):
        return "NULL"
    if sig_auc and not freq_robust:
        return "SIGNAL_BUT_FREQUENCY_ARTIFACT"
    return "SIGNAL"

# ---------------------------------------------------------------------------------------------------
def build_graded(views, tot, thresh):
    graded = sorted(s for s in views["POSITION"] if parse_value(s) and tot[s] >= thresh)
    vow = {s: parse_value(s)[1] for s in graded}
    cons = {s: parse_value(s)[0] for s in graded}
    vowels = [vow[s] for s in graded]
    is_vsign = [cons[s] == "" for s in graded]
    logf = np.array([math.log(tot[s]) for s in graded])
    return graded, vowels, is_vsign, logf

def run_script(tag, views, tot, thresh, shared_channels, extra_configs):
    graded, vowels, is_vsign, logf = build_graded(views, tot, thresh)
    # coverage per channel over the graded set
    coverage = {vn: round(sum(1 for s in graded if s in views[vn]) / len(graded), 3) for vn in views}
    present_n = {vn: int(sum(1 for s in graded if s in views[vn])) for vn in views}

    configs = {}
    # SINGLE channels
    for vn in shared_channels:
        configs[f"single__{vn}"] = [vn]
    # LEAVE_ONE_OUT of the full shared set
    full = list(shared_channels)
    configs["FULL_shared"] = full
    for vn in shared_channels:
        loo = [c for c in full if c != vn]
        if loo:
            configs[f"LOO__minus_{vn}"] = loo
    # named combinations
    configs.update(extra_configs)
    # RANDOM floor (gaussian noise, 4 dims) as a chance anchor
    rng = np.random.RandomState(SEED)
    rand_view = {"RANDOM": {s: list(rng.randn(4)) for s in graded}}

    results = {}
    for name, cfg in configs.items():
        cfg = [c for c in cfg if c in views]
        if not cfg:
            continue
        # skip a config if a required channel is too sparse to grade
        if any(present_n[c] < 8 for c in cfg):
            results[name] = {"channels": cfg, "verdict": "UNDERPOWERED_TOO_SPARSE",
                             "n_present_min": min(present_n[c] for c in cfg)}
            continue
        m = grade_config(views, cfg, graded, vowels, is_vsign, logf)
        m["verdict"] = verdict_of(m)
        results[name] = m
    # random floor
    m = grade_config(rand_view, ["RANDOM"], graded, vowels, is_vsign, logf)
    m["verdict"] = verdict_of(m)
    results["RANDOM_floor"] = m

    return {
        "tag": tag, "threshold_freq_ge": thresh,
        "n_graded_signs": len(graded), "n_pure_vowel_signs": int(sum(is_vsign)),
        "vowel_counts": dict(Counter(vowels)),
        "channel_coverage": coverage, "channel_present_n": present_n,
        "graded_signs": graded,
        "ablations": results,
    }

def main():
    # ---- Linear A: reuse D1 channels verbatim (POSITION/FREQUENCY/SUBSTITUTION/MORPHOLOGY/FORMULA/SITE) ----
    views_la, tot_la = build_channels()
    la_shared = ["POSITION", "FREQUENCY", "MORPHOLOGY", "SUBSTITUTION"]
    la_extra = {
        "combo__MORPH+POS": ["MORPHOLOGY", "POSITION"],
        "combo__MORPH+SUB": ["MORPHOLOGY", "SUBSTITUTION"],
        "combo__POS+SUB": ["POSITION", "SUBSTITUTION"],
        "combo__structural3_no_freq": ["POSITION", "MORPHOLOGY", "SUBSTITUTION"],
        "single__FORMULA": ["FORMULA"],
        "single__SITE": ["SITE"],
        "combo__D1_full_5view": ["POSITION", "SUBSTITUTION", "MORPHOLOGY", "FORMULA", "SITE"],
    }
    la = run_script("LINEAR_A", views_la, tot_la, 8, la_shared, la_extra)

    # ---- Linear B known-truth control: generic channels over 13,562 DAMOS wordforms ----
    b_words, _, _ = X.load_b_damos()
    views_lb, tot_lb = build_generic(b_words)
    lb_shared = ["POSITION", "FREQUENCY", "MORPHOLOGY", "SUBSTITUTION"]
    lb_extra = {
        "combo__MORPH+POS": ["MORPHOLOGY", "POSITION"],
        "combo__MORPH+SUB": ["MORPHOLOGY", "SUBSTITUTION"],
        "combo__POS+SUB": ["POSITION", "SUBSTITUTION"],
        "combo__structural3_no_freq": ["POSITION", "MORPHOLOGY", "SUBSTITUTION"],
    }
    lb = run_script("LINEAR_B_CONTROL", views_lb, tot_lb, 20, lb_shared, lb_extra)

    shape_note = {
        "verdict": "CAPPED_CIRCULAR_NOT_VALUE_GRADABLE",
        "cap": 0.75,
        "reason": ("F1: the SHAPE channel's grade IS an LB-homophony (identity) judgment (Salgarella "
                   "stable-11 recovered perfectly, Fisher p=1.6e-5) — the same latent LB-identity fact it "
                   "would predict. It therefore carries NO independent anonymous-partition signal and is "
                   "excluded from value grading in every ablation. Reported, not scored."),
        "source": "data/F1_decompose.json channel_meta.shape",
    }

    out = {
        "task": "D2_view_ablations",
        "seed": SEED, "as_of": "2026-07-07",
        "non_circular": ("known LB values used ONLY as grading benchmark (vowel identity / C-V split); "
                         "every model input is a pure distributional/structural statistic over sign identities. "
                         "LB is a positive control graded on its own known values."),
        "method": {
            "families": ["SINGLE (include-only)", "LEAVE_ONE_OUT (drop-from-full)", "COMBINATIONS", "RANDOM_floor"],
            "shared_channel_space": la_shared,
            "la_only_channels": ["FORMULA", "SITE"],
            "capped_channel": "SHAPE (circular, not value-gradable)",
            "partition_metric": "KMeans(k=%d) anonymous classes on PCA latent scores; graded by AMI vs vowel/CV benchmark" % NCLASS,
            "auc_metric": "one-vs-rest 5-vowel CV-AUC on PCA latent scores; +label-perm p; +freq-residualized AUC",
            "perm_reps": {"vowel_auc": VP, "cv_auc": CVP, "ami": AMIP},
            "note_cv_axis": ("the pure-vowel-sign vs consonantal (C/V) contrast is the wave-1 position->C/V "
                             "axis already REFUTED under multiplicity + oriented null; reported for continuity, "
                             "NOT re-credited."),
            "lb_substitution_note": ("LB SUBSTITUTION is a generic frame-based minimal-pair channel (signs "
                                     "sharing a (left,right) context frame); LA SUBSTITUTION is the audited "
                                     "wave-2 long-frame graph (C_la_graph). Definitions differ; each is "
                                     "internally consistent within its script."),
        },
        "linear_a": la,
        "linear_b_control": lb,
        "shape_channel": shape_note,
    }

    def _ser(o):
        if isinstance(o, (np.bool_,)):   return bool(o)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)):return float(o)
        raise TypeError(str(type(o)))

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "D2_ablations.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=_ser, ensure_ascii=False)
    print(json.dumps(out, indent=1, default=_ser, ensure_ascii=False))
    return out

if __name__ == "__main__":
    main()
