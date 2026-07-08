# Linear A methods — lineage map (collapsed reruns + supersession)

14 lineages. A lineage collapses genuine reruns/corrections of one method into an origin→authoritative chain; unchanged reruns are not counted as novel. Full data: data/METHOD_LINEAGES.json.

## LIN-01 — Distributional C/V phonology (position→vowel/consonant)
- **Origin:** paper distributional-phonology pilot (data-limited NULL)
- **Trajectory:** foundry WP1/WP3.1 position→C/V AUC 0.744/0.835 ('symmetry broken, value layer reopened') → relative-phonology WP-A multiplicity+replication+oriented-null audit
- **Current authoritative:** relative-phonology WP-A: CV_ANALOGUE_REFUTED (frequency artifact; fails Bonferroni×13=0.455, 2 unsupervised models, 2-sided null p=0.146, freq-band-disjoint 0.481)
- **Obsolete/superseded:** foundry FND-02/03 position→C/V 'reopening' (SUPERSEDED)
- **Verdict evolution:** data-limited NULL → SUPPORTED(exploratory) → REFUTED
- **Why reruns:** multiplicity + independent-replication + honest-2-sided-null were missing in foundry

## LIN-02 — Segmentation (word-boundary induction)
- **Origin:** paper segmentation DP-unigram micro-F1 0.436 vs random 0.389 (gap CI excludes 0)
- **Trajectory:** segmentation_extension PYP 0.559 / BiLSTM 0.622 / morfessor worse-than-random → foundry WP2 packed→word 0.685→0.760 ('helps C/V') → relative-phonology B channel-dependent
- **Current authoritative:** relative-phonology B: SUPPORTED_ON_LB but C/V recovery is segmentation-INVARIANT; at LA hapax regime skill over cut-everywhere ~0 (over-cut superset); signal is layout not distribution
- **Obsolete/superseded:** foundry WP2 'segmentation cleanly helps C/V' framing (tensioned/superseded)
- **Verdict evolution:** STRUCTURAL_ONLY(positive gap) → 'helps' → channel-dependent, C/V-invariant
- **Why reruns:** foundry conflated coverage with C/V discrimination

## LIN-03 — Scribal-substitution relative channel
- **Origin:** foundry WP3.2 substitution graph validated on LB (z=7.07, AUC 0.71)
- **Trajectory:** relative-phonology C_AUDIT applies the WP-A battery to it
- **Current authoritative:** relative-phonology C_AUDIT: SUBSTITUTION_CONSONANT_AXIS_VALIDATED on LB (survives freq-band-disjoint + freq-matched null p=0.0033) but C4/C5 NOT_RECOVERED on LA (underpowered support 3 vs 98; word-INITIAL wrong signature)
- **Obsolete/superseded:** —
- **Verdict evolution:** validated-on-LB (foundry) → validated-on-LB + not-recoverable-on-LA (relative-phonology)
- **Why reruns:** the load-bearing surviving channel after position fell; needed its own hard audit

## LIN-04 — Reduced-seed C/V propagation
- **Origin:** foundry WP5 reduced-seed bootstrap 3-4 seeds→AUC 0.87 on LB
- **Trajectory:** relative-phonology D3 seed-propagation audit
- **Current authoritative:** relative-phonology D3: SEED_PROPAGATION_FREQUENCY_ARTIFACT (n=5 lucky sample, honest 0.784; kv=4 reveals 80% of 5-vowel key; pure-freq ranking 0.872>seed; clean-seed random null never run, non-sig here)
- **Obsolete/superseded:** foundry FND WP5 '3-4 seeds→0.87' (REFUTED)
- **Verdict evolution:** SUPPORTED(exploratory) → REFUTED (frequency artifact)
- **Why reruns:** design leak + missing random-seed null

