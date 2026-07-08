# LOGOS Linear A — Master Methodology Inventory

**Audit branch** `audit/linear-a-methodology-master-inventory` (from `main@6fd4f20`, read-only). **Date** 2026-07-08.
Basis: 13 refs, 12 worktrees, 1 tag, **923 artifacts** (`data/ARTIFACT_INDEX.csv`), **214 method instances**
(`data/METHOD_INSTANCES.{json,csv}`), **14 lineages** (`data/METHOD_LINEAGES.{json,csv}`), **48 contradictions**
(`data/STATUS_CONTRADICTIONS.csv`). No experiments run; no prior verdict or paper artifact changed.

---

## 1. Executive totals & highest earned claim layer

**214 concrete method instances** across 12 campaigns + shared foundations + the paper.

| implementation_status | n | | scientific_outcome | n |
|---|---|---|---|---|
| RUN_CONFIRMATORY | 92 | | SUPPORTED | 37 |
| RUN_EXPLORATORY | 42 | | STRUCTURAL_ONLY | 33 |
| RUN_PREREGISTERED | 33 | | NOT_APPLICABLE (infra/audit) | 27 |
| REPRODUCED | 11 | | NULL | 26 |
| DESIGNED_NOT_RUN | 9 | | REFUTED | 18 |
| PROPOSED_ONLY | 7 | | INCOMPLETE | 16 |
| SOURCE_BLOCKED | 7 | | NO_POWER | 13 |
| PARTIALLY_IMPLEMENTED | 5 | | NULL_PUBLISHED | 13 |
| POWER_GATED_BEFORE_RUN | 3 | | PARTIAL_SUPPORT | 10 |
| SUPERSEDED | 3 | | UNDERDETERMINED | 8 |
| COMPUTE_BLOCKED / INVALIDATED | 1 / 1 | | TRIVIAL_RECOVERY / NO_VERDICT / CIRCULAR | 5 / 5 / 2 |

**Highest earned claim layer on Linear A: L2/L3 (structural / administrative-functional), held-out- and
adaptive-null-validated.** Across all 214 instances and 12 campaigns, **zero earned a phonetic (L6), lexical (L5),
semantic (L4), or language-identification (L8) licence on Linear A; every transfer licence is NOT_EARNED.** The 37
`SUPPORTED` are almost entirely (a) **discipline-instrument validations** (L_fake canary, gate calibration,
opaque-Linear-B and Ugaritic↔Hebrew positive controls), (b) **L2/L3 structural results** (document
templates/closure; A- prefixation; the KU-RO-terminal and libation formula grammars), and (c) one *honestly
downgraded* mechanical "CONFIRM" (Egyptian, effective-n≈1 → TRIVIAL). **No `SUPPORTED` is a Linear A reading.**

**The single most load-bearing output of the whole programme is a rigorously-mapped null plus a *working
false-decipherment detector*** — the same machinery, run on the June-2026 Di Mino `*301=/na/` claim, returned a
mechanical `REJECT` on a pipeline proven to recover real and planted truth.

## 2. Chronological campaign history

1. **Paper / core platform (main, →`7c509c6` submission).** Built the discipline machinery and ran the core
   probes: morphology (NULL, no power vs L_fake floor 0.375; LB control HAS power 0.5625), segmentation
   (STRUCTURAL_ONLY, micro-F1 0.436, gap CI excludes 0), metrology (NULL, p=1.0, only J=½=Bennett), distributional
   phonology (data-limited NULL), cross-script A↔B distributional (NULL 0.020 vs 0.0145) + image leg (withdrawn as
   CIRCULAR), LLM-ablation public-exposure gradient, L_not_indexed abstention, gate calibration (0.6% false
   graduation), CSA sufficiency sweep. **Submitted TACL #11385 + Zenodo; byte-frozen.**
2. **12h "crack LA" campaign (main, `linear_a_campaign`).** UNDERDETERMINED; KU-RO positive control FIRES (17×,
   p=0.0005) but Haghia-Triada-locked → cross-site NO_POWER. Headline "259 params > 212 constraints".
3. **Constraint-expansion (`2996567`).** NEW_CONSTRAINTS_BUT_NO_DECIPHERMENT; **corrected 259→92** (category
   error); L2 highest; internal-value-blindness "theorem" asserted (later itself refuted).
