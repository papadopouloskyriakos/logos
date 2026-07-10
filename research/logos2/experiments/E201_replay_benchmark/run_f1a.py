"""E201-F1a confirmatory (frozen plan: MILESTONE2_CONTROL_ADDENDUM @ 5deec1e).
Qualification at R_full (10 fit-anchors + 10% fit-bilingual) on holdout pairs; descriptive
ladder reported whole; abstention + leakage; 200-null calibration (67/67/66) at the LB regime;
exact CP95 upper bound vs the committed 0.02 target. Fail-closed hash verification first."""
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.stats import beta as _beta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
MASTER = 1336530913
THRESH = {"linear_b-greek.cog": 0.50, "csyl-greek.cog": 0.35, "uga-heb.no_speNL.cog": 0.60}


def seed_for(*p):
    return int(hashlib.sha256(("|".join(map(str, (MASTER, "E201F1") + p))).encode()
                              ).hexdigest()[:8], 16) % 2**31


def verify_hashes():
    manifest = {}
    for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "data_manifest.sha256")):
        h, p = line.split()
        manifest[os.path.basename(p)] = h
    for ds in THRESH:
        h = hashlib.sha256(open(os.path.join(harness.DATA, ds), "rb").read()).hexdigest()
        if manifest.get(ds) != h:
            raise SystemExit(f"HASH MISMATCH {ds} — disqualified (fail closed)")
    return True


def split_70_30(cw, pw, pairs, dataset):
    types = sorted(set(cw))
    rng = np.random.default_rng(seed_for(dataset, "split"))
    rng.shuffle(types)
    k = int(0.7 * len(types))
    fit_t = set(types[:k])
    fit_idx = [i for i, w in enumerate(cw) if w in fit_t]
    hold_idx = [i for i, w in enumerate(cw) if w not in fit_t]
    F = lambda idx: ([cw[i] for i in idx], [pw[i] for i in idx],
                     {cw[i]: pairs[cw[i]] for i in idx if cw[i] in pairs})
    return F(fit_idx), F(hold_idx)


def em_with_seeds(fit, hold, anchors, bilingual_frac, seed):
    """Fit phi on FIT side (anchors/bilingual from fit only); evaluate on HOLDOUT pairs.
    Plain lexicon for alignment = fit+hold plain words (the related corpus is inherent)."""
    fcw, fpw, fpairs = fit
    hcw, hpw, hpairs = hold
    rng = np.random.default_rng(seed)
    seed_pairs = list(anchors)
    if bilingual_frac > 0:
        k = int(round(bilingual_frac * len(fcw)))
        idx = rng.choice(len(fcw), size=k, replace=False)
        seed_pairs += [(fcw[i], fpairs[fcw[i]]) for i in idx if fcw[i] in fpairs]
    from scripts.decipher import align as alignmod, maplearn
    phi = maplearn.frequency_init(fcw, fpw + hpw)
    phi.update(harness.anchor_phi(seed_pairs))
    alignments = {}
    for it in range(25):
        alignments = alignmod.best_align(fcw, fpw + hpw, phi, sub_cost=1.0, indel_cost=1.0,
                                         max_len_delta=2)
        new_phi = maplearn.fit_map(alignmod.collect_pairs(alignments))
        merged = dict(phi); merged.update(new_phi)
        if merged == phi and it > 0:
            break
        phi = merged
    # confidence (abstention): chars with top1-top2 margin >= 2 in the final count matrix
    prs = alignmod.collect_pairs(alignments)
    M, rows_c, _ = maplearn.build_count_matrix(prs)
    conf = 0
    for i in range(M.shape[0]):
        srt = np.sort(M[i])[::-1]
        if len(srt) < 2 or srt[0] - srt[1] >= 2:
            conf += 1
    confidence = conf / max(len(rows_c), 1)
    # holdout evaluation: align HOLDOUT cipher words under frozen phi
    h_align = alignmod.best_align(hcw, fpw + hpw, phi, sub_cost=1.0, indel_cost=1.0,
                                  max_len_delta=2)
    best = {cwd: al[0] for cwd, al in h_align.items()}
    correct = [1 if best.get(c) == hpairs.get(c) else 0 for c in hcw]
    acc = float(np.mean(correct)) if correct else 0.0
    from scripts.decipher import eval as evalmod
    chance = evalmod.chance_cognate_accuracy(hcw, fpw + hpw, hpairs, 2)
    boots = []
    brng = np.random.default_rng(seed + 1)
    arr = np.array(correct, float)
    for _ in range(1000):
        boots.append(float(np.mean(brng.choice(arr, size=len(arr)))))
    return {"holdout_acc": acc, "chance": chance,
            "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "confidence": confidence, "abstained": confidence < 0.5,
            "n_holdout": len(hcw)}


def qualification(dataset):
    cw, pw, pairs = harness.load_cog(dataset)
    leak_split = len(set(cw[:0]))  # placeholder
    fit, hold = split_70_30(cw, pw, pairs, dataset)
    overlap = set(fit[0]) & set(hold[0])
    leak = harness.leak_detector(cw, pw)
    fpairs_list = list(fit[2].items())
    rng = np.random.default_rng(seed_for(dataset, "anchor_order"))
    order = rng.permutation(len(fpairs_list))
    anchors10 = [fpairs_list[i] for i in order[:10]]
    ladder = {}
    for k in (0, 1, 3, 5, 10):
        r = em_with_seeds(fit, hold, anchors10[:k], 0.0, seed_for(dataset, "lad", k))
        ladder[f"{k}_names"] = {kk: r[kk] for kk in ("holdout_acc", "chance", "abstained")}
    rfull = em_with_seeds(fit, hold, anchors10, 0.10, seed_for(dataset, "rfull"))
    thr = THRESH[dataset]
    qualifies = (rfull["holdout_acc"] >= thr and not rfull["abstained"] and
                 rfull["ci95"][0] > 2 * max(rfull["chance"], 1e-9) and
                 not leak["fired"] and not overlap)
    return {"dataset": dataset, "threshold": thr, "R_full": rfull, "ladder": ladder,
            "partition_overlap": bool(overlap), "leak": leak, "qualifies": bool(qualifies)}


