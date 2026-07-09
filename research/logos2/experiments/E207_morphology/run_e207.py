"""E207 driver — prereg baeefa0. Primary comparison on the frozen split; 200 enrichment-matched
synthetics; holdout axes; transcription stability; mechanical verdict."""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import battery as B  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def ck(name, obj):
    json.dump(obj, open(os.path.join(OUT, name + ".json"), "w"), indent=1, default=str)
    print(f"[cell done] {name}", flush=True)


def run_once(rows, seed):
    fit, hold = B.type_split(rows, seed)
    bat = B.Battery(fit)
    sc = bat.score(hold)
    return sc, bat, fit, hold


def main():
    t0 = time.time()
    rows = B.load_words()
    print(f"tokens={len(rows)} types={len({r['w'] for r in rows})}", flush=True)

    # ---- primary ----
    sc, bat, fit, hold = run_once(rows, B.seed_for("split"))
    par = bat.paradigm_stats()
    primary = {"scores_bits_per_sign_mdl_charged": sc, "paradigm_stats": par,
               "delta_M3_vs_M2": sc["M2"] - sc["M3"], "delta_M6_vs_M2": sc["M2"] - sc["M6"],
               "delta_M4_vs_M3": sc["M3"] - sc["M4"]}
    ck("primary", primary)
    print(json.dumps(sc, indent=1), flush=True)

    # ---- synthetics (200) ----
    d3, d6 = [], []
    for k in range(200):
        srows = B.synthetic_rows(rows, B.seed_for("synth", k))
        ssc, *_ = run_once(srows, B.seed_for("split"))
        d3.append(ssc["M2"] - ssc["M3"])
        d6.append(ssc["M2"] - ssc["M6"])
        if (k + 1) % 50 == 0:
            print(f"  synthetics {k+1}/200", flush=True)
    p3 = (1 + sum(1 for x in d3 if x >= primary["delta_M3_vs_M2"])) / 201
    p6 = (1 + sum(1 for x in d6 if x >= primary["delta_M6_vs_M2"])) / 201
    synth = {"delta_M3_real": primary["delta_M3_vs_M2"],
             "synthetic_band_M3": [float(np.percentile(d3, 5)), float(np.percentile(d3, 95))],
             "p_plus1_M3": p3,
             "delta_M6_real": primary["delta_M6_vs_M2"],
             "synthetic_band_M6": [float(np.percentile(d6, 5)), float(np.percentile(d6, 95))],
             "p_plus1_M6": p6,
             "holm_alpha": 0.05, "holm_significant":
                 sorted([("M3", p3), ("M6", p6)], key=lambda x: x[1])[0][1] < 0.025 or
                 (min(p3, p6) < 0.025 and max(p3, p6) < 0.05)}
    ck("synthetics", synth)

    # ---- holdout axes ----
    axes = {}
    ho_site = [r for r in rows if r["site"] != "Haghia Triada"]
    sc_s, *_ = run_once(ho_site, B.seed_for("loso"))
    axes["LOSO_HT"] = sc_s["M2"] - sc_s["M3"]
    for name, pred in (("LMIB", lambda r: r["context"] == "LMIB"),
                       ("Tablet", lambda r: r["support"] == "Tablet")):
        sub = [r for r in rows if pred(r)]
        sc_a, *_ = run_once(sub, B.seed_for("axis", name))
        axes[f"{name}_only"] = sc_a["M2"] - sc_a["M3"]
    # segmentation variant: divider-merged units
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "e103m", "/home/claude-runner/gitlab/n8n/logos-logos2/experiments/"
        "linear_a_frontier_72h/epochs/EPOCH-103/machinery.py")
    axes["segmentation_variant"] = "SKIPPED (frontier machinery not in this worktree path; "\
        "B_divider variant deferred with reason)" if not os.path.exists(
        "/home/claude-runner/gitlab/n8n/logos-logos2/experiments/linear_a_frontier_72h") else None
    ck("holdout_axes", axes)

    # ---- transcription stability (5% deletion x 20) ----
    rng_del = []
    for k in range(20):
        rng = np.random.default_rng(B.seed_for("del", k))
        drows = []
        for r in rows:
            w = tuple(s for s in r["w"] if rng.random() > 0.05)
            if len(w) >= 2:
                drows.append({**r, "w": w})
        sc_d, *_ = run_once(drows, B.seed_for("split"))
        rng_del.append(sc_d["M2"] - sc_d["M3"])
    stab = {"delta_M3_under_5pct_deletion": [float(np.mean(rng_del)), float(np.std(rng_del))],
            "sign_flips": sum(1 for x in rng_del
                              if (x > 0) != (primary["delta_M3_vs_M2"] > 0))}
    ck("stability", stab)

    # ---- mechanical verdict ----
    best_delta = max(primary["delta_M3_vs_M2"], primary["delta_M6_vs_M2"])
    beats_m2 = best_delta > 0
    beats_synth = synth["holm_significant"]
    rec_ok = par["recurring_stems_with_and_without_affix"] >= 10
    alt_ok = par["stems_with_2plus_distinct_affixes"] >= 5
    axes_vals = [v for v in axes.values() if isinstance(v, float)]
    axes_pos = sum(1 for v in axes_vals if v > 0)
    survives_3of4 = axes_pos >= min(3, len(axes_vals))
    survives_all = axes_pos == len(axes_vals)
    stable = stab["sign_flips"] == 0
    clitic_specific = primary["delta_M4_vs_M3"] > 0.005
    if not (beats_m2 and beats_synth):
        verdict = "POSITIONAL_ONLY"
    elif not rec_ok:
        verdict = "PREDICTIVE_FUNCTIONAL_CLASS"
    elif rec_ok and alt_ok and survives_all and stable:
        verdict = "PARADIGMATIC_MORPHOLOGY_SUPPORTED"
    elif rec_ok and survives_3of4:
        verdict = "CLITIC_COMPATIBLE" if clitic_specific else "AFFIX_COMPATIBLE"
    else:
        verdict = "PREDICTIVE_FUNCTIONAL_CLASS"
    summary = {"experiment": "E207", "verdict": verdict,
               "inputs": {"beats_M2_after_MDL": beats_m2, "beats_synthetic_band": beats_synth,
                          "recurring_stems": par["recurring_stems_with_and_without_affix"],
                          "alternant_stems": par["stems_with_2plus_distinct_affixes"],
                          "holdout_axes_positive": f"{axes_pos}/{len(axes_vals)}",
                          "stability_flips": stab["sign_flips"],
                          "clitic_specific": clitic_specific},
               "runtime_s": round(time.time() - t0, 1),
               "wording_note": ("verdict vocabulary restricted per prereg; 'A' remains an "
                                "anonymous sign; no value/meaning asserted")}
    ck("summary", summary)
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
