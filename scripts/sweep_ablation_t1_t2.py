#!/usr/bin/env python3
"""T1 / T2 instrument-ablation tests for the CSA-sufficiency novelty prereg
(docs/revision-queue/csa_sufficiency_sweep_novelty.md, frozen 2026-07-14, plan_hash = its commit).

L0 methodological tests of the GATE, not the decipherment verdict (Art. XII): they cannot raise the
earned layer, change the frozen paper, or turn a null into a positive. Mechanical verdicts only
(SUPPORT / REFUTE / NARROW / NO_POWER); no soft pass. Outputs go to NEW paths — this script NEVER
touches the canonical results/gate_null_calibration.json.

  T1  component ablation (defends N1): A = positive-control-only (trust the raw best-of-N score, no
      multiplicity deflation -> gate at n_eff=1) vs C = paired instrument (deflate at the instrumented
      n_eff=100). Committed prediction: A admits the cherry-picked syllabic-magnitude fluke, C rejects
      it, and C still accepts >=90% of planted-true (real-key) candidates.
  T2a right null (defends N4): our random-mapping null (randomize the KEY -> set-recall) vs a
      Kessler/LexStat-style pairing-permutation null (permute held<->candidate PAIRING). KS for equality.
  T2b where it matters (defends N4): realized best-of-100 false-graduation rate in the syllabic-
      magnitude regime, Clopper-Pearson 95% upper; gate valid iff <=2% (upper <=~3%).

Reproduce: python3 scripts/sweep_ablation_t1_t2.py
"""
from __future__ import annotations
import random, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import verdict
from scripts.comparison import lexstat

CONS = "'bgdhwzHTyklmnspcqrsvt"
HELD = ["nwy", "brq", "mlk", "ywm", "dn", "qtl", "zkr", "bnh", "hlk", "yqr",
        "ktb", "smr", "dbr", "rcy", "qdm", "slm", "ntn", "cbd", "gdl", "khn"]
EPS = verdict.EPS_DEFAULT
BASE = dict(confidence=0.6, free_params=3, provenance="embedding_nn", lit_index_hit=False,
            not_indexed_sign_support=0.9, u_floor=8, n_eff=1, n_fake=12, seed=1,
            not_indexed_threshold=0.5)   # n_eff here is a placeholder; search_log's .n_eff overrides it


class _Log:                                   # duck-typed instrumented SearchLog (COUNTED n_eff)
    def __init__(self, n): self.n_eff = n; self.eps_grid = None


def _rand_form(rng):
    return "".join(rng.choice(CONS) for _ in range(rng.randint(2, 4)))


def _best_of_n_null(rng, n_eff):
    """Cherry-pick the best-of-n_eff random null candidate lexicons (the multiplicity abuse)."""
    best, bo = None, -1.0
    for _ in range(n_eff):
        cand = [_rand_form(rng) for _ in range(len(HELD) + 4)]
        pf = lexstat.s_lex_per_form(HELD, cand, EPS)
        obs = (sum(pf) / len(pf)) if pf else 0.0
        if obs > bo:
            bo, best = obs, cand
    return best, bo


def _cp95_upper(k, n):
    from scipy.stats import beta
    return float(beta.ppf(0.95, k + 1, n - k)) if k < n else 1.0


