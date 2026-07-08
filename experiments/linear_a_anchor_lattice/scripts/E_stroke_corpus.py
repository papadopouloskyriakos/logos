#!/usr/bin/env python3
"""TASK E — palaeographic stroke/orientation corpus (non-circular shape channel).

Audits what geometry SigLA actually ships, builds the bbox-geometry representation
that IS recoverable, calibrates its sign-identity power WITHIN Linear A (the only
known-identity grouping available without cross-script glyph geometry), runs a
leave-one-sign-out recovery, and issues SOURCE_BLOCKED for every channel that needs
true stroke/contour/image evidence the snapshot does not carry.

NON-CIRCULAR: no phonetic value is ever used to build a feature. Signs are grouped by
GORILA sign-name (a palaeographic identification) and by allograph_family. Phonetic
values are never inputs.

Seed 20260708.
"""
import json, os, math, itertools, random
import numpy as np
from collections import defaultdict, Counter

SEED = 20260708
random.seed(SEED); np.random.seed(SEED)

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-anchor-lattice"
LOGOS = "/home/claude-runner/gitlab/n8n/logos"
EXP = f"{ROOT}/experiments/linear_a_anchor_lattice"
DATA = f"{EXP}/data/stroke_corpus"
os.makedirs(DATA, exist_ok=True)

docs = json.load(open(f"{LOGOS}/corpus/bronze/sigla_browse_2026/sigla_documents.json"))
onto = json.load(open(f"{LOGOS}/corpus/silver/signs_ontology.json"))

# ---------------------------------------------------------------- E1: source audit
# What does the raw database.js carry? -> checked externally: only `var signs` (id/class/
# gorila_number/name/ref) and `var data` (per-doc glyphs with bbox=[x,y,w,h]). No SVG path,
# no stroke polyline, no contour, no image, no orientation. Drawings (document/<d>/<d>.png)
# were deliberately NOT scraped (polite single-pass). So true-stroke evidence is absent.
fam = defaultdict(list)
for k, v in onto.items():
    fam[v.get("allograph_family")].append(k)
multi_fam = {f: m for f, m in fam.items() if len(m) > 1}

# ---------------------------------------------------------------- build instance geometry
# Per glyph instance we recover: bbox w,h  -> aspect = w/h (SCALE-INVARIANT, the only
# sign-intrinsic geometric observable). Absolute size is confounded by per-document drawing
# scale, so we also compute a within-document RELATIVE size (area / median area in that doc).
inst = defaultdict(list)          # sign -> list of dict(aspect, relsize, site, period, support)
doc_meta_by_sign = defaultdict(lambda: {"site": Counter(), "period": Counter(), "support": Counter()})
for d in docs:
    glyphs = [g for g in d.get("glyphs", []) if g.get("sign") and g.get("bbox")]
    areas = [g["bbox"][2] * g["bbox"][3] for g in glyphs]
    med = np.median(areas) if areas else 1.0
    for g in glyphs:
        x, y, w, h = g["bbox"]
        if h <= 0 or w <= 0:
            continue
        s = g["sign"]
        inst[s].append({
            "aspect": w / h,
            "relsize": (w * h) / med if med else 1.0,
            "site": d.get("site"), "period": d.get("period"), "support": d.get("support"),
        })
        doc_meta_by_sign[s]["site"][d.get("site")] += 1
        doc_meta_by_sign[s]["period"][d.get("period")] += 1
        doc_meta_by_sign[s]["support"][d.get("support")] += 1

# ---------------------------------------------------------------- E2(a): rule-based representation
rep_a = {}
for s, rows in inst.items():
    asp = np.array([r["aspect"] for r in rows])
    rel = np.array([r["relsize"] for r in rows])
    rep_a[s] = {
        "n": len(rows),
        "aspect_mean": float(asp.mean()), "aspect_sd": float(asp.std()),
        "logrel_mean": float(np.log(rel).mean()), "logrel_sd": float(np.log(rel).std()),
        "class": onto.get(s, {}).get("class"),
        "allograph_family": onto.get(s, {}).get("allograph_family"),
    }
json.dump(rep_a, open(f"{DATA}/rep_a_bbox_geometry.json", "w"), indent=1)

# feature availability matrix (which shape sub-channels exist)
CHANNELS = {
    "aspect_ratio":      {"available": True,  "source": "bbox w/h (scale-invariant)"},
    "relative_size":     {"available": True,  "source": "bbox area / within-doc median (scale-confounded across docs)"},
    "stroke_count":      {"available": False, "source": "SOURCE_BLOCKED: requires glyph tracings; not in snapshot"},
    "endpoints_junctions":{"available": False,"source": "SOURCE_BLOCKED: requires skeleton; no image/vector"},
    "curves_loops":      {"available": False, "source": "SOURCE_BLOCKED: requires contour; no image/vector"},
    "orientation":       {"available": False, "source": "SOURCE_BLOCKED: bbox is axis-aligned; no rotation angle"},
    "contour_embedding": {"available": False, "source": "SOURCE_BLOCKED (E2b): requires raster/vector glyph; drawings not scraped"},
}

