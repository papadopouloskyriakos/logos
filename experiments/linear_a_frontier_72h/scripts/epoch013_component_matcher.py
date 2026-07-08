#!/usr/bin/env python3
"""EPOCH-013: component-decomposition matcher (attack the E009 coverage ceiling).

Executes the frozen prereg epochs/EPOCH-013/prereg.md
(sha256 76ea706c1243e2decbd73d07f0ff6cc68b126bfee98c2177f6e57aad304b06e0,
frozen 2026-07-08T05:15:27Z, BEFORE this script ran on any data).
Deterministic; seed 20260708. Reuses E008/E009 frozen primitives by import.

Implementation notes (decided pre-run, consistent with the frozen prereg):
- "dot" semantics: a component whose skeleton has <= 4 pixels carries topology
  (0 endpoints, 0 junctions, 0 loops, 0 strokes) — required by the frozen PC-1(b)
  ground truth for the "÷" dots (the E008 pure-cycle fallback would otherwise
  mis-count an isolated skeleton pixel as a loop).
- PC-1 matcher sanity runs in RAW feature space (pooled z-stats do not exist yet
  when the PC runs); D(g,g)=0 is normalization-independent.
"""
import json, math, os, random, sys, time, unicodedata
from collections import Counter, defaultdict
from multiprocessing import Pool

import numpy as np
from PIL import Image
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
from skimage.measure import label as cc_label

W = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
EXP = f"{W}/experiments/linear_a_frontier_72h"
DATA = f"{EXP}/data/stroke_corpus"
OUT = f"{DATA}/component_matcher"
BRONZE = f"{W}/corpus/bronze"
SEED = 20260708
PREREG_HASH = "76ea706c1243e2decbd73d07f0ff6cc68b126bfee98c2177f6e57aad304b06e0"
FROZEN_UTC = "2026-07-08T05:15:27Z"
MAXK, SHARE_MIN, KEEP_MIN = 12, 0.03, 0.70

sys.path.insert(0, f"{EXP}/scripts")
from epoch008_stroke_pilot import binarize, skeleton_graph, despeckle, synth

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

# --------------------------------------------------------- component decomposition
def comp_features(comp_mask, H, Wd, share):
    """13-dim per-component feature (frozen prereg rule 4)."""
    ys, xs = np.nonzero(comp_mask)
    if len(ys) == 0:
        return None
    n_skel_guard = None
    from skimage.morphology import skeletonize
    sk = skeletonize(comp_mask)
    n_skel = int(sk.sum())
    bh = ys.max() - ys.min() + 1
    bw = xs.max() - xs.min() + 1
    aspect = bh / bw
    if n_skel <= 4:                                  # dot semantics (see docstring)
        f = {"n_endpoints": 0, "n_junctions": 0, "n_loops": 0, "n_strokes": 0,
             "skel_len_norm": n_skel / math.sqrt(bh * bw),
             "orient": [0.0, 0.0, 0.0, 0.0], "aspect": aspect}
    else:
        f = skeleton_graph(comp_mask)
        if f is None:
            return None
    if not (f["aspect"] > 0):
        return None
    cy, cx = float(ys.mean()) / H, float(xs.mean()) / Wd
    v = np.array([f["n_endpoints"], f["n_junctions"], f["n_loops"], f["n_strokes"],
                  f["skel_len_norm"], *f["orient"], cx, cy, share,
                  math.log(f["aspect"])], dtype=float)
    if not np.all(np.isfinite(v)):
        return None
    return v, (f["n_endpoints"], f["n_junctions"], f["n_loops"])

