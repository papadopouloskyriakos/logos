#!/usr/bin/env python3
"""A5 — DEGRADATION RESPONSE SURFACE.

Degrade opaque Linear B toward Linear A along SEPARATE axes and measure C/V recovery
(A3-style models) as a function of each axis. Full surface (AUC vs level per axis) +
the two key 2-way interactions (size x seq-length, size x hapax). Identify collapse
axes and locate Linear A's real operating point on each.

Evaluation is NON-CIRCULAR: known LB vowel labels grade the benchmark ONLY; they are
never a model input. The evaluation sign-set is FIXED (the 77 LB signs at freq>=20 in
full LB, 5 of them vowels), so AUC is comparable across every degraded cell -- the
corpus is degraded, the benchmark is held constant, feature ESTIMATES get noisier.

Primary response variable: M1 grouped-by-sign 7-fold logistic CV AUC on all 7 features
(the Foundry headline, reported 0.835). Also reported: M1 position-only AUC (drop
log_freq, the actual distributional channel) and M2 unsupervised GMM AUC (robustness).
Per-level permutation-null 95pct band (n_perm=200) defines "chance"; collapse = the
primary AUC falls within that band.

Deterministic seed 20260708. Writes data/A5_surface.json + reports feed.
"""
import json, math, os, sys
from collections import Counter
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.mixture import GaussianMixture
from sklearn.metrics import roc_auc_score

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
LB_VOWELS = {"A", "E", "I", "O", "U"}
LA_PURE_VOWELS = {"A", "I", "U", "E", "O"}
FEATS = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]
POS_FEATS = [f for f in FEATS if f != "log_freq"]
MIN_FREQ = 20
K = 7
N_PERM = 200


# ----------------------------------------------------------------- features (A3-identical)
def features(seqs):
    init = Counter(); fin = Counter(); tot = Counter(); pos = Counter(); lone = Counter()
    lnb = {}; rnb = {}
    for w in seqs:
        w = [s for s in w if s]
        L = len(w)
        if L == 0:
            continue
        if L == 1:
            lone[w[0]] += 1
        for i, s in enumerate(w):
            tot[s] += 1
            pos[s] += (i / (L - 1)) if L > 1 else 0.5
            if i > 0:
                lnb.setdefault(s, Counter())[w[i - 1]] += 1
            if i < L - 1:
                rnb.setdefault(s, Counter())[w[i + 1]] += 1
        init[w[0]] += 1; fin[w[-1]] += 1

    def ent(c):
        n = sum(c.values())
        return -sum((v / n) * math.log(v / n) for v in c.values()) if n else 0.0

    F = {}
    for s in tot:
        F[s] = {
            "initial_rate": init[s] / tot[s], "final_rate": fin[s] / tot[s],
            "mean_pos": pos[s] / tot[s], "lone_rate": lone[s] / tot[s],
            "lnbr_ent": ent(lnb.get(s, Counter())), "rnbr_ent": ent(rnb.get(s, Counter())),
            "log_freq": math.log(tot[s]), "freq": tot[s],
        }
    return F


def bench_matrix(F, signs, feat_names):
    """Rows for the FIXED benchmark signs; missing sign/feat imputed to column mean (neutral)."""
    rows = []
    present = [s for s in signs if s in F]
    # column means over present benchmark signs (fallback 0 if none)
    col_mean = {}
    for f in feat_names:
        vals = [F[s][f] for s in present]
        col_mean[f] = float(np.mean(vals)) if vals else 0.0
    for s in signs:
        if s in F:
            rows.append([F[s][f] for f in feat_names])
        else:
            rows.append([col_mean[f] for f in feat_names])
    return np.array(rows, dtype=float)


def oriented(a):
    return max(a, 1.0 - a)


def folds_for(n, seed=SEED):
    rng = np.random.RandomState(seed)
    order = rng.permutation(n)
    return [order[i::K] for i in range(K)]


def cv_oof(Xs, labels, folds):
    oof = np.zeros(len(labels))
    for te in folds:
        teset = set(te.tolist())
        tr = np.array([i for i in range(len(labels)) if i not in teset])
        if len(set(labels[tr].tolist())) < 2:
            oof[te] = 0.0
            continue
        clf = LogisticRegression(C=1.0, max_iter=2000)
        clf.fit(Xs[tr], labels[tr])
        oof[te] = clf.decision_function(Xs[te])
    return oof


