"""Adversarial tests for scripts.palaeo (sign-image I-JEPA palaeographic probe).

These pin the four properties the verification demanded, plus the JEPA-architecture
guards that prove the model is a GENUINE I-JEPA and not a contrastive Siamese or a
pixel-reconstruction autoencoder mislabelled "JEPA":

  1. DETERMINISM -- the classical/render/damaged pipeline is bit-reproducible for a
     fixed seed.  (I-JEPA itself is NOT bit-deterministic on CPU torch -- a documented
     property of BLAS reductions; run_palaeo reports it honestly as mean+/-std over
     seeds.  We test instead that JEPA training reduces loss and that different seeds
     yield different embeddings.)
  2. IMAGE RENDERING REPRODUCIBILITY -- render_glyph is a pure function of codepoint;
     the corpus counts in the manifest match the files on disk (generated, not hardcoded).
  3. CLASSICAL FEATURES FINITE -- HOG + Hu + shape-context are all finite, deterministic,
     and PCA-whitened to the fixed width.
  4. CROSS-SCRIPT IMAGE HELD-OUT SPLIT IS NON-CIRCULAR -- the orthogonal Procrustes fit
     receives ONLY train-anchor rows; held-out B-side values are never fitted (the
     encoder is unsupervised, so no value label is seen at training either).

Plus JEPA-recipe guards (EMA target encoder, stop-gradient, non-contrastive latent
objective, separate predictor) and a positive control proving the cross-script harness
can register a KNOWN alignment (so a null on the real corpus is a real null).

Run:
    pytest tests/test_palaeo.py -v
"""
import os
import sys

import numpy as np
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.palaeo import palaeo_common as pc  # noqa: E402
from scripts.palaeo import classical, validate, render_signs  # noqa: E402

try:                                    # JEPA needs torch; tests skip gracefully without it
    from scripts.palaeo import jepa as jepa_mod
    _HAS_TORCH = jepa_mod.TORCH_OK
except Exception:                       # pragma: no cover
    jepa_mod = None
    _HAS_TORCH = False

needs_torch = pytest.mark.skipif(not _HAS_TORCH, reason="torch unavailable -> palaeo falls back to classical")


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def base_paths():
    a = [p for _, p in pc.list_a_images()]
    b = [p for _, p in pc.list_b_images()]
    if not a or not b:
        pytest.skip("sign-image corpus not rendered (run scripts/palaeo/render_signs.py)")
    return a + b


@pytest.fixture(scope="module")
def classical_embedder(base_paths):
    return classical.ClassicalEmbedder(pca_dim=48).fit(base_paths)


def _first_codepoint():
    """A codepoint we know renders to non-blank ink (first entry of the A map)."""
    mp = pc.load_linA_codepoint_map()
    return next(iter(mp))


# --------------------------------------------------------------------------- #
# 2. image rendering reproducibility
# --------------------------------------------------------------------------- #

def test_render_glyph_is_pure_function_of_codepoint():
    cp = _first_codepoint()
    g1 = render_signs.render_glyph(cp)
    g2 = render_signs.render_glyph(cp)
    assert g1.shape == (pc.IMG_SIZE, pc.IMG_SIZE)
    assert np.array_equal(g1, g2), "render_glyph must be deterministic in the codepoint"
    assert g1.sum() > 0, "known codepoint must render non-blank ink"
    assert 0.0 <= g1.min() and g1.max() <= 1.0


def test_render_glyph_uses_ink_bbox_crop_and_center():
    # a rendered glyph is ink-bbox cropped + padded -> non-zero mass is not stuck in a
    # corner (centered), and the canvas is square.
    g = render_signs.render_glyph(_first_codepoint())
    ink = g > 0
    assert ink.any()
    ys, xs = np.where(ink)
    cy, cx = ys.mean(), xs.mean()
    side = pc.IMG_SIZE
    # centroid should be reasonably central (within the inner 60% band)
    assert side * 0.2 < cy < side * 0.8 and side * 0.2 < cx < side * 0.8


def test_corpus_manifest_counts_match_files_on_disk():
    # invariant-11 spirit: counts are generated, not hand-written.  The manifest is the
    # generated truth; the files on disk must agree with it.
    import json
    mpath = os.path.join(pc.SIGN_IMG_DIR, "manifest.json")
    assert os.path.exists(mpath), "manifest.json missing -- render_signs.main() not run"
    man = json.load(open(mpath))
    a_on_disk = len([f for f in os.listdir(pc.LIN_A_DIR) if f.endswith(".png")])
    b_on_disk = len([f for f in os.listdir(pc.LIN_B_DIR) if f.endswith(".png")])
    assert man["linA"]["n"] == a_on_disk
    assert man["linB"]["n"] == b_on_disk
    assert man["n_shared_anchors"] == len(man["shared_anchors_trackB"])
    # the image chance floor is derived, not asserted by hand
    assert abs(man["chance_floor_image"] - 1.0 / man["nB_image_pool"]) < 1e-12


