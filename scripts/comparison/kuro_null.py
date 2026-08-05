#!/usr/bin/env python3
"""kuro_null.py — arithmetic-anchor harness: KU-RO / KI-RO summation-FUNCTION permutation null.

WHAT THIS TESTS (and the only thing it tests). On the accounting tablets, a KU-RO line closes a
run of line items and carries a number; the testable question is purely arithmetic: does the number
on the closing line equal the sum of the item numbers ("own-sum exact match"), and does that match
count exceed what random pairing of closing-line numbers with sections would produce? This probes
KU-RO as a summation-FUNCTION sign (claim layer L2/L3, functional role). It is NOT a translation:
the word "total" appears in this module only as metrology.py's internal field name (`total_int`),
never as a semantic claim. KI-RO gets ITS OWN identical-design leg (see below).

DESIGN. Built ON scripts/comparison/metrology.py's parsing — `_stream_to_tokens`,
`load_tablets` (called here with WIDENED scope: site_prefix=""/horizon="" so every KU-RO document
is testable, not just HT/LM I), `parse_tablet` (the arithmetic authority for balance units), and
`corpus_io_structured.line_items` as the light doc-level cross-check path. Nothing is re-parsed:
this module's line-walker (`units_with_words`, needed only to attach word-token ordinals for the
damage breakdown) is cross-validated on every run against `parse_tablet`'s output and raises on
any drift.

THE STATISTIC. Per leg (KU-RO; KI-RO separately): observed = number of balance units whose item
integers sum EXACTLY to the closing-line integer. Null = the closing-line integers deranged across
the units (multiset preserved; a unit never keeps its own closing number — self-pair excluded), 2,000
trials, seed 20260805. The EMPIRICAL permutation p is the primary statistic; a Gaussian z is
reported SECONDARY only (the null is near-Poisson — Gaussianizing it, as Tsirkas's published
z=+13.4 does, overstates precision). Units whose closing line carries no numeral are EXCLUDED from
the statistic (a lost numeral can attest nothing; 0==0 pseudo-hits are not matches) and counted.

KI-RO IDENTICAL-DESIGN LEG (improvement over Tsirkas's raw 0/7 count). The KI-RO leg swaps the
two labels in the token stream and reuses the SAME parser: KI-RO lines close accumulations exactly
as KU-RO lines do in the primary leg, and KU-RO lines are skipped exactly as KI-RO lines are
skipped there. A raw count like 0/7 is uninterpretable without its chance floor; here KI-RO's
observed count faces its own derangement null. (Corpus fact, reported per-unit: KI-RO lines often
HEAD their lists rather than close them, so the closing-design observed count is expected low for
structural reasons too — the null contextualizes it; no directional claim is made.)

FRACTIONS ARE COMPARISON-ONLY (metrology.py's own discipline). Integer arithmetic is the primary
match criterion. Fraction-bearing units are counted and reported separately; a SECONDARY
"exact with editorial fractions" figure evaluates the balance under the editorial vulgar-fraction
glosses via metrology.editorial_value — editorial/Corazza values are never fed to the permutation
statistic.

DAMAGE-AWARE BREAKDOWN. Balance-unit lines are mapped to corpus/silver/damage_annex.json (Tsirkas
D1 sidecar) through silver stream word order: the k-th `label` token of a document is the k-th
annex word token. Mismatched vs matched units are split by whether any of their word tokens carries
an L/T/I damage code. Caveat: the annex covers WORD tokens only; damaged NUMERALS (Tsirkas's own
mismatch driver: 9/13 of his KU-RO mismatches involved damage-flagged numerals) appear here only as
the doc-level count of standalone illegible-number marks (U+1076B `other` tokens in the stream).

CROSS-LINEAGE SANITY (reported, NOT asserted): Tsirkas 2026 published, on HIS corpus model,
KU-RO 10/26 exact (38%) vs null 0.52±0.71 (z=+13.4) and KI-RO 0/7 raw. Ours should agree in
DIRECTION and MAGNITUDE CLASS only — the section models and corpus scopes differ; equality is
neither expected nor tested.

Constitution: Art. IV (deterministic arithmetic, no LLM anywhere), Art. V (claim layer L2/L3 —
functional role only), Art. VII/VIII (the statistic is a single pre-stated criterion; no criterion
shopping), Art. XI (Tsirkas credit: github.com/ChristosTsirkas/corpus-validation-for-undeciphered-
scripts-linear-a; record docs/2026-08-05-tsirkas-full-repo-audit.md §4), Art. XXII (this header).
Imports nothing from scripts.verdict (signals only). Deterministic for a fixed seed.

    python3 scripts/comparison/kuro_null.py [--path SILVER] [--trials N] [--seed N] [--out JSON]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.comparison import metrology  # noqa: E402
from scripts.corpus_io_structured import line_items  # noqa: E402

SILVER = metrology.SILVER
ANNEX = os.path.join(_ROOT, "corpus", "silver", "damage_annex.json")
OUT = os.path.join(_ROOT, "results", "kuro_null.json")
MARKER = "\U0001076b"          # break/lacuna + illegible-number mark (Tsirkas D1)
SEED = 20260805
N_TRIALS = 2000

CLAIM_LAYER = ("L2/L3 — KU-RO/KI-RO tested as summation-FUNCTION signs (arithmetic role only); "
               "no phonetic, lexical or translation claim; 'total_int' below is metrology.py's "
               "internal field name, not a reading")

# Tsirkas 2026 published values on HIS corpus model — CITED constants for the cross-lineage sanity
# block only (allowed hand-written: they are his published numbers, not our counts).
TSIRKAS_PUBLISHED = {
    "kuro_exact": [10, 26],
    "kuro_null_mean": 0.52,
    "kuro_null_sd": 0.71,
    "kuro_z": 13.4,
    "kiro_raw": [0, 7],
    "source": ("Tsirkas 2026, corpus-validation-for-undeciphered-scripts-linear-a; "
               "logos record: docs/2026-08-05-tsirkas-full-repo-audit.md"),
    "comparison_contract": ("direction + magnitude-class agreement only — section models and "
                            "corpus scopes differ; equality is neither expected nor tested"),
}


# --------------------------------------------------------------------------- #
# Units with word-token ordinals (shadow of parse_tablet, cross-validated)
# --------------------------------------------------------------------------- #
def swap_roles(tokens: Sequence[dict]) -> List[dict]:
    """Copy of a metrology token stream with the KU-RO and KI-RO labels exchanged — the KI-RO
    identical-design leg: KI-RO closes accumulations exactly as KU-RO does in the primary leg."""
    swap = {"KU-RO": "KI-RO", "KI-RO": "KU-RO"}
    return [dict(t, s=swap[t["s"]]) if t.get("k") == "label" and t.get("s") in swap else t
            for t in tokens]


def units_with_words(tablet: dict, commodities: set) -> List[dict]:
    """metrology.parse_tablet's balance units AUGMENTED with (a) the word-token ordinals of the
    lines each unit totals (ordinal = position among the doc's `label` tokens = silver stream word
    order = damage-annex index) and (b) whether the closing line carried a numeral. The walk
    mirrors parse_tablet line-for-line; `_assert_matches_metrology` locks the two on every call —
    metrology stays the arithmetic authority (nothing is re-parsed on trust)."""
    toks: List[dict] = []
    wi = 0
    for t in tablet["tokens"]:
        if t.get("k") == "label":
            toks.append(dict(t, _wi=wi))
            wi += 1
        else:
            toks.append(t)
    lines: List[List[dict]] = []
    cur: List[dict] = []
    for t in toks:
        if t["k"] == "nl":
            if cur:
                lines.append(cur)
                cur = []
        else:
            cur.append(t)
    if cur:
        lines.append(cur)

    acc: Dict[Optional[str], List[Tuple[int, List[str], List[int]]]] = defaultdict(list)
    order: List[Optional[str]] = []
    column_commodity: Optional[str] = None
    units: List[dict] = []

    def push(commod, ival, fracs, ords):
        acc[commod].append((ival, list(fracs), list(ords)))
        if commod not in order:
            order.append(commod)

    for ln in lines:
        labels = [t["s"] for t in ln if t["k"] == "label"]
        ords = [t["_wi"] for t in ln if t["k"] == "label"]
        is_total = "KU-RO" in labels
        is_deficit = ("KI-RO" in labels) and not is_total
        commod_labels = [t["s"] for t in ln if t["k"] == "label"
                         and metrology._base_commodity(t["s"], commodities)]
        commod = metrology._base_commodity(commod_labels[0], commodities) if commod_labels else None
        ints = [t["v"] for t in ln if t["k"] == "num"]
        fracs = [t["s"] for t in ln if t["k"] == "frac"]

        if is_total:
            total_int = ints[0] if ints else 0
            if commod is not None and commod in acc:
                items = acc.pop(commod)
                order[:] = [o for o in order if o != commod]
            else:
                items = [it for cm in order for it in acc.get(cm, [])]
                acc.clear()
                order.clear()
            word_ords = sorted(set(ords) | {o for _, _, oo in items for o in oo})
            units.append({"doc": tablet["doc"], "commodity": commod, "total_int": total_int,
                          "total_fracs": fracs, "items": [(iv, ff) for iv, ff, _ in items],
                          "total_has_num": bool(ints), "word_ords": word_ords})
        elif is_deficit:
            continue
        else:
            if commod is not None:
                column_commodity = commod
            use_c = commod if commod is not None else column_commodity
            if ints:
                push(use_c, ints[0], fracs, ords)
            elif fracs:
                push(use_c, 0, fracs, ords)
    _assert_matches_metrology(tablet, commodities, units)
    return units


def _assert_matches_metrology(tablet: dict, commodities: set, units: Sequence[dict]) -> None:
    """Hard lock: the augmented units, stripped to metrology's skeleton, must equal
    parse_tablet's output exactly. Any drift is a bug in this module, never in metrology."""
    ref = metrology.parse_tablet(tablet, commodities)
    mine = [{"doc": u["doc"], "commodity": u["commodity"], "total_int": u["total_int"],
             "total_fracs": u["total_fracs"], "items": [(iv, ff) for iv, ff in u["items"]]}
            for u in units]
    norm = lambda us: [dict(u, items=[(iv, list(ff)) for iv, ff in u["items"]]) for u in us]
    if norm(mine) != norm(ref):
        raise RuntimeError(f"units_with_words drifted from metrology.parse_tablet on "
                           f"{tablet['doc']} — fix the shadow walker")