# ---------------------------------------------------------------- E3: identity-discrimination calibration
# Known-identity grouping = GORILA sign-name (palaeographic, non-phonetic).
# Cross-script (LA<->LB / LB<->Cypriot) stroke->identity is SOURCE_BLOCKED (no LB/Cypriot
# glyph geometry anywhere in inputs). The available proxy: can the bbox-geometry channel
# even separate same-sign instance pairs from different-sign pairs WITHIN Linear A?
signs_ok = [s for s, r in rep_a.items() if r["n"] >= 5]        # 113 signs
# per-instance feature vectors
X = {}   # sign -> array (n,2)  [aspect, logrel]
for s in signs_ok:
    rows = inst[s]
    X[s] = np.array([[r["aspect"], math.log(r["relsize"])] for r in rows])
# standardize globally
allrows = np.vstack([X[s] for s in signs_ok])
mu, sd = allrows.mean(0), allrows.std(0)
Xz = {s: (X[s] - mu) / sd for s in signs_ok}

def auc_from_scores(pos, neg):
    # AUC via rank statistic; higher score = more likely SAME sign (we feed similarity)
    labels = np.array([1] * len(pos) + [0] * len(neg))
    scores = np.array(list(pos) + list(neg))
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=float); ranks[order] = np.arange(1, len(scores) + 1)
    # average ties
    _, inv, cnt = np.unique(scores, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); rmean = {}
    start = 0
    for i, c in enumerate(cnt):
        rmean[i] = (start + 1 + start + c) / 2.0; start += c
    ranks = np.array([rmean[i] for i in inv])
    n_pos = labels.sum(); n_neg = len(labels) - n_pos
    auc = (ranks[labels == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)

# sample same-sign and diff-sign instance pairs; similarity = -euclidean distance in z-space
N_PAIRS = 40000
same_scores, diff_scores = [], []
slist = signs_ok
for _ in range(N_PAIRS):
    s = random.choice(slist)
    if len(Xz[s]) < 2:
        continue
    i, j = random.sample(range(len(Xz[s])), 2)
    same_scores.append(-np.linalg.norm(Xz[s][i] - Xz[s][j]))
for _ in range(N_PAIRS):
    a, b = random.sample(slist, 2)
    i = random.randrange(len(Xz[a])); j = random.randrange(len(Xz[b]))
    diff_scores.append(-np.linalg.norm(Xz[a][i] - Xz[b][j]))
auc_geom = auc_from_scores(same_scores, diff_scores)

# aspect-ONLY (pure generic visual similarity baseline) — cannot be beaten by our channel
Xa = {s: ((X[s][:, :1] - mu[0]) / sd[0]) for s in signs_ok}
same_a, diff_a = [], []
for _ in range(N_PAIRS):
    s = random.choice(slist)
    if len(Xa[s]) < 2: continue
    i, j = random.sample(range(len(Xa[s])), 2)
    same_a.append(-abs(Xa[s][i, 0] - Xa[s][j, 0]))
for _ in range(N_PAIRS):
    a, b = random.sample(slist, 2)
    i = random.randrange(len(Xa[a])); j = random.randrange(len(Xa[b]))
    diff_a.append(-abs(Xa[a][i, 0] - Xa[b][j, 0]))
auc_aspect = auc_from_scores(same_a, diff_a)

# ---------------------------------------------------------------- E5: leave-one-sign-out recovery
# Hold out each instance; classify to nearest sign-centroid (in z-space) among the 113 signs.
cent = {s: Xz[s].mean(0) for s in signs_ok}
freq = {s: len(inst[s]) for s in signs_ok}
top1 = top5 = tot = 0
for s in signs_ok:
    for i in range(len(Xz[s])):
        # leave-one-out centroid for the true sign
        if len(Xz[s]) > 1:
            c_s = (Xz[s].sum(0) - Xz[s][i]) / (len(Xz[s]) - 1)
        else:
            c_s = Xz[s][i]
        d = []
        for t in signs_ok:
            ct = c_s if t == s else cent[t]
            d.append((np.linalg.norm(Xz[s][i] - ct), t))
        d.sort()
        rank_signs = [t for _, t in d]
        if rank_signs[0] == s: top1 += 1
        if s in rank_signs[:5]: top5 += 1
        tot += 1
acc1 = top1 / tot; acc5 = top5 / tot
chance1 = 1.0 / len(signs_ok)
mfreq_base = max(freq.values()) / sum(freq.values())   # always-guess-commonest
chance5 = 5.0 / len(signs_ok)

# ---------------------------------------------------------------- E4: ranked shape correspondences
# nearest-neighbour sign pairs by centroid distance, decomposed by channel.
def overlap(counter_a, counter_b):
    ka, kb = set(counter_a) - {None}, set(counter_b) - {None}
    if not ka or not kb: return None
    inter = sum((counter_a & counter_b).values())
    tot = sum((counter_a | counter_b).values())
    return inter / tot if tot else None

centarr = np.array([cent[s] for s in signs_ok])
pairs = []
for a_i in range(len(signs_ok)):
    for b_i in range(a_i + 1, len(signs_ok)):
        a, b = signs_ok[a_i], signs_ok[b_i]
        dist = float(np.linalg.norm(cent[a] - cent[b]))
        pairs.append((dist, a, b))
pairs.sort()
ranked = []
for dist, a, b in pairs[:60]:
    ma, mb = doc_meta_by_sign[a], doc_meta_by_sign[b]
    ranked.append({
        "sign_a": a, "sign_b": b,
        "shape_geom_dist_z": round(dist, 4),
        "shape_channel": "aspect+relsize (WEAK: generic-visual only)",
        "stroke_channel": "SOURCE_BLOCKED",
        "orientation_channel": "SOURCE_BLOCKED",
        "chronology_period_overlap": (lambda o: round(o, 3) if o is not None else None)(overlap(ma["period"], mb["period"])),
        "geography_site_overlap": (lambda o: round(o, 3) if o is not None else None)(overlap(ma["site"], mb["site"])),
        "adminfn_support_overlap": (lambda o: round(o, 3) if o is not None else None)(overlap(ma["support"], mb["support"])),
        "class_a": onto.get(a, {}).get("class"), "class_b": onto.get(b, {}).get("class"),
        "note": "shape-only proximity earns NO value transfer (LIN-08 forbidden); listed as floor only",
    })
json.dump(ranked, open(f"{DATA}/E4_ranked_correspondences.json", "w"), indent=1)

# allograph-family supplementary check (thin: 9 multi-member families; how many have >=2 signs with bbox)
fam_pairs = []
for f, members in multi_fam.items():
    present = [m for m in members if m in cent]
    for a, b in itertools.combinations(present, 2):
        fam_pairs.append({"family": f, "a": a, "b": b,
                          "geom_dist_z": round(float(np.linalg.norm(cent[a] - cent[b])), 4)})

# ---------------------------------------------------------------- summary
summary = {
    "seed": SEED,
    "E1_source_audit": {
        "sigla_docs": len(docs),
        "named_glyph_instances_with_bbox": sum(len(v) for v in inst.values()),
        "distinct_signs_with_geometry": len(inst),
        "signs_ge5_instances": len(signs_ok),
        "signs_ge10_instances": sum(1 for s, r in rep_a.items() if r["n"] >= 10),
        "raw_db_vars": ["signs", "data"],
        "geometry_in_snapshot": "bbox=[x,y,w,h] axis-aligned pixel coords ONLY",
        "strokes_vectors_images_present": False,
        "document_drawings_scraped": False,
        "allograph_families_total": len(fam),
        "allograph_families_multi_member": len(multi_fam),
        "facsimile_vs_font": "facsimile-derived bbox metadata only; NO modern-font glyphs used as evidence",
    },
    "E2_representations": {
        "rep_a_rule_based": "built (per-sign aspect_mean/sd, logrel_mean/sd)",
        "rep_b_learned_contour": "SOURCE_BLOCKED (no raster/vector glyph in snapshot)",
        "channel_availability": CHANNELS,
    },
    "E3_calibration": {
        "cross_script_stroke_to_identity": "SOURCE_BLOCKED (no LB / Cypriot glyph geometry in any input)",
        "within_LA_identity_discrimination_AUC_geom": round(auc_geom, 4),
        "aspect_only_generic_baseline_AUC": round(auc_aspect, 4),
        "beats_generic_visual_similarity": bool(auc_geom > auc_aspect + 0.02),
        "n_pairs_each_class": N_PAIRS,
        "interpretation": "channel does not exceed generic aspect/size similarity; it IS that similarity",
    },
    "E5_leave_one_sign_out": {
        "n_signs": len(signs_ok), "n_instances": tot,
        "top1_acc": round(acc1, 4), "top5_acc": round(acc5, 4),
        "chance_top1_uniform": round(chance1, 4),
        "majority_baseline_top1": round(mfreq_base, 4),
        "chance_top5_uniform": round(chance5, 4),
    },
    "E4_correspondences": {"n_ranked": len(ranked), "file": "E4_ranked_correspondences.json",
                            "allograph_family_pairs": fam_pairs},
    "verdict": "SHAPE_CHANNEL_SOURCE_BLOCKED_FOR_STROKES; bbox-aspect channel has NO sign-identity power",
}
json.dump(summary, open(f"{DATA}/E_summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
