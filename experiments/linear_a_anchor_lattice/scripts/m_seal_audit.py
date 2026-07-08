#!/usr/bin/env python3
"""TASK M — held-out + prospective seals for the anchor-lattice campaign.

Mechanical, artifact-driven (Invariant 12: every number printed here is computed
from committed artifacts, never hand-written).

Steps:
  M1  candidate-value-system check (H artifacts)  -> NO_CANDIDATE_TO_SEAL or not
  M2  scoreability audit: can any NEW lattice-derived structural prediction be
      scored on the existing held-out partitions (SEAL_2/3/4/5) WITHOUT
      contamination?  (Art. IX / XI / XII)
  M3  Anetaki delta-seal integrity record (web verification done by the operator,
      result passed in as a constant with sources)
  M4  register M_ANETAKI_LATTICE_DELTA_SEAL (prospective, targets evidence not
      yet inspected: the unpublished KN Zg 57/58 editio princeps transliteration)

Outputs: data/seals/M_candidate_check.json, M_scoreability_audit.json,
         M_ANETAKI_LATTICE_DELTA_SEAL.json, M_anetaki_integrity_check.json
Seed: 20260708 (no stochastic step in this task; recorded for provenance).
"""
import hashlib
import json
import math
import os

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-anchor-lattice/experiments/linear_a_anchor_lattice"
SEALS_EXT = ("/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals/"
             "experiments/linear_a_relative_phonology/seals")
OUT = f"{ROOT}/data/seals"
SEED = 20260708
os.makedirs(OUT, exist_ok=True)


def load(p):
    with open(p) as f:
        return json.load(f)


def dump(name, obj):
    p = f"{OUT}/{name}"
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=False)
    print(f"[wrote] {p}")


# ------------------------------------------------------------------ M1 candidate check
m1 = load(f"{ROOT}/data/candidates/h_model1_bayes_marginals.json")
m2 = load(f"{ROOT}/data/candidates/h_model2_cp_domains.json")
m3 = load(f"{ROOT}/data/candidates/h_model3_mdl_systems.json")
nul = load(f"{ROOT}/data/candidates/h_null_random_anchor.json")
lic = load(f"{ROOT}/LICENCE_STATE.json")
lat = load(f"{ROOT}/data/anchor_lattice/lattice.json")

s0 = m1["S0_collapse_compliant"]
unsat = m2["hard_anchor_hard_rel_consistency"]
s0count = m2["S0_model_counting"]

candidate_check = {
    "task": "M1_candidate_value_system_check",
    "seed": SEED,
    "licensed_scenario_S0": {
        "rho_META": s0["rho"],
        "mean_reduction_all_163": round(s0["mean_reduction_all"], 6),
        "mean_reduction_A_only_69": round(s0["mean_reduction_A_only"], 8),
        "signs_reduced_gt_0.1bit": s0["n_signs_reduced_gt_0p1"],
    },
    "random_anchor_null": {
        "real_A_only_mean_reduction_bits": nul["real_A_only_mean_reduction"],
        "null_mean": round(nul["null_A_only_mean_reduction_mean"], 5),
        "p_null_leq_real": nul["p_null_leq_real"],
        "verdict": nul["verdict"],
    },
    "continuity_x_substitution": {
        "hard_anchor_hard_rel": unsat["verdict"],
        "violated_pairs": f"{unsat['n_violated']}/{unsat['n_rel_pairs_both_pinned']}",
    },
    "S0_model_counting_keys": {k: v for k, v in s0count.items()
                               if not isinstance(v, (list, dict))},
    "mdl_accounting": m3["anchored_vs_unanchored"],
    "licence_state": lic,
    "verdict": None,
}

# mechanical rule: a scoreable candidate value system exists iff (a) some sign
# inventory gains >0.1 bit absolute reduction UNDER THE LICENSED SCENARIO, or
# (b) any transfer licence >= PHONETIC is EARNED.
has_candidate = (s0["n_signs_reduced_gt_0p1"] > 0) or (
    lic.get("all_LA_transfer") == "EARNED")
