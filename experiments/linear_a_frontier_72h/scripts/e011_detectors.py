#!/usr/bin/env python3
"""EPOCH-011 — unit-slot + arithmetic-totals detectors (frontier F5, gate A).

Prereg: epochs/EPOCH-011/prereg.md
plan_hash 38e5762b187cdda84d49e41c726d1c8df39108577a73fbd1269f96345478d25c (frozen 2026-07-08T04:46:45Z)

Stages (must run in order; PC first per protocol):
    python3 e011_detectors.py pc      # PC-A (geomA+geomB), PC-B — synthetic only
    python3 e011_detectors.py lb      # rule/variant selection (KN) + grading (KN-test, non-KN) + nulls
    python3 e011_detectors.py la      # blind LA application (gated on LB fire flags in lb output)
    python3 e011_detectors.py cross   # cross-check C (fractions vs slots)

Everything mechanical; seed 20260708. All features value-blind (Art. XI).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import unicodedata
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from e007_ledger_roles import (Doc, Tok, parse_lb, parse_la, ledger_filter,  # noqa: E402
                               gold_lb, detach_numerals, _blind, binom_sf, holm)

CAMP = os.path.dirname(HERE)
WORKTREE = os.path.dirname(os.path.dirname(CAMP))
OUT = os.path.join(CAMP, "data", "ledger_roles", "detectors")
SEED = 20260708
PLAN_HASH = "38e5762b187cdda84d49e41c726d1c8df39108577a73fbd1269f96345478d25c"


def save(name, obj):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    with open(p, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)
    print("wrote", p)


def load(name):
    return json.load(open(os.path.join(OUT, name)))


# ===================================================================== shared

def doc_split_parity(docs):
    """sha1(doc_id) parity halves (frozen)."""
    a, b = [], []
    for d in docs:
        h = int(hashlib.sha1(d.doc_id.encode()).hexdigest(), 16)
        (a if h % 2 == 0 else b).append(d)
    return a, b


def type_fn_rate(docs):
    """Unlabeled: per hashed type, followed-by-numeral rate within the partition."""
    n = Counter(); hit = Counter()
    for d in docs:
        for li, ti, t in d.groups():
            line = d.lines[li]
            n[t.bid] += 1
            if ti + 1 < len(line) and line[ti + 1].kind == "N":
                hit[t.bid] += 1
    return {b: hit[b] / n[b] for b in n}


# ============================================================ Detector A: unit-slot

RULES_A = ["R1_TRUE", "R2_prev_num", "R3_prev_group", "R4_not_line_initial",
           "R5_prev_num_and_fn50", "R6_fn50"]


def a_candidates(docs, rule, fn=None):
    """Yield (doc_id, site, li, ti, tok) for occurrences matching the rule."""
    if fn is None:
        fn = type_fn_rate(docs)
    out = []
    for d in docs:
        for li, ti, t in d.groups():
            line = d.lines[li]
            if t.n_signs != 1:
                continue
            if not (ti + 1 < len(line) and line[ti + 1].kind == "N"):
                continue
            prev_num = ti > 0 and line[ti - 1].kind == "N"
            prev_grp = ti > 0 and line[ti - 1].kind == "G"
            first_g = next(i for i, x in enumerate(line) if x.kind == "G")
            not_li = ti != first_g
            fn50 = fn.get(t.bid, 0.0) >= 0.5
            x = {"R1_TRUE": True, "R2_prev_num": prev_num, "R3_prev_group": prev_grp,
                 "R4_not_line_initial": not_li, "R5_prev_num_and_fn50": prev_num and fn50,
                 "R6_fn50": fn50}[rule]
            if x:
                out.append((d.doc_id, d.site, li, ti, t))
    return out


def a_grade(docs, cands, gold_fn):
    """F1 for gold-U against candidate set (occurrence-level)."""
    cand_keys = {(c[0], c[2], c[3]) for c in cands}
    tp = fp = fn_ = 0
    for d in docs:
        for li, ti, t in d.groups():
            is_c = (d.doc_id, li, ti) in cand_keys
            is_u = gold_fn(t) == "U"
            if is_c and is_u:
                tp += 1
            elif is_c:
                fp += 1
            elif is_u:
                fn_ += 1
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn_) if tp + fn_ else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"tp": tp, "fp": fp, "fn": fn_, "precision": round(prec, 4),
            "recall": round(rec, 4), "f1": round(f1, 4)}


def a_select(train_docs, gold_fn):
    fn = type_fn_rate(train_docs)
    scores = {}
    for rule in RULES_A:
        g = a_grade(train_docs, a_candidates(train_docs, rule, fn), gold_fn)
        scores[rule] = g
    best = max(RULES_A, key=lambda r: scores[r]["f1"])
    return best, scores


# ========================================================= Detector B: totals

VARIANTS_B = [(v, a) for v in ("V1", "V2", "V3") for a in ("A1", "A2")]


def doc_numerals(d):
    """Numerals in reading order: (li, ti, value)."""
    out = []
    for li, line in enumerate(d.lines):
        for ti, t in enumerate(line):
            if t.kind == "N":
                out.append((li, ti, t.num))
    return out


def sum_consistent(nums, variant):
    """Indices i of sum-consistent numerals under V1/V2/V3."""
    vals = [v for _, _, v in nums]
    k = len(vals)
    tot = sum(vals)
    hits = []
    for i, v in enumerate(vals):
        if v <= 0:
            continue
        if variant == "V1":
            if k >= 3 and abs(v - (tot - v)) < 1e-9:
                hits.append(i)
        elif variant == "V2":
            if i >= 2 and abs(v - sum(vals[:i])) < 1e-9:
                hits.append(i)
        elif variant == "V3":
            s = 0.0
            for j in range(i - 1, -1, -1):
                s += vals[j]
                if i - j >= 2 and abs(v - s) < 1e-9:
                    hits.append(i)
                    break
                if s > v + 1e-9:
                    break
    return hits


def attribute(d, li, ti, rule):
    """Attribute numeral at (li,ti) to a group token per A1/A2; None if none."""
    line = d.lines[li]
    if rule == "A1":
        for j in range(ti - 1, -1, -1):
            if line[j].kind == "G":
                return line[j]
    else:  # A2 line-initial group before the numeral
        for j in range(0, ti):
            if line[j].kind == "G":
                return line[j]
    return None


def b_candidates(docs, variant, attr):
    """(doc,type)-deduped candidates: dict (doc_id -> set of bids) + occurrence list."""
    occ = []
    for d in docs:
        nums = doc_numerals(d)
        for i in sum_consistent(nums, variant):
            li, ti, v = nums[i]
            g = attribute(d, li, ti, attr)
            if g is not None:
                occ.append((d.doc_id, d.site, g, v))
    dedup = {}
    for doc_id, site, g, v in occ:
        dedup.setdefault((doc_id, g.bid), (doc_id, site, g, v))
    return list(dedup.values()), occ


def b_grade(docs, cands, gold_fn):
    """Precision over (doc,type) candidates; recall over all gold-T occurrences in docs."""
    tp = sum(1 for _, _, g, _ in cands if gold_fn(g) == "T")
    prec = tp / len(cands) if cands else 0.0
    # recall denominator: gold-T (doc,type) pairs in the partition
    gold_pairs = set()
    hit_pairs = {(doc_id, g.bid) for doc_id, _, g, _ in cands if gold_fn(g) == "T"}
    for d in docs:
        for li, ti, t in d.groups():
            if gold_fn(t) == "T":
                gold_pairs.add((d.doc_id, t.bid))
    rec = len(hit_pairs & gold_pairs) / len(gold_pairs) if gold_pairs else 0.0
    return {"n_candidates": len(cands), "tp": tp, "precision": round(prec, 4),
            "n_gold_pairs": len(gold_pairs), "recall": round(rec, 4)}


def b_select(docs, gold_fn):
    scores = {}
    for v, a in VARIANTS_B:
        cands, _ = b_candidates(docs, v, a)
        g = b_grade(docs, cands, gold_fn)
        p, r = g["precision"], g["recall"]
        g["f1"] = round(2 * p * r / (p + r), 4) if p + r else 0.0
        scores[f"{v}+{a}"] = g
    best = max(scores, key=lambda k: scores[k]["f1"])
    return best, scores


def b_perm_null(docs, variant, attr, gold_fn, reps, seed0):
    """Permute numeral values among numeral positions within each doc."""
    precs = []
    for r in range(reps):
        rng = np.random.default_rng(seed0 + r)
        pdocs = []
        for d in docs:
            nd = Doc(d.doc_id, d.site)
            vals = [t.num for line in d.lines for t in line if t.kind == "N"]
            perm = list(rng.permutation(vals))
            it = iter(perm)
            for line in d.lines:
                nl = []
                for t in line:
                    if t.kind == "N":
                        nl.append(Tok("N", num=float(next(it))))
                    else:
                        nl.append(t)
                nd.lines.append(nl)
            pdocs.append(nd)
        cands, _ = b_candidates(pdocs, variant, attr)
        g = b_grade(pdocs, cands, gold_fn)
        precs.append(g["precision"])
    return precs


def b_maxnum_baseline(docs, attr, gold_fn):
    """Adversarial comparator: attribute the doc's max numeral."""
    cands = []
    for d in docs:
        nums = doc_numerals(d)
        if not nums:
            continue
        li, ti, v = max(nums, key=lambda x: x[2])
        g = attribute(d, li, ti, attr)
        if g is not None:
            cands.append((d.doc_id, d.site, g, v))
    dedup = {}
    for doc_id, site, g, v in cands:
        dedup.setdefault((doc_id, g.bid), (doc_id, site, g, v))
    return b_grade(docs, list(dedup.values()), gold_fn)