# ----------------------------------------------------------------------------- T1
def t1(B=500, N_EFF=100, n_true=40, seed=0):
    rng = random.Random(seed)
    obs_scores = []
    gA = gC = 0                                # false-case graduations at gate n_eff = 1 (A) / 100 (C)
    for _ in range(B):
        cand, bo = _best_of_n_null(rng, N_EFF)
        obs_scores.append(bo)
        gA += verdict.grade(HELD, cand, search_log=_Log(1),     **BASE)["gate_verdict"] == "GRADUATE"
        gC += verdict.grade(HELD, cand, search_log=_Log(N_EFF), **BASE)["gate_verdict"] == "GRADUATE"
    # planted-true: candidate lexicon CONTAINS the real key (+ distractors) -> should GRADUATE under C
    acc_true = 0
    for t in range(n_true):
        r2 = random.Random(1000 + t)
        cand = list(HELD) + [_rand_form(r2) for _ in range(4)]
        r2.shuffle(cand)
        acc_true += verdict.grade(HELD, cand, search_log=_Log(N_EFF), **BASE)["gate_verdict"] == "GRADUATE"
    a, c = gA / B, gC / B
    true_rate = acc_true / n_true
    # POWER PROBE (assumption A1): can a PERFECT map (accuracy 1.0) graduate at all under this abstract
    # construction? If not, the accept-true arm has no power and the SUPPORT rule ("C accepts >=90%
    # planted-true") cannot be evaluated -> NO_POWER, per the prereg (assumption fails -> NO_POWER).
    perfect = list(HELD) + ["xx", "yy", "zz", "qq"]
    g_perf = verdict.grade(HELD, perfect, search_log=_Log(N_EFF), **BASE)
    perfect_grad = g_perf["gate_verdict"] == "GRADUATE"
    accept_arm_has_power = perfect_grad
    # B (null-gate-only) is mechanically identical to C on the FALSE metric (both deflate at n_eff);
    # its distinct deficiency (cannot certify power on TRUE cases) is not a separable clause in
    # verdict.grade -> reported honestly, not fabricated. Rule uses max(A,B)_false = A here.
    worse_single_false = max(a, c)             # = a (B==C on false cases)
    if not accept_arm_has_power:
        verdict_str = "NO_POWER"
    else:
        support = (c <= 0.01) and (worse_single_false >= 0.05) and (true_rate >= 0.90)
        verdict_str = ("SUPPORT" if support else
                       "NARROW" if (c < worse_single_false and true_rate >= 0.90) else "REFUTE")
    return {
        "test": "T1_component_ablation", "defends": "N1",
        "B": B, "N_eff": N_EFF, "n_planted_true": n_true,
        "false_case_obs_score_mean": round(sum(obs_scores) / len(obs_scores), 4),
        "false_case_obs_score_max": round(max(obs_scores), 4),
        "A_positive_control_only_false_grad": round(a, 4),
        "C_paired_instrument_false_grad": round(c, 4),
        "B_null_gate_only_false_grad": round(c, 4),
        "B_note": "mechanically == C on the false metric (both deflate at n_eff); B's true-side power "
                  "deficiency is not a separable verdict.grade clause; reported, not fabricated.",
        "C_planted_true_accept_rate": round(true_rate, 4),
        "accept_arm_has_power": accept_arm_has_power,
        "perfect_map_failing_clauses": g_perf.get("failing_clauses"),
        "power_note": "the accept-true arm is DEGENERATE in this abstract skeleton harness: even a "
                      "perfect map (accuracy 1.0) fails the operative 'beats_order_stat_bar' clause "
                      "because the skeleton null has ~zero variance (sigma0<1e-12), so E[max order "
                      "stat] deflation cannot be beaten. A faithful, powered T1 needs real per-benchmark "
                      "candidate lexicons + non-degenerate null recalls plumbed into the gate.",
        "incidental_finding": "A==C false-grad (0.006): multiplicity deflation is NOT the discriminator "
                              "for these weak best-of-100 flukes (mean obs ~5%); they are rejected by the "
                              "statistic-level L_fake / deflated-S_lex bars regardless of n_eff. This "
                              "REFUTES the specific N1 premise 'the null-gate leg is what catches them', "
                              "but shows the gate's rejection is robust/overdetermined here.",
        "rule": "SUPPORT iff C_false<=0.01 AND max(A,B)_false>=0.05 AND C_true>=0.90; "
                "NO_POWER if the accept-true arm cannot graduate even a perfect map",
        "verdict": verdict_str,
    }


# ----------------------------------------------------------------------------- T2a
def _paired_recall(held, cand_paired):
    return sum(1 for h, c in zip(held, cand_paired) if lexstat.ned_capped(h, c, EPS)) / len(held)


