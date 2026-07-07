#!/usr/bin/env python3
"""D1 — Multi-view latent model of ANONYMOUS relative classes on Linear A.

Combines ONLY independently-audited channels into a single latent multi-view representation of
Linear A signs, with EXPLICIT missing-channel handling, then measures which channels carry signal
on LA versus which are null. Latent classes are ANONYMOUS relative structure: no phonetic value is
ever assigned to a class. Known LB syllabic values (parsed from the conventional transliteration of
each sign) are used ONLY as an external grading benchmark for the channels/fusion — never as a model
INPUT feature. Every view is a pure distributional / structural statistic over sign identities.

Channels (views):
  POSITION      6 feats  (initial_rate, final_rate, mean_pos, lone_rate, lnbr_ent, rnbr_ent)  [wave-1: frequency-confounded]
  FREQUENCY     1 feat   (log_freq)                                                            [nuisance / confound, reported separately]
  SUBSTITUTION  3 feats  (sub_degree, sub_support, sub_final_frac)  from C_la_graph long-frame graph  [wave-2: underpowered on LA]
  MORPHOLOGY    3 feats  (prefix_stems, suffix_stems, mid_stems)     recomputed affixation      [wave-2: LA's real axis is word-INITIAL]
  FORMULA       3 feats  (f_initial_rate, f_final_rate, f_mean_pos)  slots in SEG_FORMULA
  SITE          3 feats  (n_sites, site_entropy, ht_fraction)        provenance dispersion
  SHAPE         capped   (F1: circular = LB-homophony judgment; NOT independently value-calibratable; excluded from value grading)

Missing-channel handling: per (sign, view) present/absent mask; absent -> view-column mean imputation
with an explicit per-view missingness indicator carried into the fused matrix.

Benchmark = the two contrasts wave-1/2 studied: (A) 5-way VOWEL recovery (macro one-vs-rest CV-AUC),
(B) pure-vowel-sign vs consonantal (C/V). Each channel is graded pre- and post-frequency-residualization
(regress every feature on log_freq) so a frequency artifact (the wave-1 position finding) is exposed.

Seed 20260708. Non-circular. Imports audited primitives from a1_recompute.
"""
from __future__ import annotations
import json, math, os, re, sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
WT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, WT)
sys.path.insert(0, HERE)
from a1_recompute import logreg, auc, standardize  # audited primitives

SEED = 20260708
np.random.seed(SEED)
VOWELS = ["A", "E", "I", "O", "U"]

# ---------------------------------------------------------------------------------------------------
# benchmark parse: sign transliteration -> (consonant, vowel).  GRADING LABEL ONLY, never an input.
# ---------------------------------------------------------------------------------------------------
SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
CONS = ["D", "J", "K", "M", "N", "P", "Q", "R", "S", "T", "W", "Z"]

def parse_value(sign: str):
    """Return (consonant, vowel) for a clean CV/V syllabogram, else None. Strips subscript variants."""
    s = sign.translate(SUB)
    s = re.sub(r"\d+$", "", s)              # RA2 -> RA, A3 -> A
    if s in VOWELS:
        return ("", s)                      # pure-vowel sign
    if len(s) == 2 and s[0] in CONS and s[1] in VOWELS:
        return (s[0], s[1])
    return None

# ---------------------------------------------------------------------------------------------------
# load LA data
# ---------------------------------------------------------------------------------------------------
def load_units(path):
    return json.load(open(path))["units"]