## LIN-05 — Value-blindness / identifiability of the value layer
- **Origin:** 12h campaign + constraint-expansion 'internal distributional structure is sign-relabeling-invariant → value layer permanently closed'
- **Trajectory:** foundry WP1 audits the theorem → relative-phonology WP-A/H3 measure it directly
- **Current authoritative:** relative-phonology: internal methods NOT universally value-blind (substitution breaks C/V on LB) BUT Linear A specifically is relabeling-invariant/underdetermined (H3 0 bits; I1 ≥10^27 twins) — the measured middle
- **Obsolete/superseded:** constraint-expansion 'permanently closed' global theorem (SUPERSEDED by foundry WP1 as OVERSTATED); foundry 'position reopens it' (SUPERSEDED by WP-A: position was a frequency artifact)
- **Verdict evolution:** 'proven closed' → 'reopened via position' → 'not closed in general, but LA underdetermined by available evidence'
- **Why reruns:** both extremes were overstated; two corrections

## LIN-06 — Identifiability parameter/constraint count
- **Origin:** 12h campaign + paper headline: 259 sign-value params > 212 constraints
- **Trajectory:** constraint-expansion Stage A cleaned inventory
- **Current authoritative:** constraint-expansion: real conservative syllabary V=92 (count-FAVOURABLE, 92<212); the deficit is value-informativeness not count. '259' is a category error (incl. 108 ligatures+13 damage+logograms)
- **Obsolete/superseded:** 12h/paper '259 params' headline (INVALIDATED as category error)
- **Verdict evolution:** 'params>constraints (underdetermined by count)' → 'count favourable; value-informativeness is the real deficit'
- **Why reruns:** 259 conflated diplomatic-stream tokens with syllabogram inventory

## LIN-07 — Morphology / affix induction
- **Origin:** paper morphology pooled NULL (real 0.250 < L_fake bigram floor 0.375; no power) + LB positive control HAS power (0.5625)
- **Trajectory:** stratified morphology → foundry WP3.4 (whole-wordform-recurrence artifact) → relative-phonology E
- **Current authoritative:** relative-phonology E: A- prefixation genuine (adaptive-null p 0.008) + 2 formula grammars (KU-RO terminal / libation order); corrects 'A-/I-/-JA' to A- only; held-out-validated L3
- **Obsolete/superseded:** foundry 'A-/I-/-JA three affixes' (corrected to A- only)
- **Verdict evolution:** NULL(no power) → whole-wordform artifact → A- prefixation SUPPORTED at L3
- **Why reruns:** segmentation + adaptive null + cross-site controls added

## LIN-08 — Cross-script value transfer (A↔B distributional + image)
- **Origin:** paper A↔B distributional NULL (procrustes 0.020 vs 0.0145) + palaeo IMAGE leg (withdrawn as CIRCULAR shape-genealogy)
- **Trajectory:** crossscript_gate one-shots (REFUTE_LOTO_FRAGILE, DOIs 21168887/21173639) → foundry WP4 NULL → relative-phonology F decomposed NULL → external-anchors
- **Current authoritative:** relative-phonology F: NULL, decomposed — only admin_function non-circular+calibratable, =NULL; shape circular (≤0.75); 0/59 correspondences primary. 4th+ distributional null
- **Obsolete/superseded:** 5e82576 commit 'IMAGE alignment SUCCEEDS' (WITHDRAWN)
- **Verdict evolution:** NULL/circular → REFUTE_LOTO_FRAGILE → NULL (repeatedly confirmed)
- **Why reruns:** multiple independent implementations, all null

## LIN-09 — Administrative / formula structure recovery
- **Origin:** paper + admin_schema blinded LB role/schema induction (29.2% exact, not gate-validated)
- **Trajectory:** no_human_structure (source-label route NO_POWER) → observable_channels (L3 word-context→channel REFUTED; L2 doc-structure SUPPORTED, no licence) → relative-phonology E2
- **Current authoritative:** observable_channels + relative-phonology E2: L2 document structure (templates/closure, formula grammars) SUPPORTED but earns NO functional licence; L3 channel REFUTED
- **Obsolete/superseded:** —
- **Verdict evolution:** exploratory schema → NO_POWER (no-human) → L2 STRUCTURAL_ONLY / L3 REFUTED
- **Why reruns:** blinding + power gates + observable-channel reframing