# ============================================================ synthetic corpora

def synth_A(n_docs, seed, geometry):
    """geomA: name COMMOD UNIT num  |  geomB: name COMMOD num UNIT num (LB metrology)."""
    rng = np.random.default_rng(seed)
    names = [f"n{i}" for i in range(400)]
    commods = [f"C{i}" for i in range(8)]
    units = [f"U{i}" for i in range(3)]
    header_pool = [f"h{i}" for i in range(40)]

    def G(sym, ns):
        return Tok("G", raw=sym, n_signs=ns, bid=_blind(sym))

    docs = []
    for di in range(n_docs):
        d = Doc(f"SYN{geometry}{di}", "SYN")
        d.lines.append([G(str(rng.choice(header_pool)), int(rng.integers(2, 5)))])
        for _ in range(int(rng.integers(3, 9))):
            line = [G(str(rng.choice(names)), int(rng.integers(2, 5))),
                    G(str(rng.choice(commods)), 1)]
            q = int(rng.lognormal(2.0, 1.0)) + 1
            if geometry == "A":
                if rng.random() < 0.6:
                    line.append(G(str(rng.choice(units)), 1))
                line.append(Tok("N", num=float(q)))
            else:
                line.append(Tok("N", num=float(q)))
                if rng.random() < 0.6:
                    line.append(G(str(rng.choice(units)), 1))
                    line.append(Tok("N", num=float(int(rng.integers(1, 12)))))
            d.lines.append(line)
        docs.append(d)

    def gold_syn(t):
        if t.raw.startswith("U"):
            return "U"
        if t.raw.startswith("C"):
            return "C"
        return "W"
    return docs, gold_syn


