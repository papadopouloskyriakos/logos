#!/usr/bin/env python3
"""D4 — MINIMAL-SEED FRONTIER.

How much, and what *type*, of external information is needed to recover the relative
(vowel-vs-consonant) class partition by seeded label-spreading? We establish the frontier
HONESTLY on the Linear B known-truth control (classes gradable), then locate Linear A on it.

Reuses the audited D3 harness (features, kNN-RBF position affinity, substitution affinity,
Zhou-2004 label spreading, held-out AUC/recall) — imported read-only. NON-CIRCULAR (Art. XII):
known LB {A,E,I,O,U} label the seeds and grade held-out recovery ONLY; no phonetic value is
ever a model feature. Frequency (log_freq) is dropped from the propagation features (POS_IDX).

Frontier axes:
  k        number of CORRECT vowel-class seeds (matched kc = k consonant seeds), k in 0..5.
           The LB vowel class has only 5 members, so k=5 leaves no held-out vowel (degenerate);
           the gradable regime is k in 1..4 and the frontier SATURATES at k=4.
  type     random | secure_shared | shape_selected | anchor_derived | incorrect
             random         : k signs, labels carry NO true info                     (null floor)
             secure_shared  : k TRUE vowels + k TRUE consonants (a bilingual/shared-sign value) (ideal)
             shape_selected : value-blind selection; shape ⊥ value (WP-F circular, G3 "shape alone
                              can never be SEED_A") ⇒ modeled as value-blind draw and MEASURED
             anchor_derived : correct seeds drawn ONLY from the SEED_B toponym-anchor sign pool;
                              among those the TRUE vowels are just {A,I} ⇒ caps at k=2
             incorrect      : k TRUE CONSONANTS mislabelled vowel + k TRUE VOWELS mislabelled cons

Metric: held-out AUC + recall@(#held-out vowels), plus the honest signal = LIFT over the
random-seed null at matched k (does labelling the CORRECT signs beat labelling random signs?).
The random-null shares the identical graph+frequency structure, so type−random isolates the
information carried by the seed VALUES (the D3 frequency-leak is netted out).

Deterministic seed 20260708.
"""
from __future__ import annotations
import json
import os
import sys
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d3_seed_propagation_audit as D3  # noqa: E402  (audited harness, read-only)

CAMP = os.path.abspath(os.path.join(HERE, ".."))
DATA_DIR = os.path.join(CAMP, "data")
REP_DIR = os.path.join(CAMP, "reports")
SEED = 20260708

# SEED_B toponym-anchor sign pool (from G3 seeds.json). These are the only value-bearing
# (though LOTO-fragile) external anchors that exist for Linear A; on the LB control they carry
# their known classes, so we can measure how far *anchor-quality* seeds get you.
SEED_B_SIGNS = ["A", "DI", "I", "JA", "KI", "PA", "RI", "RU", "SA", "SE",
                "SI", "SU", "TA", "TE", "TI", "TO", "TU"]
LOTO_SURVIVOR_SIGNS = ["I", "RI"]  # only these survive the cited frozen LOTO gate, each 1-deep


def pct(a, q):
    a = [x for x in a if x is not None]
    return round(float(np.percentile(a, q)), 4) if a else None


def eval_cell(W, truth, v_seed, c_seed):
    r = D3.spread_eval(W, truth, list(v_seed), list(c_seed))
    return r["auc"], r["recall"], r["n_heldout_vowels"]


