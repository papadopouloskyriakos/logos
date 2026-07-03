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
H_FINAL = 20               # Addendum B: finalized by the operator (Phase-0 sensitivity finding)
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


def _pinned(held_set, x, forms_idx):
    """Addendum B toponym channel: x pinned iff some non-queried toponym form contains x with
    ALL its other member anchors un-held-out (LB-lexicon word completion, reliability=1)."""
    for form in forms_idx:
        if x in form and all((y == x) or (y not in held_set) for y in form):
            return True
    return False


def _nn_preds(X, U, assign, train, held):
    m = Procrustes().fit(X, U, [(i, assign[i]) for i in train])
    S = m.similarity(X, U)
    return np.argmax(S[held], axis=1), S


def replicate(U, true_val, n, h, s, seed, forms_idx):
    """One planted-signal replicate at strength s. Returns per-config observables and
    detections — config (a) machinery (no toponym channel) and config (b) finalized design —
    computed from the SAME X, split, and null permutation draws (paired, Addendum B §5)."""
    rng = np.random.default_rng(seed)
    d = U.shape[1]
    Q, _ = np.linalg.qr(rng.normal(size=(d, d)))                 # fixed random orthogonal map
    X = s * (U[true_val] @ Q.T) + rng.normal(size=(n, d))
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)

    perm = rng.permutation(n)
    held, train = perm[:h], perm[h:]
    held_set = set(held.tolist())
    pins = np.array([_pinned(held_set, int(x), forms_idx) for x in held])

    def _acc_both(assign):
        preds, S = _nn_preds(X, U, assign, train, held)
        hits = preds == assign[held]
        acc_a = float(np.mean(hits))
        # config (b): pinned prediction = the conventional slot value (true_val), overriding NN
        hits_b = np.where(pins, true_val[held] == assign[held], hits)
        acc_b = float(np.mean(hits_b))
        top5 = np.argsort(-S[held], axis=1)[:, :5]
        acc5 = float(np.mean([assign[held[j]] in top5[j] for j in range(len(held))]))
        return acc_a, acc_b, acc5

    obs_a, obs_b, obs5 = _acc_both(true_val)
    null_a = np.empty(N_PERM)
    null_b = np.empty(N_PERM)
    for k in range(N_PERM):
        pi = true_val[rng.permutation(n)]                        # permuted anchor↔value graph
        null_a[k], null_b[k], _ = _acc_both(pi)
    p_a = float((1 + np.sum(null_a >= obs_a - 1e-12)) / (N_PERM + 1))
    p_b = float((1 + np.sum(null_b >= obs_b - 1e-12)) / (N_PERM + 1))
    return {"obs_a": obs_a, "obs_b": obs_b, "obs5": obs5, "p_a": p_a, "p_b": p_b,
            "det_a": p_a < ALPHA, "det_b": p_b < ALPHA, "n_pinned": int(pins.sum())}


def power_curves_ab(U, true_val, n, h, forms_idx, *, log=print):
    """Both Addendum-B configurations over the strength grid, paired seeds."""
    curve_a, curve_b = [], []
    for si, s in enumerate(STRENGTHS):
        rows = [replicate(U, true_val, n, h, s, MASTER_SEED + 10000 * si + r, forms_idx)
                for r in range(N_REP)]
        curve_a.append({"strength": s, "power": float(np.mean([r["det_a"] for r in rows])),
                        "mean_top1": float(np.mean([r["obs_a"] for r in rows])),
                        "mean_top5": float(np.mean([r["obs5"] for r in rows]))})
        curve_b.append({"strength": s, "power": float(np.mean([r["det_b"] for r in rows])),
                        "mean_top1": float(np.mean([r["obs_b"] for r in rows])),
                        "mean_pinned": float(np.mean([r["n_pinned"] for r in rows]))})
        log(f"  s={s:>4}: machinery(a) power={curve_a[-1]['power']:.2f} "
            f"top1={curve_a[-1]['mean_top1']:.3f} | design(b) power={curve_b[-1]['power']:.2f} "
            f"top1={curve_b[-1]['mean_top1']:.3f} pins={curve_b[-1]['mean_pinned']:.1f}", flush=True)
    return curve_a, curve_b


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

    # Addendum B: the toponym-constraint channel (non-queried Table 6.4 forms only), as
    # anchor-index tuples. Every covered sign is a robust anchor (verified in the summary).
    import steele_meissner_2017 as SM
    aidx = {s: i for i, s in enumerate(anchors)}
    forms_idx = [tuple(aidx[s] for s in t["la_signs"])
                 for t in SM.TOPONYM_EQUATIONS if not t["queried"]]
    assert all(all(s in aidx for s in t["la_signs"])
               for t in SM.TOPONYM_EQUATIONS if not t["queried"])

    results = {
        "prereg_thresholds_commit_frozen": "00fb9eaec78e6de8ba684263fabc5eed6a76f07f",
        "addendum_b_commit": _git("log", "-1", "--format=%H", "--",
                                  "experiments/crossscript_gate/PREREG_DRAFT.md"),
        "run_head_commit": _git("rev-parse", "HEAD"),
        "design": {"n_anchors": n, "h": H_FINAL, "n_candidates": len(candidates),
                   "chance_top1": 1.0 / len(candidates), "d_emb": D_EMB,
                   "n_rep": N_REP, "n_perm": N_PERM, "alpha": ALPHA,
                   "strengths": list(STRENGTHS), "master_seed": MASTER_SEED,
                   "toponym_forms": [t["lb"] for t in SM.TOPONYM_EQUATIONS if not t["queried"]],
                   "toponym_reliability_assumption": 1.0},
    }

    print(f"[power 0.5] finalized design: n={n} h={H_FINAL} |V|={len(candidates)} "
          f"toponym forms={len(forms_idx)}", flush=True)
    curve_a, curve_b = power_curves_ab(U, true_val, n, H_FINAL, forms_idx)

    # INVALID checks on config (a) — the machinery, signal-free world (Addendum B §4a);
    # verdict bands verbatim from the frozen §2, applied to config (b) — the actual design.
    _, checks = verdict_from(curve_a)
    machinery_invalid = (checks["false_fire_s0"] > 0.14 or checks["power_s13"] < 0.90)
    if machinery_invalid:
        verdict = "INVALID"
    else:
        go = any(c["power"] >= 0.80 for c in curve_b if c["strength"] <= 3.0)
        marginal = any(c["power"] >= 0.80 for c in curve_b if c["strength"] <= 8.0)
        verdict = "GO" if go else ("MARGINAL" if marginal else "NO-GO")

    results["machinery_curve_a"] = curve_a
    results["design_curve_b"] = curve_b
    results["validity_checks_on_a"] = checks
    results["verdict"] = verdict

    # feature-contract self-check: the power analysis itself must be grep/import-clean
    dirty = [m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in BANNED_MODULES)]
    results["banned_modules_in_process"] = dirty
    assert not dirty, f"feature contract violated: {dirty}"

    results["wall_clock_s"] = round(time.time() - t0, 1)
    out = os.path.join(_HERE, "results")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "power_precheck_phase05.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nVERDICT: {verdict}  (checks: {checks})  wall={results['wall_clock_s']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
