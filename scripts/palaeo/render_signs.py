#!/usr/bin/env python3
"""render_signs.py -- render Linear-A (+ Linear-B) sign GLYPH images to corpus/bronze.

IMAGE SOURCE (documented, reproducible, gitignored under corpus/bronze):
  * Font        : Aegean.ttf by George Douros (UFAS license), vendored at
                  corpus/bronze/fonts/Aegean.ttf.  Covers BOTH the Linear A
                  (U+10600) and Linear B (U+10000) Unicode blocks.  Using ONE font
                  for both scripts is deliberate: cross-script embedding distances
                  then reflect real GLYPH-SHAPE differences, not font-style noise.
                  (License caveat: Douros tightened UFAS terms in 2024; this font is
                  a research tool held in the gitignored bronze tier, not redistributed.)
  * Linear A id: codepoint->value from lineara.xyz ``ideograms.js``
                  (``ideogram_to_ascii``) -- the AUTHORITATIVE editorial map.  We do
                  not derive values; we inherit them.
  * Linear B id: codepoint->value from the official Unicode character NAME
                  (``LINEAR B SYLLABLE B<hex> <VAL>``), identical to the Track B bridge.

Each sign is rendered at high resolution, ink-bbox-cropped, margin-padded to a square,
and LANCZOS-resized to 96x96 grayscale (ink = bright, anti-aliased -- sub-pixel shape
information is preserved for HOG and for the I-JEPA encoder).

A manifest JSON records source, counts, and the shared (anchor) values.

Usage:  python3 scripts/palaeo/render_signs.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palaeo.palaeo_common import (  # noqa: E402
    FONT_PATH, LIN_A_DIR, LIN_B_DIR, SIGN_IMG_DIR, IMG_SIZE, SEED,
    CONSERVATIVE_INV, ONTOLOGY, load_linA_codepoint_map, load_linB_value_map,
    load_anchors, norm_token,
)

RENDER_AT = 220          # high-res glyph render, then crop+downscale (anti-aliased)
CANVAS = 256
MARGIN_FRAC = 0.10       # of the cropped glyph dimension


def _font(font_path: str = FONT_PATH) -> ImageFont.FreeTypeFont:
    if not os.path.exists(font_path):
        raise FileNotFoundError(
            f"font missing at {font_path}. The default Aegean.ttf is fetchable from "
            "https://raw.githubusercontent.com/deepin-community/ttf-ancient-fonts/master/Aegean.ttf")
    return ImageFont.truetype(font_path, RENDER_AT)


def render_glyph(codepoint: int, font_path: str = FONT_PATH) -> np.ndarray:
    """Render one Unicode sign to a normalized IMG_SIZE x IMG_SIZE float64 [0,1] array.

    ink = high values (background = 0).  Glyph is ink-bbox-cropped, centered with a
    margin, and resized LANCZOS so stroke anti-aliasing carries shape information.

    ``font_path`` selects the typeface.  It defaults to the comprehensive Aegean face
    (which draws BOTH Linear A and Linear B); pass an alternate face to run the
    font-swap confound control (scripts/palaeo/font_control.py) — e.g. Noto Sans
    Linear A for A glyphs and Noto Sans Linear B for B glyphs, two independent type
    designers, so a surviving cross-script alignment cannot be one designer's style.
    """
    f = _font(font_path)
    img = Image.new("L", (CANVAS, CANVAS), 0)            # black bg
    d = ImageDraw.Draw(img)
    ch = chr(codepoint)
    # center the glyph's bbox in the canvas
    try:
        bbox = d.textbbox((0, 0), ch, font=f)            # (l,t,r,b)
    except Exception:
        bbox = f.getbbox(ch)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if w <= 0 or h <= 0:                                  # blank glyph -> skip sentinel
        return np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.float64)
    tx = (CANVAS - w) / 2 - bbox[0]
    ty = (CANVAS - h) / 2 - bbox[1]
    img = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(img).text((tx, ty), ch, font=f, fill=255)
    # ink-bbox crop
    arr = np.asarray(img)
    ys, xs = np.where(arr > 0)
    if len(xs) == 0:
        return np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.float64)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = img.crop((x0, y0, x1, y1))
    gw, gh = crop.size
    m = int(max(gw, gh) * MARGIN_FRAC) + 2
    side = max(gw, gh) + 2 * m
    sq = Image.new("L", (side, side), 0)
    sq.paste(crop, ((side - gw) // 2, (side - gh) // 2))
    out = sq.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
    return np.asarray(out, dtype=np.float64) / 255.0


def _save(arr: np.ndarray, path: str) -> None:
    Image.fromarray((arr * 255).astype(np.uint8)).save(path)


def main() -> dict:
    np.random.seed(SEED)
    for d in (LIN_A_DIR, LIN_B_DIR):
        os.makedirs(d, exist_ok=True)

    # ---- Linear A: the BOUNDED palaeographic probe = the conservative syllabogram
    # inventory (~92 attested signs: AB values + the *-series that survive cleaning).
    # Logograms / unattested dross are deliberately excluded.  We ALSO render any
    # attested ALLOGRAPH-VARIANT sign (e.g. *131B/*131C, *309B/*309C) even though the
    # conservative builder deduped variants to their base -- these are real signs with
    # codepoints, needed for the allograph-clustering validation (a).
    a_map = load_linA_codepoint_map()                    # {cp: value}
    inv = {norm_token(t) for t in json.load(open(CONSERVATIVE_INV))["inventory"]}
    # add allograph-variant members from the ontology
    import collections as _c
    ont = json.load(open(ONTOLOGY))
    fam = _c.defaultdict(list)
    for tok, info in ont.items():
        if info.get("allograph_family"):
            fam[info["allograph_family"]].append(norm_token(tok))
    for f, toks in fam.items():
        if len(toks) >= 2:                               # multi-member family -> keep variants
            inv.update(toks)

    a_rendered, a_skipped_blank = {}, 0
    for cp, val in sorted(a_map.items()):
        if val not in inv:                               # bounded probe: conservative inv only
            continue
        arr = render_glyph(cp)
        if arr.sum() == 0:
            a_skipped_blank += 1
            continue
        _save(arr, os.path.join(LIN_A_DIR, f"{val}.png"))
        a_rendered[val] = cp

    # ---- Linear B: every syllable codepoint with a parseable value
    b_map = load_linB_value_map()
    b_rendered, b_skipped_blank = {}, 0
    b_value_seen = set()
    for cp, val in sorted(b_map.items()):
        if val in b_value_seen:
            continue
        arr = render_glyph(cp)
        if arr.sum() == 0:
            b_skipped_blank += 1
            continue
        _save(arr, os.path.join(LIN_B_DIR, f"{val}.png"))
        b_rendered[val] = cp
        b_value_seen.add(val)

    anchors, nB_seq, chance_seq, _ = load_anchors()
    shared = sorted(set(a_rendered) & set(b_rendered) & set(anchors))
    shared_all = sorted(set(a_rendered) & set(b_rendered))

    manifest = {
        "seed": SEED,
        "img_size": IMG_SIZE,
        "font": {"path": FONT_PATH, "name": "Aegean (George Douros, UFAS)",
                 "license_caveat": "UFAS; tightened 2024; gitignored bronze, research-only, not redistributed"},
        "linA_source": "lineara.xyz ideograms.js ideogram_to_ascii (codepoint->value), parsed live",
        "linB_source": "Unicode character names (LINEAR B SYLLABLE B<hex> <VAL>)",
        "linA": {"n": len(a_rendered), "dir": LIN_A_DIR, "skipped_blank": a_skipped_blank},
        "linB": {"n": len(b_rendered), "dir": LIN_B_DIR, "skipped_blank": b_skipped_blank},
        "shared_values_all": shared_all,
        "shared_anchors_trackB": shared,
        "n_shared_anchors": len(shared),
        "nB_image_pool": len(b_rendered),                # B-side pool for image alignment
        "chance_floor_image": 1.0 / max(len(b_rendered), 1),
        "trackB_chance_floor_seq": chance_seq,
        "trackB_nB_seq": nB_seq,
    }
    mpath = os.path.join(SIGN_IMG_DIR, "manifest.json")
    json.dump(manifest, open(mpath, "w"), indent=1)
    print(f"[render] Linear A signs : {len(a_rendered)}  (skipped {a_skipped_blank} blank)")
    print(f"[render] Linear B signs : {len(b_rendered)}  (skipped {b_skipped_blank} blank)")
    print(f"[render] shared anchors : {len(shared)} / 55 (Track B)")
    print(f"[render] image chance   : 1/{len(b_rendered)} = {manifest['chance_floor_image']:.5f}")
    print(f"[render] manifest       : {mpath}")
    return manifest


if __name__ == "__main__":
    main()