def synth_B(n_docs, seed):
    """Entry lines name COMMOD num; totals line totw COMMOD sum-num; distractor big quantities."""
    rng = np.random.default_rng(seed)
    names = [f"n{i}" for i in range(400)]
    commods = [f"C{i}" for i in range(8)]
    header_pool = [f"h{i}" for i in range(40)]

    def G(sym, ns):
        return Tok("G", raw=sym, n_signs=ns, bid=_blind(sym))

    docs = []
    for di in range(n_docs):
        d = Doc(f"SYNB{di}", "SYN")
        d.lines.append([G(str(rng.choice(header_pool)), int(rng.integers(2, 5)))])
        total = 0
        for _ in range(int(rng.integers(3, 9))):
            q = int(rng.lognormal(2.0, 1.2)) + 1
            total += q
            d.lines.append([G(str(rng.choice(names)), int(rng.integers(2, 5))),
                            G(str(rng.choice(commods)), 1), Tok("N", num=float(q))])
        d.lines.append([G("totw", 2), G(str(rng.choice(commods)), 1),
                        Tok("N", num=float(total))])
        docs.append(d)

    def gold_syn(t):
        if t.raw == "totw":
            return "T"
        if t.raw.startswith("C"):
            return "C"
        return "W"
    return docs, gold_syn


