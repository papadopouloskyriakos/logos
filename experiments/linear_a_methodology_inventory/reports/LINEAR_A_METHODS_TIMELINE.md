# Linear A methods — chronological timeline

Dates from commit history; verdicts from each campaign's authoritative CAMPAIGN.md/DECISION_LOG/TASK_LEDGER.

| when | campaign (branch@HEAD) | methods introduced | result |
|---|---|---|---|
| ≤2026-07-01 | **paper / core platform** (main→github/main 7c509c6) | morphology, stratified morphology, LB morphology control, segmentation, metrology, distributional phonology pilot, cross-script A↔B distributional + palaeo image leg, LLM-ablation (C.4/gate-2), L_virgin/L_not_indexed, decontamination, L_fake canary, litindex, gate null calibration, information floor, Tamburini CSA repro, Ugaritic→Hebrew heuristic | morphology NULL / segmentation STRUCTURAL_ONLY / metrology NULL / cross-script NULL + image CIRCULAR / instruments SUPPORTED; **submitted TACL #11385 + Zenodo, byte-frozen** |
| 2026-07-02 | crossscript_gate one-shots (prereg, DOIs 21168887/21173639) | LOTO cross-script anchor gate | REFUTE_LOTO_FRAGILE / REFUTE (distributional channel 0, 3rd–4th null) |
| ~2026-07-03..06 | **admin-schema → no-human → observable** (dd98f1a/946e53e/71eb0e6) | blinded LB role/schema induction, weak-supervision, source-label route, masked-logogram, masked-quantity, observable-channel gate | schema EXPLORATORY 29.2% (not gate-validated); source-label NO_POWER; L2 doc-structure SUPPORTED; L3 channel + masked-logogram/quantity REFUTED |
| ~2026-07-06 | **external-anchors → LA-LB continuity → ritual** (3310e4b/87b4dea/e6ee2b4) | toponym/name anchors, toponym continuity, ritual feasibility | mostly circular / NULL_PUBLISHED / NO_POWER |
| 2026-07-06 | **egyptian calibration** (dfa291e) | Egyptian phonetic-anchor channel, Cretan one-shot | mechanical CONFIRM_GENERALIZES but honest TRIVIAL/NULL (effective-n≈1); programme CLOSED |
| 2026-07-07 | **12h campaign** (main linear_a_campaign) | T1–T5 incl. KU-RO positive control | UNDERDETERMINED; KU-RO 17× p=0.0005 but cross-site NO_POWER; "259 params>212" (later invalidated) |
| 2026-07-07 | **constraint-expansion** (2996567) | Stages A–L; cleaned inventory; relabeling-invariance | NEW_CONSTRAINTS_BUT_NO_DECIPHERMENT; **259→92 (category error corrected)**; value-blindness "theorem" (later refuted) |
| 2026-07-07 | **foundry** (09f7ef9) | WP1–8 + synthetic labs + seals; position→C/V, substitution graph, reduced-seed, power curves, candidate rounds | NEW_CONSTRAINTS_AND_A_SHARPER_OBSTACLE; value-blindness theorem "refuted"; 6 families AT_END_TO_END_NULL |
| 2026-07-08 | **relative-phonology / seals** (8a98607) | WPs A–M: replication+multiplicity audit, C_AUDIT, seed audit, morphology, seals, adaptive null | **position→C/V REFUTED + reduced-seed REFUTED** (frequency artifacts); substitution validated-on-LB/not-on-LA; A- prefixation + formula grammars adaptive-validated; NEW_CONSTRAINTS_BUT_NO_DECIPHERMENT |
| 2026-07-08 | **Di Mino *301 exact audit** (1cd3f86) | exact mechanical gate: value sweep, root/gloss nulls, morphology, cross-site, formula, PC1–6, end-to-end null | **DI_MINO_CORE_VERDICT=REJECT**; PC PASS (calibrated); end-to-end FP=1.0; H7–H12 SOURCE_BLOCKED |
| 2026-07-08 | **this audit** (audit/…master-inventory) | repository-forensics methodology inventory | 214 instances catalogued; 14 lineages; 48 contradictions; 0 unmapped-needing-review |

**Two self-corrections stand out** (the discipline catching itself): the foundry's position→C/V and reduced-seed
"openings" were both refuted as frequency artifacts by the relative-phonology campaign's own multiplicity +
independent-replication audits; and constraint-expansion's 259-parameter identifiability headline was invalidated
as a category error by its own cleaned inventory (V=92).
