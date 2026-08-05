#!/usr/bin/env python3
"""d1_sensitivity.py — Phase 1b of the D1 programme: three targeted sensitivity checks
run against the damage annex (corpus/silver/damage_annex.json, scripts/audit_damage_markers.py).

Scope decision (2026-08-05, plan generic-brewing-falcon): NO wholesale re-runs — phantom
exclusion shrinks the corpus, so published nulls only get more null, and Art. XVII forbids
turning a failed result into a success. Three annex-style checks only:

  (1) DENOMINATORS — distinct word types, word tokens, and Art. VIII effective_n
      (scripts/effective_n.py, dims doc+site) with vs without phantom types (phantom =
      type whose every occurrence carries a nonempty LTI damage code).
  (2) METROLOGY — the published held-out fraction-balance null
      (scripts/comparison/metrology.py; runtime/metrology-real.json: 32 docs / 35 units,
      held-out balance 0.0 vs null mean 0.113, p = 1.0) re-run twice: as published, and
      with damage-flagged balance units excluded. UNIT→ANNEX MAPPING: annex token order
      = silver stream word order, so metrology's `label` tokens are exactly the annex
      word tokens in order (asserted per tablet by list equality of the annex `types`
      against the stream labels). A line is damage-flagged iff any of its word tokens
      carries a nonempty code; a balance unit is excluded iff its KU-RO total line or any
      accumulated contributing item line is flagged. Attribution mirrors
      metrology.parse_tablet's accumulator exactly, and the damage-stripped mirror is
      asserted equal to parse_tablet's own output (mechanical cross-validation). The
      annex covers WORD-attached damage only: numeral damage and label-free lines cannot
      be flagged through it (stated caveat).
  (3) SEGMENTATION — the published boundary-recovery gap (scripts/comparison/morphology.py
      boundary_recovery, leave-one-site-out; runtime/morphology-real.json: dp_unigram
      micro-F1 0.4361 vs random 0.3888) recomputed with phantom-only word tokens removed.
      (`use_morfessor=False` reproduces the published dp_unigram/random pair exactly —
      the random-baseline rng is independent of the Morfessor leg — verified against the
      runtime baseline before the sensitivity leg runs.)

DISCIPLINE (binding, stated in the doc): results are annexes; NO VERDICT MAY FLIP via
annex. If any check IMPROVES a result, that is not a claim — it becomes a new
preregistered run deflated for the D1-prompted look. Every block reports
published_value, sensitivity_value, delta, and a one-line honest interpretation; a
`verdict_flip` flag is computed mechanically per block and must stay False.

Published baselines are READ from the runtime artifacts (never hand-typed; invariant
#12); if a runtime baseline file is absent the freshly recomputed as-published leg is
used and flagged `published_source: recomputed`.

Constitution: Art. VIII (effective_n), XI (single L_LA_CORPUS lineage noted), XVII
(append-only: annex supplements, no published figure changes), XXII (stage D1-SENS-01,
header in docs/2026-08-05-d1-damage-annex.md). Deterministic: seeded throughout, no
timestamps.

    python3 scripts/d1_sensitivity.py [--blocks a,b,c] [--seed 0] [--summary-only]
                                      [--write-doc] [--out results/d1_sensitivity.json]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import effective_n as en                       # noqa: E402
from scripts.comparison import metrology                    # noqa: E402
from scripts.comparison import morphology                   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANNEX = os.path.join(ROOT, "corpus", "silver", "damage_annex.json")
SILVER_STRUCT = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
PUB_METROLOGY = os.path.join(ROOT, "runtime", "metrology-real.json")
PUB_MORPHOLOGY = os.path.join(ROOT, "runtime", "morphology-real.json")
OUT = os.path.join(ROOT, "results", "d1_sensitivity.json")
DOC = os.path.join(ROOT, "docs", "2026-08-05-d1-damage-annex.md")

VERSION = "d1-sensitivity-v1"
STAGE = "D1-SENS-01"
ALL_BLOCKS = ("denominators", "metrology", "segmentation")

DISCIPLINE = ("Discipline: results are annexes; if anything *improves*, that is a new "
              "preregistered run deflated for the D1-prompted look — verdicts never "
              "flip via annex.")


# --------------------------------------------------------------------------- #
# Annex access + phantom semantics
# --------------------------------------------------------------------------- #
def load_annex(path: str = ANNEX) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"damage annex not found at {path} — run scripts/audit_damage_markers.py first")
    return json.load(open(path, encoding="utf-8"))


def phantom_type_set(annex_docs: dict) -> set:
    """Types whose EVERY occurrence carries a nonempty damage code (Tsirkas D1 phantoms)."""
    clean, damaged = set(), set()
    for d in annex_docs.values():
        for c, ty in zip(d["w"], d["types"]):
            (damaged if c else clean).add(ty)
    return damaged - clean


def phantom_token_count(annex_docs: dict, phantoms: set) -> int:
    return sum(1 for d in annex_docs.values() for ty in d["types"] if ty in phantoms)


# --------------------------------------------------------------------------- #
# Block 1 — denominators
# --------------------------------------------------------------------------- #
def denominators_block(annex: dict) -> dict:
    docs = annex["docs"]
    phantoms = phantom_type_set(docs)
    site_of = {r["id"]: (r.get("site") or "(unknown)")
               for r in json.load(open(SILVER_STRUCT, encoding="utf-8"))}

    items_all, items_ex = [], []
    types_all, types_ex = set(), set()
    for iid, d in docs.items():
        site = site_of.get(iid, "(unknown)")
        for ty in d["types"]:
            it = {"doc": iid, "site": site, "type": ty}
            items_all.append(it)
            types_all.add(ty)
            if ty not in phantoms:
                items_ex.append(it)
                types_ex.add(ty)

    def counts(items, types):
        return {
            "distinct_types": len(types),
            "word_tokens": len(items),
            "docs": en.distinct_units(items, "doc"),
            "sites": en.distinct_units(items, "site"),
            "effective_n_doc_site": en.effective_n(items, ["doc", "site"])["effective_n"],
        }

    published = counts(items_all, types_all)
    sensitivity = counts(items_ex, types_ex)
    delta = {k: sensitivity[k] - published[k] for k in published}

    # cross-check the with-phantom denominators against the published morphology artifact
    cross = None
    if os.path.exists(PUB_MORPHOLOGY):
        mi = json.load(open(PUB_MORPHOLOGY, encoding="utf-8"))["morpheme_induction"]
        cross = {"runtime_n_word_types": mi["n_word_types"],
                 "runtime_n_word_tokens": mi["n_word_tokens"],
                 "matches_published": (mi["n_word_types"] == published["distinct_types"]
                                       and mi["n_word_tokens"] == published["word_tokens"])}

    interp = (f"Under phantom exclusion the type denominator is "
              f"{published['distinct_types']}→{sensitivity['distinct_types']} "
              f"({delta['distinct_types']:+d}) and tokens {published['word_tokens']}→"
              f"{sensitivity['word_tokens']} ({delta['word_tokens']:+d}), while the Art. VIII "
              f"effective_n (dims doc+site) moves {published['effective_n_doc_site']}→"
              f"{sensitivity['effective_n_doc_site']} — future type-count-sensitive stages "
              f"must cite the phantom-excluded denominator (no published figure consumed "
              f"type counts; all tokens are one L_LA_CORPUS lineage under Art. XI).")
    return {
        "name": "denominators",
        "phantom_types": len(phantoms),
        "phantom_type_tokens": phantom_token_count(docs, phantoms),
        "published_value": published,
        "published_source": ("corpus/silver/damage_annex.json summary + "
                             "runtime/morphology-real.json cross-check"),
        "cross_check_published_morphology": cross,
        "sensitivity_value": sensitivity,
        "delta": delta,
        "verdict_flip": False,          # no verdict is attached to a denominator
        "interpretation": interp,
    }


# --------------------------------------------------------------------------- #
# Block 2 — metrology (damage-filtered re-run)
# --------------------------------------------------------------------------- #
def mirror_parse_tablet_damage(tablet: dict, commodities: set, codes: list):
    """metrology.parse_tablet with per-unit damage attribution.

    Walks the identical accumulator control flow; `codes` are the tablet's annex LTI codes
    in stream word order (== label-token order). Returns (units, damaged) where `units`
    must equal metrology.parse_tablet(tablet, commodities) exactly (the caller asserts) and
    damaged[i] is True iff unit i's total line or any contributing item line carries a
    damage-flagged word token."""
    n_labels = sum(1 for t in tablet["tokens"] if t["k"] == "label")
    if n_labels != len(codes):
        raise RuntimeError(f"{tablet['doc']}: {n_labels} label tokens vs {len(codes)} "
                           f"annex codes — word-order mapping broken")
    lines, cur = [], []
    li = 0
    for t in tablet["tokens"]:
        if t["k"] == "nl":
            if cur:
                lines.append(cur)
                cur = []
        else:
            if t["k"] == "label":
                t = dict(t, dmg=bool(codes[li]))
                li += 1
            cur.append(t)
    if cur:
        lines.append(cur)

    from collections import defaultdict
    acc = defaultdict(list)                 # commodity -> [(int, fracs, line_damaged)]
    order = []
    column_commodity = None
    units, damaged = [], []

    def push(commod, ival, fracs, dmg):
        acc[commod].append((ival, list(fracs), dmg))
        if commod not in order:
            order.append(commod)

    for ln in lines:
        labels = [t["s"] for t in ln if t["k"] == "label"]
        line_dmg = any(t.get("dmg") for t in ln if t["k"] == "label")
        is_total = "KU-RO" in labels
        is_deficit = ("KI-RO" in labels) and not is_total
        commod_labels = [t["s"] for t in ln if t["k"] == "label"
                         and metrology._base_commodity(t["s"], commodities)]
        commod = (metrology._base_commodity(commod_labels[0], commodities)
                  if commod_labels else None)
        ints = [t["v"] for t in ln if t["k"] == "num"]
        fracs = [t["s"] for t in ln if t["k"] == "frac"]

        if is_total:
            total_int = ints[0] if ints else 0
            if commod is not None and commod in acc:
                items3 = acc.pop(commod)
                order[:] = [o for o in order if o != commod]
            else:
                items3 = [it for cm in order for it in acc.get(cm, [])]
                acc.clear()
                order.clear()
            units.append({"doc": tablet["doc"], "commodity": commod, "total_int": total_int,
                          "total_fracs": fracs, "items": [(v, f) for v, f, _ in items3]})
            damaged.append(bool(line_dmg or any(d for _, _, d in items3)))
        elif is_deficit:
            continue
        else:
            if commod is not None:
                column_commodity = commod
            use_c = commod if commod is not None else column_commodity
            if ints:
                push(use_c, ints[0], fracs, line_dmg)
            elif fracs:
                push(use_c, 0, fracs, line_dmg)
    return units, damaged


def _metrology_stats(units, k: int, n_perms: int, seed: int) -> dict:
    fb = [u for u in units if metrology.is_fraction_bearing(u)]
    int_units = [u for u in units if not metrology.is_fraction_bearing(u)]
    int_bal = sum(1 for u in int_units if metrology.unit_balances(u, {}) is True)
    ho = metrology.heldout_balance(units, k=k, seed=seed, solver_seed=seed)
    null = metrology.permutation_null(ho, n_perms=n_perms, seed=seed)
    r = lambda x: None if x is None else round(float(x), 6)
    return {
        "n_units": len(units),
        "n_documents": len({u["doc"] for u in units}),
        "n_integer_only": len(int_units),
        "n_integer_only_balanced": int_bal,
        "n_fraction_bearing": len(fb),
        "heldout_fraction_balance_rate": r(ho["heldout_fraction_balance_rate"]),
        "heldout_overall_balance_rate": r(ho["heldout_overall_balance_rate"]),
        "n_test_fraction_bearing": ho["n_test_fraction_bearing"],
        "null_mean": r(null["null_mean"]),
        "null_max": r(null["null_max"]),
        "p_value": r(null["p_value"]),
        "separated": bool(null["separated"]),
        "powered": ho["n_test_fraction_bearing"] >= 5,
    }


def metrology_block(annex: dict, k: int = 5, n_perms: int = 500, seed: int = 0) -> dict:
    tablets = metrology.load_tablets()
    commodities = metrology.load_commodities()

    all_units, all_damaged = [], []
    for tab in tablets:
        a = annex["docs"].get(tab["doc"])
        if a is None:
            raise RuntimeError(f"{tab['doc']}: tablet missing from the damage annex")
        labels = [t["s"] for t in tab["tokens"] if t["k"] == "label"]
        if labels != a["types"]:
            raise RuntimeError(f"{tab['doc']}: stream labels do not match annex types — "
                               f"the annex/stream word-order mapping is broken")
        units, damaged = mirror_parse_tablet_damage(tab, commodities, a["w"])
        ref = metrology.parse_tablet(tab, commodities)
        if units != ref:
            raise RuntimeError(f"{tab['doc']}: damage-attribution mirror diverged from "
                               f"metrology.parse_tablet — mapping invalid")
        all_units.extend(units)
        all_damaged.extend(damaged)

    clean_units = [u for u, d in zip(all_units, all_damaged) if not d]
    n_excluded = len(all_units) - len(clean_units)
    n_excluded_fb = sum(1 for u, d in zip(all_units, all_damaged)
                        if d and metrology.is_fraction_bearing(u))

    reproduction = _metrology_stats(all_units, k=k, n_perms=n_perms, seed=seed)
    sensitivity = _metrology_stats(clean_units, k=k, n_perms=n_perms, seed=seed)

    if os.path.exists(PUB_METROLOGY):
        raw = open(PUB_METROLOGY, encoding="utf-8").read()
        pub = json.loads(raw[raw.index("{"):])          # file opens with a HEADLINE line
        published = {
            "n_units": pub["corpus"]["n_balance_units"],
            "n_documents": pub["corpus"]["n_documents"],
            "heldout_fraction_balance_rate": round(
                pub["heldout"]["heldout_fraction_balance_rate"], 6),
            "null_mean": round(pub["null"]["null_mean"], 6),
            "p_value": round(pub["null"]["p_value"], 6),
            "separated": pub["null"]["separated"],
        }
        source = "runtime/metrology-real.json"
        matches = all(reproduction[k2] == published[k2] for k2 in published)
    else:
        published = {k2: reproduction[k2] for k2 in
                     ("n_units", "n_documents", "heldout_fraction_balance_rate",
                      "null_mean", "p_value", "separated")}
        source = "recomputed (runtime baseline file absent)"
        matches = None

    def _d(key):
        a, b = sensitivity.get(key), reproduction.get(key)
        return None if (a is None or b is None) else round(a - b, 6)
    delta = {k2: _d(k2) for k2 in
             ("n_units", "heldout_fraction_balance_rate", "null_mean", "p_value")}

    # verdict-flip check: published verdict is NULL (not separated, p = 1.0); a flip would
    # be the filtered re-run claiming separation at conventional significance.
    flip = bool(sensitivity["separated"] and sensitivity["p_value"] is not None
                and sensitivity["p_value"] <= 0.05)

    power_note = ("" if sensitivity["powered"] else
                  f"; additionally UNDERPOWERED, {sensitivity['n_test_fraction_bearing']} "
                  f"fraction-bearing test units")
    verdict_note = ("word-token damage does not explain the null and no verdict moves"
                    if not flip else
                    "the filtered re-run separates from its null — NOT a claim; a new "
                    "preregistered run deflated for the D1-prompted look is required")
    interp = (f"The published metrology NULL under damage filtering: "
              f"{n_excluded}/{len(all_units)} balance units excluded "
              f"({n_excluded_fb} fraction-bearing), held-out fraction balance "
              f"{sensitivity['heldout_fraction_balance_rate']} vs null mean "
              f"{sensitivity['null_mean']} (p={sensitivity['p_value']}{power_note}) — "
              f"{verdict_note}.")
    return {
        "name": "metrology",
        "mapping": ("annex token order = silver stream word order; metrology label tokens "
                    "asserted list-equal to annex `types` per tablet; unit excluded iff its "
                    "KU-RO total line or any accumulated item line carries a damage-flagged "
                    "word token; damage-stripped mirror asserted equal to "
                    "metrology.parse_tablet output for every tablet"),
        "mapping_caveat": ("the annex records WORD-attached damage only — numeral damage and "
                           "lines without word labels cannot be flagged through it"),
        "n_tablets": len(tablets),
        "n_units_excluded": n_excluded,
        "n_units_excluded_fraction_bearing": n_excluded_fb,
        "published_value": published,
        "published_source": source,
        "reproduction": dict(reproduction, matches_published=matches),
        "sensitivity_value": sensitivity,
        "delta": delta,
        "verdict_flip": flip,
        "interpretation": interp,
    }


# --------------------------------------------------------------------------- #
# Block 3 — segmentation (phantom-only words removed)
# --------------------------------------------------------------------------- #
def filter_phantom_words(corpus, phantoms: set):
    """Drop word tokens whose type is phantom; drop inscriptions left empty."""
    out, n_words_dropped, n_insc_dropped = [], 0, 0
    for ins in corpus:
        kept = [w for w in ins.words if "-".join(w) not in phantoms]
        n_words_dropped += len(ins.words) - len(kept)
        if kept:
            out.append(morphology.Inscription(iid=ins.iid, site=ins.site, words=kept))
        else:
            n_insc_dropped += 1
    return out, n_words_dropped, n_insc_dropped


def _br_stats(br: dict) -> dict:
    dp = br["segmenters"]["dp_unigram"]["micro_f1"]
    rnd = br["random_baseline"]["micro_f1"]
    return {"dp_unigram_micro_f1": dp, "random_micro_f1": rnd,
            "gap": round(dp - rnd, 4), "boundary_base_rate": br["boundary_base_rate"],
            "n_sites": br["n_sites"]}


def segmentation_block(annex: dict, seed: int = 0, dp_iters: int = 6) -> dict:
    phantoms = phantom_type_set(annex["docs"])
    corpus = morphology.load_corpus()

    # as-published leg (use_morfessor=False reproduces the published dp/random pair: the
    # random-baseline rng draws are independent of the Morfessor leg)
    reproduction = _br_stats(morphology.boundary_recovery(
        corpus, seed=seed, min_site_size=1, dp_iters=dp_iters, use_morfessor=False))

    if os.path.exists(PUB_MORPHOLOGY):
        pub_br = json.load(open(PUB_MORPHOLOGY, encoding="utf-8"))["boundary_recovery"]
        dp = pub_br["segmenters"]["dp_unigram"]["micro_f1"]
        rnd = pub_br["random_baseline"]["micro_f1"]
        published = {"dp_unigram_micro_f1": dp, "random_micro_f1": rnd,
                     "gap": round(dp - rnd, 4)}
        source = "runtime/morphology-real.json"
        matches = (reproduction["dp_unigram_micro_f1"] == dp
                   and reproduction["random_micro_f1"] == rnd)
    else:
        published = {k: reproduction[k] for k in
                     ("dp_unigram_micro_f1", "random_micro_f1", "gap")}
        source = "recomputed (runtime baseline file absent)"
        matches = None

    filtered, n_words_dropped, n_insc_dropped = filter_phantom_words(corpus, phantoms)
    annex_phantom_tokens = phantom_token_count(annex["docs"], phantoms)
    sens_br = morphology.boundary_recovery(
        filtered, seed=seed, min_site_size=1, dp_iters=dp_iters, use_morfessor=False)
    sensitivity = dict(_br_stats(sens_br),
                       n_words_dropped=n_words_dropped,
                       n_inscriptions_dropped=n_insc_dropped,
                       n_inscriptions=len(filtered))

    delta = {k: round(sensitivity[k] - published[k], 4)
             for k in ("dp_unigram_micro_f1", "random_micro_f1", "gap")}

    # verdict-flip check: published verdict is POSITIVE (dp beats the random baseline);
    # a flip would be the phantom-filtered corpus erasing the gap.
    flip = bool(sensitivity["gap"] <= 0)

    improvement = ("" if sensitivity["gap"] <= published["gap"] else
                   "; the larger filtered gap is an IMPROVEMENT and per the discipline "
                   "rule is NOT a claim — using it would require a new preregistered run "
                   "deflated for the D1-prompted look")
    verdict_note = (("the published positive is not damage-driven and no verdict moves"
                     + improvement)
                    if not flip else
                    "the gap does NOT survive phantom exclusion — a flip signal; NOT a "
                    "re-grading: the published verdict stands and any follow-up is a new "
                    "preregistered run")
    interp = (f"The boundary-recovery gap without phantom-only words: "
              f"{published['dp_unigram_micro_f1']} vs {published['random_micro_f1']} "
              f"(gap +{published['gap']}) as published → "
              f"{sensitivity['dp_unigram_micro_f1']} vs {sensitivity['random_micro_f1']} "
              f"(gap {sensitivity['gap']:+}) after dropping {n_words_dropped} phantom "
              f"tokens — {verdict_note} (micro-F1 levels are not comparable across "
              f"corpora: the boundary base rate shifts "
              f"{reproduction['boundary_base_rate']}→{sensitivity['boundary_base_rate']}; "
              f"the GAP is the comparand).")
    return {
        "name": "segmentation",
        "phantom_types": len(phantoms),
        "annex_phantom_tokens": annex_phantom_tokens,
        "dropped_tokens_agree_with_annex": n_words_dropped == annex_phantom_tokens,
        "published_value": published,
        "published_source": source,
        "reproduction": dict(reproduction, matches_published=matches),
        "sensitivity_value": sensitivity,
        "delta": delta,
        "verdict_flip": flip,
        "interpretation": interp,
    }


# --------------------------------------------------------------------------- #
# Assembly + markdown
# --------------------------------------------------------------------------- #
def build(blocks=ALL_BLOCKS, seed: int = 0, k: int = 5, n_perms: int = 500,
          dp_iters: int = 6) -> dict:
    annex = load_annex()
    out = {
        "version": VERSION,
        "stage": STAGE,
        "generated_by": "scripts/d1_sensitivity.py",
        "seed": seed,
        "annex_version": annex["version"],
        "annex_bronze_sha256": annex["bronze_sha256"],
        "discipline": DISCIPLINE,
        "blocks": {},
    }
    if "denominators" in blocks:
        out["blocks"]["denominators"] = denominators_block(annex)
    if "metrology" in blocks:
        out["blocks"]["metrology"] = metrology_block(annex, k=k, n_perms=n_perms, seed=seed)
    if "segmentation" in blocks:
        out["blocks"]["segmentation"] = segmentation_block(annex, seed=seed, dp_iters=dp_iters)
    out["verdict_flips"] = sorted(n for n, b in out["blocks"].items() if b["verdict_flip"])
    return out


def _row(label, pub, sens, dlt):
    return f"| {label} | {pub} | {sens} | {dlt} |"


def render_md(result: dict) -> str:
    """Markdown section for docs/2026-08-05-d1-damage-annex.md (every number from `result`)."""
    b = result["blocks"]
    L = [
        "## Phase 1b — sensitivity checks "
        "(script-generated: `python3 scripts/d1_sensitivity.py --write-doc`)",
        "",
        f"Stage {result['stage']} (annex to D1-ANNEX-01; no claim; L0/L1). Machine-readable "
        f"result: `results/d1_sensitivity.json` (seed {result['seed']}, annex "
        f"`{result['annex_version']}`, bronze `{result['annex_bronze_sha256'][:16]}`). "
        f"Verdict flips: "
        f"{', '.join(result['verdict_flips']) if result['verdict_flips'] else 'NONE'}.",
        "",
    ]
    if "denominators" in b:
        d = b["denominators"]
        p, s, dl = d["published_value"], d["sensitivity_value"], d["delta"]
        L += [
            "### (1) Denominators — with vs without phantom types",
            "",
            "| quantity | published (with phantoms) | phantom-excluded | delta |",
            "|---|---|---|---|",
            _row("distinct word types", p["distinct_types"], s["distinct_types"],
                 dl["distinct_types"]),
            _row("word tokens", p["word_tokens"], s["word_tokens"], dl["word_tokens"]),
            _row("docs with ≥1 word token", p["docs"], s["docs"], dl["docs"]),
            _row("sites", p["sites"], s["sites"], dl["sites"]),
            _row("effective_n (Art. VIII, dims doc+site)", p["effective_n_doc_site"],
                 s["effective_n_doc_site"], dl["effective_n_doc_site"]),
            "",
            f"{d['interpretation']}",
            "",
        ]
    if "metrology" in b:
        m = b["metrology"]
        p, s, dl = m["published_value"], m["sensitivity_value"], m["delta"]
        L += [
            "### (2) Metrology null — as published vs damage-filtered",
            "",
            f"Mapping: {m['mapping']}. Caveat: {m['mapping_caveat']}. Excluded: "
            f"{m['n_units_excluded']}/{p['n_units']} balance units "
            f"({m['n_units_excluded_fraction_bearing']} fraction-bearing). As-published "
            f"reproduction matches `{m['published_source']}`: "
            f"{m['reproduction']['matches_published']}.",
            "",
            "| quantity | published | damage-filtered | delta |",
            "|---|---|---|---|",
            _row("balance units", p["n_units"], s["n_units"], dl["n_units"]),
            _row("held-out fraction balance", p["heldout_fraction_balance_rate"],
                 s["heldout_fraction_balance_rate"], dl["heldout_fraction_balance_rate"]),
            _row("null mean", p["null_mean"], s["null_mean"], dl["null_mean"]),
            _row("p-value", p["p_value"], s["p_value"], dl["p_value"]),
            _row("separated", p["separated"], s["separated"], "—"),
            "",
            f"{m['interpretation']}",
            "",
        ]
    if "segmentation" in b:
        g = b["segmentation"]
        p, s, dl = g["published_value"], g["sensitivity_value"], g["delta"]
        L += [
            "### (3) Segmentation boundary-recovery gap — with vs without phantom-only words",
            "",
            f"Phantom-only word tokens dropped: {s['n_words_dropped']} (annex count "
            f"{g['annex_phantom_tokens']}, agree: {g['dropped_tokens_agree_with_annex']}); "
            f"{s['n_inscriptions_dropped']} inscriptions emptied. As-published reproduction "
            f"matches `{g['published_source']}`: {g['reproduction']['matches_published']}.",
            "",
            "| quantity | published | phantom-filtered | delta |",
            "|---|---|---|---|",
            _row("dp_unigram micro-F1", p["dp_unigram_micro_f1"], s["dp_unigram_micro_f1"],
                 dl["dp_unigram_micro_f1"]),
            _row("random-baseline micro-F1", p["random_micro_f1"], s["random_micro_f1"],
                 dl["random_micro_f1"]),
            _row("gap (dp − random)", p["gap"], s["gap"], dl["gap"]),
            "",
            f"{g['interpretation']}",
            "",
        ]
    L += [DISCIPLINE, ""]
    return "\n".join(L)


def splice_doc(md: str, doc_path: str = DOC) -> None:
    """Replace the Phase 1b section (from its `## Phase 1b` heading up to the next `## `
    heading) with the generated section; the rest of the doc is untouched."""
    lines = open(doc_path, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("## Phase 1b"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    new = lines[:start] + md.splitlines() + [""] + lines[end:]     # keep a blank separator
    open(doc_path, "w", encoding="utf-8").write("\n".join(new) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--blocks", default=",".join(ALL_BLOCKS),
                    help="comma list from: " + ", ".join(ALL_BLOCKS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--k", type=int, default=5, help="metrology held-out folds")
    ap.add_argument("--n-perms", type=int, default=500, help="metrology null draws")
    ap.add_argument("--dp-iters", type=int, default=6, help="segmenter EM iterations")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--write-doc", action="store_true",
                    help="splice the generated section into the Phase-1 doc")
    ap.add_argument("--summary-only", action="store_true",
                    help="print the markdown without writing anything")
    args = ap.parse_args(argv)

    blocks = tuple(x for x in args.blocks.split(",") if x)
    unknown = [x for x in blocks if x not in ALL_BLOCKS]
    if unknown:
        sys.exit(f"unknown block(s): {unknown}")

    result = build(blocks=blocks, seed=args.seed, k=args.k, n_perms=args.n_perms,
                   dp_iters=args.dp_iters)
    md = render_md(result)
    print(md)
    if not args.summary_only:
        json.dump(result, open(args.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1, sort_keys=True)
        print(f"result -> {args.out}")
        if args.write_doc:
            if set(blocks) != set(ALL_BLOCKS):
                sys.exit("--write-doc requires all blocks (the doc section is whole)")
            splice_doc(md)
            print(f"doc section spliced -> {DOC}")
    if result["verdict_flips"]:
        print(f"WARNING: verdict_flips={result['verdict_flips']} — NOT a claim; "
              f"requires a new preregistered run (see discipline rule)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