# --------------------------------------------------------------------------- #
# Match criteria
# --------------------------------------------------------------------------- #
def integer_exact(unit: dict) -> bool:
    """PRIMARY criterion: item integers sum exactly to the closing-line integer
    (metrology.residual_terms const == 0). Fraction signs play no part."""
    return metrology.residual_terms(unit)[0] == 0


def editorial_exact(unit: dict) -> Optional[bool]:
    """SECONDARY, COMPARISON-ONLY: does the unit balance exactly when every fraction sign is read
    at its editorial vulgar-fraction gloss (metrology.editorial_value)? None if the unit bears no
    fractions or any sign has no editorial numeric. Never enters the permutation statistic."""
    const, coef = metrology.residual_terms(unit)
    if not coef:
        return None
    total = Fraction(const)
    for sign, c in coef.items():
        ev = metrology.editorial_value(sign)
        if ev is None:
            return None
        total += c * ev
    return total == 0


# --------------------------------------------------------------------------- #
# The permutation null: closing numbers deranged across units
# --------------------------------------------------------------------------- #
def derangement(rng: np.random.Generator, n: int) -> np.ndarray:
    """Uniform random permutation of range(n) with NO fixed point (rejection sampling — expected
    ~e draws). A unit is never paired with its own closing number; the multiset of closing numbers
    is preserved by construction."""
    if n < 2:
        raise ValueError("derangement needs n >= 2")
    idx = np.arange(n)
    while True:
        p = rng.permutation(n)
        if not np.any(p == idx):
            return p