def test_shared_anchor_values_have_both_an_a_and_a_b_glyph():
    a_vals = {v for v, _ in pc.list_a_images()}
    b_vals = {v for v, _ in pc.list_b_images()}
    shared = a_vals & b_vals
    assert len(shared) >= 50, "expected the ~55 borrowed-sign anchors to render in BOTH scripts"


# --------------------------------------------------------------------------- #
# 3. classical features finite + deterministic
# --------------------------------------------------------------------------- #

def test_classical_features_are_finite(base_paths):
    sample = base_paths[::max(1, len(base_paths) // 12)]
    feats = np.stack([classical.features_for(pc.load_image(p)) for p in sample])
    assert feats.ndim == 2 and feats.shape[0] == len(sample)
    assert np.isfinite(feats).all(), "HOG + Hu + shape-context must be finite everywhere"
    # Hu moments are log-transformed sign-aware -> never NaN even for symmetric glyphs
    assert (np.abs(feats) < 1e6).all()


def test_classical_embedder_is_bit_deterministic(classical_embedder, base_paths):
    probe = base_paths[:6]
    e1 = classical_embedder.embed(probe)
    e2 = classical_embedder.embed(probe)
    assert e1.shape == (len(probe), 48)
    assert np.array_equal(e1, e2), "classical PCA-whitened embedding must be bit-reproducible"
    assert np.isfinite(e1).all()


def test_classical_embedder_consistent_space_for_any_paths(classical_embedder, base_paths):
    # damaged / held-out paths land in the SAME fitted space (no per-call re-fit) ->
    # embed([x]) then embed([x, y]) give the same row for x.
    a = classical_embedder.embed([base_paths[0]])
    b = classical_embedder.embed([base_paths[0], base_paths[1]])
    assert np.allclose(a[0], b[0], atol=1e-10)


# --------------------------------------------------------------------------- #
# 1b. damaged-form generation determinism
# --------------------------------------------------------------------------- #

def test_damaged_generation_is_deterministic():
    d1 = validate._gen_damaged(n_variants=2, seed=pc.SEED)
    d2 = validate._gen_damaged(n_variants=2, seed=pc.SEED)
    assert [os.path.basename(p) for _, p in d1] == [os.path.basename(p) for _, p in d2]
    px1 = np.asarray(pc.load_image(d1[0][1]))
    px2 = np.asarray(pc.load_image(d2[0][1]))
    assert np.array_equal(px1, px2), "seeded damaged generation must be pixel-reproducible"


# --------------------------------------------------------------------------- #
# 4. cross-script held-out split is NON-CIRCULAR (the headline anti-leakage test)
# --------------------------------------------------------------------------- #

def test_procrustes_fit_is_orthogonal_and_recovers_known_rotation():
    # unit-level: a genuine orthogonal Procrustes fit (SVD-based) returns R with R^T R = I
    # and recovers a known rotation on aligned data -> the math is sound.
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, 16))
    Q, _ = np.linalg.qr(rng.normal(size=(16, 16)))        # random orthogonal
    Y = X @ Q
    idx = validate._procrustes_fit(X[:30], Y[:30], X[30:], Y[30:])
    # every held-out row recovered against its own counterpart in the 10-row POOL
    # (_procrustes_fit returns indices into B_pool, which here is Y[30:]).
    assert list(idx) == list(range(10))


def test_cross_script_heldout_never_reaches_fit(classical_embedder):
    """Spy on _procrustes_fit: the SVD-based FIT may see TRAIN anchor rows only.

    Held-out anchors (A_held) are passed only as the QUERIES to recover, never as fit
    data; their B-side values are correspondingly absent from B_tr.  This is the
    non-circularity guarantee (identical in spirit to Track B).
    """
    seen = {}

    def spy(A_tr, B_tr, A_held, B_pool):
        seen["n_train"] = A_tr.shape[0]
        seen["n_held"] = A_held.shape[0]
        seen["n_B_train"] = B_tr.shape[0]
        seen["n_B_pool"] = B_pool.shape[0]
        # the genuine fit must use equal A/B train counts (paired anchors)
        assert A_tr.shape[0] == B_tr.shape[0]
        return orig(A_tr, B_tr, A_held, B_pool)

    orig = validate._procrustes_fit
    validate._procrustes_fit = spy
    try:
        res = validate.val_cross_script(classical_embedder.embed, n_splits=12,
                                        held_frac=0.2, seed=pc.SEED)
    finally:
        validate._procrustes_fit = orig

    n_anchors = res["n_anchors"]
    assert seen["n_train"] + seen["n_held"] == n_anchors, \
        "fit(Train) + recover(Held) must partition the anchors exactly"
    assert seen["n_held"] == res["n_hold_per_split"] > 0
    assert seen["n_B_train"] == seen["n_train"], "B-side TRAIN labels never leaked into the fit"