def m1_auc(Xm, y, folds):
    mu, sd = Xm.mean(0), Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    oof = cv_oof(Xs, y, folds)
    return float(roc_auc_score(y, oof)), Xs


def m1_null95(Xs, y, folds, n_perm=N_PERM, seed=SEED):
    rp = np.random.RandomState(seed + 7)
    nulls = []
    for _ in range(n_perm):
        yp = rp.permutation(y)
        nulls.append(oriented(roc_auc_score(yp, cv_oof(Xs, yp, folds))))
    return float(np.percentile(nulls, 95)), float(np.mean(nulls))


def m2_gmm_auc(Xm, y, seed=SEED, n_init=8):
    Xs = (Xm - Xm.mean(0)) / (Xm.std(0) + 1e-9)
    try:
        gm = GaussianMixture(n_components=2, covariance_type="full", n_init=n_init,
                             random_state=seed, reg_covar=1e-4).fit(Xs)
    except Exception:
        return 0.5
    post = gm.predict_proba(Xs)
    hard = gm.predict(Xs)
    v0 = y[hard == 0].mean() if (hard == 0).any() else 0.0
    v1 = y[hard == 1].mean() if (hard == 1).any() else 0.0
    vcomp = 1 if v1 >= v0 else 0
    return float(oriented(roc_auc_score(y, post[:, vcomp])))


# ----------------------------------------------------------------- corpus transforms
def t_size(seqs, frac, rng):
    n = max(1, int(round(len(seqs) * frac)))
    idx = rng.choice(len(seqs), size=n, replace=False)
    return [seqs[i] for i in idx]


def t_hapax(seqs, p, rng):
    ctr = [0]
    out = []
    for w in seqs:
        nw = []
        for s in w:
            if rng.random() < p:
                ctr[0] += 1
                nw.append(f"__H{ctr[0]}")
            else:
                nw.append(s)
        out.append(nw)
    return out


def t_site_imbalance(seqs, alpha, rng, S=20):
    # partition words into S random groups; resample N draws where group ~ Dirichlet(alpha)
    n = len(seqs)
    grp = rng.integers(0, S, size=n)
    members = [np.where(grp == g)[0] for g in range(S)]
    w = rng.dirichlet(np.ones(S) * alpha)
    out = []
    gsel = rng.choice(S, size=n, p=w)
    for g in gsel:
        m = members[g]
        if len(m) == 0:
            m = np.arange(n)
        out.append(seqs[int(rng.choice(m))])
    return out


def t_dropout(seqs, d, rng):
    out = []
    for w in seqs:
        nw = [s for s in w if rng.random() >= d]
        if nw:
            out.append(nw)
    return out


def t_merge(seqs, g, rng):
    order = list(range(len(seqs)))
    rng.shuffle(order)
    sh = [seqs[i] for i in order]
    out = []
    for i in range(0, len(sh), g):
        chunk = []
        for w in sh[i:i + g]:
            chunk.extend(w)
        if chunk:
            out.append(chunk)
    return out


def t_truncate(seqs, L):
    return [w[:L] for w in seqs if w[:L]]


def t_notation(seqs, q):
    # merge the bottom q-fraction of sign TYPES (by freq) into a single UNK symbol
    tot = Counter(s for w in seqs for s in w)
    types = sorted(tot, key=lambda s: tot[s])  # ascending freq
    k = int(round(q * len(types)))
    merged = set(types[:k])
    out = [["__UNK" if s in merged else s for s in w] for w in seqs]
    return out


# ----------------------------------------------------------------- diagnostics
def diag(seqs):
    seqs = [[s for s in w if s] for w in seqs]
    seqs = [w for w in seqs if w]
    tok = Counter(s for w in seqs for s in w)
    ntok = sum(tok.values())
    types = len(tok)
    hapax = sum(1 for c in tok.values() if c == 1)
    lens = [len(w) for w in seqs]
    return {"n_seq": len(seqs), "n_tokens": ntok, "n_types": types,
            "hapax_type_rate": round(hapax / types, 4) if types else 0.0,
            "mean_len": round(float(np.mean(lens)), 3) if lens else 0.0}