def null_hits(item_sums: Sequence[int], closing: Sequence[int],
              n_trials: int, seed: int) -> List[int]:
    """Per-trial exact-match counts with the closing numbers deranged across the units."""
    s = np.asarray(item_sums)
    t = np.asarray(closing)
    rng = np.random.default_rng(seed)
    return [int(np.sum(s == t[derangement(rng, len(s))])) for _ in range(n_trials)]


def null_summary(obs: int, hits: Sequence[int]) -> dict:
    arr = np.asarray(hits, dtype=float)
    sd = float(arr.std())
    p = (1 + int(np.sum(arr >= obs))) / (1 + len(arr))
    return {
        "design": ("closing numbers deranged across balance units — multiset preserved, "
                   "self-pair excluded"),
        "n_trials": len(hits),
        "mean": round(float(arr.mean()), 4),
        "sd": round(sd, 4),
        "max": int(arr.max()),
        "p_empirical_primary": round(p, 6),
        "z_secondary": round((obs - float(arr.mean())) / sd, 2) if sd > 0 else None,
        "z_caveat": "z Gaussianizes a near-Poisson null; the empirical p is the statistic",
    }


# --------------------------------------------------------------------------- #
# Damage mapping (Tsirkas D1 annex, word tokens only)
# --------------------------------------------------------------------------- #
def load_annex(path: str = ANNEX) -> Optional[dict]:
    if not os.path.exists(path):
        return None
    return json.load(open(path, encoding="utf-8"))["docs"]


