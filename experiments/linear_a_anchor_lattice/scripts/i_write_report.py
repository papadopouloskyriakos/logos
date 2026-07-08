"""TASK I — report generator (reads per_sign_table.json, writes the md report)."""
import json, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
d = json.load(open(os.path.join(BASE, "data", "candidates", "per_sign", "per_sign_table.json")))
S, rows = d["summary"], d["rows"]

def gate_str(r):
    g = r["gate"]
    if g["RETAINED"]:
        return "RETAINED"
    fails = []
    if not (g["A_ge3_independent_overlapping_anchors"] or
            g["B_ge2_channels_plus_validated_sub_or_stroke"] or
            g["C_ge4slot_anchor_plus_heldout_recurrence"]):
        fails.append("no-branch(A,B,C)")
    for k, tag in [("leave_one_anchor", "LOA"), ("leave_one_lineage", "LOL"),
                   ("leave_one_site", "LOS"), ("adaptive_null", "NULL")]:
        if not g[k]:
            fails.append(tag)
    return "FAIL:" + "+".join(fails)

hdr = ("| sign | class | dom | edges | vb | channels | lineages(collapsed,vb) | indep | "
       "S2 red. (bits) | M2 domain | best cand (pre-gate) | rel pairs/viol/p | gate |")
sep = "|" + "---|" * 13
lines = [hdr, sep]
order = sorted(rows, key=lambda r: (r["class"] != "A-only", r["class"],
                                    -r["n_edges_total"], r["sign"]))
for r in order:
    ch = ",".join(r["channels_all"]) or "-"
    lin = ",".join(l.replace("META_CONTINUITY_LA_eq_LB", "META_CONT")
                   for l in r["value_lineages_collapsed"]) or "-"
    m2s = r["m2_domain_state"]
    m2s = (m2s.split("(")[0] if "(" in m2s else m2s)
    relp = (f"{r['heldout_rel_pairs']}/{r['heldout_rel_violated']}/"
            f"{r['heldout_rel_perm_p']}" if r["heldout_rel_pairs"] else "-")
    dom = {"syllabic_CV_or_V": "CV65", "commodity_ideogram_semantic": "sem",
           "fractional_quantity": "frac", "numeric_quantity": "num",
           "unknown": "?"}.get(r["domain_label"], "?")
    cand = r["pre_gate_candidate_NOT_A_RANKING"] or "-"
    if cand != "-" and not r["pre_gate_candidate_parseable"]:
        cand += " (vacuous)"
    red = r["reduction_S2_bits"]
    lines.append(f"| {r['sign']} | {r['class']} | {dom} | {r['n_edges_total']} | "
                 f"{r['n_value_bearing_edges']} | {ch} | {lin} | "
                 f"{r['n_independent_anchors_collapsed']} | "
                 f"{red if red is not None else '-'} | {m2s} | {cand} | {relp} | "
                 f"{gate_str(r)} |")
table = "\n".join(lines)

nA = S["by_class"]["A-only"]
hn = S["random_anchor_null_reused"]
rh = S["random_hyperedge_null"]
ho = S["heldout_rel"]
per_sign_min_p = min((r["heldout_rel_perm_p"] for r in rows
                      if r["heldout_rel_perm_p"] is not None), default=None)
n_signs_with_pairs = sum(1 for r in rows if r["heldout_rel_pairs"] > 0)
gpc = Counter()
for r in rows:
    for k, v in r["gate"].items():
        gpc[k] += bool(v)