# ----------------------------------------------------------------- cell evaluation
def eval_cell(seqs, signs, y, folds, want_null=False):
    F = features(seqs)
    Xall = bench_matrix(F, signs, FEATS)
    Xpos = bench_matrix(F, signs, POS_FEATS)
    auc_all, Xs_all = m1_auc(Xall, y, folds)
    auc_pos, _ = m1_auc(Xpos, y, folds)
    auc_gmm = m2_gmm_auc(Xall, y)
    res = {"auc_all": round(auc_all, 3), "auc_pos": round(auc_pos, 3), "auc_gmm": round(auc_gmm, 3)}
    if want_null:
        n95, nmean = m1_null95(Xs_all, y, folds)
        res["null95_all"] = round(n95, 3)
        res["null_mean_all"] = round(nmean, 3)
    res["diag"] = diag(seqs)
    return res


def agg(cells):
    """Average a list of eval_cell dicts (same axis level, multiple reps)."""
    keys = ["auc_all", "auc_pos", "auc_gmm"]
    out = {}
    for k in keys:
        v = [c[k] for c in cells]
        out[k] = round(float(np.mean(v)), 3)
        out[k + "_sd"] = round(float(np.std(v)), 3)
    # diagnostics averaged
    dg = {}
    for k in cells[0]["diag"]:
        dg[k] = round(float(np.mean([c["diag"][k] for c in cells])), 3)
    out["diag"] = dg
    if "null95_all" in cells[0]:
        out["null95_all"] = cells[0]["null95_all"]
        out["null_mean_all"] = cells[0]["null_mean_all"]
    return out


def run_axis(name, levels, transform, seqs, signs, y, folds, reps, level_key):
    """transform(seqs, level, rng) -> degraded seqs. Null computed on rep0 of each level."""
    rows = []
    for lv in levels:
        cells = []
        for r in range(reps):
            rng = np.random.default_rng(SEED + hash((name, str(lv), r)) % (2**31))
            deg = transform(seqs, lv, rng)
            cells.append(eval_cell(deg, signs, y, folds, want_null=(r == 0)))
        a = agg(cells)
        a[level_key] = lv
        rows.append(a)
        print(f"  [{name}] {level_key}={lv}: all={a['auc_all']}±{a['auc_all_sd']} "
              f"pos={a['auc_pos']} gmm={a['auc_gmm']} null95={a.get('null95_all')} "
              f"diag={a['diag']}")
    return rows