def damage_codes_for(tablet: dict, annex_docs: Optional[dict]) -> Tuple[Optional[List[str]], str]:
    """Damage codes aligned to the tablet's label tokens via silver stream word order. The k-th
    label of the doc is the k-th annex word token; the annex `types` column must agree with the
    label strings exactly, else the doc is reported MISALIGNED and gets no damage data."""
    if annex_docs is None:
        return None, "ANNEX_ABSENT"
    entry = annex_docs.get(tablet["doc"])
    if entry is None:
        return None, "DOC_NOT_IN_ANNEX"
    labels = [t["s"] for t in tablet["tokens"] if t["k"] == "label"]
    if entry["types"] != labels:
        return None, "MISALIGNED"
    return entry["w"], "ALIGNED"


# --------------------------------------------------------------------------- #
# Leg analysis (KU-RO primary; KI-RO identical-design via swap_roles)
# --------------------------------------------------------------------------- #
def analyze_leg(tablets: Sequence[dict], commodities: set, role: str,
                n_trials: int = N_TRIALS, seed: int = SEED,
                annex_docs: Optional[dict] = None) -> dict:
    """One full leg: units → primary integer statistic vs derangement null → fraction secondary →
    damage breakdown → per-unit detail. ``role`` = 'KU-RO' (streams as-is) or 'KI-RO'
    (labels swapped: identical design, KI-RO closes, KU-RO skipped)."""
    assert role in ("KU-RO", "KI-RO")
    per_unit: List[dict] = []
    align_status: Dict[str, str] = {}
    for tab in tablets:
        work = tab if role == "KU-RO" else dict(tab, tokens=swap_roles(tab["tokens"]))
        codes, status = damage_codes_for(tab, annex_docs)   # annex keyed on the REAL stream
        align_status[tab["doc"]] = status
        illegible = tab.get("_illegible_marks", 0)
        for u in units_with_words(work, commodities):
            dmg = ([codes[i] for i in u["word_ords"] if codes[i]] if codes is not None else None)
            item_sum = sum(iv for iv, _ in u["items"])
            per_unit.append({
                "doc": u["doc"],
                "commodity": u["commodity"],
                "closing_int": u["total_int"],
                "closing_has_numeral": u["total_has_num"],
                "item_sum_int": item_sum,
                "n_items": len(u["items"]),
                "integer_exact": integer_exact(u),
                "fraction_bearing": metrology.is_fraction_bearing(u),
                "exact_with_editorial_fractions": editorial_exact(u),
                "word_ords": u["word_ords"],
                "damage_codes": dmg,
                "n_damaged_word_tokens": (len(dmg) if dmg is not None else None),
                "doc_illegible_number_marks": illegible,
            })

    scored = [u for u in per_unit if u["closing_has_numeral"]]
    excluded = [u for u in per_unit if not u["closing_has_numeral"]]
    obs = sum(1 for u in scored if u["integer_exact"])
    null = None
    if len(scored) >= 2 and n_trials > 0:
        hits = null_hits([u["item_sum_int"] for u in scored],
                         [u["closing_int"] for u in scored], n_trials, seed)
        null = null_summary(obs, hits)

    fb = [u for u in per_unit if u["fraction_bearing"]]
    fb_comp = [u for u in fb if u["exact_with_editorial_fractions"] is not None]
    damage_ok = [u for u in scored if u["damage_codes"] is not None]
    dmg_break = {
        "available": bool(damage_ok),
        "annex_scope_caveat": ("annex covers WORD tokens only; damaged numerals appear only as "
                               "doc-level illegible-number marks"),
        "docs_aligned": sum(1 for v in align_status.values() if v == "ALIGNED"),
        "docs_not_aligned": sorted(d for d, v in align_status.items() if v != "ALIGNED"),
        "n_scored_units_with_damage_data": len(damage_ok),
        "matched": {
            "n": sum(1 for u in damage_ok if u["integer_exact"]),
            "with_damaged_word_token": sum(1 for u in damage_ok
                                           if u["integer_exact"] and u["n_damaged_word_tokens"]),
        },
        "mismatched": {
            "n": sum(1 for u in damage_ok if not u["integer_exact"]),
            "with_damaged_word_token": sum(1 for u in damage_ok
                                           if not u["integer_exact"] and u["n_damaged_word_tokens"]),
            "in_docs_with_illegible_number_marks": sum(
                1 for u in damage_ok
                if not u["integer_exact"] and u["doc_illegible_number_marks"]),
        },
    }
    return {
        "role": role,
        "design": ("closing-line design; identical to the KU-RO leg with the two labels exchanged"
                   if role == "KI-RO" else "metrology.parse_tablet balance units"),
        "n_docs": len(tablets),
        "n_units": len(per_unit),
        "n_units_scored": len(scored),
        "n_units_excluded_no_closing_numeral": len(excluded),
        "n_units_no_items": sum(1 for u in scored if u["n_items"] == 0),
        "n_commodity_tagged_units": sum(1 for u in per_unit if u["commodity"] is not None),
        "observed_integer_exact": obs,
        "observed_rate": round(obs / len(scored), 4) if scored else None,
        "null": null,
        "fraction_secondary": {
            "note": ("COMPARISON-ONLY (metrology discipline): editorial vulgar-fraction glosses "
                     "via metrology.editorial_value; never enters the permutation statistic"),
            "n_fraction_bearing_units": len(fb),
            "n_editorial_computable": len(fb_comp),
            "exact_with_editorial_fractions": sum(
                1 for u in fb_comp if u["exact_with_editorial_fractions"]),
        },
        "damage_breakdown": dmg_break,
        "per_unit": per_unit,
    }