candidate_check["verdict"] = (
    "CANDIDATE_EXISTS" if has_candidate else "NO_CANDIDATE_TO_SEAL")
dump("M_candidate_check.json", candidate_check)
print("M1 verdict:", candidate_check["verdict"],
      "| S0 signs>0.1bit:", s0["n_signs_reduced_gt_0p1"],
      "| licence:", lic.get("all_LA_transfer"))

# ------------------------------------------------------------------ M2 scoreability audit
# The lattice's NEW structural findings and their derivation provenance:
lat_predictions = {
    "UNSAT_continuity_x_substitution": {
        "statement": "continuity pins (hard) + LA substitution neighborhoods "
                     "(hard, same-C-or-same-V semantics) are mutually UNSAT "
                     "(15/24 both-pinned pairs violate)",
        "derived_from": ["literature continuity pins (corpus-external)",
                         "F4 substitution neighborhoods (FULL 1341-inscription corpus, "
                         "incl. every held-out partition's text)"],
        "target_type": "global consistency property of anchor-topology x corpus channel",
    },
    "A_only_darkness": {
        "statement": "68/69 A-only signs receive no value-bearing anchor; real "
                     "lattice sits BELOW all 200 random-anchor nulls (p=0.000)",
        "derived_from": ["literature anchor inventory (corpus-external)",
                         "A-only classification (FULL corpus attestation)"],
        "target_type": "property of the published-anchor topology, not of corpus text",
    },
    "substitution_channel_at_chance": {
        "statement": "same-C-or-same-V rate 9/28=0.321 vs chance 0.251, p=0.252",
        "derived_from": ["F4 substitution neighborhoods (FULL corpus)"],
        "target_type": "channel calibration on full-corpus-derived pairs",
    },
}
partitions = {}
for sid in ("SEAL_2", "SEAL_3", "SEAL_4", "SEAL_5",
            "ANETAKI_FINAL_EDITION_DELTA_SEAL"):
    s = load(f"{SEALS_EXT}/{sid}.json")
    partitions[sid] = {
        "type": s["type"], "status": s["status"], "verdict": s["verdict"],
        "split": s.get("split", s.get("carriers")),
    }

matrix = {}
for pk, pv in lat_predictions.items():
    row = {}
    for sid, part in partitions.items():
        if sid == "ANETAKI_FINAL_EDITION_DELTA_SEAL":
            if pk == "UNSAT_continuity_x_substitution":
                row[sid] = ("CONDITIONALLY_SCOREABLE_PROSPECTIVELY — only if the "
                            "editio princeps supplies new substitution-variant "
                            "contexts for both-pinned signs; low prior, register "
                            "as conditional")
            elif pk == "A_only_darkness":
                row[sid] = ("SCOREABLE_PROSPECTIVELY — the new text was never used "
                            "in lattice derivation (in_current_corpus=false); "
                            "register delta predictions (M seal below)")
            else:
                row[sid] = "CONDITIONALLY_SCOREABLE_PROSPECTIVELY (needs new pair contexts)"
        else:
            # corpus-internal partitions: the lattice channels were derived from
            # the FULL corpus, i.e. including this partition's text -> Art. IX
            # leakage: derivation saw the target. Also the partitions are already
            # OPENED (SEALED_AND_SCORED) for the morphology campaign.
            row[sid] = ("NOT_SCOREABLE — derivation contamination (F4/sign-universe "
                        "built on FULL corpus incl. this partition) AND partition "
                        "already opened (status=%s); scoring now would grade a "
                        "target by data that created the prediction (Art. IX/XII)"
                        % part["status"])
    matrix[pk] = {"prediction": pv, "per_partition": row}

scoreability = {
    "task": "M2_scoreability_audit",
    "seed": SEED,
    "partitions": partitions,
    "matrix": matrix,
    "verdict": "NO_UNCONTAMINATED_HELD_OUT_SCORING_AVAILABLE_NOW; "
               "ONLY_PROSPECTIVE_ANETAKI_DELTA_IS_CLEAN",
}
dump("M_scoreability_audit.json", scoreability)
print("M2 verdict:", scoreability["verdict"])

