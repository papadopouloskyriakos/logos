#!/usr/bin/env python3
"""EPOCH-008 ADDENDUM-1: held-out confirmation of the v2 (despeckle) pipeline on
10 fresh signs. Frozen: prereg_addendum1.md sha256
197a64249b944624e38a9624781acd0a12158d3b85fab338219133799862334e; pipeline script sha256
20c397b03607f39efe49cc5e6d54813dbd7633926cb9c99fc6d6b4699b3746a7."""
import json, math, os, random, sys
from collections import defaultdict
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from epoch008_stroke_pilot import (SEED, EXP, DATA, BRONZE, binarize, despeckle,
                                   skeleton_graph, feat_vec, build_frame,
                                   fetch_doc_png, pick_bbox_mode)

def mrr(rs): return float(np.mean([1.0 / r for r in rs]))

def main():
    docs, att, val2ab, elig_ab, elig_a, pick_ab0, pick_a0 = build_frame()
    rng = random.Random(SEED + 2)
    fresh_ab = rng.sample(sorted(set(elig_ab) - set(pick_ab0)), 5)
    fresh_a = rng.sample(sorted(set(elig_a) - set(pick_a0)), 5)
    res = {"addendum": "EPOCH-008/ADDENDUM-1",
           "prereg_addendum_sha256": "197a64249b944624e38a9624781acd0a12158d3b85fab338219133799862334e",
           "pipeline_script_sha256": "20c397b03607f39efe49cc5e6d54813dbd7633926cb9c99fc6d6b4699b3746a7",
           "fresh_ab": fresh_ab, "fresh_a_only": fresh_a}
    print("fresh AB:", fresh_ab, " fresh A-only:", fresh_a)
    assert not (set(fresh_ab) & set(pick_ab0)) and not (set(fresh_a) & set(pick_a0))

    plan = []
    for v in fresh_ab + fresh_a:
        name = f"AB{val2ab[v]:02d}" if v in val2ab else f"A{v[1:4]}"
        cands = sorted(att[name], reverse=True)
        chosen, used = [], set()
        for area, di, gi, b in cands:
            if len(chosen) >= 2: break
            if di in used and len(cands) > len(chosen) + 1: continue
            chosen.append((area, di, gi, b)); used.add(di)
        for r, (area, di, gi, b) in enumerate(chosen):
            plan.append((v, name, di, gi, b, r))
    need = sorted({p[2] for p in plan})
    print("docs needed:", len(need))
    fetched, mode_of, img_of = {}, {}, {}
    for di in need:
        desig = docs[di]["designation"]
        path, status = fetch_doc_png(desig)
        fetched[di] = (path, status); print("fetch", desig, status)
        if path:
            img = Image.open(path); img_of[di] = img
            mode_of[di] = pick_bbox_mode(img, docs[di].get("glyphs", []))
    res["fetch_log"] = {docs[di]["designation"]: s for di, (p, s) in fetched.items()}

    extraction = defaultdict(list)
    for v, name, di, gi, b, r in plan:
        rec = {"sign": v, "sigla": name, "doc": docs[di]["designation"], "bbox": b}
        path, status = fetched.get(di, (None, "not_fetched"))
        if not path:
            rec.update(ok_v2=False, why="download_failed"); extraction[v].append(rec); continue
        mode, dens, gdens = mode_of[di]
        if max(dens.values()) <= gdens:
            rec.update(ok_v2=False, why="bbox_density_check_failed"); extraction[v].append(rec); continue
        img = img_of[di]
        x, y, a, bb = b
        x2, y2 = (x + a, y + bb) if mode == "xywh" else (a, bb)
        Wd, H = img.size
        xa, ya = max(0, min(x, Wd - 2)), max(0, min(y, H - 2))
        xb, yb = max(xa + 2, min(x2, Wd)), max(ya + 2, min(y2, H))
        if xb - xa < 3 or yb - ya < 3:
            rec.update(ok_v2=False, why="degenerate_bbox"); extraction[v].append(rec); continue
        crop = img.crop((xa, ya, xb, yb))
        cname = f"{DATA}/crops/HELD_{name}_{docs[di]['designation'].replace(' ','_')}_{gi}.png"
        crop.save(cname)
        f = skeleton_graph(despeckle(binarize(crop)))
        if f is None:
            rec.update(ok_v2=False, why="empty_skeleton")
        else:
            ok = (0.01 <= f["ink_fraction"] <= 0.6) and f["n_components"] <= 3
            conf = "HIGH" if (ok and f["n_components"] == 1) else ("MEDIUM" if ok else "LOW")
            rec.update(ok_v2=bool(ok), conf=conf, feat=f, crop=os.path.basename(cname))
        extraction[v].append(rec)

    summ = {v: any(r.get("ok_v2") for r in extraction[v]) for v in fresh_ab + fresh_a}
    n_ok = sum(summ.values())
    res["extraction"] = {"per_instance": dict(extraction), "summary": summ, "n_ok_v2": n_ok}
    print("held-out extraction ok:", n_ok, "/10")

    lb_dir = f"{BRONZE}/sign_images/linB"
    gallery = {}
    for fn in sorted(os.listdir(lb_dir)):
        if fn.endswith(".png"):
            f = skeleton_graph(binarize(Image.open(f"{lb_dir}/{fn}")))
            if f: gallery[fn[:-4]] = f
    G = sorted(gallery)
    Gmat = np.stack([feat_vec(gallery[g]) for g in G])
    mu, sd = Gmat.mean(0), Gmat.std(0); sd[sd == 0] = 1.0

    def rank_of(qf, truth, feature):
        if feature == "stroke":
            q = (feat_vec(qf) - mu) / sd
            d = np.linalg.norm((Gmat - mu) / sd - q, axis=1)
        else:
            qa = math.log(qf["aspect"])
            d = np.array([abs(math.log(gallery[g]["aspect"]) - qa) for g in G])
        order = np.argsort(d, kind="stable")
        return int(np.where(np.array(G)[order] == truth)[0][0]) + 1

    rs, ra, detail = [], [], []
    for v in fresh_ab:
        erec = next((r for r in extraction[v] if r.get("ok_v2")), None)
        row = {"sign": v}
        if erec:
            row["stroke_rank"] = rank_of(erec["feat"], v, "stroke")
            row["aspect_rank"] = rank_of(erec["feat"], v, "aspect")
            rs.append(row["stroke_rank"]); ra.append(row["aspect_rank"])
        detail.append(row)
    obs = mrr(rs) if rs else None
    rngp = random.Random(SEED + 3)
    p = None
    if obs is not None:
        N = 20000
        cnt = sum(1 for _ in range(N)
                  if mrr([rngp.randint(1, len(G)) for _ in range(len(rs))]) >= obs)
        p = (cnt + 1) / (N + 1)
    calib = {"detail": detail, "stroke_mrr": obs, "aspect_mrr": mrr(ra) if ra else None,
             "perm_p": p, "n_queries": len(rs), "gallery_n": len(G)}
    res["calibration"] = calib
    print("held-out calibration:", calib)

    if n_ok >= 8 and p is not None and p < 0.05 and obs > calib["aspect_mrr"]:
        out = "AMENDMENT_CONFIRMED"
    elif n_ok >= 6:
        out = "AMENDMENT_PARTIAL"
    else:
        out = "AMENDMENT_REFUTED"
    res["outcome"] = out
    print("ADDENDUM-1 OUTCOME:", out)
    json.dump(res, open(f"{EXP}/epochs/EPOCH-008/result_addendum1.json", "w"),
              indent=1, default=str)

if __name__ == "__main__":
    main()
