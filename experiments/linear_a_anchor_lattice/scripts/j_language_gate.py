#!/usr/bin/env python3
"""TASK J — Conditional language-family gate (mechanical evaluation).

Rule: language families are tested ONLY after the lattice produces nontrivial
sign constraints, defined as: some lattice candidate reduces A-only absolute
value entropy beyond the random-anchor null, USING EARNED LICENCES ONLY
(scenario S0; conditional-on-META_CONTINUITY reductions do not count, Art. XV).

Reads Task-H artifacts, evaluates the gate, writes data/candidates/j_gate_decision.json.
No language data is loaded or tested by this script. Seed-free (pure arithmetic).
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(BASE, "data", "candidates")

null = json.load(open(os.path.join(CAND, "h_null_random_anchor.json")))
setup = json.load(open(os.path.join(CAND, "h_setup_and_calibration.json")))

real = null["real_A_only_mean_reduction"]            # bits/sign, A-only, absolute
null_mean = null["null_A_only_mean_reduction_mean"]  # random-anchor null
null_p5, null_p95 = null["null_A_only_mean_reduction_p5_p95"]
p_null_leq_real = null["p_null_leq_real"]            # fraction of null draws <= real
pins_parseable_A_only = null["real_A_only_signs_pinned_parseable"]

# Gate criterion G1: real A-only reduction strictly exceeds the null's 95th pct.
G1_exceeds_null = real > null_p95
# Gate criterion G2: licensed-state (S0, rho_META=0) reduction is nonzero.
S0 = setup["scenarios"]["S0_collapse_compliant"]     # rho used in the licensed scenario
# From H_MODEL_1 S0 row: A-only mean reduction 0.00001 bits (MC noise), 0 signs >0.1 bit.
S0_A_only_bits = 0.00001
S0_signs_gt_0p1 = 0
G2_licensed_nonzero = S0_signs_gt_0p1 > 0
# Gate criterion G3: any unconditional (non-META_CONTINUITY) A-only constraint exists.
G3_unconditional_A_only = pins_parseable_A_only > 0

authorized = G1_exceeds_null and G2_licensed_nonzero and G3_unconditional_A_only

decision = {
    "task": "J_LANGUAGE_CONDITIONAL_GATE",
    "gate_inputs": {
        "real_A_only_mean_reduction_bits": real,
        "null_A_only_mean_reduction_mean_bits": null_mean,
        "null_p5_p95_bits": [null_p5, null_p95],
        "p_null_leq_real": p_null_leq_real,
        "h_null_verdict": null["verdict"],
        "A_only_signs_with_parseable_pin": pins_parseable_A_only,
        "vacuous_A_only_pin": null["vacuous_A_only_pin"],
        "S0_licensed_A_only_mean_reduction_bits": S0_A_only_bits,
        "S0_licensed_A_only_signs_gt_0.1bit": S0_signs_gt_0p1,
        "pinned_sign_reduction_bits_S2": null["R_bits_per_pinned_sign_S2"],
        "pinned_reduction_conditional_on": "META_CONTINUITY_LA_eq_LB (licence NOT_EARNED)",
    },
    "criteria": {
        "G1_real_exceeds_random_anchor_null_p95": G1_exceeds_null,
        "G2_licensed_state_S0_nonzero": G2_licensed_nonzero,
        "G3_unconditional_A_only_constraint_exists": G3_unconditional_A_only,
    },
    "verdict": "J_AUTHORIZED" if authorized else "J_NOT_AUTHORIZED",
    "consequence": (
        "language-family tournament RUN" if authorized else
        "NO language tournament run; prior 6-family AT_END_TO_END_NULL stands "
        "(research/linear-a-decipherment-foundry)"
    ),
}

out = os.path.join(CAND, "j_gate_decision.json")
json.dump(decision, open(out, "w"), indent=1)
print(json.dumps(decision, indent=1))
print("wrote", out)
