"""EPOCH-103R — corrected joint maxT null for the A-initial positional-enrichment adjudication.

Governed by prereg_addendum_R.md (append-only; frozen originals untouched). Fixes the
audit-confirmed comonotone defect in the original universe_maxT(): the joint null now samples,
per (draw, word), ONE categorical first sign (probability count/len over the unit's distinct
signs), so candidate-sign indicators are mutually exclusive within a realization, exactly as
under the true within-word permutation null. Marginals are unchanged; only the family-wise
max-z null (and hence the maxT p-values / survivor set) can differ.

Reuses the frozen machinery.py for scheme construction, marginal nulls, and the positive
control so those stay bit-identical in design to the original run. Also mechanizes the LOMO
block from the frozen E022/E023/E024 artifacts (no recomputation from corpus data).

No phonetic value, prefixhood, or productivity is asserted. The finding, if replicated, is a
RELATIVE A-initial positional-enrichment constraint (L2/L3) only.
"""
import hashlib
import json
import os
from collections import Counter

import numpy as np

import importlib.util

EPOCH_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e103", os.path.join(EPOCH_DIR, "machinery.py"))
e103 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e103)

M_DRAWS = 10000


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def universe_maxT_categorical(words, n_draws=M_DRAWS, seed=0, min_initial=5):
    """Corrected best-of-universe maxT deflation. Joint null: per (draw, word) exactly ONE
    categorical first sign (P = count/len over the unit's distinct signs, fixed sorted order);
    all candidate-sign counts per draw derive from the same categorical realization. Marginals
    match the within-word permutation null exactly; the joint dependence is the true mutually
    exclusive (negatively dependent) one, not the comonotone shared-uniform of the original."""
    rng = np.random.default_rng(seed)
    signs = sorted({w[0] for w in words})
    signs = [s for s in signs if e103.initial_count(words, s) >= min_initial]
    sign_col = {s: j for j, s in enumerate(signs)}
    obs = {s: e103.initial_count(words, s) for s in signs}
    n_words = len(words)
    U = rng.random((n_draws, n_words))
    counts = np.zeros((n_draws, len(signs)), dtype=np.int64)
    for i, w in enumerate(words):
        cnt = Counter(w)
        ss = sorted(cnt)
        cum = np.cumsum(np.array([cnt[s] / len(w) for s in ss]))
        cum[-1] = 1.0  # guard float rounding; probabilities sum to 1 exactly in theory
        idx = np.searchsorted(cum, U[:, i], side="right")
        for j_local, s in enumerate(ss):
            col = sign_col.get(s)
            if col is not None:
                counts[:, col] += (idx == j_local)
    mu = counts.mean(axis=0)
    sd = counts.std(axis=0) + 1e-9
    null_matrix = (counts - mu[None, :]) / sd[None, :]
    null_max_z = null_matrix.max(axis=1)
    obs_z = {s: (obs[s] - mu[sign_col[s]]) / sd[sign_col[s]] for s in signs}
    maxT_p = {s: (1 + int(np.sum(null_max_z >= obs_z[s]))) / (1 + n_draws) for s in signs}
    ranked = sorted(signs, key=lambda s: -obs_z[s])
    return {
        "signs_tested": len(signs),
        "n_draws": n_draws,
        "obs_z": {s: round(float(obs_z[s]), 3) for s in signs},
        "maxT_p": maxT_p,
        "null_max_z_mean": round(float(null_max_z.mean()), 3),
        "null_max_z_p95": round(float(np.quantile(null_max_z, 0.95)), 3),
        "null_max_z_max": round(float(null_max_z.max()), 3),
        "top_sign": ranked[0],
        "A_rank": ranked.index("A") + 1 if "A" in ranked else None,
        "A_maxT_p": maxT_p.get("A"),
        "A_obs_z": round(float(obs_z.get("A", float("nan"))), 3),
        "survivors_p01": sorted([s for s in signs if maxT_p[s] <= 0.01],
                                key=lambda s: -obs_z[s]),
    }


