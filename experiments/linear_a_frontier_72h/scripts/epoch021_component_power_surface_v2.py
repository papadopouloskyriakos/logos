#!/usr/bin/env python3
"""EPOCH-021 -- Component-channel value-recovery identifiability surface, ATTEMPT 2 (redesigned).

Preregistered: epochs/EPOCH-021/prereg.md
plan_hash 397633786d941f96f96d769ea6781c6a7a3a09d85ec4e81fe28b17f9fffa66a6
(frozen 2026-07-08, before any (b,q) cell of this final grid realized)

Redesign of E019 (which returned HARNESS_NOT_VALIDATED: symmetric row/col block amplitude made
"differs only in row" and "differs only in col" pairwise distances numerically identical, so
KMeans(n_clusters=18) reached the SAME globally-optimal inertia via a non-row-respecting partition
as via the true row-partition -- a genuine geometric tie, not an algorithm bug).

FIX 1: row-block gets amplitude A_ROW=1.3, col-block A_COL=1.0 (asymmetric per-dimension scale) --
breaks the exact tie (diagnosed: A_ROW>=1.1 already suffices at oracle).
FIX 2 (b>0 only): per-dimension Fisher-like weight learned from anchors ALONE, generalized to
classes never seen among the anchors via a k=5 nearest-neighbour smoothing over each dimension's
own UNSUPERVISED (label-free) marginal variance -- no privileged block-index knowledge, no
hand-specified row/col split. Seeded weighted K-means: anchors hard-assigned to their true class,
missing classes seeded via weighted-space k-means++ among unlabeled points, Lloyd iterations refine
everything else. b=0 (no anchors, nothing to learn): plain unweighted KMeans on the FIX-1 code.

Same Q axis (7 levels incl. LA's real E013/E018 MRR and LB's real E009 MRR), same B axis
([0,2,4,8,12]), same R=30 replicates/cell, same positive-control bars, same adversarial
shuffled-identity null, same LA operating point (b=0, q=0.24701551940826028) as E019.
Seed 20260708. Claim layer L1 only -- no phonetic value anywhere in this script.
"""
from __future__ import annotations
import hashlib, json, os, time
import numpy as np
from sklearn.cluster import KMeans, kmeans_plusplus
from sklearn.metrics import adjusted_rand_score
from scipy.stats import spearmanr

SEED = 20260708
PLAN_HASH = "397633786d941f96f96d769ea6781c6a7a3a09d85ec4e81fe28b17f9fffa66a6"

N_C, N_V = 18, 5
K = N_C * N_V  # 90
A_ROW, A_COL = 1.3, 1.0  # FIX 1: asymmetric block amplitude (search receipt: diagnosed minimum 1.1)
K_SMOOTH = 5              # FIX 2: nearest-neighbour smoothing width in marginal-variance space

LA_MRR = 0.24701551940826028     # E013/E018 real measured component-channel agg MRR
LB_MRR = 0.39934712069259104     # E009 real measured LB within-script self MRR
Q_LEVELS = [0.15, LA_MRR, 0.30, LB_MRR, 0.55, 0.75, 1.0]
Q_LABELS = ["sub_LA_ref", "LA_measured", "mid1", "LB_within_script", "mid2", "high", "oracle"]
B_LEVELS = [0, 2, 4, 8, 12]
R_REPLICATES = 30
FOOTHOLD = 0.5
ABSOLUTE = 0.9
ADV_FLOOR_BAR = 0.05

CAMP = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h/experiments/linear_a_frontier_72h"
OUTDIR = os.path.join(CAMP, "data", "component_power_surface_v2")
os.makedirs(OUTDIR, exist_ok=True)


def rng_for(*key):
    s = "|".join(str(k) for k in key)
    h = int(hashlib.sha256(f"{SEED}|{s}".encode()).hexdigest()[:16], 16) % (2**32)
    return np.random.default_rng(h)


def onehot(x, n):
    m = np.zeros((len(x), n))
    m[np.arange(len(x)), x] = 1.0
    return m