def main():
    lb_seqs, _, _ = X.load_b_damos()
    lb_seqs = [[s.upper() for s in w if s] for w in lb_seqs]
    lb_seqs = [w for w in lb_seqs if w]
    Ffull = features(lb_seqs)
    signs = sorted(s for s in Ffull if Ffull[s]["freq"] >= MIN_FREQ)  # fixed 77-sign benchmark
    y = np.array([1.0 if s in LB_VOWELS else 0.0 for s in signs])
    folds = folds_for(len(signs))
    print(f"[data] LB words={len(lb_seqs)} bench_signs={len(signs)} vowels={int(y.sum())}")

    baseline = eval_cell(lb_seqs, signs, y, folds, want_null=True)
    print(f"[baseline full-LB] {baseline}")

    LB_TOK = sum(Ffull[s]["freq"] for s in Ffull)

    surface = {}

    # ---- AXIS 1: corpus size (word subsample) ----
    print("[axis] size")
    size_levels = [1.0, 0.5, 0.25, 0.0968, 0.05, 0.025, 0.0125]  # 0.0968 = LA token fraction
    surface["size"] = run_axis("size", size_levels, t_size, lb_seqs, signs, y, folds, reps=5, level_key="frac")

    # ---- AXIS 2: hapax injection ----
    print("[axis] hapax")
    hapax_levels = [0.0, 0.05, 0.1, 0.2, 0.4]
    surface["hapax"] = run_axis("hapax", hapax_levels, t_hapax, lb_seqs, signs, y, folds, reps=5, level_key="inject_p")

    # ---- AXIS 3: site imbalance ----
    print("[axis] site_imbalance")
    site_levels = [1000.0, 1.0, 0.3, 0.1, 0.03]  # Dirichlet alpha; large=uniform, small=imbalanced
    surface["site_imbalance"] = run_axis("site", site_levels, t_site_imbalance, lb_seqs, signs, y, folds,
                                         reps=5, level_key="dirichlet_alpha")

    # ---- AXIS 4: simulated damage (sign dropout) ----
    print("[axis] damage_dropout")
    drop_levels = [0.0, 0.1, 0.2, 0.35, 0.5, 0.7]
    surface["damage_dropout"] = run_axis("dropout", drop_levels, t_dropout, lb_seqs, signs, y, folds,
                                         reps=5, level_key="drop_p")

    # ---- AXIS 5: segmentation uncertainty (merge words -> pseudo-inscriptions) ----
    print("[axis] segmentation_merge")
    merge_levels = [1, 2, 3, 4, 6]  # words concatenated per sequence
    surface["segmentation_merge"] = run_axis("merge", merge_levels, t_merge, lb_seqs, signs, y, folds,
                                             reps=5, level_key="words_per_seq")

    # ---- AXIS 6: missing layout (not a model input -> null axis) ----
    # ---- AXIS 7: missing scribe (not a model input -> null axis) ----
    # The A3 C/V channel uses ONLY intra-sequence distributional features (initial/final/mean_pos/
    # lone/nbr-entropy/log_freq). Layout and scribe are NOT inputs -> removing them is identity.
    surface["missing_layout"] = [{"present": True, **{k: baseline[k] for k in
                                 ("auc_all", "auc_pos", "auc_gmm")}, "note": "layout not a model input"},
                                 {"present": False, **{k: baseline[k] for k in
                                 ("auc_all", "auc_pos", "auc_gmm")},
                                  "note": "identical: layout absent from the C/V feature set"}]
    surface["missing_scribe"] = [{"present": True, **{k: baseline[k] for k in
                                 ("auc_all", "auc_pos", "auc_gmm")}, "note": "scribe not a model input"},
                                 {"present": False, **{k: baseline[k] for k in
                                 ("auc_all", "auc_pos", "auc_gmm")},
                                  "note": "identical: scribe absent from the C/V feature set"}]

    # ---- AXIS 8: short sequence length (truncate) ----
    print("[axis] seq_length_truncate")
    trunc_levels = [99, 6, 5, 4, 3, 2, 1]
    surface["seq_length_truncate"] = run_axis("truncate", trunc_levels,
                                              lambda s, L, rng: t_truncate(s, L),
                                              lb_seqs, signs, y, folds, reps=1, level_key="max_len")

    # ---- AXIS 9: notation loss (merge low-freq types into UNK) ----
    print("[axis] notation_loss")
    notation_levels = [0.0, 0.1, 0.25, 0.5, 0.75]
    surface["notation_loss"] = run_axis("notation", notation_levels,
                                        lambda s, q, rng: t_notation(s, q),
                                        lb_seqs, signs, y, folds, reps=1, level_key="frac_types_merged")

    # ---- INTERACTION A: size x seq-length ----
    print("[interaction] size x seq_length")
    sizes_i = [1.0, 0.25, 0.0968, 0.05]
    seqs_i = [99, 4, 3, 2]
    inter1 = []
    for f in sizes_i:
        for L in seqs_i:
            cells = []
            for r in range(3):
                rng = np.random.default_rng(SEED + hash(("i1", f, L, r)) % (2**31))
                deg = t_truncate(t_size(lb_seqs, f, rng), L)
                cells.append(eval_cell(deg, signs, y, folds, want_null=(r == 0)))
            a = agg(cells); a["frac"] = f; a["max_len"] = L
            inter1.append(a)
            print(f"  [sizexlen] frac={f} max_len={L}: all={a['auc_all']} pos={a['auc_pos']} "
                  f"gmm={a['auc_gmm']} null95={a.get('null95_all')}")
    surface["interaction_size_x_seqlen"] = inter1

    # ---- INTERACTION B: size x hapax ----
    print("[interaction] size x hapax")
    hap_i = [0.0, 0.1, 0.2, 0.4]
    inter2 = []
    for f in sizes_i:
        for p in hap_i:
            cells = []
            for r in range(3):
                rng = np.random.default_rng(SEED + hash(("i2", f, p, r)) % (2**31))
                deg = t_hapax(t_size(lb_seqs, f, rng), p, rng)
                cells.append(eval_cell(deg, signs, y, folds, want_null=(r == 0)))
            a = agg(cells); a["frac"] = f; a["inject_p"] = p
            inter2.append(a)
            print(f"  [sizexhapax] frac={f} inject_p={p}: all={a['auc_all']} pos={a['auc_pos']} "
                  f"gmm={a['auc_gmm']} null95={a.get('null95_all')}")
    surface["interaction_size_x_hapax"] = inter2

    # ---- LINEAR A actual operating point (real corpus, real benchmark) ----
    print("[LA] actual operating point")
    la_seqs = [[s.upper() for s in w if s] for w in X.load_a()[1]]
    la_seqs = [w for w in la_seqs if w]
    LF = features(la_seqs)
    la_signs = sorted(s for s in LF if LF[s]["freq"] >= MIN_FREQ)
    la_y = np.array([1.0 if s in LA_PURE_VOWELS else 0.0 for s in la_signs])
    la_folds = folds_for(len(la_signs))
    la_diag = diag(la_seqs)
    la_op = {"diag": la_diag, "n_signs": len(la_signs), "n_vowels": int(la_y.sum())}
    if 0 < la_y.sum() < len(la_y):
        Xla = bench_matrix(LF, la_signs, FEATS)
        Xlap = bench_matrix(LF, la_signs, POS_FEATS)
        a_all, Xs = m1_auc(Xla, la_y, la_folds)
        a_pos, _ = m1_auc(Xlap, la_y, la_folds)
        n95, nmean = m1_null95(Xs, la_y, la_folds)
        la_op.update({"auc_all": round(a_all, 3), "auc_pos": round(a_pos, 3),
                      "auc_gmm": round(m2_gmm_auc(Xla, la_y), 3),
                      "null95_all": round(n95, 3), "null_mean_all": round(nmean, 3)})
    # LA site imbalance (from full silver inscriptions)
    try:
        insc = json.load(open(os.path.join(MAIN, "corpus", "silver", "inscriptions.json")))
        sc = Counter(x["site"] for x in insc if x.get("signs"))
        v = np.sort(np.array(list(sc.values()), float)); nn = len(v); c = np.cumsum(v)
        la_site_gini = float((nn + 1 - 2 * (c / c[-1]).sum()) / nn)
    except Exception:
        la_site_gini = None

    la_operating_points = {
        "size": {"axis": "corpus size", "LA_value": round(la_diag["n_tokens"] / LB_TOK, 4),
                 "unit": "token fraction vs full LB", "LB_tokens": LB_TOK, "LA_tokens": la_diag["n_tokens"]},
        "hapax": {"axis": "hapax type rate", "LA_value": la_diag["hapax_type_rate"],
                  "LB_full_value": round(baseline["diag"]["hapax_type_rate"], 4)},
        "seq_length": {"axis": "mean sequence length", "LA_value": la_diag["mean_len"],
                       "LB_full_value": baseline["diag"]["mean_len"],
                       "note": "LA is UNSEGMENTED (inscription-level) -> LONGER, not shorter; "
                               "LA's real deficit is the MERGE/segmentation axis, not truncation"},
        "site_imbalance": {"axis": "site Gini", "LA_value": round(la_site_gini, 3) if la_site_gini else None,
                           "note": "Haghia Triada ~63% of inscriptions; extreme imbalance"},
        "damage": {"axis": "sign dropout", "LA_value": "substantial-but-unquantified",
                   "note": "silver strips [ ] ? damage masks; LA lacunae are heavy in practice"},
        "notation_loss": {"axis": "frac types merged", "LA_value": "~0",
                          "note": "LA type inventory (85) ~ LB (89); notation resolution comparable"},
        "layout": {"axis": "layout present", "LA_value": "absent", "note": "not a C/V-channel input -> no effect"},
        "scribe": {"axis": "scribe present", "LA_value": "absent", "note": "not a C/V-channel input -> no effect"},
    }

    out = {
        "meta": {"seed": SEED, "min_freq": MIN_FREQ, "k_folds": K, "n_perm_null": N_PERM,
                 "bench_signs": len(signs), "bench_vowels": int(y.sum()),
                 "primary_metric": "M1 grouped-by-sign 7-fold logistic CV AUC (all 7 features)",
                 "secondary": ["M1 position-only (no log_freq)", "M2 unsupervised GMM AUC"],
                 "collapse_rule": "primary AUC within permutation-null 95pct band",
                 "note": "known LB/LA vowel labels grade benchmark ONLY, never model input; "
                         "benchmark sign-set held FIXED across all degraded cells"},
        "baseline_full_LB": baseline,
        "surface": surface,
        "linear_a_operating_point_measured": la_op,
        "linear_a_axis_positions": la_operating_points,
    }
    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(os.path.join(DATA, "A5_surface.json"), "w"), indent=1)
    print("[LA op]", json.dumps(la_op))
    print("[wrote] data/A5_surface.json")
    return out


if __name__ == "__main__":
    main()
