#!/usr/bin/env python3
"""p2_select_certify.py — Phase 2 §1 selection (provenance-only) + §2 conjunctive certification.

--select : apply SELECTION_RULE.md (commit fcb0c34) to anchor_census.csv -> selected_anchors.json
--certify: LOTO-survival power on the SELECTED set's real coverage geometry, stratified h=20
           draw, at the CROSS-ATTEMPT-CORRECTED bar (Sidak N_attempts=2: p_raw < 1-0.95^0.5),
           k-escalation per the rule. Synthetic planted signal only — no real label anywhere.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_GATE = os.path.dirname(_HERE)
sys.path.insert(0, _GATE)

from power_precheck import _git, _nn_preds, load_design          # noqa: E402
from phase1_power import INELIGIBLE                              # noqa: E402

RULE_COMMIT = "fcb0c34"
SALT = "p2sel-2026-07-03|"
K0 = 8
STRENGTHS = (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0)
N_REP = 100
N_PERM = 200
H = 20
ALPHA_EFF = 1.0 - 0.95 ** 0.5                                    # 0.02532 (Sidak, 2 attempts)
CERT_MASTER = 20260713

CLASS_RANK = {"toponym": 1, "personal_name": 2, "gloss_acrophonic": 3}
TRUST_RANK = {"tempting": 0, "neutral": 1, "n/a": 2}
STATUS_RANK = {"primary": 0, "secondary": 1}
HEDGES = ("queried", "hedge", "=?", "perhaps", "do not assert", "inconsistency")


def _hedged_notes(notes: str) -> bool:
    """Equation-level hedge test, v2 (disclosed): negation-aware ('unqueried'/'unhedged' do not
    trigger), and a bare source '?' counts only when NOT tied to variation-series evidence (the
    Phase-1 frozen prereg adjudicated tu-ru-sa's s-series '?' as non-equation-level)."""
    t = notes.lower().replace("unqueried", "").replace("unhedged", "")
    if any(m in t for m in HEDGES):
        return True
    return "'?'" in t and "s-series" not in t

_G: dict = {}


def _init():
    anchors, candidates, U, true_val = load_design()
    aidx = {s: i for i, s in enumerate(anchors)}
    elig = [s for s in anchors if s not in INELIGIBLE]
    rows = {r["sign_id"]: r for r in
            csv.DictReader(open(os.path.join(_GATE, "anchors.csv"), encoding="utf-8"))}
    esorted = sorted(elig, key=lambda s: (int(rows[s]["la_attestations"]), s))
    tert = {s: ("T1" if i < 17 else "T2" if i < 33 else "T3") for i, s in enumerate(esorted)}
    _G.update(anchors=anchors, U=U, true_val=true_val, aidx=aidx, elig=set(elig),
              tert=tert, n=len(anchors))


def strict_pool():
    rows = list(csv.DictReader(open(os.path.join(_HERE, "anchor_census.csv"), encoding="utf-8")))
    pool = []
    for r in rows:
        notes = (r["disagreement_notes"] or "").lower()
        if (r["class"] in CLASS_RANK and r["fringe_flag"] != "True"
                and r["sm_trust"] != "debunked"
                and r["source_status"] in STATUS_RANK
                and len([s for s in r["covered_signs"].split(",") if s.strip()]) >= 2
                and not _hedged_notes(notes)):
            pool.append(r)
    return pool


def rank_key(r):
    return (CLASS_RANK[r["class"]], TRUST_RANK.get(r["sm_trust"], 2),
            STATUS_RANK[r["source_status"]],
            hashlib.sha256((SALT + r["anchor_id"]).encode()).hexdigest())


def select(k):
    """Coverage-constrained greedy per SELECTION_RULE.md; prefix-stable in k."""
    _init()
    pool = sorted(strict_pool(), key=rank_key)
    degenerate = [r["anchor_id"] for r in pool
                  if len({s.strip().upper() for s in r["covered_signs"].split(",")}
                         & set(_G["aidx"])) < 2]
    pool = [r for r in pool if r["anchor_id"] not in degenerate]
    union, accepted, skipped = set(), [], []
    for r in pool:
        ss = {s.strip().upper() for s in r["covered_signs"].split(",")} & _G["elig"]
        (accepted if (ss - union) else skipped).append(r)
        if ss - union:
            union |= ss
        if len(accepted) >= k:
            break
    for r in skipped:
        if len(accepted) >= k:
            break
        accepted.append(r)
    words = []
    for r in accepted:
        members = [s.strip().upper() for s in r["covered_signs"].split(",") if s.strip()]
        widx = tuple(_G["aidx"][s] for s in members if s in _G["aidx"])
        words.append({"anchor_id": r["anchor_id"], "class": r["class"],
                      "sm_trust": r["sm_trust"], "source_status": r["source_status"],
                      "members": members, "design_idx": widx})
    legs = Counter(s for w in words for s in set(w["members"]) if s in _G["elig"])
    return {"rule_commit": RULE_COMMIT, "k": len(words), "pool_size": len(pool),
            "pin_degenerate_excluded": degenerate, "words": words,
            "covered_eligible_signs": sorted(legs), "legs_per_sign": dict(sorted(legs.items())),
            "max_legs": max(legs.values()) if legs else 0}


def strata_for(sel):
    covered = set(sel["covered_eligible_signs"])
    cells = {}
    for s in sorted(_G["elig"]):
        key = ("C" if s in covered else "U", _G["tert"][s])
        cells.setdefault(key, []).append(_G["aidx"][s])
    quotas = {kk: H * len(v) / len(_G["elig"]) for kk, v in cells.items()}
    alloc = {kk: int(q) for kk, q in quotas.items()}
    for kk in sorted(quotas, key=lambda kk: -(quotas[kk] - int(quotas[kk])))[:H - sum(alloc.values())]:
        alloc[kk] += 1
    return cells, alloc


def cert_strength(args):
    words_idx, cells, alloc, si, s = args
    U, true_val, n = _G["U"], _G["true_val"], _G["n"]
    det_s, det_full, pins_l = [], [], []
    order = sorted(cells)
    for rep in range(N_REP):
        rng = np.random.default_rng(CERT_MASTER + 1000 * si + rep)
        d = U.shape[1]
        Q, _ = np.linalg.qr(rng.normal(size=(d, d)))
        X = s * (U[true_val] @ Q.T) + rng.normal(size=(n, d))
        X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
        held = []
        for kk in order:
            if alloc[kk]:
                held.extend(rng.choice(cells[kk], size=alloc[kk], replace=False).tolist())
        held = np.array(sorted(held))
        train = np.array(sorted(set(range(n)) - set(held.tolist())))
        hs = set(held.tolist())
        pin_words = {int(x): [j for j, w in enumerate(words_idx)
                              if x in w and all((y == int(x)) or (y not in hs) for y in w)]
                     for x in held}
        pin_words = {x: pw for x, pw in pin_words.items() if pw}
        pinning = sorted({j for pw in pin_words.values() for j in pw})

        def score(assign, preds, drop=None):
            hits = 0
            for kk2, x in enumerate(held):
                pw = [j for j in pin_words.get(int(x), []) if j != drop]
                hits += int(true_val[x] == assign[x]) if pw else int(preds[kk2] == assign[x])
            return hits / H

        scorings = [None] + pinning
        p_obs, _ = _nn_preds(X, U, true_val, train, held)
        obs = [score(true_val, p_obs, dr) for dr in scorings]
        null = np.zeros((len(scorings), N_PERM))
        for kk2 in range(N_PERM):
            pi = true_val[rng.permutation(n)]
            p_k, _ = _nn_preds(X, U, pi, train, held)
            for si2, dr in enumerate(scorings):
                null[si2, kk2] = score(pi, p_k, dr)
        p = (1 + np.sum(null >= np.array(obs)[:, None] - 1e-12, axis=1)) / (N_PERM + 1)
        det_full.append(bool(p[0] < ALPHA_EFF))
        det_s.append(bool(p[0] < ALPHA_EFF and all(pv < ALPHA_EFF for pv in p[1:])))
        pins_l.append(len(pin_words))
    return si, {"strength": s, "loto_survival_power": float(np.mean(det_s)),
                "raw_power": float(np.mean(det_full)), "mean_pinned": float(np.mean(pins_l))}


def certify(workers):
    _init()
    trail = []
    k = K0
    while True:
        sel = select(k)
        if sel["k"] < k:
            return {"result": "POOL_EXHAUSTED", "trail": trail, "pool": sel["pool_size"]}
        cells, alloc = strata_for(sel)
        words_idx = [w["design_idx"] for w in sel["words"]]
        t0 = time.time()
        with Pool(min(workers, len(STRENGTHS)), initializer=_init) as pool:
            got = pool.map(cert_strength,
                           [(words_idx, cells, alloc, si, s) for si, s in enumerate(STRENGTHS)])
        curve = [rec for _, rec in sorted(got)]
        # machinery (pins off) at s=0 and s=13, corrected bar
        mach = {}
        for si in (0, len(STRENGTHS) - 1):
            _, rec = cert_strength(([], cells, alloc, si, STRENGTHS[si]))
            mach[STRENGTHS[si]] = rec["raw_power"]
        entry = {"k": k, "curve": curve, "machinery": mach,
                 "alloc": {f"{a}_{b}": alloc[(a, b)] for (a, b) in alloc},
                 "secs": round(time.time() - t0, 1),
                 "passes": any(c["loto_survival_power"] >= 0.80 for c in curve
                               if c["strength"] <= 3.0)
                 and mach[0.0] <= 0.14 and mach[13.0] >= 0.90}
        trail.append(entry)
        print(f"[certify] k={k}: surv@s<=3 max="
              f"{max(c['loto_survival_power'] for c in curve if c['strength'] <= 3):.2f} "
              f"mach(ff={mach[0.0]:.2f}, s13={mach[13.0]:.2f}) "
              f"passes={entry['passes']} ({entry['secs']}s)", flush=True)
        if entry["passes"]:
            return {"result": "CERTIFIED", "k": k, "selection": sel, "trail": trail,
                    "alpha_eff": ALPHA_EFF, "n_rep": N_REP, "n_perm": N_PERM,
                    "cert_master_seed": CERT_MASTER}
        k += 1
        if k > sel["pool_size"]:
            return {"result": "POOL_EXHAUSTED", "trail": trail, "pool": sel["pool_size"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--select", action="store_true")
    ap.add_argument("--certify", action="store_true")
    ap.add_argument("--k", type=int, default=K0)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(os.path.join(_HERE, "results"), exist_ok=True)
    if a.select:
        sel = select(a.k)
        with open(os.path.join(_HERE, "results", "selected_anchors.json"), "w") as f:
            json.dump(sel, f, indent=2)
        print(json.dumps({kk: sel[kk] for kk in
                          ("k", "pool_size", "pin_degenerate_excluded",
                           "covered_eligible_signs", "legs_per_sign", "max_legs")}, indent=2))
        print("selected:", [w["anchor_id"] for w in sel["words"]])
    if a.certify:
        out = certify(a.workers)
        with open(os.path.join(_HERE, "results", "p2_certification.json"), "w") as f:
            json.dump(out, f, indent=2)
        print("RESULT:", out["result"], "| k =", out.get("k"))