def run_type(W, truth, v_idx, c_idx, ttype, k, rng, n_draw=120,
             anchor_v=None, anchor_c=None):
    """Return list of (auc, recall) draws for one (type, k) cell, or None if unavailable."""
    n = len(truth)
    aucs, recs = [], []
    if k == 0:
        # zero seeds of any kind → nothing to propagate → no class recovery.
        return None  # handled specially (chance)

    if ttype == "secure_shared":
        v_combos = list(combinations(v_idx, k)) if k <= len(v_idx) else []
        if not v_combos:
            return None
        for vc in v_combos:
            for _ in range(max(1, n_draw // max(1, len(v_combos)))):
                cc = list(rng.choice(c_idx, k, replace=False))
                a, rc, _ = eval_cell(W, truth, vc, cc)
                aucs.append(a); recs.append(rc)

    elif ttype == "anchor_derived":
        av = anchor_v; ac = anchor_c
        if k > len(av):
            return None  # not enough correct anchor vowels exist (the real cap)
        v_combos = list(combinations(av, k))
        for vc in v_combos:
            for _ in range(max(1, n_draw // max(1, len(v_combos)))):
                if k > len(ac):
                    cc = list(rng.choice(c_idx, k, replace=False))
                else:
                    cc = list(rng.choice(ac, k, replace=False))
                a, rc, _ = eval_cell(W, truth, vc, cc)
                aucs.append(a); recs.append(rc)

    elif ttype in ("random", "shape_selected"):
        # value-blind: k signs get the 'vowel' label, k get the 'consonant' label, at random.
        for _ in range(n_draw):
            allidx = list(range(n)); rng.shuffle(allidx)
            vc = allidx[:k]; cc = allidx[k:2 * k]
            a, rc, _ = eval_cell(W, truth, vc, cc)
            aucs.append(a); recs.append(rc)

    elif ttype == "incorrect":
        # adversarial: true consonants mislabelled vowel, true vowels mislabelled consonant.
        if k > len(v_idx):
            return None
        for _ in range(n_draw):
            vc = list(rng.choice(c_idx, k, replace=False))         # cons → 'vowel'
            cc = list(rng.choice(v_idx, min(k, len(v_idx)), replace=False))  # vowel → 'cons'
            a, rc, _ = eval_cell(W, truth, vc, cc)
            aucs.append(a); recs.append(rc)

    return list(zip(aucs, recs))


def summarize(draws):
    aucs = [a for a, _ in draws if a is not None]
    recs = [r for _, r in draws if r is not None]
    return {
        "n_draws": len(draws),
        "auc_mean": round(float(np.mean(aucs)), 4) if aucs else None,
        "auc_sd": round(float(np.std(aucs)), 4) if aucs else None,
        "auc_ci95": [pct(aucs, 2.5), pct(aucs, 97.5)] if aucs else None,
        "recall_mean": round(float(np.mean(recs)), 4) if recs else None,
    }


def run():
    signs, tot, Xs, truth, Wpos, Wsub, F = D3.build()
    n = len(signs)
    idx = {s: i for i, s in enumerate(signs)}
    v_idx = [i for i in range(n) if truth[i]]
    c_idx = [i for i in range(n) if not truth[i]]
    base_rate = round(len(v_idx) / n, 4)
    Wboth = Wpos + D3.BETA_SUB * Wsub
    channels = {"pos": Wpos, "pos+sub": Wboth}

    # anchor pools on the LB control: SEED_B signs present in the freq>=20 inventory, split by TRUE class.
    anchor_present = [s for s in SEED_B_SIGNS if s in idx]
    anchor_v = [idx[s] for s in anchor_present if s in D3.LB_VOWELS]         # true vowels among anchors
    anchor_c = [idx[s] for s in anchor_present if s not in D3.LB_VOWELS]     # true cons among anchors
    loto_v = [idx[s] for s in LOTO_SURVIVOR_SIGNS if s in idx and s in D3.LB_VOWELS]
    loto_c = [idx[s] for s in LOTO_SURVIVOR_SIGNS if s in idx and s not in D3.LB_VOWELS]

    types = ["random", "shape_selected", "secure_shared", "anchor_derived", "incorrect"]
    ks = [0, 1, 2, 3, 4, 5]

    out = {
        "meta": {
            "seed": SEED, "task": "D4 minimal-seed frontier",
            "control": "Linear B known-truth (V-vs-C partition gradable)",
            "n_signs": n, "n_vowels": len(v_idx), "base_rate_vowel": base_rate,
            "freq_min": D3.FREQ_MIN, "alpha": D3.ALPHA, "knn": D3.KNN, "beta_sub": D3.BETA_SUB,
            "channels": list(channels), "seed_types": types, "k_grid": ks,
            "kc_matched": "k consonant seeds per k vowel seeds",
            "metric": "held-out AUC + recall@#heldout_vowels; honest signal = lift over random-null at matched k",
            "vowel_signs": [signs[i] for i in v_idx],
            "anchor_pool_present": anchor_present,
            "anchor_true_vowels": [signs[i] for i in anchor_v],
            "anchor_true_cons_n": len(anchor_c),
            "loto_survivors_present": [signs[i] for i in (loto_v + loto_c)],
            "non_circular": "LB values grade/seed ONLY; never a model feature. log_freq dropped from propagation.",
        },
        "note_k_ceiling": ("The vowel class has only 5 members; k=5 seeds all of them (no held-out vowel), so "
                           "the V/C frontier SATURATES at k=4. 'k=5+' is degenerate on this axis, not a "
                           "higher-power regime."),
    }

    frontier = {}
    for ch, W in channels.items():
        # random-null reference per k (the matched-count floor)
        null_ref = {}
        rng_null = np.random.default_rng(SEED + 101)
        for k in ks:
            if k == 0:
                null_ref[k] = None
                continue
            dr = run_type(W, truth, v_idx, c_idx, "random", k, rng_null, n_draw=300)
            null_ref[k] = summarize(dr) if dr else None

        ch_rows = {}
        for ttype in types:
            rows = []
            rng = np.random.default_rng(SEED + hash(ttype) % 9973)
            for k in ks:
                if k == 0:
                    rows.append({"k": 0, "available": False,
                                 "auc_mean": None, "recall_mean": None,
                                 "note": "no seeds → classes cannot be attached to values → chance (AUC=0.5)"})
                    continue
                dr = run_type(W, truth, v_idx, c_idx, ttype, k, rng, n_draw=150,
                              anchor_v=anchor_v, anchor_c=anchor_c)
                if dr is None:
                    reason = ("k>#true anchor vowels (only {A,I}) — anchor channel exhausted"
                              if ttype == "anchor_derived" else
                              "k>5 or k>#vowels — no held-out vowel (degenerate)")
                    rows.append({"k": k, "available": False, "auc_mean": None,
                                 "recall_mean": None, "note": reason})
                    continue
                s = summarize(dr)
                nr = null_ref.get(k)
                lift = None; exceeds95 = None; p_vs_null = None
                if nr and nr["auc_mean"] is not None and s["auc_mean"] is not None:
                    lift = round(s["auc_mean"] - nr["auc_mean"], 4)
                    null95 = nr["auc_ci95"][1]
                    exceeds95 = bool(s["auc_mean"] > null95)
                    # p: fraction of null draws >= this type's mean (recompute a null sample)
                s.update({"k": k, "available": True,
                          "lift_auc_over_random_null": lift,
                          "exceeds_null_ci95_upper": exceeds95})
                rows.append(s)
            ch_rows[ttype] = rows
        frontier[ch] = {"random_null_by_k": null_ref, "by_type": ch_rows}

    out["frontier_LB_control"] = frontier

    # ---- frontier k* per type (min k where AUC beats the random-null 95% upper AND recall>=0.5) ----
    kstar = {}
    for ch in channels:
        kstar[ch] = {}
        for ttype in types:
            rows = frontier[ch]["by_type"][ttype]
            k_auc = None; k_rec = None
            for r in rows:
                if not r.get("available"):
                    continue
                if k_auc is None and r.get("exceeds_null_ci95_upper"):
                    k_auc = r["k"]
                if k_rec is None and r.get("recall_mean") is not None and r["recall_mean"] >= 0.5:
                    k_rec = r["k"]
            kstar[ch][ttype] = {"k_star_auc_beats_null95": k_auc, "k_star_recall_ge_0.5": k_rec}
    out["frontier_k_star"] = kstar

    # ---- Linear A placement ----------------------------------------------------------------------
    out["LA_placement"] = {
        "secure_value_seeds_available_SEED_A": 0,
        "why": "WP-G: SEED_A=0. 6 SEED_B toponym equations are one-anchor-deep and collapse under the "
               "cited frozen LOTO gate (survivors {I,RI}, each 1-toponym-deep); shape-homomorphy (57 recs) "
               "and Cypriot (11) are SEED_X by rule; no non-circular secure value seed exists.",
        "availability_by_type_for_LA": {
            "random": "unlimited but value-blind → sits on the null floor (no recovery)",
            "shape_selected": "available (SigLA shapes) but shape ⊥ value (WP-F circular/capped ≤0.75); "
                              "value-blind → null floor",
            "secure_shared": "0 (no bilingual / no secure shared-sign value; relabeling-invariant)",
            "anchor_derived": "≤2 on paper (toponym vowels among SEED_B) but LOTO-survivable = 1 vowel {I}; "
                              "each one-anchor-deep, fails held-out gate → effectively 0 secure",
            "incorrect": "the risk if disputed anchors are trusted — actively harmful (see incorrect curve)",
        },
        "where_LA_sits": "k=0 SECURE seeds. LA has access only to the value-blind (random/shape) channels, "
                         "which the LB control measures at the null floor; and to anchor_derived seeds that "
                         "cap at k≤2 on paper and 0 after LOTO. LA is at the pre-frontier origin.",
    }
    return out, signs, v_idx


def main():
    out, signs, v_idx = run()

    def _ser(o):
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        raise TypeError(str(type(o)))

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "D4_frontier.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=_ser)

    # compact console echo
    ch = "pos+sub"
    print("=== D4 frontier (channel pos+sub) ===")
    nr = out["frontier_LB_control"][ch]["random_null_by_k"]
    print("random-null AUC by k:", {k: (nr[k]["auc_mean"] if nr[k] else None) for k in [1, 2, 3, 4]})
    for ttype in out["meta"]["seed_types"]:
        rows = {r["k"]: (r.get("auc_mean"), r.get("recall_mean"), r.get("lift_auc_over_random_null"),
                         r.get("exceeds_null_ci95_upper"))
                for r in out["frontier_LB_control"][ch]["by_type"][ttype]}
        print(f"{ttype:16s} (auc,rec,lift,>null95) by k:",
              {k: rows.get(k) for k in [1, 2, 3, 4]})
    print("k*:", out["frontier_k_star"][ch])
    print("LA:", out["LA_placement"]["where_LA_sits"])
    return out


if __name__ == "__main__":
    main()