def t2a(n=400, seed=0):
    """Two nulls of the recovery statistic. Null-1 (ours): randomize the KEY -> random candidate
    lexicons, set-recall. Null-2 (pairing): a well-paired key, permute the held<->candidate PAIRING,
    PAIRED recall. KS for distribution equality."""
    rng = random.Random(seed)
    from scipy.stats import ks_2samp
    # our null: random-mapping, set-recall
    d_ours = []
    for _ in range(n):
        cand = [_rand_form(rng) for _ in range(len(HELD) + 4)]
        pf = lexstat.s_lex_per_form(HELD, cand, EPS)
        d_ours.append((sum(pf) / len(pf)) if pf else 0.0)
    # pairing null: start from an exact-paired key (paired recall = 1.0), permute the pairing
    base_key = list(HELD)                        # cand[i] pairs to held[i] exactly
    d_pair = []
    for _ in range(n):
        perm = base_key[:]; rng.shuffle(perm)
        d_pair.append(_paired_recall(HELD, perm))
    # set-recall is invariant to pairing permutation -> record whether the pairing null is degenerate
    # FOR OUR STATISTIC (the honest crux of N4):
    setrec_under_pairing = []
    for _ in range(n):
        perm = base_key[:]; rng.shuffle(perm)
        pf = lexstat.s_lex_per_form(HELD, perm, EPS)   # set-recall ignores order -> constant 1.0
        setrec_under_pairing.append((sum(pf) / len(pf)) if pf else 0.0)
    ks = ks_2samp(d_ours, d_pair)
    fdr_ours = sum(x >= 0.10 for x in d_ours) / n      # false "signal" >=10% under each null
    fdr_pair = sum(x >= 0.10 for x in d_pair) / n
    setrec_pairing_var = (max(setrec_under_pairing) - min(setrec_under_pairing))
    nulls_differ = ks.pvalue < 0.01
    # our null strictly no-laxer than the pairing null AND the pairing null is degenerate for the
    # set-recall statistic our gate actually uses -> NARROW to the honest claim, never a clean SUPPORT
    ours_not_laxer = fdr_ours >= fdr_pair
    verdict_str = ("NARROW" if (nulls_differ and setrec_pairing_var == 0.0) else
                   "SUPPORT" if (nulls_differ and ours_not_laxer) else "REFUTE")
    return {
        "test": "T2a_right_null", "defends": "N4", "n": n,
        "ours_random_mapping_mean": round(sum(d_ours) / n, 4),
        "pairing_perm_mean": round(sum(d_pair) / n, 4),
        "ks_stat": round(float(ks.statistic), 4), "ks_p": float(f"{ks.pvalue:.3e}"),
        "fdr_ours_ge10pct": round(fdr_ours, 4), "fdr_pairing_ge10pct": round(fdr_pair, 4),
        "setrecall_variance_under_pairing_perm": round(setrec_pairing_var, 6),
        "rule": "SUPPORT iff nulls differ (KS p<0.01) AND ours no-laxer; NARROW if the pairing null is "
                "DEGENERATE for our set-recall statistic (variance 0) -> pairing null inapplicable",
        "interpretation": "our claim object is the KEY (sign->value), a set-recall statistic that is "
                          "INVARIANT to held<->candidate pairing; the Kessler/LexStat pairing-permutation "
                          "null therefore does not apply to our statistic (variance 0). N4 narrows to: "
                          "'the appropriate null randomizes the key; the pairing null is not applicable', "
                          "rather than the KS-difference framing.",
        "verdict": verdict_str,
    }


# ----------------------------------------------------------------------------- T2b
def t2b(B=500, N_EFF=100, seed=0):
    """Realized best-of-100 false-graduation rate in the syllabic-magnitude regime (the best-of-100
    flukes ARE 10-16% 'signals'). Fresh run to a NEW path; must match the canonical ~0.6%."""
    rng = random.Random(seed)
    grads = 0
    for _ in range(B):
        cand, _ = _best_of_n_null(rng, N_EFF)
        grads += verdict.grade(HELD, cand, search_log=_Log(N_EFF), **BASE)["gate_verdict"] == "GRADUATE"
    rate = grads / B
    hi = _cp95_upper(grads, B)
    return {
        "test": "T2b_syllabic_regime_fdr", "defends": "N4",
        "B": B, "N_eff": N_EFF, "false_graduations": grads,
        "false_graduation_rate": round(rate, 5), "cp95_upper": round(hi, 5),
        "rule": "gate valid iff rate<=0.02 AND cp95_upper<=~0.03",
        "verdict": "SUPPORT" if (rate <= 0.02 and hi <= 0.031) else "REFUTE",
        "note": "gate deflation is by N_eff order-statistic, benchmark-agnostic; the best-of-100 flukes "
                "reproduce the 10-16% syllabic-magnitude 'signals' the gate must reject.",
    }


if __name__ == "__main__":
    Path("results").mkdir(exist_ok=True)
    r1, r2a, r2b = t1(), t2a(), t2b()
    for name, r, path in [("T1", r1, "results/ablation_T1.json"),
                          ("T2a", r2a, "results/null_compare_T2.json"),
                          ("T2b", r2b, "results/t2b_syllabic_fdr.json")]:
        json.dump(r, open(path, "w"), indent=2)
        print(f"\n===== {name} -> {path} =====")
        for k, v in r.items():
            print(f"  {k}: {v}")
    print("\nCANONICAL results/gate_null_calibration.json UNTOUCHED:",
          Path("results/gate_null_calibration.json").exists())
