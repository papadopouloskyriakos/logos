"""Regression tests for scripts.palaeo.font_control — the cross-script font-swap confound control.

Pins the properties the pre-submission review (P2) demanded of the control:

  1. PARAMETRIC RENDERING -- render_glyph honours an alternate font_path, and the two Noto faces
     are single-script (NotoA draws Linear A but NOT Linear B, and vice-versa), which is what makes
     the swap a genuine two-independent-designers control rather than a restyle.
  2. STRUCTURE + MECHANICAL VERDICT -- run() emits both conditions, a delta with a chance floor,
     and a font_confound_verdict/residual_confound computed mechanically (never by a model).
  3. HONEST LABEL -- the artifact is labelled an engineering demonstration, and the residual
     graphic-genealogy circularity is stated (so the leg cannot masquerade as an offensive positive).

Skips cleanly when the licensed sign corpus or the Noto fonts are absent (as the other palaeo
tests skip on a missing render corpus), so the suite stays green in a fonts-only checkout.

Run:
    pytest tests/test_font_control.py -v
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from palaeo import font_control as fc  # noqa: E402
from palaeo.render_signs import render_glyph  # noqa: E402

_HAVE_FONTS = all(os.path.exists(p) for p in (fc.AEGEAN, fc.NOTO_A, fc.NOTO_B))
_HAVE_CORPUS = os.path.exists(os.path.join(os.path.dirname(__file__), "..",
                                           "scripts", "cross_script", "results_ab.json"))
_skip = pytest.mark.skipif(not (_HAVE_FONTS and _HAVE_CORPUS),
                           reason="Noto fonts or licensed sign corpus absent")


@_skip
def test_render_glyph_honours_alternate_font_and_noto_is_single_script():
    # Linear A block U+10600-U+1077F ; Linear B syllabary+ideograms U+10000-U+100FF.
    # Single-script property is a CMAP fact (PIL renders a .notdef box for absent codepoints,
    # so ink>0 is not a coverage signal -- the control checks the real cmap, see fc._font_cmap).
    cmap_a = fc._font_cmap(fc.NOTO_A)
    cmap_b = fc._font_cmap(fc.NOTO_B)
    cmap_ae = fc._font_cmap(fc.AEGEAN)
    a_block = lambda cm: any(0x10600 <= c <= 0x1077F for c in cm)
    b_block = lambda cm: any(0x10000 <= c <= 0x100FF for c in cm)
    # NotoA draws Linear A and NOT Linear B; NotoB the reverse -> two independent single-script faces.
    assert a_block(cmap_a) and not b_block(cmap_a)
    assert b_block(cmap_b) and not a_block(cmap_b)
    # Aegean (the confounded baseline face) draws BOTH scripts.
    assert a_block(cmap_ae) and b_block(cmap_ae)
    # render_glyph honours the font_path argument for an in-cmap glyph (Linear A DA = U+10608).
    assert render_glyph(0x10608, font_path=fc.NOTO_A).sum() > 0


@_skip
def test_run_structure_and_mechanical_verdict():
    out = fc.run(n_splits=15, seed=fc.SEED)
    # both conditions present, each far above its chance floor (the pipeline recovers anchors)
    for name in ("aegean_baseline", "noto_crossfont"):
        c = out["conditions"][name]
        assert c["direct_nn"]["mean"] > c["chance_floor"] * 3
        assert 0.0 <= c["direct_nn"]["mean"] <= 1.0
    d = out["delta"]["direct_nn"]
    assert "abs_drop" in d and "frac_retained" in d and "control_beats_chance" in d
    # the mechanical honesty verdict is a string, computed here (not by any model)
    assert isinstance(out["font_confound_verdict"], str) and out["font_confound_verdict"]
    assert isinstance(out["residual_confound"], str) and "circular" in out["residual_confound"].lower()
    # honest label: an engineering demonstration, NOT an archaeological positive
    assert "not an archaeological positive" in out["label"].lower()


@_skip
def test_control_is_deterministic_for_a_fixed_seed():
    a = fc.run(n_splits=12, seed=fc.SEED)["delta"]["direct_nn"]["noto_crossfont"]
    b = fc.run(n_splits=12, seed=fc.SEED)["delta"]["direct_nn"]["noto_crossfont"]
    assert a == b
