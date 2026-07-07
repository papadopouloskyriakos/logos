#!/usr/bin/env python3
"""D3 — SEED-PROPAGATION AUDIT.

Audits the Foundry WP5(b) claim: "~3-4 CORRECT C/V seeds -> held-out AUC 0.78 (kv=3)
-> 0.82/0.87 (kv=4 pos / pos+sub) on known-truth Linear B ... the mechanism is validated".
(Source: experiments/linear_a_foundry/scripts/wp5_reduced_seed_bootstrap.py,
 data/wp5_reduced_seed_bootstrap.json, reports/WP4_WP5_CROSSSCRIPT_ANCHORS.md line 24.)

Audited EXACTLY like WP-A audited position->C/V. Independent reimplementation of the
label-spreading pipeline (features, kNN-RBF affinity, Zhou-2004 closed form, AUC); the
substitution-graph builder is imported from the Foundry (read-only data reuse) so the
pos+sub 0.87 can be reproduced faithfully.

NON-CIRCULAR (Art. XII): known LB {A,E,I,O,U} label seeds and grade held-out AUC ONLY;
no phonetic value is ever a model feature. Frequency (log_freq) is dropped from the
propagation features exactly as the Foundry did.

Audit axes:
  R  RECONSTRUCT the published numbers (small-draw pipeline).
  L  LEAK diagnosis: with 5 vowels total, kv=4 seeds reveal 80% of the positive class and
     leave >=1 held-out vowel; AUC is a rank stat on ~1 positive; recall is the honest metric.
  E  FULL enumeration of vowel-seed combos + many consonant draws -> honest CI (vs n_draws=5).
  S  Leave-one-seed-out sensitivity (drop each vowel / consonant seed).
  A  ADVERSARIAL wrong seeds (label true consonants as vowels & vice versa).
  N  RANDOM-SEED null at matched counts (the null Foundry ran for regime A but NOT for the
     pivotal regime-B 0.87).
  F  FREQUENCY-ARTIFACT test (WP-A carryover): does pure frequency ranking / freq-matched
     random seeds / a no-propagation seed-centroid baseline already reach 0.87?

Deterministic seed 20260708.
"""
from __future__ import annotations
import json
import math
import os
import sys
from collections import Counter
from itertools import combinations

import numpy as np
from scipy.spatial.distance import cdist

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

FOUNDRY = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals/experiments/linear_a_foundry/scripts"
sys.path.insert(0, FOUNDRY)
import wp3_2_scribal_substitution as SUB  # substitution_graph builder (read-only)  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, ".."))
DATA_DIR = os.path.join(CAMP, "data")
REP_DIR = os.path.join(CAMP, "reports")
SEED = 20260708
FREQ_MIN = 20
LB_VOWELS = {"A", "E", "I", "O", "U"}
POS_IDX = [0, 1, 2, 3, 4, 5]     # initial,final,mean_pos,lone,lnbr_ent,rnbr_ent (drop log_freq)
KNN = 7
ALPHA = 0.2
BETA_SUB = 0.5


# ------------------------------------------------------------------ features (independent)
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
        F[s] = [init[s] / tot[s], fin[s] / tot[s], pos[s] / tot[s], lone[s] / tot[s],
                ent(lnb.get(s, Counter())), ent(rnb.get(s, Counter())), math.log(tot[s])]
    return F, tot


def knn_rbf(Xs, k=KNN):
    D = cdist(Xs, Xs)
    p = D[D > 0]
    sigma = np.median(p) if p.size else 1.0
    Wfull = np.exp(-(D ** 2) / (2 * sigma ** 2))
    idx = np.argsort(D, 1)[:, 1:k + 1]
    M = np.zeros_like(Wfull)
    for i in range(Xs.shape[0]):
        M[i, idx[i]] = Wfull[i, idx[i]]
    M = np.maximum(M, M.T)
    np.fill_diagonal(M, 0.0)
    return M


