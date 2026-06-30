#!/usr/bin/env python3
"""jepa.py -- a SMALL I-JEPA (Assran et al. 2023) for sign glyph images.

I-JEPA predicts the LATENT of target image patches from a context, IN LATENT SPACE
(not pixels), with an EMA target encoder + stop-gradient + a non-contrastive MSE
objective.  This is the faithful recipe -- NOT a contrastive Siamese mislabelled:
there are no negatives, no pairs, and the supervision is the target encoder's own
stop-gradiented latent (a bootstrap that would collapse without the EMA + predictor
asymmetry, exactly as in the paper).

CNN-backbone adaptation (documented): the original I-JEPA masks patch TOKENS of a
ViT.  We use a lightweight CNN encoder that emits a G x G feature map (one latent
vector per 16x16 patch); masking is therefore realized in INPUT space (target +
context-erased patches are zeroed before the context encoder).  The objective is
unchanged: predict the stop-gradiented target-encoder latent at the target
positions.  This is the standard "masked-prediction over a conv feature map" reading
of I-JEPA, kept tiny for CPU.

Tiny by design (the audits predict classical wins on ~90 images): a 4-layer conv
encoder (~D=128), a 2-layer conv predictor, G=6 (=> 36 patches/img), ~50 epochs.

If torch is unavailable, TORCH_OK is False and the pipeline falls back to the
classical comparator (reported honestly by run_palaeo.py).

Ref: Assran, M., ...
  "Self-Supervised Learning from Images with a Joint-Embedding Predictive
   Architecture", M. Assran, A. Dubois, I. Misra, P. Bojanowski, F. Bordes,
   P. Vincent, M. Rabbat, Y. LeCun, arXiv:2301.08243, 2023 (Meta AI).
"""
from __future__ import annotations

import os
import sys
from typing import List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palaeo.palaeo_common import SEED  # noqa: E402

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_OK = True
    try:
        torch.set_num_threads(4)
    except Exception:
        pass
except Exception as _e:                                # pragma: no cover
    torch = None
    TORCH_OK = False
    _IMPORT_ERR = str(_e)

PATCH = 16
G = 96 // PATCH                                        # 6 -> 36 patches
D = 128                                                # latent width


# --------------------------------------------------------------------------- nets
class ConvEncoder(nn.Module):
    """96x96x1 -> (D, G, G): one latent vector per 16x16 patch."""

    def __init__(self, d: int = D):
        super().__init__()
        def blk(i, o):
            return nn.Sequential(nn.Conv2d(i, o, 3, stride=2, padding=1),
                                 nn.BatchNorm2d(o), nn.ReLU(inplace=True))
        self.net = nn.Sequential(blk(1, 32), blk(32, 64), blk(64, 128), blk(128, d))

    def forward(self, x):
        return self.net(x)


class Predictor(nn.Module):
    """context latent (+pos) -> predicted target latents, same (D,G,G) shape."""

    def __init__(self, d: int = D):
        super().__init__()
        self.pos = nn.Parameter(torch.randn(1, d, G, G) * 0.02)
        self.net = nn.Sequential(
            nn.Conv2d(d, d, 3, padding=1), nn.BatchNorm2d(d), nn.ReLU(inplace=True),
            nn.Conv2d(d, d, 3, padding=1), nn.BatchNorm2d(d), nn.ReLU(inplace=True),
            nn.Conv2d(d, d, 1),
        )

    def forward(self, zc):
        return self.net(zc + self.pos)


