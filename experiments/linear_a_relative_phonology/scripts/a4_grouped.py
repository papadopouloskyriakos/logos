#!/usr/bin/env python3
"""A4 — GROUPED / LEAKAGE-CONTROLLED evaluation of C/V recovery on opaque Linear B.

Audits the Foundry WP1/WP3 claim (single-feature position AUC 0.744; 7-feature 7-fold CV
AUC 0.835) and the A3 replication (M1 sign-grouped 7-fold AUC 0.828, but logfreq-only 0.838
=> the "signal" may be a frequency typological prior, not position/distribution).

The classified UNIT is the sign (77 LB signs freq>=20; 5 true vowels A,E,I,O,U). The feature
vector of every sign is ESTIMATED FROM A CORPUS. "Related units leaking between train and test"
therefore has two distinct meanings, both tested here:

  (1) FEATURE-DOMAIN leave-one-group-out (site / series / formula-family(series+sub) / scribe /
      chronology / document / word-family): the classifier is TRAINED on sign features estimated
      from the COMPLEMENT corpus, then must recover C/V from sign features RE-ESTIMATED on the
      held-out group's corpus alone. Genuine cross-domain generalization — a signal that is an
      artifact of a few documents/sites/scribes/formulae will not transfer.

  (2) SIGN-UNIT leave-one-frequency-band-out: whole frequency bands of signs are held out, so
      train and test signs occupy DISJOINT frequency ranges. This directly attacks the log_freq
      confound: if C/V is only "vowels are frequent", the model cannot rank vowels vs consonants
      WITHIN a band it never trained on, and AUC collapses toward chance.

Every grouping is reported vs (a) the ungrouped in-sample baseline, (b) the A3 sign-grouped
7-fold baseline (reproduced here), and (c) a label-permutation null (shuffle the 77 sign labels,
rerun the FULL grouped procedure). Non-circular: known LB vowel labels grade benchmarks ONLY;
they are never a model input. Deterministic seed 20260708. Writes data/A4_grouped.json.
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
LB_VOWELS = {"A", "E", "I", "O", "U"}
FEATS = ["initial_rate", "final_rate", "mean_pos", "lone_rate", "lnbr_ent", "rnbr_ent", "log_freq"]
POS_FEATS = [f for f in FEATS if f != "log_freq"]  # position/distribution only (no frequency)
MIN_FREQ = 20        # global freq threshold -> canonical 77-sign set (matches A3)
N_PERM = 200
DAMOS_ITEMS = os.path.join(MAIN, "corpus", "bronze", "linearb", "damos", "items.jsonl")


# ---------------------------------------------------------------- features (identical to A3)
def features(seqs, feat_names=FEATS, min_freq=None):
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


def matrix(F, signs, feat_names):
    return np.array([[F[s][f] for f in feat_names] for s in signs], dtype=float)


# ---------------------------------------------------------------- DAMOS with per-wordform metadata
def load_b_damos_meta():
    """Re-parse DAMOS items into (wordform, meta) using the SAME wordform extractor as data.py."""
    rows = []
    with open(DAMOS_ITEMS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            it = rec.get("item", {}) or {}
            content = it.get("content", "") or ""
            site = it.get("ishort")
            series = it.get("seriessicura") or it.get("series")
            sub = it.get("subseriessicura") or it.get("subseries") or ""
            formula = (series or "") + (sub or "")
            hand = it.get("hand_easy") or it.get("handpreptt3")
            hand = hand if (hand and hand.strip() and hand.strip() != "-") else None
            chrono = it.get("chronogroup")
            doc = str(it.get("id"))
            meta = {"site": site, "series": series, "formula": formula,
                    "scribe": hand, "chrono": chrono, "doc": doc}
            for w in X._damos_wordforms(content):
                rows.append((w, meta))
    return rows


# ---------------------------------------------------------------- classifier helpers
def fit_predict_auc(F_tr, tr_signs, ytr, F_te, te_signs, yte, feat_names):
    """Train logistic on complement-domain features, score held-out-domain features. Directed AUC."""
    if len(set(ytr.tolist())) < 2 or len(set(yte.tolist())) < 2:
        return None
    Xtr = matrix(F_tr, tr_signs, feat_names)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    Xtr = (Xtr - mu) / sd
    clf = LogisticRegression(C=1.0, max_iter=2000).fit(Xtr, ytr)
    Xte = (matrix(F_te, te_signs, feat_names) - mu) / sd
    scores = clf.decision_function(Xte)
    return float(roc_auc_score(yte, scores)), scores


def sign_grouped_cv(F, signs, y, feat_names, k=7, seed=SEED):
    """Reproduce A3 M1: sign-grouped k-fold (each sign in exactly one held-out fold), directed OOF AUC."""
    Xm = matrix(F, signs, feat_names)
    mu, sd = Xm.mean(0), Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    rng = np.random.RandomState(seed)
    order = rng.permutation(len(signs))
    folds = [order[i::k] for i in range(k)]
    oof = np.zeros(len(signs))
    for te in folds:
        tr = np.array([i for i in range(len(signs)) if i not in set(te.tolist())])
        if len(set(y[tr].tolist())) < 2:
            oof[te] = 0.0
            continue
        clf = LogisticRegression(C=1.0, max_iter=2000).fit(Xs[tr], y[tr])
        oof[te] = clf.decision_function(Xs[te])
    return float(roc_auc_score(y, oof))


# ---------------------------------------------------------------- feature-domain LOGO / K-fold engine
def logo_eval2(rows, key, canon_signs, y_map, feat_names,
               min_group_words, min_test_freq, min_test_vowels, min_test_cons,
               kfold=None, seed=SEED):
    """Concrete LOGO / grouped-K-fold. If kfold is set, groups are bucketed into kfold folds
    (whole groups per fold) and each fold's corpus is the test domain; else true leave-one-group-out."""
    by_group = defaultdict(list)
    for w, meta in rows:
        g = meta[key]
        if g is None:
            continue
        by_group[g].append(w)

    if kfold:
        # assign whole groups to folds, sized to balance wordform counts
        gsorted = sorted(by_group, key=lambda g: -len(by_group[g]))
        fold_words = [[] for _ in range(kfold)]
        load = [0] * kfold
        for g in gsorted:
            j = int(np.argmin(load))
            fold_words[j].extend(by_group[g])
            load[j] += len(by_group[g])
        test_units = {f"fold{j}": fold_words[j] for j in range(kfold)}
    else:
        test_units = {g: ws for g, ws in by_group.items() if len(ws) >= min_group_words}

    # precompute per-unit test-feature dict and complement-feature dict
    all_group_of = []  # not needed
    units = sorted(test_units, key=lambda u: (-len(test_units[u]), str(u)))
    canon_set = set(canon_signs)
    cached = []
    for u in units:
        in_seqs = test_units[u]
        in_ids = set(id(w) for w in in_seqs)
        comp_seqs = [w for w, _ in rows if id(w) not in in_ids]
        Fin = features(in_seqs)
        Fout = features(comp_seqs)
        tr_signs = [s for s in canon_signs if s in Fout and Fout[s]["freq"] >= MIN_FREQ]
        te_signs = [s for s in canon_signs if s in Fin and Fin[s]["freq"] >= min_test_freq and s in Fout]
        v = sum(1 for s in te_signs if s in LB_VOWELS)
        c = len(te_signs) - v
        if v < min_test_vowels or c < min_test_cons or len(tr_signs) < 10:
            continue
        cached.append((u, Fin, Fout, tr_signs, te_signs, len(in_seqs)))

    def run_once(ymap):
        per = {}
        pooled_scores = []; pooled_labels = []
        for u, Fin, Fout, tr_signs, te_signs, nwords in cached:
            ytr = np.array([ymap[s] for s in tr_signs], dtype=float)
            yte = np.array([ymap[s] for s in te_signs], dtype=float)
            r = fit_predict_auc(Fout, tr_signs, ytr, Fin, te_signs, yte, feat_names)
            if r is None:
                continue
            auc, scores = r
            per[u] = {"auc": round(auc, 3), "n_test_signs": len(te_signs),
                      "n_test_vowels": int(yte.sum()), "n_words": nwords}
            pooled_scores.extend(scores.tolist()); pooled_labels.extend(yte.tolist())
        pooled = None
        if pooled_labels and 0 < sum(pooled_labels) < len(pooled_labels):
            pooled = float(roc_auc_score(pooled_labels, pooled_scores))
        aucs = [d["auc"] for d in per.values()]
        return {"per_group": per, "n_groups_scored": len(per),
                "mean_group_auc": round(float(np.mean(aucs)), 3) if aucs else None,
                "median_group_auc": round(float(np.median(aucs)), 3) if aucs else None,
                "pooled_auc": round(pooled, 3) if pooled is not None else None}

    obs = run_once(y_map)
    # permutation null on pooled AUC
    signs_all = canon_signs
    yv = np.array([y_map[s] for s in signs_all])
    rng = np.random.RandomState(seed + 7)
    null_pooled = []; null_mean = []
    for _ in range(N_PERM):
        perm = rng.permutation(yv)
        pm = {s: float(perm[i]) for i, s in enumerate(signs_all)}
        r = run_once(pm)
        if r["pooled_auc"] is not None:
            null_pooled.append(r["pooled_auc"])
        if r["mean_group_auc"] is not None:
            null_mean.append(r["mean_group_auc"])
    def pval(obsv, nulls):
        if obsv is None or not nulls:
            return None
        return round((sum(1 for a in nulls if a >= obsv) + 1) / (len(nulls) + 1), 4)
    obs["perm_p_pooled"] = pval(obs["pooled_auc"], null_pooled)
    obs["perm_p_mean"] = pval(obs["mean_group_auc"], null_mean)
    obs["null_pooled_mean"] = round(float(np.mean(null_pooled)), 3) if null_pooled else None
    obs["null_pooled_95"] = round(float(np.percentile(null_pooled, 95)), 3) if null_pooled else None
    obs["null_mean_mean"] = round(float(np.mean(null_mean)), 3) if null_mean else None
    obs["null_mean_95"] = round(float(np.percentile(null_mean, 95)), 3) if null_mean else None
    return obs


