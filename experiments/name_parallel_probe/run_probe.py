#!/usr/bin/env python3
"""run_probe.py — NAME-PARALLEL-01: the single gated Linear A name-parallel probe run.

Thin driver over scripts/comparison/name_parallel.py. FAIL-CLOSED gates, in order:
  1. results/name_parallel_calibration.json must exist, be a full (fast=false) run, and be GREEN
     (positive control fires + bar-v2 false-fire CP95 <= 0.05). RED/absent => verdict INVALID,
     the LA true-value statistic is never computed.
  2. prereg.md + plan_hash.txt must exist here and plan_hash.txt must equal sha256(prereg.md)
     (epoch_runner file-prereg contract). Missing/mismatched => refuse before computing anything.

Then, ONCE: M_obs = match_count(LA decodable pool, KN-attested names, C1) — the first and only
time the true-value statistic is computed (invariant #1: prediction committed first).
Verdict per prereg P1 (mechanical): MATCH_EXCESS iff M_obs > augmented bar
(max(banded E[max], banded corrected margin, out-of-sample lfake floor) at instrumented n_eff);
NULL if below and the power row says a plausible effect was detectable; DATA-LIMITED if below
and it was not; INVALID only via gate failure.
Strata S1/S2 + N2 doc-permutation + effective_n + info-budget panel are REPORTED, non-verdict.

Interpretation cap (prereg): L3; a MATCH_EXCESS validates NO individual sign value, creates NO
anchor, leaves REFUTE_LOTO_FRAGILE and the anchor-lattice foothold≈0 untouched.

    PYTHONPATH=. python3 experiments/name_parallel_probe/run_probe.py [--dry-run]
"""
import argparse
import hashlib
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

from scripts.comparison import name_parallel as npb  # noqa: E402
from scripts import effective_n as en  # noqa: E402
from scripts import info_budget as ib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = os.path.join(HERE, "prereg.md")
PLAN_HASH = os.path.join(HERE, "plan_hash.txt")
RESULT = os.path.join(HERE, "result.json")
CALIBRATION = npb.CALIBRATION_JSON

TASK_ID = "NAME-PARALLEL-01"
ALLOWED_VERDICTS = ("MATCH_EXCESS", "NULL", "DATA-LIMITED", "INVALID")
SEED = 0
B_MAP = 1000
B_DOC = 500
B_STRATUM = 200


def _refuse(reason, extra=None):
    out = {"task_id": TASK_ID, "verdict": "INVALID",
           "numbers": {"gate_refusal": reason, **(extra or {})},
           "key_findings": [f"probe refused before computing the LA statistic: {reason}"],
           "successor_hypotheses": ["fix the failed gate, then re-run; the LA statistic remains uncomputed"]}
    json.dump(out, open(RESULT, "w"), indent=1)
    print(f"REFUSED (fail closed): {reason}")
    return 2


def gates():
    """Returns (calibration dict) or an int exit code from _refuse."""
    if not os.path.exists(CALIBRATION):
        return _refuse("calibration file absent")
    cal = json.load(open(CALIBRATION))
    if cal.get("fast"):
        return _refuse("calibration file is a fast run — full run required")
    if not cal.get("calibration_green"):
        return _refuse("calibration is RED (calibration_green=false)",
                       {"false_fire_cp95": cal.get("false_fire", {}).get(
                           "clopper_pearson_onesided_95_upper")})
    if not (os.path.exists(PREREG) and os.path.exists(PLAN_HASH)):
        return _refuse("prereg.md/plan_hash.txt missing — freeze the prereg first")
    want = open(PLAN_HASH).read().split()[0].strip()
    got = hashlib.sha256(open(PREREG, "rb").read()).hexdigest()
    if want != got:
        return _refuse("plan_hash.txt does not match sha256(prereg.md)")
    return cal


