#!/usr/bin/env python3
"""p2_oneshot.py — Phase 2 §5: the one-shot run (PREREG_FINAL_P2 @ 0aeaee8,
DOI 10.5281/zenodo.21173639 published 2026-07-03T16:48:50Z BEFORE this file existed).

Real held-out labels are compared against predictions exactly once, here. LOTO and descriptive
rows are deterministic re-scorings of this run's persisted artifacts. Corrected two-attempt bar
in force (not vetoed): p_raw < 1 - 0.95**0.5.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_GATE = os.path.dirname(_HERE)
_ROOT = os.path.dirname(os.path.dirname(_GATE))
sys.path.insert(0, _GATE)
sys.path.insert(0, _ROOT)

from power_precheck import _git, _nn_preds, load_design          # noqa: E402
import p2_select_certify as PS                                   # noqa: E402
from scripts.cross_script import data as D                       # noqa: E402
from scripts.cross_script import embeddings as E                 # noqa: E402
from scripts.comparison.searchlog import SearchLog               # noqa: E402

DRAW_SEED = 20260714
NULL_SEED = 20260715
N_PERM = 2000
ALPHA_EFF = 1.0 - 0.95 ** 0.5
FROZEN_HELD = ["DI", "JA", "KI", "MA", "ME", "NE", "O", "PO", "PU", "PU2", "QE", "RA", "RI",
               "SU", "TA2", "TE", "TI", "TO", "U", "WA"]
P1_HELD = {"DI", "I", "KU", "ME", "NA", "NE", "NI", "NU", "O", "PA", "PO", "QA", "QE", "RA2",
           "RE", "RI", "TA2", "TE", "WA", "ZA"}
ELEVEN = ("A", "DA", "I", "NA", "PA", "PO", "RO", "SA", "SE", "TI", "TO")
SECONDARY_ANCHORS = {"top_ku_ta_younger", "top_ku_ni_su_younger", "top_sa_ra2_younger"}
BANNED = ("PIL", "cv2", "skimage", "torchvision", "scripts.palaeo")


def main() -> int:
    t0 = time.time()
    PS._init()
    anchors, U, true_val, aidx, n = (PS._G["anchors"], PS._G["U"], PS._G["true_val"],
                                     PS._G["aidx"], PS._G["n"])
    sel = json.load(open(os.path.join(_HERE, "results", "selected_anchors.json")))
    words = sel["words"]
    words_idx = [tuple(w["design_idx"]) for w in words]

    # frozen stratified draw — must reproduce the prereg's materialized list EXACTLY
    cells, alloc = PS.strata_for(sel)
    rng = np.random.default_rng(DRAW_SEED)
    held = []
    for k in sorted(cells):
        if alloc[k]:
            held.extend(rng.choice(cells[k], size=alloc[k], replace=False).tolist())
    held = np.array(sorted(held))
    assert sorted(anchors[i] for i in held) == FROZEN_HELD, "freeze violation: draw mismatch"
    train = np.array(sorted(set(range(n)) - set(held.tolist())))
    hs = set(held.tolist())

    a_inv, a_seqs, _ = D.load_a()
    vocab_a, EA_full = E.embed(a_seqs, d=24, window=2, cds=0.75, seed=0)
    EA = np.vstack([EA_full[vocab_a[s]] for s in anchors])

    pin_words = {}
    for x in held:
        pw = [j for j, w in enumerate(words_idx)
              if x in w and all((y == int(x)) or (y not in hs) for y in w)]
        if pw:
            pin_words[int(x)] = pw
    pinning = sorted({j for pw in pin_words.values() for j in pw})
    sec_idx = {j for j, w in enumerate(words) if w["anchor_id"] in SECONDARY_ANCHORS}

    def score(assign, preds, drop=None, drop_set=None):
        hits = 0
        for k2, x in enumerate(held):
            pw = pin_words.get(int(x), [])
            if drop is not None:
                pw = [j for j in pw if j != drop]
            if drop_set is not None:
                pw = [j for j in pw if j not in drop_set]
            hits += int(true_val[x] == assign[x]) if pw else int(preds[k2] == assign[x])
        return hits / len(held)

    slog = SearchLog()
    slog.log_candidate({"config": "d24-w2-cds075-procrustes-pins", "attempt": 2}, "p2-primary", ())
    scorings = ([("full", {})] + [(f"loto_{words[j]['anchor_id']}", {"drop": j}) for j in range(len(words))]
                + [("off", {"drop_set": set(range(len(words)))}),
                   ("secondary_drop", {"drop_set": sec_idx})])

    preds_obs, S_obs = _nn_preds(EA, U, true_val, train, held)
    order_obs = np.argsort(-S_obs[held], axis=1)
    obs = {nm: score(true_val, preds_obs, **kw) for nm, kw in scorings}
    null = {nm: np.empty(N_PERM) for nm, _ in scorings}
    rngN = np.random.default_rng(NULL_SEED)
    for k2 in range(N_PERM):
        pi = true_val[rngN.permutation(n)]
        p_k, _ = _nn_preds(EA, U, pi, train, held)
        for nm, kw in scorings:
            null[nm][k2] = score(pi, p_k, **kw)
        slog.log_candidate({"draw": k2}, "p2-null", ())
    stats = {}
    for nm, _ in scorings:
        p = float((1 + np.sum(null[nm] >= obs[nm] - 1e-12)) / (N_PERM + 1))
        stats[nm] = {"observed_top1": obs[nm], "null_mean": float(null[nm].mean()),
                     "p_raw": p, "clears_corrected_bar": p < ALPHA_EFF,
                     "null_degenerate": bool(null[nm].std() < 1e-12)}

    per_sign = []
    for k2, x in enumerate(held):
        rank = int(np.where(order_obs[k2] == true_val[x])[0][0]) + 1
        per_sign.append({"sign_id": anchors[x], "nn_rank_of_true": rank,
                         "pinned_by": [words[j]["anchor_id"] for j in pin_words.get(int(x), [])],
                         "hit_full": bool(pin_words.get(int(x))) or bool(preds_obs[k2] == true_val[x]),
                         "p1_overlap": anchors[x] in P1_HELD})
    ov = [r for r in per_sign if r["p1_overlap"]]
    fr = [r for r in per_sign if not r["p1_overlap"]]
    overlap_row = {"overlap_n": len(ov), "overlap_acc": sum(r["hit_full"] for r in ov) / len(ov),
                   "fresh_n": len(fr), "fresh_acc": sum(r["hit_full"] for r in fr) / len(fr)}

    # descriptive Cypriot-eleven block (no gate authority)
    held_c = np.array(sorted(aidx[s] for s in ELEVEN))
    train_c = np.array(sorted(set(range(n)) - set(held_c.tolist())))
    hc = set(held_c.tolist())
    pin_c = {int(x): [j for j, w in enumerate(words_idx)
                      if x in w and all((y == int(x)) or (y not in hc) for y in w)] for x in held_c}
    pin_c = {x: pw for x, pw in pin_c.items() if pw}
    pc_obs, _ = _nn_preds(EA, U, true_val, train_c, held_c)
    hits_c = sum((true_val[x] == true_val[x]) if pin_c.get(int(x)) else int(pc_obs[k2] == true_val[x])
                 for k2, x in enumerate(held_c))
    null_c = np.empty(N_PERM)
    for k2 in range(N_PERM):
        pi = true_val[rngN.permutation(n)]
        p_k, _ = _nn_preds(EA, U, pi, train_c, held_c)
        null_c[k2] = sum(int(true_val[x] == pi[x]) if pin_c.get(int(x)) else int(p_k[j] == pi[x])
                         for j, x in enumerate(held_c)) / len(held_c)
    cyp = {"observed_top1": hits_c / len(held_c),
           "p_raw": float((1 + np.sum(null_c >= hits_c / len(held_c) - 1e-12)) / (N_PERM + 1)),
           "n_pinned": len(pin_c), "descriptive_only": True}

    dirty = [m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in BANNED)]
    slog_ok = slog.n_eff > 0 and not dirty
    loto = [nm for nm, _ in scorings if nm.startswith("loto_")]
    if any(stats[nm]["null_degenerate"] for nm in stats) or not slog_ok:
        verdict = "INCOMPLETE"
    elif stats["full"]["clears_corrected_bar"]:
        verdict = ("CONFIRM" if all(stats[nm]["clears_corrected_bar"] for nm in loto)
                   else "REFUTE_LOTO_FRAGILE")
    else:
        verdict = "REFUTE"

    art = {"prereg": {"freeze_commit": "0aeaee8aa4c5d5c8e2120d38c57c8013def5e067",
                      "sha256": "1fce8401f5efedebe1f71d1e7ddd095f0d14c1998f098461617dfa0b96faeb71",
                      "doi": "10.5281/zenodo.21173639",
                      "published": "2026-07-03T16:48:50Z"},
           "run_head_commit": _git("rev-parse", "HEAD"),
           "alpha_corrected": ALPHA_EFF, "n_perm": N_PERM,
           "seeds": {"draw": DRAW_SEED, "null": NULL_SEED, "embeddings": 0},
           "held_out": [anchors[i] for i in held], "n_pinned": len(pin_words),
           "pinning_anchors": [words[j]["anchor_id"] for j in pinning],
           "stats": stats, "per_sign": per_sign, "overlap_row": overlap_row,
           "cypriot_block_descriptive": cyp,
           "searchlog": {"n_eff": slog.n_eff, "n_logged": slog.n_logged, "n_trials": 1},
           "banned_modules": dirty, "gate_verdict": verdict,
           "wall_clock_s": round(time.time() - t0, 1)}
    out = os.path.join(_HERE, "results", "p2_oneshot_gate.json")
    with open(out, "w") as f:
        json.dump(art, f, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(f"artifact sha256: {hashlib.sha256(open(out,'rb').read()).hexdigest()}")
    print(f"GATE VERDICT: {verdict} | full p={stats['full']['p_raw']:.4f} "
          f"obs={stats['full']['observed_top1']:.4f} pins={len(pin_words)} "
          f"({art['pinning_anchors']}) | wall {art['wall_clock_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