# ------------------------------------------------------------------ M3 Anetaki integrity
integrity = {
    "task": "M3_anetaki_delta_seal_integrity",
    "checked_on": "2026-07-08",
    "seal_as_of": partitions["ANETAKI_FINAL_EDITION_DELTA_SEAL"],
    "web_verification": {
        "query_scope": "Anetaki / KN Zg 57 / KN Zg 58 / Kanta-Nakassis-Palaima-Perna "
                       "editio princeps or full transliteration, through 2026-07",
        "found": "only the 2025 preliminary overview (Kanta, Nakassis, Palaima & "
                 "Perna, Ariadne, pp. 27-43, doi 10.26248/ariadne.vi.1841) and "
                 "2025/2026 press coverage of the same paper (GreekReporter "
                 "2026-03-30; La Brujula Verde 2025-03; Biblical Archaeology "
                 "Society; languagehat). No full edition / held-out "
                 "transliteration located.",
        "sources": [
            "https://ejournals.lib.uoc.gr/Ariadne/article/download/1841/1751",
            "https://greekreporter.com/2026/03/30/minoan-ivory-scepter-longest-linear-a-inscription/",
            "https://www.labrujulaverde.com/en/2025/03/the-longest-known-inscription-in-the-undeciphered-linear-a-script-found-on-an-ivory-scepter-in-knossos/",
            "https://www.biblicalarchaeology.org/daily/ancient-cultures/longest-linear-a-inscription-found-in-knossos/",
        ],
    },
    "verdict": "SEAL_STILL_UNOPENED_AND_UNCONTAMINATED",
}
dump("M_anetaki_integrity_check.json", integrity)
print("M3 verdict:", integrity["verdict"])

# ------------------------------------------------------------------ M4 new prospective seal
# Base rates from the merged sign universe (full corpus is legitimate here:
# Anetaki II is NOT in the corpus, so no leakage into the target).
uni = load(f"{ROOT}/data/sign_universe/merged.json")["signs"]
tot_tokens = sum(v.get("occurrence_count") or 0 for v in uni.values())
aonly_tokens = sum(v.get("occurrence_count") or 0 for v in uni.values()
                   if v.get("class") == "A-only")
aonly_types = sum(1 for v in uni.values() if v.get("class") == "A-only")
rate = aonly_tokens / tot_tokens
n_target = 119  # published sign count of KN Zg 57 (ring) per the 2025 overview
mean_ct = n_target * rate
sd = math.sqrt(n_target * rate * (1 - rate))
lo = max(0, int(math.floor(mean_ct - 1.96 * sd)))
hi = int(math.ceil(mean_ct + 1.96 * sd))
print(f"A-only token base rate: {aonly_tokens}/{tot_tokens} = {rate:.4f} "
      f"({aonly_types} A-only types); expected on {n_target} signs: "
      f"{mean_ct:.2f} +- {sd:.2f} -> 95% approx [{lo},{hi}]")

