#!/usr/bin/env python3
"""EPOCH-019 POSTHOC (Art. XVII, declared, verdict-neutral) -- seeded-KMeans recovery.

The frozen prereg's nearest-centroid recovery (b>0) failed its own positive control (Art.
XXII fail-closed): it performs WORSE than blind unsupervised KMeans (b=0) across the entire
tested budget range, even at oracle channel quality. This posthoc pass asks: is that a real
information-geometry ceiling, or an artifact of the FROZEN nearest-centroid design (which
conflates the row-block and col-block in one full-embedding distance, and leaves classes with
zero anchors entirely unreachable)?

Alternative recovery method (still non-circular -- uses ONLY anchor labels as an
initialization hint, never any privileged block/feature decomposition): seeded KMeans.
Anchor-label centroids seed as many of the k initial cluster centers as there are distinct
observed labels among the b anchors; any remaining centers are filled via k-means++ over the
full point set; standard Lloyd iterations then run to convergence over ALL points (anchors
included, single n_init=1 run per axis, since the anchor seed IS the informative init).
Scoring is identical to the primary pipeline (held-out ARI, same grid, same R=30, same PC/
adversarial rules).

THIS DOES NOT CHANGE THE FROZEN EPOCH-019 VERDICT (HARNESS_NOT_VALIDATED stands per the
prereg's own fail-closed rule). Declared POSTHOC_CHARACTERIZATION only -- diagnostic, not
confirmatory. Written to data/component_power_surface/E019_posthoc_seeded.json.
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np
from sklearn.cluster import KMeans, kmeans_plusplus
from sklearn.metrics import adjusted_rand_score
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import epoch019_component_power_surface as E19

K, N_C, N_V = E19.K, E19.N_C, E19.N_V
CODE, TRUE_ROW, TRUE_COL = E19.CODE, E19.TRUE_ROW, E19.TRUE_COL
Q_LEVELS, Q_LABELS, B_LEVELS, R_REPLICATES = E19.Q_LEVELS, E19.Q_LABELS, E19.B_LEVELS, E19.R_REPLICATES
FOOTHOLD, ABSOLUTE, ADV_FLOOR_BAR = E19.FOOTHOLD, E19.ABSOLUTE, E19.ADV_FLOOR_BAR
rng_for = E19.rng_for
LA_MRR, LB_MRR = E19.LA_MRR, E19.LB_MRR

OUTDIR = E19.OUTDIR


def seeded_kmeans_labels(query_emb, anchor_idx, anchor_labels_axis, k, rng):
    if len(anchor_idx) == 0:
        km = KMeans(n_clusters=k, n_init=10, random_state=int(rng.integers(0, 2**31))).fit(query_emb)
        return km.labels_
    uniq = sorted(set(anchor_labels_axis))
    init_centers = []
    for lab in uniq:
        idx = [anchor_idx[i] for i, l in enumerate(anchor_labels_axis) if l == lab]
        init_centers.append(query_emb[idx].mean(axis=0))
    init_centers = np.array(init_centers)
    n_have = len(uniq)
    if n_have < k:
        extra, _ = kmeans_plusplus(query_emb, n_clusters=k - n_have,
                                    random_state=int(rng.integers(0, 2**31)))
        init_centers = np.vstack([init_centers, extra])
    elif n_have > k:
        init_centers = init_centers[:k]
    km = KMeans(n_clusters=k, init=init_centers, n_init=1,
                random_state=int(rng.integers(0, 2**31))).fit(query_emb)
    return km.labels_


def run_cell(q_val, q_label, b, sigma, adversarial, r_replicates=R_REPLICATES):
    ari_rows, ari_cols, ari_combined = [], [], []
    for rep in range(r_replicates):
        rng = rng_for("posthoc_seeded", q_label, b, "adv" if adversarial else "main", rep)
        query_emb = CODE + rng.normal(0, sigma, CODE.shape)

        if adversarial:
            perm = rng.permutation(K)
            grade_row = TRUE_ROW[perm]
            grade_col = TRUE_COL[perm]
        else:
            grade_row = TRUE_ROW
            grade_col = TRUE_COL

        anchor_idx = list(rng.choice(K, size=b, replace=False)) if b > 0 else []
        anchor_row = [int(grade_row[i]) for i in anchor_idx]
        anchor_col = [int(grade_col[i]) for i in anchor_idx]

        pred_row = seeded_kmeans_labels(query_emb, anchor_idx, anchor_row, N_C, rng)
        pred_col = seeded_kmeans_labels(query_emb, anchor_idx, anchor_col, N_V, rng)

        held_mask = np.ones(K, dtype=bool)
        if anchor_idx:
            held_mask[anchor_idx] = False

        ar = adjusted_rand_score(grade_row[held_mask], pred_row[held_mask])
        ac = adjusted_rand_score(grade_col[held_mask], pred_col[held_mask])
        ari_rows.append(ar)
        ari_cols.append(ac)
        ari_combined.append((ar + ac) / 2.0)

    ari_combined = np.array(ari_combined)
    m = float(ari_combined.mean())
    sd = float(ari_combined.std(ddof=1))
    ci = 1.96 * sd / np.sqrt(r_replicates)
    return {
        "q_val": q_val, "q_label": q_label, "b": b, "adversarial": adversarial,
        "ari_row_mean": float(np.mean(ari_rows)), "ari_col_mean": float(np.mean(ari_cols)),
        "ari_combined_mean": m, "ari_combined_sd": sd,
        "ari_combined_ci95_lo": m - ci, "ari_combined_ci95_hi": m + ci,
    }


def main():
    t0 = time.time()
    sigmas = {}
    for qv, ql in zip(Q_LEVELS, Q_LABELS):
        sigma, _ = E19.calibrate_sigma(qv, ql)
        sigmas[ql] = sigma

    print("POSTHOC seeded-KMeans main sweep...")
    main_cells = []
    for qv, ql in zip(Q_LEVELS, Q_LABELS):
        for b in B_LEVELS:
            c = run_cell(qv, ql, b, sigmas[ql], adversarial=False)
            main_cells.append(c)
            print(f"  q={ql:18s} b={b:3d}  ARI_comb={c['ari_combined_mean']:.4f}"
                  f" (row={c['ari_row_mean']:.4f} col={c['ari_col_mean']:.4f})")

    print("POSTHOC seeded-KMeans adversarial sweep...")
    adv_cells = []
    for qv, ql in zip(Q_LEVELS, Q_LABELS):
        for b in B_LEVELS:
            adv_cells.append(run_cell(qv, ql, b, sigmas[ql], adversarial=True))
    max_adv = max(c["ari_combined_mean"] for c in adv_cells)

    def lookup(cells, q_label=None, b=None):
        for c in cells:
            if (q_label is None or c["q_label"] == q_label) and (b is None or c["b"] == b):
                yield c

    lb_row = sorted(lookup(main_cells, q_label="LB_within_script"), key=lambda c: c["b"])
    rho_b, p_b = spearmanr([c["b"] for c in lb_row], [c["ari_combined_mean"] for c in lb_row])
    b12_row = sorted(lookup(main_cells, b=12), key=lambda c: c["q_val"])
    rho_q, p_q = spearmanr([c["q_val"] for c in b12_row], [c["ari_combined_mean"] for c in b12_row])
    oracle_b12 = next(lookup(main_cells, q_label="oracle", b=12))
    lb_b12 = next(lookup(main_cells, q_label="LB_within_script", b=12))

    pc = {
        "pc_monotonic_b": {"rho": float(rho_b), "pass": bool(rho_b >= 0.8)},
        "pc_monotonic_q": {"rho": float(rho_q), "pass": bool(rho_q >= 0.8)},
        "pc_oracle_ceiling": {"ari_combined_mean": oracle_b12["ari_combined_mean"],
                               "pass": bool(oracle_b12["ari_combined_mean"] >= ABSOLUTE)},
        "pc_lb_point": {"ari_combined_mean": lb_b12["ari_combined_mean"],
                         "pass": bool(lb_b12["ari_combined_mean"] >= FOOTHOLD)},
    }
    pc["PASS"] = all(v["pass"] for k, v in pc.items() if isinstance(v, dict))
    adv_pass = bool(max_adv < ADV_FLOOR_BAR)

    la_cell = next(lookup(main_cells, q_label="LA_measured", b=0))
    result = {
        "label": "POSTHOC_CHARACTERIZATION -- does NOT change EPOCH-019's frozen verdict",
        "method": "seeded_kmeans (anchor-label centroids as partial init, kmeans++ fill, Lloyd to convergence)",
        "main_cells": main_cells,
        "adversarial_cells": adv_cells,
        "adversarial_max_ari_combined": max_adv,
        "adversarial_pass": adv_pass,
        "positive_control": pc,
        "la_operating_point_seeded": la_cell,
        "runtime_s": time.time() - t0,
    }
    outpath = os.path.join(OUTDIR, "E019_posthoc_seeded.json")
    with open(outpath, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {outpath}")
    print(f"PC_PASS={pc['PASS']} ADV_PASS={adv_pass} runtime={result['runtime_s']:.1f}s")
    print(f"LA point (seeded, b=0 same as primary since b=0 falls back to unsupervised): {la_cell['ari_combined_mean']:.4f}")
    return result


if __name__ == "__main__":
    main()