# ---------------------------------------------------------------- sign-unit frequency-band LOGO
def freq_band_logo(F, signs, y, feat_names, n_bands=4, seed=SEED):
    """Hold out whole log-frequency bands of SIGNS. Train/test signs have DISJOINT freq ranges.
    OOF directed AUC over all signs; permutation null shuffles labels."""
    lf = np.array([F[s]["log_freq"] for s in signs])
    order = np.argsort(lf)
    bands = np.array_split(order, n_bands)  # equal-count bands along the freq axis
    Xm = matrix(F, signs, feat_names)

    def oof_auc(yv):
        oof = np.full(len(signs), np.nan)
        for b in bands:
            te = set(b.tolist())
            tr = np.array([i for i in range(len(signs)) if i not in te])
            teb = np.array(sorted(te))
            if len(set(yv[tr].tolist())) < 2:
                continue
            mu, sd = Xm[tr].mean(0), Xm[tr].std(0) + 1e-9
            clf = LogisticRegression(C=1.0, max_iter=2000).fit((Xm[tr] - mu) / sd, yv[tr])
            oof[teb] = clf.decision_function((Xm[teb] - mu) / sd)
        mask = ~np.isnan(oof)
        if len(set(yv[mask].tolist())) < 2:
            return None
        return float(roc_auc_score(yv[mask], oof[mask]))

    obs = oof_auc(y)
    rng = np.random.RandomState(seed + 11)
    nulls = []
    for _ in range(N_PERM):
        a = oof_auc(rng.permutation(y))
        if a is not None:
            nulls.append(a)
    p = round((sum(1 for a in nulls if a >= obs) + 1) / (len(nulls) + 1), 4) if (obs is not None and nulls) else None
    band_info = []
    for b in bands:
        sgn = [signs[i] for i in b]
        band_info.append({"n": len(sgn), "n_vowels": sum(1 for s in sgn if s in LB_VOWELS),
                          "log_freq_range": [round(float(lf[b].min()), 2), round(float(lf[b].max()), 2)]})
    return {"oof_auc": round(obs, 3) if obs is not None else None, "n_bands": n_bands,
            "perm_p": p, "null_mean": round(float(np.mean(nulls)), 3) if nulls else None,
            "null_95": round(float(np.percentile(nulls, 95)), 3) if nulls else None,
            "bands": band_info}