# ==================================================================== stages

def stage_pc():
    res = {"stage": "PC", "plan_hash": PLAN_HASH, "seed": SEED}
    # PC-A: both geometries, full pipeline (select on synth-train, grade synth-test)
    pca = {}
    for geom in ("A", "B"):
        docs, gold = synth_A(150, SEED + (0 if geom == "A" else 1), geom)
        tr, te = docs[:75], docs[75:]
        best, scores = a_select(tr, gold)
        g = a_grade(te, a_candidates(te, best), gold)
        pca[f"geom{geom}"] = {"selected_rule": best, "train_scores": scores,
                              "test": g, "pass": g["f1"] >= 0.90}
    res["PC_A"] = pca
    res["PC_A_pass"] = all(v["pass"] for v in pca.values())
    # PC-B: selection procedure on synth-train, grade synth-test
    docs, gold = synth_B(150, SEED + 2)
    tr, te = docs[:75], docs[75:]
    best, scores = b_select(tr, gold)
    v, a = best.split("+")
    cands, _ = b_candidates(te, v, a)
    g = b_grade(te, cands, gold)
    res["PC_B"] = {"selected_variant": best, "train_scores": scores, "test": g,
                   "pass": g["precision"] >= 0.90 and g["recall"] >= 0.90}
    res["PC_B_pass"] = res["PC_B"]["pass"]
    save("e011_pc.json", res)
    print(json.dumps({"PC_A_pass": res["PC_A_pass"], "PC_B_pass": res["PC_B_pass"],
                      "PC_A_rules": {k: v["selected_rule"] for k, v in pca.items()},
                      "PC_B_variant": best}, indent=1))


