#!/usr/bin/env python3
"""power_precheck.py — Phase 0 §3: planted-value synthetic power analysis (the go/no-go).

Implements EXACTLY the design frozen in PREREG_DRAFT.md §2 (committed BEFORE this script ran;
the commit hash is recorded in the results and a mismatch voids the run):

  - real design size: 51 robust anchors (anchors.csv), held-out h=10 primary
    (h ∈ {5,15,20} sensitivity), candidate space = 73 DĀMOS-attested LB syllabary values;
  - value embeddings U_v: the existing Track-B recipe (PPMI window 2, cds 0.75 → SVD d=24)
    over the real DĀMOS wordforms — ALLOWED features only (no image/shape anywhere);
  - LA-side features SYNTHETIC (B.2 planted-positive-control pattern, never real vectors with
    real labels): X_sign = s·(R @ U_{v(sign)}) + N(0, I), L2-normalised;
  - stand-in decoder: orthogonal Procrustes (align_methods.Procrustes, reused) — a simulation
    stand-in, NOT a recovery model run on real data;
  - null: permuted-graph (permute the anchor↔value assignment, refit, re-evaluate),
    n_perm=200, add-one p<0.05 = detection; n_rep=50 per strength;
  - strengths {0, 0.5, 1, 2, 3, 5, 8, 13}; seeds 20260703 + 10000·strength_idx + rep.

Verdict per the frozen thresholds: INVALID / GO / MARGINAL / NO-GO (+ the pre-committed NO-GO
follow-up sweep). CPU only.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _ROOT)

from scripts.cross_script import data as D                     # noqa: E402
from scripts.cross_script import embeddings as E               # noqa: E402
from scripts.cross_script.align_methods import Procrustes      # noqa: E402

MASTER_SEED = 20260703
STRENGTHS = (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0)
N_REP = 50
N_PERM = 200
H_PRIMARY = 10
H_SENSITIVITY = (5, 15, 20)
D_EMB = 24
ALPHA = 0.05

BANNED_MODULES = ("PIL", "cv2", "skimage", "torchvision", "scripts.palaeo")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=_ROOT, capture_output=True,
                          text=True).stdout.strip()


def load_design():
    """Real anchors + real DĀMOS value embeddings (the ALLOWED-feature geometry)."""
    with open(os.path.join(_HERE, "anchors.csv"), encoding="utf-8") as f:
        anchor_rows = [r for r in csv.DictReader(f) if r["robust_anchor"] == "True"]
    anchors = [r["sign_id"] for r in anchor_rows]

    bd_seqs, bd_freq, _ = D.load_b_damos()
    syll = [v for cp in range(0x10000, 0x10080)
            if (v := D._b_value_from_codepoint(chr(cp)))]
    candidates = sorted(v for v in syll if bd_freq.get(v, 0) >= 1)      # 73

    vocab, U_full = E.embed(bd_seqs, d=D_EMB, window=2, cds=0.75, seed=0)
    U = np.vstack([U_full[vocab[v]] for v in candidates])
    U = U / np.maximum(np.linalg.norm(U, axis=1, keepdims=True), 1e-12)

    cand_idx = {v: i for i, v in enumerate(candidates)}
    true_val = np.array([cand_idx[s] for s in anchors])                  # value == sign token
    return anchors, candidates, U, true_val


def _heldout_acc(X, U, assign, train, held, top_k=1):
    m = Procrustes().fit(X, U, [(i, assign[i]) for i in train])
    S = m.similarity(X, U)
    if top_k == 1:
        pred = np.argmax(S[held], axis=1)
        return float(np.mean(pred == assign[held]))
    ranks = np.argsort(-S[held], axis=1)[:, :top_k]
    return float(np.mean([assign[h] in ranks[j] for j, h in enumerate(held)]))


def replicate(U, true_val, n, h, s, seed):
    """One planted-signal replicate at strength s: returns (obs_top1, obs_top5, perm_p, detect)."""
    rng = np.random.default_rng(seed)
    d = U.shape[1]
    Q, _ = np.linalg.qr(rng.normal(size=(d, d)))                 # fixed random orthogonal map
    X = s * (U[true_val] @ Q.T) + rng.normal(size=(n, d))
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)

    perm = rng.permutation(n)
    held, train = perm[:h], perm[h:]

    obs = _heldout_acc(X, U, true_val, train, held)
    obs5 = _heldout_acc(X, U, true_val, train, held, top_k=5)

    null = np.empty(N_PERM)
    for k in range(N_PERM):
        pi = true_val[rng.permutation(n)]                        # permuted anchor↔value graph
        null[k] = _heldout_acc(X, U, pi, train, held)
    p = float((1 + np.sum(null >= obs - 1e-12)) / (N_PERM + 1))
    return obs, obs5, p, p < ALPHA


def power_curve(U, true_val, n, h, *, label, log=print):
    curve = []
    for si, s in enumerate(STRENGTHS):
        det, o1, o5 = [], [], []
        for r in range(N_REP):
            obs, obs5, p, d_ = replicate(U, true_val, n, h, s,
                                         MASTER_SEED + 10000 * si + r)
            det.append(d_); o1.append(obs); o5.append(obs5)
        curve.append({"strength": s, "power": float(np.mean(det)),
                      "mean_top1": float(np.mean(o1)), "mean_top5": float(np.mean(o5))})
        log(f"  [{label}] s={s:>4}: power={np.mean(det):.2f} top1={np.mean(o1):.3f}", flush=True)
    return curve


def verdict_from(curve):
    p0 = next(c["power"] for c in curve if c["strength"] == 0.0)
    p13 = next(c["power"] for c in curve if c["strength"] == 13.0)
    if p0 > 0.14 or p13 < 0.90:
        return "INVALID", {"false_fire_s0": p0, "power_s13": p13}
    go = any(c["power"] >= 0.80 for c in curve if c["strength"] <= 3.0)
    marginal = any(c["power"] >= 0.80 for c in curve if c["strength"] <= 8.0)
    v = "GO" if go else ("MARGINAL" if marginal else "NO-GO")
    return v, {"false_fire_s0": p0, "power_s13": p13}


def main() -> int:
    t0 = time.time()
    anchors, candidates, U, true_val = load_design()
    n = len(anchors)
    assert n == 51 and len(candidates) == 73, (n, len(candidates))

    results = {
        "prereg_thresholds_commit": _git("log", "-1", "--format=%H", "--",
                                         "experiments/crossscript_gate/PREREG_DRAFT.md"),
        "run_head_commit": _git("rev-parse", "HEAD"),
        "design": {"n_anchors": n, "h_primary": H_PRIMARY, "n_candidates": len(candidates),
                   "chance_top1": 1.0 / len(candidates), "d_emb": D_EMB,
                   "n_rep": N_REP, "n_perm": N_PERM, "alpha": ALPHA,
                   "strengths": list(STRENGTHS), "master_seed": MASTER_SEED},
    }

    print(f"[power] primary design: n={n} h={H_PRIMARY} |V|={len(candidates)}", flush=True)
    primary = power_curve(U, true_val, n, H_PRIMARY, label=f"h={H_PRIMARY}")
    verdict, checks = verdict_from(primary)
    results["primary_curve"] = primary
    results["validity_checks"] = checks
    results["verdict"] = verdict

    results["sensitivity"] = {}
    for h in H_SENSITIVITY:
        results["sensitivity"][f"h={h}"] = power_curve(U, true_val, n, h, label=f"h={h}")

    if verdict == "NO-GO":                       # pre-committed follow-up: smallest n with power
        rng = np.random.default_rng(MASTER_SEED + 999)
        sweep = {}
        for n_syn in (51, 100, 150, 200, 300):
            tv = (true_val if n_syn == n
                  else rng.integers(0, len(candidates), size=n_syn))   # non-injective for n>|V|
            c = power_curve(U, tv, n_syn, max(1, int(round(0.2 * n_syn))), label=f"n={n_syn}")
            sweep[f"n={n_syn}"] = {"curve": c,
                                   "go_would_hold": any(x["power"] >= 0.80 for x in c
                                                        if x["strength"] <= 3.0)}
        results["nogo_followup_n_sweep"] = sweep

    # feature-contract self-check: the power analysis itself must be grep/import-clean
    dirty = [m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in BANNED_MODULES)]
    results["banned_modules_in_process"] = dirty
    assert not dirty, f"feature contract violated: {dirty}"

    results["wall_clock_s"] = round(time.time() - t0, 1)
    out = os.path.join(_HERE, "results")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "power_precheck.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nVERDICT: {verdict}  (checks: {checks})  wall={results['wall_clock_s']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
