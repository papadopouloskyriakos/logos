#!/usr/bin/env python3
"""EPOCH-007 runner: PC1 -> LB leg (+nulls) -> LA leg. All thresholds from prereg."""
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e007_ledger_roles import (  # noqa: E402
    CAMP, OUTDIR, SEED, GOLD_CLASSES,
    parse_lb, parse_la, gold_lb, gold_lb_secondary_D, ledger_filter,
    type_stats, fit_pipeline, predict, grade,
    run_null, label_perm_null, synth_corpus,
    la_gold_check_sets, doc_level_check, binom_sf, holm,
)
from collections import Counter, defaultdict  # noqa: E402

os.makedirs(OUTDIR, exist_ok=True)
R = {"seed": SEED,
     "deviations": [
         {"id": "DEV-1", "when": "PC1 calibration, before any real-corpus run",
          "what": "added 2 preceding-token structural features (prev_is_group, prev_group_len)",
          "why": "PC1 FAILED (macro-F1 0.692, recall(U)=0): unit-slot vs commodity-slot needs left context",
          "calibrated_on": "synthetic control only"},
         {"id": "DEV-2", "when": "PC1 calibration, before any real-corpus run",
          "what": "k-means k: 5 -> 12 (many-to-one decode absorbs extra clusters)",
          "why": "k=5 never allocated a unit cluster; synthetic-only sweep {6:.71,8:.71,10:.92,12:1.00}",
          "calibrated_on": "synthetic control only"},
     ]}

# ---------------------------------------------------------------- PC1 FIRST
print("== PC1 synthetic positive control ==", flush=True)
syn, gold_syn = synth_corpus(150, SEED)
syn = ledger_filter(syn)
half = len(syn) // 2
rng = np.random.default_rng(SEED)
order = rng.permutation(len(syn))
syn_d = [syn[i] for i in order[:half]]
syn_h = [syn[i] for i in order[half:]]
m_syn = fit_pipeline(syn_d, gold_syn)
roles_s, meta_s, _ = predict(m_syn, syn_h, type_stats(syn_h))
g_syn = grade(roles_s, meta_s, gold_syn)
R["PC1"] = {"n_docs_deriv": len(syn_d), "n_docs_held": len(syn_h), **g_syn,
            "threshold_macro_f1": 0.80,
            "pass": bool(g_syn["macro_f1"] >= 0.80)}
print(json.dumps(R["PC1"], indent=1))
if not R["PC1"]["pass"]:
    R["verdict"] = "ROLE_INDUCTION_NO_POWER"
    R["verdict_reason"] = "PC1 machinery control failed"
    json.dump(R, open(os.path.join(OUTDIR, "e007_results.json"), "w"), indent=1)
    sys.exit(0)

# ---------------------------------------------------------------- LB leg
print("== LB leg ==", flush=True)
lb = ledger_filter(parse_lb())
deriv = [d for d in lb if d.site == "KN"]
held = [d for d in lb if d.site != "KN"]
R["LB_corpus"] = {"ledger_docs": len(lb), "deriv_KN": len(deriv), "held_nonKN": len(held),
                  "held_sites": dict(Counter(d.site for d in held))}
print(R["LB_corpus"])

model = fit_pipeline(deriv, gold_lb)
roles_d, meta_d, _ = predict(model, deriv, model["deriv_stats"])
g_deriv = grade(roles_d, meta_d, gold_lb)
roles_h, meta_h, _ = predict(model, held, type_stats(held))
g_held = grade(roles_h, meta_h, gold_lb)
R["LB_derivation"] = g_deriv
R["LB_heldout"] = g_held
R["LB_cluster_mapping"] = {str(k): v for k, v in model["mapping"].items()}
# secondary descriptive: where does o-pe-ro land
d_idx = [i for i, m in enumerate(meta_h) if gold_lb_secondary_D(m[4])]
R["LB_secondary_D_opero_heldout"] = dict(Counter(roles_h[i] for i in d_idx))
print("deriv:", json.dumps(g_deriv["per_class"]), g_deriv["macro_f1"])
print("held :", json.dumps(g_held["per_class"]), g_held["macro_f1"], flush=True)