def stage_lb():
    pc = load("e011_pc.json")
    assert pc["PC_A_pass"] and pc["PC_B_pass"], "PC must pass before LB stage"
    lb = ledger_filter(parse_lb())
    kn = [d for d in lb if d.site == "KN"]
    nonkn = [d for d in lb if d.site != "KN"]
    kn_tr, kn_te = doc_split_parity(kn)
    res = {"stage": "LB", "plan_hash": PLAN_HASH,
           "n_docs": {"KN_train": len(kn_tr), "KN_test": len(kn_te), "nonKN": len(nonkn)}}

    # ---- Detector A
    best_a, sel_scores = a_select(kn_tr, gold_lb)
    g_kn_te = a_grade(kn_te, a_candidates(kn_te, best_a), gold_lb)
    g_nonkn = a_grade(nonkn, a_candidates(nonkn, best_a), gold_lb)
    # null N-A1: numeral-detach on nonKN, 25 reps
    null_f1 = []
    for r in range(25):
        rng = np.random.default_rng(SEED + 100 + r)
        nd = [detach_numerals(d, rng) for d in nonkn]
        null_f1.append(a_grade(nd, a_candidates(nd, best_a), gold_lb)["f1"])
    p95_a = float(np.percentile(null_f1, 95))
    fires_a = (g_kn_te["f1"] >= 0.60 and g_nonkn["f1"] >= 0.50 and g_nonkn["f1"] > p95_a)
    res["A"] = {"selected_rule": best_a, "selection_scores_KN_train": sel_scores,
                "KN_test": g_kn_te, "nonKN": g_nonkn,
                "N_A1_numeral_detach": {"reps": 25, "f1_p95": round(p95_a, 4),
                                        "f1_max": round(max(null_f1), 4)},
                "fire_criteria": {"a_KNtest_f1_ge_.60": g_kn_te["f1"] >= 0.60,
                                  "b_nonKN_f1_ge_.50": g_nonkn["f1"] >= 0.50,
                                  "c_gt_null_p95": g_nonkn["f1"] > p95_a},
                "fires": fires_a}

    # ---- Detector B
    best_b, sel_b = b_select(kn, gold_lb)
    fallback_used = False
    if all(v["tp"] == 0 for v in sel_b.values()):
        best_b = pc["PC_B"]["selected_variant"]
        fallback_used = True
    v, a = best_b.split("+")
    cands, _ = b_candidates(nonkn, v, a)
    g_b = b_grade(nonkn, cands, gold_lb)
    null_prec = b_perm_null(nonkn, v, a, gold_lb, 25, SEED + 200)
    p95_b = float(np.percentile(null_prec, 95))
    base = b_maxnum_baseline(nonkn, a, gold_lb)
    fires_b = (g_b["precision"] >= 0.30 and g_b["recall"] >= 0.10
               and g_b["precision"] > p95_b and g_b["n_candidates"] >= 10)
    # per-candidate detail for the report
    cand_detail = Counter((gold_lb(g), ) for _, _, g, _ in cands)
    res["B"] = {"selected_variant": best_b, "fallback_used": fallback_used,
                "selection_scores_KN": sel_b, "nonKN": g_b,
                "candidate_gold_mix": {k[0]: n for k, n in cand_detail.items()},
                "N_B1_value_perm": {"reps": 25, "prec_p95": round(p95_b, 4),
                                    "prec_max": round(max(null_prec), 4)},
                "baseline_maxnum": base,
                "fire_criteria": {"a_prec_ge_.30": g_b["precision"] >= 0.30,
                                  "b_rec_ge_.10": g_b["recall"] >= 0.10,
                                  "c_gt_null_p95": g_b["precision"] > p95_b,
                                  "d_n_ge_10": g_b["n_candidates"] >= 10},
                "fires": fires_b}
    save("e011_lb.json", res)
    print(json.dumps({"A_rule": best_a, "A_KNtest_f1": g_kn_te["f1"],
                      "A_nonKN_f1": g_nonkn["f1"], "A_null_p95": p95_a, "A_fires": fires_a,
                      "B_variant": best_b, "B": g_b, "B_null_p95": p95_b,
                      "B_baseline": base, "B_fires": fires_b}, indent=1))


