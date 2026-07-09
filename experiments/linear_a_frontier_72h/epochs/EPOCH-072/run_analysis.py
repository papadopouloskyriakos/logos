"""EPOCH-072 run: real corpus + positive control."""
import sys, json, copy, random
sys.path.insert(0, "experiments/linear_a_frontier_72h/epochs/EPOCH-072")
import machinery as m
from collections import Counter

CORPUS = "corpus/silver/inscriptions_structured.json"

def main():
    corpus = m.load_corpus(CORPUS)
    lib = m.libation_inscriptions(corpus)
    n_lib = len(lib)
    multi = [x for x in lib if len(m.word_forms(x)) >= 2]
    n_multi = len(multi)

    print(f"n_lib_inscriptions={n_lib}  n_multiword={n_multi}")

    # ---- REAL corpus permutation test ----
    res = m.permutation_test(lib, n_draws=2000, rng=random.Random(20240712))
    obs = res["obs"]; nm = res["null_mean"]; p = res["p"]
    print("OBS", obs)
    print("NULL_MEAN", nm)
    print("P", p)

    # top cross-site pairs (anonymized)
    cross = res["cross"]; pto = res["pair_total_occ"]; pss = res["pair_site_signs"]
    top = []
    for k in cross:
        n_sites = len(pss[k])
        n_occ = pto[k]
        np_ = sum(c.get(1,0) for c in pss[k].values())
        nm_ = sum(c.get(-1,0) for c in pss[k].values())
        tot = np_+nm_
        c = max(np_,nm_)/tot if tot else 0.5
        dom = "+" if np_ >= nm_ else "-"
        top.append((n_sites, n_occ, c, dom, k))
    top.sort(key=lambda t: (-t[0], -t[1], -t[2]))
    print("--- top cross-site pairs (anonymized) ---")
    top_pairs_str = []
    for n_sites, n_occ, c, dom, k in top[:15]:
        s = f"n_sites={n_sites}, n_occ={n_occ}, consistency={c:.3f}, dominant={dom}"
        print(s)
        top_pairs_str.append(s)

    n_sites_total = len(set(x.get("site") for x in lib))

    # ---- POSITIVE CONTROL ----
    pc = positive_control()
    print("PC", pc)

    result = {
        "task_id": "EPOCH-072",
        "method": "within-inscription word-order shuffle null; consistency of pair order; C_glob/C_cross/A_cross; L3 anonymous forms",
        "numbers": {
            "global": {
                "n_lib_inscriptions": n_lib,
                "n_multiword_inscriptions": n_multi,
                "n_testable_pairs": obs["n_testable"],
                "C_glob": obs["C_glob"],
                "C_glob_null": nm["C_glob"],
                "C_glob_p": p["C_glob"],
            },
            "cross_site": {
                "n_cross_pairs": obs["n_cross"],
                "n_sites": n_sites_total,
                "C_cross": obs["C_cross"],
                "C_cross_null": nm["C_cross"],
                "C_cross_p": p["C_cross"],
                "A_cross": obs["A_cross"],
                "A_cross_null": nm["A_cross"],
                "A_cross_p": p["A_cross"],
                "agree_frac": obs["agree_frac"],
            },
            "top_pairs": top_pairs_str,
            "positive_control": pc,
        },
    }
    json.dump(result, open("experiments/linear_a_frontier_72h/data/epoch_072/observed_stats.json", "w"), indent=2)
    # also dump full pair table
    pair_table = []
    for k in cross:
        n_sites = len(pss[k]); n_occ = pto[k]
        np_ = sum(cc.get(1,0) for cc in pss[k].values())
        nm_ = sum(cc.get(-1,0) for cc in pss[k].values())
        tot = np_+nm_
        c = max(np_,nm_)/tot if tot else 0.5
        pair_table.append({"pair": [list(k[0]), list(k[1])], "n_sites": n_sites,
                           "n_occ": n_occ, "n_plus": np_, "n_minus": nm_,
                           "consistency": c})
    json.dump(pair_table, open("experiments/linear_a_frontier_72h/data/epoch_072/cross_site_pairs.json", "w"), indent=2)
    print("DONE")