def sub_affinity(signs, edge_weight):
    idx = {s: i for i, s in enumerate(signs)}
    n = len(signs)
    W = np.zeros((n, n))
    for e, w in edge_weight.items():
        u, v = tuple(e)
        if u in idx and v in idx:
            val = math.log1p(w)
            W[idx[u], idx[v]] = val
            W[idx[v], idx[u]] = val
    m = W.max()
    if m > 0:
        W = W / m
    return W


def label_spread(W, Y, alpha=ALPHA):
    d = W.sum(1); d = np.where(d <= 0, 1e-9, d)
    dinv = 1.0 / np.sqrt(d)
    S = (W * dinv[:, None]) * dinv[None, :]
    n = W.shape[0]
    return (1 - alpha) * np.linalg.solve(np.eye(n) - alpha * S, Y)


def auc(scores, labels):
    p = [s for s, l in zip(scores, labels) if l]
    q = [s for s, l in zip(scores, labels) if not l]
    if not p or not q:
        return None
    return sum((a > b) + 0.5 * (a == b) for a in p for b in q) / (len(p) * len(q))


def spread_eval(W, truth, v_seed, c_seed):
    n = W.shape[0]
    Y = np.zeros((n, 2))
    for i in v_seed:
        Y[i, 0] = 1.0
    for i in c_seed:
        Y[i, 1] = 1.0
    F = label_spread(W, Y)
    vscore = F[:, 0] - F[:, 1]
    seedset = set(v_seed) | set(c_seed)
    ho = [i for i in range(n) if i not in seedset]
    hs = [vscore[i] for i in ho]
    ht = [truth[i] for i in ho]
    a = auc(hs, ht)
    nv = int(sum(ht))
    rec = None
    if nv > 0:
        order = sorted(range(len(ho)), key=lambda j: -hs[j])[:nv]
        rec = sum(ht[j] for j in order) / nv
    return {"auc": a, "recall": rec, "n_heldout": len(ho), "n_heldout_vowels": nv, "vscore": vscore, "ho": ho}


# ------------------------------------------------------------------ build LB
def build():
    seqs, _, _ = X.load_b_damos()
    F, tot = features(seqs)
    signs = sorted((s for s in F if math.exp(F[s][6]) >= FREQ_MIN), key=lambda s: -tot[s])
    Xm = np.array([[F[s][c] for c in POS_IDX] for s in signs], float)
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    truth = [1 if s in LB_VOWELS else 0 for s in signs]
    edge_weight, _, _ = SUB.substitution_graph(seqs)
    Wpos = knn_rbf(Xs)
    Wsub = sub_affinity(signs, edge_weight)
    return signs, tot, Xs, truth, Wpos, Wsub, F


def summ(a):
    a = [x for x in a if x is not None]
    if not a:
        return None
    return {"mean": round(float(np.mean(a)), 4), "sd": round(float(np.std(a)), 4),
            "min": round(float(np.min(a)), 4), "max": round(float(np.max(a)), 4), "n": len(a)}


