#!/usr/bin/env python3
"""oneshot_run.py — PREREG_FINAL §4: the one-shot gate run on the REAL held-out labels.

Frozen protocol (commit 23da20d, DOI 10.5281/zenodo.21168887, deposited 2026-07-03T14:35:02Z
BEFORE this file was written): single configuration (§C: PPMI w2/cds0.75/SVD d24 seed 0 both
sides, Procrustes on train pairs, NN over the 73 DĀMOS-attested candidates, toponym pins per
Addendum B), primary axis = stratified h=20 from the 49 eligible (selection seed 20260710),
secondary axis = the Cypriot-eleven block (DESCRIPTIVE, never gate-deciding), N=1,
n_perm=2000 (null seed 20260711, ONE generator consumed sequentially: primary then secondary),
add-one p, LOTO over the five non-queried toponym forms + toponym-off floor, fail-closed §H
verdict computed FROM THE PERSISTED ARTIFACT (never asserted in prose first).

The real held-out labels are compared against predictions exactly once, here. The LOTO battery
and the floor are deterministic re-scorings of this single run's persisted per-sign artifacts.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _ROOT)

from power_precheck import _git, load_design                        # noqa: E402
from phase1_power import ALLOC, ELEVEN, load_strata                 # noqa: E402
import steele_meissner_2017 as SM                                   # noqa: E402
from scripts.cross_script import data as D                          # noqa: E402
from scripts.cross_script import embeddings as E                    # noqa: E402
from scripts.cross_script.align_methods import Procrustes           # noqa: E402
from scripts.comparison.searchlog import SearchLog                  # noqa: E402

SELECTION_SEED = 20260710
NULL_SEED = 20260711
N_PERM = 2000
ALPHA = 0.05                       # N=1 (secondary descriptive) => corrected_p == p_raw
CELL_ORDER = [("False", "T1"), ("False", "T2"), ("False", "T3"),
              ("True", "T1"), ("True", "T2"), ("True", "T3")]
BANNED_MODULES = ("PIL", "cv2", "skimage", "torchvision", "scripts.palaeo")

CONFIG = (("aligner", "procrustes"), ("d", 24), ("window", 2), ("cds", 0.75),
          ("emb_seed", 0), ("channel", "toponym_pins_addendumB"))


def axis_run(name, EA, U, true_val, held, train, forms_idx, rng, slog):
    """One axis: fit-once observed scoring + the sequential 2000-draw permuted-graph null,
    all seven scorings (full / LOTO x5 / toponym-off) computed per draw. Returns the artifact."""
    n = len(true_val)
    held_set = set(held.tolist())

    def qualifying_forms(x):
        return [fi for fi, form in enumerate(forms_idx)
                if x in form and all((y == x) or (y not in held_set) for y in form)]

    pin_forms = {int(x): qualifying_forms(int(x)) for x in held}

    def nn_preds(assign):
        m = Procrustes().fit(EA, U, [(i, int(assign[i])) for i in train])
        S = m.similarity(EA, U)
        order = np.argsort(-S[held], axis=1)
        return order[:, 0], order

    def score(assign, preds, drop=None):
        """drop=None: full; drop=int f: LOTO form f; drop='ALL': toponym-off."""
        hits = 0
        for j, x in enumerate(held):
            forms = pin_forms[int(x)]
            if drop == "ALL":
                forms = []
            elif drop is not None:
                forms = [f for f in forms if f != drop]
            if forms:
                hits += int(true_val[x] == assign[x])       # pin predicts the conventional value
            else:
                hits += int(preds[j] == assign[x])
        return hits / len(held)

    scorings = ["full"] + [f"loto_{t['lb']}" for t in SM.TOPONYM_EQUATIONS if not t["queried"]] + ["off"]
    drops = [None, 0, 1, 2, 3, 4, "ALL"]

    preds_obs, order_obs = nn_preds(true_val)
    obs = {sc: score(true_val, preds_obs, dr) for sc, dr in zip(scorings, drops)}
    slog.log_candidate(dict(CONFIG), f"axis:{name}", ())

    null = {sc: np.empty(N_PERM) for sc in scorings}
    for k in range(N_PERM):
        pi = true_val[rng.permutation(n)]
        preds_k, _ = nn_preds(pi)
        for sc, dr in zip(scorings, drops):
            null[sc][k] = score(pi, preds_k, dr)
        slog.log_candidate({"draw": k}, f"null:{name}", ())
    for sc, dr in zip(scorings, drops):
        if dr not in (None, "ALL"):
            slog.log_candidate(dict(CONFIG) | {"loto": sc}, f"loto:{name}", ())

    stats = {}
    for sc in scorings:
        p = float((1 + np.sum(null[sc] >= obs[sc] - 1e-12)) / (N_PERM + 1))
        stats[sc] = {"observed_top1": obs[sc], "null_mean": float(null[sc].mean()),
                     "null_p95": float(np.percentile(null[sc], 95)), "p_raw": p,
                     "corrected_p": p,              # N=1 per the freeze
                     "clears": p < ALPHA,
                     "null_degenerate": bool(null[sc].std() < 1e-12)}

    per_sign = []
    for j, x in enumerate(held):
        rank = int(np.where(order_obs[j] == true_val[x])[0][0]) + 1
        per_sign.append({"sign_id": ANCHORS[x], "true_value": CANDS[true_val[x]],
                         "nn_pred": CANDS[preds_obs[j]], "nn_rank_of_true": rank,
                         "pinned_by": [SM_FORMS[f] for f in pin_forms[int(x)]],
                         "final_hit_full": bool(pin_forms[int(x)] or preds_obs[j] == true_val[x])})
    return {"held_out": [ANCHORS[x] for x in held], "n_train": len(train),
            "n_pinned": sum(1 for x in held if pin_forms[int(x)]),
            "stats": stats, "per_sign": per_sign}


def verdict_from_artifact(axis, slog_ok):
    """§H mapping, computed from the persisted stats — fail-closed."""
    st = axis["stats"]
    if any(st[sc]["null_degenerate"] for sc in st) or not slog_ok:
        return "INCOMPLETE"
    loto = [sc for sc in st if sc.startswith("loto_")]
    if st["full"]["clears"]:
        return "CONFIRM" if all(st[sc]["clears"] for sc in loto) else "REFUTE_LOTO_FRAGILE"
    return "REFUTE"


def main() -> int:
    global ANCHORS, CANDS, SM_FORMS
    t0 = time.time()
    anchors, candidates, U, true_val = load_design()
    ANCHORS, CANDS = anchors, candidates
    SM_FORMS = [t["lb"] for t in SM.TOPONYM_EQUATIONS if not t["queried"]]
    n = len(anchors)
    aidx = {s: i for i, s in enumerate(anchors)}
    forms_idx = [tuple(aidx[s] for s in t["la_signs"])
                 for t in SM.TOPONYM_EQUATIONS if not t["queried"]]

    # REAL LA-side embeddings (the one place real features meet real labels, once)
    a_inv, a_seqs, _ = D.load_a()
    vocab_a, EA_full = E.embed(a_seqs, d=24, window=2, cds=0.75, seed=0)
    assert all(s in vocab_a for s in anchors), "anchor missing from LA embedding vocab"
    EA = np.vstack([EA_full[vocab_a[s]] for s in anchors])

    # PRIMARY held-out: the frozen stratified draw, selection seed 20260710
    cells = load_strata(anchors)
    rng_sel = np.random.default_rng(SELECTION_SEED)
    held_p = []
    for k in CELL_ORDER:
        if ALLOC[k]:
            held_p.extend(rng_sel.choice(cells[k], size=ALLOC[k], replace=False).tolist())
    held_p = np.array(sorted(held_p))
    train_p = np.array(sorted(set(range(n)) - set(held_p.tolist())))

    held_s = np.array(sorted(aidx[s] for s in ELEVEN))
    train_s = np.array(sorted(set(range(n)) - set(held_s.tolist())))

    slog = SearchLog()
    rng_null = np.random.default_rng(NULL_SEED)      # ONE generator, primary then secondary
    print(f"[oneshot] primary: h={len(held_p)} train={len(train_p)}; "
          f"secondary(desc): h={len(held_s)} train={len(train_s)}; n_perm={N_PERM}", flush=True)
    primary = axis_run("primary", EA, U, true_val, held_p, train_p, forms_idx, rng_null, slog)
    secondary = axis_run("secondary_descriptive", EA, U, true_val, held_s, train_s,
                         forms_idx, rng_null, slog)

    dirty = [m for m in sys.modules
             if any(m == b or m.startswith(b + ".") for b in BANNED_MODULES)]
    slog_ok = slog.n_eff > 0 and not dirty

    artifact = {
        "prereg": {"freeze_commit": "23da20dfba200fc1c623e0ea3ce9ff86b8f8ed9f",
                   "file_sha256": "a74f99e79614128c17615672b664dcacd34c58d407e469557ff41da45daf055f",
                   "zenodo_doi": "10.5281/zenodo.21168887",
                   "zenodo_published": "2026-07-03T14:35:02.478025+00:00"},
        "run_head_commit": _git("rev-parse", "HEAD"),
        "config": dict(CONFIG), "n_trials_per_axis": 1,
        "seeds": {"selection": SELECTION_SEED, "null": NULL_SEED, "embeddings": 0},
        "n_perm": N_PERM, "alpha": ALPHA, "n_axes_confirmatory": 1,
        "primary": primary, "secondary_descriptive": secondary,
        "searchlog": {"n_eff": slog.n_eff, "n_logged": slog.n_logged},
        "banned_modules_in_process": dirty,
        "wall_clock_s": round(time.time() - t0, 1),
    }
    artifact["primary"]["verdict"] = verdict_from_artifact(primary, slog_ok)
    artifact["secondary_descriptive"]["verdict_descriptive_only"] = \
        verdict_from_artifact(secondary, slog_ok)
    artifact["gate_verdict"] = artifact["primary"]["verdict"]

    out = os.path.join(_HERE, "results", "oneshot_gate.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False,
                  default=lambda o: o.item() if hasattr(o, "item") else str(o))
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"\nartifact: {out}\nsha256:  {sha}")
    print(f"GATE VERDICT (primary axis): {artifact['gate_verdict']}")
    print(f"secondary (descriptive only): "
          f"{artifact['secondary_descriptive']['verdict_descriptive_only']}")
    print(f"wall: {artifact['wall_clock_s']}s  searchlog n_eff={slog.n_eff} "
          f"n_logged={slog.n_logged}  banned_modules={dirty}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
