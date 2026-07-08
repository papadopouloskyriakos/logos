#!/usr/bin/env python3
"""EPOCH-008: GORILA-plate stroke recovery pilot.

Executes the frozen prereg (epochs/EPOCH-008/prereg.md,
sha256 67ea9ac471221ec91ebe1067d3696af725b14951d443637c4c9574fa6181e6a2).
Deterministic; seed 20260708. All downloads polite, gitignored.
"""
import json, math, os, random, sys, time, unicodedata, urllib.request, urllib.parse
from collections import Counter, defaultdict

import numpy as np
from PIL import Image
from skimage.filters import threshold_otsu
from skimage.morphology import skeletonize

SEED = 20260708
W = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
EXP = f"{W}/experiments/linear_a_frontier_72h"
DATA = f"{EXP}/data/stroke_pilot"
BRONZE = f"{W}/corpus/bronze"
PREREG_HASH = "67ea9ac471221ec91ebe1067d3696af725b14951d443637c4c9574fa6181e6a2"
PLAN = json.load if False else None

# ---------------------------------------------------------------- stroke graph
def binarize(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img)
    if arr.ndim == 3 and arr.shape[-1] == 4 and arr[..., 3].min() < 255:
        # transparent-background trace render (SigLA): ink intensity = alpha
        g = 255.0 - arr[..., 3].astype(float)
    else:
        g = np.asarray(img.convert("L"), dtype=float)
    if g.max() == g.min():
        return np.zeros_like(g, dtype=bool)
    t = threshold_otsu(g)
    dark = g < t
    # ink = minority side if border is majority-colored; auto-invert via border vote
    border = np.concatenate([dark[0, :], dark[-1, :], dark[:, 0], dark[:, -1]])
    ink = dark if border.mean() < 0.5 else ~dark
    return ink

NB8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def skeleton_graph(ink: np.ndarray) -> dict:
    """Extract stroke-graph features from a binary ink mask."""
    if ink.sum() == 0:
        return None
    sk = skeletonize(ink)
    ys, xs = np.nonzero(sk)
    if len(ys) == 0:
        return None
    pix = set(zip(ys.tolist(), xs.tolist()))
    deg = {}
    for (y, x) in pix:
        deg[(y, x)] = sum((y+dy, x+dx) in pix for dy, dx in NB8)
    endpoints = [p for p, d in deg.items() if d == 1]
    junc_pix = [p for p, d in deg.items() if d >= 3]
    # merge adjacent junction pixels into clusters
    junc_set = set(junc_pix); clusters = []; seen = set()
    for p in junc_pix:
        if p in seen: continue
        stack = [p]; comp = []
        while stack:
            q = stack.pop()
            if q in seen: continue
            seen.add(q); comp.append(q)
            for dy, dx in NB8:
                r = (q[0]+dy, q[1]+dx)
                if r in junc_set and r not in seen: stack.append(r)
        clusters.append(comp)
    n_junc = len(clusters)
    # connected components of the whole skeleton
    seen2 = set(); n_comp = 0
    for p in pix:
        if p in seen2: continue
        n_comp += 1; stack = [p]
        while stack:
            q = stack.pop()
            if q in seen2: continue
            seen2.add(q)
            for dy, dx in NB8:
                r = (q[0]+dy, q[1]+dx)
                if r in pix and r not in seen2: stack.append(r)
    # condensed critical-point graph: trace edges between critical nodes
    crit = set(endpoints)
    cl_of = {}
    for ci, comp in enumerate(clusters):
        for q in comp: crit.add(q); cl_of[q] = ci
    node_id = {}
    for p in crit:
        node_id[p] = ("J", cl_of[p]) if p in cl_of else ("E", p)
    edges = set(); edge_lens = []; orient = np.zeros(4)
    visited_dir = set()
    for p in crit:
        for dy, dx in NB8:
            q0 = (p[0]+dy, p[1]+dx)
            if q0 not in pix: continue
            if (p, q0) in visited_dir: continue
            # walk from p through q0 until next critical point
            path = [p, q0]; visited_dir.add((p, q0))
            prev, cur = p, q0
            while cur not in crit:
                nxts = [ (cur[0]+a, cur[1]+b) for a, b in NB8
                         if (cur[0]+a, cur[1]+b) in pix and (cur[0]+a, cur[1]+b) != prev
                         and (cur[0]+a, cur[1]+b) not in path[-3:-1] ]
                # prefer non-critical continuation deterministically
                if not nxts: break
                nxt = sorted(nxts)[0]
                path.append(nxt); prev, cur = cur, nxt
                if len(path) > len(pix) + 2: break
            if cur in crit:
                visited_dir.add((cur, path[-2]))
                a, b = node_id[p], node_id[cur]
                if a == b and len(path) < 6:
                    continue  # intra-junction-cluster artifact, not a real loop
                edges.add((min(a, b), max(a, b), len(path)))
                edge_lens.append(len(path))
                dyv = path[-1][0] - path[0][0]; dxv = path[-1][1] - path[0][1]
                ang = math.atan2(dyv, dxv) % math.pi
                orient[int(ang / (math.pi / 4)) % 4] += len(path)
    n_edges = len(edges)
    # cycles on condensed graph (fallback: pixel-level Euler)
    nodes = set()
    for a, b, _l in edges: nodes.add(a); nodes.add(b)
    if nodes:
        # count components of condensed graph
        adj = defaultdict(set)
        for a, b, _l in edges: adj[a].add(b); adj[b].add(a)
        seenc = set(); ncc = 0
        for n in nodes:
            if n in seenc: continue
            ncc += 1; st = [n]
            while st:
                u = st.pop()
                if u in seenc: continue
                seenc.add(u); st.extend(adj[u] - seenc)
        n_loops = max(0, n_edges - len(nodes) + ncc)
    else:
        # pure cycle(s) with no critical points (e.g. 'O'): each component is a loop
        n_loops = n_comp if not endpoints and not clusters else 0
        n_edges = n_loops
    skel_len = len(pix)
    h, wd = ink.shape
    ys2, xs2 = np.nonzero(ink)
    bh = ys2.max() - ys2.min() + 1; bw = xs2.max() - xs2.min() + 1
    o = orient / orient.sum() if orient.sum() > 0 else np.zeros(4)
    return {
        "n_endpoints": len(endpoints), "n_junctions": n_junc, "n_loops": int(n_loops),
        "n_components": n_comp, "n_strokes": int(n_edges),
        "skel_len_norm": skel_len / math.sqrt(bh * bw),
        "orient": o.tolist(), "aspect": bh / bw,
        "ink_fraction": float(ink.mean()),
    }

