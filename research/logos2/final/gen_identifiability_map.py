#!/usr/bin/env python3
"""IDENTIFIABILITY_MAP.json — generated from E203 result artifacts (invariant 12)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "experiments", "E203_identifiability_engine", "results")
def j(n): return json.load(open(os.path.join(R, n)))
counts, nulls, mus = j("F1_exact_counts.json"), j("F1_extended_nulls.json"), j("F1_mus_cores.json")
out = {
 "generated_from": ["F1_exact_counts.json", "F1_extended_nulls.json", "F1_mus_cores.json"],
 "ambiguity_log10_by_configuration": {
   k: {"log10_count": v["log10_count"], "exact": v["exact"],
       "n_components": v["n_components"], "largest_component": v["largest_component"]}
   for k, v in counts["configs"].items()},
 "null_adjudication": nulls["systems"],
 "mus_cores": {k: {"sizes": v["empirical_mus_sizes"], "verdict": v["verdict"]}
               for k, v in mus["systems"].items()},
 "reading": ("Ambiguity remains astronomically underdetermined under every configuration; "
             "hard-pin UNSAT is generic (matched nulls UNSAT 200/200); MUS cores are "
             "typical of random instances. No non-generic domain contraction exists at "
             "current evidence. Identifiability threshold as priced by the anchor-lattice "
             "campaign stands: 12 anchors x 8 slots across 12 distinct lineages; foothold 2-3; "
             "Linear A holds zero dependency-collapsed independent anchors."),
}
json.dump(out, open(os.path.join(ROOT, "final", "IDENTIFIABILITY_MAP.json"), "w"), indent=1)
print("IDENTIFIABILITY_MAP.json:", len(out["ambiguity_log10_by_configuration"]), "configurations")
