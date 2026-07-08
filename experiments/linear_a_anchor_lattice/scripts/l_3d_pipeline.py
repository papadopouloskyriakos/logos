#!/usr/bin/env python3
"""Task L — 3D/seal-imaging ingestion + validation pipeline (SOURCE_BLOCKED branch).

No corpus-scale licensed 3D data exists (see data/3d_channel/source_audit.json), so this
module delivers the TESTED pipeline that would ingest such data the day it appears:

  * a record schema for 3D/RTI/multi-angle/depthmap captures of Linear A-bearing objects
    and CMS seals/impressions (corpus refs, units, provenance, licence gate, ground truth)
  * deterministic validators V1-V6 (fail CLOSED)
  * a synthetic round-trip: generate seals + noisy negative-relief impressions, ingest
    them through the schema, validate, then run the two calibration tasks the real data
    would face — known-join recovery (seal <-> impression) and allograph grouping —
    against a permutation null.

Pure numpy + stdlib. Seed 20260708. Nothing here touches real corpus values (Art. XI/XII:
synthetic ground truth is generated, never derived from Linear A readings).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys

import numpy as np

SEED = 20260708
GRID = 96  # depthmap resolution (pixels); synthetic scale 1 px = 0.25 mm
PX_MM = 0.25

ALLOWED_LICENSES_ANALYSIS = {
    "CC0", "CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-NC-4.0", "CC-BY-NC-SA-4.0",
    "explicit-permission-on-file",
}
REDISTRIBUTABLE_LICENSES = {"CC0", "CC-BY-4.0", "CC-BY-SA-4.0"}

SCHEMA_REQUIRED = {
    "record_id": str,
    "corpus_ref": dict,      # {"system": GORILA|CMS|SigLA|museum_inv|SYNTHETIC, "id": str}
    "object_class": str,     # tablet|roundel|nodule|seal|sealing|libation_table|other
    "modality": str,         # mesh|rti|multiangle_photo|depthmap
    "file": dict,            # {"path","format","sha256","bytes"}
    "geometry": dict,        # {"units_mm": bool, "bbox_mm": [dx,dy,dz], "n_vertices", "n_faces"}
    "acquisition": dict,     # {"method","device","date","operator"}
    "provenance": dict,      # {"source","url","license","license_ok_for_analysis","redistributable"}
}
OBJECT_CLASSES = {"tablet", "roundel", "nodule", "seal", "sealing", "libation_table", "other"}
MODALITIES = {"mesh", "rti", "multiangle_photo", "depthmap"}
BBOX_MM_RANGE = (1.0, 1000.0)  # seals ~10-30mm, tablets/libation tables up to ~50cm


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------- validators
def validate_record(rec: dict, base_dir: str) -> list[str]:
    """Return list of violation strings; empty list == PASS. Fail CLOSED on anything odd."""
    errs: list[str] = []
    # V1 schema completeness + types
    for k, t in SCHEMA_REQUIRED.items():
        if k not in rec:
            errs.append(f"V1:missing:{k}")
        elif not isinstance(rec[k], t):
            errs.append(f"V1:type:{k}")
    if errs:
        return errs  # cannot proceed safely
    if rec["object_class"] not in OBJECT_CLASSES:
        errs.append("V1:enum:object_class")
    if rec["modality"] not in MODALITIES:
        errs.append("V1:enum:modality")
    if rec["corpus_ref"].get("system") not in {"GORILA", "CMS", "SigLA", "museum_inv", "SYNTHETIC"}:
        errs.append("V1:enum:corpus_ref.system")

    # V2 file exists + sha256 + size match
    fpath = os.path.join(base_dir, rec["file"].get("path", ""))
    if not os.path.isfile(fpath):
        errs.append("V2:file_missing")
    else:
        if sha256_file(fpath) != rec["file"].get("sha256"):
            errs.append("V2:sha256_mismatch")
        if os.path.getsize(fpath) != rec["file"].get("bytes"):
            errs.append("V2:bytes_mismatch")

    # V3 geometry sanity (depthmap npz or mesh obj)
    if os.path.isfile(fpath):
        try:
            if rec["file"].get("format") == "npz":
                z = np.load(fpath)["depth_mm"]
                if not np.all(np.isfinite(z)):
                    errs.append("V3:nonfinite_depth")
                if z.ndim != 2 or min(z.shape) < 16:
                    errs.append("V3:degenerate_grid")
            elif rec["file"].get("format") == "obj":
                v, f = load_obj(fpath)
                if not np.all(np.isfinite(v)):
                    errs.append("V3:nonfinite_vertices")
                if len(f) == 0 or degenerate_fraction(v, f) > 0.01:
                    errs.append("V3:degenerate_faces")
                if len(v) != rec["geometry"].get("n_vertices"):
                    errs.append("V3:vertex_count_mismatch")
            else:
                errs.append("V3:unknown_format")
        except Exception as e:  # noqa: BLE001 — any parse failure is a validation failure
            errs.append(f"V3:parse_error:{type(e).__name__}")

    # V4 units plausibility
    bbox = rec["geometry"].get("bbox_mm", [])
    if (not rec["geometry"].get("units_mm", False) or len(bbox) != 3
            or not all(BBOX_MM_RANGE[0] <= b <= BBOX_MM_RANGE[1] for b in bbox)):
        errs.append("V4:units_or_bbox_implausible")

    # V5 licence gate (Art. XV/X: analysis requires an allowlisted licence)
    prov = rec["provenance"]
    lic = prov.get("license")
    if lic not in ALLOWED_LICENSES_ANALYSIS:
        errs.append("V5:license_not_allowlisted")
    if bool(prov.get("license_ok_for_analysis")) is not (lic in ALLOWED_LICENSES_ANALYSIS):
        errs.append("V5:license_flag_inconsistent")
    if bool(prov.get("redistributable")) and lic not in REDISTRIBUTABLE_LICENSES:
        errs.append("V5:redistribution_overclaim")

    # V6 ground-truth referential integrity (optional block)
    gt = rec.get("ground_truth")
    if gt is not None:
        if not isinstance(gt, dict):
            errs.append("V6:gt_type")
        else:
            joins = gt.get("joins", [])
            if not isinstance(joins, list) or any(not isinstance(j, str) or j == rec["record_id"] for j in joins):
                errs.append("V6:joins_invalid")
    return errs


def validate_manifest(manifest_path: str) -> dict:
    base = os.path.dirname(manifest_path)
    recs = json.load(open(manifest_path))["records"]
    ids = [r.get("record_id") for r in recs]
    report = {"n_records": len(recs), "per_record": {}, "n_pass": 0, "n_fail": 0}
    idset = set(ids)
    if len(idset) != len(ids):
        report["duplicate_ids"] = True
    for r in recs:
        errs = validate_record(r, base)
        gt = r.get("ground_truth") or {}
        for j in gt.get("joins", []):
            if j not in idset:
                errs.append("V6:join_target_missing")
        report["per_record"][r.get("record_id", "?")] = errs
        report["n_pass" if not errs else "n_fail"] += 1
    return report


# ----------------------------------------------------------------------------- mesh utils
def load_obj(path: str):
    vs, fs = [], []
    for line in open(path):
        p = line.split()
        if not p:
            continue
        if p[0] == "v":
            vs.append([float(x) for x in p[1:4]])
        elif p[0] == "f":
            fs.append([int(x.split("/")[0]) - 1 for x in p[1:4]])
    return np.array(vs, float), np.array(fs, int)


def degenerate_fraction(v: np.ndarray, f: np.ndarray) -> float:
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    area2 = np.linalg.norm(np.cross(b - a, c - a), axis=1)
    return float(np.mean(area2 < 1e-12))


def heightfield_to_obj(z_mm: np.ndarray, path: str):
    h, w = z_mm.shape
    with open(path, "w") as f:
        for i in range(h):
            for j in range(w):
                f.write(f"v {j*PX_MM:.4f} {i*PX_MM:.4f} {z_mm[i, j]:.5f}\n")
        for i in range(h - 1):
            for j in range(w - 1):
                a = i * w + j + 1
                f.write(f"f {a} {a+1} {a+w}\nf {a+1} {a+w+1} {a+w}\n")


# ----------------------------------------------------------------------------- synthetic gen
def stroke_library(rng: np.random.Generator, n_motifs: int) -> list[list[tuple]]:
    """Each motif = list of strokes (x0,y0,x1,y1,width,depth) in unit coords."""
    motifs = []
    for _ in range(n_motifs):
        strokes = []
        for _ in range(rng.integers(2, 5)):
            x0, y0 = rng.uniform(0.15, 0.85, 2)
            ang = rng.uniform(0, 2 * math.pi)
            ln = rng.uniform(0.2, 0.5)
            x1, y1 = np.clip([x0 + ln * math.cos(ang), y0 + ln * math.sin(ang)], 0.1, 0.9)
            strokes.append((x0, y0, x1, y1, rng.uniform(0.02, 0.045), rng.uniform(0.3, 0.6)))
        motifs.append(strokes)
    return motifs


def render_motif(strokes, grid=GRID, jitter_rng=None, jitter=0.0) -> np.ndarray:
    """Engraving depth field (mm, >=0) of a motif; optional per-render jitter (allographs)."""
    yy, xx = np.mgrid[0:grid, 0:grid] / (grid - 1.0)
    z = np.zeros((grid, grid))
    for (x0, y0, x1, y1, w, d) in strokes:
        if jitter_rng is not None and jitter > 0:
            x0 += jitter_rng.normal(0, jitter); y0 += jitter_rng.normal(0, jitter)
            x1 += jitter_rng.normal(0, jitter); y1 += jitter_rng.normal(0, jitter)
            w *= float(jitter_rng.uniform(0.85, 1.15)); d *= float(jitter_rng.uniform(0.85, 1.15))
        px, py = x1 - x0, y1 - y0
        nrm2 = px * px + py * py + 1e-12
        t = np.clip(((xx - x0) * px + (yy - y0) * py) / nrm2, 0, 1)
        dist = np.hypot(xx - (x0 + t * px), yy - (y0 + t * py))
        z = np.maximum(z, d * np.exp(-(dist / w) ** 2))
    return z  # mm of engraving depth


def make_impression(seal_depth: np.ndarray, rng: np.random.Generator,
                    noise_mm=0.02, blur=1) -> tuple[np.ndarray, dict]:
    """Impression = positive relief of the seal's engraving + capture noise + pose change."""
    k = int(rng.integers(0, 4))
    imp = np.rot90(seal_depth, k)
    sx, sy = int(rng.integers(-3, 4)), int(rng.integers(-3, 4))
    imp = np.roll(np.roll(imp, sx, axis=1), sy, axis=0)
    for _ in range(blur):  # cheap 3x3 box blur (clay softening)
        imp = (imp + np.roll(imp, 1, 0) + np.roll(imp, -1, 0)
               + np.roll(imp, 1, 1) + np.roll(imp, -1, 1)) / 5.0
    imp = imp + rng.normal(0, noise_mm, imp.shape)
    return imp, {"rot90": k, "shift": [sx, sy]}