def positive_control():
    rng = random.Random(424242)
    # (a) DETECT: planted canonical order at every site
    forms_canon = [("F0","a"), ("F1","b"), ("F2","c"), ("F3","d")]
    detect_p_vals = []
    for rep in range(20):
        inscs = m.make_synthetic_corpus(4, forms_canon, n_canon_insc=24,
                                        n_random_insc=10, canon_strength=1.0, rng=rng)
        r = m.permutation_test(inscs, n_draws=500, rng=random.Random(rep))
        # detect if BOTH C_cross and A_cross enriched
        detect_p_vals.append(max(r["p"]["C_cross"], r["p"]["A_cross"]))
    detect_p = min(detect_p_vals)  # best-case detect p
    detect_flag_frac = sum(1 for pv in detect_p_vals if pv <= 0.05) / len(detect_p_vals)

    # (b) FALSE-POSITIVE: random order, same structure
    fp_flags = []
    for rep in range(20):
        inscs = m.make_synthetic_corpus(4, forms_canon, n_canon_insc=24,
                                        n_random_insc=10, random_order=True, rng=rng)
        r = m.permutation_test(inscs, n_draws=500, rng=random.Random(1000+rep))
        fp_flags.append(1 if (r["p"]["C_cross"] <= 0.05 or r["p"]["A_cross"] <= 0.05) else 0)
    false_pos_rate = sum(fp_flags) / len(fp_flags)

    # (c) POWER at observed corpus scale: use observed n_cross_pairs / n_sites
    # observed scale read from a quick run on real corpus
    corpus = m.load_corpus(CORPUS)
    lib = m.libation_inscriptions(corpus)
    obs_res = m.permutation_test(lib, n_draws=200, rng=random.Random(1))
    obs_ncross = obs_res["obs"]["n_cross"]
    obs_nsites = len(set(x.get("site") for x in lib))
    # plant a canonical order scaled to roughly match observed cross-pair count
    # choose n_canon forms so that #pairs ~ obs_ncross; pairs = C(nf,2)
    import math
    nf = 2
    while math.comb(nf, 2) < max(obs_ncross, 3):
        nf += 1
        if nf > 8: break
    nf = max(3, min(nf, 6))
    canon_forms = [(f"C{i}", f"x{i}") for i in range(nf)]
    # number of canon inscriptions ~ n_multiword observed, spread over obs_nsites
    n_multi_obs = sum(1 for x in lib if len(m.word_forms(x)) >= 2)
    n_canon = max(8, min(n_multi_obs, 40))
    power_flags = []
    for rep in range(20):
        inscs = m.make_synthetic_corpus(max(2, obs_nsites), canon_forms,
                                        n_canon_insc=n_canon, n_random_insc=max(4, n_canon//3),
                                        canon_strength=1.0, rng=rng)
        r = m.permutation_test(inscs, n_draws=500, rng=random.Random(5000+rep))
        power_flags.append(1 if (r["p"]["C_cross"] <= 0.05 and r["p"]["A_cross"] <= 0.05) else 0)
    power_est = sum(power_flags) / len(power_flags)

    pc_passed = (detect_flag_frac >= 0.8) and (false_pos_rate <= 0.10) and (power_est >= 0.5)
    return {
        "pc_verdict": "PASSED" if pc_passed else "FAILED",
        "detect_p": detect_p,
        "detect_flag_frac": detect_flag_frac,
        "false_pos_rate": false_pos_rate,
        "power_est": power_est,
        "pc_is_synthetic": True,
        "power_scale": {"obs_n_cross_pairs": obs_ncross, "obs_n_sites": obs_nsites,
                        "n_canon_forms": nf, "n_canon_insc": n_canon},
    }

if __name__ == "__main__":
    main()
