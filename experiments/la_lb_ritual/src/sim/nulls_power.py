#!/usr/bin/env python3
"""§X ritual null families + power simulation — SYNTHETIC / within-script only (no real LA↔LB matching).

Estimates whether a FUTURE frozen ritual experiment could separate true continuity from chance, using
the frozen inventory's counts/lengths/sign marginals. Includes the two families unique to a post-hoc
channel: the permissive best-of-edit-search stress test (family 10) and the post-hoc channel-selection
penalty (family 12)."""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import simlib as S  # noqa: E402

N = 4000
N_CHANNELS_TRIED = 2          # administrative (closed) + ritual → post-hoc multiplicity
KNOWN_EXACT_FRACTION = 2 / 5  # only 2/5 known pairs are exact-representable (drift inadmissible)


def _lev(a, b):
    m, n = len(a), len(b); dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            cur = dp[j]; dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + (a[i - 1] != b[j - 1])); prev = cur
    return dp[n]


def mc(gen_c, gen_t, seed, edit_k=0):
    rng = random.Random(seed); hits = tot = 0
    for _ in range(N):
        cs, ts = gen_c(rng), gen_t(rng)
        if edit_k == 0:
            m = S.count_exact(cs, ts)
        else:
            ts_l = [list(t) for t in ts]
            m = sum(1 for c in cs for t in ts_l if _lev(list(c), t) <= edit_k)
        tot += m; hits += (m >= 1)
    return {"fp_rate_ge1": round(hits / N, 4), "mean_matches": round(tot / N, 4)}


def run():
    la, lb = S.la_primary_seqs(), S.lb_eval_seqs()
    signs, wts = S.sign_freq(la + lb)
    us = sorted(set(signs)); uw = [1] * len(us)
    Lp, Le = S.length_dist(la), S.length_dist(lb)
    nP, nE = len(la), len(lb)
    fam = {}
    fam["1_random_pairing"] = mc(lambda r: S.gen_seqs(nP, Lp, us, uw, r), lambda r: lb, S.SEED + 1)
    fam["2_freqmatched_synth_ritual"] = mc(lambda r: S.gen_seqs(nP, Lp, signs, wts, r), lambda r: lb, S.SEED + 2)
    fam["3_lenmatched_synth_targets"] = mc(lambda r: la, lambda r: S.gen_seqs(nE, Le, signs, wts, r), S.SEED + 3)
    fam["4_formula_cluster_shuffle"] = {"note": "cluster label not a match feature → degenerate", "matches": S.count_exact(la, lb)}
    fam["5_site_shuffle"] = {"note": "site not a match feature → degenerate", "matches": S.count_exact(la, lb)}
    fam["6_object_class_shuffle"] = {"note": "object class not a match feature → degenerate", "matches": S.count_exact(la, lb)}
    fam["7_matched_nonritual_controls"] = mc(lambda r: S.gen_seqs(nP, Lp, signs, wts, r), lambda r: lb, S.SEED + 7)
    def perturb(r):
        perm = dict(zip(signs, r.sample(signs, len(signs)))); return [tuple(perm.get(x, x) for x in s) for s in la]
    fam["8_perturbed_equivalence"] = mc(perturb, lambda r: lb, S.SEED + 8)
    fam["9_independent_drift_null"] = {"note": "no admissible independent drift model (D3 inadmissible) → "
                                       "no calibrated independent-drift null exists"}
    fam["10_permissive_best_of_edit"] = mc(lambda r: S.gen_seqs(nP, Lp, signs, wts, r), lambda r: lb, S.SEED + 10, edit_k=2)
    fam["11_knownpair_selection_penalty"] = {"known_exact_representable": 2, "known_drift": 3,
                                             "note": "the known pairs exhaust the exact-representable signal; "
                                                     "the 3 drift pairs cannot be recovered admissibly"}
    base_fp = fam["2_freqmatched_synth_ritual"]["fp_rate_ge1"]
    fam["12_posthoc_selection_penalty"] = {"n_channels_tried": N_CHANNELS_TRIED,
                                           "nominal_fp": base_fp,
                                           "posthoc_bounded_fp": round(min(1.0, base_fp * N_CHANNELS_TRIED), 4),
                                           "note": "channel chosen post-hoc after the administrative channel; "
                                                   "any nominal FP is inflated by the channels tried (sensitivity bound)"}
    mc_fams = [k for k in fam if isinstance(fam[k], dict) and "fp_rate_ge1" in fam[k]]
    combined = 1 - math.prod(1 - fam[k]["fp_rate_ge1"] for k in mc_fams)

    power = {
        "detection_rule": "≥1 exact recovered match (null 95th pct ≈ 0)",
        "exact_continuity": {"min_detectable_pairs": 1, "recovery": 1.0, "power": "FULL (exact only)"},
        "drift_continuity": {"admissible_model": False, "recovery": 0.0, "min_detectable_pairs": None,
                             "note": "D3 inadmissible (§VIII) → drift undetectable"},
        "permissive_edit_FP": fam["10_permissive_best_of_edit"]["fp_rate_ge1"],
        "min_useful_length": ">=3 (2-sign forms dominate the chance-collision under edit tolerance)",
        "effect_of_formulaic_clustering": "reduces effective independent units below the 9 PRIMARY / 7 cross-site",
        "effect_of_knownpair_quarantine": "removes the only exact drift exemplars from the evaluable set",
        "n_independent_primary": nP, "n_independent_eval": nE,
        "untouched_evaluation_evidence_remains": (nP >= 3 and nE >= 3),
        "prob_no_power_realistic": round(1 - KNOWN_EXACT_FRACTION, 3),
    }
    return {"channel_class": "EXPLORATORY_POSTHOC_CHANNEL", "null_families": fam,
            "combined_best_of_search_fp": round(combined, 4), "power": power}


if __name__ == "__main__":
    r = run()
    for k in sorted(r["null_families"]):
        print(f"  {k}: {r['null_families'][k]}")
    print("combined best-of-search FP:", r["combined_best_of_search_fp"])
    print("power:", r["power"])
    os.makedirs(S.RESULTS, exist_ok=True)
    json.dump(r, open(os.path.join(S.RESULTS, "ritual_nulls_power.json"), "w"), indent=1, default=str)
    print("saved ritual_nulls_power.json")