def stage_la():
    lb = load("e011_lb.json")
    la = ledger_filter(parse_la())
    ht = [d for d in la if d.site == "Haghia Triada"]
    nonht = [d for d in la if d.site != "Haghia Triada"]
    res = {"stage": "LA", "plan_hash": PLAN_HASH,
           "n_docs": {"LA": len(la), "HT": len(ht), "nonHT": len(nonht)}}

    # ---- Detector A LA leg (gated)
    if lb["A"]["fires"]:
        rule = lb["A"]["selected_rule"]
        cands = a_candidates(la, rule)
        per_type = defaultdict(lambda: {"n": 0, "sites": set(), "docs": set()})
        for doc_id, site, li, ti, t in cands:
            e = per_type[t.raw]
            e["n"] += 1; e["sites"].add(site); e["docs"].add(doc_id)
        types = {k: {"n": v["n"], "n_docs": len(v["docs"]), "sites": sorted(v["sites"])}
                 for k, v in per_type.items()}
        cls = {k: v for k, v in types.items() if v["n"] >= 3}
        multi_site = [k for k, v in cls.items() if len(v["sites"]) >= 2]
        # LOSO robustness: recompute type stats within folds
        loso = {}
        for name, fold in (("HT", ht), ("nonHT", nonht)):
            fc = a_candidates(fold, rule)
            cnt = Counter(t.raw for _, _, _, _, t in fc)
            loso[name] = {k: n for k, n in cnt.most_common()}
        a_d = len(cls) >= 2
        a_e = len(multi_site) >= 1
        res["A"] = {"rule": rule, "n_candidates": len(cands),
                    "types_all": dict(sorted(types.items(), key=lambda kv: -kv[1]["n"])),
                    "candidate_class_ge3": cls, "multi_site_types": multi_site,
                    "criteria": {"d_ge2_types_ge3hits": a_d, "e_ge1_multisite": a_e},
                    "loso_candidate_counts": loso,
                    "transfers": a_d and a_e}
    else:
        res["A"] = {"gated": "LB did not fire; LA leg not run for record"}

    # ---- Detector B LA leg (gated)
    if lb["B"]["fires"]:
        v, a = lb["B"]["selected_variant"].split("+")
        cands, occ = b_candidates(la, v, a)
        # chance model: attribution of ALL numerals (no sum test), (doc,type) dedup
        allpairs = {}
        for d in la:
            for li, ti, val in doc_numerals(d):
                g = attribute(d, li, ti, a)
                if g is not None:
                    allpairs.setdefault((d.doc_id, g.bid), g.raw)
        share = Counter(allpairs.values())
        n_all = sum(share.values())
        cand_types = Counter(g.raw for _, _, g, _ in cands)
        n_c = len(cands)
        pvals = {}
        for tgt, key in (("KU-RO", "T1_KURO"), ("PO-TO-KU-RO", "T2_POTOKURO")):
            p = share.get(tgt, 0) / n_all if n_all else 0.0
            k = cand_types.get(tgt, 0)
            pvals[key] = binom_sf(k, n_c, p) if n_c and p > 0 else 1.0
            res.setdefault("B_checks", {})[key] = {
                "k": k, "n": n_c, "chance_p": round(p, 5),
                "p_binomial": pvals[key]}
        adj = holm(pvals)
        # LOSO directional
        loso = {}
        for name, fold in (("HT", ht), ("nonHT", nonht)):
            fc, _ = b_candidates(fold, v, a)
            fall = {}
            for d in fold:
                for li, ti, val in doc_numerals(d):
                    g = attribute(d, li, ti, a)
                    if g is not None:
                        fall.setdefault((d.doc_id, g.bid), g.raw)
            fshare = Counter(fall.values())
            fn_all = sum(fshare.values())
            p = fshare.get("KU-RO", 0) / fn_all if fn_all else 0.0
            k = sum(1 for _, _, g, _ in fc if g.raw == "KU-RO")
            loso[name] = {"n_candidates": len(fc), "kuro_hits": k,
                          "kuro_rate": round(k / len(fc), 4) if fc else None,
                          "chance_p": round(p, 5),
                          "directional": (k / len(fc) > p) if fc and p > 0 else None}
        # new candidates
        halves = {d.doc_id: int(hashlib.sha1(d.doc_id.encode()).hexdigest(), 16) % 2
                  for d in la}
        newc = {}
        for (doc_id, bid), (di, site, g, val) in zip(
                [(c[0], c[2].bid) for c in cands], cands):
            pass
        per_new = defaultdict(lambda: {"n": 0, "sites": set(), "halves": set(),
                                       "docs": [], "values": []})
        for doc_id, site, g, val in cands:
            if g.raw in ("KU-RO", "PO-TO-KU-RO"):
                continue
            e = per_new[g.raw]
            e["n"] += 1; e["sites"].add(site); e["halves"].add(halves[doc_id])
            e["docs"].append(doc_id); e["values"].append(val)
        newc = {k: {"n": v["n"], "sites": sorted(v["sites"]),
                    "split_half_replicated": len(v["halves"]) == 2,
                    "docs": v["docs"], "totals_values": v["values"]}
                for k, v in per_new.items() if v["n"] >= 2}
        res["B"] = {"variant": lb["B"]["selected_variant"], "n_candidates": n_c,
                    "candidate_types": dict(cand_types.most_common()),
                    "holm_adjusted": {k: round(vv, 6) for k, vv in adj.items()},
                    "T1_pass": adj["T1_KURO"] < 0.05,
                    "loso_KURO": loso,
                    "new_totals_candidates_ge2": newc,
                    "transfers": adj["T1_KURO"] < 0.05}
    else:
        res["B"] = {"gated": "LB did not fire; LA leg not run for record"}
    save("e011_la.json", res)
    print(json.dumps(res, indent=1, default=str)[:4000])