print("== nulls (N1 shuffle, N2 numeral-detach; 25 reps each; full refit) ==", flush=True)
n1 = run_null(deriv, held, gold_lb, "shuffle", 25, SEED + 1000)
n2 = run_null(deriv, held, gold_lb, "detach", 25, SEED + 2000)
n3_accs = label_perm_null(roles_h, meta_h, gold_lb, 1000, SEED + 3000)


def pct(v, q):
    return float(np.percentile(np.array(v), q))


n1_f1 = [g["macro_f1"] for g in n1]
n2_f1 = [g["macro_f1"] for g in n2]
R["N1_shuffled_doc"] = {"reps": 25, "macro_f1_p95": round(pct(n1_f1, 95), 4),
                        "macro_f1_max": round(max(n1_f1), 4),
                        "acc_p95": round(pct([g["accuracy"] for g in n1], 95), 4)}
R["N2_numeral_detach"] = {"reps": 25, "macro_f1_p95": round(pct(n2_f1, 95), 4),
                          "macro_f1_max": round(max(n2_f1), 4),
                          "acc_p95": round(pct([g["accuracy"] for g in n2], 95), 4)}
R["N3_label_perm"] = {"reps": 1000, "acc_p95": round(pct(n3_accs, 95), 4),
                      "acc_p99": round(pct(n3_accs, 99), 4),
                      "p_value_acc": float((1 + sum(1 for a in n3_accs if a >= g_held["accuracy"])) / 1001)}
print("N1 p95 macroF1:", R["N1_shuffled_doc"]["macro_f1_p95"],
      "N2 p95:", R["N2_numeral_detach"]["macro_f1_p95"],
      "N3 acc p95:", R["N3_label_perm"]["acc_p95"], flush=True)

fires = (
    g_held["macro_f1"] >= 0.50
    and g_held["macro_f1"] > R["N1_shuffled_doc"]["macro_f1_p95"]
    and g_held["macro_f1"] > R["N2_numeral_detach"]["macro_f1_p95"]
    and g_held["accuracy"] > R["N3_label_perm"]["acc_p95"]
    and g_held["per_class"]["T"]["recall"] >= 0.50
    and g_held["per_class"]["C"]["recall"] >= 0.50
)
R["LB_fires"] = bool(fires)
R["LB_fire_criteria"] = {
    "a_macro_f1_ge_.50": g_held["macro_f1"] >= 0.50,
    "b_gt_N1_p95": g_held["macro_f1"] > R["N1_shuffled_doc"]["macro_f1_p95"],
    "b_gt_N2_p95": g_held["macro_f1"] > R["N2_numeral_detach"]["macro_f1_p95"],
    "c_acc_gt_N3_p95": g_held["accuracy"] > R["N3_label_perm"]["acc_p95"],
    "d_recall_T_ge_.50": g_held["per_class"]["T"]["recall"] >= 0.50,
    "d_recall_C_ge_.50": g_held["per_class"]["C"]["recall"] >= 0.50,
}
print("LB FIRES:", fires, R["LB_fire_criteria"], flush=True)

if not fires:
    R["verdict"] = "ROLE_INDUCTION_NO_POWER"
    R["verdict_reason"] = "LB detector did not fire under prereg criteria"
    json.dump(R, open(os.path.join(OUTDIR, "e007_results.json"), "w"), indent=1)
    print("VERDICT:", R["verdict"])
    sys.exit(0)

# ---------------------------------------------------------------- LA leg
print("== LA leg ==", flush=True)
la = ledger_filter(parse_la())
R["LA_corpus"] = {"ledger_docs": len(la), "sites": dict(Counter(d.site for d in la))}
la_stats = type_stats(la)
roles_a, meta_a, _ = predict(model, la, la_stats)
share = Counter(roles_a)
n_all = len(roles_a)
role_share = {r: share.get(r, 0) / n_all for r in GOLD_CLASSES}
R["LA_predicted_role_share"] = {k: round(v, 4) for k, v in role_share.items()}

checks = la_gold_check_sets(meta_a)
targets = {"C1_KURO": "T", "C2_LOGO": "C", "C3_KIRO": "T", "C4_APREFIX": "W"}
raw_p, detail = {}, {}
for ck, idxs in checks.items():
    tgt = targets[ck]
    occ_hits = sum(1 for i in idxs if roles_a[i] == tgt)
    succ, ndoc = doc_level_check(idxs, roles_a, meta_a, tgt)
    p = binom_sf(succ, ndoc, role_share[tgt]) if ndoc else 1.0
    raw_p[ck] = p
    detail[ck] = {"target": tgt, "occurrences": len(idxs), "occ_hits": occ_hits,
                  "docs": ndoc, "doc_successes": succ,
                  "chance_rate": round(role_share[tgt], 4), "p_raw": float(p)}