# --------------------------------------------------------------------------- #
# Corpus assembly + light path
# --------------------------------------------------------------------------- #
def _has_label(tokens: Sequence[dict], label: str) -> bool:
    return any(t["k"] == "label" and t["s"] == label for t in tokens)


def load_legs(path: str = SILVER) -> Tuple[List[dict], List[dict], List[dict]]:
    """(kuro_tablets, kiro_tablets, light_rows). WIDENED scope: site_prefix='' / horizon='' so
    every document with the relevant closing label is testable (34 KU-RO docs vs metrology's
    32 at HT/LM I). Tablets carry `_illegible_marks` = standalone U+1076B `other` tokens in the
    raw silver stream (the damaged-numeral proxy). Light rows = corpus_io_structured.line_items
    doc-level cross-check for the KU-RO docs."""
    kuro = metrology.load_tablets(path, site_prefix="", horizon="", require_total=True)
    everything = metrology.load_tablets(path, site_prefix="", horizon="", require_total=False)
    kiro = [t for t in everything if _has_label(t["tokens"], "KI-RO")]

    raw = {r["id"]: r for r in json.load(open(path, encoding="utf-8"))}
    for t in kuro + kiro:
        rec = raw[t["doc"]]
        t["_illegible_marks"] = sum(1 for s in rec["stream"]
                                    if s.get("t") == "other" and MARKER in s.get("raw", ""))
    light = []
    for t in kuro:
        items, total, deficit = line_items(raw[t["doc"]])
        s = sum(v for _, v in items)
        light.append({"doc": t["doc"], "light_item_sum": s, "light_closing_int": total,
                      "light_exact": (total is not None and s == total)})
    return kuro, kiro, light