TRUE_ROW = np.array([i // N_V for i in range(K)])
TRUE_COL = np.array([i % N_V for i in range(K)])
CODE = np.concatenate([A_ROW * onehot(TRUE_ROW, N_C), A_COL * onehot(TRUE_COL, N_V)], axis=1)  # (K, 23)


def retrieval_mrr(sigma, rng, n_trials=30):
    vals = []
    for _ in range(n_trials):
        q = CODE + rng.normal(0, sigma, CODE.shape)
        g = CODE + rng.normal(0, sigma, CODE.shape)
        D = np.linalg.norm(q[:, None, :] - g[None, :, :], axis=2)
        diag = D[np.arange(K), np.arange(K)][:, None]
        ranks = (D < diag).sum(axis=1) + 1
        vals.append(np.mean(1.0 / ranks))
    return float(np.mean(vals))


def calibrate_sigma(target, key, lo=1e-6, hi=2.0, tol=0.004, max_iter=40):
    if target >= 0.999:
        return 0.0, 1.0
    rng = rng_for("calibrate", key)
    achieved = None
    mid = None
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        achieved = retrieval_mrr(mid, rng, n_trials=30)
        if abs(achieved - target) < tol:
            break
        if achieved > target:
            lo = mid
        else:
            hi = mid
    return float(mid), float(achieved)


def fisher_smoothed_weights(X, anchor_idx, anchor_labels, k_smooth=K_SMOOTH):
    """FIX 2, step (a)+(b): per-dim Fisher score from anchors, smoothed via k-NN in
    UNSUPERVISED marginal-variance space so classes never seen among anchors don't collapse
    to zero weight. No block-index privilege: dims are never split by a known row/col split."""
    labs = np.array(anchor_labels)
    Xa = X[anchor_idx]
    classes = sorted(set(labs))
    overall_mean = Xa.mean(axis=0)
    between = np.zeros(X.shape[1])
    within = np.zeros(X.shape[1])
    for c in classes:
        Xc = Xa[labs == c]
        cm = Xc.mean(axis=0)
        between += len(Xc) * (cm - overall_mean) ** 2
        within += ((Xc - cm) ** 2).sum(axis=0) if len(Xc) > 1 else np.zeros(X.shape[1])
    within = np.maximum(within, 1e-3)
    raw_score = between / within
    marg_var = X.var(axis=0)
    D = X.shape[1]
    smoothed = np.zeros(D)
    for d in range(D):
        dist = np.abs(marg_var - marg_var[d])
        nn = np.argsort(dist)[:k_smooth]
        smoothed[d] = raw_score[nn].mean()
    w = smoothed / (smoothed.sum() + 1e-12)
    return w


def recover(query_emb, anchor_idx, anchor_row, anchor_col, n_c, n_v, rng):
    def seeded_weighted_kmeans(labs_list, n_clusters, weights, n_iter=25, n_init=8):
        sw = np.sqrt(weights)
        Xw = query_emb * sw[None, :]
        labs = np.array(labs_list)
        classes = sorted(set(labs))
        n_seen = len(classes)
        n_missing = n_clusters - n_seen
        anchor_set = set(anchor_idx)
        unlabeled_idx = np.array([i for i in range(K) if i not in anchor_set])
        best_inertia = None
        best_labels = None
        for _init in range(n_init):
            cent = np.zeros((n_clusters, Xw.shape[1]))
            cls_to_cent = {}
            for ci, c in enumerate(classes):
                idxs = [anchor_idx[i] for i, l in enumerate(labs) if l == c]
                cent[ci] = Xw[idxs].mean(axis=0)
                cls_to_cent[c] = ci
            if n_missing > 0:
                seed_pts, _ = kmeans_plusplus(
                    Xw[unlabeled_idx], n_clusters=n_missing,
                    random_state=int(rng.integers(0, 2**31)))
                cent[n_seen:] = seed_pts
            fixed_assign = {a: cls_to_cent[l] for a, l in zip(anchor_idx, labs)}
            labels = np.zeros(K, dtype=int)
            for a, ci in fixed_assign.items():
                labels[a] = ci
            for it in range(n_iter):
                Dm = np.linalg.norm(Xw[:, None, :] - cent[None, :, :], axis=2)
                new_labels = Dm.argmin(axis=1)
                for a, ci in fixed_assign.items():
                    new_labels[a] = ci
                converged = np.array_equal(new_labels, labels) and it > 0
                labels = new_labels
                for ci in range(n_clusters):
                    members = Xw[labels == ci]
                    if len(members) > 0:
                        cent[ci] = members.mean(axis=0)
                if converged:
                    break
            inertia = sum(((Xw[labels == ci] - cent[ci]) ** 2).sum() for ci in range(n_clusters))
            if best_inertia is None or inertia < best_inertia:
                best_inertia = inertia
                best_labels = labels.copy()
        return best_labels

    def unsupervised_kmeans(n_clusters, n_init=15):
        best = None
        best_labels = None
        for _ in range(n_init):
            km = KMeans(n_clusters=n_clusters, n_init=1,
                        random_state=int(rng.integers(0, 2**31))).fit(query_emb)
            if best is None or km.inertia_ < best:
                best = km.inertia_
                best_labels = km.labels_
        return best_labels

    if len(anchor_idx) == 0:
        pred_row = unsupervised_kmeans(n_c)
        pred_col = unsupervised_kmeans(n_v)
        return pred_row, pred_col

    w_row = fisher_smoothed_weights(query_emb, anchor_idx, anchor_row)
    w_col = fisher_smoothed_weights(query_emb, anchor_idx, anchor_col)
    pred_row = seeded_weighted_kmeans(anchor_row, n_c, w_row)
    pred_col = seeded_weighted_kmeans(anchor_col, n_v, w_col)
    return pred_row, pred_col


def run_cell(q_val, q_label, b, sigma, adversarial, r_replicates=R_REPLICATES):
    ari_rows, ari_cols, ari_combined = [], [], []
    diag_mrrs = []
    for rep in range(r_replicates):
        rng = rng_for("cell", q_label, b, "adv" if adversarial else "main", rep)
        query_emb = CODE + rng.normal(0, sigma, CODE.shape)
        gallery_emb = CODE + rng.normal(0, sigma, CODE.shape)
        D = np.linalg.norm(query_emb[:, None, :] - gallery_emb[None, :, :], axis=2)
        diag = D[np.arange(K), np.arange(K)][:, None]
        ranks = (D < diag).sum(axis=1) + 1
        diag_mrrs.append(float(np.mean(1.0 / ranks)))

        if adversarial:
            sigma_perm = rng.permutation(K)
            grade_row = TRUE_ROW[sigma_perm]
            grade_col = TRUE_COL[sigma_perm]
        else:
            grade_row = TRUE_ROW
            grade_col = TRUE_COL

        anchor_idx = list(rng.choice(K, size=b, replace=False)) if b > 0 else []
        anchor_row = [int(grade_row[i]) for i in anchor_idx]
        anchor_col = [int(grade_col[i]) for i in anchor_idx]

        pred_row, pred_col = recover(query_emb, anchor_idx, anchor_row, anchor_col, N_C, N_V, rng)

        held_mask = np.ones(K, dtype=bool)
        if anchor_idx:
            held_mask[anchor_idx] = False

        ar = adjusted_rand_score(grade_row[held_mask], pred_row[held_mask])
        ac = adjusted_rand_score(grade_col[held_mask], pred_col[held_mask])
        ari_rows.append(ar)
        ari_cols.append(ac)
        ari_combined.append((ar + ac) / 2.0)

    ari_rows = np.array(ari_rows)
    ari_cols = np.array(ari_cols)
    ari_combined = np.array(ari_combined)
    m = float(ari_combined.mean())
    sd = float(ari_combined.std(ddof=1))
    ci = 1.96 * sd / np.sqrt(r_replicates)
    return {
        "q_val": q_val, "q_label": q_label, "b": b, "sigma": sigma, "adversarial": adversarial,
        "n_replicates": r_replicates,
        "ari_row_mean": float(ari_rows.mean()), "ari_row_sd": float(ari_rows.std(ddof=1)),
        "ari_col_mean": float(ari_cols.mean()), "ari_col_sd": float(ari_cols.std(ddof=1)),
        "ari_combined_mean": m, "ari_combined_sd": sd,
        "ari_combined_ci95_lo": m - ci, "ari_combined_ci95_hi": m + ci,
        "diag_mrr_realized_mean": float(np.mean(diag_mrrs)),
    }


def main():
    t0 = time.time()
    print(f"A_ROW={A_ROW} A_COL={A_COL} K_SMOOTH={K_SMOOTH}")
    print("Calibrating sigma(q) against the asymmetric-amplitude code...")
    sigmas = {}
    calib_records = []
    for qv, ql in zip(Q_LEVELS, Q_LABELS):
        sigma, achieved = calibrate_sigma(qv, ql)
        sigmas[ql] = sigma
        calib_records.append({"q_label": ql, "target_mrr": qv, "sigma": sigma, "achieved_mrr": achieved})
        print(f"  {ql:18s} target={qv:.4f} sigma={sigma:.4f} achieved={achieved:.4f}")

    print("Running main-condition sweep...")
    main_cells = []
    for qv, ql in zip(Q_LEVELS, Q_LABELS):
        for b in B_LEVELS:
            cell = run_cell(qv, ql, b, sigmas[ql], adversarial=False)
            main_cells.append(cell)
            print(f"  MAIN  q={ql:18s} b={b:3d}  ARI_comb={cell['ari_combined_mean']:.4f}"
                  f" (row={cell['ari_row_mean']:.4f} col={cell['ari_col_mean']:.4f})"
                  f"  realized_MRR={cell['diag_mrr_realized_mean']:.4f}")

    print("Running adversarial (shuffled-identity) sweep...")
    adv_cells = []
    for qv, ql in zip(Q_LEVELS, Q_LABELS):
        for b in B_LEVELS:
            cell = run_cell(qv, ql, b, sigmas[ql], adversarial=True)
            adv_cells.append(cell)
    max_adv = max(c["ari_combined_mean"] for c in adv_cells)
    print(f"  max adversarial ARI_combined over all cells = {max_adv:.4f}")

    def cell_lookup(cells, q_label=None, b=None):
        for c in cells:
            if (q_label is None or c["q_label"] == q_label) and (b is None or c["b"] == b):
                yield c

    lb_row = sorted(cell_lookup(main_cells, q_label="LB_within_script"), key=lambda c: c["b"])
    rho_b, p_b = spearmanr([c["b"] for c in lb_row], [c["ari_combined_mean"] for c in lb_row])
    pc_monotonic_b = bool(rho_b >= 0.8)

    b12_row = sorted(cell_lookup(main_cells, b=12), key=lambda c: c["q_val"])
    rho_q, p_q = spearmanr([c["q_val"] for c in b12_row], [c["ari_combined_mean"] for c in b12_row])
    pc_monotonic_q = bool(rho_q >= 0.8)

    oracle_b12 = next(cell_lookup(main_cells, q_label="oracle", b=12))
    pc_oracle = bool(oracle_b12["ari_combined_mean"] >= ABSOLUTE)

    lb_b12 = next(cell_lookup(main_cells, q_label="LB_within_script", b=12))
    pc_lb_point = bool(lb_b12["ari_combined_mean"] >= FOOTHOLD)

    pc_pass = pc_monotonic_b and pc_monotonic_q and pc_oracle and pc_lb_point
    adv_pass = bool(max_adv < ADV_FLOOR_BAR)

    la_cell = next(cell_lookup(main_cells, q_label="LA_measured", b=0))
    m = la_cell["ari_combined_mean"]
    if not adv_pass:
        la_verdict = "SURFACE_CONFOUNDED"
    elif not pc_pass:
        la_verdict = "HARNESS_NOT_VALIDATED"
    elif m < FOOTHOLD:
        la_verdict = "LA_COMPONENT_POINT_BELOW_FOOTHOLD"
    elif m < ABSOLUTE:
        la_verdict = "LA_COMPONENT_POINT_AT_FOOTHOLD"
    else:
        la_verdict = "LA_COMPONENT_POINT_RECOVERS"

    gap_foothold = max(0.0, FOOTHOLD - m)
    gap_absolute = max(0.0, ABSOLUTE - m)

    def first_crossing_by_q(bar):
        out = {}
        for ql in Q_LABELS:
            row = sorted(cell_lookup(main_cells, q_label=ql), key=lambda c: c["b"])
            hit = next((c["b"] for c in row if c["ari_combined_mean"] >= bar), None)
            out[ql] = hit
        return out

    def first_crossing_by_b(bar):
        out = {}
        for b in B_LEVELS:
            row = sorted(cell_lookup(main_cells, b=b), key=lambda c: c["q_val"])
            hit = next((c["q_label"] for c in row if c["ari_combined_mean"] >= bar), None)
            out[str(b)] = hit
        return out

    contour_foothold_by_q = first_crossing_by_q(FOOTHOLD)
    contour_foothold_by_b = first_crossing_by_b(FOOTHOLD)
    contour_absolute_by_q = first_crossing_by_q(ABSOLUTE)
    contour_absolute_by_b = first_crossing_by_b(ABSOLUTE)

    result = {
        "epoch": "EPOCH-021",
        "seed": SEED,
        "plan_hash": PLAN_HASH,
        "design": {"A_ROW": A_ROW, "A_COL": A_COL, "K_SMOOTH": K_SMOOTH,
                   "b0_method": "unweighted KMeans on FIX-1 asymmetric code",
                   "bpos_method": "smoothed-Fisher-weighted seeded KMeans (anchors fixed, missing "
                                  "classes seeded via weighted-space kmeans++)"},
        "grid": {"n_c": N_C, "n_v": N_V, "K": K},
        "q_levels": [{"label": l, "target_mrr": v} for l, v in zip(Q_LABELS, Q_LEVELS)],
        "b_levels": B_LEVELS,
        "r_replicates": R_REPLICATES,
        "calibration": calib_records,
        "main_cells": main_cells,
        "adversarial_cells": adv_cells,
        "adversarial_max_ari_combined": max_adv,
        "adversarial_pass": adv_pass,
        "positive_control": {
            "pc_monotonic_b": {"rho": float(rho_b), "p": float(p_b), "pass": pc_monotonic_b},
            "pc_monotonic_q": {"rho": float(rho_q), "p": float(p_q), "pass": pc_monotonic_q},
            "pc_oracle_ceiling": {"ari_combined_mean": oracle_b12["ari_combined_mean"], "pass": pc_oracle},
            "pc_lb_point": {"ari_combined_mean": lb_b12["ari_combined_mean"], "pass": pc_lb_point},
            "PASS": pc_pass,
        },
        "la_operating_point": {
            "b": 0, "q_label": "LA_measured", "q_val": LA_MRR,
            "citation": "b=0: anchor-lattice WP-C dependency-collapsed independent distinct-lineage "
                        "anchor count (research/linear-a-anchor-lattice HEAD 28bbd59); "
                        "q=0.24701551940826028: E013/E018 real measured LEG-1 agg component-channel MRR",
            "ari_row_mean": la_cell["ari_row_mean"],
            "ari_col_mean": la_cell["ari_col_mean"],
            "ari_combined_mean": m,
            "ari_combined_ci95": [la_cell["ari_combined_ci95_lo"], la_cell["ari_combined_ci95_hi"]],
            "gap_to_foothold": gap_foothold,
            "gap_to_absolute": gap_absolute,
            "verdict": la_verdict,
        },
        "contour": {
            "foothold_bar": FOOTHOLD,
            "absolute_bar": ABSOLUTE,
            "first_b_crossing_foothold_by_q": contour_foothold_by_q,
            "first_q_crossing_foothold_by_b": contour_foothold_by_b,
            "first_b_crossing_absolute_by_q": contour_absolute_by_q,
            "first_q_crossing_absolute_by_b": contour_absolute_by_b,
        },
        "runtime_s": time.time() - t0,
    }

    outpath = os.path.join(OUTDIR, "E021_surface.json")
    with open(outpath, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {outpath}")
    print(f"PC_PASS={pc_pass} ADV_PASS={adv_pass} LA_VERDICT={la_verdict} m={m:.4f} "
          f"runtime={result['runtime_s']:.1f}s")
    return result


if __name__ == "__main__":
    main()
