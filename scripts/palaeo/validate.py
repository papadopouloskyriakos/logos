#!/usr/bin/env python3
"""validate.py -- THREE palaeographic validations for a sign-image representation.

Each validation is run for BOTH the I-JEPA and the classical representation (the
embedder is passed in, so the comparison is apples-to-apples on identical images).

  (a) ALLOGRAPH CLUSTERING  -- do known allograph families (from
      corpus/silver/signs_ontology.json -- subscript/diacritic variants:
      PA/PA3, PU/PU2, RA/RA2, TA/TA2, *131B/*131C, *309/*309B/*309C) cluster
      together in the learned space?  Metric: NN-purity (is each sign's nearest
      neighbour its allograph sibling?) + silhouette, vs a permutation null.

  (b) DAMAGED-FORM held-out -- synthesize damaged/noisy/occluded/rotated renderings
      of each base sign; can the representation identify the damaged form as its
      base sign (NN recall@1)?  Robustness of the representation.  vs 1/N_base.

  (c) CROSS-SCRIPT IMAGE ALIGNMENT -- align Linear-A glyph IMAGES to Linear-B glyph
      IMAGES via the shared signs (the 55 Track B anchors), Procrustes fit on train
      anchors + held-out recovery, AND direct shared-space NN.  This is a DIFFERENT
      signal from Track B's PPMI-SEQUENCE null: borrowed signs are VISUALLY similar,
      so image alignment MAY recover shared signs where sequence co-occurrence did
      not.  Reported vs the 1/|B| image chance floor AND vs Track B's sequence null.

Anti-circularity (identical to Track B): held-out anchors' B-side is never used in
the fit; the encoder is unsupervised (no value labels seen at training).
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from typing import Callable, Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palaeo.palaeo_common import (  # noqa: E402
    SEED, ONTOLOGY, DAMAGED_DIR, LIN_A_DIR, LIN_B_DIR, norm_token, load_anchors,
    list_a_images, list_b_images, load_image,
)

EmbedFn = Callable[[List[str]], np.ndarray]          # paths -> (N,F) matrix


# --------------------------------------------------------------------------- utils
def _cos_dist(M: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(M, axis=1, keepdims=True) + 1e-9
    C = M / n
    return 1.0 - C @ C.T


def _eucl_dist(M: np.ndarray) -> np.ndarray:
    return np.sqrt(((M[:, None, :] - M[None, :, :]) ** 2).sum(-1) + 1e-9)


def _nn_purity(D: np.ndarray, labels: List[str]) -> float:
    """Fraction of points whose NEAREST neighbour shares their label."""
    np.fill_diagonal(D, np.inf)
    hits = 0
    for i in range(len(labels)):
        j = int(D[i].argmin())
        hits += (labels[j] == labels[i])
    return hits / len(labels)


def _silhouette(M: np.ndarray, labels: List[str]) -> float:
    try:
        from sklearn.metrics import silhouette_score
        if len(set(labels)) < 2 or len(labels) < 3:
            return float("nan")
        return float(silhouette_score(M, labels))
    except Exception:
        return float("nan")


def _permutation_null(labels: List[str], observed: float, stat_fn, n: int = 2000,
                      seed: int = SEED) -> Tuple[float, float]:
    """Mean +/- p-value of NN-purity under random label permutation."""
    rng = np.random.default_rng(seed)
    arr = np.array(labels)
    ge = 0
    samples = []
    for _ in range(n):
        perm = rng.permutation(arr)
        s = stat_fn(perm)
        samples.append(s)
        ge += (s >= observed)
    return float(np.mean(samples)), (ge + 1) / (n + 1)


# ----------------------------------------------------------------- (a) allographs
def allograph_families() -> Dict[str, List[str]]:
    """Renderable allograph families (>=2 members with a rendered A glyph)."""
    ont = json.load(open(ONTOLOGY))
    fam = defaultdict(list)
    for tok, info in ont.items():
        f = info.get("allograph_family")
        if f:
            fam[f].append(norm_token(tok))
    present = {v for v, _ in list_a_images()}
    out = {}
    for f, toks in fam.items():
        rt = [t for t in toks if t in present]
        if len(rt) >= 2:
            out[f] = sorted(set(rt))
    return out


def val_allograph(embed_fn: EmbedFn) -> dict:
    fams = allograph_families()
    members = [t for toks in fams.values() for t in toks]
    paths = {v: p for v, p in list_a_images()}
    sel = [paths[m] for m in members if m in paths]
    sel_members = [m for m in members if m in paths]
    labels = []
    for m in sel_members:
        fam = next(f for f, toks in fams.items() if m in toks)
        labels.append(fam)
    M = embed_fn(sel)
    D = _cos_dist(M)
    obs = _nn_purity(D.copy(), labels)
    sil = _silhouette(M, labels)

    def stat(lab):
        return _nn_purity(D.copy(), list(lab))
    chance, p = _permutation_null(labels, obs, stat, n=2000)
    return {"n_signs": len(sel_members), "n_families": len(set(labels)),
            "families": fams, "nn_purity": obs, "nn_purity_chance": chance,
            "nn_purity_p": p, "silhouette": sil,
            "chance_note": "permutation null (random label shuffle, 2000 draws)"}


# ------------------------------------------------------------ (b) damaged recall
def _damage(img: np.ndarray, kind: str, rng) -> np.ndarray:
    t = img.copy()
    H, W = t.shape
    if kind == "rotate":
        from skimage.transform import rotate
        ang = float(rng.uniform(-18, 18))
        t = rotate(t, ang, order=1, mode="constant", cval=0.0, preserve_range=True)
    elif kind == "occlude":
        bh, bw = int(H * rng.uniform(0.15, 0.35)), int(W * rng.uniform(0.15, 0.35))
        y0 = int(rng.integers(0, H - bh + 1)); x0 = int(rng.integers(0, W - bw + 1))
        t[y0:y0 + bh, x0:x0 + bw] = 0.0
    elif kind == "erode":
        thr = t.max() * rng.uniform(0.3, 0.6)
        b = (t > thr)
        from scipy.ndimage import binary_erosion
        b = binary_erosion(b, iterations=int(rng.integers(1, 3)))
        t = t * b
    elif kind == "noise":
        t = t + rng.normal(0, 0.12, t.shape)
        t = np.clip(t, 0, 1)
    elif kind == "scale":
        from skimage.transform import rescale
        s = float(rng.uniform(0.80, 1.20))
        r = rescale(t, s, order=1, mode="constant", cval=0.0, anti_aliasing=True)
        # pad/crop back to IMG_SIZE
        out = np.zeros_like(t)
        h, w = min(r.shape[0], H), min(r.shape[1], W)
        out[:h, :w] = r[:h, :w]
        t = out
    return t


def _gen_damaged(n_variants: int, seed: int) -> List[Tuple[str, str]]:
    """Generate damaged PNGs for every base sign. Returns [(base_value, path)]."""
    from PIL import Image
    rng = np.random.default_rng(seed)
    os.makedirs(DAMAGED_DIR, exist_ok=True)
    kinds = ["rotate", "occlude", "erode", "noise", "scale"]
    base = list_a_images() + list_b_images()
    pairs = []
    for val, p in base:
        img = load_image(p)
        for k in range(n_variants):
            kind = kinds[k % len(kinds)]
            d = _damage(img, kind, rng)
            outp = os.path.join(DAMAGED_DIR, f"{val}__{kind}{k}.png")
            Image.fromarray((d * 255).astype(np.uint8)).save(outp)
            pairs.append((val, outp))
    return pairs


def val_damaged(embed_fn: EmbedFn, n_variants: int = 5, seed: int = SEED) -> dict:
    pairs = _gen_damaged(n_variants, seed)
    base = list_a_images() + list_b_images()
    base_paths = [p for _, p in base]
    base_vals = [v for v, _ in base]
    B = embed_fn(base_paths)                           # (Nb, F) clean references
    damaged_paths = [p for _, p in pairs]
    true = [v for v, _ in pairs]
    Dm = embed_fn(damaged_paths)                       # (Nd, F)
    # cosine NN in the shared embedding space
    Bn = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-9)
    Dn = Dm / (np.linalg.norm(Dm, axis=1, keepdims=True) + 1e-9)
    sim = Dn @ Bn.T
    nn = sim.argmax(axis=1)
    pred = [base_vals[j] for j in nn]
    hits = sum(p == t for p, t in zip(pred, true))
    recall = hits / len(true)
    chance = 1.0 / len(base_vals)
    per_kind = defaultdict(lambda: [0, 0])
    for (val, p), pr in zip(pairs, pred):
        kind = os.path.basename(p).split("__")[1].rstrip("0123456789.png") \
            if "__" in os.path.basename(p) else "?"
        # robust kind parse
        bn = os.path.basename(p)[:-4]
        kind = bn.split("__")[1].rstrip("0123456789") if "__" in bn else "?"
        per_kind[kind][0 if pr == val else 1] += 1
    per_kind_recall = {k: v[0] / (v[0] + v[1]) for k, v in per_kind.items()}
    return {"recall_at_1": recall, "chance": chance, "n_base": len(base_vals),
            "n_damaged": len(true), "n_variants": n_variants,
            "recall_by_damage": dict(sorted(per_kind_recall.items()))}


# ------------------------------------------------------- (c) cross-script images
def _procrustes_fit(A_tr, B_tr, A_held, B_pool):
    """Orthogonal Procrustes A->B fit on train, NN-recover held-out in B_pool."""
    # center
    am, bm = A_tr.mean(0), B_tr.mean(0)
    Xs, Ys = A_tr - am, B_tr - bm
    U, _, Vt = np.linalg.svd(Xs.T @ Ys, full_matrices=False)
    R = U @ Vt
    Ah = (A_held - am) @ R
    Bp = B_pool - bm
    # NN by cosine
    Ahn = Ah / (np.linalg.norm(Ah, axis=1, keepdims=True) + 1e-9)
    Bpn = Bp / (np.linalg.norm(Bp, axis=1, keepdims=True) + 1e-9)
    idx = (Ahn @ Bpn.T).argmax(axis=1)
    return idx


def val_cross_script(embed_fn: EmbedFn, n_splits: int = 200,
                     held_frac: float = 0.2, seed: int = SEED) -> dict:
    a_imgs = dict(list_a_images())
    b_imgs = dict(list_b_images())
    anchors, nB_seq, chance_seq, seq_null = load_anchors()
    # anchors that have BOTH an A glyph and a B glyph image
    anchors = [v for v in anchors if v in a_imgs and v in b_imgs]
    a_paths = [a_imgs[v] for v in anchors]
    b_paths = [b_imgs[v] for v in anchors]
    A = embed_fn(a_paths)
    B = embed_fn(b_paths)
    # full B pool (every rendered B glyph is a valid distractor)
    bpool_paths = [p for _, p in list_b_images()]
    bpool_vals = [v for v, _ in list_b_images()]
    Bpool = embed_fn(bpool_paths)
    nB_image = len(bpool_vals)

    rng = np.random.default_rng(seed)
    n_hold = max(1, int(round(held_frac * len(anchors))))
    direct_hits, proc_hits = 0, 0
    total = 0
    direct_split_rates, proc_split_rates = [], []
    for _ in range(n_splits):
        perm = rng.permutation(len(anchors))
        held = perm[:n_hold]
        train = perm[n_hold:]
        # shared-space direct NN (no fit needed -- same encoder)
        Ah = A[held]; Bp = Bpool
        Ahn = Ah / (np.linalg.norm(Ah, axis=1, keepdims=True) + 1e-9)
        Bpn = Bp / (np.linalg.norm(Bp, axis=1, keepdims=True) + 1e-9)
        di = (Ahn @ Bpn.T).argmax(axis=1)
        # procrustes on train anchor pairs
        pi = _procrustes_fit(A[train], B[train], A[held], Bpool)
        dh = ph = 0
        for k, h in enumerate(held):
            true_val = anchors[h]
            dh += (bpool_vals[di[k]] == true_val)
            ph += (bpool_vals[pi[k]] == true_val)
        direct_hits += dh; proc_hits += ph; total += n_hold
        direct_split_rates.append(dh / n_hold)
        proc_split_rates.append(ph / n_hold)
    direct_rec = direct_hits / total
    proc_rec = proc_hits / total
    # 95% interval over the per-split hit rate (Track B reports ci_lo/ci_hi this way)
    def ci(rates):
        return (float(np.percentile(rates, 2.5)), float(np.percentile(rates, 97.5)))
    chance_image = 1.0 / nB_image
    return {
        "n_anchors": len(anchors), "n_hold_per_split": n_hold, "n_splits": n_splits,
        "nB_image_pool": nB_image, "chance_image": chance_image,
        "recovery_direct_nn": direct_rec, "recovery_direct_ci95": ci(direct_split_rates),
        "recovery_procrustes": proc_rec, "recovery_procrustes_ci95": ci(proc_split_rates),
        "trackB_nB_seq": nB_seq, "trackB_chance_seq": chance_seq,
        "trackB_seq_null": seq_null,   # {method: mean recovery}
        "trackB_best_seq": max(seq_null.get(m, 0) for m in seq_null if m != "random_chance"),
    }


if __name__ == "__main__":
    from palaeo import classical
    paths = [p for _, p in list_a_images()]
    fn = lambda ps: classical.embed(ps)[0]
    print("(a)", val_allograph(fn))