def feat_vec(f):
    return np.array([f["n_endpoints"], f["n_junctions"], f["n_loops"],
                     f["n_components"], f["n_strokes"], f["skel_len_norm"], *f["orient"]],
                    dtype=float)

# ---------------------------------------------------------------- positive control
def synth(kind):
    im = np.zeros((96, 96), dtype=bool)
    if kind == "+": im[48, 16:81] = True; im[16:81, 48] = True; gt = (4, 1, 0)
    elif kind == "O":
        yy, xx = np.mgrid[0:96, 0:96]; r = np.hypot(yy - 48, xx - 48)
        im = (r > 26) & (r < 32); gt = (0, 0, 1)
    elif kind == "T": im[20, 16:81] = True; im[20:81, 48] = True; gt = (3, 1, 0)
    elif kind == "X":
        for i in range(65): im[16+i, 16+i] = True; im[16+i, 80-i] = True
        gt = (4, 1, 0)
    elif kind == "L": im[16:81, 30] = True; im[80, 30:71] = True; gt = (2, 0, 0)
    return im, gt

def run_pc():
    out = []
    for k in ["+", "O", "T", "X", "L"]:
        f = skeleton_graph(synth(k)[0])
        gt = synth(k)[1]
        got = (f["n_endpoints"], f["n_junctions"], f["n_loops"])
        ok = got == gt or (k == "L" and f["n_endpoints"] == 2 and f["n_loops"] == 0
                           and f["n_junctions"] <= 1)
        out.append({"glyph": k, "gt": gt, "got": got, "pass": bool(ok)})
    n = sum(o["pass"] for o in out)
    return {"cases": out, "n_pass": n, "PASS": n >= 4}