4. **Foundry (`09f7ef9`).** NEW_CONSTRAINTS_AND_A_SHARPER_OBSTACLE; refuted the value-blindness *theorem* via
   position→C/V (AUC 0.744/0.835) + reduced-seed 0.87 + substitution-on-LB; 6 candidate families AT_END_TO_END_NULL.
5. **Relative-phonology / seals (`8a98607`).** NEW_CONSTRAINTS_BUT_NO_DECIPHERMENT — audited the foundry to the
   bone: **position→C/V REFUTED (frequency artifact), reduced-seed REFUTED (frequency artifact)**; substitution
   validated-on-LB / not-recoverable-on-LA; L2/L3 positives (A- prefixation, formula grammars) adaptive-null-validated.
6. **Di Mino `*301` exact audit (`1cd3f86`).** DI_MINO_CORE_VERDICT=REJECT (the missing mechanical gate).
7. **Sibling programmes:** admin-schema / no-human-structure / observable-channels (L2 SUPPORTED, L3 REFUTED,
   source-label NO_POWER); external-anchors / LA-LB continuity / LA-LB ritual (mostly circular / NO_POWER /
   NULL_PUBLISHED); Egyptian calibration (mechanical CONFIRM but honest TRIVIAL, effective-n≈1); tamburini CSA repro.

## 3. Catalogue by lineage & instance
Full per-instance records: `data/METHOD_INSTANCES.{json,csv}` (214 rows, all canonical fields). The 14 collapsed
**lineages** (`data/METHOD_LINEAGES.json`, `reports/LINEAR_A_METHODS_LINEAGE_MAP.md`) are the authoritative
de-duplicated view: LIN-01 distributional C/V · LIN-02 segmentation · LIN-03 substitution channel · LIN-04
reduced-seed propagation · LIN-05 value-blindness/identifiability · LIN-06 parameter/constraint count · LIN-07
morphology · LIN-08 cross-script transfer · LIN-09 admin/formula structure · LIN-10 external anchors/candidate
languages · LIN-11 Egyptian calibration · LIN-12 Di Mino `*301` · LIN-13 metrology/accounting · LIN-14
falsification instruments.

## 4. Result matrix
`reports/LINEAR_A_METHODS_RESULT_MATRIX.md` (+ `reports/_result_matrix_rows.csv`): per instance — question, data,
held-out design, null, outcome, verdict, power, claim layer, authoritative artifact. Load-bearing numbers with
verification class in `data/RESULT_NUMBERS.csv`.

## 5. What has genuinely been learned

- **Observations (L0–L1):** corpus is 1,341 inscriptions / 5,792 syllable-signs / V≈92 conservative; 53.9%
  single-sign, 63% Haghia Triada, 83.8% hapax among multi-sign words; `load_a()` packs 539 inscriptions vs 3,147
  GORILA word units (a text-unit finding that changed later analyses).
- **Structural / functional (L2/L3, earned):** segmentation carries a real but modest boundary signal (0.436,
  gap CI excludes 0), driven by physical/administrative layout not distribution; **document structure
  (templates/closure) SUPPORTED**; **A- prefixation** genuine (adaptive-null p 0.008); **formula grammars** —
  KU-RO terminal-TOTAL (arithmetic sum-consistency) + libation rigid order (p 5e-5) — held-out validated. No
  phonetic licence attaches to any of these.
- **Relative phonology (RELATIVE_PHONOLOGY_ONLY, on the analogue only):** internal substitution structure
  *genuinely* breaks the C/V symmetry **on opaque Linear B** (consonant-held axis, twice-audited) — so internal
  methods are **not universally value-blind** — **but Linear A does not exhibit the exploitable axis** (underpowered
  + word-initial typology).
- **Failed phonetic / language hypotheses:** position→C/V (frequency artifact); reduced-seed 0.87 (frequency
  artifact + design leak); cross-script value transfer (≥4 independent distributional nulls); 6 candidate families
  + isolate (AT_END_TO_END_NULL); Egyptian channel (TRIVIAL, effective-n≈1); Di Mino `*301=/na/→N-W-Y→dwell→Semitic`
  (REJECT; end-to-end FP=1.0); external anchors (SEED_A=0, mostly circular/one-toponym-deep).