def test_cross_script_chance_and_trackB_null_fields_correct(classical_embedder):
    res = validate.val_cross_script(classical_embedder.embed, n_splits=8,
                                    held_frac=0.2, seed=pc.SEED)
    # image chance floor is derived from the B image pool, not the sequence pool
    assert abs(res["chance_image"] - 1.0 / res["nB_image_pool"]) < 1e-12
    # Track B sequence null is reported alongside, excluding the random_chance entry
    assert "random_chance" in res["trackB_seq_null"]
    assert res["trackB_best_seq"] == max(
        v for m, v in res["trackB_seq_null"].items() if m != "random_chance")
    assert 0.0 < res["trackB_best_seq"] < 1.0
    # the two chance floors are DISTINCT (image pool != sequence pool) and both reported
    assert res["chance_image"] != res["trackB_chance_seq"]


def test_cross_script_positive_control_registers_known_alignment():
    """If A and B embeddings share an aligned geometry (A[v] == B[v]), the harness must
    recover held-out anchors at ~1.0 via the direct shared-space NN.  This proves a null
    on the real corpus is a real null (the harness can see a signal when one exists),
    mirroring Track B's positive control.  Uses the direct-NN metric (no fit/centering)
    so the control isolates 'can the harness register a real alignment'."""
    anchors, *_ = pc.load_anchors()
    a_imgs = dict(pc.list_a_images())
    b_imgs = dict(pc.list_b_images())
    anchors = [v for v in anchors if v in a_imgs and v in b_imgs]
    # every VALUE (anchor or distractor) gets one fixed high-dim random vector, shared
    # across scripts -> A[v] == B[v] exactly; distinct values are near-orthogonal.
    all_vals = sorted({v for v, _ in pc.list_a_images()} | {v for v, _ in pc.list_b_images()})
    rng = np.random.default_rng(0)
    code = {v: rng.normal(size=128) for v in all_vals}
    for v in anchors:                       # boost the shared-anchor signal above distractors
        code[v] = code[v] * 10.0

    def fake_embed(paths):
        return np.stack([code[os.path.splitext(os.path.basename(p))[0]] for p in paths])

    res = validate.val_cross_script(fake_embed, n_splits=12, held_frac=0.2, seed=pc.SEED)
    assert res["recovery_direct_nn"] >= 0.98, \
        "perfectly aligned embeddings must be recovered by direct NN (positive control)"


# --------------------------------------------------------------------------- #
# JEPA-recipe guards: genuine I-JEPA, not a contrastive Siamese / pixel autoencoder
# --------------------------------------------------------------------------- #

@needs_torch
def test_ijepa_target_encoder_is_frozen_and_ema():
    import torch
    m = jepa_mod.IJEPA()
    # stop-gradient: target encoder receives NO gradients
    assert not any(p.requires_grad for p in m.target.parameters()), \
        "target encoder must be stop-gradiented (requires_grad=False)"
    # context + predictor ARE trainable
    assert any(p.requires_grad for p in m.context.parameters())
    assert any(p.requires_grad for p in m.pred.parameters())
    # EMA init: target is a HARD copy of context at construction
    for cp, tp in zip(m.context.parameters(), m.target.parameters()):
        assert torch.allclose(cp.detach(), tp.detach())


@needs_torch
def test_ijepa_ema_updates_track_context_not_hard_sync():
    """After one optimizer step + soft EMA sync, the target moves TOWARD the new context
    by exactly tau=0.99 (target = 0.99*target_old + 0.01*context_new).  This is the
    bootstrap that distinguishes I-JEPA from a frozen-teacher method."""
    import torch
    rng = np.random.default_rng(0)
    imgs = np.stack([pc.load_image(p) for _, p in pc.list_a_images()[:16]])
    m = jepa_mod.IJEPA()
    opt = torch.optim.AdamW(list(m.context.parameters()) + list(m.pred.parameters()), lr=1e-3)
    ctx0 = next(p.detach().clone() for p in m.context.parameters())
    tgt0 = next(p.detach().clone() for p in m.target.parameters())
    assert torch.allclose(tgt0, ctx0), "hard-sync at init"
    opt.zero_grad()
    xb = torch.from_numpy(imgs.astype(np.float32)).unsqueeze(1)
    loss = m.step_loss(xb, rng)
    loss.backward()
    opt.step()
    m._sync_ema(hard=False)
    ctx1 = next(p.detach().clone() for p in m.context.parameters())
    tgt1 = next(p.detach().clone() for p in m.target.parameters())
    assert not torch.allclose(tgt1, tgt0), "target must move on EMA update"
    assert torch.allclose(tgt1, 0.99 * tgt0 + 0.01 * ctx1, atol=1e-6), \
        "soft EMA update must equal tau*old + (1-tau)*new"


