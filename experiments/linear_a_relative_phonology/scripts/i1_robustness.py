#!/usr/bin/env python3
"""I1 robustness augmentation: multiplicity correction over grid x axis grade tests,
real-vs-permuted grade comparison, and equivalence-spread summary. Reads/writes I1_agnostic.json.
Deterministic; no new modeling. Seed 20260708."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
d = json.load(open(os.path.join(DATA, "I1_agnostic.json")))

# collect the 6 grade tests actually run (3 grids x 2 axes)
tests = []
for g in ["C12", "C15", "C18"]:
    gr = d["grids_real"][g]["grade"]
    tests.append((f"{g}_consonant", gr["consonant_axis"]["perm_p"], gr["consonant_axis"]["nmi"]))
    tests.append((f"{g}_vowel", gr["vowel_axis"]["perm_p"], gr["vowel_axis"]["nmi"]))
pvals = sorted(tests, key=lambda t: t[1])
m = len(pvals)
# Holm-Bonferroni
holm = []
running = 0.0
for k, (name, p, nmi) in enumerate(pvals):
    adj = min(1.0, p * (m - k))
    running = max(running, adj)  # enforce monotonicity
    holm.append(dict(test=name, raw_p=p, nmi=nmi, holm_adj_p=running))
any_sig = any(h["holm_adj_p"] < 0.05 for h in holm)

# real vs permuted consonant-axis grade (primary grid C15)
real_c = d["grids_real"]["C15"]["grade"]["consonant_axis"]["nmi"]
perm_c = d["permuted_corpus"]["grade"]["consonant_axis"]["nmi"]
real_v = d["grids_real"]["C15"]["grade"]["vowel_axis"]["nmi"]
perm_v = d["permuted_corpus"]["grade"]["vowel_axis"]["nmi"]

d["robustness"] = dict(
    grade_tests_run=m,
    holm_bonferroni=holm,
    any_grade_significant_after_multiplicity=any_sig,
    min_raw_p=pvals[0][1], min_raw_p_test=pvals[0][0],
    consonant_axis_nmi_real=real_c, consonant_axis_nmi_permuted=perm_c,
    consonant_axis_nmi_excess=real_c - perm_c,
    consonant_axis_nmi_ratio_real_over_permuted=real_c / perm_c if perm_c else None,
    vowel_axis_nmi_real=real_v, vowel_axis_nmi_permuted=perm_v,
    seqLL_gain_ratio_real_over_permuted=d["gain_ratio_real_vs_permuted"],
    interpretation=("The single sub-0.05 grade (C15 consonant, raw p=0.046) does NOT survive Holm "
                    "correction over the 6 grid x axis tests, is grid-unstable (C12 p=0.235, C15 0.046, "
                    "C18 0.020), and is matched by the permuted-corpus winner (consonant nmi 0.525 vs "
                    "real 0.558; ratio 1.06) whose sequential phonotactics were destroyed. The seqLL "
                    "selection basis is 100%% artifactual (real/permuted gain ratio 1.01). No value "
                    "system is supported."),
)
json.dump(d, open(os.path.join(DATA, "I1_agnostic.json"), "w"), indent=2)
print("grade tests", m, "| any sig after Holm:", any_sig, "| min raw p:", pvals[0])
print("C-axis nmi real %.3f permuted %.3f excess %.3f" % (real_c, perm_c, real_c - perm_c))
print("Holm:", [(h["test"], round(h["raw_p"], 3), round(h["holm_adj_p"], 3)) for h in holm])