def run(path: str = SILVER, annex_path: str = ANNEX,
        n_trials: int = N_TRIALS, seed: int = SEED) -> dict:
    """Full harness: KU-RO leg, KI-RO identical-design leg, commodity-sectioning ablation,
    light-path cross-check, cross-lineage sanity block."""
    commodities = metrology.load_commodities()
    annex_docs = load_annex(annex_path)
    kuro_tabs, kiro_tabs, light = load_legs(path)

    kuro = analyze_leg(kuro_tabs, commodities, "KU-RO", n_trials, seed, annex_docs)
    kiro = analyze_leg(kiro_tabs, commodities, "KI-RO", n_trials, seed, annex_docs)

    # Commodity-sectioning ablation: no commodity recognition -> every closing line totals the
    # whole accumulation. Expected near-inert (most units are commodity=None already).
    abl = analyze_leg(kuro_tabs, set(), "KU-RO", n_trials, seed, annex_docs)
    ablation = {
        "note": ("commodity recognition disabled (commodities=set()); expected near-inert — "
                 "most units carry no commodity tag under the primary parse"),
        "n_units": abl["n_units"],
        "n_units_scored": abl["n_units_scored"],
        "observed_integer_exact": abl["observed_integer_exact"],
        "null": abl["null"],
        "delta_units_vs_primary": abl["n_units"] - kuro["n_units"],
        "delta_observed_vs_primary": (abl["observed_integer_exact"]
                                      - kuro["observed_integer_exact"]),
    }

    ours_sep = bool(kuro["null"] and kuro["null"]["p_empirical_primary"] < 0.05
                    and kuro["observed_integer_exact"] > kuro["null"]["mean"])
    sanity = dict(TSIRKAS_PUBLISHED)
    sanity["ours_kuro"] = [kuro["observed_integer_exact"], kuro["n_units_scored"]]
    sanity["ours_kuro_null_mean"] = kuro["null"]["mean"] if kuro["null"] else None
    sanity["ours_kuro_p_empirical"] = (kuro["null"]["p_empirical_primary"]
                                       if kuro["null"] else None)
    sanity["ours_kuro_z_secondary"] = kuro["null"]["z_secondary"] if kuro["null"] else None
    sanity["ours_kiro"] = [kiro["observed_integer_exact"], kiro["n_units_scored"]]
    sanity["ours_kiro_p_empirical"] = (kiro["null"]["p_empirical_primary"]
                                       if kiro["null"] else None)
    sanity["direction_agrees"] = ours_sep   # his KU-RO leg separated; does ours, in the same direction

    return {
        "harness": "kuro_null — arithmetic-anchor (summation-function) permutation harness",
        "claim_layer": CLAIM_LAYER,
        "articles": ["Art. IV", "Art. V (L2/L3)", "Art. VII", "Art. XI (Tsirkas credit)",
                     "Art. XXII"],
        "seed": seed,
        "n_trials": n_trials,
        "scope": {
            "path": os.path.relpath(path, _ROOT) if path.startswith(_ROOT) else path,
            "site_prefix": "",
            "horizon": "",
            "n_kuro_docs": kuro["n_docs"],
            "n_kiro_docs": kiro["n_docs"],
        },
        "kuro": kuro,
        "kiro": kiro,
        "ablation_no_commodity_sectioning": ablation,
        "light_path": {
            "note": ("corpus_io_structured.line_items doc-level cross-check (crude: last closing "
                     "numeral per doc, no commodity columns); comparison only"),
            "n_docs": len(light),
            "n_light_exact": sum(1 for r in light if r["light_exact"]),
            "per_doc": light,
        },
        "cross_lineage_sanity": sanity,
        "caveats": [
            "L2/L3 ONLY: a separated null supports KU-RO as a summation-FUNCTION sign — it is not "
            "a reading, not a translation, and licenses nothing above the functional layer.",
            "Integer arithmetic is the primary criterion; fraction-bearing units whose fractional "
            "mass closes into the closing integer can mismatch here by design — they are counted "
            "and reported in the fraction secondary panel.",
            "The section model is metrology.parse_tablet's; mismatches include section-model "
            "artifacts (e.g. KI-RO-headed sub-lists lumped into a KU-RO span). The null uses the "
            "SAME section model, so the comparison is internally consistent.",
            "The damage annex covers word tokens only; damaged numerals are visible only as "
            "doc-level illegible-number marks (U+1076B).",
            "Cross-lineage sanity vs Tsirkas is direction/magnitude-class only — different corpus "
            "model, different section counts; equality is not tested.",
        ],
    }


