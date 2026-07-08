#!/usr/bin/env python3
"""EPOCH-009: full-corpus SigLA stroke sweep.

Executes the frozen prereg epochs/EPOCH-009/prereg.md
(sha256 ec87a23b87d0c984ba47e79d6b9d8dfd0d83f397fa5a1f05cb188e3cc8d88cdc,
frozen 2026-07-08T04:44:07Z, BEFORE this script ran on any data).
Deterministic; seed 20260708. Reuses E008's validated primitives by import.
"""
import json, math, os, random, re, sys, time, unicodedata
from collections import Counter, defaultdict

import numpy as np
from PIL import Image

W = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
EXP = f"{W}/experiments/linear_a_frontier_72h"
DATA = f"{EXP}/data/stroke_corpus"
BRONZE = f"{W}/corpus/bronze"
SEED = 20260708
PREREG_HASH = "ec87a23b87d0c984ba47e79d6b9d8dfd0d83f397fa5a1f05cb188e3cc8d88cdc"

sys.path.insert(0, f"{EXP}/scripts")
from epoch008_stroke_pilot import (binarize, skeleton_graph, feat_vec, run_pc,
                                   pick_bbox_mode, despeckle)

COUNT_IDX = [0, 1, 2, 3, 4]        # endpoints junctions loops components strokes
ORIENT_IDX = [6, 7, 8, 9]

def dest_of(desig):
    return f"{DATA}/renders/{desig.replace(' ', '_').replace('/', '~')}.png"

def mrr(ranks):
    return float(np.mean([1.0 / r for r in ranks])) if ranks else None

def perm_p(rng, obs, n_q, gal_n, N=20000):
    if obs is None or n_q == 0:
        return None
    cnt = 0
    for _ in range(N):
        if mrr([rng.randint(1, gal_n) for _ in range(n_q)]) >= obs:
            cnt += 1
    return (cnt + 1) / (N + 1)

# ------------------------------------------------------------------ extraction
def extract_all(docs, fetch_log):
    """Per-instance stroke features over the whole fetched corpus."""
    inst = []          # dicts: label, doc, gi, ok, feat(11), aspect, why
    doc_meta = {}
    t0 = time.time()
    for di, d in enumerate(docs):
        desig = d["designation"]
        glyphs = [g for g in d.get("glyphs", [])
                  if g.get("sign") and g.get("bbox") and len(g["bbox"]) == 4
                  and g["bbox"][2] >= 12 and g["bbox"][3] >= 12]
        if not glyphs:
            continue
        path = dest_of(desig)
        status = fetch_log.get(desig, "missing")
        if status.startswith("ERROR") or not os.path.exists(path):
            for gi, g in enumerate(d.get("glyphs", [])):
                if g in glyphs:
                    inst.append({"label": g["sign"], "doc": desig, "gi": gi,
                                 "ok": False, "why": "doc_not_fetched"})
            continue
        try:
            img = Image.open(path); img.load()
        except Exception as e:
            for gi, g in enumerate(d.get("glyphs", [])):
                if g in glyphs:
                    inst.append({"label": g["sign"], "doc": desig, "gi": gi,
                                 "ok": False, "why": f"image_unreadable:{type(e).__name__}"})
            continue
        mode, dens, gdens = pick_bbox_mode(img, d.get("glyphs", []))
        doc_meta[desig] = {"mode": mode, "density": dens, "global_ink": gdens}
        dens_ok = max(dens.values()) > gdens if dens else False
        Wd, H = img.size
        for gi, g in enumerate(d.get("glyphs", [])):
            if g not in glyphs:
                continue
            rec = {"label": g["sign"], "doc": desig, "gi": gi, "ok": False}
            if not dens_ok:
                rec["why"] = "bbox_density_check_failed"; inst.append(rec); continue
            x, y, a, bb = g["bbox"]
            x2, y2 = (x + a, y + bb) if mode == "xywh" else (a, bb)
            xa, ya = max(0, min(x, Wd - 2)), max(0, min(y, H - 2))
            xb, yb = max(xa + 2, min(x2, Wd)), max(ya + 2, min(y2, H))
            if xb - xa < 3 or yb - ya < 3:
                rec["why"] = "degenerate_bbox"; inst.append(rec); continue
            crop = img.crop((xa, ya, xb, yb))
            if max(crop.size) > 512:                     # prereg downscale guard
                s = 512.0 / max(crop.size)
                crop = crop.resize((max(1, int(crop.size[0] * s)),
                                    max(1, int(crop.size[1] * s))), Image.LANCZOS)
            ink = despeckle(binarize(crop))
            f = skeleton_graph(ink)
            if f is None:
                rec["why"] = "empty_skeleton"; inst.append(rec); continue
            v = feat_vec(f)
            ok = (0.01 <= f["ink_fraction"] <= 0.6 and f["n_components"] <= 8
                  and np.all(np.isfinite(v)) and f["aspect"] > 0)
            rec.update(ok=bool(ok), feat=v.tolist(), aspect=float(f["aspect"]),
                       n_components=f["n_components"], ink_fraction=f["ink_fraction"])
            if not ok:
                rec["why"] = ("ink_fraction_out_of_range"
                              if not 0.01 <= f["ink_fraction"] <= 0.6
                              else "too_many_components")
            inst.append(rec)
        img.close()
        if di % 100 == 0:
            print(f"[extract {di}/{len(docs)}] {desig} "
                  f"({time.time()-t0:.0f}s, {len(inst)} inst)", flush=True)
    return inst, doc_meta