adj = holm(raw_p)
for ck in detail:
    detail[ck]["p_holm"] = float(adj[ck])
    detail[ck]["holm_significant"] = bool(adj[ck] < 0.05)
R["LA_checks"] = detail
print(json.dumps(detail, indent=1), flush=True)

# LOSO folds: HT vs pooled non-HT (directional)
folds = {"HT": lambda s: s == "Haghia Triada", "nonHT": lambda s: s != "Haghia Triada"}
loso = {}
for fname, fpred in folds.items():
    fr = {}
    fold_idx = [i for i, m in enumerate(meta_a) if fpred(m[1])]
    fshare = Counter(roles_a[i] for i in fold_idx)
    fn_all = max(1, len(fold_idx))
    for ck in ("C1_KURO", "C2_LOGO"):
        tgt = targets[ck]
        idxs = [i for i in checks[ck] if fpred(meta_a[i][1])]
        succ, ndoc = doc_level_check(idxs, roles_a, meta_a, tgt)
        chance = fshare.get(tgt, 0) / fn_all
        fr[ck] = {"docs": ndoc, "doc_successes": succ, "chance": round(chance, 4),
                  "directional_pass": bool(ndoc > 0 and succ / ndoc > chance)}
    loso[fname] = fr
R["LA_LOSO"] = loso
print(json.dumps(loso, indent=1), flush=True)

primary_ok = detail["C1_KURO"]["holm_significant"] and detail["C2_LOGO"]["holm_significant"]
loso_ok = all(loso[f][ck]["directional_pass"] for f in loso for ck in ("C1_KURO", "C2_LOGO"))
if primary_ok and loso_ok:
    R["verdict"] = "ROLE_INDUCTION_VALIDATED_LB_AND_TRANSFERS"
else:
    R["verdict"] = "ROLE_INDUCTION_VALIDATED_LB_ONLY"
R["verdict_reason"] = f"primary_holm_ok={primary_ok}, loso_directional_ok={loso_ok}"

# ------------------------------------------------- new constraints output
per_type = defaultdict(list)
for i, (doc_id, site, li, ti, t) in enumerate(meta_a):
    per_type[t.raw].append((site, roles_a[i]))
constraints = []
for raw, occ in sorted(per_type.items(), key=lambda kv: -len(kv[1])):
    if len(occ) < 3:
        continue
    cnt = Counter(r for _, r in occ)
    modal, mn = cnt.most_common(1)[0]
    sites = defaultdict(Counter)
    for s, r in occ:
        sites[s][r] += 1
    multi = [s for s in sites if sum(sites[s].values()) >= 2]
    stable = [s for s in multi if sites[s].most_common(1)[0][0] == modal]
    constraints.append({
        "group": raw, "n_occ": len(occ), "modal_role": modal,
        "modal_frac": round(mn / len(occ), 3),
        "n_sites": len(sites),
        "cross_site_stable": bool(len(multi) >= 2 and len(stable) == len(multi)),
        "site_breakdown": {s: dict(c) for s, c in sites.items()},
    })
json.dump({"prereg_plan_hash": "6c85277da7c4e5d30abdd12bca084db4076c4f12e334225f5a5c535dfc2be566",
           "claim_layer": "L2/L3 functional-slot constraints, PROPOSED; no value claims",
           "role_legend": {"W": "name/lexical-slot", "C": "commodity-slot", "U": "unit-slot",
                            "T": "totals/function-slot"},
           "constraints": constraints},
          open(os.path.join(OUTDIR, "la_role_constraints.json"), "w"), indent=1)
R["LA_new_constraints"] = {"n_types_ge3occ": len(constraints),
                           "n_cross_site_stable": sum(1 for c in constraints if c["cross_site_stable"]),
                           "file": "data/ledger_roles/la_role_constraints.json"}

json.dump(R, open(os.path.join(OUTDIR, "e007_results.json"), "w"), indent=1)
print("VERDICT:", R["verdict"], R["verdict_reason"])