def build_channels():
    gwords = load_units(os.path.join(DATA, "segmentations", "SEG_GORILA_WORD.json"))
    fwords = load_units(os.path.join(DATA, "segmentations", "SEG_FORMULA.json"))
    graph = json.load(open(os.path.join(DATA, "C_la_graph.json")))

    # ---- POSITION + FREQUENCY (over GORILA words) ----
    init = Counter(); fin = Counter(); tot = Counter(); pos = defaultdict(float); lone = Counter()
    lnb = defaultdict(Counter); rnb = defaultdict(Counter)
    prefix = defaultdict(set); suffix = defaultdict(set); mid = defaultdict(set)  # MORPHOLOGY: distinct stems
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

    # ---- FORMULA slots (over SEG_FORMULA units) ----
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

    # ---- SUBSTITUTION graph (long-frame) : per-sign degree/support/final-frac ----
    sub_deg = Counter(); sub_sup = Counter(); sub_finw = defaultdict(float); sub_finn = Counter()
    for e in graph["sign_substitution_graph"]["top_edges"]:
        a, b = e["signs"]
        w = e["w_long_frame"]; ff = e["final_fraction"]
        for x in (a, b):
            sub_deg[x] += 1; sub_sup[x] += w; sub_finw[x] += ff * w; sub_finn[x] += w

    # assemble per-sign channel dicts (raw; presence tracked per view)
    views = {"POSITION": {}, "FREQUENCY": {}, "SUBSTITUTION": {}, "MORPHOLOGY": {},
             "FORMULA": {}, "SITE": {}}
    for s in tot:
        f = tot[s]
        views["POSITION"][s] = [init[s] / f, fin[s] / f, pos[s] / f, lone[s] / f,
                                ent(lnb[s]), ent(rnb[s])]
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

# ---------------------------------------------------------------------------------------------------
# grading machinery (uses audited logreg/auc; binary OVR macro-AUC with CV)
# ---------------------------------------------------------------------------------------------------
def _cv_auc_binary(Xs, y, k=5, seed=SEED, l2=1.0):
    n = len(y)
    rng = np.random.RandomState(seed)
    order = rng.permutation(n)
    oof = np.zeros(n)
    for f in range(k):
        te = [order[i] for i in range(n) if i % k == f]
        tr = [order[i] for i in range(n) if i % k != f]
        w, b = logreg(Xs[tr], y[tr], l2=l2)
        oof[te] = Xs[te] @ w + b
    return auc(list(oof), list(y))

def macro_vowel_auc(Xm, vowels, seed=SEED):
    """Mean over the 5 vowels of one-vs-rest CV-AUC. Xm = standardized feature matrix (signs x feats)."""
    Xs, _, _ = standardize(Xm)
    aucs = []
    for v in VOWELS:
        y = np.array([1.0 if vv == v else 0.0 for vv in vowels])
        if y.sum() < 2 or y.sum() > len(y) - 2:
            continue
        a = _cv_auc_binary(Xs, y, seed=seed)
        if a is not None:
            aucs.append(a)
    return float(np.mean(aucs)) if aucs else None

def cv_contrast_auc(Xm, is_vowel_sign, seed=SEED):
    Xs, _, _ = standardize(Xm)
    y = np.array([1.0 if b else 0.0 for b in is_vowel_sign])
    if y.sum() < 2 or y.sum() > len(y) - 2:
        return None
    return _cv_auc_binary(Xs, y, seed=seed)

def residualize_on_freq(Xm, logf):
    """Regress every column of Xm on log_freq (+intercept) and return residuals (frequency removed)."""
    A = np.column_stack([np.ones(len(logf)), np.asarray(logf)])
    R = np.zeros_like(Xm)
    for j in range(Xm.shape[1]):
        beta, *_ = np.linalg.lstsq(A, Xm[:, j], rcond=None)
        R[:, j] = Xm[:, j] - A @ beta
    return R

def perm_p(observed, statfn, vowels, n=500, seed=SEED):
    rng = np.random.RandomState(seed)
    vv = list(vowels)
    hits = 0; tot = 0
    for _ in range(n):
        rng.shuffle(vv)
        a = statfn(list(vv))
        if a is not None:
            tot += 1
            if a >= observed:
                hits += 1
    return (hits + 1) / (tot + 1)

def perm_p_cv(observed, Xm, is_vsign, n=1000, seed=SEED):
    """Two-sided-ish permutation p for the C/V contrast: shuffle the pure-vowel-sign labels."""
    if observed is None:
        return None
    rng = np.random.RandomState(seed)
    b = list(is_vsign); hits = 0; tot = 0
    for _ in range(n):
        rng.shuffle(b)
        a = cv_contrast_auc(Xm, b)
        if a is not None:
            tot += 1
            if max(a, 1 - a) >= max(observed, 1 - observed):
                hits += 1
    return (hits + 1) / (tot + 1)