- **The identifiability floor, correctly stated:** the LA value layer is **underdetermined by the available
  monolingual evidence** (0 selection-exploitable bits under relabeling; ≥10²⁷ relabeling-equivalent value
  systems) — **not** a proof of impossibility. Only a bilingual or ≥3 independent held-out anchors, or a
  substantially larger/longer corpus for the relative channels, can move it.
- **The discipline works:** L_fake canary holds at every ε; the gate false-graduates at 0.6%; opaque-LB and
  Ugaritic↔Hebrew positive controls recover truth; the Di Mino REJECT + PC-PASS proves the machinery rejects a
  real-world false claim without rejecting truth. **This is the platform's primary deliverable.**

## 6. What has genuinely never been tried
See `reports/OPEN_AND_UNTESTED_METHODS.md`. Headline gaps: no bilingual/joint-decipherment against a *newly
ingested* held-out edition (Anetaki II delta seal is registered but unpublished); no palaeographic **stroke-corpus**
cross-script channel (unpopulated — the one non-circular shape channel never built); no 3D/seal-imaging channel; no
prospective test scored against a genuinely-late inscription; the 408-lexicon / 40-sign-map / LB-correction gates
are `SOURCE_BLOCKED` (artifacts withheld), not run.

## 7. Unresolved contradictions & missing artifacts
`reports/METHODOLOGY_STATUS_RECONCILIATION.md` + `data/STATUS_CONTRADICTIONS.csv` (48). The material ones:
- **CSA sufficiency clamps in the *frozen submitted paper*** — the "curve splits the branches at the LA-scale
  locator" sentence rests on 600–700-word cells that were never measured (endpoint clamps); Exit-B flags an
  **invariant-12 (generated-counts) break in the deposited paper** → would be an ERRATUM (paper byte-frozen, not
  editable here).
- **259 vs 92 parameters** — the paper/12h headline vs the cleaned inventory (superseded, category error).
- **Frozen-paper corpus anchors** (650 vs 1021 words recompute) — definitional gap, ERRATUM-class.
- **Palaeo image leg** — commit `5e82576` "IMAGE alignment SUCCEEDS" vs the settled CIRCULAR withdrawal.
- **Stale STATUS files** across ~5 parked branches (scaffold/"not yet issued"/"READY" headers on CLOSED campaigns).
- **Egyptian mechanical-CONFIRM vs honest-TRIVIAL** (effective-n≈1) — mechanical verdict and honest interpretation
  diverge (correctly disclosed, but a naive reader would misread).
All preserved in-timeline; none silently resolved. **UNMAPPED_ARTIFACTS.csv = 288, all classified
(SUBSUMED/INHERITED), 0 NEEDS_REVIEW** — no method left uncatalogued.

## 8. Inputs available for the next campaign (not a plan)
- **Methods worth extending:** the substitution consonant-axis (validated on LB — the only internal channel that
  ever broke C/V non-circularly); A- prefixation + formula grammars (the only held-out-validated LA structure);
  the L_fake/gate machinery (reuse as the honesty backstop, as Di Mino demonstrated).
- **Methods not worth repeating unchanged:** position→C/V, reduced-seed propagation, cross-script distributional
  transfer, unconstrained candidate-language/root search — all null/artifact under proper multiplicity.
- **Missing channels:** palaeographic stroke corpus; 3D/seal imaging; a genuine bilingual; a late held-out edition.
- **Unresolved signs / anchor lattice:** SEED_A=0 today; the value substrate is one circular toponym lineage —
  the binding need is ≥3 *independent* held-out anchors or a bilingual.
- **Held-out partitions & prospective seals ready:** the relative-phonology seals (SEAL_2/3/4 held-out-validated;
  SEAL_5 = Anetaki II delta, dated+hashed, awaiting the editio princeps) and the Di Mino frozen prereg.

**Bottom line:** 12 campaigns, 214 method instances, and the honest result is consistent and hard-won — **Linear A
remains undeciphered at every phonetic/lexical/semantic layer; the value layer is underdetermined by the available
monolingual evidence (not proven impossible); the durable positives are L2/L3 administrative structure and a
*validated false-decipherment gate*.** The programme's discipline held: two of its own headline "openings"
(position→C/V, reduced-seed) were caught and refuted by its own later audits, and a widely-circulated external
claim was mechanically rejected.
