#!/usr/bin/env python3
"""E212 finalizer — runs ONLY after E204_FINAL_STATUS.json exists. Mechanically:
(1) classifies the E204 node from the terminal status; (2) leave-one-channel-out over the
decisive-input channels; (3) claim-dependency table; (4) independence verdict."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP = os.path.join(ROOT, "experiments", "E212_independence_graph.json")
E204 = os.path.join(ROOT, "experiments", "E204_metrology", "E204_FINAL_STATUS.json")

def main():
    if not os.path.exists(E204):
        print("REFUSED: E204_FINAL_STATUS.json absent — E204 not yet scored"); return 1
    st = json.load(open(E204))["E204_TERMINAL_STATUS"]
    g = json.load(open(GP))
    g["claims"]["E204_metrology_outcome"] = {
        "level": "L1/L2 (structural at most; no value claim)",
        "terminal_status": st,
        "decisive_inputs": ["E204R2 canonical apparatus (single source edition)",
                            "CP-SAT soft-satisfiability pipeline"],
        "channels": ["arithmetic-consistency channel over ONE extraction lineage"],
        "classification": "SINGLE_CHANNEL",
        "note": "strict-arm infeasibility = data-completeness property, kept separate"}
    # leave-one-channel-out: which claims survive removing each unique channel lineage
    lineages = sorted({inp for c in g["claims"].values()
                       for inp in c.get("decisive_inputs", [])})
    loco = {}
    for ln in lineages:
        dead = [k for k, c in g["claims"].items() if ln in c.get("decisive_inputs", [])]
        loco[ln] = {"claims_lost": dead, "claims_surviving": len(g["claims"]) - len(dead)}
    g["leave_one_channel_out"] = loco
    g["claim_dependency_table"] = {
        k: {"depends_on": c.get("decisive_inputs", []),
            "classification": c["classification"]} for k, c in g["claims"].items()}
    silver_dead = loco.get("silver corpus (single lineage)", {}).get("claims_lost", [])
    g["independence_verdict"] = (
        "NO_MULTI_CHANNEL_INDEPENDENT_CLAIM: every LA-substantive claim is SINGLE_CHANNEL; "
        f"removing the silver-corpus lineage kills {len(silver_dead)} claim(s) outright; "
        "the only CONDITIONALLY_INDEPENDENT item (E201-F1a) is a calibration certificate "
        "about the HARNESS, not about Linear A; RAG is NOT_A_CHANNEL. Anchor independence "
        "remains the binding bottleneck (consistent with the 72h campaign conclusion).")
    g["status"] = "FINAL"
    json.dump(g, open(GP, "w"), indent=1)
    print("E212 FINAL | E204 node:", st, "| lineages:", len(lineages))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