def decompose(ink):
    """Frozen prereg rule 1-4. Returns dict with ok/why/comps/log_aspect/n_kept."""
    total = int(ink.sum())
    H, Wd = ink.shape
    out = {"ok": False, "n_kept": 0}
    if total == 0:
        out["why"] = "empty_ink"; return out
    frac = ink.mean()
    out["ink_fraction"] = float(frac)
    if not (0.01 <= frac <= 0.6):
        out["why"] = "ink_fraction_out_of_range"; return out
    lab = cc_label(ink, connectivity=2)
    sizes = np.bincount(lab.ravel()); sizes[0] = 0
    order = np.argsort(sizes)[::-1]
    qual = [int(i) for i in order if sizes[i] >= SHARE_MIN * total and sizes[i] > 0]
    out["n_qualifying"] = len(qual)
    kept = qual[:MAXK]
    kept_px = int(sizes[kept].sum()) if kept else 0
    out["kept_share"] = kept_px / total if total else 0.0
    if not kept:
        out["why"] = "kept_share_lt_070"; return out
    if out["kept_share"] < KEEP_MIN:
        out["why"] = ("fragmented_beyond_cap" if len(qual) > MAXK
                      else "kept_share_lt_070")
        return out
    comps, topo = [], []
    for i in kept:
        r = comp_features(lab == i, H, Wd, sizes[i] / kept_px)
        if r is None:
            out["why"] = "empty_component_skeleton"; return out
        comps.append(r[0]); topo.append(r[1])
    ys, xs = np.nonzero(ink)
    bh = ys.max() - ys.min() + 1; bw = xs.max() - xs.min() + 1
    out.update(ok=True, n_kept=len(comps), comps=np.stack(comps),
               topo=topo, log_aspect=math.log(bh / bw))
    return out

def bag_dist(Za, Zb, lam):
    m, n = len(Za), len(Zb)
    s = max(m, n)
    if s == 0:
        return lam
    C = np.full((s, s), lam)
    C[:m, :n] = cdist(Za, Zb)
    ri, ci = linear_sum_assignment(C)
    return float(C[ri, ci].sum() / s)

# --------------------------------------------------------------- positive control
def synth_multi(kind):
    im = np.zeros((96, 96), dtype=bool)
    yy, xx = np.mgrid[0:96, 0:96]
    if kind == "=":
        im[30, 16:81] = True; im[60, 16:81] = True
        gt = sorted([(2, 0, 0), (2, 0, 0)])
    elif kind == "÷":
        im[48, 16:81] = True
        im |= (np.hypot(yy - 24, xx - 48) <= 5)
        im |= (np.hypot(yy - 72, xx - 48) <= 5)
        gt = sorted([(2, 0, 0), (0, 0, 0), (0, 0, 0)])
    elif kind == "%":
        r1 = np.hypot(yy - 24, xx - 24); r2 = np.hypot(yy - 72, xx - 72)
        im |= (r1 > 6) & (r1 < 11); im |= (r2 > 6) & (r2 < 11)
        for i in range(65):
            im[80 - i, 16 + i] = True
        gt = sorted([(0, 0, 1), (0, 0, 1), (2, 0, 0)])
    return im, gt

