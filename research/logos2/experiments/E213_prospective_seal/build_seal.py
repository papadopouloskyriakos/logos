#!/usr/bin/env python3
"""E213 prospective seal builder. Runs ONLY after E204 terminal scoring (reads its status;
includes LOO-stable relations iff any). Seals ONLY L2/L3 structural predictions with
mechanical decision rules. NEVER seals: E206 failed matches, RAG interpretations, phonetic
values, language-family claims. Hard RAG index cutoff: INDEX_MANIFEST.sha256 embedded."""
import hashlib, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # research/logos2
E204F = os.path.join(ROOT, "experiments", "E204_metrology", "E204_FINAL_STATUS.json")
E204S = os.path.join(ROOT, "experiments", "E204_metrology", "results_metrology",
                     "METROLOGY_SOFT_RESULTS.json")
RAGMAN = os.path.join(ROOT, "rag", "INDEX_MANIFEST.sha256")

def main():
    if not os.path.exists(E204F):
        print("REFUSED: E204 not terminally scored"); return 1
    if os.path.exists(os.path.join(HERE, "SEAL_MANIFEST.json")):
        print("REFUSED: seal already exists (append-only)"); return 1
    e204 = json.load(open(E204F))
    preds = [
        {"id": "P1_A_INITIAL", "layer": "L2",
         "basis": "E207 POSITIONAL_ONLY + prior-campaign graduated A-initial enrichment (E103R)",
         "prediction": ("In newly published Linear A administrative inscriptions (post-cutoff, "
                        ">=15 inscriptions, >=60 word tokens), the word-initial rate of sign A "
                        "exceeds its all-positions rate."),
         "decision_rule": ("one-sided exact binomial: n = word tokens, k = A-initial tokens, "
                           "p0 = corpus all-positions A rate recomputed on the NEW data only; "
                           "SUPPORTED iff p < 0.05; REFUTED iff observed rate < p0; else UNDERPOWERED."),
         "no_value_claim": True},
        {"id": "P2_LEDGER_TERMINAL_TOTAL", "layer": "L2/L3-functional",
         "basis": "prior-campaign KU-RO-terminal graduated finding (K1-adaptive-validated)",
         "prediction": ("In newly published multi-entry ledger-format tablets (>=5 tablets with "
                        ">=3 numbered entries each), the KU-RO sign-group occurs in the terminal "
                        "summary position in a majority, and where a number follows it, that number "
                        "equals the column sum within scribal-error tolerance (<=1 unit) in >=60%."),
         "decision_rule": ("count both criteria per tablet; SUPPORTED iff exact binomial vs 0.25 "
                           "structural-position chance gives p < 0.05 AND sum-agreement >= 60%; "
                           "REFUTED iff terminal-position rate <= chance; else UNDERPOWERED."),
         "no_value_claim": True},
    ]
    soft = json.load(open(E204S)) if os.path.exists(E204S) else {}
    stable = soft.get("loo_stable_relations", [])
    if stable and e204["E204_TERMINAL_STATUS"] in ("L3_METROLOGICAL_CLASS_SUPPORTED",
                                                    "METROLOGICAL_RELATIONS_PARTIAL"):
        preds.append({"id": "P3_FRACTION_RELATIONS", "layer": "L2 relational",
                      "basis": f"E204 soft arm ({e204['E204_TERMINAL_STATUS']})",
                      "prediction": ("Newly published fraction-bearing arithmetic documents "
                                     f"(>=5) remain jointly satisfiable under the relations {stable} "
                                     "at the soft optimum of the frozen pipeline."),
                      "decision_rule": ("rerun run_metrology_soft.py with new docs appended; "
                                        "SUPPORTED iff all listed relations persist LOO-stable; "
                                        "REFUTED iff any relation becomes unsatisfiable at optimum; "
                                        "else UNDERPOWERED."),
                      "no_value_claim": True})
    sealed = {
        "experiment": "E213", "sealed_date": "2026-07-10",
        "predictions": preds,
        "excluded_by_rule": ["E206 onomastic matches (verdict NO_MATCH_BEYOND_CANARIES — nothing to seal)",
                              "RAG retrievals/interpretations (NOT_A_CHANNEL)",
                              "any phonetic value", "any language-family claim"],
        "opening_condition": ("New Linear A inscriptions published AFTER 2026-07-10 and ingested "
                               "to silver with provenance meeting each prediction's minimum n. "
                               "Scoring uses ONLY the frozen RAG index snapshot below for prior-art "
                               "checks — post-cutoff scholarship may not inform scoring choices."),
        "rag_index_cutoff_sha256": open(RAGMAN).read().strip(),
        "relation_to_prior_seal": ("Distinct from the 72h FRACTION_ORDER_ANETAKI seal (which stays "
                                    "closed and is NOT superseded); no prediction here overlaps it."),
    }
    blob = json.dumps(sealed, indent=1, sort_keys=True).encode()
    open(os.path.join(HERE, "SEALED_PREDICTIONS.json"), "wb").write(blob)
    man = {"experiment": "E213", "sealed_file": "SEALED_PREDICTIONS.json",
           "sealed_sha256": hashlib.sha256(blob).hexdigest(), "opened": False,
           "verify_without_opening": "sha256sum SEALED_PREDICTIONS.json == sealed_sha256",
           "n_predictions": len(preds), "status": "SEALED_PROSPECTIVE"}
    json.dump(man, open(os.path.join(HERE, "SEAL_MANIFEST.json"), "w"), indent=1)
    print(f"SEALED: {len(preds)} predictions | sha256 {man['sealed_sha256'][:16]}…")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