## LIN-10 — External anchors / candidate languages
- **Origin:** external_anchors + toponym/name inventory (115 records)
- **Trajectory:** la_lb_continuity (toponym continuity split H_exact NULL_PUBLISHED / H_drift NO_POWER) → la_lb_ritual (NO_POWER) → egyptian calibration → foundry candidate rounds → relative-phonology G/H
- **Current authoritative:** relative-phonology G: SEED_A=0 (no independently-secure value seed; value substrate=one circular toponym lineage); H1-H3 candidate rounds all AT_END_TO_END_NULL (6 families+isolate); only bilingual/≥3 independent anchors can crack
- **Obsolete/superseded:** —
- **Verdict evolution:** anchor inventory → mostly circular/one-toponym-deep → SEED_A=0 + candidate NULL
- **Why reruns:** decontamination + Art. XII circularity gate + end-to-end null

## LIN-11 — Egyptian phonetic-anchor calibration
- **Origin:** egyptian-calibration-gate REQ-01
- **Trajectory:** Cretan one-shot pre-registered test
- **Current authoritative:** egyptian: mechanical CONFIRM_GENERALIZES but honest interpretation TRIVIAL/NULL (fair š~s baseline ties M2; edge = 1 training record, LOO flips; effective-n≈1); channel NOT confirmed; programme CLOSED
- **Obsolete/superseded:** STATUS.md 'READY_FOR_PREREG / first channel to pass its gate' (STALE)
- **Verdict evolution:** 'READY/passes gate' (stale) → mechanical CONFIRM but honest NULL/TRIVIAL (effective-n≈1)
- **Why reruns:** effective-n audit exposed n≈1

## LIN-12 — Di Mino *301=/na/ exact claim audit
- **Origin:** docs/linear-a-claims-2026.md qualitative three-part takedown (literature/primary-source, NOT a mechanical verdict)
- **Trajectory:** di_mino exact mechanical gate (families A-H + PC + end-to-end null)
- **Current authoritative:** di-mino: DI_MINO_CORE_VERDICT=REJECT (chain *301=/na/→N-W-Y→dwell→Semitic); pipeline calibrated (PC PASS); end-to-end FP=1.0; H4 PARTIAL_SUPPORT L3-functional; H7-H12 SOURCE_BLOCKED
- **Obsolete/superseded:** —
- **Verdict evolution:** qualitative critique (paper §4, flagged as NOT-yet-mechanical) → exact mechanical REJECT
- **Why reruns:** the paper named the mechanical gate as the missing priority

## LIN-13 — Metrology / accounting / masked-quantity
- **Origin:** paper metrology NULL (held-out fraction balance p=1.0; only J=1/2 = Bennett 1950)
- **Trajectory:** observable_channels masked-logogram (Exp1) + masked-quantity (Exp2)
- **Current authoritative:** observable: masked-logogram + masked-quantity REFUTED (commodity is a document-series shortcut; word-context fails A12 + cross-site)
- **Obsolete/superseded:** —
- **Verdict evolution:** metrology NULL → masked-quantity REFUTED
- **Why reruns:** reframed as observable-channel recovery

## LIN-14 — Falsification instruments (L_fake / gate calibration / opaque-LB positive controls)
- **Origin:** L_fake canary + litindex decontamination + gate null calibration
- **Trajectory:** gate_null_calibration (3/500=0.6% false graduation) → opaque-LB + Ugaritic↔Hebrew surrogates → di_mino PC (PC1-6)
- **Current authoritative:** instruments VALIDATED: L_fake CANARY_HOLDS (every eps), gate FP 0.6% (CP-upper 1.54%), LB morphology control HAS power, di_mino PC PASS (recovers real+planted, rejects fake)
- **Obsolete/superseded:** —
- **Verdict evolution:** SUPPORTED throughout (the discipline machinery works)
- **Why reruns:** reused across campaigns as the honesty backstop