def headline(report: dict) -> str:
    k, g = report["kuro"], report["kiro"]
    bits = [f"KU-RO: {k['observed_integer_exact']}/{k['n_units_scored']} units integer-exact"]
    if k["null"]:
        bits.append(f"vs derangement null mean {k['null']['mean']} "
                    f"(p={k['null']['p_empirical_primary']}, z~{k['null']['z_secondary']}).")
    bits.append(f"KI-RO (identical design): {g['observed_integer_exact']}/{g['n_units_scored']}")
    if g["null"]:
        bits.append(f"vs null mean {g['null']['mean']} (p={g['null']['p_empirical_primary']}).")
    a = report["ablation_no_commodity_sectioning"]
    bits.append(f"Commodity-sectioning ablation: {a['observed_integer_exact']}/{a['n_units_scored']} "
                f"(delta {a['delta_observed_vs_primary']:+d}).")
    bits.append("Summation-FUNCTION evidence only (L2/L3).")
    return " ".join(bits)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", default=SILVER, help="structured silver corpus json")
    ap.add_argument("--annex", default=ANNEX, help="damage annex sidecar json")
    ap.add_argument("--trials", type=int, default=N_TRIALS)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", default=OUT, help="result json path")
    ap.add_argument("--json", action="store_true", help="also print the full JSON report")
    args = ap.parse_args(argv)

    if not os.path.exists(args.path):
        print(f"corpus not found at {args.path}; run scripts/corpus_io_structured.py first")
        return 2
    report = run(args.path, args.annex, n_trials=args.trials, seed=args.seed)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(report, open(args.out, "w"), ensure_ascii=False, indent=1, sort_keys=True)
    print("HEADLINE:", headline(report))
    print(f"result -> {args.out}")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