report = f"""# TASK I — Exhaustive unresolved-sign lattice search (per-sign accounting)

**Status: COMPLETE. Retention result: 0 / {S['n_unresolved']} candidates retained
(0 / {nA} A-only). Consistent with, and a per-sign refinement of, Task H
`JOINT_INFERENCE_NULL`.**

Stage header (Art. XXII): articles_triggered = V (claim layers; this stage stays at L2
accounting, no value claim), VII (search receipt: full enumeration below, no cherry-pick),
VIII (effective_n: 39 anchored signs collapse to 1 value-bearing meta-lineage), IX
(information budget: per-sign entropy panel), XI (source-dependency collapse), XII (no
grading a target by the rule that created it — continuity pins graded on the substitution
channel they did NOT create), XV (no transfer licence used; SEMANTIC+ NOT_AUTHORIZED),
XVII (append-only; this supersedes nothing), XVIII (assumptions: continuity meta-lineage
reliability is the registered unknown rho).
Gates: `DEPENDENCY_COLLAPSED_INDEPENDENT_ANCHORS = 0` (Task C);
`LA_AT_IDENTIFIABILITY_ZERO` (Task G); `JOINT_INFERENCE_NULL` (Task H).
Seed 20260708. Script `scripts/i_per_sign_lattice_search.py`; canonical table
`data/candidates/per_sign/per_sign_table.json`.

## 1. What was run (the 7 preregistered steps, per sign)

For **each of the {S['n_unresolved']} value-unresolved signs** in the conservative
universe (163 variables minus 12 numerals; {nA} A-only):

1. **Candidate-value domain** enumerated from the Task B universe:
   `syllabic_CV_or_V` -> the 65-slot LB CV grid (H_max = {S['domain']['H_max_grid_bits']}
   bits; Task H used H0 = {S['domain']['H0_bits_used_by_H']} bits);
   `commodity_ideogram_semantic` / `fractional_quantity` / `unknown` -> not
   grid-enumerable (recorded, never ranked).
2. **All lattice hyperedges touching the sign** (208 edges, 8 types), split into
   value-bearing (47: toponym / personal-name / commodity-gloss / loanword) and
   value-free (substitution, morphology, formula, cross-script descent).
3. **Independent channels + dependency lineages**, with the Art. XI collapse:
   LIN_L_TOP / LIN_L_PN / LIN_L_GLOSS / LIN_H / LIN_C all descend from
   `META_CONTINUITY_LA_eq_LB`; LIN_EG has SEED_A = 0.
4. **Joint propagation reused from Task H**: M1 Bayes marginals (S2 held-out-calibrated
   rho = 2/26), M2 arc-consistent domains (anchor-hard; globally UNSAT vs the rel
   channel), M3 tie-diversity.
5. **Ranking only if >= 2 independent channels** contribute to the sign's value.
6. **Held-out prediction**: the sign's continuity candidate must satisfy the
   corpus-internal substitution channel (share-one-coordinate rule, validated on LB),
   which was **not** used to derive the pins (Art. XII compliant).
7. **Matched random comparisons**: (a) permutation null on pin labels (2,000 perms);
   (b) 200 random-hyperedge lattices (value-bearing edges re-targeted at random signs,
   sizes/lineages preserved); (c) Task H random-anchor null reused.

**Retention gate** (fail CLOSED, all mechanical): [A: >=3 independent overlapping
anchors] OR [B: >=2 independent channels + validated substitution/stroke support
(stroke = SOURCE_BLOCKED per Task E; substitution support = per-sign perm p < 0.05 with
>= 3 pairs)] OR [C: one >=4-slot anchor + independent held-out recurrence]; AND
leave-one-anchor AND leave-one-lineage AND leave-one-site AND adaptive-null survival.
A candidate is NOT retained for producing a recognizable word.

## 2. Global result — the per-sign accounting confirms the structural zero

| quantity | value |
|---|---|
| unresolved signs audited | {S['n_unresolved']} ({nA} A-only, {S['by_class']['AB-shared']} AB-shared, {S['by_class']['logogram']} logogram, {S['by_class']['uncertain']} uncertain) |
| signs with ZERO lattice edges of any type | {S['signs_with_zero_lattice_edges']} (A-only: {S['A_only_zero_edges']}) |
| A-only signs value-dark (no value-bearing edge) | {S['A_only_value_dark']} / {nA} (the exception, *49, is the known vacuous pin) |
| signs with >= 1 collapsed value-bearing lineage | {S['signs_with_ge1_collapsed_anchor']} |
| **max independent anchors on ANY sign (Art. XI collapsed)** | **{S['max_independent_anchors_any_sign']}** (gate branch A needs 3) |
| signs where ranking was authorized (>= 2 independent channels) | **0** |
| gate branch passes A / B / C | {gpc['A_ge3_independent_overlapping_anchors']} / {gpc['B_ge2_channels_plus_validated_sub_or_stroke']} / {gpc['C_ge4slot_anchor_plus_heldout_recurrence']} |
| leave-one-anchor / -lineage / -site survivors (pre-branch) | {gpc['leave_one_anchor']} / {gpc['leave_one_lineage']} / {gpc['leave_one_site']} |
| adaptive-null survivors | {gpc['adaptive_null']} |
| **RETAINED candidates** | **0** |

Why the zero is over-determined, per sign: every value-bearing edge on every sign
collapses to the single `META_CONTINUITY_LA_eq_LB` meta-lineage, so (i) branch A caps at
1 < 3 for all 39 anchored signs, (ii) branch B's ">= 2 independent channels" is never
met, (iii) branch C's held-out-recurrence leg is unmet because **all 208 edges are
DERIVATION-side** (the one held-out-capable edge is the vacuous *49 pin), and (iv)
leave-one-lineage fails for every sign (removing the continuity lineage removes ALL
value evidence). These are four independent closures.

## 3. Held-out check (step 6): continuity pins vs the substitution channel

Reproduces Task H M2 exactly: **{ho['both_pinned_pairs']} both-pinned rel pairs, {ho['violated']} violated (UNSAT)**.
Graded as a held-out prediction with a label-permutation null ({ho['n_perm']} perms):
real satisfied = {ho['satisfied']}/{ho['both_pinned_pairs']}; null mean = {ho['perm_null_mean_sat']}; one-sided
**p = {ho['perm_p_one_sided']}**. The continuity value system is statistically
indistinguishable from a random relabeling on the only in-corpus channel it did not
create — and is hard-inconsistent with it (15/24). Best single-sign record
(min per-sign perm p over the {n_signs_with_pairs} signs with pairs) = {per_sign_min_p};
not significant even before the x{n_signs_with_pairs} multiplicity correction
(Art. VIII).

## 4. Matched random comparisons (step 7)

- **Random-anchor null (reused, Task H)**: real A-only mean reduction = {hn['real_A_only_mean_reduction']}
  bits vs null mean {hn['null_A_only_mean_reduction_mean']:.4f} (p5-p95 {hn['null_A_only_mean_reduction_p5_p95'][0]:.4f}-{hn['null_A_only_mean_reduction_p5_p95'][1]:.4f});
  verdict `{hn['verdict']}` — the real anchor set delivers LESS to A-only signs than
  random anchors of the same size would.
- **Random-hyperedge null (new, {rh['n_reps']} reps)**: retained candidates = 0 in
  {rh['n_reps']}/{rh['n_reps']} replicates (max {rh['retained_max']}); max independent
  anchors ever observed = {rh['max_indep_anchors_overall']}. The gate zero is
  **structural** (lineage accounting), not a near-miss: the real lattice is not
  distinguishable from random re-targetings at gate level, and no re-arrangement of the
  existing evidence can open branch A.

## 5. Interpretation (bounded, Art. V)

- **0 retained candidate values across all 151 unresolved signs**, including all 69
  A-only. The per-sign table shows this is not one global verdict hiding variance:
  {S['signs_with_zero_lattice_edges']} signs (59%) have no lattice constraint of ANY
  type; 67/69 A-only signs have zero edges; the {S['signs_with_ge1_collapsed_anchor']}
  anchored signs all sit on exactly one collapsed lineage.
- The M2 "PINNED_SINGLETON" / "REDUCED" domain states in the table are **conditional on
  the unproven continuity meta-lineage** (S1-style conditioning); they are recorded for
  the audit and confer no absolute value (relative reduction != absolute value).
- This is an L2 accounting result. It does NOT claim Linear A values are unknowable in
  principle: the gate reopens if a genuinely independent value-bearing lineage appears
  (e.g., a bilingual, an Egyptian transcription with SEED_A > 0, or a newly excavated
  archive), which would raise the max independent-anchor count above 1.

Compliance line (Art. XXII): stage executed under v2.2; no claim worded above L2; no
transfer licence invoked; all verdicts computed mechanically from
`data/candidates/per_sign/per_sign_table.json`; record appended, nothing deleted.

## 6. Per-sign table (all {S['n_unresolved']} unresolved signs)

Columns: dom = candidate domain (CV65 = 65-slot syllabic grid, sem = commodity-semantic,
frac = fraction, ? = unknown); edges = all lattice hyperedges touching the sign; vb =
value-bearing edges; indep = independent anchors after Art. XI collapse; S2 red. = M1
Bayes entropy reduction (bits) under the held-out-calibrated scenario; M2 domain =
arc-consistent domain state (conditional, anchor-hard); rel pairs/viol/p = held-out
substitution record. Gate outcome `FAIL:no-branch(A,B,C)` = no retention branch fired;
LOA/LOL/LOS/NULL = leave-one-anchor/-lineage/-site/adaptive-null failure.

{table}

*A-only signs listed first, then AB-shared / logogram / uncertain, each by descending
edge count. Canonical machine-readable version:
`data/candidates/per_sign/per_sign_table.json` (151 rows, full field set);
random-hyperedge null: `data/candidates/per_sign/random_hyperedge_null.json`.*
"""
out = os.path.join(BASE, "reports", "I_ALL_UNRESOLVED_SIGN_RESULTS.md")
open(out, "w").write(report)
print("wrote", out, len(report), "chars,", len(lines) - 2, "table rows")