# ---------------------------------------------------------------- chronological holdout
def chrono_holdout(rows, canon_signs, y_map, feat_names, seed=SEED):
    """Split corpus into early/late halves by chronogroup, train features on one, test on other."""
    chr_words = defaultdict(list)
    for w, meta in rows:
        c = meta["chrono"]
        if c is None:
            continue
        chr_words[c].append((w, c))
    # order chronogroups; DAMOS chronogroup ~ ordinal period code. Split by cumulative wordform median.
    cs = sorted(chr_words, key=lambda c: c)
    counts = [(c, len(chr_words[c])) for c in cs]
    total = sum(n for _, n in counts)
    cum = 0; early = set()
    for c, n in counts:
        if cum < total / 2:
            early.add(c)
        cum += n
    early_seqs = [w for w, meta in rows if meta["chrono"] in early]
    late_seqs = [w for w, meta in rows if (meta["chrono"] is not None and meta["chrono"] not in early)]

    def one(tr_seqs, te_seqs):
        Ftr = features(tr_seqs); Fte = features(te_seqs)
        tr_signs = [s for s in canon_signs if s in Ftr and Ftr[s]["freq"] >= MIN_FREQ]
        te_signs = [s for s in canon_signs if s in Fte and Fte[s]["freq"] >= 5 and s in Ftr]
        ytr = np.array([y_map[s] for s in tr_signs], dtype=float)
        yte = np.array([y_map[s] for s in te_signs], dtype=float)
        r = fit_predict_auc(Ftr, tr_signs, ytr, Fte, te_signs, yte, feat_names)
        auc = None if r is None else r[0]
        # permutation null
        yv = np.array([y_map[s] for s in canon_signs])
        rng = np.random.RandomState(seed + 5)
        nulls = []
        for _ in range(N_PERM):
            perm = rng.permutation(yv); pm = {s: float(perm[i]) for i, s in enumerate(canon_signs)}
            rr = fit_predict_auc(Ftr, tr_signs, np.array([pm[s] for s in tr_signs], float),
                                 Fte, te_signs, np.array([pm[s] for s in te_signs], float), feat_names)
            if rr is not None:
                nulls.append(rr[0])
        p = round((sum(1 for a in nulls if a >= auc) + 1) / (len(nulls) + 1), 4) if (auc is not None and nulls) else None
        return {"auc": round(auc, 3) if auc is not None else None, "n_test_signs": len(te_signs),
                "n_test_vowels": int(yte.sum()), "n_train_words": len(tr_seqs), "n_test_words": len(te_seqs),
                "perm_p": p, "null_95": round(float(np.percentile(nulls, 95)), 3) if nulls else None}

    return {"early_chronogroups": sorted(early), "n_early_words": len(early_seqs), "n_late_words": len(late_seqs),
            "train_early_test_late": one(early_seqs, late_seqs),
            "train_late_test_early": one(late_seqs, early_seqs)}