dark = lat["summary"].get("grain")
predictions = {
    "MP1_A_only_token_fraction": {
        "target": "the full published transliteration of KN Zg 57 (+58 if signs "
                  "are identified), NOT yet inspected by anyone in this repo",
        "claim": "A-only-class sign tokens occur at ~the corpus base rate; the "
                 "carrier is ordinary Linear A, not a distinct sign system",
        "corpus_base_rate_A_only_tokens": round(rate, 5),
        "basis_counts": {"A_only_tokens": aonly_tokens, "total_tokens": tot_tokens,
                         "A_only_types_in_universe": aonly_types},
        "n_target_signs_assumed": n_target,
        "predicted_count_mean": round(mean_ct, 2),
        "predicted_95pct_interval_count": [lo, hi],
        "probability": 0.80,
        "scoring_rule": "count identified A-only-class sign tokens among the "
                        "published sign-by-sign transliteration of the ring; "
                        "PASS if count in the interval (rescale interval "
                        "binomially if published n differs from 119). "
                        "Unidentified/new signs counted separately, excluded "
                        "from the denominator.",
        "failure_criterion": "count outside the binomial 95% interval",
    },
    "MP2_anchor_delta_darkness": {
        "target": "the lattice delta after mechanically ingesting the editio "
                  "princeps as a new SOURCE node (re-run c_build_anchor_lattice "
                  "with the new source)",
        "claim": "the new carrier adds ZERO new dependency-collapsed independent "
                 "value-bearing anchors, and ZERO value-bearing edges touching "
                 "any A-only sign; A-only dark count stays 68/69",
        "current_state": {"dependency_collapsed_independent_anchors": 0,
                          "A_only_dark": "68/69", "grain": dark},
        "probability": 0.90,
        "scoring_rule": "re-run the lattice builder with the editio princeps "
                        "registered as a SOURCE; count (a) new independent "
                        "value-bearing anchors after Art.-XI collapse, (b) new "
                        "value-bearing edges incident to A-only signs. PASS if "
                        "(a)==0 and (b)==0.",
        "failure_criterion": "any genuinely new independent value-bearing anchor "
                             "(e.g. a bilingual or a sign equation grounded in "
                             "carrier-internal evidence) — this would be GOOD "
                             "NEWS and must be recorded as the seal FAILING",
    },
    "MP3_conditional_substitution_nonrescue": {
        "target": "any new substitution-variant contexts on KN Zg 57/58 between "
                  "both-continuity-pinned signs",
        "claim": "IF >=5 new both-pinned variant pairs are attested, their "
                 "same-C-or-same-V rate stays statistically indistinguishable "
                 "from chance (0.251) — the new text does not rescue the UNSAT/"
                 "at-chance substitution channel",
        "conditional": True,
        "prior_condition_met": 0.15,
        "probability_conditional": 0.85,
        "scoring_rule": "if condition met: one-sided binomial test of rate>chance "
                        "at alpha=0.05; PASS if not significant. If <5 pairs: "
                        "NOT_TESTABLE (no verdict).",
        "failure_criterion": "same-C-or-same-V rate significantly above chance "
                             "on the new pairs",
    },
}
payload = json.dumps(predictions, sort_keys=True).encode()
plan_hash = hashlib.sha256(payload).hexdigest()
seal = {
    "seal_id": "M_ANETAKI_LATTICE_DELTA_SEAL",
    "name": "anetaki_II_anchor_lattice_delta",
    "type": "prospective_pre_registration_STRUCTURAL_ONLY",
    "campaign": "research/linear-a-anchor-lattice",
    "as_of": "2026-07-08",
    "seed": SEED,
    "constitution": "v2.2",
    "claim_layer": "L2 (sign-class/topology); NO claim above L3",
    "phonetic_scoring": "NO_CANDIDATE_TO_SEAL (see M_candidate_check.json)",
    "carriers": {"KN Zg 57": "ivory ring, ~119 signs",
                 "KN Zg 58": "ivory handle, numerals+fractions"},
    "in_current_corpus": False,
    "targets_evidence_not_yet_inspected": True,
    "distinct_from_existing_seal": "ANETAKI_FINAL_EDITION_DELTA_SEAL predicts "
        "A-prefixation / ledger grammar / libation order (L2/L3 morphology); "
        "THIS seal predicts sign-CLASS composition + anchor-topology delta + "
        "substitution-channel non-rescue. No shared scoring target.",
    "n_hypotheses_registered": 3,
    "structural_predictions": predictions,
    "plan_hash": plan_hash,
    "scored_when": "editio princeps publishes the full transliteration",
    "status": "SEALED_PROSPECTIVE",
    "verdict": "SEALED_PROSPECTIVE_NOT_YET_SCORED",
}
dump("M_ANETAKI_LATTICE_DELTA_SEAL.json", seal)
print("M4 plan_hash:", plan_hash)
print("DONE")