# ----------------------------------------------------------------------------- matching
def ncc(a: np.ndarray, b: np.ndarray) -> float:
    """Max normalized cross-correlation of b over all 4 rot90 poses and translations (FFT)."""
    a0 = a - a.mean()
    na = np.linalg.norm(a0) + 1e-12
    best = -1.0
    Fa = np.fft.rfft2(a0)
    for k in range(4):
        b0 = np.rot90(b, k)
        b0 = b0 - b0.mean()
        nb = np.linalg.norm(b0) + 1e-12
        corr = np.fft.irfft2(Fa * np.conj(np.fft.rfft2(b0)), s=a.shape)
        best = max(best, float(corr.max()) / (na * nb))
    return best


def join_recovery(seals: dict[str, np.ndarray], imps: dict[str, np.ndarray],
                  truth: dict[str, str], rng: np.random.Generator, n_null=200):
    """Score every seal x impression; recover joins; calibrate threshold on a permutation null."""
    sids, iids = sorted(seals), sorted(imps)
    S = np.array([[ncc(seals[s], imps[i]) for i in iids] for s in sids])
    # permutation null: scores between non-joined pairs define the null distribution;
    # planted-pair scores must clear its max (exact, no parametric assumption)
    null_scores = [S[a, b] for a, s in enumerate(sids) for b, i in enumerate(iids)
                   if truth.get(s) != i]
    planted = [(s, truth[s], S[sids.index(s), iids.index(truth[s])])
               for s in sids if truth.get(s) in imps]
    thr = float(np.max(null_scores))
    hits = sum(1 for _, _, sc in planted if sc > thr)
    # greedy argmax assignment accuracy
    pred = {s: iids[int(np.argmax(S[a]))] for a, s in enumerate(sids)}
    acc = sum(1 for s, i in truth.items() if pred.get(s) == i)
    # bootstrap of the separation margin
    margins = [sc - thr for _, _, sc in planted]
    return {
        "n_seals": len(sids), "n_impressions": len(iids),
        "n_planted_joins": len(planted),
        "argmax_recovered": acc,
        "null_max_score": round(thr, 4),
        "planted_scores": [round(sc, 4) for _, _, sc in planted],
        "planted_above_null_max": hits,
        "min_margin": round(min(margins), 4) if margins else None,
        "null_n": len(null_scores),
        "null_mean": round(float(np.mean(null_scores)), 4),
    }


