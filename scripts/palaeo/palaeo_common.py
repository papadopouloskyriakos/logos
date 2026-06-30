"""palaeo_common.py -- shared paths, seeding, IO, and a self-contained resource guard.

The guard mirrors the agora_guard pattern (CLAUDE.md, IFRNLLEI01PRD-1419): cap BLAS
threads, optionally RLIMIT_AS so a runaway never OOMs the LXC.  logos has no agora
package importable, so this is a small local stand-in (documented, stdlib-only).
"""
from __future__ import annotations

import json
import os
import re
import resource
from typing import Dict, List, Tuple

import numpy as np

# --------------------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # .../logos
BRONZE = os.path.join(ROOT, "corpus", "bronze")
SILVER = os.path.join(ROOT, "corpus", "silver")

FONT_PATH = os.path.join(BRONZE, "fonts", "Aegean.ttf")          # George Douros, UFAS
SIGN_IMG_DIR = os.path.join(BRONZE, "sign_images")
LIN_A_DIR = os.path.join(SIGN_IMG_DIR, "linA")
LIN_B_DIR = os.path.join(SIGN_IMG_DIR, "linB")
DAMAGED_DIR = os.path.join(SIGN_IMG_DIR, "damaged")              # synthetic damaged forms

LIN_A_MAP = os.path.join(BRONZE, "palaeo", "linA_codepoint_map.json")
IDEOGRAMS_JS = "/tmp/lineara/ideograms.js"                       # authoritative source (lineara.xyz)

ONTOLOGY = os.path.join(SILVER, "signs_ontology.json")
CONSERVATIVE_INV = os.path.join(SILVER, "inventory_syllabograms_conservative.json")
RESULTS_AB = os.path.join(ROOT, "scripts", "cross_script", "results_ab.json")

IMG_SIZE = 96                                                   # glyph canvas (square)
SEED = 20260630                                                 # matches Track B seed

# subscript digits -> ASCII (same rule as cross_script/data.py::_norm_a_token)
_SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def norm_token(t: str) -> str:
    """Normalize an editorial value token: strip GORILA damage masks, ASCII digits."""
    return re.sub(r"[\[\]\?]", "", t.translate(_SUB)).strip()


# --------------------------------------------------------------------------- guard
def bound(level: str = "medium") -> None:
    """Cap BLAS threads + address space.  Levels: light(3G) medium(6G) heavy(10G).

    Cheap insurance so a torch/BLAS runaway cannot OOM the host (the 2026-06-25
    finops-agora incident was an uncapped research job).  No-op-safe if it fails.
    """
    limits = {"light": 3, "medium": 6, "heavy": 10, "extreme": 12}
    gb = limits.get(level, 6)
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "TORCH_NUM_THREADS"):
        os.environ.setdefault(var, "4")
    try:
        import torch as _t  # noqa
        _t.set_num_threads(4)
    except Exception:
        pass
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        want = gb * (1024 ** 3)
        if hard == resource.RLIM_INFINITY or want < hard:
            resource.setrlimit(resource.RLIMIT_AS, (min(want, hard) if hard != resource.RLIM_INFINITY else want, hard))
    except Exception:
        pass


# --------------------------------------------------------------------------- IO
def load_linA_codepoint_map() -> Dict[int, str]:
    """Linear A Unicode codepoint -> editorial value (normalized ASCII token).

    Source of truth = lineara.xyz ``ideograms.js`` (``ideogram_to_ascii``), parsed
    live when /tmp/lineara is present; else the gitignored bronze fixture (rebuilt
    from the same source).  This is the AUTHORITATIVE sign->value map for Linear A;
    we do NOT invent it.
    """
    mp: Dict[int, str] = {}
    if os.path.exists(IDEOGRAMS_JS):
        src = open(IDEOGRAMS_JS, encoding="utf-8").read()
        for glyph, val in re.findall(r'\["(.)","([^"]+)"\]', src):
            mp[ord(glyph)] = norm_token(val)
    elif os.path.exists(LIN_A_MAP):
        raw = json.load(open(LIN_A_MAP, encoding="utf-8"))["linA_cp2val"]
        mp = {int(k): v for k, v in raw.items()}
    else:
        raise FileNotFoundError(
            "Linear A codepoint map missing: need /tmp/lineara/ideograms.js or "
            f"{LIN_A_MAP}")
    # dedup: one codepoint per value (keep smallest codepoint = canonical form)
    best: Dict[str, int] = {}
    for cp, v in mp.items():
        if v not in best or cp < best[v]:
            best[v] = cp
    return {cp: v for v, cp in best.items()}


def load_linB_value_map() -> Dict[int, str]:
    """Linear B syllable codepoint -> uppercase value, via the official Unicode name.

    e.g. 'LINEAR B SYLLABLE B039 RA' -> 'RA'.  Identical parsing to
    cross_script/data.py::_b_value_from_codepoint (the Track B bridge).
    """
    import unicodedata
    mp: Dict[int, str] = {}
    for cp in range(0x10000, 0x10050):
        try:
            nm = unicodedata.name(chr(cp))
        except ValueError:
            continue
        m = re.match(r"LINEAR B SYLLABLE B[0-9A-F]+ (\S+)", nm)
        if m:
            mp[cp] = norm_token(m.group(1))
    return mp


def load_image(path: str) -> np.ndarray:
    """Load a sign PNG as float64 grayscale [0,1], ink = high values."""
    from PIL import Image
    a = np.asarray(Image.open(path).convert("L"), dtype=np.float64)
    return a / 255.0


def list_a_images() -> List[Tuple[str, str]]:
    """[(value, path)] for every rendered Linear A sign."""
    out = []
    if os.path.isdir(LIN_A_DIR):
        for f in sorted(os.listdir(LIN_A_DIR)):
            if f.endswith(".png"):
                out.append((os.path.splitext(f)[0], os.path.join(LIN_A_DIR, f)))
    return out


def list_b_images() -> List[Tuple[str, str]]:
    out = []
    if os.path.isdir(LIN_B_DIR):
        for f in sorted(os.listdir(LIN_B_DIR)):
            if f.endswith(".png"):
                out.append((os.path.splitext(f)[0], os.path.join(LIN_B_DIR, f)))
    return out


def load_anchors() -> Tuple[List[str], int, float, dict]:
    """Track B's anchor set + chance floor + sequence-null recovery (for comparison).

    Returns (anchors, nB_seq, chance_floor_seq, seq_null_summary).
    nB_seq/chance come from results_ab.json so the IMAGE result is reported against
    the IDENTICAL chance floor Track B used.
    """
    r = json.load(open(RESULTS_AB, encoding="utf-8"))
    anchors = r["data"]["anchors"]
    rec = r["recovery"]
    chance = rec["random_chance"]["chance_analytic"]      # 1/nB_seq
    nB = rec["random_chance"]["nB"]
    seq_null = {m: rec[m]["mean"] for m in rec}
    return anchors, nB, chance, seq_null