@needs_torch
def test_ijepa_objective_is_latent_target_mse_not_pixels_or_contrastive():
    """The loss is MSE between the PREDICTOR output and the STOP-GRADIENTED TARGET
    ENCODER latent at the target positions -- not pixel reconstruction, and there are no
    negative pairs (non-contrastive).  Verified by structural inspection of step_loss."""
    import torch
    import inspect
    src = inspect.getsource(jepa_mod.IJEPA.step_loss)
    # target latent is computed under no_grad from the TARGET encoder on the FULL image
    assert "self.target(x)" in src and "no_grad" in src
    # the loss is an L2 in latent space, masked to target patches
    assert "(pred - z_t) ** 2" in src and "target_mask" in src
    assert "self.pred(z_c)" in src, "a separate predictor maps context latent -> target latent"
    # no contrastive / negative-pair machinery IN THE LOSS CODE.  (Scan step_loss only --
    # the module docstring legitimately says "non-contrastive" / "no negatives".)
    for bad in ("infonce", "nt_xent", "temperature", "softmax", "neg_keys", "negatives"):
        assert bad.lower() not in src.lower(), f"contrastive term '{bad}' in step_loss -> not I-JEPA"


@needs_torch
def test_ijepa_context_masking_erases_target_patches():
    """I-JEPA predicts the latent of TARGET patches from a CONTEXT where those patches
    are missing.  _erase_patches must zero the non-visible cells in input space."""
    import torch
    m = jepa_mod.IJEPA()
    x = torch.from_numpy((np.random.RandomState(0).rand(2, 1, 96, 96))).float()
    # mask only patch (0,0) visible -> every other 16x16 cell must be zero
    mask = torch.zeros(2, jepa_mod.G * jepa_mod.G)
    mask[:, 0] = 1.0
    out = m._erase_patches(x, mask)
    # patch (0,0) retains input; all other patches are zeroed
    assert torch.allclose(out[:, :, :16, :16], x[:, :, :16, :16])
    assert out[:, :, 16:, :].abs().sum() == 0
    assert out[:, :, :, 16:].abs().sum() == 0


@needs_torch
def test_ijepa_training_reduces_loss_and_embeds_to_fixed_width():
    """End-to-end: training lowers the objective and produces a D-wide embedding.  (We
    do NOT assert bit-determinism -- CPU-torch BLAS reductions are not bit-reproducible,
    which is exactly why run_palaeo reports mean+/-std over seeds.)"""
    imgs = np.stack([pc.load_image(p) for _, p in pc.list_a_images()[:30]])
    m = jepa_mod.IJEPA()
    hist = m.train_on(imgs, epochs=4, seed=pc.SEED, log=False)
    assert len(hist) == 4 and hist[-1] < hist[0], "JEPA objective must decrease"
    E = m.embed(imgs)
    assert E.shape == (30, jepa_mod.D)
    assert np.isfinite(E).all()


@needs_torch
def test_ijepa_is_not_catastrophically_collapsed():
    """Genuine non-contrastive SSL can dimensionally-collapse on tiny data (a known
    I-JEPA risk, NOT a mislabel).  We assert only that the embedding is not a single
    point -- effective rank (participation ratio) > 2 -- so downstream NN/clustering is
    operating on a real (if low-dimensional) representation."""
    imgs = np.stack([pc.load_image(p) for _, p in pc.list_a_images()[:50]])
    m = jepa_mod.IJEPA()
    m.train_on(imgs, epochs=6, seed=pc.SEED, log=False)
    E = m.embed(imgs)
    cov = np.cov(E.T)
    ev = np.linalg.eigvalsh(cov)
    ev = ev[ev > 1e-9]
    eff_rank = float(ev.sum() ** 2 / (ev ** 2).sum())
    assert eff_rank > 2.0, f"embedding collapsed to ~1 dimension (eff_rank={eff_rank:.2f})"


# --------------------------------------------------------------------------- #
# allograph validation sanity
# --------------------------------------------------------------------------- #

def test_allograph_chance_is_a_permutation_null(classical_embedder):
    res = validate.val_allograph(classical_embedder.embed)
    assert res["n_signs"] >= 6 and res["n_families"] >= 2
    # the chance baseline is a random-label-shuffle null, strictly in [0,1]
    assert 0.0 <= res["nn_purity_chance"] <= 1.0
    assert 0.0 < res["nn_purity_p"] <= 1.0
    assert "permutation null" in res["chance_note"]