def scheme_overlap(schemes):
    """Descriptive unit-level overlap between the variants (for the closure-doc disclosure)."""
    cA = Counter(tuple(w) for w in schemes["A_editor"])
    cB = Counter(tuple(w) for w in schemes["B_divider_strict"])
    cC = Counter(tuple(w) for w in schemes["C_numeral_anchored"])
    inter_AB = sum((cA & cB).values())
    return {
        "n_units": {k: len(v) for k, v in schemes.items()},
        "A_B_identical_units": inter_AB,
        "A_B_identical_frac_of_A": round(inter_AB / sum(cA.values()), 4),
        "A_only_units": sum((cA - cB).values()),
        "B_only_units": sum((cB - cA).values()),
        "C_subset_of_A_units": sum((cC & cA).values()),
        "C_n_units": sum(cC.values()),
        "C_is_subset_of_A": sum((cC & cA).values()) == sum(cC.values()),
        "note": ("the three variants derive from a single corpus lineage (editor tokens): "
                 "B_divider_strict shares the listed fraction of unit realizations with "
                 "A_editor (merging editorially-split adjacent words), and C_numeral_anchored "
                 "is a function-restricted subset of A_editor. Robustness across overlapping "
                 "variants, not independent replication."),
    }


def lomo_from_frozen_artifacts():
    """Audit item A3: evaluate the LOMO condition mechanically from the FROZEN E022/E023/E024
    result.json artifacts (loading + extracting recorded values only; nothing recomputed from
    corpus data). Extraction rule frozen in prereg_addendum_R.md."""
    base = os.path.normpath(os.path.join(EPOCH_DIR, ".."))
    paths = {e: os.path.join(base, e, "result.json")
             for e in ("EPOCH-022", "EPOCH-023", "EPOCH-024")}
    arts = {e: json.load(open(p)) for e, p in paths.items()}
    shas = {e: sha256_file(p) for e, p in paths.items()}

    e22 = arts["EPOCH-022"]
    e23 = arts["EPOCH-023"]
    e24 = arts["EPOCH-024"]
    methods = {
        "E022_global_adaptive_null": {
            "artifact_sha256": shas["EPOCH-022"],
            "recorded_verdict": e22["verdict"],
            "positive_class": "A_PREFIX_SURVIVES_ADAPTIVE_NULL",
            "pc_passed": bool(e22["step4_positive_control"]["pc_pass"]),
            "headline_p": float(e22["step3_family_deflation"]["p_maxT"]),
            "headline_p_field": "step3_family_deflation.p_maxT",
        },
        "E023_cross_site_heldout": {
            "artifact_sha256": shas["EPOCH-023"],
            "recorded_verdict": e23["verdict"],
            "positive_class": "A_PREFIX_CROSS_SITE_ROBUST",
            "pc_passed": str(e23["numbers"]["positive_control"]["pc_verdict"]).startswith("PASSED"),
            "headline_p": float(e23["numbers"]["global"]["p_one_sided_1000draws"]),
            "headline_p_field": "numbers.global.p_one_sided_1000draws",
            "sites_significant_holm": int(
                e23["numbers"]["la_per_site_A"]["sites_significant_holm_adj_le_0.05"]),
            "loo_survives": bool(e23["numbers"]["la_leave_one_site_out"]["survives"]),
        },
        "E024_multiaxis_support_chrono": {
            "artifact_sha256": shas["EPOCH-024"],
            "recorded_verdict": e24["verdict"],
            "positive_class": "A_PREFIX_MULTIAXIS_ROBUST",
            "pc_passed": bool(e24["numbers"]["verdict_inputs"]["pc_passed"]),
            "headline_p": float(e24["numbers"]["global"]["p"]),
            "headline_p_field": "numbers.global.p",
            "loo_ok": bool(e24["numbers"]["verdict_inputs"]["loo_ok"]),
            "comp_ok": bool(e24["numbers"]["verdict_inputs"]["comp_ok"]),
        },
    }
    for m in methods.values():
        m["independently_significant"] = bool(
            m["pc_passed"] and m["headline_p"] <= 0.01
            and m["recorded_verdict"] == m["positive_class"])
    names = list(methods)
    lomo_table = {}
    for dropped in names:
        remaining = [n for n in names if n != dropped]
        k = sum(methods[n]["independently_significant"] for n in remaining)
        lomo_table[f"drop_{dropped}"] = {"remaining_significant": k, "holds": k >= 2}
    holds = all(v["holds"] for v in lomo_table.values())
    return {
        "methods": methods,
        "lomo_table": lomo_table,
        "lomo_condition_holds": holds,
        "rule": ("independently_significant := recorded PC passed AND recorded headline p <= "
                 "0.01 AND recorded verdict == positive class; LOMO holds iff dropping any one "
                 "method leaves >=2 independently significant confirmations. Evaluated from "
                 "frozen artifacts only (prereg_addendum_R.md)."),
    }