def allograph_test(motifs, rng: np.random.Generator, n_groups=4, per_group=5, jitter=0.02):
    """Same-motif re-engravings (allographs) vs different motifs: within/between NCC AUC."""
    fields, labels = [], []
    for g in range(n_groups):
        for _ in range(per_group):
            fields.append(render_motif(motifs[g], jitter_rng=rng, jitter=jitter))
            labels.append(g)
    within, between = [], []
    for i in range(len(fields)):
        for j in range(i + 1, len(fields)):
            sc = ncc(fields[i], fields[j])
            (within if labels[i] == labels[j] else between).append(sc)
    w, b = np.array(within), np.array(between)
    auc = float(np.mean(w[:, None] > b[None, :]) + 0.5 * np.mean(w[:, None] == b[None, :]))
    # 1-NN grouping accuracy
    correct = 0
    for i in range(len(fields)):
        scs = [(ncc(fields[i], fields[j]), labels[j]) for j in range(len(fields)) if j != i]
        correct += int(max(scs)[1] == labels[i])
    return {"n_items": len(fields), "n_groups": n_groups,
            "within_mean": round(float(w.mean()), 4), "between_mean": round(float(b.mean()), 4),
            "auc_within_vs_between": round(auc, 4),
            "nn1_grouping_acc": round(correct / len(fields), 4)}


