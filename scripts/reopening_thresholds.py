#!/usr/bin/env python3
"""reopening_thresholds.py — mechanical reopening tripwires for the closed Linear A routes.

Tsirkas-derived mechanism #1 (docs/2026-08-05-tsirkas-full-repo-audit.md, owner-directed
2026-08-05): adequacy counting + injection power curves run IN REVERSE — for each closed
analytical route, compute the corpus size / find-type at which the route becomes
re-runnable, converting "wait for more data" into mechanical tripwires wired to the
Anetaki II watch (docs/watch/anetaki_ii.md).

WHAT A THRESHOLD IS (and is not): a PLANNING number (L0 — no claim about Linear A is
made). A crossing means "the route is worth re-running under a NEW pre-registration";
it NEVER auto-generates a claim, never reopens a closed verdict by itself (Art. XVII),
and analogue (Linear B) thresholds are optimistic lower bounds — a crossing means
"re-runnable", never "identifiable".

The 7 routes (each keeps its native axis; conversion ratios stamped once in `units`):
  1 morphology       — LB document-subsample detection curve of the published bigram-floor
                       affix test (morphology.null_falsification on DĀMOS via
                       linb_morphology_control.load_linb).
  2 h2_entropy       — analytic: Heaps-fit sign-vocabulary growth vs bigram-cell coverage;
                       c_min calibrated from LB H2 stabilization (±0.05 bit); closed-form N*.
  3 alternation_grid — analytic birthday-problem model of S&M-shape word-final alternation
                       pairs over shared stems; threshold = E[grid-supported signs] >= G=10.
  4 vowel_harmony    — injection power curve on LA-matched synthetic corpora at kx scale,
                       planted P(V_i+1 = V_i) excess 0.15, within-form permutation null.
  5 phonology_cv     — the identical distributional C/V LOO-1NN test (phono_distributional)
                       on subsampled LB, where the labels are real; minimal detection size.
  6 segmentation     — LA descending-subsample boundary-recovery F1 curve, saturating fit,
                       extrapolation to the 0.62 supervised-headroom target (never a number
                       if the asymptote refuses one).
  7 anchors          — pure counting: independent 8-slot anchors from the phase-2 census,
                       lineage-collapsed via source_dependency (Art. XI); event tripwire.

STATUS vocabulary (mechanical, per route):
  MEASURED_ON_ANALOG — threshold measured on the LB analogue detection curve and ABOVE
                       LA's current size (a token-count tripwire exists).
  SIZE_NOT_BINDING   — the analogue detection threshold is at/below LA's current size:
                       corpus SIZE is not the binding constraint (the published LA null is
                       structural, e.g. short words); no token-count tripwire — the reopen
                       event is structural, stamped per route.
  ANALYTIC           — closed-form from fitted growth laws (assumptions stamped).
  EXTRAPOLATED       — saturating-fit extrapolation (route 6); never a measurement.
  ASYMPTOTE_LIMITED  — fitted asymptote below target: threshold REFUSED (None).
  UNREACHABLE_AT_CAP — analytic expectation does not reach target within the scan cap.
  EVENT_COUNT        — route 7: the threshold is an event count, not a corpus size.
  FIT_FAILED         — a curve fit did not converge; threshold None (fail soft, loud).

Constitution: Art. VIII (evidence sizing), Art. IX (info-budget panel per route, reported —
no graduating claim is made here), Art. XI (route 7 lineage collapse), Art. XVII
(append-only: no threshold reopens a closed verdict), Art. XXII (this header; the generated
doc repeats it). Invariant #12: every count in results/doc is produced by this script.
Does NOT import scripts.verdict (invariants 2/4).

Reuse: scripts/comparison/morphology.py (null_falsification, boundary_recovery, SignCodec,
PREREG_AFFIXES), scripts/comparison/linb_morphology_control.py (load_linb, MYC_AFFIXES),
scripts/comparison/phono_distributional.py (build_context_vectors, _loo_nn_accuracy,
_power_control, cv_label), scripts/comparison/nulls.py (within_form_permutation semantics —
vectorized here for the injection sweep, equivalence unit-tested), scripts/source_dependency
(effective_sources/concordance), scripts/info_budget (build_panel), the D1 damage annex
(scripts/audit_damage_markers.py output) for phantom sensitivity. scripts/logos_stats.py has
no isotonic fit, so a small pool-adjacent-violators lives here (pav_isotonic).

CLI:
    PYTHONPATH=. python3 scripts/reopening_thresholds.py [--fast] [--route a,b] [--seed N]
        [--out results/reopening_thresholds.json] [--write-doc] [--render-only]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.comparison import morphology as M                      # noqa: E402
from scripts.comparison import linb_morphology_control as LBC       # noqa: E402
from scripts.comparison.phono_distributional import (               # noqa: E402
    build_context_vectors, _loo_nn_accuracy, _power_control, cv_label)
from scripts import info_budget                                     # noqa: E402
from scripts import source_dependency                               # noqa: E402

VERSION = "reopening-thresholds-v1"
RESULTS_PATH = os.path.join(ROOT, "results", "reopening_thresholds.json")
DOC_PATH = os.path.join(ROOT, "docs", "reopening-thresholds.md")
ANNEX_PATH = os.path.join(ROOT, "corpus", "silver", "damage_annex.json")
CENSUS_PATH = os.path.join(ROOT, "experiments", "crossscript_gate", "phase2", "anchor_census.csv")
MISSING_PATH = os.path.join(ROOT, "experiments", "crossscript_gate", "phase3", "sweep",
                            "missing_items.csv")
WATCH_DOC = "docs/watch/anetaki_ii.md"

# ---- pre-committed constants (cited, not tuned) --------------------------------------- #
DETECTION_TARGET = 0.8        # detection/power target for curve thresholds (same as route 4)
ALPHA = 0.05                  # per-test alpha for detection/power routes
GRID_SUPPORT_G = 10           # route 3 pre-committed G (grid-supported signs)
GRID_SCAN_CAP_MULT = 1000.0   # route 3 analytic scan cap (x current corpus)
VOWEL_EXCESS = 0.15           # route 4 planted P(V_{i+1}=V_i) excess
H2_STABLE_BITS = 0.05         # route 2 stabilization band (+-0.05 bit)
CLASSICAL_OBS_PER_CELL = 5.0  # route 2 classical >=5 obs/cell sensitivity
RESTRICTED_INVENTORY = 92     # route 2 sensitivity: the real LA syllabary size
                              # (constraint-expansion campaign correction)
SUPERVISED_HEADROOM_F1 = 0.62 # route 6 target: supervised headroom low end
                              # (experiments/segmentation_extension: 0.62-0.66)
ALL_BOUNDARIES_F1_CEILING = 0.577  # micro-F1 all-boundaries ceiling caveat (same source)
FOOTHOLD_SLOTS = 8            # route 7: anchor-lattice pricing slot width
NEEDED_FOOTHOLD = (2, 3)      # route 7: foothold anchor count (anchor-lattice campaign)
NEEDED_DECIPHERMENT = 12      # route 7: distinct-lineage 8-slot anchors for decipherment
KN_ZG57_SIGNS_EST = 119       # editor-reported ~119 signs on the ivory ring (watch doc)

# D1 pinned fallback (annex absent -> approx: true). Values generated 2026-08-05 by
# scripts/audit_damage_markers.py (damage-annex-v1) + this module's phantom-token pass;
# used ONLY as a marked-approximate fallback, never silently as exact.
D1_PINNED = {
    "word_tokens": 3147, "distinct_types": 1165, "phantom_types": 359,
    "types_excl_phantoms": 806, "phantom_word_tokens": 395,
    "word_tokens_excl_phantoms": 2752, "damage_touching_tokens": 911,
}
# Unit-ratio pinned fallback (silver absent -> approx: true). Generated from the 2026-08-05
# silver snapshot by this module (compute_units); marked-approximate fallback only.
UNITS_PINNED = {"la_docs_now": 1341, "la_word_tokens_now": 3147, "la_sign_tokens_now": 5792,
                "signs_per_word": 1.8405, "tokens_per_doc": 2.3468}

ROUTE_ORDER = ["morphology", "h2_entropy", "alternation_grid", "vowel_harmony",
               "phonology_cv", "segmentation", "anchors"]
_ROUTE_IDX = {r: i + 1 for i, r in enumerate(ROUTE_ORDER)}


def _rng(seed: int, route: str, *coords: int) -> np.random.Generator:
    """Deterministic per-route/per-point rng namespace."""
    return np.random.default_rng([int(seed), _ROUTE_IDX[route]] + [int(c) & 0x7FFFFFFF
                                                                   for c in coords])


# --------------------------------------------------------------------------- #
# Isotonic (pool-adjacent-violators) smoothing + honest threshold extraction
# --------------------------------------------------------------------------- #
def pav_isotonic(ys: Sequence[float], weights: Optional[Sequence[float]] = None) -> List[float]:
    """Weighted least-squares nondecreasing fit (pool-adjacent-violators)."""
    w = [1.0] * len(ys) if weights is None else [float(x) for x in weights]
    blocks: List[List[float]] = []          # [sum_wy, sum_w, count]
    for y, wi in zip(ys, w):
        blocks.append([float(y) * wi, wi, 1])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1] + 1e-15:
            b = blocks.pop()
            blocks[-1][0] += b[0]; blocks[-1][1] += b[1]; blocks[-1][2] += b[2]
    out: List[float] = []
    for s, wsum, c in blocks:
        out.extend([s / wsum] * int(c))
    return out


def threshold_from_curve(sizes: Sequence[float], rates: Sequence[float], target: float,
                         weights: Optional[Sequence[float]] = None
                         ) -> Tuple[Optional[float], List[float], str]:
    """Isotonic-smooth a detection curve and extract the first target crossing.

    Returns (threshold_or_None, fitted_curve, note). A curve that never reaches the target
    yields None — NEVER a fabricated number. Sizes must be ascending."""
    if list(sizes) != sorted(float(s) for s in sizes):
        raise ValueError("sizes must be ascending")
    fit = pav_isotonic(rates, weights)
    for i, f in enumerate(fit):
        if f >= target - 1e-12:
            if i == 0:
                return float(sizes[0]), fit, "at_or_below_grid_min"
            lo_s, lo_f = float(sizes[i - 1]), fit[i - 1]
            if f - lo_f < 1e-12:
                return float(sizes[i]), fit, "grid_point"
            x = lo_s + (target - lo_f) * (float(sizes[i]) - lo_s) / (f - lo_f)
            return float(x), fit, "interpolated"
    return None, fit, "never_reaches_target"


# --------------------------------------------------------------------------- #
# Units + D1 phantom sensitivity (fail soft: annex absent -> approx pinned values)
# --------------------------------------------------------------------------- #
def load_phantom(annex_path: str = ANNEX_PATH) -> Dict[str, object]:
    """D1 phantom info. Exact from the annex when present; else approx pinned (never crash)."""
    if not os.path.exists(annex_path):
        return {"approx": True, "phantom_type_set": None, **D1_PINNED,
                "note": "damage annex absent — pinned damage-annex-v1 (2026-08-05) values; "
                        "run scripts/audit_damage_markers.py for exact"}
    annex = json.load(open(annex_path, encoding="utf-8"))
    clean: set = set()
    damaged: set = set()
    tok_by_type: Counter = Counter()
    for d in annex["docs"].values():
        for c, ty in zip(d["w"], d["types"]):
            tok_by_type[ty] += 1
            (damaged if c else clean).add(ty)
    phantom = damaged - clean
    n_ph_tok = sum(tok_by_type[t] for t in phantom)
    n_tok = sum(tok_by_type.values())
    return {"approx": False, "phantom_type_set": phantom,
            "word_tokens": n_tok, "distinct_types": len(clean | damaged),
            "phantom_types": len(phantom), "types_excl_phantoms": len(clean | damaged) - len(phantom),
            "phantom_word_tokens": n_ph_tok, "word_tokens_excl_phantoms": n_tok - n_ph_tok,
            "damage_touching_tokens": annex["summary"]["damage_touching_tokens"]}


def compute_units(la_corpus: Optional[Sequence[M.Inscription]],
                  phantom: Dict[str, object]) -> Dict[str, object]:
    """The stamped unit system (canonical axis = LA word tokens). Generated, never hand-typed;
    pinned-approx fallback only when the silver corpus is absent."""
    if la_corpus:
        wt = sum(len(i.words) for i in la_corpus)
        st = sum(len(w) for i in la_corpus for w in i.words)
        base = {"la_docs_now": len(la_corpus), "la_word_tokens_now": wt,
                "la_sign_tokens_now": st, "signs_per_word": round(st / wt, 4),
                "tokens_per_doc": round(wt / len(la_corpus), 4)}
        approx = False
    else:
        base = dict(UNITS_PINNED)
        approx = True
    zg = KN_ZG57_SIGNS_EST / base["signs_per_word"]
    return {
        "canonical_axis": "la_word_tokens", "approx": approx, **base,
        "kn_zg57_signs_est": KN_ZG57_SIGNS_EST,
        "kn_zg57_word_token_equiv": round(zg, 2),
        "phantom_sensitivity": {
            "approx": bool(phantom["approx"]),
            "phantom_types": phantom["phantom_types"],
            "phantom_word_tokens": phantom["phantom_word_tokens"],
            "la_word_tokens_excl_phantoms": phantom["word_tokens_excl_phantoms"],
            "distinct_types": phantom["distinct_types"],
            "types_excl_phantoms": phantom["types_excl_phantoms"],
        },
    }


def convert_threshold(la_word_tokens: Optional[float], units: Dict[str, object]
                      ) -> Optional[Dict[str, float]]:
    """Canonical-axis reading of a threshold: LA word tokens + 'x more docs' + 'x KN Zg 57s'."""
    if la_word_tokens is None:
        return None
    now = float(units["la_word_tokens_now"])
    add = max(0.0, float(la_word_tokens) - now)
    return {"la_word_tokens": round(float(la_word_tokens), 1),
            "additional_word_tokens": round(add, 1),
            "approx_new_docs": round(add / float(units["tokens_per_doc"]), 1),
            "approx_kn_zg57_equivalents": round(add / float(units["kn_zg57_word_token_equiv"]), 2)}


def _phantom_distance_row(threshold_la: Optional[float], units: Dict[str, object]
                          ) -> Dict[str, object]:
    """Per-route D1 sensitivity: the now-marker under phantom exclusion (fail-soft approx)."""
    ph = units["phantom_sensitivity"]
    row: Dict[str, object] = {"approx": ph["approx"],
                              "la_word_tokens_now_excl_phantoms": ph["la_word_tokens_excl_phantoms"]}
    if threshold_la is not None:
        row["additional_word_tokens_excl_phantoms"] = round(
            max(0.0, float(threshold_la) - float(ph["la_word_tokens_excl_phantoms"])), 1)
    row["note"] = ("distance measured from the phantom-excluded now-marker "
                   "(D1: phantom types are attested only damaged)")
    return row


# --------------------------------------------------------------------------- #
# Shared corpus helpers
# --------------------------------------------------------------------------- #
def stratified_doc_subsample(corpus: Sequence[M.Inscription], target_tokens: int,
                             rng: np.random.Generator) -> Tuple[List[M.Inscription], int]:
    """Site-stratified doc subsample (without replacement): per-site shuffled queues, always
    drawing from the site with the least fractional progress, until >= target word tokens."""
    total = sum(len(i.words) for i in corpus)
    if target_tokens >= total:
        return list(corpus), total
    by_site: Dict[str, List[M.Inscription]] = defaultdict(list)
    for ins in corpus:
        by_site[ins.site].append(ins)
    queues = {s: [by_site[s][i] for i in rng.permutation(len(by_site[s]))]
              for s in sorted(by_site)}
    taken = {s: 0 for s in queues}
    out: List[M.Inscription] = []
    tok = 0
    while tok < target_tokens:
        cands = [s for s in queues if taken[s] < len(queues[s])]
        if not cands:
            break
        s = min(cands, key=lambda k: (taken[k] / len(queues[k]), k))
        d = queues[s][taken[s]]
        taken[s] += 1
        out.append(d)
        tok += len(d.words)
    return out, tok


def _filter_phantoms(corpus: Sequence[M.Inscription],
                     phantom_types: set) -> List[M.Inscription]:
    """LA corpus with word tokens of phantom types (D1) removed."""
    out = []
    for ins in corpus:
        words = [w for w in ins.words if "-".join(w) not in phantom_types]
        if words:
            out.append(M.Inscription(ins.iid, ins.site, words))
    return out


def _vocab_growth(doc_streams: Sequence[Sequence[str]], checkpoints: Sequence[int],
                  n_orders: int, rng: np.random.Generator) -> List[Dict[str, float]]:
    """Averaged vocabulary/bigram growth over seeded doc-order shuffles. Streams are per-doc
    item sequences; bigrams are within-doc adjacencies. Returns one row per checkpoint with
    mean N (item tokens), V (distinct items), B (bigram tokens), H2 (plug-in cond. entropy)."""
    acc: List[List[Tuple[float, float, float, float]]] = [[] for _ in checkpoints]
    for _o in range(n_orders):
        order = rng.permutation(len(doc_streams))
        seen: set = set()
        bigr: Counter = Counter()
        left: Counter = Counter()
        n = b = 0
        ci = 0
        for di in order:
            st = doc_streams[di]
            seen.update(st)
            for a, bb in zip(st, st[1:]):
                bigr[(a, bb)] += 1
                left[a] += 1
                b += 1
            n += len(st)
            while ci < len(checkpoints) and n >= checkpoints[ci]:
                acc[ci].append((n, len(seen), b, _h2_bits(bigr, left, b)))
                ci += 1
        while ci < len(checkpoints):        # short corpus: final state stands in
            acc[ci].append((n, len(seen), b, _h2_bits(bigr, left, b)))
            ci += 1
    rows = []
    for ck, pts in zip(checkpoints, acc):
        a = np.asarray(pts, dtype=float)
        rows.append({"target": int(ck), "N": float(a[:, 0].mean()), "V": float(a[:, 1].mean()),
                     "B": float(a[:, 2].mean()), "H2": float(a[:, 3].mean())})
    return rows


def _h2_bits(bigr: Counter, left: Counter, b: int) -> float:
    """Plug-in conditional entropy H(next|prev) in bits from bigram counts."""
    if b <= 0:
        return 0.0
    h = 0.0
    for (a, _), c in bigr.items():
        p = c / b
        h -= p * math.log2(c / left[a])
    return h


def _geom_grid(lo: int, hi: int, n: int) -> List[int]:
    xs = np.unique(np.round(np.geomspace(max(2, lo), max(3, hi), n)).astype(int))
    return [int(x) for x in xs]


def heaps_fit(Ns: Sequence[float], Vs: Sequence[float], burn_in: float = 300.0
              ) -> Tuple[float, float]:
    """Least-squares log-log Heaps fit V = K * N^beta over N >= burn_in."""
    pts = [(n, v) for n, v in zip(Ns, Vs) if n >= burn_in and v > 0]
    if len(pts) < 2:
        pts = [(n, v) for n, v in zip(Ns, Vs) if v > 0]
    x = np.log([p[0] for p in pts])
    y = np.log([p[1] for p in pts])
    beta, logk = np.polyfit(x, y, 1)
    return float(math.exp(logk)), float(beta)


def h2_closed_form(K: float, beta: float, c_min: float, r: float) -> Optional[float]:
    """Solve r*N / (K*N^beta)^2 >= c_min for N (sign tokens). None when vocabulary growth
    dominates (1 - 2*beta <= 0): cell coverage never catches up under the fitted law."""
    expo = 1.0 - 2.0 * beta
    if expo <= 1e-9 or K <= 0 or r <= 0 or c_min <= 0:
        return None
    return float((c_min * K * K / r) ** (1.0 / expo))


# --------------------------------------------------------------------------- #
# Route 1 — morphology above the bigram floor (LB document-subsample curve)
# --------------------------------------------------------------------------- #
def route_morphology(ctx: "Ctx", fast: bool, seed: int,
                     params: Optional[dict] = None) -> Dict[str, object]:
    p = {"sizes": [800, 3147, 6400, 13562] if fast else [800, 1600, 3147, 4800, 6400, 9600, 13562],
         "replicates": 2 if fast else 3, "n_null": 40 if fast else 200,
         "la_control_n_null": 40 if fast else 200}
    if params:
        p.update(params)
    lb = ctx.lb_corpus
    lb_total = sum(len(i.words) for i in lb)
    curve = []
    for size in p["sizes"]:
        reps = 1 if size >= lb_total else p["replicates"]
        det = []
        for rep in range(reps):
            sub, tok = stratified_doc_subsample(lb, size, _rng(seed, "morphology", size, rep))
            r = M.null_falsification(sub, M.SignCodec.from_corpus(sub), affixes=LBC.MYC_AFFIXES,
                                     n_null=p["n_null"], seed=seed * 1000 + size + rep)
            det.append({"rep": rep, "tokens": tok, "docs": len(sub),
                        "real_confirm_rate": round(r["real_confirm_rate"], 4),
                        "shuffle_floor": round(r["shuffle_confirm_rate"], 4),
                        "lfake_floor": round(r["lfake_confirm_rate"], 4),
                        "fires": bool(r["has_morphology_power"])})
        curve.append({"size": size, "detection_rate": round(sum(d["fires"] for d in det) / reps, 4),
                      "replicates": det})
    thr, fitted, note = threshold_from_curve([c["size"] for c in curve],
                                             [c["detection_rate"] for c in curve],
                                             DETECTION_TARGET)
    # contradiction guard, in-artifact: the published LA panel at its own size must NOT fire.
    la = ctx.la_corpus
    la_r = M.null_falsification(la, M.SignCodec.from_corpus(la), affixes=M.PREREG_AFFIXES,
                                n_null=p["la_control_n_null"], seed=seed)
    la_now = ctx.units["la_word_tokens_now"]
    size_binding = thr is not None and thr > la_now
    if thr is None:
        status = "FIT_FAILED" if note == "never_reaches_target" else "FIT_FAILED"
        reopen_la = None
    elif size_binding:
        status = "MEASURED_ON_ANALOG"
        reopen_la = thr                    # word-token axis carries over 1:1 (analog assumption)
    else:
        status = "SIZE_NOT_BINDING"
        reopen_la = None
    return {
        "title": "Morphology above the bigram floor (LB analogue detection curve)",
        "native_axis": "lb_word_tokens", "native_now_marker": la_now,
        "closed_result": ("Linear A affix panel NO-POWER at its 3,147 word tokens (real rate not "
                          "above the max(shuffle, L_fake) bigram floor; "
                          "scripts/comparison/morphology.py; the LB positive control fires — "
                          "results/linb_morphology_control.json)"),
        "method": ("site-stratified DĀMOS document subsample at each size; statistic = "
                   "morphology.null_falsification real_confirm_rate vs max(shuffle, L_fake); "
                   "detection = has_morphology_power; threshold = isotonic-smoothed curve "
                   f"crossing {DETECTION_TARGET}"),
        "params": p, "curve": curve, "isotonic_fit": [round(f, 4) for f in fitted],
        "threshold_native": None if thr is None else round(thr, 1),
        "threshold_note": note, "status": status,
        "la_control": {"n_null": p["la_control_n_null"],
                       "real_confirm_rate": round(la_r["real_confirm_rate"], 4),
                       "shuffle_floor": round(la_r["shuffle_confirm_rate"], 4),
                       "lfake_floor": round(la_r["lfake_confirm_rate"], 4),
                       "fires": bool(la_r["has_morphology_power"]),
                       "note": "the published LA NO-POWER, reproduced in-artifact"},
        "reopen_at": convert_threshold(reopen_la, ctx.units),
        "structural_reopen_event": (
            None if size_binding else
            "a shift in the LA word-length structure — a materially higher share of >=3-sign "
            "word tokens (e.g. the KN Zg 57 ring edition), NOT more same-shape tokens: the LB "
            "analogue detects at/below LA's current size, so size alone cannot reopen this route"),
        "caveats": [
            "LB-analogue threshold = optimistic lower bound; a crossing means 're-runnable', "
            "never 'identifiable'",
            "the published LA null is short-word/structural (LB positive control fires): the "
            "measured analogue curve prices the SIZE axis only",
        ],
        "phantom_sensitivity": _phantom_distance_row(reopen_la, ctx.units),
        "info_budget": _panel(
            raw_corpus_size=lb_total, effective_independent_evidence=len({i.site for i in lb}),
            parameter_count=0, search_space_size=len(p["sizes"]),
            source_dependency_structure="single lineage (L_LB_DECIPHERMENT analogue)",
            damage_rate=_la_damage_rate(ctx), estimated_power=DETECTION_TARGET,
            minimum_detectable_effect="confirm-rate above max(shuffle,L_fake) floor"),
    }


# --------------------------------------------------------------------------- #
# Route 2 — conditional entropy H2 (analytic cell-coverage adequacy)
# --------------------------------------------------------------------------- #
def _h2_route_core(la_corpus: Sequence[M.Inscription], c_min: float, n_orders: int,
                   seed: int, tag: int) -> Dict[str, object]:
    streams = [[s for w in i.words for s in w] for i in la_corpus]
    streams = [s for s in streams if s]
    total = sum(len(s) for s in streams)
    grid = _geom_grid(200, total, 24)
    growth = _vocab_growth(streams, grid, n_orders, _rng(seed, "h2_entropy", tag, 1))
    K, beta = heaps_fit([g["N"] for g in growth], [g["V"] for g in growth])
    n_docs = len(streams)
    r = (total - n_docs) / total            # bigram tokens per sign token (per-doc streams)
    nstar = h2_closed_form(K, beta, c_min, r)
    full_v = growth[-1]["V"]
    return {"sign_tokens_now": total, "docs": n_docs, "V_now": int(round(full_v)),
            "H2_now_bits": round(growth[-1]["H2"], 4),
            "obs_per_cell_now": round(r * total / full_v ** 2, 4),
            "heaps_K": round(K, 4), "heaps_beta": round(beta, 4),
            "bigrams_per_sign_token": round(r, 4),
            "n_star_sign_tokens": None if nstar is None else round(nstar, 1),
            "shortfall_orders_of_magnitude":
                None if nstar is None else round(math.log10(nstar / total), 2)}


def route_h2(ctx: "Ctx", fast: bool, seed: int, params: Optional[dict] = None) -> Dict[str, object]:
    p = {"n_orders": 6 if fast else 20}
    if params:
        p.update(params)
    # LB calibration: at which obs/cell does the LB H2 estimate stabilize to +-0.05 bit?
    lb_streams = [[s for w in i.words for s in w] for i in ctx.lb_corpus]
    lb_streams = [s for s in lb_streams if s]
    lb_total = sum(len(s) for s in lb_streams)
    lb_grid = _geom_grid(400, lb_total, 24)
    lb_growth = _vocab_growth(lb_streams, lb_grid, p["n_orders"], _rng(seed, "h2_entropy", 0, 0))
    h2_ref = lb_growth[-1]["H2"]
    stab = None
    for i in range(len(lb_growth)):
        if all(abs(g["H2"] - h2_ref) <= H2_STABLE_BITS for g in lb_growth[i:]):
            stab = lb_growth[i]
            break
    c_min_emp = None if stab is None else stab["B"] / (stab["V"] ** 2)
    calib = {"lb_sign_tokens": lb_total, "lb_H2_ref_bits": round(h2_ref, 4),
             "stabilization_band_bits": H2_STABLE_BITS,
             "lb_stabilization_sign_tokens": None if stab is None else round(stab["N"], 1),
             "c_min_empirical_obs_per_cell": None if c_min_emp is None else round(c_min_emp, 4)}
    main = _h2_route_core(ctx.la_corpus, c_min_emp if c_min_emp else CLASSICAL_OBS_PER_CELL,
                          p["n_orders"], seed, 1)
    classical = _h2_route_core(ctx.la_corpus, CLASSICAL_OBS_PER_CELL, p["n_orders"], seed, 2)
    r = main["bigrams_per_sign_token"]
    restricted = {
        "V_fixed": RESTRICTED_INVENTORY,
        "n_star_sign_tokens_empirical_cmin":
            None if c_min_emp is None else round(c_min_emp * RESTRICTED_INVENTORY ** 2 / r, 1),
        "n_star_sign_tokens_classical":
            round(CLASSICAL_OBS_PER_CELL * RESTRICTED_INVENTORY ** 2 / r, 1),
    }
    nstar = main["n_star_sign_tokens"]
    spw = float(ctx.units["signs_per_word"])
    reopen_la = None if nstar is None else nstar / spw
    status = "ANALYTIC" if nstar is not None else "UNREACHABLE_AT_CAP"
    # phantom sensitivity: recompute the analytic fit on the phantom-excluded corpus
    if ctx.phantom["phantom_type_set"] is not None:
        excl = _h2_route_core(_filter_phantoms(ctx.la_corpus, ctx.phantom["phantom_type_set"]),
                              c_min_emp if c_min_emp else CLASSICAL_OBS_PER_CELL,
                              p["n_orders"], seed, 3)
        ph_row: Dict[str, object] = {"approx": False,
                                     "n_star_sign_tokens_excl_phantoms": excl["n_star_sign_tokens"],
                                     "V_now_excl_phantoms": excl["V_now"],
                                     "sign_tokens_now_excl_phantoms": excl["sign_tokens_now"]}
    else:
        ph_row = {"approx": True,
                  "note": "annex absent — analytic phantom re-fit skipped; pinned D1 counts only"}
    ph_row.update({k: v for k, v in _phantom_distance_row(reopen_la, ctx.units).items()
                   if k not in ph_row})
    return {
        "title": "Conditional entropy H2 (bigram cell-coverage adequacy, analytic)",
        "native_axis": "la_sign_tokens", "native_now_marker": main["sign_tokens_now"],
        "closed_result": ("information floor: LA bigram statistics are cell-starved at current "
                          "size (obs/cell << 1); every H2-dependent probe is budget-capped "
                          "(Art. IX panels; paper information-budget discipline)"),
        "method": ("Heaps fit V=K*N^beta on LA sign-vocabulary growth (averaged over seeded "
                   "doc-order shuffles); obs/cell(N) = r*N/V(N)^2; c_min calibrated from LB H2 "
                   f"stabilization (+-{H2_STABLE_BITS} bit) with classical "
                   f">={CLASSICAL_OBS_PER_CELL:g}/cell and the {RESTRICTED_INVENTORY}-sign "
                   "restricted inventory as sensitivity rows; closed-form N*"),
        "params": p, "lb_calibration": calib, "la_fit": main,
        "sensitivity_classical": classical, "sensitivity_restricted_inventory": restricted,
        "threshold_native": nstar, "threshold_note": "closed_form", "status": status,
        "reopen_at": convert_threshold(reopen_la, ctx.units),
        "structural_reopen_event": None,
        "caveats": [
            "analytic: assumes the fitted Heaps law keeps holding (damage variants inflate V; "
            "the restricted-inventory row is the linguistically-real syllabary bound)",
            "adequacy only: reaching N* makes H2 estimable, it does not make any reading true",
        ],
        "phantom_sensitivity": ph_row,
        "info_budget": _panel(
            raw_corpus_size=main["sign_tokens_now"],
            effective_independent_evidence=len({i.site for i in ctx.la_corpus}),
            parameter_count=3, search_space_size=1,
            source_dependency_structure="L_LA_CORPUS silver (single lineage); LB calibration analogue",
            damage_rate=_la_damage_rate(ctx),
            minimum_detectable_effect=f"H2 stable to +-{H2_STABLE_BITS} bit"),
    }


# --------------------------------------------------------------------------- #
# Route 3 — alternation grid / minimal pairs (analytic birthday-problem model)
# --------------------------------------------------------------------------- #
def final_slot_alternation_stats(types: set) -> Dict[str, object]:
    """Observed S&M-shape alternation material: pairs of types (len>=3) sharing the full
    leading stem and differing in the final sign. Grid support = an unordered final-sign
    pair attested over >=2 DISTINCT stems (the repeated-variation evidence unit, S&M 2017
    §5); a sign is grid-supported when it belongs to such a pair."""
    buckets: Dict[tuple, List[tuple]] = defaultdict(list)
    for t in types:
        if len(t) >= 3:
            buckets[t[:-1]].append(t)
    events: Counter = Counter()
    for _stem, mem in buckets.items():
        finals = sorted({m[-1] for m in mem})
        for a in range(len(finals)):
            for b in range(a + 1, len(finals)):
                events[(finals[a], finals[b])] += 1
    multi = {p: c for p, c in events.items() if c >= 2}
    signs = sorted({s for pr in multi for s in pr})
    return {"stem_sharing_pair_events": int(sum(events.values())),
            "distinct_alternating_pairs": len(events),
            "doubly_attested_pairs": len(multi),
            "grid_supported_signs": len(signs),
            "grid_supported_sign_list": signs}


def _alternation_model(types: set, scan_mults: Sequence[float]) -> Dict[str, object]:
    """Birthday-problem expectation of grid-supported signs as the type inventory grows.
    Per length: E[stem-sharing pair events] = C(T_L,2) * prod(slot collision probs) *
    (1 - final collision); events distributed over final-sign pairs by the final-slot
    marginal; per-pair counts Poisson; grid support = P(>=2 events)."""
    by_len: Dict[int, List[tuple]] = defaultdict(list)
    for t in types:
        if len(t) >= 3:
            by_len[len(t)].append(t)
    if not by_len:
        return {"model_events_now": 0.0, "scan": [], "finals": 0}
    # per-length slot marginals -> collision probs; global final-slot marginal
    a_d: Dict[int, Tuple[float, float]] = {}
    qf: Counter = Counter()
    for L, mem in by_len.items():
        colls = []
        for j in range(L):
            cnt = Counter(t[j] for t in mem)
            n = len(mem)
            colls.append(sum((c / n) ** 2 for c in cnt.values()))
        a_d[L] = (float(np.prod(colls[:-1])), 1.0 - colls[-1])
        for t in mem:
            qf[t[-1]] += 1
    finals = sorted(qf)
    q = np.array([qf[s] for s in finals], dtype=float)
    q /= q.sum()
    d_f = 1.0 - float(np.sum(q ** 2))
    lam_shape = np.outer(q, q) * 2.0 / max(d_f, 1e-12)      # pair share of one event
    np.fill_diagonal(lam_shape, 0.0)

    def e_events(scale: float) -> float:
        tot = 0.0
        for L, mem in by_len.items():
            T = len(mem) * scale
            aL, dL = a_d[L]
            tot += 0.5 * T * (T - 1.0) * aL * dL
        return tot

    def e_grid_signs(total_events: float) -> float:
        lam = lam_shape * total_events
        p2 = 1.0 - np.exp(-lam) * (1.0 + lam)               # P(pair Poisson >= 2)
        p_sign = 1.0 - np.prod(1.0 - p2 + np.eye(len(q)) * p2, axis=1)
        return float(np.sum(p_sign))

    return {"model_events_now": e_events(1.0), "e_events": e_events,
            "e_grid_signs": e_grid_signs, "finals": len(finals)}


def route_alternation(ctx: "Ctx", fast: bool, seed: int,
                      params: Optional[dict] = None) -> Dict[str, object]:
    p = {"scan_points": 40 if fast else 60,
         "lb_check_sizes": [13562] if fast else [3400, 6800, 13562]}
    if params:
        p.update(params)

    def _compute(corpus: Sequence[M.Inscription]) -> Dict[str, object]:
        n_tok = sum(len(i.words) for i in corpus)
        types = {tuple(w) for i in corpus for w in i.words}
        obs = final_slot_alternation_stats(types)
        model = _alternation_model(types, [])
        calib = (obs["stem_sharing_pair_events"] / model["model_events_now"]
                 if model["model_events_now"] > 0 else 1.0)
        # type-inventory growth: Heaps on word-type growth over doc-order shuffles
        streams = [["-".join(w) for w in i.words] for i in corpus]
        grid = _geom_grid(100, n_tok, 20)
        growth = _vocab_growth(streams, grid, 6, _rng(seed, "alternation_grid", n_tok, 4))
        K, beta = heaps_fit([g["N"] for g in growth], [g["V"] for g in growth], burn_in=100)
        v_now = len(types)

        def scale_at(N: float) -> float:
            return (K * N ** beta) / v_now

        mults = np.geomspace(1.0, GRID_SCAN_CAP_MULT, p["scan_points"])
        scan = []
        thr = None
        prev = None
        for m in mults:
            N = n_tok * float(m)
            ev = calib * model["e_events"](scale_at(N))
            eg = model["e_grid_signs"](ev)
            scan.append({"la_word_tokens": round(N, 1), "e_events": round(ev, 2),
                         "e_grid_supported_signs": round(eg, 2)})
            if thr is None and eg >= GRID_SUPPORT_G:
                if prev is None:
                    thr = N
                else:
                    n0, g0 = prev
                    frac = (GRID_SUPPORT_G - g0) / max(eg - g0, 1e-12)
                    thr = float(np.exp(np.log(n0) + frac * (np.log(N) - np.log(n0))))
            prev = (N, eg)
        return {"word_tokens": n_tok, "types": len(types), "observed": obs,
                "model_events_now": round(model["model_events_now"], 2),
                "calibration_factor": round(calib, 3),
                "heaps_K": round(K, 4), "heaps_beta": round(beta, 4),
                "scan_head": scan[:6], "threshold_la_word_tokens": None if thr is None
                else round(thr, 1)}

    main = _compute(ctx.la_corpus)
    # empirical LB shape check (reported only): observed grid-supported signs at subsample
    # sizes vs the LB-fitted model prediction.
    lb = ctx.lb_corpus
    lb_types_full = {tuple(w) for i in lb for w in i.words}
    lb_model = _alternation_model(lb_types_full, [])
    lb_obs_full = final_slot_alternation_stats(lb_types_full)
    lb_calib = (lb_obs_full["stem_sharing_pair_events"] / lb_model["model_events_now"]
                if lb_model["model_events_now"] > 0 else 1.0)
    lb_check = []
    for size in p["lb_check_sizes"]:
        sub, tok = stratified_doc_subsample(lb, size, _rng(seed, "alternation_grid", size, 9))
        st = {tuple(w) for i in sub for w in i.words}
        o = final_slot_alternation_stats(st)
        scale = len({t for t in st if len(t) >= 3}) / max(
            1, len({t for t in lb_types_full if len(t) >= 3}))
        pred = lb_model["e_grid_signs"](lb_calib * lb_model["e_events"](scale))
        lb_check.append({"lb_word_tokens": tok,
                         "observed_grid_supported_signs": o["grid_supported_signs"],
                         "model_grid_supported_signs": round(pred, 1)})
    thr = main["threshold_la_word_tokens"]
    status = "ANALYTIC" if thr is not None else "UNREACHABLE_AT_CAP"
    if thr is not None and thr <= ctx.units["la_word_tokens_now"]:
        status = "ALREADY_ADEQUATE"
    if ctx.phantom["phantom_type_set"] is not None:
        excl = _compute(_filter_phantoms(ctx.la_corpus, ctx.phantom["phantom_type_set"]))
        ph_row: Dict[str, object] = {
            "approx": False,
            "threshold_excl_phantoms_la_word_tokens": excl["threshold_la_word_tokens"],
            "observed_grid_supported_signs_excl_phantoms": excl["observed"]["grid_supported_signs"],
            "types_excl_phantoms": excl["types"]}
    else:
        ph_row = {"approx": True,
                  "note": "annex absent — phantom re-fit skipped; pinned D1 counts only"}
    ph_row.update({k: v for k, v in _phantom_distance_row(thr, ctx.units).items()
                   if k not in ph_row})
    return {
        "title": "Alternation grid / minimal pairs (analytic adequacy model)",
        "native_axis": "la_word_tokens", "native_now_marker": main["word_tokens"],
        "closed_result": ("relative-phonology campaign: substitution consonant-axis validated "
                          "on LB, NOT recoverable on LA (branch "
                          "research/linear-a-relative-phonology-seals); the S&M variation "
                          "constraints stay constraints, never pins"),
        "method": ("evidence unit = an unordered final-sign pair alternating word-finally over "
                   ">=2 DISTINCT shared stems (len>=2), the S&M 2017 §5 repeated-variation "
                   "shape; E[pairs] per length from per-slot type marginals (birthday problem) "
                   "+ Heaps-grown type counts, Poisson per pair, calibrated to the observed "
                   f"event count at N_now; threshold = E[grid-supported signs] >= G={GRID_SUPPORT_G}"),
        "params": {**p, "G": GRID_SUPPORT_G, "scan_cap_mult": GRID_SCAN_CAP_MULT},
        "la": main, "lb_shape_check": lb_check,
        "threshold_native": thr,
        "threshold_note": "analytic_scan", "status": status,
        "reopen_at": convert_threshold(thr, ctx.units),
        "structural_reopen_event": None,
        "caveats": [
            "adequacy only: E >= G means the corpus is expected to CONTAIN a 10-sign grid's "
            "worth of repeated alternation material; whether it is genuine morphophonology is "
            "the reopened experiment's question (with the birthday null inside it)",
            "slot marginals and per-length shares held fixed at their observed values "
            "(assumption stamped)",
        ],
        "phantom_sensitivity": ph_row,
        "info_budget": _panel(
            raw_corpus_size=main["word_tokens"],
            effective_independent_evidence=len({i.site for i in ctx.la_corpus}),
            parameter_count=2, search_space_size=p["scan_points"],
            source_dependency_structure="L_LA_CORPUS silver (single lineage)",
            damage_rate=_la_damage_rate(ctx),
            minimum_detectable_effect=f"E[grid-supported signs] >= {GRID_SUPPORT_G}"),
    }


# --------------------------------------------------------------------------- #
# Route 4 — vowel harmony (injection power curve with a size axis)
# --------------------------------------------------------------------------- #
def _grouped_within_form_permutation(groups: Dict[int, np.ndarray],
                                     rng: np.random.Generator) -> Dict[int, np.ndarray]:
    """Vectorized within-form (per-word) sign-order permutation — the semantics of
    nulls.within_form_permutation (Nair 2026), grouped by word length for the injection
    sweep. Equivalence is unit-tested (tests/test_reopening_thresholds.py)."""
    out = {}
    for L, arr in groups.items():
        idx = np.argsort(rng.random(arr.shape), axis=1)
        out[L] = np.take_along_axis(arr, idx, axis=1)
    return out


def _same_vowel_rate(groups: Dict[int, np.ndarray]) -> float:
    num = den = 0
    for L, arr in groups.items():
        num += int((arr[:, 1:] == arr[:, :-1]).sum())
        den += arr.shape[0] * (L - 1)
    return num / den if den else 0.0


def route_vowel_harmony(ctx: "Ctx", fast: bool, seed: int,
                        params: Optional[dict] = None) -> Dict[str, object]:
    p = {"k_grid": [0.5, 1, 4] if fast else [0.25, 0.5, 1, 2, 4, 8],
         "replicates": 8 if fast else 25, "n_perm": 60 if fast else 150}
    if params:
        p.update(params)
    la = ctx.la_corpus
    dec_words = [w for i in la for w in i.words
                 if len(w) >= 2 and all(cv_label(s) for s in w)]
    n_base = len(dec_words)
    signs = sorted({s for w in dec_words for s in w})
    sidx = {s: i for i, s in enumerate(signs)}
    vowels = sorted({cv_label(s)[1] for s in signs})
    vidx = {v: i for i, v in enumerate(vowels)}
    vowel_of = np.array([vidx[cv_label(s)[1]] for s in signs])
    freq = Counter(s for w in dec_words for s in w)
    q = np.array([freq[s] for s in signs], dtype=float)
    q /= q.sum()
    q_by_v = []
    for v in range(len(vowels)):
        qq = np.where(vowel_of == v, q, 0.0)
        q_by_v.append(qq / qq.sum() if qq.sum() > 0 else qq)
    lens = Counter(len(w) for w in dec_words)
    len_vals = np.array(sorted(lens))
    len_p = np.array([lens[int(l)] for l in len_vals], dtype=float)
    len_p /= len_p.sum()
    p0 = float(sum((q[vowel_of == v].sum()) ** 2 for v in range(len(vowels))))
    eps = min(1.0, VOWEL_EXCESS / max(1e-9, 1.0 - p0))

    def gen(n_words: int, rng: np.random.Generator, plant: bool) -> Dict[int, np.ndarray]:
        lengths = rng.choice(len_vals, p=len_p, size=n_words)
        groups: Dict[int, np.ndarray] = {}
        for L in sorted(set(int(x) for x in lengths)):
            n_l = int((lengths == L).sum())
            mat = np.empty((n_l, L), dtype=np.int64)
            mat[:, 0] = rng.choice(len(signs), p=q, size=n_l)
            for j in range(1, L):
                col = rng.choice(len(signs), p=q, size=n_l)
                if plant:
                    match = rng.random(n_l) < eps
                    prev_v = vowel_of[mat[:, j - 1]]
                    for v in range(len(vowels)):
                        mask = match & (prev_v == v)
                        if mask.any() and q_by_v[v].sum() > 0:
                            col[mask] = rng.choice(len(signs), p=q_by_v[v], size=int(mask.sum()))
                mat[:, j] = col
            groups[L] = mat
        return groups

    def one_test(k: float, rep: int, plant: bool) -> float:
        rng = _rng(seed, "vowel_harmony", int(round(k * 1000)), rep, 0 if plant else 1)
        groups = gen(int(round(k * n_base)), rng, plant)
        vgroups = {L: vowel_of[m] for L, m in groups.items()}
        obs = _same_vowel_rate(vgroups)
        null = np.array([_same_vowel_rate(_grouped_within_form_permutation(vgroups, rng))
                         for _ in range(p["n_perm"])])
        return float((np.sum(null >= obs - 1e-12) + 1) / (p["n_perm"] + 1))

    curve = []
    for k in p["k_grid"]:
        ps = [one_test(k, rep, True) for rep in range(p["replicates"])]
        curve.append({"k": k, "la_word_tokens": int(round(k * ctx.units["la_word_tokens_now"])),
                      "decodable_word_tokens": int(round(k * n_base)),
                      "power": round(sum(x < ALPHA for x in ps) / len(ps), 4),
                      "median_p": round(float(np.median(ps)), 4)})
    fp = [one_test(p["k_grid"][-1], rep, False) for rep in range(p["replicates"])]
    fp_rate = sum(x < ALPHA for x in fp) / len(fp)
    thr_k, fitted, note = threshold_from_curve([c["k"] for c in curve],
                                               [c["power"] for c in curve], DETECTION_TARGET)
    thr_la = None if thr_k is None else thr_k * ctx.units["la_word_tokens_now"]
    status = "MEASURED_ON_ANALOG" if thr_la is not None else "UNREACHABLE_AT_CAP"
    if thr_la is not None and thr_la <= ctx.units["la_word_tokens_now"]:
        status = "SIZE_NOT_BINDING"
    reopen_la = thr_la if status == "MEASURED_ON_ANALOG" else None
    return {
        "title": "Vowel harmony (injection power curve, LA-matched synthetic corpora)",
        "native_axis": "corpus_scale_k_x_la_word_tokens",
        "native_now_marker": ctx.units["la_word_tokens_now"],
        "closed_result": ("phonology data-limited null (paper; phono_distributional pilot): "
                          "no harmony-type regularity was claimable at current size"),
        "method": (f"synthetic corpora matched to the LA decodable-word length/sign-frequency "
                   f"profile at k x current size; planted P(V_i+1=V_i) excess {VOWEL_EXCESS} "
                   f"(mixture eps={eps:.3f} over independence baseline p0={p0:.3f}); null = "
                   "within-form sign-order permutation (Nair semantics, vectorized); threshold "
                   f"= power >= {DETECTION_TARGET} at alpha={ALPHA}"),
        "params": {**p, "planted_excess": VOWEL_EXCESS, "alpha": ALPHA,
                   "decodable_word_tokens_now": n_base, "p0_independence": round(p0, 4),
                   "eps_mixture": round(eps, 4)},
        "curve": curve, "isotonic_fit": [round(f, 4) for f in fitted],
        "false_positive_rate_unplanted": round(fp_rate, 4),
        "threshold_native": None if thr_k is None else round(thr_k, 3),
        "threshold_note": note, "status": status,
        "reopen_at": convert_threshold(reopen_la, ctx.units),
        "structural_reopen_event": (
            None if status != "SIZE_NOT_BINDING" else
            f"a planted {VOWEL_EXCESS} vowel-adjacency excess is already detectable at/below "
            "the current corpus size: size is not what blocks a harmony claim — reopening "
            "requires an actual preregistered harmony hypothesis (a smaller target effect "
            "needs proportionally more corpus, priced by this curve)"),
        "caveats": [
            "power only: a crossing means a planted 0.15 excess would be detectable, not that "
            "harmony exists",
            "length-2 words are invariant under the within-form null (the adjacent pair "
            "survives the swap): power is carried by length>=3 words — an honest property of "
            "the pre-specified null, stated not patched",
        ],
        "phantom_sensitivity": _phantom_distance_row(reopen_la, ctx.units),
        "info_budget": _panel(
            raw_corpus_size=n_base,
            effective_independent_evidence=len({i.site for i in la}),
            parameter_count=0, search_space_size=len(p["k_grid"]),
            source_dependency_structure="L_LA_CORPUS silver (single lineage; synthetic sweep)",
            damage_rate=_la_damage_rate(ctx), estimated_power=DETECTION_TARGET,
            minimum_detectable_effect=f"P(V_i+1=V_i) excess {VOWEL_EXCESS}"),
    }


# --------------------------------------------------------------------------- #
# Route 5 — phonology C/V power (the identical LOO-1NN test on subsampled LB)
# --------------------------------------------------------------------------- #
def route_phonology_cv(ctx: "Ctx", fast: bool, seed: int,
                       params: Optional[dict] = None) -> Dict[str, object]:
    p = {"sizes": [800, 3147, 6400, 13562] if fast else [800, 1600, 3147, 4800, 6400, 9600, 13562],
         "replicates": 2 if fast else 5, "n_perm": 300 if fast else 1000,
         "power_n_perm": 100 if fast else 300, "min_count": 3}
    if params:
        p.update(params)
    lb = ctx.lb_corpus
    lb_total = sum(len(i.words) for i in lb)
    sidak = lambda x: 1.0 - (1.0 - x) ** 2

    def point(size: int, rep: int) -> Optional[Dict[str, object]]:
        rng = _rng(seed, "phonology_cv", size, rep)
        sub, tok = stratified_doc_subsample(lb, size, rng)
        vecs, _, freq = build_context_vectors(sub)
        lab = {s: cv_label(s) for s in vecs if cv_label(s)}
        testable = [s for s in sorted(lab) if freq.get(s, 0) >= p["min_count"]]
        if len(testable) < 5:
            return {"tokens": tok, "testable": len(testable), "fires": False,
                    "class": "DATA_LIMITED", "note": "too few testable signs"}
        X = np.vstack([vecs[s] for s in testable])
        res = {}
        for name, labs in (("consonant", [lab[s][0] for s in testable]),
                           ("vowel", [lab[s][1] for s in testable])):
            obs = _loo_nn_accuracy(X, labs)
            arr = np.array(labs, dtype=object)
            null = np.array([_loo_nn_accuracy(X, list(arr[rng.permutation(len(arr))]))
                             for _ in range(p["n_perm"])])
            pv = float((np.sum(null >= obs) + 1) / (p["n_perm"] + 1))
            res[name] = {"acc": round(obs, 4), "perm_p": round(pv, 4),
                         "sidak_p": round(sidak(pv), 4)}
        fires = res["consonant"]["sidak_p"] < ALPHA or res["vowel"]["sidak_p"] < ALPHA
        power = _power_control([lab[s][0] for s in testable], n_perm=p["power_n_perm"],
                               seed=int(rng.integers(0, 2 ** 31)))
        cls = ("SIGNAL" if fires else
               "DATA_LIMITED" if power.get("test_has_power") else "INVALID")
        return {"tokens": tok, "testable": len(testable), **res, "fires": bool(fires),
                "power_control_fires_at": power.get("min_firing_strength"), "class": cls}

    curve = []
    for size in p["sizes"]:
        reps = 1 if size >= lb_total else p["replicates"]
        pts = [point(size, rep) for rep in range(reps)]
        curve.append({"size": size,
                      "detection_rate": round(sum(pt["fires"] for pt in pts) / len(pts), 4),
                      "replicates": pts})
    thr, fitted, note = threshold_from_curve([c["size"] for c in curve],
                                             [c["detection_rate"] for c in curve],
                                             DETECTION_TARGET)
    la_now = ctx.units["la_word_tokens_now"]
    size_binding = thr is not None and thr > la_now
    reopen_la = thr if size_binding else None
    status = ("MEASURED_ON_ANALOG" if size_binding else
              "SIZE_NOT_BINDING" if thr is not None else "FIT_FAILED")
    return {
        "title": "Distributional phonology C/V (LOO-1NN detection curve on subsampled LB)",
        "native_axis": "lb_word_tokens", "native_now_marker": la_now,
        "closed_result": ("LA pilot DATA-LIMITED NULL (phono_distributional): the test works "
                          "(positive control fires at strong planted signal) but the real LA "
                          "context does not predict C/V class above the permutation null"),
        "method": ("identical statistic to the LA pilot: PPMI context vectors, LOO-1NN over "
                   "the labelled (real-valued) LB signs, label-permutation null, Sidak over "
                   "the C and V tests; detection = either Sidak p < alpha; per-point "
                   "SIGNAL/DATA_LIMITED/INVALID via the pilot's _power_control"),
        "params": p, "curve": curve, "isotonic_fit": [round(f, 4) for f in fitted],
        "threshold_native": None if thr is None else round(thr, 1),
        "threshold_note": note, "status": status,
        "reopen_at": convert_threshold(reopen_la, ctx.units),
        "structural_reopen_event": (
            None if size_binding else
            "more per-sign attestation and real anchor labels, not more tokens: on LA only "
            "~50 AB signs are testable and their labels are themselves the hypothesis under "
            "test — the analogue detects at/below LA's current size, so token count alone "
            "cannot reopen this route"),
        "caveats": [
            "LB-analogue = optimistic lower bound: LB labels are true values; LA labels are "
            "LB-convention transfers (the circularity the cross-script gate REFUTED for "
            "anchor use)",
            "a crossing means 're-runnable', never 'identifiable'",
        ],
        "phantom_sensitivity": _phantom_distance_row(reopen_la, ctx.units),
        "info_budget": _panel(
            raw_corpus_size=lb_total,
            effective_independent_evidence=len({i.site for i in lb}),
            parameter_count=0, search_space_size=len(p["sizes"]),
            source_dependency_structure="single lineage (L_LB_DECIPHERMENT analogue)",
            damage_rate=_la_damage_rate(ctx), estimated_power=DETECTION_TARGET,
            minimum_detectable_effect="LOO-1NN accuracy above label-permutation null"),
    }


# --------------------------------------------------------------------------- #
# Route 6 — segmentation headroom (descending-subsample F1 curve, saturating fit)
# --------------------------------------------------------------------------- #
def fit_saturating(Ns: Sequence[float], F1s: Sequence[float]
                   ) -> Optional[Tuple[float, float, float]]:
    """Deterministic least-squares fit of F1(N) = a - b*exp(-c*N). None on failure."""
    from scipy.optimize import curve_fit
    N = np.asarray(Ns, dtype=float)
    F = np.asarray(F1s, dtype=float)
    if len(N) < 3:
        return None

    def f(n, a, b, c):
        return a - b * np.exp(-c * n)

    try:
        p0 = (float(F.max()), max(1e-3, float(F.max() - F.min())), 1.0 / max(N.mean(), 1.0))
        popt, _ = curve_fit(f, N, F, p0=p0, maxfev=20000,
                            bounds=([0.0, 0.0, 1e-9], [1.0, 1.0, 1.0]))
        return float(popt[0]), float(popt[1]), float(popt[2])
    except Exception:
        return None


def segmentation_threshold(fit: Optional[Tuple[float, float, float]],
                           target: float = SUPERVISED_HEADROOM_F1
                           ) -> Tuple[Optional[float], str]:
    """Honesty rule: asymptote at/below target -> ASYMPTOTE_LIMITED, threshold None (never a
    fabricated number); a usable fit above target -> extrapolated crossing."""
    if fit is None:
        return None, "FIT_FAILED"
    a, b, c = fit
    if a <= target:
        return None, "ASYMPTOTE_LIMITED"
    if a >= 0.999:                          # asymptote pinned at its bound: the curve is
        return None, "FIT_UNCONSTRAINED"    # still rising — extrapolation would be fabricated
    if b <= 0 or c <= 0:
        return None, "FIT_FAILED"
    return float(math.log(b / (a - target)) / c), "EXTRAPOLATED"


def route_segmentation(ctx: "Ctx", fast: bool, seed: int,
                       params: Optional[dict] = None) -> Dict[str, object]:
    p = {"fractions": [0.3, 0.6, 1.0] if fast else [0.25, 0.4, 0.55, 0.7, 0.85, 1.0],
         "replicates": 1 if fast else 3, "dp_iters": 4}
    if params:
        p.update(params)
    la = ctx.la_corpus
    points = []
    for fi, frac in enumerate(p["fractions"]):
        reps = 1 if frac >= 1.0 else p["replicates"]
        for rep in range(reps):
            rng = _rng(seed, "segmentation", fi, rep)
            if frac >= 1.0:
                sub = list(la)
            else:
                idx = rng.permutation(len(la))[:int(round(frac * len(la)))]
                sub = [la[i] for i in sorted(idx)]
            br = M.boundary_recovery(sub, seed=seed, dp_iters=p["dp_iters"],
                                     use_morfessor=False)
            points.append({"fraction": frac, "rep": rep,
                           "word_tokens": sum(len(i.words) for i in sub),
                           "micro_f1": br["segmenters"]["dp_unigram"]["micro_f1"],
                           "random_f1": br["random_baseline"]["micro_f1"]})
    fit = fit_saturating([pt["word_tokens"] for pt in points],
                         [pt["micro_f1"] for pt in points])
    thr, status = segmentation_threshold(fit)
    return {
        "title": "Segmentation headroom (descending-subsample F1, saturating extrapolation)",
        "native_axis": "la_word_tokens",
        "native_now_marker": ctx.units["la_word_tokens_now"],
        "closed_result": ("published micro-F1 0.436 vs 0.389 random stands (site-clustered gap "
                          "CI excludes 0); supervised headroom 0.62-0.66 "
                          "(experiments/segmentation_extension)"),
        "method": ("LA doc-subsample curve of morphology.boundary_recovery (dp_unigram, "
                   "leave-one-site-out) at descending fractions; saturating fit "
                   "F1(N) = a - b*exp(-c*N); extrapolate to the "
                   f"{SUPERVISED_HEADROOM_F1} supervised-headroom target — an asymptote at/"
                   "below target REFUSES a threshold"),
        "params": {**p, "target_f1": SUPERVISED_HEADROOM_F1},
        "curve": points,
        "fit": None if fit is None else {"asymptote_a": round(fit[0], 4),
                                         "b": round(fit[1], 4), "c": round(fit[2], 8)},
        "threshold_native": None if thr is None else round(thr, 1),
        "threshold_note": status, "status": status,
        "reopen_at": convert_threshold(thr, ctx.units),
        "structural_reopen_event": (
            None if thr is not None else
            ("unsupervised F1 saturates below the supervised-headroom target: the gap is "
             "model-class/structure, not corpus size — reopen on a method advance or a "
             "word-length-structure shift, not on token count") if status == "ASYMPTOTE_LIMITED"
            else "the descending-subsample curve does not constrain a saturating asymptote at "
                 "current size (F1 still rising / fit degenerate): no honest extrapolation "
                 "exists — re-fit when new corpus lands"),
        "caveats": [
            f"micro-F1 has a {ALL_BOUNDARIES_F1_CEILING} all-boundaries ceiling on this corpus "
            "— check cut-rate before reading any gain as structure "
            "(experiments/segmentation_extension)",
            "status is EXTRAPOLATED at best: a fitted crossing is a planning number, never a "
            "measurement",
            "dp_unigram-only curve (deterministic); the published 0.436 is the reference point",
        ],
        "phantom_sensitivity": _phantom_distance_row(thr, ctx.units),
        "info_budget": _panel(
            raw_corpus_size=ctx.units["la_word_tokens_now"],
            effective_independent_evidence=len({i.site for i in la}),
            parameter_count=3, search_space_size=len(p["fractions"]),
            source_dependency_structure="L_LA_CORPUS silver (single lineage)",
            damage_rate=_la_damage_rate(ctx),
            minimum_detectable_effect=f"micro-F1 {SUPERVISED_HEADROOM_F1}"),
    }


# --------------------------------------------------------------------------- #
# Route 7 — anchor foothold (pure counting; lineage-collapsed; event tripwire)
# --------------------------------------------------------------------------- #
def parse_census(path: str = CENSUS_PATH) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def anchor_counts(rows: Sequence[Dict[str, str]],
                  foothold_slots: int = FOOTHOLD_SLOTS) -> Dict[str, object]:
    """Mechanical counting of the anchor census. An anchor qualifies for the lattice at
    >= foothold_slots covered signs, not debunked, not fringe-flagged."""
    by_class: Counter = Counter()
    slots = []
    qualifying = []
    for r in rows:
        n_slots = len([s for s in r["covered_signs"].split(",") if s.strip()])
        slots.append(n_slots)
        by_class[r["class"]] += 1
        if (n_slots >= foothold_slots and r.get("sm_trust", "") != "debunked"
                and r.get("fringe_flag", "false").strip().lower() != "true"):
            qualifying.append(r["anchor_id"])
    return {"census_rows": len(rows), "rows_by_class": dict(sorted(by_class.items())),
            "max_covered_slots": max(slots) if slots else 0,
            "eight_slot_anchors": len(qualifying),
            "eight_slot_anchor_ids": qualifying}


def route_anchors(ctx: "Ctx", fast: bool, seed: int,
                  params: Optional[dict] = None) -> Dict[str, object]:
    rows = parse_census()
    counts = anchor_counts(rows)
    # Art. XI lineage collapse: every census identification routes through the LB sound-value
    # transfer (S&M 2017 / Younger equations) on GORILA-tradition LA readings — one
    # identification lineage, mechanically confirmed via source_dependency.
    id_sources = ["SRC-DECIPHERMENT-1952", "SRC-DAMOS", "SRC-VC-DOCS2"]
    conc = source_dependency.concordance(id_sources)
    independent_8slot = min(counts["eight_slot_anchors"], conc["effective_n"]) \
        if counts["eight_slot_anchors"] else 0
    # watched events from the corpus-completeness sweep (generated, invariant 12)
    watched = []
    if os.path.exists(MISSING_PATH):
        for r in csv.DictReader(open(MISSING_PATH, encoding="utf-8")):
            if r.get("class") == "c_pending_edition":
                watched.append(r["designation"])
    return {
        "title": "Anchor foothold (independent 8-slot anchors; event tripwire)",
        "native_axis": "independent_lineage_anchors", "convertible": False,
        "native_now_marker": independent_8slot,
        "closed_result": ("cross-script gate REFUTE_LOTO_FRAGILE (prereg DOI "
                          "10.5281/zenodo.21168887): pins I+RI each one-toponym-deep; "
                          "anchor-lattice pricing: decipherment needs ~12 distinct-lineage "
                          "8-slot anchors, foothold 2-3; LA at ~0"),
        "method": ("pure counting from experiments/crossscript_gate/phase2/anchor_census.csv; "
                   f"a lattice anchor needs >= {FOOTHOLD_SLOTS} covered sign slots, not "
                   "debunked, not fringe; independence = Art. XI lineage collapse "
                   "(source_dependency.concordance over the identification sources)"),
        "params": {"foothold_slots": FOOTHOLD_SLOTS, "needed_foothold": list(NEEDED_FOOTHOLD),
                   "needed_decipherment": NEEDED_DECIPHERMENT},
        "census": counts,
        "identification_lineage": {
            "sources": id_sources, "effective_votes": conc["effective_n"],
            "verdict": conc["verdict"],
            "note": "all census equations route through the Ventris value transfer: their "
                    "agreement is ONE evidentiary vote (Art. XI), so new anchors only count "
                    "when they arrive through a DIFFERENT lineage"},
        "independent_eight_slot_anchors": independent_8slot,
        "threshold_native": float(NEEDED_FOOTHOLD[0]),
        "threshold_note": (f"reopen at >= {NEEDED_FOOTHOLD[0]} independent {FOOTHOLD_SLOTS}-slot "
                           f"anchors (foothold {NEEDED_FOOTHOLD[0]}-{NEEDED_FOOTHOLD[1]}; "
                           f"decipherment ~{NEEDED_DECIPHERMENT})"),
        "status": "EVENT_COUNT",
        "reopen_at": None,
        "trigger": {
            "event": "new_site_toponym_candidates",
            "operational_definition": (
                "a newly PUBLISHED LA inscription (editor-printed transliteration only — the "
                "no-reading-from-photographs rule stands) from a site whose ancient name is "
                "independently attested outside the LB decipherment lineage, containing a "
                "recurring (>=2 attestations) word type of >=3 signs in heading/list position "
                "that an editor identifies as a name parallel; each candidate becomes an "
                "anchor_census.csv row BEFORE any grading, and grading requires a NEW prereg"),
            "watched_pending_editions": len(watched),
            "watched_designations": watched,
        },
        "caveats": [
            "an anchor census row is a CANDIDATE, never a pin: the cross-script gate verdict "
            "(REFUTE_LOTO_FRAGILE) stands until a NEW preregistered run says otherwise",
            "census identifications may rest on damaged attestations (underdotted forms); "
            "D1 damage flags are not yet joined to census rows — noted, out of scope here",
        ],
        "phantom_sensitivity": {"approx": bool(ctx.phantom["approx"]),
                                "note": "route counts anchors, not tokens; D1 phantom "
                                        "exclusion does not move the anchor count"},
        "info_budget": _panel(
            raw_corpus_size=counts["census_rows"],
            effective_independent_evidence=conc["effective_n"],
            parameter_count=0, search_space_size=1,
            source_dependency_structure=conc["verdict"],
            damage_rate=_la_damage_rate(ctx),
            minimum_detectable_effect=f">= {NEEDED_FOOTHOLD[0]} independent "
                                      f"{FOOTHOLD_SLOTS}-slot anchors"),
    }


# --------------------------------------------------------------------------- #
# Info-budget panel helper (Art. IX — reported; no graduating claim is made here)
# --------------------------------------------------------------------------- #
def _panel(**fields) -> Dict[str, object]:
    panel = info_budget.build_panel(**fields)
    panel["_note"] = ("Art. IX panel, reported for visibility; thresholds are planning "
                      "numbers (L0) — nothing here graduates a claim")
    return panel


def _la_damage_rate(ctx: "Ctx") -> float:
    ph = ctx.phantom
    return round(ph["damage_touching_tokens"] / ph["word_tokens"], 4)


# --------------------------------------------------------------------------- #
# Context + top-level compute
# --------------------------------------------------------------------------- #
class Ctx:
    """Lazy shared data context (LA silver, LB DĀMOS, D1 phantom info, units)."""

    def __init__(self, annex_path: str = ANNEX_PATH):
        self._la: Optional[List[M.Inscription]] = None
        self._lb: Optional[List[M.Inscription]] = None
        self._phantom: Optional[Dict[str, object]] = None
        self._units: Optional[Dict[str, object]] = None
        self._annex_path = annex_path

    @property
    def la_corpus(self) -> List[M.Inscription]:
        if self._la is None:
            if not os.path.exists(M.DEFAULT_SILVER):
                raise FileNotFoundError(f"LA silver not present: {M.DEFAULT_SILVER}")
            self._la = M.load_corpus()
        return self._la

    @property
    def lb_corpus(self) -> List[M.Inscription]:
        if self._lb is None:
            if not os.path.exists(LBC.DAMOS):
                raise FileNotFoundError(f"DĀMOS not present: {LBC.DAMOS}")
            self._lb = LBC.load_linb()
        return self._lb

    @property
    def phantom(self) -> Dict[str, object]:
        if self._phantom is None:
            self._phantom = load_phantom(self._annex_path)
        return self._phantom

    @property
    def units(self) -> Dict[str, object]:
        if self._units is None:
            la = self.la_corpus if os.path.exists(M.DEFAULT_SILVER) else None
            self._units = compute_units(la, self.phantom)
        return self._units


@dataclass(frozen=True)
class RouteSpec:
    name: str
    fn: Callable
    needs: Tuple[str, ...]         # data dependencies, for fail-loud messages
    convertible: bool = True


ROUTES: Dict[str, RouteSpec] = {
    "morphology": RouteSpec("morphology", route_morphology, ("la", "lb")),
    "h2_entropy": RouteSpec("h2_entropy", route_h2, ("la", "lb")),
    "alternation_grid": RouteSpec("alternation_grid", route_alternation, ("la", "lb")),
    "vowel_harmony": RouteSpec("vowel_harmony", route_vowel_harmony, ("la",)),
    "phonology_cv": RouteSpec("phonology_cv", route_phonology_cv, ("la", "lb")),
    "segmentation": RouteSpec("segmentation", route_segmentation, ("la",)),
    "anchors": RouteSpec("anchors", route_anchors, (), convertible=False),
}

ARTICLES = ("Art. VIII (evidence sizing), Art. IX (info-budget panels, reported), "
            "Art. XI (route-7 lineage collapse), Art. XVII (append-only: no threshold "
            "reopens a closed verdict), Art. XXII (stage header)")


def compute(routes: Optional[Sequence[str]] = None, fast: bool = False, seed: int = 0,
            annex_path: str = ANNEX_PATH) -> Dict[str, object]:
    names = list(routes) if routes else list(ROUTE_ORDER)
    unknown = [n for n in names if n not in ROUTES]
    if unknown:
        raise KeyError(f"unknown route(s): {unknown}; valid: {ROUTE_ORDER}")
    ctx = Ctx(annex_path=annex_path)
    out_routes: Dict[str, object] = {}
    for name in ROUTE_ORDER:
        if name not in names:
            continue
        out_routes[name] = ROUTES[name].fn(ctx, fast, seed)
    return {
        "version": VERSION,
        "generated_by": "scripts/reopening_thresholds.py",
        "articles": ARTICLES,
        "seed": int(seed),
        "fast": bool(fast),
        "routes_computed": [n for n in ROUTE_ORDER if n in names],
        "units": ctx.units,
        "routes": out_routes,
        "trigger_protocol": {
            "watch_doc": WATCH_DOC,
            "rule": ("a crossing of any 'reopen at' value MANDATES a NEW pre-registration "
                     "(new plan_hash, new external timestamp) BEFORE any re-run — a crossing "
                     "is never an automatic claim and never reopens a closed verdict "
                     "(Art. XVII)"),
            "detection_target": DETECTION_TARGET,
        },
        "compliance": ("stage cites " + ARTICLES + "; counts generated by this script "
                       "(invariant 12); scripts/verdict.py not imported (invariants 2/4); "
                       "silver untouched (sidecar reads only)"),
    }


# --------------------------------------------------------------------------- #
# Markdown rendering — a PURE function of the results JSON
# --------------------------------------------------------------------------- #
def _fmt_reopen(route: Dict[str, object]) -> Tuple[str, str, str]:
    """(reopen-at cell, new-docs cell, zg57 cell) for the summary table."""
    if route.get("status") == "EVENT_COUNT":
        note = route.get("threshold_note", "")
        return (note or "event count", "n/a", "n/a")
    ra = route.get("reopen_at")
    if ra is None:
        return ("— (" + str(route.get("status")) + ")", "—", "—")
    return (f"{ra['la_word_tokens']:,.0f}", f"+{ra['approx_new_docs']:,.0f}",
            f"{ra['approx_kn_zg57_equivalents']:,.1f}")


def render_doc(result: Dict[str, object]) -> str:
    u = result["units"]
    ph = u["phantom_sensitivity"]
    L: List[str] = []
    L.append("<!-- GENERATED FILE — DO NOT EDIT BY HAND.")
    L.append("     Source of truth: results/reopening_thresholds.json")
    L.append("     Regenerate: PYTHONPATH=. python3 scripts/reopening_thresholds.py "
             "--render-only --write-doc -->")
    L.append("")
    L.append("# Reopening thresholds — mechanical tripwires for the closed Linear A routes")
    L.append("")
    L.append(f"*Generated by `{result['generated_by']}` ({result['version']}, "
             f"seed {result['seed']}, fast={str(result['fast']).lower()}). "
             f"Constitution: {result['articles']}.*")
    L.append("")
    L.append("A threshold here is a **planning number (L0)** — no claim about Linear A is "
             "made. A crossing means \"the route is worth re-running under a NEW "
             "pre-registration\"; it never auto-generates a claim, never reopens a closed "
             "verdict (Art. XVII), and Linear-B-analogue thresholds are optimistic lower "
             "bounds: a crossing means *re-runnable*, never *identifiable*.")
    L.append("")
    L.append("## Unit system (canonical axis: LA word tokens)")
    L.append("")
    L.append("| quantity | value |")
    L.append("|---|---|")
    L.append(f"| LA documents now | {u['la_docs_now']:,} |")
    L.append(f"| LA word tokens now | {u['la_word_tokens_now']:,} |")
    L.append(f"| LA sign tokens now | {u['la_sign_tokens_now']:,} |")
    L.append(f"| signs / word | {u['signs_per_word']} |")
    L.append(f"| word tokens / document | {u['tokens_per_doc']} |")
    L.append(f"| KN Zg 57 (ivory ring, ~{u['kn_zg57_signs_est']} signs) | "
             f"≈ {u['kn_zg57_word_token_equiv']} word tokens |")
    L.append(f"| D1 phantom-excluded word tokens | {ph['la_word_tokens_excl_phantoms']:,} "
             f"({ph['phantom_word_tokens']} tokens of {ph['phantom_types']} phantom types"
             f"{'; APPROX — annex absent' if ph['approx'] else ''}) |")
    L.append(f"| distinct word types | {ph['distinct_types']:,} "
             f"({ph['types_excl_phantoms']:,} excluding phantoms) |")
    L.append("")
    L.append("## Summary — reopen-at per route")
    L.append("")
    L.append("| route | status | native threshold | reopen at (LA word tokens) | "
             "≈ new docs | ≈ KN Zg 57s |")
    L.append("|---|---|---|---|---|---|")
    for name in [n for n in ROUTE_ORDER if n in result["routes"]]:
        r = result["routes"][name]
        thr = r.get("threshold_native")
        thr_s = "None" if thr is None else f"{thr:,}"
        cell, docs, zg = _fmt_reopen(r)
        L.append(f"| {name} | {r['status']} | {thr_s} ({r['native_axis']}) | "
                 f"{cell} | {docs} | {zg} |")
    L.append("")
    for name in [n for n in ROUTE_ORDER if n in result["routes"]]:
        r = result["routes"][name]
        L.append(f"## {name} — {r['title']}")
        L.append("")
        L.append(f"- **closed result:** {r['closed_result']}")
        L.append(f"- **method:** {r['method']}")
        L.append(f"- **status:** `{r['status']}` (threshold note: {r.get('threshold_note')})")
        thr = r.get("threshold_native")
        L.append(f"- **native threshold:** "
                 f"{'None' if thr is None else format(thr, ',')} ({r['native_axis']})")
        ra = r.get("reopen_at")
        if ra is not None:
            L.append(f"- **reopen at:** {ra['la_word_tokens']:,.0f} LA word tokens "
                     f"(+{ra['additional_word_tokens']:,.0f} tokens ≈ "
                     f"{ra['approx_new_docs']:,.0f} new docs ≈ "
                     f"{ra['approx_kn_zg57_equivalents']:,.1f} KN-Zg-57-equivalents)")
        if r.get("structural_reopen_event"):
            L.append(f"- **structural reopen event:** {r['structural_reopen_event']}")
        if name == "anchors":
            c = r["census"]
            L.append(f"- **census:** {c['census_rows']} rows "
                     f"({', '.join(f'{k} {v}' for k, v in c['rows_by_class'].items())}); "
                     f"max covered slots {c['max_covered_slots']}; "
                     f"{FOOTHOLD_SLOTS}-slot anchors: {c['eight_slot_anchors']}; "
                     f"independent {FOOTHOLD_SLOTS}-slot anchors: "
                     f"{r['independent_eight_slot_anchors']} "
                     f"(identification lineage: {r['identification_lineage']['verdict']}, "
                     f"{r['identification_lineage']['effective_votes']} effective vote)")
            L.append(f"- **trigger event:** `{r['trigger']['event']}` — "
                     f"{r['trigger']['operational_definition']}")
            L.append(f"- **watched pending editions:** "
                     f"{r['trigger']['watched_pending_editions']} items "
                     f"(missing_items.csv class `c_pending_edition`), headline: "
                     f"{', '.join(r['trigger']['watched_designations'][:4])}, …")
        if "curve" in r and name in ("morphology", "phonology_cv"):
            L.append("")
            L.append("| size (LB word tokens) | detection rate |")
            L.append("|---|---|")
            for c in r["curve"]:
                L.append(f"| {c['size']:,} | {c['detection_rate']} |")
        if "curve" in r and name == "vowel_harmony":
            L.append("")
            L.append("| k (× corpus) | LA word tokens | power |")
            L.append("|---|---|---|")
            for c in r["curve"]:
                L.append(f"| {c['k']} | {c['la_word_tokens']:,} | {c['power']} |")
            L.append("")
            L.append(f"unplanted false-positive rate at k={r['params']['k_grid'][-1]}: "
                     f"{r['false_positive_rate_unplanted']}")
        if "curve" in r and name == "segmentation":
            L.append("")
            L.append("| fraction | word tokens | micro-F1 | random |")
            L.append("|---|---|---|---|")
            for c in r["curve"]:
                L.append(f"| {c['fraction']} | {c['word_tokens']:,} | {c['micro_f1']} | "
                         f"{c['random_f1']} |")
            if r.get("fit"):
                L.append("")
                L.append(f"saturating fit asymptote a = {r['fit']['asymptote_a']} "
                         f"(target {r['params']['target_f1']})")
        if name == "h2_entropy":
            cal = r["lb_calibration"]
            fitla = r["la_fit"]
            L.append("")
            L.append(f"- LB calibration: H2_ref {cal['lb_H2_ref_bits']} bits, stabilization "
                     f"at {cal['lb_stabilization_sign_tokens']} sign tokens → empirical "
                     f"c_min {cal['c_min_empirical_obs_per_cell']} obs/cell")
            L.append(f"- LA fit: V={fitla['V_now']} signs at {fitla['sign_tokens_now']:,} "
                     f"sign tokens; obs/cell now {fitla['obs_per_cell_now']}; Heaps "
                     f"K={fitla['heaps_K']}, β={fitla['heaps_beta']}; "
                     f"N* = {fitla['n_star_sign_tokens']} sign tokens "
                     f"({fitla['shortfall_orders_of_magnitude']} orders of magnitude away)")
            sr = r["sensitivity_restricted_inventory"]
            L.append(f"- restricted-inventory sensitivity (V={sr['V_fixed']}): N* = "
                     f"{sr['n_star_sign_tokens_empirical_cmin']} (empirical c_min) / "
                     f"{sr['n_star_sign_tokens_classical']} (classical ≥"
                     f"{CLASSICAL_OBS_PER_CELL:g}/cell) sign tokens")
        if name == "alternation_grid":
            la = r["la"]
            o = la["observed"]
            L.append("")
            L.append(f"- observed now: {o['stem_sharing_pair_events']} stem-sharing pair "
                     f"events, {o['doubly_attested_pairs']} doubly-attested pairs, "
                     f"{o['grid_supported_signs']} grid-supported signs (G={GRID_SUPPORT_G})")
            L.append(f"- model calibration factor {la['calibration_factor']}; LB shape "
                     f"check (observed vs model grid-supported signs): " +
                     "; ".join(f"{c['lb_word_tokens']:,}: {c['observed_grid_supported_signs']}"
                               f" vs {c['model_grid_supported_signs']}"
                               for c in r["lb_shape_check"]))
        L.append("")
        phr = r.get("phantom_sensitivity", {})
        L.append(f"- **D1 phantom sensitivity:** " +
                 "; ".join(f"{k}={phr[k]}" for k in sorted(phr) if k != "note") +
                 (f" — {phr['note']}" if phr.get("note") else ""))
        if r.get("caveats"):
            L.append("- **caveats:** " + " | ".join(r["caveats"]))
        L.append("")
    L.append("## Trigger protocol — wiring into the Anetaki II watch")
    L.append("")
    tp = result["trigger_protocol"]
    L.append(f"The `reopen at` column above is part of the trigger protocol of "
             f"`{tp['watch_doc']}`: when newly published corpus (e.g. the KN Zg 57/58 "
             f"editions) moves the corpus across a route's reopen-at value — or when the "
             f"anchors route's event tripwire fires — **{tp['rule']}**.")
    L.append("")
    L.append(f"*Compliance: {result['compliance']}.*")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--route", default=None,
                    help=f"comma-separated subset of {ROUTE_ORDER} (default: all)")
    ap.add_argument("--fast", action="store_true",
                    help="reduced grids/nulls for iteration; recorded as fast:true — "
                         "a fast JSON cannot impersonate published numbers")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=RESULTS_PATH)
    ap.add_argument("--doc", default=DOC_PATH)
    ap.add_argument("--write-doc", action="store_true",
                    help="also render docs/reopening-thresholds.md from the JSON")
    ap.add_argument("--render-only", action="store_true",
                    help="do not compute; render the doc from the existing JSON")
    args = ap.parse_args(argv)

    if args.render_only:
        if not os.path.exists(args.out):
            sys.stderr.write(f"no results JSON at {args.out}\n")
            return 2
        result = json.load(open(args.out, encoding="utf-8"))
        with open(args.doc, "w", encoding="utf-8") as f:
            f.write(render_doc(result))
        print(f"doc -> {args.doc}")
        return 0

    routes = [r.strip() for r in args.route.split(",")] if args.route else None
    result = compute(routes=routes, fast=args.fast, seed=args.seed)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print(f"results -> {args.out} (fast={result['fast']}, routes={result['routes_computed']})")
    for name in result["routes_computed"]:
        r = result["routes"][name]
        cell, docs, zg = _fmt_reopen(r)
        print(f"  {name:<18} {r['status']:<20} reopen at: {cell}"
              + (f"  (~{docs} docs, {zg} Zg57s)" if docs not in ("—", "n/a") else ""))
    if args.write_doc:
        with open(args.doc, "w", encoding="utf-8") as f:
            f.write(render_doc(result))
        print(f"doc -> {args.doc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