class IJEPA(nn.Module):
    def __init__(self, d: int = D, ema_tau: float = 0.99):
        super().__init__()
        self.context = ConvEncoder(d)
        self.target = ConvEncoder(d)
        self.pred = Predictor(d)
        self.ema_tau = ema_tau
        self._init_target_ema()

    def _init_target_ema(self):
        for p in self.target.parameters():
            p.requires_grad_(False)
        self._sync_ema(hard=True)

    @torch.no_grad()
    def _sync_ema(self, hard: bool = False):
        tau = 0.0 if hard else self.ema_tau
        for cp, tp in zip(self.context.parameters(), self.target.parameters()):
            tp.mul_(tau).add_(cp.detach() * (1.0 - tau))

    def _erase_patches(self, x, visible_mask):
        """Zero out non-visible 16x16 patches in the input image (input-space mask).

        x: (N,1,96,96); visible_mask: (N, G*G) in {0,1}.
        """
        N = x.shape[0]
        m = visible_mask.view(N, 1, G, G, 1, 1)            # (N,1,G,G,1,1) -> broadcast
        # x is (N,1,H,W). Group into a G x G grid of PATCH x PATCH cells:
        # view -> (N,1, row_g, row_px, col_g, col_px); permute -> (N,1, row_g, col_g, row_px, col_px)
        patches = x.view(N, 1, G, PATCH, G, PATCH).permute(0, 1, 2, 4, 3, 5)
        # m: (N,1,G,G,1,1) broadcasts over the trailing (row_px, col_px)
        patches = patches * m
        return patches.permute(0, 1, 2, 4, 3, 5).reshape(N, 1, 96, 96)

    def step_loss(self, x, rng):
        """One I-JEPA objective evaluation for a batch.

        Returns scalar loss.  x: (N,1,96,96).  For each image we sample target
        patches (to predict) and a context-visibility mask (the rest, partly erased).
        """
        N = x.shape[0]
        device = x.device
        pos = torch.arange(G * G, device=device)
        # target patches per image: random count 4..10
        n_tgt = int(rng.integers(4, 11))
        tgt_idx = torch.from_numpy(rng.choice(G * G, size=n_tgt, replace=False)).to(device)
        target_mask = torch.zeros(N, G * G, device=device)
        target_mask[:, tgt_idx] = 1.0
        target_mask = target_mask.view(N, 1, G, G)
        # context visibility: erase targets + a random extra fraction (~45% of rest)
        extra_keep = (torch.rand(N, G * G, device=device) > 0.45).float()
        visible = extra_keep * (1 - target_mask.view(N, G * G))
        visible = (visible > 0).float()
        # safety: ensure at least ~40% visible
        frac = visible.mean(dim=1, keepdim=True)
        visible = torch.where(frac < 0.30, torch.ones_like(visible), visible)
        x_ctx = self._erase_patches(x, visible)
        with torch.no_grad():
            z_t = self.target(x)                          # (N,D,G,G) stop-grad targets
        z_c = self.context(x_ctx)
        pred = self.pred(z_c)
        diff2 = (pred - z_t) ** 2 * target_mask
        return diff2.sum() / (target_mask.sum() * D + 1e-9)

    # --------------------------------------------------------------- training API
    def train_on(self, images: np.ndarray, epochs: int = 50, batch: int = 32,
                 lr: float = 1e-3, seed: int = SEED, log: bool = True):
        torch.manual_seed(seed)
        np.random.seed(seed)
        rng = np.random.default_rng(seed)
        X = torch.from_numpy(images.astype(np.float32)).unsqueeze(1)   # (N,1,96,96)
        N = X.shape[0]
        opt = torch.optim.AdamW(list(self.context.parameters()) +
                                list(self.pred.parameters()), lr=lr, weight_decay=1e-4)
        self.train()
        hist = []
        for ep in range(epochs):
            perm = rng.permutation(N)
            tot = 0.0
            for i in range(0, N, batch):
                idx = perm[i:i + batch]
                xb = X[idx]
                opt.zero_grad()
                loss = self.step_loss(xb, rng)
                loss.backward()
                opt.step()
                self._sync_ema(hard=False)
                tot += float(loss.item()) * len(idx)
            hist.append(tot / N)
            if log and (ep == 0 or (ep + 1) % 10 == 0 or ep == epochs - 1):
                print(f"  [ijepa] epoch {ep + 1:3d}/{epochs}  loss={hist[-1]:.4f}")
        return hist

    @torch.no_grad()
    def embed(self, images: np.ndarray) -> np.ndarray:
        """Embed images via the context encoder, global-average-pooled -> (N, D)."""
        self.eval()
        X = torch.from_numpy(images.astype(np.float32)).unsqueeze(1)
        z = self.context(X)                               # (N,D,G,G)
        return z.mean(dim=(2, 3)).cpu().numpy()


def embed_images(paths: List[str], epochs: int = 50, seed: int = SEED) -> Tuple[np.ndarray, List[str], dict]:
    """Train an I-JEPA on ALL glyph images (self-supervised, no labels), embed them.

    Returns (matrix NxD, paths, meta).  Training uses both scripts' pixels (the
    encoder is script-agnostic and unsupervised); labels are never seen, so the
    downstream validations remain non-circular.
    """
    if not TORCH_OK:
        raise RuntimeError(f"torch unavailable: {_IMPORT_ERR}")
    from palaeo.palaeo_common import load_image
    imgs = np.stack([load_image(p) for p in paths])
    model = IJEPA()
    model.train_on(imgs, epochs=epochs, seed=seed)
    E = model.embed(imgs)
    meta = {"arch": "ConvEncoder(4x stride2, D=128) + Predictor(3x conv), EMA tau=0.99",
            "method": "I-JEPA (Assran et al. 2023, arXiv:2301.08243)",
            "epochs": epochs, "n_images": len(paths), "embed_dim": E.shape[1],
            "masking": "input-space patch erasure (CNN backbone adaptation)",
            "objective": "latent-target MSE, stop-grad EMA target, non-contrastive"}
    return E, list(paths), meta


class JepaEmbedder:
    """Train I-JEPA ONCE on a base corpus; embed ANY paths (incl. damaged) in that
    learned space.  Mirrors ClassicalEmbedder's fit/embed interface so the two
    representations are interchangeable in validate.py."""

    def __init__(self, epochs: int = 50, seed: int = SEED):
        if not TORCH_OK:
            raise RuntimeError(f"torch unavailable: {_IMPORT_ERR}")
        self.epochs = epochs
        self.seed = seed
        self.model: "IJEPA" = None
        self.meta: dict = {}

    def fit(self, paths: List[str]) -> "JepaEmbedder":
        from palaeo.palaeo_common import load_image
        imgs = np.stack([load_image(p) for p in paths])
        self.model = IJEPA()
        self.model.train_on(imgs, epochs=self.epochs, seed=self.seed)
        self.meta = {"method": "I-JEPA (Assran et al. 2023, arXiv:2301.08243)",
                     "epochs": self.epochs, "n_train": len(paths),
                     "embed_dim": D,
                     "objective": "latent-target MSE, stop-grad EMA target, non-contrastive"}
        return self

    def embed(self, paths: List[str]) -> np.ndarray:
        from palaeo.palaeo_common import load_image
        imgs = np.stack([load_image(p) for p in paths])
        return self.model.embed(imgs)


if __name__ == "__main__":
    if not TORCH_OK:
        print("torch unavailable -- pipeline will use classical features:", _IMPORT_ERR)
        sys.exit(0)
    from palaeo.palaeo_common import list_a_images, list_b_images
    paths = [p for _, p in list_a_images()] + [p for _, p in list_b_images()]
    E, _, meta = embed_images(paths, epochs=20)
    print("I-JEPA embed:", E.shape, meta)
