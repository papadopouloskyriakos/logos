"""§VI held-out / generalization.

(a) Known-pair leave-one-out DIAGNOSTIC — POSTHOC_DEVELOPMENT_BENCHMARK / NOT_CONFIRMATORY. Quantifies
    how many of the five known continuities the exact/near-exact model can even REPRESENT (the drift
    problem). It sets no threshold and alters no model.
(b) Administrative evaluation — PRIMARY × EVALUATION, run once after the freezes; ARKH reported
    separately; effective-independence bookkeeping.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import cfg, model as M, partitions as P  # noqa: E402

_LEDGER = os.path.join(os.path.dirname(cfg.GOLD), "quarantine", "known_persistence_pairs.jsonl")


def known_pair_diagnostic():
    """DEVELOPMENT diagnostic only: match each known LA form against its known LB form under A1–A5."""
    ledger = [json.loads(l) for l in open(_LEDGER, encoding="utf-8")]
    tgts = {t["standard_transliteration"]: t for t in P.load_targets()}
    rows = []
    for r in ledger:
        if r["confirmatory_eligibility"].startswith("SPECULATIVE"):
            continue
        la = {"candidate_id": r["linear_a_form"], "raw_sign_ids": r["linear_a_raw_sign_sequence"],
              "uncertainty": {"composite_sensitive": False, "damaged": False}}
        # its LB counterpart among the DEVELOPMENT targets (attested form)
        lb_form = r["linear_b_form"]
        # map bare di-ka-ta / i-da to their attested derived dev targets
        alias = {"di-ka-ta": "di-ka-ta-de", "i-da": "i-da-i-jo"}
        t = tgts.get(lb_form) or tgts.get(alias.get(lb_form, ""))
        res = {L: (M.matches(la, t, L) if t else None) for L in ("A1", "A2", "A3", "A4", "A5")}
        rows.append({"pair": r["linear_a_form"], "lb": lb_form,
                     "la_raw": r["linear_a_raw_sign_sequence"],
                     "lb_raw": (t["raw_sign_sequence"] if t else None),
                     "la_absent": not r["linear_a_source_documents"],
                     "layers": res,
                     "representable_exact": bool(res["A1"]),
                     "label": "POSTHOC_DEVELOPMENT_BENCHMARK / NOT_CONFIRMATORY"})
    n_exact = sum(1 for x in rows if x["representable_exact"])
    return {"rows": rows, "n_known": len(rows), "n_exact_representable": n_exact,
            "interpretation": f"{n_exact}/{len(rows)} known continuities are exact-representable; the rest "
                              "involve orthographic drift / derived forms / absence that the no-free-mapping "
                              "model cannot span. DEVELOPMENT DIAGNOSTIC ONLY."}


def administrative_evaluation():
    prim = P.partitioned()["PRIMARY_B"]
    arkh = [c for c in prim if c.get("site_ambiguity")]
    prim_unamb = [c for c in prim if not c.get("site_ambiguity")]
    ev = [t for t in P.load_targets() if t["development_or_evaluation_role"] == "EVALUATION"]
    res = {L: M.summary(prim, ev, L)["n_pairs"] for L in ("A1", "A2", "A3", "A4", "A5")}
    res_unamb = {L: M.summary(prim_unamb, ev, L)["n_pairs"] for L in ("A1", "A2", "A3")}
    res_arkh = {L: M.summary(arkh, ev, L)["n_pairs"] for L in ("A1", "A2", "A3")}
    return {"primary_x_evaluation": res, "run_once_after_freeze": True,
            "arkh_reported_separately": {"n_arkh": len(arkh), "matches": res_arkh,
                                         "non_arkh_matches": res_unamb},
            "effective_independence": P.unit_summary(),
            "n_unique_candidates_primary": len(prim), "n_unique_targets_evaluation": len(ev)}


def run():
    cfg.verify_inputs()
    return {"analysis_version": cfg.ANALYSIS_VERSION,
            "known_pair_LOO_diagnostic": known_pair_diagnostic(),
            "administrative_evaluation": administrative_evaluation()}


if __name__ == "__main__":
    r = run()
    kp = r["known_pair_LOO_diagnostic"]
    print("known-pair diagnostic (DEVELOPMENT ONLY):")
    for x in kp["rows"]:
        print(f"  {x['pair']:11} vs {x['lb']:11} A1={x['layers']['A1']} A3={x['layers']['A3']} "
              f"absent={x['la_absent']}  la={x['la_raw']} lb={x['lb_raw']}")
    print(" ", kp["interpretation"])
    print("\nadministrative PRIMARY×EVAL:", r["administrative_evaluation"]["primary_x_evaluation"])
    print("effective independence:", r["administrative_evaluation"]["effective_independence"])
    os.makedirs(cfg.RESULTS, exist_ok=True)
    json.dump(r, open(os.path.join(cfg.RESULTS, "heldout.json"), "w"), indent=1)
    print("saved heldout.json")