def _attestations(matched, silver_path=npb.STRUCTURED_SILVER):
    """One item per (matched type, attesting doc): {type, doc, site} — Art. VIII units."""
    matched_set = {tuple(t) for t in matched}
    items = []
    for rec in json.load(open(silver_path)):
        for w in rec.get("words", []):
            t = tuple(w)
            if t in matched_set:
                items.append({"type": "-".join(t), "doc": rec["id"], "site": rec["site"]})
    return items


def _stratum_row(stratum_pool, kn_names, n_eff, seed):
    """REPORTED row: the stratum's own count, banded bars, empirical p."""
    if not stratum_pool:
        return {"pool_types": 0, "m": 0, "note": "empty stratum"}
    m = npb.match_count(stratum_pool, kn_names, npb.PRIMARY)
    nulls = npb.n1_banded_null(stratum_pool, kn_names, npb.PRIMARY, B=B_STRATUM, seed=seed)
    bars = npb.bars_from_nulls(nulls, n_eff=n_eff)
    return {"pool_types": len(stratum_pool), "m": int(m),
            "mu0": bars["mu0"], "operative_bar_banded": bars["operative_bar"],
            "empirical_p_vs_banded": float((1 + sum(1 for c in nulls if c >= m))
                                           / (1 + len(nulls)))}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="run the gates only, never the statistic")
    args = ap.parse_args(argv)

    g = gates()
    if isinstance(g, int):
        return g
    cal = g
    if args.dry_run:
        print("gates GREEN (dry run; statistic not computed)")
        return 0

    log = npb.CriterionLog()
    for crit in npb.criterion_grid():
        log.register(crit)
    n_eff = log.n_eff

    la = npb.load_la_packard_pool()
    names_info = npb.load_names_cog()
    docs = npb.load_damos_docs()
    join = npb.kn_attested_names(names_info["names"], docs)
    kn_names = join["kn_names"]
    pool = la["pool"]

    # ---- THE statistic (first and only computation) + confirmatory bars ---------- #
    m_obs = npb.match_count(pool, kn_names, npb.PRIMARY, log=log)
    matched = npb.matched_types(pool, kn_names, npb.PRIMARY)
    nulls_map = npb.n1_banded_null(pool, kn_names, npb.PRIMARY, B=B_MAP, seed=SEED + 1_000_000)
    bars = npb.bars_from_nulls(nulls_map, n_eff=n_eff)
    lfloor = float(cal["false_fire"]["lfake_floor"]["floor"])
    augmented_bar = float(max(bars["operative_bar"], lfloor))

    # ---- power row: k_min planted matches detectable ------------------------------ #
    k_min = int(math.ceil(max(0.0, augmented_bar - bars["mu0"])))
    plausible_band = max(1, int(0.05 * len(pool)))  # 5% of the pool as a generous onomastic band
    data_limited = m_obs <= augmented_bar and k_min > plausible_band

    # ---- reported, non-verdict rows ---------------------------------------------- #
    n2_counts = npb.n2_document_permutation_null(
        pool, names_info["names"], docs, int(join["diagnostics"]["kn_docs_by_collectionid"]),
        npb.PRIMARY, B=B_DOC, seed=SEED + 2_000_000)
    n2 = {"B": B_DOC, "mean": float(np.mean(n2_counts)),
          "p95": float(np.percentile(n2_counts, 95)),
          "empirical_p": float((1 + int(np.sum(np.asarray(n2_counts) >= m_obs)))
                               / (1 + len(n2_counts)))}

    s1_pool = npb.stratum_s1_darkblue(pool, npb.PRIMARY, npb.load_salgarella_darkblue())
    s2_pool = npb.stratum_s2_toponym_excluded(pool, npb.PRIMARY,
                                              npb.load_toponym_covered_signs())
    strata = {"s1_salgarella_darkblue": _stratum_row(s1_pool, kn_names, n_eff, SEED + 3_000_000),
              "s2_toponym_excluded": _stratum_row(s2_pool, kn_names, n_eff, SEED + 4_000_000)}

    attest = _attestations(matched)
    eff = (en.effective_n(attest, dims=["type", "site"])
           if attest else {"raw_n": 0, "effective_n": 0})

    panel = ib.build_panel(
        effective_independent_evidence=eff.get("effective_n", 0),
        parameter_count=0,
        source_dependency_structure="single lineage L_LB_DECIPHERMENT (1 effective vote: "
                                    "SRC-NAMESCOG collapses with SRC-DAMOS, Art. XI)",
        search_space_size=n_eff,
        minimum_detectable_effect=k_min,
        estimated_power=0.0 if k_min > plausible_band else 1.0,
    )

    # ---- mechanical verdict per prereg P1 ----------------------------------------- #
    if m_obs > augmented_bar:
        verdict = "MATCH_EXCESS"
    elif data_limited:
        verdict = "DATA-LIMITED"
    else:
        verdict = "NULL"
    assert verdict in ALLOWED_VERDICTS

    numbers = {
        "m_obs": int(m_obs),
        "n_la_pool_decodable_types": len(pool),
        "n_kn_names": len(kn_names),
        "null_map_mu0": bars["mu0"], "null_map_sigma0": bars["sigma0"],
        "expected_max_order_stat": bars["expected_max_order_stat"],
        "corrected_margin_bar": bars["corrected_margin_bar"],
        "lfake_floor": lfloor,
        "augmented_bar": augmented_bar,
        "empirical_p_vs_banded": float((1 + sum(1 for c in nulls_map if c >= m_obs))
                                       / (1 + len(nulls_map))),
        "n_eff": n_eff,
        "bar_design": "v2 (banded E[max] + corrected margin + out-of-sample lfake floor)",
        "power": {"k_min_detectable": k_min, "plausible_onomastic_band": plausible_band,
                  "data_limited": bool(data_limited)},
        "n2_doc_permutation": n2,
        "strata": strata,
        "matched_la_types": ["-".join(t) for t in matched],
        "attestations_of_matched": len(attest),
        "effective_n": {k: v for k, v in eff.items() if not isinstance(v, dict)},
        "info_budget_panel": panel,
        "seed": SEED, "B_map": B_MAP, "B_doc": B_DOC,
        "calibration_sha256": hashlib.sha256(open(CALIBRATION, "rb").read()).hexdigest(),
    }
    key = {
        "MATCH_EXCESS": [f"M_obs={m_obs} exceeds the augmented bar {augmented_bar:.1f} — "
                         "frequency-band-level onomastic-overlap evidence ONLY (L3 cap; no sign "
                         "value validated, no anchor created)"],
        "NULL": [f"M_obs={m_obs} does not exceed the augmented bar {augmented_bar:.1f}; "
                 f"k_min={k_min} within the plausible onomastic band ({plausible_band}) — a "
                 "plausible effect was detectable and did not appear"],
        "DATA-LIMITED": [f"M_obs={m_obs} below the augmented bar {augmented_bar:.1f} AND "
                         f"k_min={k_min} planted matches needed exceeds the plausible onomastic "
                         f"band ({plausible_band}) — the corpus could not have shown a plausible "
                         "effect at this bar"],
    }[verdict]
    out = {"task_id": TASK_ID, "verdict": verdict, "numbers": _pyify(numbers),
           "key_findings": key,
           "successor_hypotheses": [
               "re-run mechanically on corpus growth per docs/reopening-thresholds.md triggers",
               "a new-site toponym candidate (anchor route) would justify a NEW prereg with a "
               "site-restricted variant",
               "if DATA-LIMITED: the bar is dominated by the lfake floor — only a corpus with "
               "materially different sign texture (new finds) can lower it honestly"]}
    json.dump(out, open(RESULT, "w"), indent=1)
    print(f"{TASK_ID}: verdict={verdict} m_obs={m_obs} bar={augmented_bar:.2f} "
          f"(lfake floor {lfloor:.2f}) k_min={k_min} -> {RESULT}")
    return 0


def _pyify(o):
    if isinstance(o, dict):
        return {k: _pyify(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_pyify(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    return o


if __name__ == "__main__":
    sys.exit(main())