# ---------------------------------------------------------------- word-family key on rows
def add_word_family(rows):
    """Word family := 2-sign prefix (shared stem/onset). Attach to a copy of meta."""
    out = []
    for w, meta in rows:
        fam = "|".join(w[:2]) if len(w) >= 2 else "|".join(w)
        m2 = dict(meta); m2["wordfam"] = fam
        out.append((w, m2))
    return out


def run():
    rows = load_b_damos_meta()
    all_seqs = [w for w, _ in rows]
    F = features(all_seqs)
    canon = sorted(s for s in F if F[s]["freq"] >= MIN_FREQ)
    y = np.array([1.0 if s in LB_VOWELS else 0.0 for s in canon])
    y_map = {s: (1.0 if s in LB_VOWELS else 0.0) for s in canon}
    print(f"[data] DAMOS wordforms={len(all_seqs)} canon signs(freq>={MIN_FREQ})={len(canon)} vowels={int(y.sum())}")

    # ---- baselines ----
    base_insample_all = float(roc_auc_score(y, LogisticRegression(C=1.0, max_iter=2000).fit(
        (matrix(F, canon, FEATS) - matrix(F, canon, FEATS).mean(0)) /
        (matrix(F, canon, FEATS).std(0) + 1e-9), y).decision_function(
        (matrix(F, canon, FEATS) - matrix(F, canon, FEATS).mean(0)) /
        (matrix(F, canon, FEATS).std(0) + 1e-9))))
    base_signgrouped_all = sign_grouped_cv(F, canon, y, FEATS)
    base_signgrouped_pos = sign_grouped_cv(F, canon, y, POS_FEATS)
    base_signgrouped_freq = sign_grouped_cv(F, canon, y, ["log_freq"])
    print(f"[base] in-sample(all)={base_insample_all:.3f}  sign-grouped 7f all={base_signgrouped_all:.3f} "
          f"pos-only={base_signgrouped_pos:.3f} logfreq-only={base_signgrouped_freq:.3f}")

    baselines = {
        "ungrouped_in_sample_all_feats": round(base_insample_all, 3),
        "sign_grouped_7fold_all_feats": round(base_signgrouped_all, 3),
        "sign_grouped_7fold_position_only": round(base_signgrouped_pos, 3),
        "sign_grouped_7fold_logfreq_only": round(base_signgrouped_freq, 3),
        "foundry_single_feature_position_auc": 0.744,
        "foundry_7feat_cv_auc": 0.835,
        "a3_M1_all_auc": 0.828,
        "a3_M1_logfreq_only_auc": 0.838,
    }

    rows_wf = add_word_family(rows)

    grouped = {}
    # feature-domain leave-one-group-out
    print("[LOGO] site ..."); grouped["leave_one_site_out"] = {
        "type": "feature_domain_LOGO", "grouping": "site (ishort)",
        "all_feats": logo_eval2(rows, "site", canon, y_map, FEATS, 60, 3, 2, 5),
        "position_only": logo_eval2(rows, "site", canon, y_map, POS_FEATS, 60, 3, 2, 5)}
    print("[LOGO] series ..."); grouped["leave_one_series_out"] = {
        "type": "feature_domain_LOGO", "grouping": "series (seriessicura)",
        "all_feats": logo_eval2(rows, "series", canon, y_map, FEATS, 60, 3, 2, 5),
        "position_only": logo_eval2(rows, "series", canon, y_map, POS_FEATS, 60, 3, 2, 5)}
    print("[LOGO] formula/document-series ..."); grouped["leave_one_series_formula_out"] = {
        "type": "feature_domain_LOGO", "grouping": "document series / formula family (series+subseries)",
        "all_feats": logo_eval2(rows, "formula", canon, y_map, FEATS, 60, 3, 2, 5),
        "position_only": logo_eval2(rows, "formula", canon, y_map, POS_FEATS, 60, 3, 2, 5)}
    print("[LOGO] scribe ..."); grouped["leave_one_scribe_out"] = {
        "type": "feature_domain_LOGO", "grouping": "scribe (hand_easy, '-' excluded)",
        "all_feats": logo_eval2(rows, "scribe", canon, y_map, FEATS, 60, 3, 2, 5),
        "position_only": logo_eval2(rows, "scribe", canon, y_map, POS_FEATS, 60, 3, 2, 5)}
    print("[LOGO] chronogroup ..."); grouped["leave_one_chronogroup_out"] = {
        "type": "feature_domain_LOGO", "grouping": "chronogroup",
        "all_feats": logo_eval2(rows, "chrono", canon, y_map, FEATS, 60, 3, 2, 5),
        "position_only": logo_eval2(rows, "chrono", canon, y_map, POS_FEATS, 60, 3, 2, 5)}
    # grouped K-fold for high-cardinality: document + word-family
    print("[GKF] document (7-fold over documents) ..."); grouped["grouped_kfold_document"] = {
        "type": "feature_domain_grouped_Kfold(7)", "grouping": "document id",
        "all_feats": logo_eval2(rows, "doc", canon, y_map, FEATS, 0, 3, 2, 5, kfold=7),
        "position_only": logo_eval2(rows, "doc", canon, y_map, POS_FEATS, 0, 3, 2, 5, kfold=7)}
    print("[GKF] word-family (7-fold over 2-sign-prefix stems) ..."); grouped["grouped_kfold_word_family"] = {
        "type": "feature_domain_grouped_Kfold(7)", "grouping": "word family (2-sign prefix)",
        "all_feats": logo_eval2(rows_wf, "wordfam", canon, y_map, FEATS, 0, 3, 2, 5, kfold=7),
        "position_only": logo_eval2(rows_wf, "wordfam", canon, y_map, POS_FEATS, 0, 3, 2, 5, kfold=7)}

    # sign-unit frequency-band leave-out (the log_freq confound killer)
    print("[BAND] leave-one-frequency-band-out ...")
    band = {"all_feats": freq_band_logo(F, canon, y, FEATS, n_bands=4),
            "position_only": freq_band_logo(F, canon, y, POS_FEATS, n_bands=4),
            "logfreq_only": freq_band_logo(F, canon, y, ["log_freq"], n_bands=4)}

    # chronological holdout (directional)
    print("[CHRONO] early/late holdout ...")
    chrono = {"all_feats": chrono_holdout(rows, canon, y_map, FEATS),
              "position_only": chrono_holdout(rows, canon, y_map, POS_FEATS)}

    out = {
        "meta": {"seed": SEED, "damos_wordforms": len(all_seqs), "n_signs": len(canon),
                 "n_vowels": int(y.sum()), "min_freq": MIN_FREQ, "n_perm": N_PERM, "feats": FEATS,
                 "note": "known LB vowel values grade benchmarks ONLY, never a model input"},
        "baselines": baselines,
        "feature_domain_grouped": grouped,
        "sign_unit_frequency_band_leaveout": band,
        "chronological_holdout": chrono,
    }
    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(os.path.join(DATA, "A4_grouped.json"), "w"), indent=1)

    # compact console summary
    def gsum(d):
        return {"pooled_auc": d["all_feats"]["pooled_auc"], "p_pooled": d["all_feats"]["perm_p_pooled"],
                "mean_auc": d["all_feats"]["mean_group_auc"], "n": d["all_feats"]["n_groups_scored"],
                "pos_pooled": d["position_only"]["pooled_auc"], "pos_p": d["position_only"]["perm_p_pooled"]}
    print(json.dumps({
        "baselines": baselines,
        "site": gsum(grouped["leave_one_site_out"]),
        "series": gsum(grouped["leave_one_series_out"]),
        "formula": gsum(grouped["leave_one_series_formula_out"]),
        "scribe": gsum(grouped["leave_one_scribe_out"]),
        "chronogroup": gsum(grouped["leave_one_chronogroup_out"]),
        "document_gkf": gsum(grouped["grouped_kfold_document"]),
        "wordfamily_gkf": gsum(grouped["grouped_kfold_word_family"]),
        "freq_band_all": {"auc": band["all_feats"]["oof_auc"], "p": band["all_feats"]["perm_p"]},
        "freq_band_pos": {"auc": band["position_only"]["oof_auc"], "p": band["position_only"]["perm_p"]},
        "freq_band_logfreq": {"auc": band["logfreq_only"]["oof_auc"], "p": band["logfreq_only"]["perm_p"]},
        "chrono_all_e2l": chrono["all_feats"]["train_early_test_late"]["auc"],
        "chrono_all_l2e": chrono["all_feats"]["train_late_test_early"]["auc"],
        "chrono_pos_e2l": chrono["position_only"]["train_early_test_late"]["auc"],
        "chrono_pos_l2e": chrono["position_only"]["train_late_test_early"]["auc"],
    }, indent=1))
    return out


if __name__ == "__main__":
    run()