def _null_campaign(args):
    kind, k = args
    cw, pw, pairs = harness.load_cog("linear_b-greek.cog")
    if kind == "shuffled_inventory":
        cw = harness.control_shuffled_inventory(cw, seed_for("null", kind, k))
        pairs = dict(zip(cw, [pairs.get(c) for c in pairs]))  # broken mapping by construction
        pairs = {c: p for c, p in zip(cw, list(p2 for p2 in pw))}
    elif kind == "synthetic_isolate":
        pw = harness.control_synthetic_isolate(pw, seed_for("null", kind, k))
        pairs = dict(zip(cw, pw))
    elif kind == "unrelated_target":
        _, gpw, _ = harness.load_cog("uga-heb.no_speNL.cog")
        rng = np.random.default_rng(seed_for("null", kind, k, "pad"))
        while len(gpw) < len(cw):
            gpw = gpw + gpw
        pw = gpw[:len(cw)]
        pairs = dict(zip(cw, pw))
    fit, hold = split_70_30(cw, pw, pairs, f"null_{kind}_{k}")
    fp = list(fit[2].items())
    rng = np.random.default_rng(seed_for("null", kind, k, "a"))
    order = rng.permutation(len(fp))
    anchors = [fp[i] for i in order[:10]]
    r = em_with_seeds(fit, hold, anchors, 0.10, seed_for("null", kind, k, "em"))
    grad = (r["holdout_acc"] >= THRESH["linear_b-greek.cog"] and
            r["holdout_acc"] >= 2 * max(r["chance"], 1e-9) and not r["abstained"])
    return {"kind": kind, "k": k, "acc": r["holdout_acc"], "chance": r["chance"],
            "abstained": r["abstained"], "false_graduation": bool(grad)}


def cp95_upper(k, n):
    return 1.0 if k == n else float(_beta.ppf(0.95, k + 1, n - k))


def main():
    t0 = time.time()
    verify_hashes()
    print("hashes OK (fail-closed check passed)", flush=True)
    quals = {}
    for ds in ("linear_b-greek.cog", "csyl-greek.cog", "uga-heb.no_speNL.cog"):
        quals[ds] = qualification(ds)
        r = quals[ds]["R_full"]
        print(f"  {ds}: R_full acc={r['holdout_acc']:.3f} (thr {THRESH[ds]}, chance "
              f"{r['chance']:.4f}) abstained={r['abstained']} -> qualifies="
              f"{quals[ds]['qualifies']}", flush=True)
    json.dump(quals, open(os.path.join(OUT, "F1a_qualification.json"), "w"), indent=1)

    jobs = ([("synthetic_isolate", i) for i in range(67)] +
            [("shuffled_inventory", i) for i in range(67)] +
            [("unrelated_target", i) for i in range(66)])
    res = []
    with ProcessPoolExecutor(max_workers=4) as ex:
        for i, r in enumerate(ex.map(_null_campaign, jobs)):
            res.append(r)
            if (i + 1) % 40 == 0:
                print(f"  nulls {i+1}/200 (false so far: "
                      f"{sum(x['false_graduation'] for x in res)})", flush=True)
    k_false = sum(r["false_graduation"] for r in res)
    ub = cp95_upper(k_false, len(res))
    calib = {"n_null": len(res), "false_graduations": k_false,
             "rate": k_false / len(res), "cp95_upper": ub,
             "target": 0.02, "passes": ub <= 0.02,
             "abstention_rate_on_nulls": float(np.mean([r["abstained"] for r in res])),
             "by_kind": {kk: {"n": sum(1 for r in res if r["kind"] == kk),
                              "false": sum(r["false_graduation"] for r in res
                                           if r["kind"] == kk)}
                         for kk in ("synthetic_isolate", "shuffled_inventory",
                                    "unrelated_target")}}
    json.dump({"campaigns": res, **calib},
              open(os.path.join(OUT, "F1a_null_calibration.json"), "w"), indent=1)

    syllabic_ok = quals["linear_b-greek.cog"]["qualifies"] or \
        quals["csyl-greek.cog"]["qualifies"]
    verdict = ("SYLLABIC_QUALIFIED" if (syllabic_ok and calib["passes"]) else
               "NOT_QUALIFIED_FOR_LINEAR_A_POSITIVE_INFERENCE")
    summary = {"run": "E201_F1a", "confirmatory": True,
               "qualification": {ds: q["qualifies"] for ds, q in quals.items()},
               "calibration": {k: calib[k] for k in
                               ("n_null", "false_graduations", "rate", "cp95_upper",
                                "target", "passes")},
               "verdict": verdict, "runtime_s": round(time.time() - t0, 1),
               "note": ("F1b (sufficiency-curve integration) remains PENDING the CSA sweep "
                        "import under the 2.3 boundary")}
    json.dump(summary, open(os.path.join(OUT, "F1a_summary.json"), "w"), indent=1)
    print("VERDICT:", verdict, "| CP95 upper:", round(ub, 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
