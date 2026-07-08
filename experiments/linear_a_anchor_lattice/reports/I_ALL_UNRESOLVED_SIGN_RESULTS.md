# TASK I — Exhaustive unresolved-sign lattice search (per-sign accounting)

**Status: COMPLETE. Retention result: 0 / 151 candidates retained
(0 / 69 A-only). Consistent with, and a per-sign refinement of, Task H
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

For **each of the 151 value-unresolved signs** in the conservative
universe (163 variables minus 12 numerals; 69 A-only):

1. **Candidate-value domain** enumerated from the Task B universe:
   `syllabic_CV_or_V` -> the 65-slot LB CV grid (H_max = 6.0224
   bits; Task H used H0 = 6.0661 bits);
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
| unresolved signs audited | 151 (69 A-only, 59 AB-shared, 20 logogram, 3 uncertain) |
| signs with ZERO lattice edges of any type | 89 (A-only: 67) |
| A-only signs value-dark (no value-bearing edge) | 68 / 69 (the exception, *49, is the known vacuous pin) |
| signs with >= 1 collapsed value-bearing lineage | 39 |
| **max independent anchors on ANY sign (Art. XI collapsed)** | **1** (gate branch A needs 3) |
| signs where ranking was authorized (>= 2 independent channels) | **0** |
| gate branch passes A / B / C | 0 / 0 / 0 |
| leave-one-anchor / -lineage / -site survivors (pre-branch) | 33 / 0 / 10 |
| adaptive-null survivors | 0 |
| **RETAINED candidates** | **0** |

Why the zero is over-determined, per sign: every value-bearing edge on every sign
collapses to the single `META_CONTINUITY_LA_eq_LB` meta-lineage, so (i) branch A caps at
1 < 3 for all 39 anchored signs, (ii) branch B's ">= 2 independent channels" is never
met, (iii) branch C's held-out-recurrence leg is unmet because **all 208 edges are
DERIVATION-side** (the one held-out-capable edge is the vacuous *49 pin), and (iv)
leave-one-lineage fails for every sign (removing the continuity lineage removes ALL
value evidence). These are four independent closures.

## 3. Held-out check (step 6): continuity pins vs the substitution channel

Reproduces Task H M2 exactly: **24 both-pinned rel pairs, 15 violated (UNSAT)**.
Graded as a held-out prediction with a label-permutation null (2000 perms):
real satisfied = 9/24; null mean = 7.29; one-sided
**p = 0.2794**. The continuity value system is statistically
indistinguishable from a random relabeling on the only in-corpus channel it did not
create — and is hard-inconsistent with it (15/24). Best single-sign record
(min per-sign perm p over the 24 signs with pairs) = 0.0855;
not significant even before the x24 multiplicity correction
(Art. VIII).

## 4. Matched random comparisons (step 7)

- **Random-anchor null (reused, Task H)**: real A-only mean reduction = 0.0
  bits vs null mean 0.0316 (p5-p95 0.0228-0.0381);
  verdict `REAL_BELOW_NULL` — the real anchor set delivers LESS to A-only signs than
  random anchors of the same size would.
- **Random-hyperedge null (new, 200 reps)**: retained candidates = 0 in
  200/200 replicates (max 0); max independent
  anchors ever observed = 2. The gate zero is
  **structural** (lineage accounting), not a near-miss: the real lattice is not
  distinguishable from random re-targetings at gate level, and no re-arrangement of the
  existing evidence can open branch A.

## 5. Interpretation (bounded, Art. V)

- **0 retained candidate values across all 151 unresolved signs**, including all 69
  A-only. The per-sign table shows this is not one global verdict hiding variance:
  89 signs (59%) have no lattice constraint of ANY
  type; 67/69 A-only signs have zero edges; the 39
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

## 6. Per-sign table (all 151 unresolved signs)

Columns: dom = candidate domain (CV65 = 65-slot syllabic grid, sem = commodity-semantic,
frac = fraction, ? = unknown); edges = all lattice hyperedges touching the sign; vb =
value-bearing edges; indep = independent anchors after Art. XI collapse; S2 red. = M1
Bayes entropy reduction (bits) under the held-out-calibrated scenario; M2 domain =
arc-consistent domain state (conditional, anchor-hard); rel pairs/viol/p = held-out
substitution record. Gate outcome `FAIL:no-branch(A,B,C)` = no retention branch fired;
LOA/LOL/LOS/NULL = leave-one-anchor/-lineage/-site/adaptive-null failure.