# ---------------------------------------------------------------- sample frame
def build_frame():
    cp2val = json.load(open(f"{BRONZE}/palaeo/linA_codepoint_map.json"))["linA_cp2val"]
    val2ab = {}
    for cp, val in cp2val.items():
        try: name = unicodedata.name(chr(int(cp)))
        except ValueError: continue
        if name.startswith("LINEAR A SIGN AB"):
            num = name.split("AB")[1]
            if num.isdigit(): val2ab[val] = int(num)
    la_dir = f"{BRONZE}/sign_images/linA"; lb_dir = f"{BRONZE}/sign_images/linB"
    la = {f[:-4] for f in os.listdir(la_dir) if f.endswith(".png")}
    lb = {f[:-4] for f in os.listdir(lb_dir) if f.endswith(".png")}
    docs = json.load(open(f"{BRONZE}/sigla_browse_2026/sigla_documents.json"))
    att = defaultdict(list)  # sigla sign name -> [(area, doc_idx, glyph_idx, bbox)]
    for di, d in enumerate(docs):
        for gi, g in enumerate(d.get("glyphs", [])):
            s, b = g.get("sign"), g.get("bbox")
            if not s or not b or len(b) != 4: continue
            wv, hv = b[2], b[3]
            if wv >= 12 and hv >= 12:
                att[s].append((wv * hv, di, gi, b))
    shared = json.load(open(f"{BRONZE}/sign_images/manifest.json"))["shared_values_all"]
    elig_ab = sorted(v for v in shared if v in la and v in lb and v in val2ab
                     and att.get(f"AB{val2ab[v]:02d}"))
    elig_a = sorted(v for v in la if v.startswith("*") and v[1:4].isdigit()
                    and att.get(f"A{v[1:4]}") and v[1:4].startswith("3"))
    rng = random.Random(SEED)
    pick_ab = rng.sample(elig_ab, 5); pick_a = rng.sample(elig_a, 5)
    return docs, att, val2ab, elig_ab, elig_a, pick_ab, pick_a