FRACT_GLYPHS = set("¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉⁄")


def is_fraction_event(raw):
    if any(c in FRACT_GLYPHS for c in raw):
        return True
    return any(0x10760 <= ord(c) <= 0x10774 for c in raw)


def stage_cross():
    la_res = load("e011_la.json")
    cand_types = set()
    if "candidate_class_ge3" in la_res.get("A", {}):
        cand_types = set(la_res["A"]["candidate_class_ge3"])
    data = json.load(open(os.path.join(WORKTREE, "corpus", "silver",
                                       "inscriptions_structured.json")))
    seen = {}
    for x in data:
        seen.setdefault(x["id"], x)
    # rebuild ledger-doc id set from parse
    ledger_ids = {d.doc_id for d in ledger_filter(parse_la())}
    dist = Counter()
    n_prev_cand = 0
    n_fr = 0
    base_positions = 0
    base_cand = 0
    frac_docs = 0
    for x in seen.values():
        if x["id"] not in ledger_ids:
            continue
        lines = []
        cur = []
        for ev in x.get("stream", []):
            if ev.get("t") == "nl":
                lines.append(cur); cur = []
            else:
                cur.append(ev)
        if cur:
            lines.append(cur)
        has_fr = any(ev.get("t") == "other" and is_fraction_event(ev.get("raw", ""))
                     for line in lines for ev in line)
        if not has_fr:
            continue
        frac_docs += 1
        for line in lines:
            for i, ev in enumerate(line):
                t = ev.get("t")
                if t == "word":
                    base_positions += 1
                    raw = "-".join(ev["signs"])
                    if raw in cand_types:
                        base_cand += 1
                elif t == "num":
                    base_positions += 1
                if t == "other" and is_fraction_event(ev.get("raw", "")):
                    n_fr += 1
                    if i == 0:
                        dist["line_initial"] += 1
                        continue
                    p = line[i - 1]
                    pt = p.get("t")
                    if pt == "num":
                        dist["numeral"] += 1
                    elif pt == "other" and is_fraction_event(p.get("raw", "")):
                        dist["fraction"] += 1
                    elif pt == "word":
                        raw = "-".join(p["signs"])
                        if raw in cand_types:
                            dist["unit_candidate_word"] += 1
                            n_prev_cand += 1
                        elif len(p["signs"]) == 1:
                            dist["other_single_sign_word"] += 1
                        else:
                            dist["multi_sign_word"] += 1
                    else:
                        dist["other"] += 1
    base_rate = base_cand / base_positions if base_positions else 0.0
    p_binom = binom_sf(n_prev_cand, n_fr, base_rate) if n_fr and base_rate > 0 else None
    res = {"stage": "CROSS", "plan_hash": PLAN_HASH,
           "n_fraction_bearing_ledger_docs": frac_docs,
           "n_fraction_events": n_fr,
           "predecessor_distribution": dict(dist),
           "unit_candidate_base_rate": round(base_rate, 5),
           "n_prev_is_unit_candidate": n_prev_cand,
           "p_binomial_enrichment": p_binom,
           "note": "non-gating coherence check (prereg C)"}
    save("e011_cross.json", res)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"pc": stage_pc, "lb": stage_lb, "la": stage_la, "cross": stage_cross}[sys.argv[1]]()
