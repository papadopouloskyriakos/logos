#!/usr/bin/env python3
"""EPOCH-019 -- Component-channel value-recovery identifiability surface.

Preregistered: epochs/EPOCH-019/prereg.md
plan_hash af5d970eb54872fd1b10da8beded3256c952358b58d3a69abc728f21bcd91cb2
(frozen 2026-07-08, before any (b,q) cell realized)

Synthetic, truth-known generative benchmark: an 18-consonant-row x 5-vowel-column grid
(K=90 signs). Sweeps anchor budget b in {0,2,4,8,12} x injected channel quality q in
{0.15, 0.24701551940826028 (LA real E013/E018 MRR), 0.30, 0.39934712069259104 (LB real
E009 within-script MRR), 0.55, 0.75, 1.0 (oracle)}. At each cell measures value-CLASS
recovery (ARI of the recovered consonant-row and vowel-column partition) via a frozen
KMeans(b=0)/nearest-centroid(b>0) recovery method, R=30 replicates/cell. Positive control
(monotonicity + oracle ceiling + LB-point foothold) gates interpretation; adversarial
shuffled-identity null must stay at the ARI floor. Locates LA's real operating point
(b=0 anchors [anchor-lattice WP-C], q=0.24701551940826028 [E013/E018]) on the surface.
Seed 20260708. Claim layer L1 only -- no phonetic value anywhere in this script.
"""
from __future__ import annotations
import hashlib, json, os, time
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from scipy.stats import spearmanr

SEED = 20260708
PLAN_HASH = "af5d970eb54872fd1b10da8beded3256c952358b58d3a69abc728f21bcd91cb2"

N_C, N_V = 18, 5
K = N_C * N_V  # 90

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
OUTDIR = os.path.join(CAMP, "data", "component_power_surface")
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
CODE = np.concatenate([onehot(TRUE_ROW, N_C), onehot(TRUE_COL, N_V)], axis=1)  # (K, 23)


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


def calibrate_sigma(target, key, lo=1e-6, hi=1.5, tol=0.004, max_iter=40):
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


def recover(query_emb, anchor_idx, anchor_row, anchor_col, n_c, n_v, rng):
    n = query_emb.shape[0]
    if len(anchor_idx) == 0:
        km_r = KMeans(n_clusters=n_c, n_init=10, random_state=int(rng.integers(0, 2**31))).fit(query_emb)
        km_c = KMeans(n_clusters=n_v, n_init=10, random_state=int(rng.integers(0, 2**31))).fit(query_emb)
        return km_r.labels_, km_c.labels_
    # nearest-centroid classifier seeded by anchors
    def centroids(labels_at_anchor):
        cents = {}
        for lab in set(labels_at_anchor):
            idx = [anchor_idx[i] for i, l in enumerate(labels_at_anchor) if l == lab]
            cents[lab] = query_emb[idx].mean(axis=0)
        return cents

    row_cents = centroids(anchor_row)
    col_cents = centroids(anchor_col)
    row_labels = sorted(row_cents.keys())
    col_labels = sorted(col_cents.keys())
    row_mat = np.stack([row_cents[l] for l in row_labels])
    col_mat = np.stack([col_cents[l] for l in col_labels])
    d_row = np.linalg.norm(query_emb[:, None, :] - row_mat[None, :, :], axis=2)
    d_col = np.linalg.norm(query_emb[:, None, :] - col_mat[None, :, :], axis=2)
    pred_row = np.array([row_labels[i] for i in d_row.argmin(axis=1)])
    pred_col = np.array([col_labels[i] for i in d_col.argmin(axis=1)])
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
    print("Calibrating sigma(q)...")
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

    # ---- Positive control ----
    def cell_lookup(cells, q_label=None, b=None):
        for c in cells:
            if (q_label is None or c["q_label"] == q_label) and (b is None or c["b"] == b):
                yield c

    # PC-monotonic-b: q fixed at LB point, across B
    lb_row = sorted(cell_lookup(main_cells, q_label="LB_within_script"), key=lambda c: c["b"])
    rho_b, p_b = spearmanr([c["b"] for c in lb_row], [c["ari_combined_mean"] for c in lb_row])
    pc_monotonic_b = bool(rho_b >= 0.8)

    # PC-monotonic-q: b fixed at 12, across Q
    b12_row = sorted(cell_lookup(main_cells, b=12), key=lambda c: c["q_val"])
    rho_q, p_q = spearmanr([c["q_val"] for c in b12_row], [c["ari_combined_mean"] for c in b12_row])
    pc_monotonic_q = bool(rho_q >= 0.8)

    # PC-oracle-ceiling: (q=oracle, b=12)
    oracle_b12 = next(cell_lookup(main_cells, q_label="oracle", b=12))
    pc_oracle = bool(oracle_b12["ari_combined_mean"] >= ABSOLUTE)

    # PC-LB-point: (q=LB_within_script, b=12)
    lb_b12 = next(cell_lookup(main_cells, q_label="LB_within_script", b=12))
    pc_lb_point = bool(lb_b12["ari_combined_mean"] >= FOOTHOLD)

    pc_pass = pc_monotonic_b and pc_monotonic_q and pc_oracle and pc_lb_point
    adv_pass = bool(max_adv < ADV_FLOOR_BAR)

    # ---- LA operating point ----
    la_cell = next(cell_lookup(main_cells, q_label="LA_measured", b=0))
    m = la_cell["ari_combined_mean"]
    if not (pc_pass and adv_pass):
        la_verdict = "HARNESS_NOT_VALIDATED" if not pc_pass else "SURFACE_CONFOUNDED"
    elif m < FOOTHOLD:
        la_verdict = "LA_COMPONENT_POINT_BELOW_FOOTHOLD"
    elif m < ABSOLUTE:
        la_verdict = "LA_COMPONENT_POINT_AT_FOOTHOLD"
    else:
        la_verdict = "LA_COMPONENT_POINT_RECOVERS"

    gap_foothold = max(0.0, FOOTHOLD - m)
    gap_absolute = max(0.0, ABSOLUTE - m)

    # ---- contour: first (b,q) crossing foothold / absolute ----
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
        "epoch": "EPOCH-019",
        "seed": SEED,
        "plan_hash": PLAN_HASH,
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
            "citation": "b=0: anchor-lattice WP-C dependency-collapsed independent distinct-lineage anchor count (research/linear-a-anchor-lattice HEAD 28bbd59); q=0.24701551940826028: E013/E018 real measured LEG-1 agg component-channel MRR",
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

    outpath = os.path.join(OUTDIR, "E019_surface.json")
    with open(outpath, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {outpath}")
    print(f"PC_PASS={pc_pass} ADV_PASS={adv_pass} LA_VERDICT={la_verdict} m={m:.4f} runtime={result['runtime_s']:.1f}s")
    return result


if __name__ == "__main__":
    main()