def run_pc1():
    out = {"a_single": [], "b_multi": [], "c_matcher": {}}
    # (a) E008 singles through the decomposition path
    for k in ["+", "O", "T", "X", "L"]:
        im, gt = synth(k)
        d = decompose(despeckle(im))
        got = d["topo"][0] if d.get("ok") and d["n_kept"] == 1 else None
        ok = (d.get("ok") and d["n_kept"] == 1 and
              (got == gt or (k == "L" and got and got[0] == 2 and got[2] == 0
                             and got[1] <= 1)))
        out["a_single"].append({"glyph": k, "gt": gt, "got": got,
                                "n_kept": d.get("n_kept"), "pass": bool(ok)})
    a_pass = sum(o["pass"] for o in out["a_single"]) >= 4
    # (b) multi-component decomposition ground truth
    bags = {}
    for k in ["=", "÷", "%"]:
        im, gt = synth_multi(k)
        d = decompose(despeckle(im))
        got = sorted(d["topo"]) if d.get("ok") else None
        bags[k] = d
        out["b_multi"].append({"glyph": k, "gt": gt, "got": got,
                               "n_kept": d.get("n_kept"),
                               "pass": bool(d.get("ok") and got == gt)})
    b_pass = all(o["pass"] for o in out["b_multi"])
    # (c) matcher sanity in raw space
    c = out["c_matcher"]
    if b_pass:
        pool = np.vstack([bags[k]["comps"] for k in bags])
        rng = random.Random(SEED)
        pairs = [np.linalg.norm(pool[rng.randrange(len(pool))]
                                - pool[rng.randrange(len(pool))]) for _ in range(2000)]
        lam = float(np.median([p for p in pairs if p > 0]))
        c["lambda_pc"] = lam
        c["d_self"] = {k: bag_dist(bags[k]["comps"], bags[k]["comps"], lam)
                       for k in bags}
        c["d_eq_eq"] = c["d_self"]["="]
        c["d_eq_pct"] = bag_dist(bags["="]["comps"], bags["%"]["comps"], lam)
        c["pass"] = bool(all(v < 1e-9 for v in c["d_self"].values())
                         and c["d_eq_pct"] > 1e-9)
    else:
        c["pass"] = False
    out["PASS"] = bool(a_pass and b_pass and c["pass"])
    return out

# ------------------------------------------------------------------- extraction
G_DOCS = None
def _proc_doc(args):
    desig, mode, recs = args
    path = dest_of(desig)
    res = []
    try:
        img = Image.open(path); img.load()
    except Exception as e:
        return [(idx, {"ok": False, "why": f"image_unreadable:{type(e).__name__}"})
                for idx, gi, b in recs]
    Wd, H = img.size
    for idx, gi, b in recs:
        x, y, a, bb = b
        x2, y2 = (x + a, y + bb) if mode == "xywh" else (a, bb)
        xa, ya = max(0, min(x, Wd - 2)), max(0, min(y, H - 2))
        xb, yb = max(xa + 2, min(x2, Wd)), max(ya + 2, min(y2, H))
        if xb - xa < 3 or yb - ya < 3:
            res.append((idx, {"ok": False, "why": "degenerate_bbox"})); continue
        crop = img.crop((xa, ya, xb, yb))
        if max(crop.size) > 512:
            s = 512.0 / max(crop.size)
            crop = crop.resize((max(1, int(crop.size[0] * s)),
                                max(1, int(crop.size[1] * s))), Image.LANCZOS)
        ink = despeckle(binarize(crop))
        d = decompose(ink)
        if d.get("ok"):
            d["comps"] = d["comps"].tolist()
        d.pop("topo", None)
        res.append((idx, d))
    img.close()
    return res

