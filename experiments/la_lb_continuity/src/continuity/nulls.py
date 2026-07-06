#!/usr/bin/env python3
"""§V end-to-end nulls — 10 prespecified families + best-of-search receipt.

Each null reproduces the full comparison (all candidate×target exact-identity matches) with the
signal destroyed, over N_NULL Monte-Carlo draws, and reports the end-to-end false-positive rate
FP = P(≥1 spurious match). The observed statistic (§III) is 0 matches; the nulls therefore measure
SPECIFICITY — how often chance alone yields a continuity — which is the load-bearing quantity given
that 8/11 PRIMARY candidates are only 2 signs long.
"""
import json, os, random, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import cfg, model as M, partitions as P  # noqa: E402


def _num(seq):  # keep only integer (deciphered/homomorph) signs for the frequency model
    return [x for x in seq if isinstance(x, int)]


def sign_freq(seqs):
    c = Counter()
    for s in seqs:
        c.update(_num(s))
    signs, wts = zip(*c.items())
    return list(signs), list(wts)


def length_dist(seqs):
    return [len(s) for s in seqs]


def gen_seqs(n, lengths, signs, wts, rng):
    return [tuple(rng.choices(signs, weights=wts, k=rng.choice(lengths))) for _ in range(n)]


def count_matches(cseqs, tseqs):
    tset = Counter(tseqs)
    return sum(tset.get(c, 0) for c in cseqs)          # exact-identity pairs over all comparisons


def mc_fp(gen_c, gen_t, n_draws, seed):
    rng = random.Random(seed)
    hits = 0; total = 0
    for _ in range(n_draws):
        cs, ts = gen_c(rng), gen_t(rng)
        m = count_matches(cs, ts)
        total += m; hits += (m >= 1)
    return {"draws": n_draws, "fp_rate_ge1": round(hits / n_draws, 4),
            "mean_spurious_matches": round(total / n_draws, 4)}


def run():
    cfg.verify_inputs()
    prim = [M.la_seq(c) for c in P.partitioned()["PRIMARY_B"]]
    bc = [M.la_seq(c) for c in P.primary_plus_sensitivity()]
    negc = [M.la_seq(c) for c in P.partitioned()["NEGATIVE_CONTROL"]]
    ev = [M.lb_seq(t) for t in P.load_targets() if t["development_or_evaluation_role"] == "EVALUATION"]
    negt = [M.lb_seq(t) for t in P.load_targets() if t["development_or_evaluation_role"] == "NEGATIVE_CONTROL"]
    la_signs, la_wts = sign_freq(bc + negc)
    lb_signs, lb_wts = sign_freq(ev + negt)
    Lp, Le = length_dist(prim), length_dist(ev)
    N = cfg.N_NULL

    fam = {}
    # 1 random LA↔LB pairing (uniform sign draw, candidate lengths) vs real targets
    us = sorted(set(la_signs) | set(lb_signs)); uw = [1] * len(us)
    fam["1_random_pairing"] = mc_fp(lambda r: gen_seqs(len(prim), Lp, us, uw, r), lambda r: ev, N, cfg.SEED + 1)
    # 2 sign-frequency-matched synthetic LA vs real EVAL targets
    fam["2_freqmatched_synth_LA"] = mc_fp(lambda r: gen_seqs(len(prim), Lp, la_signs, la_wts, r),
                                          lambda r: ev, N, cfg.SEED + 2)
    # 3 length-matched synthetic LB targets vs real PRIMARY candidates
    fam["3_lenmatched_synth_LB"] = mc_fp(lambda r: prim,
                                         lambda r: gen_seqs(len(ev), Le, lb_signs, lb_wts, r), N, cfg.SEED + 3)
    # 4/5 site/genre-shuffled — site/genre are NOT features of the exact-identity match → degenerate
    obs = count_matches(prim, ev)
    fam["4_site_shuffled"] = {"note": "site not a match feature → null ≡ observed", "matches": obs}
    fam["5_genre_shuffled"] = {"note": "genre not a match feature → null ≡ observed", "matches": obs}
    # 6 matched non-toponym LA controls vs real EVAL targets (real-data null)
    fam["6_nontoponym_LA_controls"] = {"matches": count_matches(negc, ev), "n_candidates": len(negc)}
    # 7 false LB targets from non-toponyms vs real PRIMARY candidates (real-data null)
    fam["7_false_LB_targets"] = {"matches": count_matches(prim, negt), "n_targets": len(negt)}
    # 8 perturbed A↔B equivalence map: random relabel of LA signs (breaks the homomorphy) vs real targets
    def perturb_LA(r):
        perm = dict(zip(la_signs, r.sample(la_signs, len(la_signs))))
        return [tuple(perm.get(x, x) for x in s) for s in prim]
    fam["8_perturbed_equivalence"] = mc_fp(perturb_LA, lambda r: ev, N, cfg.SEED + 8)
    # 9 wrong projected phonetic values (A5-style) — recount under permuted value map
    fam["9_wrong_projected_values"] = {"note": "A5 layer; observed A5 matches", "matches":
                                       len(M.match_pairs(P.partitioned()["PRIMARY_B"],
                                                         [t for t in P.load_targets()
                                                          if t["development_or_evaluation_role"] == "EVALUATION"], "A5"))}
    # 10 best-of-search: worst-case FP across every non-degenerate comparison actually run
    worst = max(fam[k]["fp_rate_ge1"] for k in fam if isinstance(fam[k], dict) and "fp_rate_ge1" in fam[k])
    # combined P(≥1 anywhere) over the independent MC families (upper bound via 1-∏(1-fp))
    import math
    fps = [fam[k]["fp_rate_ge1"] for k in fam if isinstance(fam[k], dict) and "fp_rate_ge1" in fam[k]]
    combined = 1 - math.prod(1 - f for f in fps)
    fam["10_best_of_search"] = {"worst_family_fp": worst, "combined_fp_upper_bound": round(combined, 4),
                                "families_with_mc": len(fps),
                                "note": "union FP across all MC families/layers/candidate-sets tried"}
    fam["_observed_primary_matches"] = obs
    return fam


if __name__ == "__main__":
    r = run()
    for k in sorted(r):
        print(f"  {k}: {r[k]}")
    os.makedirs(cfg.RESULTS, exist_ok=True)
    json.dump(r, open(os.path.join(cfg.RESULTS, "nulls.json"), "w"), indent=1)
    print("saved nulls.json")