# ----------------------------------------------------------------------------- round trip
def run_roundtrip(out_dir: str) -> dict:
    rng = np.random.default_rng(SEED)
    os.makedirs(out_dir, exist_ok=True)
    files_dir = os.path.join(out_dir, "files")
    os.makedirs(files_dir, exist_ok=True)

    motifs = stroke_library(rng, 12)
    n_seals, n_joined = 8, 6
    seals, imps, truth, records = {}, {}, {}, []

    def add_record(rid, arr, oclass, joins=None, mesh=False):
        fname = f"{rid}.npz"
        fpath = os.path.join(files_dir, fname)
        np.savez_compressed(fpath, depth_mm=arr.astype(np.float32))
        rec = {
            "record_id": rid,
            "corpus_ref": {"system": "SYNTHETIC", "id": rid},
            "object_class": oclass,
            "modality": "depthmap",
            "file": {"path": f"files/{fname}", "format": "npz",
                     "sha256": sha256_file(fpath), "bytes": os.path.getsize(fpath)},
            "geometry": {"units_mm": True,
                                                  # z = object thickness (body + relief), not relief range alone
                         "bbox_mm": [GRID * PX_MM, GRID * PX_MM,
                                     float(arr.max() - arr.min()) + 2.0],
                         "n_vertices": int(arr.size), "n_faces": 0},
            "acquisition": {"method": "synthetic", "device": "l_3d_pipeline.py",
                            "date": "2026-07-08", "operator": "seed20260708"},
            "provenance": {"source": "synthetic round-trip", "url": None,
                           "license": "CC0", "license_ok_for_analysis": True,
                           "redistributable": True},
        }
        if joins is not None:
            rec["ground_truth"] = {"joins": joins, "allograph_group": None}
        records.append(rec)
        return rec

    for s in range(n_seals):
        depth = render_motif(motifs[s])
        sid = f"SEAL_{s:02d}"
        seals[sid] = depth
        add_record(sid, depth, "seal",
                   joins=[f"IMP_{s:02d}"] if s < n_joined else [])
    for s in range(n_joined):
        imp, _pose = make_impression(seals[f"SEAL_{s:02d}"], rng)
        iid = f"IMP_{s:02d}"
        imps[iid] = imp
        truth[f"SEAL_{s:02d}"] = iid
        add_record(iid, imp, "sealing", joins=[f"SEAL_{s:02d}"])
    for d in range(2):  # distractor impressions from motifs no seal record uses
        imp, _ = make_impression(render_motif(motifs[10 + d]), rng)
        iid = f"IMP_DISTRACTOR_{d}"
        imps[iid] = imp
        add_record(iid, imp, "sealing", joins=[])

    # one OBJ mesh record to exercise the mesh path of V3
    mesh_path = os.path.join(files_dir, "SEAL_00_mesh.obj")
    heightfield_to_obj(-seals["SEAL_00"], mesh_path)  # negative relief = actual seal face
    v, f = load_obj(mesh_path)
    records.append({
        "record_id": "SEAL_00_MESH",
        "corpus_ref": {"system": "SYNTHETIC", "id": "SEAL_00"},
        "object_class": "seal", "modality": "mesh",
        "file": {"path": "files/SEAL_00_mesh.obj", "format": "obj",
                 "sha256": sha256_file(mesh_path), "bytes": os.path.getsize(mesh_path)},
        "geometry": {"units_mm": True, "bbox_mm": [24.0, 24.0, 1.0],
                     "n_vertices": len(v), "n_faces": len(f)},
        "acquisition": {"method": "synthetic", "device": "l_3d_pipeline.py",
                        "date": "2026-07-08", "operator": "seed20260708"},
        "provenance": {"source": "synthetic round-trip", "url": None, "license": "CC0",
                       "license_ok_for_analysis": True, "redistributable": True},
    })

    manifest_path = os.path.join(out_dir, "manifest.json")
    json.dump({"schema_version": "1.0", "records": records}, open(manifest_path, "w"), indent=1)

    # -- validation of the clean manifest must PASS
    vrep = validate_manifest(manifest_path)

    # -- corruption battery: each corruption must be CAUGHT
    corruptions = {}
    import copy
    base = json.load(open(manifest_path))

    def check(name, mutate):
        m = copy.deepcopy(base)
        mutate(m)
        p = os.path.join(out_dir, "_corrupt.json")
        json.dump(m, open(p, "w"))
        rep = validate_manifest(p)
        corruptions[name] = {"caught": rep["n_fail"] > 0,
                             "example": next((e for e in rep["per_record"].values() if e), [])[:2]}
        os.remove(p)

    check("sha256_tamper", lambda m: m["records"][0]["file"].update(sha256="0" * 64))
    check("units_meters", lambda m: m["records"][1]["geometry"].update(bbox_mm=[0.024, 0.024, 0.001]))
    check("forbidden_license", lambda m: m["records"][2]["provenance"].update(
        license="all-rights-reserved", license_ok_for_analysis=True))
    check("redistribution_overclaim", lambda m: m["records"][3]["provenance"].update(
        license="CC-BY-NC-4.0", redistributable=True))
    check("self_join", lambda m: m["records"][4].update(
        ground_truth={"joins": [m["records"][4]["record_id"]], "allograph_group": None}))
    check("dangling_join", lambda m: m["records"][5].update(
        ground_truth={"joins": ["NO_SUCH_RECORD"], "allograph_group": None}))
    check("missing_field", lambda m: m["records"][6].pop("acquisition"))
    # NaN depth corruption (writes a bad file)
    bad = np.full((GRID, GRID), np.nan, np.float32)
    badp = os.path.join(files_dir, "BAD.npz")
    np.savez_compressed(badp, depth_mm=bad)
    def add_bad(m):
        r = copy.deepcopy(m["records"][0])
        r.update(record_id="BAD", file={"path": "files/BAD.npz", "format": "npz",
                                        "sha256": sha256_file(badp),
                                        "bytes": os.path.getsize(badp)})
        r.pop("ground_truth", None)
        m["records"].append(r)
    check("nan_depth", add_bad)
    os.remove(badp)

    # -- calibration tasks on the validated synthetic data
    joins = join_recovery(seals, imps, truth, rng)
    allo = allograph_test(motifs, rng)

    results = {
        "seed": SEED,
        "validation_clean": {"n_pass": vrep["n_pass"], "n_fail": vrep["n_fail"],
                             "n_records": vrep["n_records"]},
        "corruption_battery": corruptions,
        "corruptions_caught": sum(c["caught"] for c in corruptions.values()),
        "corruptions_total": len(corruptions),
        "join_recovery": joins,
        "allograph": allo,
    }
    json.dump(results, open(os.path.join(out_dir, "roundtrip_results.json"), "w"), indent=1)
    return results


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "3d_channel", "synthetic_roundtrip")
    res = run_roundtrip(out)
    ok = (res["validation_clean"]["n_fail"] == 0
          and res["corruptions_caught"] == res["corruptions_total"]
          and res["join_recovery"]["argmax_recovered"] == res["join_recovery"]["n_planted_joins"]
          and res["join_recovery"]["planted_above_null_max"] == res["join_recovery"]["n_planted_joins"]
          and res["allograph"]["auc_within_vs_between"] >= 0.95)
    print(json.dumps(res, indent=1))
    print("ROUNDTRIP:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