# ---------------------------------------------------------------------------------------------------
# fused latent multi-view model  (missing-channel: mean impute + mask indicators; PCA -> KMeans)
# ---------------------------------------------------------------------------------------------------
def kmeans(Xz, k, seed=SEED, iters=200, restarts=12):
    rng = np.random.RandomState(seed)
    best = None
    for _ in range(restarts):
        idx = rng.choice(len(Xz), k, replace=False)
        C = Xz[idx].copy()
        for _i in range(iters):
            d = ((Xz[:, None, :] - C[None, :, :]) ** 2).sum(2)
            lab = d.argmin(1)
            newC = np.array([Xz[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
            if np.allclose(newC, C):
                C = newC; break
            C = newC
        inertia = ((Xz - C[lab]) ** 2).sum()
        if best is None or inertia < best[0]:
            best = (inertia, lab.copy())
    return best[1]

def ami(a, b):
    """Adjusted mutual information between two labelings."""
    a = np.asarray(a); b = np.asarray(b)
    n = len(a)
    ua = np.unique(a); ub = np.unique(b)
    cont = np.array([[np.sum((a == x) & (b == y)) for y in ub] for x in ua], float)
    ai = cont.sum(1); bj = cont.sum(0)
    def H(p):
        p = p[p > 0] / p.sum()
        return -np.sum(p * np.log(p))
    with np.errstate(divide="ignore", invalid="ignore"):
        mi = 0.0
        for i in range(len(ua)):
            for j in range(len(ub)):
                if cont[i, j] > 0:
                    mi += (cont[i, j] / n) * np.log(n * cont[i, j] / (ai[i] * bj[j]))
    Ha, Hb = H(ai), H(bj)
    # expected MI (Vinh 2010) — approximate via permutation instead for robustness
    return mi, Ha, Hb

def ami_perm(labels, truth, seed=SEED, n=500):
    mi_obs, Ha, Hb = ami(labels, truth)
    denom = max((Ha + Hb) / 2, 1e-12)
    nmi = mi_obs / denom
    rng = np.random.RandomState(seed)
    t = list(truth); hits = 0
    exp = 0.0
    for _ in range(n):
        rng.shuffle(t)
        m, _, _ = ami(labels, t)
        exp += m
        if m >= mi_obs:
            hits += 1
    exp /= n
    adj = (mi_obs - exp) / (denom - exp) if denom > exp else 0.0
    return {"nmi": round(nmi, 4), "adjusted_mi": round(adj, 4),
            "mi_obs": round(mi_obs, 4), "mi_null_mean": round(exp, 4),
            "perm_p": round((hits + 1) / (n + 1), 4)}

# ---------------------------------------------------------------------------------------------------
def run():
    views, tot = build_channels()

    # graded sign set: clean CV/V syllabograms with freq>=THRESH (power) present in POSITION view
    THRESH = 8
    graded = sorted(s for s in views["POSITION"]
                    if parse_value(s) and tot[s] >= THRESH)
    cons = {s: parse_value(s)[0] for s in graded}
    vow = {s: parse_value(s)[1] for s in graded}
    vowels = [vow[s] for s in graded]
    is_vsign = [cons[s] == "" for s in graded]
    logf = np.array([views["FREQUENCY"][s][0] for s in graded])

    VIEW_ORDER = ["POSITION", "FREQUENCY", "SUBSTITUTION", "MORPHOLOGY", "FORMULA", "SITE"]
    VIEW_STATUS = {
        "POSITION": "wave1: frequency-confounded (position->C/V REFUTED)",
        "FREQUENCY": "nuisance/confound channel (kept separate)",
        "SUBSTITUTION": "wave2: consonant-held axis validated on LB, underpowered on LA",
        "MORPHOLOGY": "wave2: LA's real axis (word-INITIAL affixation), anonymous",
        "FORMULA": "administrative slot structure",
        "SITE": "provenance dispersion",
    }

    # ---- per-channel signal, pre + post frequency-residualization ----
    channel_report = {}
    for vn in VIEW_ORDER:
        d = views[vn]
        present = [s in d for s in graded]
        cov = sum(present) / len(graded)
        # signs present in this view (for grading restricted to present signs)
        idx = [i for i, s in enumerate(graded) if present[i]]
        if len(idx) < 8 or len(set(vowels[i] for i in idx)) < 2:
            channel_report[vn] = {"coverage": round(cov, 3), "n_present": len(idx),
                                  "status_prior": VIEW_STATUS[vn], "verdict": "UNDERPOWERED_TOO_SPARSE"}
            continue
        Xm = np.array([d[graded[i]] for i in idx], float)
        vsub = [vowels[i] for i in idx]
        csub = [is_vsign[i] for i in idx]
        lfsub = logf[idx]

        vowel_auc = macro_vowel_auc(Xm, vsub)
        vowel_p = perm_p(vowel_auc, lambda vv: macro_vowel_auc(Xm, vv), vsub) if vowel_auc else None
        cv_auc_v = cv_contrast_auc(Xm, csub)
        cv_p = perm_p_cv(cv_auc_v, Xm, csub)
        # frequency-residualized
        Xr = residualize_on_freq(Xm, lfsub)
        vowel_auc_r = macro_vowel_auc(Xr, vsub)
        cv_auc_r = cv_contrast_auc(Xr, csub)

        # verdict at alpha=0.05 with frequency-robustness check
        if vowel_auc and vowel_p is not None and vowel_p <= 0.05 and vowel_auc_r and vowel_auc_r >= 0.55:
            verdict = "SIGNAL_FREQ_ROBUST"
        elif vowel_auc and vowel_p is not None and vowel_p <= 0.05:
            verdict = "SIGNAL_BUT_FREQUENCY_ARTIFACT"  # collapses after residualization
        else:
            verdict = "NULL"
        channel_report[vn] = {
            "coverage": round(cov, 3), "n_present": len(idx),
            "status_prior": VIEW_STATUS[vn],
            "vowel_macro_auc": round(vowel_auc, 4) if vowel_auc else None,
            "vowel_perm_p": vowel_p,
            "vowel_macro_auc_freq_residualized": round(vowel_auc_r, 4) if vowel_auc_r else None,
            "cv_contrast_auc": round(cv_auc_v, 4) if cv_auc_v else None,
            "cv_contrast_perm_p": round(cv_p, 4) if cv_p else None,
            "cv_contrast_auc_freq_residualized": round(cv_auc_r, 4) if cv_auc_r else None,
            "cv_note": ("pure-vowel-sign vs consonantal rests on only %d pure-vowel signs; this is the "
                        "wave-1 position->C/V contrast, already REFUTED under multiplicity+oriented-null "
                        "-- not re-credited here" % sum(csub)),
            "verdict": verdict,
        }

    # ---- SHAPE channel: documented, capped, NOT value-gradable (F1 circular) ----
    f1 = json.load(open(os.path.join(DATA, "F1_decompose.json")))
    shape_report = {
        "coverage": f1["channel_meta"]["shape"]["coverage"],
        "status_prior": "F1: circular (grade = LB-homophony judgment); capped <=0.75; NOT independently calibratable",
        "verdict": "CAPPED_NOT_VALUE_GRADABLE",
        "note": "Present as a view in principle but excluded from value grading: any vowel/consonant it "
                "predicts is the same latent LB-identity fact it is graded on. Confidence capped <=0.75.",
    }

    # ---- FUSED latent multi-view model (explicit missing handling) ----
    # Core fusion excludes raw FREQUENCY (confound) and SHAPE (capped); includes POSITION, SUBSTITUTION,
    # MORPHOLOGY, FORMULA, SITE with per-view mean imputation + missingness indicator columns.
    fuse_views = ["POSITION", "SUBSTITUTION", "MORPHOLOGY", "FORMULA", "SITE"]
    cols = []; colnames = []; masks = []; maskn = []
    for vn in fuse_views:
        d = views[vn]
        present = np.array([1.0 if s in d else 0.0 for s in graded])
        dim = len(next(iter(d.values())))
        M = np.zeros((len(graded), dim))
        for i, s in enumerate(graded):
            if s in d:
                M[i] = d[s]
        # standardize present rows, impute missing to 0 (=view mean after standardization)
        if present.sum() > 1:
            pr = present.astype(bool)
            mu = M[pr].mean(0); sd = M[pr].std(0) + 1e-9
            Mz = (M - mu) / sd
            Mz[~pr] = 0.0
        else:
            Mz = M * 0.0
        cols.append(Mz); colnames += [f"{vn}:{j}" for j in range(dim)]
        masks.append(present.reshape(-1, 1)); maskn.append(f"{vn}:present")
    Xfused = np.hstack(cols + masks)
    fused_feat_names = colnames + maskn

    # PCA via SVD on centered fused matrix
    Xc = Xfused - Xfused.mean(0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = (S ** 2) / (S ** 2).sum()
    K = int(np.searchsorted(np.cumsum(var), 0.80) + 1)  # #components for 80% variance
    K = max(3, min(K, 8))
    scores = U[:, :K] * S[:K]

    # grade fused latent scores vs vowel benchmark (pre / post freq-residualization)
    fused_vowel_auc = macro_vowel_auc(scores, vowels)
    fused_vowel_p = perm_p(fused_vowel_auc, lambda vv: macro_vowel_auc(scores, vv), vowels)
    scores_r = residualize_on_freq(scores, logf)
    fused_vowel_auc_r = macro_vowel_auc(scores_r, vowels)
    fused_cv_auc = cv_contrast_auc(scores, is_vsign)
    fused_cv_p = perm_p_cv(fused_cv_auc, scores, is_vsign)

    # anonymous relative classes: KMeans on latent scores (standardized)
    Sz, _, _ = standardize(scores)
    NCLASS = 6
    lab = kmeans(Sz, NCLASS)
    classes = []
    for j in range(NCLASS):
        members = [graded[i] for i in range(len(graded)) if lab[i] == j]
        classes.append({"anon_class": f"LATENT_{j:02d}", "n": len(members), "signs": members})
    # grade anonymous classes vs vowel + vs C/V partitions (benchmark only; classes stay anonymous)
    vowel_int = [VOWELS.index(v) for v in vowels]
    cv_int = [1 if b else 0 for b in is_vsign]
    ami_vowel = ami_perm(lab, vowel_int)
    ami_cv = ami_perm(lab, cv_int)

    # ---- assemble output ----
    out = {
        "task": "D1_multiview_relative_features",
        "seed": SEED, "as_of": "2026-07-07",
        "non_circular": "known LB values parsed from transliteration used ONLY as grading benchmark; "
                        "every model input is a distributional/structural statistic over sign identities.",
        "graded_sign_set": {
            "threshold_freq_ge": THRESH, "n_signs": len(graded),
            "n_pure_vowel_signs": sum(is_vsign), "signs": graded,
            "vowel_counts": dict(Counter(vowels)),
        },
        "channel_signal": channel_report,
        "shape_channel": shape_report,
        "fused_latent_model": {
            "fused_views": fuse_views,
            "fused_feature_dim": Xfused.shape[1],
            "n_feature_cols": len(colnames), "n_mask_cols": len(maskn),
            "missing_handling": "per-view mean imputation (=0 after within-view standardization) + explicit "
                                "per-view present/absent indicator columns carried into fusion",
            "pca_components_for_80pct_var": int(np.searchsorted(np.cumsum(var), 0.80) + 1),
            "K_latent_used": K,
            "explained_variance_top": [round(float(v), 4) for v in var[:K]],
            "fused_vowel_macro_auc": round(fused_vowel_auc, 4) if fused_vowel_auc else None,
            "fused_vowel_perm_p": round(fused_vowel_p, 4),
            "fused_vowel_macro_auc_freq_residualized": round(fused_vowel_auc_r, 4) if fused_vowel_auc_r else None,
            "fused_cv_contrast_auc": round(fused_cv_auc, 4) if fused_cv_auc else None,
            "fused_cv_contrast_perm_p": round(fused_cv_p, 4) if fused_cv_p else None,
            "n_class": NCLASS,
            "anonymous_classes": classes,
            "class_vs_vowel_benchmark": ami_vowel,
            "class_vs_CV_benchmark": ami_cv,
        },
    }

    # ranked channel summary
    ranked = sorted(
        [(vn, r.get("vowel_macro_auc")) for vn, r in channel_report.items() if r.get("vowel_macro_auc")],
        key=lambda t: -t[1])
    out["channel_ranking_by_vowel_auc"] = [{"view": vn, "vowel_auc": a,
                                            "verdict": channel_report[vn]["verdict"]} for vn, a in ranked]

    def _ser(o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        raise TypeError(str(type(o)))

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "D1_multiview.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=_ser, ensure_ascii=False)
    print(json.dumps(out, indent=1, default=_ser, ensure_ascii=False))
    return out


if __name__ == "__main__":
    run()