# ---------------------------------------------------------------- SigLA acquisition
def fetch_doc_png(desig):
    safe = urllib.parse.quote(desig)
    url = f"https://sigla.phis.me/document/{safe}/{safe}.png"
    dest = f"{DATA}/sigla_raw/{desig.replace(' ', '_')}.png"
    if os.path.exists(dest): return dest, "cached"
    req = urllib.request.Request(url, headers={"User-Agent": "logos-epoch008-stroke-pilot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            blob = r.read()
        open(dest, "wb").write(blob)
        time.sleep(1.6)
        return dest, "fetched"
    except Exception as e:
        time.sleep(1.6)
        return None, f"ERROR:{e}"

def pick_bbox_mode(img, glyphs):
    """Bug-fixed rule: geometric validity FIRST (all boxes must have x2>x1, y2>y1
    inside the image under the candidate mode), then mean in-box ink density."""
    ink = binarize(img)
    H, Wd = ink.shape
    dens = {"xywh": [], "xyxy": []}
    valid = {"xywh": True, "xyxy": True}
    for g in glyphs:
        b = g.get("bbox")
        if not b or len(b) != 4: continue
        x, y, a, bb = b
        for mode, (x2, y2) in (("xywh", (x + a, y + bb)), ("xyxy", (a, bb))):
            if not (x2 > x and y2 > y and x2 <= Wd + 8 and y2 <= H + 8):
                valid[mode] = False; continue
            xa, ya = max(0, min(x, Wd - 1)), max(0, min(y, H - 1))
            xb, yb = max(xa + 1, min(x2, Wd)), max(ya + 1, min(y2, H))
            if xb - xa < 3 or yb - ya < 3: continue
            dens[mode].append(ink[ya:yb, xa:xb].mean())
    m = {k: (float(np.mean(v)) if v else 0.0) for k, v in dens.items()}
    cands = [k for k in m if valid[k]] or list(m)
    mode = max(cands, key=lambda k: m[k])
    return mode, m, float(ink.mean())


def despeckle(ink: np.ndarray) -> np.ndarray:
    """AMENDMENT-A (pipeline v2, documented deviation): remove connected components
    smaller than max(4 px, 2% of the largest component); close 1-px gaps."""
    from skimage.measure import label
    from skimage.morphology import binary_closing, footprint_rectangle
    lab = label(ink, connectivity=2)
    if lab.max() == 0:
        return ink
    sizes = np.bincount(lab.ravel()); sizes[0] = 0
    thr = max(4, 0.02 * sizes.max())
    keep = np.isin(lab, np.nonzero(sizes >= thr)[0])
    return binary_closing(keep, footprint_rectangle((3, 3)))

# ---------------------------------------------------------------- main
def main():
    os.makedirs(f"{DATA}/sigla_raw", exist_ok=True)
    os.makedirs(f"{DATA}/crops", exist_ok=True)
    res = {"epoch": "EPOCH-008", "seed": SEED, "prereg_sha256": PREREG_HASH}

    pc = run_pc()
    res["positive_control"] = pc
    print("PC:", pc["n_pass"], "/5 PASS" if pc["PASS"] else "/5 FAIL")
    docs, att, val2ab, elig_ab, elig_a, pick_ab, pick_a = build_frame()
    res["frame"] = {"n_elig_ab": len(elig_ab), "n_elig_a_only": len(elig_a),
                    "pick_ab": pick_ab, "pick_a_only": pick_a}
    print("eligible AB:", len(elig_ab), "A-only:", len(elig_a))
    print("picked AB:", pick_ab, " A-only:", pick_a)
    if not pc["PASS"]:
        res["verdict"] = "STROKE_RECOVERY_INFEASIBLE"
        json.dump(res, open(f"{EXP}/epochs/EPOCH-008/result.json", "w"), indent=1)
        return

    # choose attestations: top-2 by area, prefer distinct docs
    plan = []  # (sign_value, sigla_name, doc_idx, glyph_idx, bbox, rank)
    for v in pick_ab + pick_a:
        name = f"AB{val2ab[v]:02d}" if v in val2ab else f"A{v[1:4]}"
        cands = sorted(att[name], reverse=True)
        chosen, used_docs = [], set()
        for area, di, gi, b in cands:
            if len(chosen) >= 2: break
            if di in used_docs and len(cands) > len(chosen) + 1: continue
            chosen.append((area, di, gi, b)); used_docs.add(di)
        for r, (area, di, gi, b) in enumerate(chosen):
            plan.append((v, name, di, gi, b, r))
    need = sorted({p[2] for p in plan})
    res["acquisition"] = {"n_docs": len(need), "docs": [docs[i]["designation"] for i in need]}
    print("docs needed:", len(need), [docs[i]["designation"] for i in need])

    fetched, mode_of, img_of = {}, {}, {}
    for di in need:
        desig = docs[di]["designation"]
        path, status = fetch_doc_png(desig)
        fetched[di] = (path, status)
        print("fetch", desig, status)
        if path:
            img = Image.open(path)
            img_of[di] = img
            mode, dens, gdens = pick_bbox_mode(img, docs[di].get("glyphs", []))
            mode_of[di] = (mode, dens, gdens)
    res["acquisition"]["fetch_log"] = {docs[di]["designation"]: s for di, (p, s) in fetched.items()}
    res["acquisition"]["bbox_modes"] = {docs[di]["designation"]:
        {"mode": m[0], "density": m[1], "global_ink": m[2]} for di, m in mode_of.items()}

    # extraction over pilot instances
    extraction = defaultdict(list)
    for v, name, di, gi, b, r in plan:
        rec = {"sign": v, "sigla": name, "doc": docs[di]["designation"], "glyph_idx": gi,
               "bbox": b, "instance_rank": r}
        path, status = fetched.get(di, (None, "not_fetched"))
        if not path:
            rec.update(ok=False, why=f"download_failed:{status}")
            extraction[v].append(rec); continue
        mode, dens, gdens = mode_of[di]
        if max(dens.values()) <= gdens:
            rec.update(ok=False, why="bbox_density_check_failed")
            extraction[v].append(rec); continue
        img = img_of[di]
        x, y, a, bb = b
        x2, y2 = (x + a, y + bb) if mode == "xywh" else (a, bb)
        Wd, H = img.size
        xa, ya = max(0, min(x, Wd - 2)), max(0, min(y, H - 2))
        xb, yb = max(xa + 2, min(x2, Wd)), max(ya + 2, min(y2, H))
        if xb - xa < 3 or yb - ya < 3:
            rec.update(ok=False, why="degenerate_bbox_under_chosen_mode")
            extraction[v].append(rec); continue
        crop = img.crop((xa, ya, xb, yb))
        cname = f"{DATA}/crops/{name}_{docs[di]['designation'].replace(' ','_')}_{gi}.png"
        crop.save(cname)
        ink = binarize(crop)
        for tag, mask in (("v1", ink), ("v2", despeckle(ink))):
            f = skeleton_graph(mask)
            if f is None:
                rec.update(**{f"ok_{tag}": False, f"why_{tag}": "empty_skeleton"})
            else:
                ok = (0.01 <= f["ink_fraction"] <= 0.6) and f["n_components"] <= 3
                conf = "HIGH" if (ok and f["n_components"] == 1) else ("MEDIUM" if ok else "LOW")
                rec.update(**{f"ok_{tag}": bool(ok), f"conf_{tag}": conf, f"feat_{tag}": f})
        rec["ok"] = rec.get("ok_v1", False)  # frozen-rule primary
        rec["crop"] = os.path.basename(cname)
        extraction[v].append(rec)

    ext_summary = {}
    for v in pick_ab + pick_a:
        recs = extraction[v]
        ext_summary[v] = {
            "ok_v1": any(r.get("ok_v1") for r in recs),
            "ok_v2": any(r.get("ok_v2") for r in recs),
            "conf_v1": next((r["conf_v1"] for r in recs if r.get("ok_v1")), "NONE"),
            "conf_v2": next((r["conf_v2"] for r in recs if r.get("ok_v2")), "NONE"),
            "n_instances": len(recs)}
    n_ok = sum(1 for v in ext_summary if ext_summary[v]["ok_v1"])
    n_ok2 = sum(1 for v in ext_summary if ext_summary[v]["ok_v2"])
    res["extraction"] = {"per_instance": {v: extraction[v] for v in extraction},
                         "summary": ext_summary, "n_ok_v1_frozen": n_ok,
                         "n_ok_v2_amended": n_ok2, "n_pilot": len(pick_ab + pick_a)}
    print(f"extraction ok: v1(frozen) {n_ok}/10, v2(amended) {n_ok2}/10")

    # ------------------------------------------------------------ calibration
    lb_dir = f"{BRONZE}/sign_images/linB"; la_dir = f"{BRONZE}/sign_images/linA"
    gallery = {}
    for fn in sorted(os.listdir(lb_dir)):
        if not fn.endswith(".png"): continue
        f = skeleton_graph(binarize(Image.open(f"{lb_dir}/{fn}")))
        if f: gallery[fn[:-4]] = f
    G = sorted(gallery)
    Gmat = np.stack([feat_vec(gallery[g]) for g in G])
    mu, sd = Gmat.mean(0), Gmat.std(0); sd[sd == 0] = 1.0

    def rank_of(query_feat, truth, feature="stroke"):
        if feature == "stroke":
            q = (feat_vec(query_feat) - mu) / sd
            d = np.linalg.norm((Gmat - mu) / sd - q, axis=1)
        else:
            qa = math.log(query_feat["aspect"])
            d = np.array([abs(math.log(gallery[g]["aspect"]) - qa) for g in G])
        order = np.argsort(d, kind="stable")
        return int(np.where(np.array(G)[order] == truth)[0][0]) + 1

    def mrr(ranks): return float(np.mean([1.0 / r for r in ranks]))

    calib = {"gallery_n": len(G)}
    ranks = {"epig_stroke_v1": [], "epig_aspect_v1": [], "epig_stroke_v2": [],
             "epig_aspect_v2": [], "font_stroke": [], "font_aspect": []}
    detail = []
    for v in pick_ab:
        row = {"sign": v}
        for tag in ("v1", "v2"):
            erec = next((r for r in extraction[v] if r.get(f"ok_{tag}")), None)
            if erec:
                fs = erec[f"feat_{tag}"]
                row[f"epig_stroke_rank_{tag}"] = rank_of(fs, v, "stroke")
                row[f"epig_aspect_rank_{tag}"] = rank_of(fs, v, "aspect")
                ranks[f"epig_stroke_{tag}"].append(row[f"epig_stroke_rank_{tag}"])
                ranks[f"epig_aspect_{tag}"].append(row[f"epig_aspect_rank_{tag}"])
        ff = skeleton_graph(binarize(Image.open(f"{la_dir}/{v}.png")))
        row["font_stroke_rank"] = rank_of(ff, v, "stroke")
        row["font_aspect_rank"] = rank_of(ff, v, "aspect")
        ranks["font_stroke"].append(row["font_stroke_rank"])
        ranks["font_aspect"].append(row["font_aspect_rank"])
        detail.append(row)
    calib["detail"] = detail
    for k in ranks: calib[f"{k}_mrr"] = mrr(ranks[k]) if ranks[k] else None
    calib["epig_top5_v1"] = sum(1 for r in ranks["epig_stroke_v1"] if r <= 5)
    calib["epig_top5_v2"] = sum(1 for r in ranks["epig_stroke_v2"] if r <= 5)

    rngp = random.Random(SEED + 1)
    def perm_p(obs, n_q):
        if obs is None or n_q == 0: return None
        cnt = 0; N = 20000
        for _ in range(N):
            if mrr([rngp.randint(1, len(G)) for _ in range(n_q)]) >= obs: cnt += 1
        return (cnt + 1) / (N + 1)
    calib["epig_stroke_p_v1"] = perm_p(calib["epig_stroke_v1_mrr"], len(ranks["epig_stroke_v1"]))
    calib["epig_stroke_p_v2"] = perm_p(calib["epig_stroke_v2_mrr"], len(ranks["epig_stroke_v2"]))
    calib["font_stroke_p"] = perm_p(calib["font_stroke_mrr"], len(ranks["font_stroke"]))
    calib["chance_mrr"] = float(np.mean([1.0 / rngp.randint(1, len(G)) for _ in range(200000)]))
    res["calibration"] = calib
    print("calibration:", {k: calib[k] for k in calib if k != "detail"})

    # ------------------------------------------------------------ NC3 degradation
    dmg_dir = f"{BRONZE}/sign_images/damaged"
    dmg = {"per_variant": [], }
    dranks = []
    for v in pick_ab:
        for fn in sorted(os.listdir(dmg_dir)):
            if not fn.startswith(v + "__") or not fn.endswith(".png"): continue
            f = skeleton_graph(binarize(Image.open(f"{dmg_dir}/{fn}")))
            if f is None: continue
            r = rank_of(f, v, "stroke")
            dranks.append(r)
            dmg["per_variant"].append({"file": fn, "rank": r})
    dmg["mrr"] = mrr(dranks) if dranks else None
    dmg["n"] = len(dranks)
    dmg["retention_vs_font"] = (dmg["mrr"] / calib["font_stroke_mrr"]
                                if dmg["mrr"] and calib["font_stroke_mrr"] else None)
    res["degradation_nc3"] = dmg
    print("NC3 degradation:", dmg["n"], "variants, mrr", dmg["mrr"])

    # ------------------------------------------------------------ verdict
    def decide(n_ok_x, p, m_str, m_asp):
        feas = (pc["PASS"] and n_ok_x >= 8 and p is not None and p < 0.05
                and m_str is not None and m_asp is not None and m_str > m_asp)
        if feas: return "STROKE_RECOVERY_FEASIBLE"
        if pc["PASS"] and n_ok_x >= 6: return "STROKE_RECOVERY_PARTIAL"
        return "STROKE_RECOVERY_INFEASIBLE"
    v1 = decide(n_ok, calib["epig_stroke_p_v1"], calib["epig_stroke_v1_mrr"],
                calib["epig_aspect_v1_mrr"])
    v2 = decide(n_ok2, calib["epig_stroke_p_v2"], calib["epig_stroke_v2_mrr"],
                calib["epig_aspect_v2_mrr"])
    res["verdict_v1_frozen"] = v1
    res["verdict_v2_amended"] = v2
    res["verdict"] = v1  # frozen rule is primary; amendment reported, never upgrades
    res["amendment_note"] = ("AMENDMENT-A: despeckle+closing preprocessing was NOT in the "
                             "frozen prereg; v2 is reported for successor planning only. "
                             "Bbox-mode geometric-validity fix and RGBA-alpha ink decoding "
                             "are I/O bug fixes applied to both v1 and v2.")
    res["verdict_route"] = "SigLA-trace raster renders (GORILA-derived); GORILA plates NOT processed"
    print("VERDICT v1(frozen):", v1, "| v2(amended):", v2)
    json.dump(res, open(f"{EXP}/epochs/EPOCH-008/result.json", "w"), indent=1, default=str)

if __name__ == "__main__":
    main()