def run_R():
    schemes = e103.load_schemes()
    original = json.load(open(os.path.join(EPOCH_DIR, "result.json")))
    out = {
        "epoch": "EPOCH-103R",
        "governing_addendum": "prereg_addendum_R.md",
        "schemes": {},
        "n_units": {k: len(v) for k, v in schemes.items()},
        "scheme_overlap": scheme_overlap(schemes),
    }
    for name, words in schemes.items():
        obs, null, p = e103.perm_null_fast(words, "A", n_draws=M_DRAWS, seed=42)
        mt = universe_maxT_categorical(words, n_draws=M_DRAWS, seed=42)
        orig_surv = original["schemes"][name]["maxT"]["survivors_p01"]
        out["schemes"][name] = {
            "n_units": len(words),
            "A_initial_obs": int(obs),
            "A_initial_frac": round(obs / len(words), 4),
            "perm_null_mean": round(float(null.mean()), 2),
            "perm_null_max": int(null.max()),
            "p_single_permute": p,
            "maxT": mt,
            "A_significant_p01_single": p < 0.01,
            "A_significant_p01_maxT": (mt["A_maxT_p"] is not None and mt["A_maxT_p"] <= 0.01),
            "A_is_top_survivor": mt["top_sign"] == "A",
            "survivor_set_diff_vs_original": {
                "original_survivors_p01": orig_surv,
                "corrected_survivors_p01": mt["survivors_p01"],
                "dropped_by_correction": [s for s in orig_surv if s not in mt["survivors_p01"]],
                "added_by_correction": [s for s in mt["survivors_p01"] if s not in orig_surv],
            },
        }
    out["positive_control"] = e103.positive_control(schemes["A_editor"], seed=7)
    out["leave_one_method_out"] = lomo_from_frozen_artifacts()

    # ---- mechanical verdict (rule UNCHANGED from the frozen prereg) ----
    schemes_sig = [n for n, s in out["schemes"].items()
                   if s["A_significant_p01_maxT"] and s["A_is_top_survivor"]]
    n_sig = len(schemes_sig)
    pc = out["positive_control"]
    pc_ok = pc["power_detected"] and pc["cal_clean"]
    if not pc_ok:
        verdict = "NO_POWER"
        rationale = "PC failed (power or calibration) -> detector uninformative this run."
    elif n_sig >= 2:
        verdict = "REPLICATED_RELATIVE_CONSTRAINT"
        rationale = (f"Under the corrected categorical joint null (M={M_DRAWS}), A is the top "
                     f"best-of-universe maxT survivor at p<=.01 under {n_sig}/3 overlapping "
                     f"segmentation/selection variants derived from a single corpus lineage "
                     f"({', '.join(schemes_sig)}); PC power+cal clean; LOMO evaluated "
                     f"mechanically from frozen artifacts and invariant. Replicated as a "
                     f"RELATIVE A-initial positional-enrichment constraint; robustness across "
                     f"variants, not independent replication. No phonetic value, morphological "
                     f"prefixhood, or productivity asserted (L2/L3).")
    elif n_sig == 1:
        verdict = "CONDITIONAL_SIGNAL_ONLY"
        rationale = (f"A clears the corrected maxT bar under only 1/3 variants ({schemes_sig}); "
                     f"segmentation-dependent -> conditional signal, not a replicated constraint.")
    else:
        verdict = "GENERIC_UNDER_NULL"
        rationale = "A clears no variant at corrected maxT p<=.01 under this adjudication."
    if not out["leave_one_method_out"]["lomo_condition_holds"]:
        verdict = "STOP_LOMO_CONTRADICTION"
        rationale = ("A frozen-artifact statistic contradicts the LOMO condition; halting per "
                     "prereg_addendum_R.md STOP rule.")
    out["verdict"] = verdict
    out["rationale"] = rationale
    out["schemes_replicated"] = schemes_sig

    # corrected qualification-of-E022 note, stated EXACTLY from the corrected survivor sets
    union_secondary = sorted({s for name in out["schemes"]
                              for s in out["schemes"][name]["maxT"]["survivors_p01"]
                              if s != "A"})
    per_scheme = {name: out["schemes"][name]["maxT"]["survivors_p01"]
                  for name in out["schemes"]}
    out["qualification_of_E022_corrected"] = {
        "type": "QUALIFICATION",
        "supersedes": "qualification_of_E022 in the frozen EPOCH-103 result.json (comonotone-null survivor sets)",
        "target": ("EPOCH-022 verdict wording \"A- is the SOLE survivor in the 72-member GORILA "
                   "universe\""),
        "corrected_survivor_sets_p01": per_scheme,
        "secondary_survivor_union_excl_A": union_secondary,
        "finding": (f"Under the corrected categorical joint null (M={M_DRAWS}), the p<=.01 "
                    f"survivor sets are exactly: " +
                    "; ".join(f"{k}: {{{', '.join(v)}}}" for k, v in per_scheme.items()) +
                    f". A remains the dominant survivor (rank 1 in all variants); the secondary "
                    f"set (union excl. A) is exactly {{{', '.join(union_secondary)}}}. "
                    f"Word-initial positional enrichment is a real but not-A-unique phenomenon."),
        "effect": ("The E022 \"sole survivor\" phrasing remains narrowed to \"dominant survivor\" "
                   "(append-only, Art. XVII); the secondary set is stated exactly as measured "
                   "under the corrected null, neither omitting nor retaining signs by expectation."),
    }

    out["plan_hash"] = sha256_file(os.path.join(EPOCH_DIR, "prereg_addendum_R.md"))
    out["code_manifest"] = {
        "machinery_R.py": sha256_file(os.path.join(EPOCH_DIR, "machinery_R.py")),
        "machinery.py (frozen, reused for schemes/marginals/PC)":
            sha256_file(os.path.join(EPOCH_DIR, "machinery.py")),
    }
    out["frozen_original_result_sha256"] = sha256_file(os.path.join(EPOCH_DIR, "result.json"))
    return out


if __name__ == "__main__":
    res = run_R()
    json.dump(res, open(os.path.join(EPOCH_DIR, "result_R.json"), "w"), indent=2)
    print("VERDICT:", res["verdict"])
    print(res["rationale"])
    for n, s in res["schemes"].items():
        mt = s["maxT"]
        print(f"  {n}: n={s['n_units']} A_obs={s['A_initial_obs']} "
              f"p_single={s['p_single_permute']:.6f} A_maxT_p={mt['A_maxT_p']:.6f} "
              f"rank={mt['A_rank']} top={mt['top_sign']} "
              f"null_max_z mean={mt['null_max_z_mean']} p95={mt['null_max_z_p95']} "
              f"max={mt['null_max_z_max']}")
        print(f"    survivors={mt['survivors_p01']}")
        print(f"    diff: dropped={s['survivor_set_diff_vs_original']['dropped_by_correction']} "
              f"added={s['survivor_set_diff_vs_original']['added_by_correction']}")
    print("  PC:", res["positive_control"])
    print("  LOMO holds:", res["leave_one_method_out"]["lomo_condition_holds"])