# ------------------------------------------------------------------ main
def main():
    rng = random.Random(SEED + 9)
    res = {"epoch": "EPOCH-009", "seed": SEED, "prereg_sha256": PREREG_HASH,
           "prereg_frozen_utc": "2026-07-08T04:44:07Z"}

    pc = run_pc()
    res["positive_control"] = pc
    print("PC:", pc["n_pass"], "/5", "PASS" if pc["PASS"] else "FAIL", flush=True)
    if not pc["PASS"]:
        res["verdict"] = "STROKE_CHANNEL_NOT_USABLE"
        json.dump(res, open(f"{EXP}/epochs/EPOCH-009/result.json", "w"), indent=1)
        return

    docs = json.load(open(f"{BRONZE}/sigla_browse_2026/sigla_documents.json"))
    fetch_log = json.load(open(f"{DATA}/fetch_log.json"))
    n_avail = sum(1 for v in fetch_log.values() if not v.startswith("ERROR"))
    res["acquisition"] = {"n_docs": len(docs), "n_available": n_avail,
                          "n_failed": len(docs) - n_avail,
                          "failed": sorted(d for d, v in fetch_log.items()
                                           if v.startswith("ERROR"))}
    print(f"acquisition: {n_avail}/{len(docs)} renders", flush=True)
    if n_avail < 200:
        res["verdict"] = "STROKE_CHANNEL_NOT_USABLE"
        res["abort"] = "SOURCE_BLOCKED (<200 docs)"
        json.dump(res, open(f"{EXP}/epochs/EPOCH-009/result.json", "w"), indent=1)
        return

    # frame
    cp2val = json.load(open(f"{BRONZE}/palaeo/linA_codepoint_map.json"))["linA_cp2val"]
    val2ab, ab2val = {}, {}
    for cp, val in cp2val.items():
        try:
            name = unicodedata.name(chr(int(cp)))
        except ValueError:
            continue
        if name.startswith("LINEAR A SIGN AB"):
            num = name.split("AB")[1]
            if num.isdigit():
                val2ab[val] = int(num); ab2val[int(num)] = val
    la_dir = f"{BRONZE}/sign_images/linA"; lb_dir = f"{BRONZE}/sign_images/linB"
    la = {f[:-4] for f in os.listdir(la_dir) if f.endswith(".png")}
    lb = {f[:-4] for f in os.listdir(lb_dir) if f.endswith(".png")}
    shared = json.load(open(f"{BRONZE}/sign_images/manifest.json"))["shared_values_all"]
    dark69 = [f"A{300+n}" for n in range(1, 72)
              if n not in (2, 48)]                     # A301..A371 minus A302,A348
    assert len(dark69) == 69

    inst, doc_meta = extract_all(docs, fetch_log)
    ok_inst = [r for r in inst if r.get("ok")]
    res["extraction"] = {
        "n_instances": len(inst), "n_ok": len(ok_inst),
        "ok_rate": len(ok_inst) / len(inst) if inst else 0.0,
        "fail_reasons": dict(Counter(r.get("why") for r in inst if not r.get("ok"))),
    }
    print(f"extraction: {len(ok_inst)}/{len(inst)} ok", flush=True)
    json.dump({"instances": inst, "doc_meta": doc_meta},
              open(f"{DATA}/features/instances.json", "w"), default=str)

    # aggregation
    by_label = defaultdict(list)
    for r in ok_inst:
        by_label[r["label"]].append(r)
    pool = np.array([r["feat"] for r in ok_inst])
    pmu, psd = pool.mean(0), pool.std(0); psd[psd == 0] = 1.0
    signatures = {}
    for lab, rs in by_label.items():
        F = np.array([r["feat"] for r in rs])
        la_ = np.array([math.log(r["aspect"]) for r in rs])
        z = (F - pmu) / psd
        spread = (float(np.mean([np.linalg.norm(z[i] - z[j])
                                 for i in range(len(z)) for j in range(i + 1, len(z))]))
                  if len(z) > 1 else None)
        signatures[lab] = {"n": len(rs), "mean": F.mean(0).tolist(),
                           "sd": F.std(0).tolist(),
                           "log_aspect_mean": float(la_.mean()),
                           "log_aspect_sd": float(la_.std()),
                           "allograph_spread_z": spread}
    res["aggregation"] = {
        "n_labels_usable": len(signatures),
        "n_labels_robust": sum(1 for s in signatures.values() if s["n"] >= 3),
        "median_instances_per_label": float(np.median([s["n"] for s in signatures.values()])),
    }

    # ---------------------------------------------------------------- LEG 1
    gallery = {}
    for fn in sorted(os.listdir(lb_dir)):
        if fn.endswith(".png"):
            f = skeleton_graph(binarize(Image.open(f"{lb_dir}/{fn}")))
            if f:
                gallery[fn[:-4]] = f
    G = sorted(gallery)
    Gmat = np.stack([feat_vec(gallery[g]) for g in G])
    gmu, gsd = Gmat.mean(0), Gmat.std(0); gsd[gsd == 0] = 1.0
    Gz = (Gmat - gmu) / gsd
    Gasp = np.array([math.log(gallery[g]["aspect"]) for g in G])

    def rank_stroke(vec, truth):
        q = (np.asarray(vec) - gmu) / gsd
        d = np.linalg.norm(Gz - q, axis=1)
        order = np.argsort(d, kind="stable")
        return int(np.where(np.array(G)[order] == truth)[0][0]) + 1

    def rank_aspect(log_asp, truth):
        d = np.abs(Gasp - log_asp)
        order = np.argsort(d, kind="stable")
        return int(np.where(np.array(G)[order] == truth)[0][0]) + 1

    elig = sorted(v for v in shared if v in la and v in lb and v in val2ab
                  and signatures.get(f"AB{val2ab[v]:02d}"))
    leg1 = {"eligible_frame": 57, "realized_n": len(elig), "gallery_n": len(G)}
    agg_r, asp_r, per_inst_r, detail = [], [], [], []
    for v in elig:
        lab = f"AB{val2ab[v]:02d}"
        s = signatures[lab]
        rs_ = rank_stroke(s["mean"], v)
        ra_ = rank_aspect(s["log_aspect_mean"], v)
        agg_r.append(rs_); asp_r.append(ra_)
        irs = [rank_stroke(r["feat"], v) for r in by_label[lab]]
        per_inst_r.extend(irs)
        detail.append({"value": v, "label": lab, "n_inst": s["n"],
                       "agg_stroke_rank": rs_, "agg_aspect_rank": ra_,
                       "inst_ranks": irs})
    leg1["detail"] = detail
    leg1["agg_mrr"] = mrr(agg_r)
    leg1["agg_top1"] = sum(1 for r in agg_r if r == 1)
    leg1["agg_top5"] = sum(1 for r in agg_r if r <= 5)
    leg1["aspect_mrr"] = mrr(asp_r)
    leg1["per_instance_mrr"] = mrr(per_inst_r)
    leg1["per_instance_n"] = len(per_inst_r)
    leg1["e008_pilot_mrr"] = 0.273
    leg1["p_agg"] = perm_p(rng, leg1["agg_mrr"], len(agg_r), len(G))
    leg1["chance_mrr"] = float(np.mean([1.0 / rng.randint(1, len(G))
                                        for _ in range(200000)]))
    res["leg1_calibration"] = leg1
    print("LEG1:", {k: leg1[k] for k in leg1 if k != "detail"}, flush=True)

    # ---------------------------------------------------------------- LEG 2
    stab_labels = sorted(l for l, rs in by_label.items() if len(rs) >= 4)
    halfA, halfB, asp_A, asp_B = {}, {}, {}, {}
    for lab in stab_labels:
        rs = sorted(by_label[lab], key=lambda r: (r["doc"], r["gi"]))
        A = [r for i, r in enumerate(rs) if i % 2 == 0]
        B = [r for i, r in enumerate(rs) if i % 2 == 1]
        halfA[lab] = np.mean([r["feat"] for r in A], axis=0)
        halfB[lab] = np.mean([r["feat"] for r in B], axis=0)
        asp_A[lab] = float(np.mean([math.log(r["aspect"]) for r in A]))
        asp_B[lab] = float(np.mean([math.log(r["aspect"]) for r in B]))
    leg2 = {"n_signs": len(stab_labels)}
    if stab_labels:
        Bmat = np.stack([halfB[l] for l in stab_labels])
        bmu, bsd = Bmat.mean(0), Bmat.std(0); bsd[bsd == 0] = 1.0
        Bz = (Bmat - bmu) / bsd
        Basp = np.array([asp_B[l] for l in stab_labels])
        s_r, a_r = [], []
        for i, lab in enumerate(stab_labels):
            q = (halfA[lab] - bmu) / bsd
            d = np.linalg.norm(Bz - q, axis=1)
            s_r.append(int(np.where(np.argsort(d, kind="stable") == i)[0][0]) + 1)
            da = np.abs(Basp - asp_A[lab])
            a_r.append(int(np.where(np.argsort(da, kind="stable") == i)[0][0]) + 1)
        leg2["self_mrr"] = mrr(s_r)
        leg2["self_top1"] = sum(1 for r in s_r if r == 1)
        leg2["self_top5"] = sum(1 for r in s_r if r <= 5)
        leg2["aspect_self_mrr"] = mrr(a_r)
        leg2["p_self"] = perm_p(rng, leg2["self_mrr"], len(s_r), len(stab_labels))
        leg2["chance_mrr"] = float(np.mean([1.0 / rng.randint(1, len(stab_labels))
                                            for _ in range(200000)]))
        leg2["ranks"] = {l: r for l, r in zip(stab_labels, s_r)}
    res["leg2_stability"] = {k: v for k, v in leg2.items() if k != "ranks"}
    json.dump(leg2, open(f"{DATA}/features/leg2_detail.json", "w"), indent=1)
    print("LEG2:", {k: leg2[k] for k in leg2 if k != "ranks"}, flush=True)

    # ---------------------------------------------------------------- LEG 3
    cov_us = [l for l in dark69 if l in signatures]
    cov_rb = [l for l in dark69 if l in signatures and signatures[l]["n"] >= 3]
    all_a = sorted(l for l in signatures if re.fullmatch(r"A\d+", l))
    leg3 = {"frame_69": 69, "usable": len(cov_us), "robust": len(cov_rb),
            "coverage_usable": len(cov_us) / 69, "coverage_robust": len(cov_rb) / 69,
            "missing": sorted(set(dark69) - set(cov_us)),
            "secondary_all_A_labels_usable": len(all_a)}
    res["leg3_coverage"] = leg3
    print("LEG3:", {k: leg3[k] for k in leg3 if k != "missing"}, flush=True)

    # ------------------------------------------------- similarity matrix output
    names = sorted(signatures) + [f"LBfont:{g}" for g in G]
    M = np.array([signatures[l]["mean"] for l in sorted(signatures)]
                 + [feat_vec(gallery[g]).tolist() for g in G])
    asp = np.array([signatures[l]["log_aspect_mean"] for l in sorted(signatures)]
                   + [math.log(gallery[g]["aspect"]) for g in G])
    mu, sd = M.mean(0), M.std(0); sd[sd == 0] = 1.0
    Z = (M - mu) / sd
    topo = np.linalg.norm(Z[:, None, COUNT_IDX] - Z[None, :, COUNT_IDX], axis=2)
    ori = np.abs(M[:, None, ORIENT_IDX] - M[None, :, ORIENT_IDX]).sum(2)
    aspd = np.abs(asp[:, None] - asp[None, :])
    comb = np.linalg.norm(Z[:, None, :] - Z[None, :, :], axis=2)
    np.savez_compressed(f"{DATA}/stroke_similarity_matrix.npz",
                        names=np.array(names), topology=topo, orientation=ori,
                        log_aspect=aspd, combined=comb)
    json.dump({"prereg_sha256": PREREG_HASH, "claim_layer": "L1",
               "caveat": ("Distances over hand-traced SigLA renders; trace author knew "
                          "sign identities (standardization confound); NO phonetic values; "
                          "supports no reading."),
               "names": names,
               "n_instances_per_name": {l: signatures[l]["n"] for l in sorted(signatures)},
               "channels": ["topology", "orientation", "log_aspect", "combined"],
               "combined": [[round(float(x), 4) for x in row] for row in comb]},
              open(f"{DATA}/stroke_similarity_matrix.json", "w"))
    res["matrix"] = {"n_names": len(names), "n_epigraphic": len(signatures),
                     "n_lb_font_block": len(G),
                     "files": ["data/stroke_corpus/stroke_similarity_matrix.npz",
                               "data/stroke_corpus/stroke_similarity_matrix.json"]}

    # ---------------------------------------------------------------- verdict
    L1P = (leg1["realized_n"] >= 30 and leg1["p_agg"] is not None
           and leg1["p_agg"] < 0.01 and leg1["agg_mrr"] > leg1["aspect_mrr"])
    L1W = (leg1["realized_n"] >= 30 and leg1["p_agg"] is not None
           and leg1["p_agg"] < 0.05 and leg1["agg_mrr"] > leg1["aspect_mrr"])
    L2P = (leg2["n_signs"] >= 15 and leg2.get("p_self") is not None
           and leg2["p_self"] < 0.01 and leg2["self_mrr"] > leg2["aspect_self_mrr"])
    L3P = leg3["coverage_usable"] >= 0.50
    if L1P and L2P and L3P:
        verdict = "STROKE_CHANNEL_CALIBRATED_USEFUL"
    elif L1W and (L2P or L3P):
        verdict = "STROKE_CHANNEL_CALIBRATED_WEAK"
    else:
        verdict = "STROKE_CHANNEL_NOT_USABLE"
    ps = [p for p in (leg1.get("p_agg"), leg2.get("p_self")) if p is not None]
    holm = sorted(ps)
    res["multiplicity"] = {"raw_p": ps,
                           "holm": [min(1.0, p * (len(holm) - i))
                                    for i, p in enumerate(holm)]}
    res["legs"] = {"LEG1_PASS": L1P, "LEG1_WEAK": L1W, "LEG2_PASS": L2P, "LEG3_PASS": L3P}
    res["verdict"] = verdict
    res["scale_comparison"] = {
        "aggregate_mrr": leg1["agg_mrr"], "per_instance_mrr": leg1["per_instance_mrr"],
        "e008_pilot_mrr": 0.273,
        "scale_improves": bool(leg1["agg_mrr"] and leg1["per_instance_mrr"]
                               and leg1["agg_mrr"] >= leg1["per_instance_mrr"]
                               and leg1["agg_mrr"] >= 0.273)}
    print("VERDICT:", verdict, res["legs"], flush=True)
    json.dump(res, open(f"{EXP}/epochs/EPOCH-009/result.json", "w"), indent=1, default=str)

if __name__ == "__main__":
    main()