| sign | class | dom | edges | vb | channels | lineages(collapsed,vb) | indep | S2 red. (bits) | M2 domain | best cand (pre-gate) | rel pairs/viol/p | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| *324 | A-only | CV65 | 2 | 0 | substitution | - | 0 | 0.0 | REDUCED:18 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *49 | A-only | CV65 | 1 | 1 | L | META_CONT | 1 | 0.0 | FULL:65 | *49 (vacuous) | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *118 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *131 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *164 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *188 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *28 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *301 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *304 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *305 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *306 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *307 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *308 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *309 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *310 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *312 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *314 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *316 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *317 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *321 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *322 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *323 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *325 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *327 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *328 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *329 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *330 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *331 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *333 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *339 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *34 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *341 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *342 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *345 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *348 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *349 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *350 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *352 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *353 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *354 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *355 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *358 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *361 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *362 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *363 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *401 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *402 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *403 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *404 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *405 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *406 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *406VAS | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *408 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *409 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *410 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *411 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *412 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *413 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *414 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *415 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *416 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *417 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *418 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *47 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *516 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *560 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *82 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *86 | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| *OLIV | A-only | CV65 | 0 | 0 | - | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| A | AB-shared | CV65 | 24 | 9 | C,H,L,formula,morphology,substitution | META_CONT | 1 | 0.1487 | PINNED_SINGLETON | A | 5/2/0.1694 | FAIL:no-branch(A,B,C)+LOL+NULL |
| RU | AB-shared | CV65 | 17 | 8 | H,L,morphology,substitution | META_CONT | 1 | 0.1312 | PINNED_SINGLETON | RU | 3/3/1.0 | FAIL:no-branch(A,B,C)+LOL+NULL |
| DA | AB-shared | CV65 | 16 | 6 | C,H,L,morphology,substitution | META_CONT | 1 | 0.1363 | PINNED_SINGLETON | DA | 3/2/0.6597 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| TA | AB-shared | CV65 | 16 | 7 | H,L,morphology,substitution | META_CONT | 1 | 0.1316 | PINNED_SINGLETON | TA | 2/1/0.5122 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| I | AB-shared | CV65 | 15 | 8 | C,H,L,morphology,substitution | META_CONT | 1 | 0.1626 | PINNED_SINGLETON | I | 2/0/0.0855 | FAIL:no-branch(A,B,C)+LOL+NULL |
| JA | AB-shared | CV65 | 14 | 5 | H,L,morphology,substitution | META_CONT | 1 | 0.1502 | PINNED_SINGLETON | JA | 3/1/0.2259 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| KI | AB-shared | CV65 | 14 | 8 | H,L,formula,morphology,substitution | META_CONT | 1 | 0.1469 | PINNED_SINGLETON | KI | 1/1/1.0 | FAIL:no-branch(A,B,C)+LOL+NULL |
| KU | AB-shared | CV65 | 13 | 6 | H,L,formula,substitution | META_CONT | 1 | 0.1265 | PINNED_SINGLETON | KU | 2/2/1.0 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| RA | AB-shared | CV65 | 13 | 4 | H,L,morphology,substitution | META_CONT | 1 | 0.1524 | PINNED_SINGLETON | RA | 3/1/0.2359 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| SA | AB-shared | CV65 | 13 | 8 | C,H,L,substitution | META_CONT | 1 | 0.1304 | PINNED_SINGLETON | SA | 1/1/1.0 | FAIL:no-branch(A,B,C)+LOL+NULL |
| SI | AB-shared | CV65 | 11 | 4 | H,L,morphology,substitution | META_CONT | 1 | 0.1291 | PINNED_SINGLETON | SI | 2/1/0.5177 | FAIL:no-branch(A,B,C)+LOL+NULL |
| TE | AB-shared | CV65 | 11 | 2 | H,L,morphology,substitution | META_CONT | 1 | 0.1246 | PINNED_SINGLETON | TE | 3/2/0.6577 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| WA | AB-shared | CV65 | 11 | 2 | H,L,morphology,substitution | META_CONT | 1 | 0.1312 | PINNED_SINGLETON | WA | 3/2/0.6577 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| NA | AB-shared | CV65 | 10 | 5 | C,H,L,morphology,substitution | META_CONT | 1 | 0.1518 | PINNED_SINGLETON | NA | - | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| RE | AB-shared | CV65 | 10 | 5 | H,L,morphology,substitution | META_CONT | 1 | 0.138 | PINNED_SINGLETON | RE | 1/0/0.3123 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| TI | AB-shared | CV65 | 10 | 3 | C,H,L,morphology,substitution | META_CONT | 1 | 0.1157 | PINNED_SINGLETON | TI | 2/1/0.5267 | FAIL:no-branch(A,B,C)+LOL+NULL |
| KA | AB-shared | CV65 | 9 | 2 | H,L,morphology,substitution | META_CONT | 1 | 0.1333 | PINNED_SINGLETON | KA | 2/1/0.5222 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| PA | AB-shared | CV65 | 9 | 4 | C,H,L,substitution | META_CONT | 1 | 0.1396 | PINNED_SINGLETON | PA | 1/1/1.0 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| QE | AB-shared | CV65 | 8 | 0 | H,morphology,substitution | - | 0 | 0.0005 | REDUCED:5 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| RO | AB-shared | CV65 | 8 | 2 | C,H,L,formula,morphology,substitution | META_CONT | 1 | 0.1404 | PINNED_SINGLETON | RO | 1/1/1.0 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| MA | AB-shared | CV65 | 7 | 2 | H,L,morphology,substitution | META_CONT | 1 | 0.1212 | PINNED_SINGLETON | MA | 1/1/1.0 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| MI | AB-shared | CV65 | 7 | 3 | H,L,substitution | META_CONT | 1 | 0.1239 | PINNED_SINGLETON | MI | 1/1/1.0 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| RI | AB-shared | CV65 | 7 | 5 | H,L,morphology | META_CONT | 1 | 0.1416 | PINNED_SINGLETON | RI | - | FAIL:no-branch(A,B,C)+LOL+NULL |
| SU | AB-shared | CV65 | 7 | 4 | H,L,substitution | META_CONT | 1 | 0.1286 | PINNED_SINGLETON | SU | 1/1/1.0 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| TO | AB-shared | CV65 | 7 | 4 | C,H,L,formula | META_CONT | 1 | 0.1485 | PINNED_SINGLETON | TO | - | FAIL:no-branch(A,B,C)+LOL+NULL |
| U | AB-shared | CV65 | 7 | 2 | H,L,substitution | META_CONT | 1 | 0.1337 | PINNED_SINGLETON | U | 2/2/1.0 | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| DI | AB-shared | CV65 | 6 | 5 | H,L | META_CONT | 1 | 0.1362 | PINNED_SINGLETON | DI | - | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| NI | AB-shared | CV65 | 6 | 5 | H,L | META_CONT | 1 | 0.1467 | PINNED_SINGLETON | NI | - | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| PI | AB-shared | CV65 | 6 | 1 | H,L,substitution | META_CONT | 1 | 0.1344 | PINNED_SINGLETON | PI | 2/1/0.5072 | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| TU | AB-shared | CV65 | 6 | 3 | H,L,substitution | META_CONT | 1 | 0.1432 | PINNED_SINGLETON | TU | - | FAIL:no-branch(A,B,C)+LOL+NULL |
| NE | AB-shared | CV65 | 5 | 1 | H,L,morphology,substitution | META_CONT | 1 | 0.1358 | PINNED_SINGLETON | NE | 1/1/1.0 | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| NU | AB-shared | CV65 | 5 | 2 | H,L,substitution | META_CONT | 1 | 0.1353 | PINNED_SINGLETON | NU | - | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| SE | AB-shared | CV65 | 5 | 2 | C,H,L,morphology | META_CONT | 1 | 0.1184 | PINNED_SINGLETON | SE | - | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| RA2 | AB-shared | CV65 | 4 | 3 | H,L | META_CONT | 1 | 0.1517 | PINNED_SINGLETON | RA2 | - | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| DU | AB-shared | CV65 | 3 | 2 | H,L | META_CONT | 1 | 0.1132 | PINNED_SINGLETON | DU | - | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| PO | AB-shared | CV65 | 3 | 0 | C,H,formula | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| QA | AB-shared | CV65 | 3 | 2 | H,L | META_CONT | 1 | 0.1165 | PINNED_SINGLETON | QA | - | FAIL:no-branch(A,B,C)+LOL+LOS+NULL |
| WI | AB-shared | CV65 | 3 | 0 | H,substitution | - | 0 | 0.0012 | REDUCED:18 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| ZU | AB-shared | CV65 | 3 | 1 | L,substitution | META_CONT | 1 | 0.1382 | PINNED_SINGLETON | ZU | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| DE | AB-shared | CV65 | 2 | 1 | H,L | META_CONT | 1 | 0.1359 | PINNED_SINGLETON | DE | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| ME | AB-shared | CV65 | 2 | 0 | H,morphology | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| PA3 | AB-shared | CV65 | 2 | 0 | substitution | - | 0 | 0.0018 | REDUCED:18 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| PU2 | AB-shared | CV65 | 2 | 1 | H,L | META_CONT | 1 | 0.1265 | PINNED_SINGLETON | PU2 | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| AU | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| E | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| JE | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| JU | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| KE | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| KO | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| MU | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| NWA | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| O | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| PU | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| QI | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| TA2 | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| TWE | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| ZA | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| ZE | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| ZO | AB-shared | CV65 | 1 | 0 | H | - | 0 | 0.0 | FULL:65 | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:*21F | logogram | sem | 2 | 0 | substitution | - | 0 | 0.0014 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:*21M | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:*22F | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:*22M | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:*23M | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:AROM | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:CAP | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:CAPm | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:CYP | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:GAL | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:GRA | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:HIDE | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:OLE | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:OLIV | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:TELA | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:VAS | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:VIN | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:VINb | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:VIR | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| LOGO:VS | logogram | sem | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| PUA:0xfd1eb | uncertain | ? | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| QA2 | uncertain | ? | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |
| __DATA_ERROR__ | uncertain | ? | 0 | 0 | - | - | 0 | 0.0 | FULL | - | - | FAIL:no-branch(A,B,C)+LOA+LOL+LOS+NULL |

*A-only signs listed first, then AB-shared / logogram / uncertain, each by descending
edge count. Canonical machine-readable version:
`data/candidates/per_sign/per_sign_table.json` (151 rows, full field set);
random-hyperedge null: `data/candidates/per_sign/random_hyperedge_null.json`.*