def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(SEED + 9)
    res = {"epoch": "EPOCH-013", "seed": SEED, "prereg_sha256": PREREG_HASH,
           "prereg_frozen_utc": FROZEN_UTC}

    pc = run_pc1()
    res["positive_control_pc1"] = pc
    print("PC-1:", "PASS" if pc["PASS"] else "FAIL",
          {k: [o["pass"] for o in pc[k]] for k in ("a_single", "b_multi")}, flush=True)
    if not pc["PASS"]:
        res["verdict"] = "DECOMPOSITION_DEGRADES"
        res["verdict_reason"] = "PC_FAIL"
        json.dump(res, open(f"{EXP}/epochs/EPOCH-013/result.json", "w"), indent=1,
                  default=str)
        return

    # ---------------- load E009 artifacts (published inputs, Art. XI graph) ------
    store = json.load(open(f"{DATA}/features/instances.json"))
    inst9, doc_meta = store["instances"], store["doc_meta"]
    docs = json.load(open(f"{BRONZE}/sigla_browse_2026/sigla_documents.json"))
    doc_by = {d["designation"]: d for d in docs}
    todo = defaultdict(list)   # desig -> [(idx, gi, bbox)]
    for idx, r in enumerate(inst9):
        if r.get("ok") or r.get("why") == "too_many_components":
            desig = r["doc"]
            if desig not in doc_meta:
                continue
            b = doc_by[desig]["glyphs"][r["gi"]]["bbox"]
            todo[desig].append((idx, r["gi"], b))
    jobs = [(desig, doc_meta[desig]["mode"], recs) for desig, recs in sorted(todo.items())]
    print(f"extraction: {sum(len(j[2]) for j in jobs)} instances over {len(jobs)} docs",
          flush=True)
    dec = {}
    with Pool(16) as pool:
        for i, chunk in enumerate(pool.imap_unordered(_proc_doc, jobs, chunksize=8)):
            for idx, d in chunk:
                dec[idx] = d
            if i % 100 == 0:
                print(f"[decomp {i}/{len(jobs)}] {time.time()-t0:.0f}s", flush=True)

    # status per instance
    usable = {}    # idx -> dict(bag, label, doc, gi, log_aspect, n_kept, status)
    attrition, recovered = [], []
    fail_why = Counter()
    for idx, d in dec.items():
        r = inst9[idx]
        st = "ok" if r.get("ok") else "tm"
        if d.get("ok"):
            usable[idx] = {"label": r["label"], "doc": r["doc"], "gi": r["gi"],
                           "bag": np.array(d["comps"]), "n_kept": d["n_kept"],
                           "log_aspect": d["log_aspect"],
                           "status": "ok" if st == "ok" else "recovered"}
            if st == "tm":
                recovered.append(idx)
        else:
            fail_why[d.get("why")] += 1
            if st == "ok":
                attrition.append(idx)
    n_tm = sum(1 for r in inst9 if r.get("why") == "too_many_components")
    n_ok9 = sum(1 for r in inst9 if r.get("ok"))
    res["extraction"] = {
        "n_processed": len(dec), "n_e009_ok": n_ok9, "n_e009_tm": n_tm,
        "n_usable": len(usable),
        "n_recovered": len(recovered), "recovery_rate": len(recovered) / n_tm,
        "n_ok_attrition": len(attrition), "ok_attrition_rate": len(attrition) / n_ok9,
        "fail_reasons_new": dict(fail_why),
    }
    print("extraction:", res["extraction"], flush=True)

    # pooled z + lambda (frozen rule 5-6)
    allc = np.vstack([u["bag"] for u in usable.values()])
    pmu, psd = allc.mean(0), allc.std(0); psd[psd == 0] = 1.0
    for u in usable.values():
        u["z"] = (u["bag"] - pmu) / psd
    keys = sorted(usable)
    rngl = random.Random(SEED)
    costs = []
    for _ in range(20000):
        i, j = rngl.choice(keys), rngl.choice(keys)
        if i == j:
            continue
        za = usable[i]["z"]; zb = usable[j]["z"]
        costs.append(float(np.linalg.norm(
            za[rngl.randrange(len(za))] - zb[rngl.randrange(len(zb))])))
    LAM = float(np.median(costs))
    res["matcher"] = {"lambda": LAM, "n_lambda_pairs": len(costs),
                      "pooled_dims": 13, "component_cap": MAXK}
    print(f"lambda={LAM:.4f}", flush=True)

    # gallery (LB font renders, identical decomposition, lenient keep)
    lb_dir = f"{BRONZE}/sign_images/linB"
    gal = {}
    for fn in sorted(os.listdir(lb_dir)):
        if not fn.endswith(".png"):
            continue
        ink = despeckle(binarize(Image.open(f"{lb_dir}/{fn}")))
        d = decompose(ink)
        if not d.get("ok"):     # lenient: keep qualifying comps anyway
            lab_ = cc_label(ink, connectivity=2)
            sizes = np.bincount(lab_.ravel()); sizes[0] = 0
            order = np.argsort(sizes)[::-1]
            total = int(ink.sum())
            kept = [int(i) for i in order
                    if sizes[i] >= SHARE_MIN * total and sizes[i] > 0][:MAXK]
            kept_px = int(sizes[kept].sum())
            comps = []
            for i in kept:
                r2 = comp_features(lab_ == i, *ink.shape, sizes[i] / kept_px)
                if r2 is not None:
                    comps.append(r2[0])
            if not comps:
                continue
            ys, xs = np.nonzero(ink)
            d = {"ok": True, "comps": np.stack(comps), "n_kept": len(comps),
                 "log_aspect": math.log((ys.max() - ys.min() + 1)
                                        / (xs.max() - xs.min() + 1)),
                 "lenient": True}
        else:
            d["comps"] = np.asarray(d["comps"])
        gal[fn[:-4]] = d
    G = sorted(gal)
    for g in G:
        gal[g]["z"] = (gal[g]["comps"] - pmu) / psd
    res["gallery"] = {"n": len(G),
                      "n_lenient": sum(1 for g in G if gal[g].get("lenient"))}

    # ------------------------------------------------------------- LEG-1 / PC-2
    cp2val = json.load(open(f"{BRONZE}/palaeo/linA_codepoint_map.json"))["linA_cp2val"]
    val2ab = {}
    for cp, val in cp2val.items():
        try:
            name = unicodedata.name(chr(int(cp)))
        except ValueError:
            continue
        if name.startswith("LINEAR A SIGN AB"):
            num = name.split("AB")[1]
            if num.isdigit():
                val2ab[val] = int(num)
    la_dir = f"{BRONZE}/sign_images/linA"
    la = {f[:-4] for f in os.listdir(la_dir) if f.endswith(".png")}
    lb = {f[:-4] for f in os.listdir(lb_dir) if f.endswith(".png")}
    shared = json.load(open(f"{BRONZE}/sign_images/manifest.json"))["shared_values_all"]

    by_label = defaultdict(list)          # usable instances by label
    for idx in keys:
        by_label[usable[idx]["label"]].append(idx)

    def leg1(query_pool_name, allow_status):
        q_by_lab = {lab: [i for i in ids if usable[i]["status"] in allow_status]
                    for lab, ids in by_label.items()}
        elig = sorted(v for v in shared if v in la and v in lb and v in val2ab
                      and q_by_lab.get(f"AB{val2ab[v]:02d}"))
        Garr = np.array(G)
        agg_r, asp_r, cnt_r, per_r, detail = [], [], [], [], []
        Gasp = np.array([gal[g]["log_aspect"] for g in G])
        Gcnt = np.array([gal[g]["n_kept"] for g in G], dtype=float)
        for v in elig:
            ids = q_by_lab[f"AB{val2ab[v]:02d}"]
            Dm = np.zeros((len(ids), len(G)))
            for qi, i in enumerate(ids):
                for gi_, g in enumerate(G):
                    Dm[qi, gi_] = bag_dist(usable[i]["z"], gal[g]["z"], LAM)
                r_ = int(np.where(Garr[np.argsort(Dm[qi], kind="stable")] == v)[0][0]) + 1
                per_r.append(r_)
            dm = Dm.mean(0)
            rs = int(np.where(Garr[np.argsort(dm, kind="stable")] == v)[0][0]) + 1
            la_m = float(np.mean([usable[i]["log_aspect"] for i in ids]))
            ra = int(np.where(Garr[np.argsort(np.abs(Gasp - la_m),
                                              kind="stable")] == v)[0][0]) + 1
            cm = np.mean(np.abs(np.array([[usable[i]["n_kept"]] for i in ids]) - Gcnt),
                         axis=0)
            rc = int(np.where(Garr[np.argsort(cm, kind="stable")] == v)[0][0]) + 1
            agg_r.append(rs); asp_r.append(ra); cnt_r.append(rc)
            detail.append({"value": v, "n_inst": len(ids), "agg_rank": rs,
                           "aspect_rank": ra, "count_rank": rc})
        L = {"pool": query_pool_name, "realized_n": len(elig), "gallery_n": len(G),
             "agg_mrr": mrr(agg_r),
             "agg_top1": sum(1 for r in agg_r if r == 1),
             "agg_top5": sum(1 for r in agg_r if r <= 5),
             "aspect_mrr": mrr(asp_r), "count_mrr": mrr(cnt_r),
             "per_instance_mrr": mrr(per_r), "per_instance_n": len(per_r),
             "detail": detail}
        L["p_agg"] = perm_p(rng, L["agg_mrr"], len(agg_r), len(G))
        return L

    leg1_ok = leg1("e009_ok_only", {"ok"})
    leg1_ok["chance_mrr"] = float(np.mean([1.0 / rng.randint(1, len(G))
                                           for _ in range(200000)]))
    res["leg1_nondegrade"] = {k: v for k, v in leg1_ok.items() if k != "detail"}
    print("LEG1(ok-only):", res["leg1_nondegrade"], flush=True)
    leg1_exp = leg1("expanded_ok_plus_recovered", {"ok", "recovered"})
    res["leg1_expanded_descriptive"] = {k: v for k, v in leg1_exp.items()
                                        if k != "detail"}
    print("LEG1(expanded):", res["leg1_expanded_descriptive"], flush=True)

    NONDEG = (leg1_ok["realized_n"] >= 30 and leg1_ok["p_agg"] is not None
              and leg1_ok["p_agg"] < 0.01 and leg1_ok["agg_mrr"] >= 0.145
              and leg1_ok["agg_mrr"] > leg1_ok["aspect_mrr"]
              and leg1_ok["agg_mrr"] > leg1_ok["count_mrr"])

    # --------------------------------------------------------------- LEG-R
    dark69 = [f"A{300+n}" for n in range(1, 72) if n not in (2, 48)]
    dk_us = [l for l in dark69 if by_label.get(l)]
    dk_rb = [l for l in dark69 if len(by_label.get(l, [])) >= 3]
    rec_by_lab = Counter(usable[i]["label"] for i in recovered)
    legR = {"n_recovered": len(recovered), "of_tm": n_tm,
            "recovery_rate": len(recovered) / n_tm,
            "dark_usable": len(dk_us), "dark_robust": len(dk_rb),
            "dark_usable_prev": 65, "dark_robust_prev": 21,
            "dark_robust_ceiling": 25, "dark_usable_ceiling": 69,
            "dark_missing": sorted(set(dark69) - set(dk_us)),
            "leg2_frame_size": sum(1 for l in by_label if len(by_label[l]) >= 4),
            "leg2_frame_prev": 116,
            "recovered_labels_top": rec_by_lab.most_common(15)}
    res["legR_recovery"] = legR
    print("LEG-R:", {k: legR[k] for k in legR if k != "recovered_labels_top"},
          flush=True)
    REC_GOOD = (legR["recovery_rate"] >= 0.30 and legR["dark_usable"] >= 67
                and legR["dark_robust"] >= 23)

    # --------------------------------------------------------------- LEG-2'
    def leg2(pool_name, allow_status, restrict_labels=None):
        labs = sorted(l for l, ids in by_label.items()
                      if len([i for i in ids
                              if usable[i]["status"] in allow_status]) >= 4
                      and (restrict_labels is None or l in restrict_labels))
        rng2 = random.Random(SEED + 13)
        half = {}
        for l in labs:
            ids = sorted([i for i in by_label[l]
                          if usable[i]["status"] in allow_status],
                         key=lambda i: (usable[i]["doc"], usable[i]["gi"]))
            A = [i for k_, i in enumerate(ids) if k_ % 2 == 0]
            B = [i for k_, i in enumerate(ids) if k_ % 2 == 1]
            if len(A) > 6: A = sorted(rng2.sample(A, 6))
            if len(B) > 6: B = sorted(rng2.sample(B, 6))
            half[l] = (A, B)
        n = len(labs)
        L = {"pool": pool_name, "n_signs": n}
        if n < 2:
            return L
        DH = np.zeros((n, n))
        for i, li in enumerate(labs):
            for j, lj in enumerate(labs):
                A, B = half[li][0], half[lj][1]
                DH[i, j] = float(np.mean([bag_dist(usable[a]["z"], usable[b]["z"], LAM)
                                          for a in A for b in B]))
        aspA = np.array([np.mean([usable[i]["log_aspect"] for i in half[l][0]])
                         for l in labs])
        aspB = np.array([np.mean([usable[i]["log_aspect"] for i in half[l][1]])
                         for l in labs])
        cntA = np.array([np.mean([usable[i]["n_kept"] for i in half[l][0]])
                         for l in labs])
        cntB = np.array([np.mean([usable[i]["n_kept"] for i in half[l][1]])
                         for l in labs])
        s_r, a_r, c_r = [], [], []
        for i in range(n):
            s_r.append(int(np.where(np.argsort(DH[i], kind="stable") == i)[0][0]) + 1)
            a_r.append(int(np.where(np.argsort(np.abs(aspB - aspA[i]),
                                               kind="stable") == i)[0][0]) + 1)
            c_r.append(int(np.where(np.argsort(np.abs(cntB - cntA[i]),
                                               kind="stable") == i)[0][0]) + 1)
        L.update(self_mrr=mrr(s_r), self_top1=sum(1 for r in s_r if r == 1),
                 self_top5=sum(1 for r in s_r if r <= 5),
                 aspect_self_mrr=mrr(a_r), count_self_mrr=mrr(c_r),
                 p_self=perm_p(rng, mrr(s_r), n, n),
                 chance_mrr=float(np.mean([1.0 / rng.randint(1, n)
                                           for _ in range(200000)])))
        return L

    leg2_exp = leg2("expanded", {"ok", "recovered"})
    res["leg2_expanded"] = leg2_exp
    print("LEG2'(expanded):", leg2_exp, flush=True)
    leg2_okonly = leg2("e009_ok_only", {"ok"})
    res["leg2_ok_only_descriptive"] = leg2_okonly
    print("LEG2'(ok-only):", leg2_okonly, flush=True)
    # E009 116-label frame variant (labels with >=4 E009-ok instances)
    ok9_by = Counter(r["label"] for r in inst9 if r.get("ok"))
    frame116 = {l for l, c in ok9_by.items() if c >= 4}
    leg2_f116 = leg2("e009_frame116_ok_only", {"ok"}, restrict_labels=frame116)
    res["leg2_frame116_descriptive"] = leg2_f116
    print("LEG2'(frame116):", leg2_f116, flush=True)

    HOLD = (leg2_exp.get("n_signs", 0) >= 15 and leg2_exp.get("p_self") is not None
            and leg2_exp["p_self"] < 0.01 and leg2_exp["self_mrr"] >= 0.359
            and leg2_exp["self_mrr"] > leg2_exp["aspect_self_mrr"])

    # ------------------------------------------------------------- matrix output
    rng3 = random.Random(SEED + 14)
    reps = {}
    for l in sorted(by_label):
        ids = sorted(by_label[l], key=lambda i: (usable[i]["doc"], usable[i]["gi"]))
        reps[l] = sorted(rng3.sample(ids, 4)) if len(ids) > 4 else ids
    names = sorted(by_label) + [f"LBfont:{g}" for g in G]
    bags_of = {}
    for l in sorted(by_label):
        bags_of[l] = [usable[i]["z"] for i in reps[l]]
    for g in G:
        bags_of[f"LBfont:{g}"] = [gal[g]["z"]]
    N = len(names)
    M = np.zeros((N, N))
    for i in range(N):
        bi = bags_of[names[i]]
        for j in range(i + 1, N):
            bj = bags_of[names[j]]
            M[i, j] = M[j, i] = float(np.mean(
                [bag_dist(a, b, LAM) for a in bi for b in bj]))
        if i % 50 == 0:
            print(f"[matrix {i}/{N}] {time.time()-t0:.0f}s", flush=True)
    np.savez_compressed(f"{OUT}/component_similarity_matrix.npz",
                        names=np.array(names), distance=M)
    json.dump({"prereg_sha256": PREREG_HASH, "claim_layer": "L1",
               "caveat": ("Hungarian bag-of-components distances over hand-traced "
                          "SigLA renders; trace author knew sign identities "
                          "(standardization confound); NO phonetic values; supports "
                          "no reading."),
               "lambda": LAM, "names": names,
               "n_instances_per_name": {l: len(by_label[l]) for l in sorted(by_label)},
               "distance": [[round(float(x), 4) for x in row] for row in M]},
              open(f"{OUT}/component_similarity_matrix.json", "w"))
    res["matrix"] = {"n_names": N, "n_epigraphic": len(by_label),
                     "n_lb_font_block": len(G)}

    # per-instance component store + recovery manifest
    json.dump({"prereg_sha256": PREREG_HASH,
               "feature_dims": ["n_endpoints", "n_junctions", "n_loops", "n_strokes",
                                "skel_len_norm", "o0", "o1", "o2", "o3",
                                "rel_cx", "rel_cy", "ink_share", "log_aspect"],
               "instances": [{"doc": u["doc"], "gi": u["gi"], "label": u["label"],
                              "status": u["status"], "n_kept": u["n_kept"],
                              "log_aspect": u["log_aspect"],
                              "comps": u["bag"].tolist()}
                             for u in (usable[i] for i in keys)]},
              open(f"{OUT}/components.json", "w"))
    json.dump({"prereg_sha256": PREREG_HASH,
               "recovered": [{"doc": inst9[i]["doc"], "gi": inst9[i]["gi"],
                              "label": inst9[i]["label"],
                              "e009_n_components": inst9[i].get("n_components"),
                              "n_kept": usable[i]["n_kept"]} for i in recovered],
               "ok_attrition": [{"doc": inst9[i]["doc"], "gi": inst9[i]["gi"],
                                 "label": inst9[i]["label"],
                                 "why": dec[i].get("why")} for i in attrition],
               "still_failed_tm": sum(1 for i in dec
                                      if inst9[i].get("why") == "too_many_components"
                                      and not dec[i].get("ok"))},
              open(f"{OUT}/recovery_manifest.json", "w"))

    # ------------------------------------------------------------------ verdict
    ps = [p for p in (leg1_ok.get("p_agg"), leg2_exp.get("p_self")) if p is not None]
    holm = sorted(ps)
    res["multiplicity"] = {"raw_p": ps,
                           "holm": [min(1.0, p * (len(holm) - i))
                                    for i, p in enumerate(holm)]}
    res["gates"] = {"PC1_PASS": pc["PASS"], "NONDEGRADE": bool(NONDEG),
                    "RECOVERY_GOOD": bool(REC_GOOD), "HOLD": bool(HOLD)}
    if not NONDEG:
        verdict = "DECOMPOSITION_DEGRADES"
    elif REC_GOOD and HOLD:
        verdict = "DECOMPOSITION_RECOVERS"
    else:
        verdict = "DECOMPOSITION_NEUTRAL"
    res["verdict"] = verdict
    res["runtime_s"] = round(time.time() - t0, 1)
    print("VERDICT:", verdict, res["gates"], flush=True)
    json.dump(res, open(f"{EXP}/epochs/EPOCH-013/result.json", "w"), indent=1,
              default=str)

if __name__ == "__main__":
    main()
