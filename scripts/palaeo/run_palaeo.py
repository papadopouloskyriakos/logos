#!/usr/bin/env python3
"""run_palaeo.py -- run the sign-image I-JEPA probe end to end and report.

Pipeline:
  1. bound("medium")           -- cap threads + address space (agora_guard pattern)
  2. render_signs              -- (re)build the glyph corpus if missing
  3. fit ClassicalEmbedder     -- HOG + Hu + shape-context (torch-LESS baseline)
  4. fit JepaEmbedder (if torch)-- real I-JEPA, latent-target prediction + EMA
  5. validate (a)/(b)/(c)      -- allograph clustering, damaged recall, cross-script
                                  image alignment; each for BOTH representations
  6. write results JSON + print a comparison table

The whole point is the HONEST I-JEPA-vs-classical comparison: the expert audits
predicted classical wins on ~90 small glyph images, and Track B's sequence null
(procrustes 0.0205 ~= 1/69 chance) sets the bar for the cross-script image result.

Usage:  PYTHONPATH=scripts python3 scripts/palaeo/run_palaeo.py [--epochs N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palaeo.palaeo_common import bound, list_a_images, list_b_images, SEED  # noqa: E402
from palaeo import classical, validate  # noqa: E402


def _banner(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def _aggregate_seeds(per_seed):
    """Mean across I-JEPA seeds.  Numeric scalars get a '_std' companion; dicts of
    per-kind rates are averaged; meta is taken from seed 0."""
    import numpy as _np
    agg = {"n_seeds": len(per_seed), "_is_mean_over_seeds": True}
    meta = per_seed[0]["embed_meta"]
    meta["n_seeds"] = len(per_seed)
    agg["embed_meta"] = meta
    for sec in ("allograph", "damaged", "cross_script"):
        merged = dict(per_seed[0][sec])               # keep structure + chance fields
        for k, v in list(merged.items()):
            vals = [r[sec].get(k) for r in per_seed]
            if isinstance(v, (int, float)) and all(isinstance(x, (int, float)) for x in vals):
                arr = _np.array(vals, dtype=float)
                merged[k] = float(arr.mean())
                merged[k + "_std"] = float(arr.std())
            elif isinstance(v, dict):                 # average only numeric-valued dicts
                # (e.g. recall_by_damage); keep seed-0 for non-numeric (families, ...)
                def _num(x):
                    try:
                        float(x); return True
                    except (TypeError, ValueError):
                        return False
                if v and all(_num(val) for val in v.values()) and \
                        all(_num(r[sec].get(k, {}).get(next(iter(v)))) for r in per_seed):
                    merged[k] = {kk: float(_np.mean([float(r[sec][k][kk]) for r in per_seed]))
                                 for kk in v}
        agg[sec] = merged
    return agg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--skip-jepa", action="store_true", help="force classical-only")
    ap.add_argument("--jepa-seeds", type=int, default=3,
                    help="I-JEPA is noisy at this tiny scale (CPU torch is not fully "
                         "deterministic); train N models and report mean+/-std.")
    args = ap.parse_args()

    bound("medium")
    np.random.seed(SEED)

    # 1. corpus
    if not args.no_render or not list_a_images():
        from palaeo import render_signs
        _banner("STEP 1  render sign-image corpus")
        render_signs.main()
    a_imgs = list_a_images(); b_imgs = list_b_images()
    base_paths = [p for _, p in a_imgs] + [p for _, p in b_imgs]
    print(f"[corpus] {len(a_imgs)} Linear A + {len(b_imgs)} Linear B = {len(base_paths)} glyph images")

    embedders = {}
    # 2. classical
    _banner("STEP 2  fit CLASSICAL representation (HOG + Hu + shape-context)")
    t0 = time.time()
    cls = classical.ClassicalEmbedder(pca_dim=48).fit(base_paths)
    embedders["classical"] = cls
    print(f"[classical] fit in {time.time()-t0:.1f}s; dim={cls.embed(base_paths[:3]).shape[1]}")

    # 3. I-JEPA (multi-seed: tiny-model SSL is noisy on CPU; report mean+/-std)
    from palaeo import jepa
    jepa_models = []
    if args.skip_jepa or not jepa.TORCH_OK:
        if not jepa.TORCH_OK and not args.skip_jepa:
            print(f"\n[jepa] torch UNAVAILABLE ({getattr(jepa,'_IMPORT_ERR','?')}) -- "
                  "FALLING BACK to classical-only (the audits-predicted winner anyway).")
    else:
        try:
            import torch as _t
            _t.use_deterministic_algorithms(True, warn_only=True)
        except Exception:
            pass
        _banner(f"STEP 3  fit I-JEPA (Assran et al. 2023) -- {args.epochs} epochs x {args.jepa_seeds} seeds, CPU")
        for s in range(args.jepa_seeds):
            t0 = time.time()
            je = jepa.JepaEmbedder(epochs=args.epochs, seed=SEED + s).fit(base_paths)
            jepa_models.append(je)
            print(f"[ijepa] seed {SEED+s} trained in {time.time()-t0:.1f}s; "
                  f"dim={je.embed(base_paths[:3]).shape[1]}")

    # 4. validations
    results = {"seed": SEED, "corpus": {"linA": len(a_imgs), "linB": len(b_imgs)}}

    def run_validations(name, emb, seed=SEED):
        t0 = time.time()
        a = validate.val_allograph(emb.embed)
        b = validate.val_damaged(emb.embed, n_variants=5, seed=SEED)   # fixed damaged set
        c = validate.val_cross_script(emb.embed, n_splits=200, held_frac=0.2, seed=seed)
        print(f"  (a) allograph NN-purity = {a['nn_purity']:.3f}  "
              f"[chance {a['nn_purity_chance']:.3f}, p={a['nn_purity_p']:.3f}]  "
              f"silhouette={a['silhouette']:.3f}")
        print(f"  (b) damaged recall@1    = {b['recall_at_1']:.3f}  "
              f"[chance {b['chance']:.4f}]   by-kind: "
              + ", ".join(f"{k}={v:.2f}" for k, v in b['recall_by_damage'].items()))
        print(f"  (c) cross-script image  = direct {c['recovery_direct_nn']:.4f} "
              f"[{c['recovery_direct_ci95'][0]:.3f},{c['recovery_direct_ci95'][1]:.3f}] / "
              f"procrustes {c['recovery_procrustes']:.4f} "
              f"[{c['recovery_procrustes_ci95'][0]:.3f},{c['recovery_procrustes_ci95'][1]:.3f}]   "
              f"[chance 1/{c['nB_image_pool']}={c['chance_image']:.4f}]")
        print(f"      Track B seq-null best = {c['trackB_best_seq']:.4f} "
              f"(~= chance {c['trackB_chance_seq']:.4f}); "
              f"image vs seq-null lift = {c['recovery_procrustes']/max(c['trackB_best_seq'],1e-9):.2f}x")
        print(f"  [{name}] {time.time()-t0:.1f}s")
        return {"allograph": a, "damaged": b, "cross_script": c,
                "embed_meta": getattr(emb, "meta", {"dim": emb.embed(base_paths[:2]).shape[1]})}

    # classical: single deterministic run
    _banner("STEP 4  VALIDATIONS -- CLASSICAL")
    results["classical"] = run_validations("classical", embedders["classical"])

    # I-JEPA: mean+/-std over seeds (tiny-model SSL is noisy)
    if jepa_models:
        _banner(f"STEP 4  VALIDATIONS -- I-JEPA ({len(jepa_models)} seeds, aggregated)")
        per_seed = []
        for i, je in enumerate(jepa_models):
            print(f"-- ijepa seed {SEED+i} --")
            per_seed.append(run_validations("ijepa", je, seed=SEED + i))
        results["ijepa"] = _aggregate_seeds(per_seed)
        results["ijepa_seeds_raw"] = per_seed

    # 5. compare table
    _banner("STEP 5  I-JEPA vs CLASSICAL")
    print(f"{'metric':32s} {'classical':>12s} {'ijepa':>12s} {'chance/null':>14s}")
    def g(name, *path, default=float("nan")):
        d = results.get(name)
        for k in path:
            if not isinstance(d, dict) or k not in d:
                return default
            d = d[k]
        return d
    rows = [
        ("(a) allograph NN-purity", "classical", "allograph", "nn_purity",
         results.get("classical", {}).get("allograph", {}).get("nn_purity_chance", float("nan"))),
        ("(a) allograph silhouette", "classical", "allograph", "silhouette", 0.0),
        ("(b) damaged recall@1", "classical", "damaged", "recall_at_1",
         results.get("classical", {}).get("damaged", {}).get("chance", float("nan"))),
        ("(c) cross-script direct NN", "classical", "cross_script", "recovery_direct_nn",
         results.get("classical", {}).get("cross_script", {}).get("chance_image", float("nan"))),
        ("(c) cross-script procrustes", "classical", "cross_script", "recovery_procrustes",
         results.get("classical", {}).get("cross_script", {}).get("chance_image", float("nan"))),
    ]
    for label, _n, sec, key, chance in rows:
        cv = results.get("classical", {}).get(sec, {}).get(key, float("nan"))
        if jepa_models:
            jv = results.get("ijepa", {}).get(sec, {}).get(key, float("nan"))
            js = results.get("ijepa", {}).get(sec, {}).get(key + "_std", float("nan"))
            jstr = f"{jv:.3f}±{js:.3f}"
        else:
            jstr = "n/a"
        print(f"{label:32s} {cv:>12.4f} {jstr:>16s} {chance:>14.4f}")

    outp = os.path.join(os.path.dirname(__file__), "..", "..", "corpus", "bronze",
                        "palaeo", "results_palaeo.json")
    json.dump(results, open(outp, "w"), indent=1, default=float)
    print(f"\n[done] results -> {outp}")


if __name__ == "__main__":
    main()