def run():
    signs, tot, Xs, truth, Wpos, Wsub, F = build()
    n = len(signs)
    v_idx = [i for i in range(n) if truth[i]]
    c_idx = [i for i in range(n) if not truth[i]]
    Wboth = Wpos + BETA_SUB * Wsub
    rng = np.random.default_rng(SEED)
    channels = {"pos": Wpos, "pos+sub": Wboth}

    out = {"meta": {"seed": SEED, "n_signs": n, "n_vowels": len(v_idx),
                    "vowel_signs": [signs[i] for i in v_idx],
                    "freq_min": FREQ_MIN, "alpha": ALPHA, "knn": KNN, "beta_sub": BETA_SUB,
                    "audited_claim": "3-4 correct C/V seeds -> held-out AUC 0.78(kv3)/0.82(kv4 pos)/0.87(kv4 pos+sub)",
                    "note": "independent reimpl; SUB graph imported read-only; LB values grade ONLY"}}

    # ============ R: RECONSTRUCT the published small-draw pipeline (faithful) =================
    recon = {}
    for ch, W in channels.items():
        rows = []
        for kv in (1, 2, 3, 4):
            kc = max(kv, 3)
            v_combos = list(combinations(v_idx, kv))
            rr = np.random.default_rng(SEED + kv)
            picks = v_combos if len(v_combos) <= 10 else [tuple(rr.choice(v_idx, kv, replace=False)) for _ in range(10)]
            aucs, recs, nhv = [], [], []
            for vc in picks:
                cc = list(rr.choice(c_idx, kc, replace=False))
                r = spread_eval(W, truth, list(vc), cc)
                aucs.append(r["auc"]); recs.append(r["recall"]); nhv.append(r["n_heldout_vowels"])
            rows.append({"kv": kv, "kc": kc, "n_draws": len(picks),
                         "auc_mean": round(float(np.mean(aucs)), 4),
                         "auc_min": round(float(np.min(aucs)), 4),
                         "recall_mean": round(float(np.mean([x for x in recs if x is not None])), 4),
                         "mean_heldout_vowels": round(float(np.mean(nhv)), 2)})
        recon[ch] = rows

    # ============ E: FULL enumeration + many consonant draws (honest CI) ======================
    N_CDRAW = 60
    full = {}
    for ch, W in channels.items():
        rows = []
        for kv in (1, 2, 3, 4):
            kc = max(kv, 3)
            aucs, recs = [], []
            rr = np.random.default_rng(SEED + 7 * kv)
            for vc in combinations(v_idx, kv):        # ALL vowel combos
                for _ in range(N_CDRAW):
                    cc = list(rr.choice(c_idx, kc, replace=False))
                    r = spread_eval(W, truth, list(vc), cc)
                    aucs.append(r["auc"]); recs.append(r["recall"])
            rows.append({"kv": kv, "kc": kc, "auc": summ(aucs),
                         "recall": summ([x for x in recs if x is not None]),
                         "n_heldout_vowels": len(v_idx) - kv})
        full[ch] = rows

    # ============ L: LEAK signature — AUC vs fraction of positive class revealed =============
    # For each kv, held-out vowels = 5-kv. Show AUC rises as you reveal more of the 5 vowels.
    leak = []
    for kv in (1, 2, 3, 4):
        pr = full["pos+sub"][kv - 1]
        leak.append({"kv_vowel_seeds": kv, "frac_positive_class_revealed": round(kv / len(v_idx), 3),
                     "n_heldout_vowels": len(v_idx) - kv,
                     "auc_mean_pos+sub": pr["auc"]["mean"], "recall_mean_pos+sub": pr["recall"]["mean"]})

    # ============ S: leave-one-seed-out sensitivity ==========================================
    # Fix the kv=4 vowel set (all but the least-frequent vowel) + a fixed consonant set; drop each.
    vseed4 = sorted(v_idx, key=lambda i: -tot[signs[i]])[:4]
    cseed4 = c_idx[:4]                       # 4 most-frequent consonants (deterministic)
    loso = {}
    for ch, W in channels.items():
        base = spread_eval(W, truth, vseed4, cseed4)
        drops = []
        for i in vseed4:
            vs = [x for x in vseed4 if x != i]
            r = spread_eval(W, truth, vs, cseed4)
            drops.append({"dropped_vowel_seed": signs[i], "auc_without": round(r["auc"], 4),
                          "delta_vs_base": round((r["auc"] or 0) - (base["auc"] or 0), 4),
                          "n_heldout_vowels": r["n_heldout_vowels"]})
        cdrops = []
        for i in cseed4:
            cs = [x for x in cseed4 if x != i]
            r = spread_eval(W, truth, vseed4, cs)
            cdrops.append({"dropped_cons_seed": signs[i], "auc_without": round(r["auc"], 4),
                           "delta_vs_base": round((r["auc"] or 0) - (base["auc"] or 0), 4)})
        loso[ch] = {"base_auc": round(base["auc"], 4), "base_n_heldout_vowels": base["n_heldout_vowels"],
                    "vowel_seed_drops": drops, "cons_seed_drops": cdrops}

    # ============ A: adversarial wrong seeds =================================================
    # Label true consonants as VOWEL seeds and true vowels as CONSONANT seeds (kv=4/kc=4).
    adv = {}
    rr = np.random.default_rng(SEED + 999)
    for ch, W in channels.items():
        aucs = []
        for _ in range(40):
            wrong_v = list(rr.choice(c_idx, 4, replace=False))    # consonants mislabelled vowel
            wrong_c = list(rr.choice(v_idx, min(4, len(v_idx)), replace=False))  # vowels mislabelled cons
            r = spread_eval(W, truth, wrong_v, wrong_c)
            aucs.append(r["auc"])
        adv[ch] = {"adversarial_wrong_seed_auc": summ(aucs),
                   "interpretation": "AUC<0.5 => seeds drive the score (sanity); AUC~0.5 => seeds inert"}

    # ============ N: RANDOM-SEED null at matched counts (regime B — the missing null) =========
    # kv=4/kc=4: draw 4 random 'vowel' seeds + 4 random 'consonant' seeds (any signs), propagate,
    # grade held-out AUC vs TRUE labels. Does labelling the CORRECT vowels beat random labelling?
    N_NULL = 500
    randnull = {}
    for ch, W in channels.items():
        # observed: correct 4 most-freq vowels seeded vowel, 4 random consonants seeded cons (avg)
        rr2 = np.random.default_rng(SEED + 3)
        obs = np.mean([spread_eval(W, truth, vseed4, list(rr2.choice(c_idx, 4, replace=False)))["auc"]
                       for _ in range(30)])
        nulls = []
        rr3 = np.random.default_rng(SEED + 55)
        for _ in range(N_NULL):
            allidx = list(range(n)); rr3.shuffle(allidx)
            vs = allidx[:4]; cs = allidx[4:8]
            a = spread_eval(W, truth, vs, cs)["auc"]
            if a is not None:
                nulls.append(a)
        mu = float(np.mean(nulls)); sdv = float(np.std(nulls))
        p = (sum(1 for x in nulls if x >= obs) + 1) / (len(nulls) + 1)
        randnull[ch] = {"obs_correct_seed_auc": round(float(obs), 4),
                        "random_seed_null": summ(nulls),
                        "z": round((obs - mu) / sdv, 3) if sdv > 0 else None,
                        "p_value": round(p, 4), "n_null": len(nulls)}

    # ============ F: FREQUENCY-ARTIFACT test (the WP-A carryover) =============================
    # F1: pure frequency ranking of ALL signs -> AUC vs truth (NO seeds, NO propagation).
    freq_scores = [-i for i in range(n)]        # signs already sorted desc by freq
    f1_freq_auc = auc(freq_scores, truth)
    # F2: pure single-feature initial_rate ranking (WP-A's artifact feature), NO seeds/propagation.
    init_scores = [F[s][0] for s in signs]
    f2_init_auc = auc(init_scores, truth)
    # F3: frequency-MATCHED random seeds — draw 'vowel' seeds whose frequency ranks match the true
    #     vowels' ranks (+-3), so seeds are as high-freq as real vowels but NOT the real vowels.
    v_ranks = sorted(v_idx)                      # index == freq rank (0 = most frequent)
    rr4 = np.random.default_rng(SEED + 22)
    fm_aucs = []
    for _ in range(300):
        picked = []
        for vr in v_ranks[:4]:
            cand = [j for j in c_idx if abs(j - vr) <= 4 and j not in picked]
            if not cand:
                cand = [j for j in c_idx if j not in picked]
            picked.append(int(rr4.choice(cand)))
        cc = list(rr4.choice([j for j in c_idx if j not in picked], 4, replace=False))
        fm_aucs.append(spread_eval(Wboth, truth, picked, cc)["auc"])
    # F4: no-propagation seed-centroid baseline — score held-out sign by dist to vowel-seed centroid
    #     minus dist to consonant-seed centroid (pure feature similarity, NO graph diffusion).
    def centroid_eval(v_seed, c_seed):
        vc = Xs[v_seed].mean(0); cc_ = Xs[c_seed].mean(0)
        seedset = set(v_seed) | set(c_seed)
        ho = [i for i in range(n) if i not in seedset]
        sc = [float(np.linalg.norm(Xs[i] - cc_) - np.linalg.norm(Xs[i] - vc)) for i in ho]
        return auc(sc, [truth[i] for i in ho])
    cen_aucs = []
    rr5 = np.random.default_rng(SEED + 33)
    for vc in combinations(v_idx, 4):
        for _ in range(30):
            cc = list(rr5.choice(c_idx, 4, replace=False))
            cen_aucs.append(centroid_eval(list(vc), cc))
    freq_art = {
        "F1_pure_frequency_ranking_auc_no_seeds_no_prop": round(f1_freq_auc, 4),
        "F2_pure_initial_rate_ranking_auc_no_seeds_no_prop": round(f2_init_auc, 4),
        "F3_freq_matched_random_seed_auc_pos+sub": summ(fm_aucs),
        "F4_no_propagation_seed_centroid_auc_pos": summ(cen_aucs),
        "seed_prop_kv4_pos+sub_auc": full["pos+sub"][3]["auc"]["mean"],
        "interpretation": ("If F1/F2 (no seeds) already >= the seed-prop AUC, the '0.87' carries no "
                           "information beyond the frequency ordering WP-A flagged as an artifact."),
    }

    out.update({
        "R_reconstruction_small_draw": recon,
        "E_full_enumeration_honest_ci": full,
        "L_leak_signature_auc_vs_class_revealed": leak,
        "S_leave_one_seed_out": loso,
        "A_adversarial_wrong_seeds": adv,
        "N_random_seed_null_regimeB": randnull,
        "F_frequency_artifact": freq_art,
    })

    # ============ VERDICT ====================================================================
    kv4 = full["pos+sub"][3]["auc"]["mean"]
    freq_beats = f1_freq_auc >= kv4 - 0.01     # pure frequency matches/exceeds the seed-prop headline
    recall4 = full["pos+sub"][3]["recall"]["mean"]
    randnull_ns = all(randnull[c]["p_value"] > 0.05 for c in channels) if False else None
    reasons = []
    reasons.append(f"pure frequency ranking (no seeds, no propagation) AUC={round(f1_freq_auc,3)} "
                   f">= seed-prop kv4 pos+sub AUC={round(kv4,3)}" if freq_beats else
                   f"frequency ranking AUC={round(f1_freq_auc,3)} < seed-prop AUC={round(kv4,3)}")
    reasons.append(f"initial_rate ranking (WP-A artifact feature) alone AUC={round(f2_init_auc,3)} — no seeds")
    reasons.append(f"kv=4 reveals {round(4/len(v_idx),2)} of the {len(v_idx)}-vowel positive class; "
                   f"only {len(v_idx)-4} held-out vowel(s); recall@k={round(recall4,3) if recall4 else 0.0} "
                   f"(AUC is a rank stat on ~1 positive)")
    if freq_beats:
        verdict = "SEED_PROPAGATION_FREQUENCY_ARTIFACT"
    else:
        verdict = "SEED_PROPAGATION_VALIDATED"
    out["verdict"] = verdict
    out["verdict_reasons"] = reasons

    os.makedirs(DATA_DIR, exist_ok=True)
    def _ser(o):
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        raise TypeError(str(type(o)))
    # drop non-serializable vscore/ho arrays (they were never stored in out)
    with open(os.path.join(DATA_DIR, "D3_seed_audit.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=_ser)
    print(json.dumps({"verdict": verdict, "reasons": reasons,
                      "F1_freq_auc": round(f1_freq_auc, 4), "F2_init_auc": round(f2_init_auc, 4),
                      "kv4_pos+sub": kv4, "F3_freqmatched": summ(fm_aucs)["mean"],
                      "F4_centroid": summ(cen_aucs)["mean"],
                      "randnull": {c: randnull[c]["p_value"] for c in channels}}, indent=1, default=_ser))
    return out


if __name__ == "__main__":
    run()
