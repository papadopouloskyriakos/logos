#!/usr/bin/env python3
"""classical.py -- the torch-LESS comparator representation (always available).

Per sign image we concatenate three classical palaeographic descriptors, then
z-score and (optionally) PCA-whiten to a fixed-width embedding:

  * HOG  -- histogram of oriented gradients (skimage).  Captures STROKE DIRECTION,
            the workhorse descriptor for hand-drawn glyph similarity.
  * Hu moments -- 7 translation/scale/rotation invariant image moments
            (skimage.measure).  Captures global shape layout.
  * Radial + angular profile of the ink (a lightweight global shape-context):
            16 log-radius bins x 16 angle bins of ink mass about the centroid.

This is the baseline the expert audits predicted would WIN on ~90 small glyph
images (hand-crafted descriptors dominate deep SSL when data is tiny).  The honest
I-JEPA-vs-classical comparison is the point of run_palaeo.py.

No torch dependency.  Deterministic (seeded).
"""
from __future__ import annotations

import os
import sys
from typing import List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palaeo.palaeo_common import load_image, SEED  # noqa: E402


def _hog(img: np.ndarray) -> np.ndarray:
    from skimage.feature import hog
    return hog(img, orientations=8, pixels_per_cell=(12, 12),
               cells_per_block=(2, 2), block_norm="L2-Hys", feature_vector=True)


def _hu_moments(img: np.ndarray) -> np.ndarray:
    from skimage.measure import moments_normalized, moments_hu
    bin = (img > (img.max() * 0.25)).astype(np.float64) if img.max() > 0 else img
    try:
        m = moments_normalized(bin, order=3)
        hu = np.asarray(moments_hu(m), dtype=np.float64)
    except Exception:
        hu = np.zeros(7)
    hu = np.where(np.isfinite(hu), hu, 0.0)
    # Hu moments span orders of magnitude -> log-transform (sign-aware)
    return np.sign(hu) * np.log1p(np.abs(hu))


def _shape_profile(img: np.ndarray, n_rad: int = 12, n_ang: int = 16) -> np.ndarray:
    """Log-radial x angular histogram of ink mass about the centroid (global shape)."""
    ink = img > (img.max() * 0.25)
    if ink.sum() < 4:
        return np.zeros(n_rad * n_ang)
    ys, xs = np.where(ink)
    cy, cx = ys.mean(), xs.mean()
    dy, dx = ys - cy, xs - cx
    r = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)                       # [-pi, pi]
    rmax = r.max() if r.max() > 0 else 1.0
    logr = np.log1p(r) / (np.log1p(rmax) + 1e-9)   # [0,1]
    ri = np.clip((logr * n_rad).astype(int), 0, n_rad - 1)
    ai = np.clip(((ang + np.pi) / (2 * np.pi) * n_ang).astype(int), 0, n_ang - 1)
    H = np.zeros((n_rad, n_ang))
    np.add.at(H, (ri, ai), 1)
    H /= (H.sum() + 1e-9)
    return H.ravel()


def features_for(img: np.ndarray) -> np.ndarray:
    return np.concatenate([_hog(img), _hu_moments(img), _shape_profile(img)])


def embed(paths: List[str], pca_dim: int = 48) -> Tuple[np.ndarray, List[str]]:
    """Embed a list of image paths -> (matrix NxF', paths).  z-scored + PCA-whitened.

    PCA to pca_dim keeps the comparison fair with I-JEPA's fixed embedding width and
    removes the trivially-correlated burst in HOG.  Falls back to no PCA if N or F
    is too small.  For a CONSISTENT embedding space across validations, use
    ``ClassicalEmbedder`` (fit once, apply anywhere) instead of this helper.
    """
    emb = ClassicalEmbedder(pca_dim=pca_dim).fit(paths)
    return emb.embed(paths), list(paths)


class ClassicalEmbedder:
    """Fit the standardize+PCA transform ONCE; embed any paths in the SAME space.

    The transform is fit on the base corpus so damaged / held-out images land in a
    single consistent feature space (no per-call re-fit -> fair across validations).
    """

    def __init__(self, pca_dim: int = 48):
        self.pca_dim = pca_dim
        self.mu = self.sd = self.Vt = self.pca_mean = None
        self._has_pca = False

    def fit(self, paths: List[str]) -> "ClassicalEmbedder":
        feats = np.stack([features_for(load_image(p)) for p in paths])
        self.mu = feats.mean(0)
        self.sd = feats.std(0) + 1e-9
        Z = (feats - self.mu) / self.sd
        if self.pca_dim and Z.shape[1] > self.pca_dim and Z.shape[0] > self.pca_dim:
            self.pca_mean = Z.mean(0)
            U, S, Vt = np.linalg.svd(Z - self.pca_mean, full_matrices=False)
            self.Vt = Vt[:self.pca_dim]
            self._S = S[:self.pca_dim]
            self._has_pca = True
        return self

    def embed(self, paths: List[str]) -> np.ndarray:
        feats = np.stack([features_for(load_image(p)) for p in paths])
        Z = (feats - self.mu) / self.sd
        if self._has_pca:
            Z = (Z - self.pca_mean) @ self.Vt.T
            Z = Z * self._S                      # scale by singular values (whiten-ish)
        return Z


if __name__ == "__main__":
    from palaeo.palaeo_common import list_a_images
    paths = [p for _, p in list_a_images()]
    M, _ = embed(paths)
    print(f"classical embed: {M.shape} from {len(paths)} Linear A signs")
