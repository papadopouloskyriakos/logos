# Linear A methods — result matrix

214 instances. Full fields in data/METHOD_INSTANCES.csv; load-bearing numbers + verification class in data/RESULT_NUMBERS.csv. Grouped by campaign lineage.

## paper_core (39 instances)

| id | method | layer | outcome | verdict | power |
|---|---|---|---|---|---|
| PC-01-scaffold | Comparison-layer scaffold: predict/verdict/family_scores + | NOT_APPLIC | NOT_APPLICABLE | n/a (it IS the verdict engine); grep-ver | n/a |
| PC-02-decontamination-framework | Decontamination framework: S_phono / S_morph / N_eff instr | NOT_APPLIC | NOT_APPLICABLE | 226->365 tests pass; S_morph productivit | 100% on genuine re |
| PC-03-inventory-ontology | Cleaned GORILA/SigLA sign ontology by inheritance (259 tok | L1 (sign-i | STRUCTURAL_ONLY | 35/35 tests (+4 xfail); class counts + c | n/a |
| PC-04-information-floor | Shannon unicity-distance information floor (WITHDRAWN as i | L0/L1 diag | UNDERDETERMINED | WITHDRAWN by two independent red-teams;  | n/a |
| PC-05-morphology-pooled | Direction A pooled unsupervised morphology / affix inducti | L3 (struct | NULL_PUBLISHED | has_morphology_power=False (real 0.250 b | underpowered by sh |
| PC-06-segmentation-published | Word-boundary segmentation positive: DP-unigram (Goldwater | L2 (struct | SUPPORTED | micro-F1 0.4361 vs random 0.3888; site-c | adequate; positive |
| PC-07-linb-morphology-control | Linear B (Mycenaean Greek) morphology positive control for | L3 (contro | SUPPORTED | has_morphology_power=True: real 0.5625 > | fires; power track |
| PC-08-morphology-stratified | Direction-A STRATIFIED morphology re-run (per-genre stratu | L3 (struct | NULL_PUBLISHED | has_validated_morphology=False at pre-re | thin strata; even  |
| PC-09-metrology | Direction D metrology: constraint-optimization / RANSAC fr | L4/L3 (fun | NULL_PUBLISHED | held-out fraction balance 0.0 vs permuta | parse-coverage lim |
| PC-10-ab-alignment-null | Track B A<->B distributional/sequence alignment: held-out  | L6 (phonet | NULL_PUBLISHED | clearly_above_chance=False; best (CCA/pr | positive control 0 |
| PC-11-distributional-phonology-pilot | Distributional-phonology pilot (Track-2): does a sign's co | L6 (phonet | NULL_PUBLISHED | bridge_detected=False (DATA-LIMITED); co | detects planted s> |
| PC-12-palaeo-image | Sign-image palaeography: cross-script A<->B IMAGE alignmen | L6 image-b | CIRCULAR | classical direct-NN 0.410 / Procrustes 0 | recovers far above |
| PC-13-lfake-canary | L_fake fabricated-language canary: false-positive floor se | NOT_APPLIC | SUPPORTED | CANARY_HOLDS at every eps: real S_lex cl | clears at every ep |
| PC-14-litindex-population | litindex populated with 6 verified West-Semitic proposals  | NOT_APPLIC | NOT_APPLICABLE | index 57->63 claims; 6 written, 2 reject | n/a |
| PC-15-llm-ablation-c4 | C.4 LLM-ablation on qwen2.5:72b: contamination delta (raw  | L6 (LLM ph | INCOMPLETE | contamination_rate=1.000 in all 32 defin | harness runs clean |
| PC-16-llm-ablation-gate2 | C.4 gate-2 cognate-level per-word regurgitation table (qwe | L6 / decon | PARTIAL_SUPPORT | cognate_contamination_rate CONFOUNDED (r | distinctive regurg |
| PC-17-lvirgin-lnotindexed | L_virgin / L_not_indexed generalization test on qwen2.5:72 | L6 / decon | PARTIAL_SUPPORT | headline excess-gap 0.601 p=0.0005 is CO | no power for rigor |
| PC-18-gate-null-calibration | Graduation-gate null calibration: realized false-graduatio | NOT_APPLIC | SUPPORTED | false_graduations 3/500 = 0.6%; Clopper- | companion LB morph |
| PC-19-tamburini-reproduction | Tamburini 2025 CSA_OptMatcher reproduction (non-neural cog | NOT_APPLIC | PARTIAL_SUPPORT | wrapper VALIDATED: Luvian-Hittite 0.475= | converged benchmar |
| PC-20-ugaritic-hebrew-heuristic | Ugaritic->Hebrew known-answer recovery (simplified Hungari | NOT_APPLIC | PARTIAL_SUPPORT | cognate_accuracy 0.0055 (12/2182) vs cha | above chance (find |
| PC-21-csa-h100-build | CSA batched-parallel CUDA cognate-matcher build + validati | NOT_APPLIC | INCOMPLETE | matcher built + validated bit-identical  | n/a |
| PC-22-csa-sufficiency-curve | CSA pseudo-decipherment learning-curve sufficiency sweep ( | L0/L1 suff | INCOMPLETE | deposited LA-scale value is an _interp E | under-convergence  |
| PC-23-referee-simulation | Hostile-referee simulation of the preprint (revision roadm | NOT_APPLIC | NOT_APPLICABLE | verdict: major revisions; 8 issues (2 ru | n/a |
| PC-24-review-code-fixes | Pre-submission code-integrity fixes (P0-P5 + second-pass)  | NOT_APPLIC | NOT_APPLICABLE | 365 passed, 4 xfailed; every determinist | n/a |
| PC-25-paper-audit-priorart | Paper audit: Tamburini 2025 as major prior art; novelty re | NOT_APPLIC | NOT_APPLICABLE | faithful-B-K&K rebuild MOOT (Tamburini p | n/a |
| PC-26-redteam-synthesis | Expert red-team synthesis: withdrawn overclaims + correcte | NOT_APPLIC | NOT_APPLICABLE | 7 claims WITHDRAWN (unicity identifiabil | n/a |
| PC-30-crossscript-gate-phase0 | Cross-script LA<->LB value-recovery gate Phase 0 + 0.5 (po | L6 (design | NO_VERDICT_RECORDED | Phase 0 MARGINAL (power 0.26 at s<=3, GO | GO conditional on  |
| PC-31-crossscript-gate-phase1 | Cross-script gate Phase 1 one-shot: preregistered/DOI-time | L6 (phonet | REFUTED | REFUTE_LOTO_FRAGILE: full clears (p=0.03 | certified GO (brid |
| PC-32-crossscript-gate-phase2 | Cross-script gate Phase 2 second one-shot: 8 vetted anchor | L6 (phonet | REFUTED | REFUTE: full p_raw 0.0255 misses correct | certified LOTO-sur |
| PC-33-crossscript-gate-phase3 | Cross-script gate Phase 3 + corpus-completeness sweep (Ane | L1/L6 (cor | INCOMPLETE | GAP verdict PENDING-FULL-EDITION; VERDIC | n/a |
| PC-34-segmentation-extension | Segmentation extension: PYP-Gibbs + tiny neural BiLSTM + t | L2 (word s | SUPPORTED | gates PASSED (DP 0.4361/random 0.3888 EX | adequate (all rich |
| PC-35-representation-audit | Representation audit: transcription-treatment sensitivity  | L1 (repres | STRUCTURAL_ONLY | sensitivity LOW/LOCALIZED: under plausib | n/a |
| PC-36-schema-recon | Schema recon: does the corpus retain the administrative pa | L3 (functi | STRUCTURAL_ONLY | PARTIAL-executable: integer core (commod | n/a |
| PC-37-schema-induction | Administrative-schema induction: total-reconciliation from | L3 (functi | STRUCTURAL_ONLY | EXPLORATORY/DESCRIPTIVE (NOT gate-valida | null proves the st |
| PC-38-campaign-phaseA-audit | Linear A 12h campaign Phase A: exhaustive verdict-map audi | meta (L2-L | UNDERDETERMINED | every avenue converges on one corpus-ide | ceiling liftable o |
| PC-39-campaign-egyptian-power | Campaign T2: Egyptian external-anchor frozen-regime power  | L6 (extern | NO_POWER | design-viable but scarcity-limited: FP d | NOT NO_POWER by de |
| PC-40-campaign-completeness-critic | Campaign T3: adversarial completeness critic (methods / da | meta | UNDERDETERMINED | all 3 diverse-lens critics converge: NO_ | the one non-circul |
| PC-41-campaign-identifiability-synthesis | Campaign T4: identifiability synthesis (parameters > const | L6 (info-b | UNDERDETERMINED | UNDERDETERMINED: 259 sign-value paramete | estimated_power 0. |
| PC-42-campaign-kuro-control | Campaign T5: KU-RO arithmetic-reconciliation positive cont | L3 (functi | STRUCTURAL_ONLY | harness_fires_on_signal=True (25% vs 1.4 | fires strongly in- |

## constraint_expansion (20 instances)

| id | method | layer | outcome | verdict | power |
|---|---|---|---|---|---|
| CE-A-identifiability-recount | Stage A identifiability reopening audit (syllabary paramet | meta (audi | NULL | A_REOPENED — prior 259>212 INVALIDATED a | NOT_APPLICABLE |
| CE-B2-sign-allography-recount | Stage B2 sign/allography inventory forensics | L0-L1 (phy | STRUCTURAL_ONLY | Confirms syllabary=92 (259 = 108 ligatur | NOT_APPLICABLE |
| CE-B1-sigla-cross-edition-independence | Stage B1 SigLA cross-edition independence check (AB-class  | L1 (sign-i | STRUCTURAL_ONLY | SigLA = second digitization of same GORI | NOT_APPLICABLE |
| CE-B4-joins-effective-n | Stage B4 joins/duplicates effective_n recomputation | L0 (physic | STRUCTURAL_ONLY | Raw 1341 overstates independence -> 1242 | NOT_APPLICABLE |
| CE-B5-notation-typing | Stage B5 notation-channel typing + cleaned phonetic wordfo | L1-L2 (sig | STRUCTURAL_ONLY | 26% of the word channel was non-phonetic | NOT_APPLICABLE |
| CE-B6-support-invariance-axis | Stage B6 context/support invariance-axis recovery | L0-L2 (met | STRUCTURAL_ONLY | 'context' field mislabelled (holds chron | NOT_APPLICABLE |
| CE-C-source-discovery | Stage C new-source & evidence discovery audit | L0 (eviden | STRUCTURAL_ONLY | C_NEW_INFORMATION_FOUND but none value-i | NOT_APPLICABLE |
| CE-D1-formula-grammar | Stage D1 formula-grammar mining | L2-L3 (str | TRIVIAL_RECOVERY | CONFIRMS_KNOWN — nothing beyond libation | corpus too shallow |
| CE-D2-morphology | Stage D2 morphology paradigm test (clean material) | L3-L5 (gra | NULL | NULL (has power, not NO_POWER) — paradig | HAS POWER (Stage E |
| CE-D4-accounting-closure | Stage D4 accounting-closure / fraction-typing test | L3 (functi | TRIVIAL_RECOVERY | CONFIRMS_KNOWN — typing fractions does N | planted control re |
| CE-D5-cross-site-support-invariance | Stage D5 cross-site/support phonotactic invariance (held-o | L2 (struct | STRUCTURAL_ONLY | CONFIRMS_KNOWN — a GENUINE held-out posi | fires (significant |
| CE-D7-compression-grammar | Stage D7 administrative-grammar compression (held-out) | L2 (struct | STRUCTURAL_ONLY | CONFIRMS_KNOWN — GENUINE held-out positi | fires (beats all b |
| CE-E-method-validation-battery | Stage E value-recovery method-validation battery (fires on | meta (meth | SUPPORTED | METHOD_VALID_LA_NULL_IS_CORPUS — detecto | DEMONSTRATED — det |
| CE-F-external-anchor-reaudit | Stage F external-anchor re-audit (Salgarella non-circular  | L5-L6 (lex | NO_POWER | NO_NONCIRCULAR_ANCHOR — Salgarella's A-B | no non-circular an |
| CE-G-language-family-gate | Stage G language-family hypothesis authorization gate | L8 (langua | NOT_APPLICABLE | G_NOT_AUTHORIZED — no value anchor exist | NOT_APPLICABLE (ga |
| CE-H-relabeling-invariance-null | Stage H agnostic internal value-search relabeling-invarian | L6 (phonet | NULL | PROVABLE_NULL — held-out bigram log-like | PROVABLE (analytic |
| CE-J-end-to-end-null | Stage J end-to-end decipherment null (gate-bounded) | L6-L9 (ful | NULL | No agnostic system beats the end-to-end  | gate calibrated; i |
| CE-I-sealed-challenges | Stage I sealed-challenge preregistration (no surviving hyp | L5-L6 (wou | NOT_APPLICABLE | n/a — no surviving hypothesis to seal (S | NOT_APPLICABLE |
| CE-K-active-unlock-ranking | Stage K active-unlock ranking (what evidence would actuall | meta (acqu | NULL | Only external value-bearing evidence hel | NOT_APPLICABLE |
| CE-L-final-verdict-synthesis | Stage L final verdict synthesis (by earned layer) | meta (synt | UNDERDETERMINED | campaign_status=COMPLETE; decipherment_r | NOT_APPLICABLE |

## foundry (23 instances)

| id | method | layer | outcome | verdict | power |
|---|---|---|---|---|---|
| FND-01 | WP1 formal identifiability & symmetry theorem (relabeling- | L2 (struct | REFUTED (of the prior glob | PRIOR_THEOREM_OVERSTATED | N/A |
| FND-02 | WP1 word-initial-rate position statistic — C/V symmetry-br | L2 (relati | PARTIAL_SUPPORT (LB, singl | PRIOR_THEOREM_OVERSTATED (empirical leg) | single feature; st |
| FND-03 | WP1 symmetry-breaking atlas (13-channel enumeration) | L2 / meta  | STRUCTURAL_ONLY (organizin | atlas built (NOT a verdict-bearing test) | N/A |
| FND-04 | WP3.1 multi-feature C/V classifier (logistic, LB 7-fold CV | L2 (C/V pa | SUPPORTED on LB (partition | CV_PARTITION_RECOVERED (LB) | adequate on LB; LA |
| FND-05 | WP3.1b unsupervised LA-internal C/V clustering (k-means/GM | L2 | NULL (needs labels) | NULL | dominant variance  |
| FND-06 | WP3.2 scribal-substitution similarity graph (n-gram contex | L2 (phonol | SUPPORTED on LB (SIGNAL_VA | SIGNAL_VALIDATED (LB); LA candidate-unde | LA max weight 105  |
| FND-07 | WP3.2b substitution power curve (LB subsample ladder) | L2 (power  | PARTIAL_SUPPORT / QUANTIFI | QUANTIFIED | explicitly a power |
| FND-08 | WP3.3 orthographic-alternation detector | L2/L3 (ort | SUPPORTED on LB / NO_POWER | validated (LB) / NO_POWER (LA) | LA unsegmented ->  |
| FND-09 | WP3.4 morphology C/V-typing detector (bits/word gain) | L3 (morpho | SUPPORTED on LB (detector  | NULL (LA) | LA lacks paradigm  |
| FND-10 | WP2 segmentation lever (packed vs GORILA word units, C/V v | L2 (method | PARTIAL_SUPPORT (segmentat | SEGMENTATION_LEVER_HELPS | shows part of the  |
| FND-11 | WP4 diachronic & cross-script sign-evolution (shape / dist | L5/L6 (val | NULL (non-circular distrib | NULL (4th distributional null); shared-A | distributional at  |
| FND-12 | WP5(a) external-anchor inventory (3-channel provenance cen | L5 (anchor | STRUCTURAL_ONLY / TRIVIAL_ | INVENTORY_BUILT | anchors are not th |
| FND-13 | WP5(b) reduced-seed C/V bootstrap (semi-supervised label s | L2 (C/V pa | SUPPORTED on LB (mechanism | SIGNAL_VALIDATED (LB) / NULL (LA) | LA affinity graph  |
| FND-14 | WP5.2 seed-propagation power curve (LB size ladder) | L2 (power  | QUANTIFIED (LA ~chance; ne | QUANTIFIED | the WP5 LA null is |
| FND-15 | Synthetic recovery lab (planted CV-syllabary, 5 regimes) | L2 (method | SUPPORTED (methods proven  | QUANTIFIED (5/5) | the core deliverab |
| FND-16 | WP6 agnostic reduced-K-class value search + multi-family e | L5/L6 (val | NULL (fails decisive value | AT_END_TO_END_NULL | detects generic li |
| FND-17 | WP7 word-segmented substitution channel (segmentation trad | L2 (method | REFUTED (of the 'segmentat | AT_END_TO_END_NULL for the word-segmente | short GORILA words |
| FND-18 | WP8 word-segmented reduced-seed C/V bootstrap | L2 (C/V pa | PARTIAL_SUPPORT (coverage  | opaque-LB gate unchanged (>=3 correct vo | coverage improves  |
| FND-19 | Candidate-language round 1 (West Semitic / Pre-Greek-Anato | L8/L9 (lan | NULL (same-structure-lexic | AT_END_TO_END_NULL | adequate to detect |
| FND-20 | Candidate-language round 2 (Hurrian / Luwian / control) | L8/L9 | NULL | AT_END_TO_END_NULL | adequate |
| FND-21 | Candidate-language round 3 (Etruscan / Aegean-isolate subs | L8/L9 | NULL (the decisive clean f | AT_END_TO_END_NULL | the clean mechanis |
| FND-22 | Sealed-prediction programme (5 hashed held-out challenge m | L0-L9 (eva | NOT_APPLICABLE / NO_VERDIC | NO_CANDIDATE_TO_SEAL | preserves the spli |
| FND-23 | Source-lineage audit / value-lineage-independence register | meta (prov | STRUCTURAL_ONLY (honesty f | INVENTORY_BUILT (63 sources; quota met) | N/A |

## relative_phonology (46 instances)

| id | method | layer | outcome | verdict | power |
|---|---|---|---|---|---|
| A1_reconstruct | Reconstruction/recompute of Foundry position->C/V analogue | L2 | SUPPORTED | REPRODUCED_EXACTLY + filter-bug found (e | NOT_RECORDED |
| A2_multiplicity | Multiplicity audit of the position->C/V p-value | L2 | REFUTED | SINGLE-FEATURE POSITION DOWNGRADED — sur | NOT_RECORDED |
| A3_replications | Independent replications of C/V partition (GMM/HMM latent  | L2 | REFUTED | EXPLORATORY_FREQUENCY_ARTIFACT; 2 unsupe | NOT_RECORDED |
| A4_grouped | Grouped generalization (freq-band-disjoint / LOSO / chrono | L2 | REFUTED | REFUTE-AS-STATED; collapses under freq-b | NOT_RECORDED |
| A5_degradation | Degradation response surface (LB -> LA regime) | L2 | REFUTED | REFUTE+NO_POWER; flat non-significant su | NOT_RECORDED |
| A6_nulls | End-to-end null battery for the position channel (WP-A ver | L2 | REFUTED | CV_ANALOGUE_REFUTED (WP-A verdict) | NOT_RECORDED |
| B1_representations | Build 8 channel-specific segmentation representations | L1 | SUPPORTED | COMPLETE — 8 representations, provenance | NOT_RECORDED |
| B3_known_script | Known-script (LB) boundary recovery + downstream by segmen | L2 | SUPPORTED | SUPPORTED_ON_LB (6 families beat baselin | NOT_RECORDED |
| B4_synthetic | Synthetic syllabic-corpus segmentation calibration | L1 | NO_POWER | QUANTIFIED: at LA hapax regime boundary  | NOT_RECORDED |
| B5_la_ensemble | Linear A segmentation ensemble (validated models only) | L2 | STRUCTURAL_ONLY | probabilistic over-cut set; real signal  | NOT_RECORDED |
| B6_downstream | Downstream causal segmentation test (held-out LB endorseme | L2 | PARTIAL_SUPPORT | held-out LB endorses GORILA_WORD; ensemb | NOT_RECORDED |
| C1_candidates | Catalogue LA one/few-sign-diff substitution pairs | L1 | SUPPORTED | CATALOGUED 3749 pairs + 253 edition-disa | NOT_RECORDED |
| C3_lb_calib | Linear B substitution-channel calibration | L2 | SUPPORTED | CALIBRATED: consonant-held axis AUC 0.74 | NOT_RECORDED |
| C_AUDIT | Substitution consonant-held axis WP-A-style audit on LB (B | L2 | SUPPORTED | SUBSTITUTION_CONSONANT_AXIS_VALIDATED (s | NOT_RECORDED |
| C4_la_graph | Linear A substitution graph (anonymous relative classes) | L2 | NULL | CONSONANT_HELD_ANALOGUE = NOT_RECOVERED  | NOT_RECORDED |
| C5_stability | LA substitution-graph stability + deflated information gai | L2 | UNDERDETERMINED | FRAGILE; SEVERE Haghia-Triada dependency | NOT_RECORDED |
| D1_multiview | Multi-view latent relative-feature model over audited chan | L2 | NULL | MULTIVIEW_NO_VALUE_RECOVERY (fused vowel | NOT_RECORDED |
| D2_ablations | View ablations of the multi-view model | L2 | NULL | LA null after frequency across all views | NOT_RECORDED |
| D3_seed_audit | Seed-propagation audit of Foundry '3-4 seeds -> 0.87' | L2 | REFUTED | SEED_PROPAGATION_FREQUENCY_ARTIFACT (3rd | NOT_RECORDED |
| D4_frontier | Minimal-seed frontier for value recovery | L2 | NO_POWER | LA below minimal-seed threshold; value-b | NOT_RECORDED |
| D5_posterior | Linear A anonymous relative posterior classes (value-free) | L2 | NULL | anonymous K=2 partition (provenance+morp | NOT_RECORDED |
| E1_morphology | Three anonymous morphology models (MDL/Bayesian/FSM-paradi | L3 | STRUCTURAL_ONLY | A- prefixation robust; corrects wave-2 t | NOT_RECORDED |
| E2_formula | Formula grammar induction (ledger + libation registers) | L3 | STRUCTURAL_ONLY | 2 formula grammars (ledger KU-RO/KI-RO + | NOT_RECORDED |
| E3_crosssite | Cross-site generalization of morphology (A-/-JA/I-) | L3 | NULL | published p 0.0099 (non-HT A-) DOWNGRADE | NOT_RECORDED |
| E4_paramreduce | Parameter reduction: compression vs held-out prediction | L3 | NULL | compresses training but held-out gain no | NOT_RECORDED |
| E5_wrongstruct | Wrong-structure controls for A- morphology | L3 | SUPPORTED | real A- morphology beats all wrong-struc | NOT_RECORDED |
| F1_decompose | Cross-script evidence decomposition (per-channel calibrata | L2 | NULL | only admin_function non-circular+calibra | NOT_RECORDED |
| F2_calib | Known-script calibration of shape->descent->value chain | L2 | NO_POWER | cross-script value power NULL at LA scal | NOT_RECORDED |
| F4_loso | Leave-one-sign-out LA-LB value-family prediction (+Cypro-M | L2 | NULL | LOSO NULL (R@5 0.071 vs shuffled 0.066;  | NOT_RECORDED |
| G1_anchor_audit | Audit of existing 115 external anchors | L2 | NULL | 115 records -> 6 lineages / 1 value chan | NOT_RECORDED |
| G2_expand | Expand high-value multi-sign-constraining anchor classes | L2 | NULL | rich relative substrate but ZERO new val | NOT_RECORDED |
| G3_seedq | Seed-quality classification + compound systems + anchor nu | L2 | NULL | SEED_A=0; no independently-secure value  | NOT_RECORDED |
| H1_round1 | Bounded candidate round 1 (relative-class-constrained fami | L2 | NULL | AT_END_TO_END_NULL (0/3 families; SEM on | NOT_RECORDED |
| H2_round2 | Bounded candidate round 2 (anchor-constrained family/isola | L2 | NULL | AT_ANCHOR_CONSTRAINED_NULL (anchors add  | NOT_RECORDED |
| H3_round3 | Bounded candidate round 3 (morphology-first joint decipher | L2 | UNDERDETERMINED | AT_JOINT_INFERENCE_NULL — backbone relab | NOT_RECORDED |
| I1_agnostic | Agnostic constrained value search (beam/best-first + MDL g | L3 | UNDERDETERMINED | UNDERDETERMINED_NO_RECOVERY (detector LI | NOT_RECORDED |
| J1_exposure | Anetaki public-exposure audit (sealable-delta definition) | L2 | SUPPORTED | only unpublished transliterated VALUES s | NOT_RECORDED |
| J2_seals_programme | Sealed-prediction programme (freeze 5 hashed seals) | L3 | STRUCTURAL_ONLY | 5 hashed seals frozen; phonetic scoring  | NOT_RECORDED |
| SEAL_2 | SEAL_2 held-out 15% inscriptions (A-prefix + ledger well-f | L3 | SUPPORTED | SUPPORTED (held-out A-rate 0.0525 inside | NOT_RECORDED |
| SEAL_3 | SEAL_3 unseen site Khania (carrier-value grammar transfer  | L3 | SUPPORTED | SUPPORTED (carrier-value wf 0.8525; KU-R | NOT_RECORDED |
| SEAL_4 | SEAL_4 unseen libation family (rigid anchor order, leave-o | L3 | SUPPORTED | SUPPORTED (0/45 inversions, LOO) | NOT_RECORDED |
| SEAL_5 | SEAL_5 masked-notation ledger arithmetic (committed negati | L3 | NULL | honest committed NEGATIVE — UNDERPOWERED | NOT_RECORDED |
| ANETAKI_DELTA_SEAL | ANETAKI_FINAL_EDITION_DELTA_SEAL (prospective structural-o | L3 | INCOMPLETE | SEALED_PROSPECTIVE (PASS=null; scoreable | NOT_RECORDED |
| K1_nulls | Full adaptive best-of-selection null programme | L3 | SUPPORTED | NULLS_CONFIRM_NULLS; value-layer FP=chan | NOT_RECORDED |
| L1_sourcewatch | Source watch + expected-information-gain ranking + ingesti | L0 | INCOMPLETE | 9 acquisitions ranked; Anetaki II = fals | NOT_RECORDED |
| M1_synthesis | Final synthesis + 7-licence gate evaluation | L3 | NULL_PUBLISHED | NEW_CONSTRAINTS_BUT_NO_DECIPHERMENT; all | NOT_RECORDED |

## di_mino (21 instances)

| id | method | layer | outcome | verdict | power |
|---|---|---|---|---|---|
| DIMINO-T00-CENSUS | Prior-test census: has the exact *301=/na/ core gate ever  | L0 | NOT_APPLICABLE | EXACT_CORE_CLAIM_GATE (H1-H6) DOES NOT E | NOT_APPLICABLE |
| DIMINO-T01-ARCHIVE | Immutable public-claim archive + cryptographic hashing of  | L0 | NOT_APPLICABLE | CLB-01 (AI Clambake article, 2026-06-16) | NOT_APPLICABLE |
| DIMINO-T02-CLAIMGRAPH | Claim dependency graph + free-parameter (lower-bound searc | L1 | CIRCULAR | Load-bearing circularity e2->e3->e4: *30 | NOT_APPLICABLE |
| DIMINO-T03-PREREG | Frozen preregistration of H1-H12 with success/null/failure | L0 | NOT_APPLICABLE | Frozen 2026-07-08 before any outcome obs | min ~3 independent |
| DIMINO-T04-CORPUS | Non-circular libation-formula / *301 corpus build with der | L2 | NOT_APPLICABLE | 36 *301 attestations / 23 distinct forms | held_out 32; leave |
| DIMINO-T05-SEGMENTATION | Segmentation comparison of A-TA-I-*301-WA-JA across 6 fami | L2 | STRUCTURAL_ONLY | DECISIVE AGAINST the *301-WA-JA root cut | NOT_APPLICABLE |
| DIMINO-A-VALUE-SWEEP | Family A — exhaustive *301 value audit (H1: *301=/na/) | L6 | REFUTED | REJECT. Primary S_morph value-INVARIANT  | ADEQUATE — 32 held |
| DIMINO-B-ROOT-SEARCH-NULL | Family B — Semitic root existence search-null (H2: A-TA-I- | L5 | NULL_PUBLISHED | REJECT — root existence is a generic sea | ADEQUATE (enumerab |
| DIMINO-B-LFAKE-CANARY | Family B — L_fake / Packard edit-distance 'match-exists' c | L5 | NO_POWER | NO_POWER — the L_fake INVENTED lexicon a | ZERO (floor >= rea |
| DIMINO-B-GLOSS-FEATURE | Family B — gloss specificity + formula-feature prediction  | L4 | REFUTED | REJECT — 'dwell' scores 0.0/3 on observa | limited (single ta |
| DIMINO-C-MORPHOLOGY | Family C — exact morphology / paradigm audit + head-to-hea | L7 | REFUTED | REJECT. MORPH_ROOT REFUTED (sign after * | MORPH detector has |
| DIMINO-D-LOSO | Family D — leave-one-site-out formula prediction (H4 funct | L3 | NO_POWER | NO_POWER — Di Mino's exact-form predicti | INSUFFICIENT — 3 e |
| DIMINO-E-FULLFORMULA | Family E — full libation-formula interpretation audit (nov | L4 | STRUCTURAL_ONLY | REJECT (one-novel-parameter): 34/35 sign | NOT_APPLICABLE |
| DIMINO-PC-CONTROLS | Positive/negative controls PC1-PC6 + PCNP (pipeline calibr | L0 | SUPPORTED | PASS — pipeline CALIBRATED. PC1 Ugaritic | confirmed on contr |
| DIMINO-E2E-NULL | End-to-end adaptive null programme + whole-pipeline false- | L5 | NULL_PUBLISHED | End-to-end FP rate = 1.0; search-adjuste | value channel HAS  |
| DIMINO-F-SIGNMAP | Family F — 40-sign map gate (H7 ~40 signs / H8 13 LA-only  | L6 | NOT_APPLICABLE | FULL_SIGN_MAP_VERDICT = SOURCE_BLOCKED — | NOT_APPLICABLE |
| DIMINO-G-LEXICON | Family G — 408-term lexicon gate (H9) | L5 | NOT_APPLICABLE | FULL_LEXICON_VERDICT = SOURCE_BLOCKED —  | NOT_APPLICABLE |
| DIMINO-H-LB-CORRECTIONS | Family H — Linear B corrections gate (H10: 5 LB signs reso | L6 | NOT_APPLICABLE | LINEAR_B_CORRECTIONS_VERDICT = SOURCE_BL | NOT_APPLICABLE |
| DIMINO-H-LOGOGRAM-CORRECTIONS | Family H — logogram corrections gate (H11) | L2 | NOT_APPLICABLE | LOGOGRAM_CORRECTIONS_VERDICT = SOURCE_BL | NOT_APPLICABLE |
| DIMINO-VERDICT | Final mechanical adjudication — DI_MINO_CORE_VERDICT + ext | L3 | REFUTED | DI_MINO_CORE_VERDICT = REJECT. Chain *30 | ADEQUATE (PC passe |
| DIMINO-PRIOR-QUALITATIVE-AUDIT | PRIOR qualitative literature audit of the Di Mino claim (s | L5 | NO_VERDICT_RECORDED | NOT_APPLICABLE — explicitly flagged in t | NOT_APPLICABLE |

## admin_structure (18 instances)

| id | method | layer | outcome | verdict | power |
|---|---|---|---|---|---|
| ADMIN-01 | Prior-art / novelty audit (blinded cross-script admin sche | NOT_APPLIC | NOT_APPLICABLE | NOVELTY_SUPPORTED (combinatorial); 0/20  | NOT_APPLICABLE |
| ADMIN-02 | Source / licence audit + de-phoneticisation blinding desig | NOT_APPLIC | NOT_APPLICABLE | No licensing/repro blocker; blinding = m | NOT_APPLICABLE |
| ADMIN-03 | Canonical de-phoneticised transferable document graph (LB  | L2 (docume | NOT_APPLICABLE (infrastruc | Frozen graphs; determinism + no-semantic | NOT_APPLICABLE |
| ADMIN-04 | Blind formula-cluster induction (document grouping) | L2 (docume | NOT_APPLICABLE (grouping u | GROUPING_ONLY; SAME_FORMULA_CLUSTER edge | NOT_APPLICABLE |
| ADMIN-05 | LB role ontology freeze (8 coarse / 17 fine classes) | L4 (functi | NOT_APPLICABLE | FROZEN (ontology hash 781902c0) | NOT_APPLICABLE |
| ADMIN-06 | Automated annotation feasibility pilot (Stage 5.1, model-b | L4 (functi | NO_POWER | NO_POWER (alpha 0.614 < 0.667 primary-go | min detectable K=1 |
| ADMIN-07 | Human-expert annotation package (blinded double annotation | L4 (functi | INCOMPLETE | BLOCKED / UNTESTED — validate/compare/ad | would test whether |
| NOHUM-01 | Source-label dependency audit (DAG) — shared-decipherment  | NOT_APPLIC | NOT_APPLICABLE (structural | All content-role sources descend from sa | forecasts a thin n |
| NOHUM-02 | Deterministic source-derived label corpus (Stage 3) | L4 (functi | NOT_APPLICABLE (corpus bui | 66 non-trivial REFERENCE_GOLD_A; only 2  | forecasts NO_POWER |
| NOHUM-03 | Weak-supervision labeling functions (13 LFs, WS0-4) + circ | L4 (functi | NULL (edition-independent  | coverage 0.71 / abstain 0.29 / conflict  | structural signal  |
| NOHUM-04 | Pre-Stage-5 power gate -> NO_POWER_BEFORE_MODELING (route  | L4 (functi | NO_POWER | NO_POWER_BEFORE_MODELING | 0.0 (definitive un |
| OBS-01 | Experiment 1 — masked logogram (commodity channel) recover | L3 (functi | REFUTED (per-channel NEGAT | NEGATIVE — word-context does NOT beat se | well-powered (457  |
| OBS-02 | Experiment 2 — masked quantity/accounting channel recovery | L3 (functi | REFUTED (TRIVIAL_RECOVERY  | per-channel NEGATIVE: M_sign below major | well-powered (1,59 |
| OBS-03 | Experiment 3 — accounting-closure structure + masked-summa | L2 (docume | STRUCTURAL_ONLY (L2 positi | closure 0.071 > null 0.049 (real but spa | closure concentrat |
| OBS-04 | Experiment 4 — document-template completion (notation-type | L2 (docume | STRUCTURAL_ONLY (L2 positi | M_template 0.508 > position 0.398 > glob | held-out unseen do |
| OBS-05 | Experiment 5 — cross-site invariance of the template gramm | L2 (docume | STRUCTURAL_ONLY (bidirecti | SITE_DEPENDENT — template beats target b | adequate (thousand |
| OBS-06 | Experiment 6 — pseudo-script O2 (sign permutation) + D8 (L | L2 (docume | STRUCTURAL_ONLY (template  | O2: template 0.497 = 0.497 (identical -> | LA density compara |
| OBS-07 | Mechanical gate synthesis — OBSERVABLE_CHANNEL_READY = NO | L3 functio | REFUTED (L3) + NO_POWER/NO | OBSERVABLE_CHANNEL_READY = NO; FUNCTIONA | well-powered negat |

## external_language (33 instances)

| id | method | layer | outcome | verdict | power |
|---|---|---|---|---|---|
| EA-01-SLOT-CLASSIFIER | Internal-only Linear A slot classifier (Task A) | L3 | STRUCTURAL_ONLY | Frozen manifest of 1165 candidates; 11 t | NOT_APPLICABLE |
| EA-02-TOPONYM-POWER-ENVELOPE | Toponym-anchor power envelope pilot (Task D / E1) | L6 | NO_POWER | Design-level null (provisional): in-samp | leans NO_POWER for |
| EA-03-FROZEN-EGYPTIAN-CORRESPONDENCE-MODEL | Frozen Egyptian->foreign correspondence (group-writing->so | L7 | INCOMPLETE | Model NOT fit; calibration source blocke | NOT_RECORDED |
| EA-04-LB-MATCHED-SCARCITY-POSITIVE-CONTROL | Linear-B matched-scarcity positive control (Task B / E2) | L6 | INCOMPLETE | Protocol + module design + provisional d | gate: if pipeline  |
| EA-05-END-TO-END-NULL-FRAMEWORK | End-to-end null framework + adaptive-choice inventory + se | L6 | INCOMPLETE | Spec + 10 null families + config schema  | NOT_RECORDED |
| EA-06-E3-TOPONYM-CONFIRMATORY | Egyptian toponym-anchor confirmatory test (E3) | L7 | NO_VERDICT_RECORDED | Behind Stage-4 hard human-approval gate; | provisional NO_POW |
| EA-07-EA5647-PERSONAL-NAMES-GREEK | Personal-name anchor channel (E4) + EA5647 Keftiu-names id | L8 | TRIVIAL_RECOVERY | REQ-03 closed: EA5647's seven Keftiu nam | low a-priori (thin |
| EA-08-E5-ADMIN-SEMANTIC-ONTOLOGY | Mari/Ugarit/Egypt administrative ontology -> LA semantic s | L4 | INCOMPLETE | Bronze Mari/Kaptara records audited (REQ | NOT_RECORDED |
| EA-09-E6-KEFTIU-RITUAL-PHONOLOGY | Keftiu ritual-language phonological constraints (E6 / RQ4) | L6 | INCOMPLETE | Exploratory-only for phonology; voces ma | NOT_RECORDED |
| EA-10-E8-CANDIDATE-LANGUAGE-TOURNAMENT | Candidate-language tournament at equal budget (E8 / RQ5) | L8 | NO_VERDICT_RECORDED | Runs LAST, only after anchor+calibration | NOT_RECORDED |
| EA-11-E7-POPULATION-PRIOR | Population-history (aDNA/archaeology) prior audit (E7 / RQ | L8 | NO_VERDICT_RECORDED | May reorder candidate tests by AT MOST a | NOT_RECORDED |
| EA-12-EGYPTIAN-CALIBRATION-CORPUS-BUILD | Egyptian foreign-form calibration corpus build (Task B cor | L7 | INCOMPLETE | Hoch 1994 PDF OCR corrupts the translite | a too-small subset |
| LC-01-SIGLA-SILVER-RECONCILE | SigLA<->silver reconciliation crosswalk + corpus delta | L1 | STRUCTURAL_ONLY | matched 575; only-silver 766 (730 genuin | NOT_APPLICABLE |
| LC-02-AB-SIGN-EQUIVALENCE-MAP | A<->B sign-equivalence map freeze (77 tier-A homomorphs) | L1 | STRUCTURAL_ONLY | 77 tier-A AB homomorphs (LEVEL_1 shared  | NOT_APPLICABLE |
| LC-03-KNOWN-PAIR-AUDIT | Known-pair source-critical audit (the five continuities) | L5 | TRIVIAL_RECOVERY | 4 DEVELOPMENT_BENCHMARK, 1 CONFIRMATORY_ | NOT_APPLICABLE (de |
| LC-04-LA-CANDIDATE-PACKET-FREEZE | Internal-only LA candidate packet freeze (packet A) | L3 | STRUCTURAL_ONLY | PRIMARY 11 (tier-B TOPONYM_LIKE), SENSIT | the tiny 11-candid |
| LC-05-LB-TARGET-MANIFEST-FREEZE | Independent LB toponym target manifest freeze (packet B) | L4 | STRUCTURAL_ONLY | 33 targets: 5 DEVELOPMENT (known-pair LB | 16 EVALUATION targ |
| LC-06-CONTINUITY-MATCHING-MODEL | Administrative toponym-continuity matching model A1-A5 (ex | L5 | NULL_PUBLISHED | PRIMARY_B(11) x EVALUATION(16) = 0 match | full for exact con |
| LC-07-CONTINUITY-POSITIVE-CONTROLS | Continuity positive controls PC1-PC4 (sensitivity) | L5 | SUPPORTED | PC1 exact implant 100% recovery / 0 inci | confirms exact-con |
| LC-08-CONTINUITY-END-TO-END-NULLS | Continuity end-to-end null families (10 families, N=4000) | L5 | NULL_PUBLISHED | Channel is specific: freq-matched FP 1.2 | specificity good;  |
| LC-09-CONTINUITY-HELDOUT | Held-out generalization + known-pair LOO diagnostic (§VI) | L5 | NULL_PUBLISHED | Held-out PRIMARY(11)xEVALUATION(16)=0 at | sensitivity ceilin |
| LC-10-CONTINUITY-POWER-ENVELOPE | Continuity power envelope (exact vs drift) (§VII) | L5 | NO_POWER | Full power for EXACT continuity (min det | step function: FUL |
| LC-11-CONTINUITY-CIRCULARITY-AUDIT | Continuity circularity audit (§IX) | L5 | SUPPORTED | CIRCULARITY_LOW: all load-bearing compon | NOT_APPLICABLE |
| LC-12-CHANNEL-COMPARISON | Risk-adjusted channel comparison (LA<->LB vs Egyptian) | L5 | PARTIAL_SUPPORT | LA<->LB far more specific (FP 1.25% vs E | LA<->LB power ~0 f |
| LC-13-ADMIN-CHANNEL-CLOSURE | Administrative channel final verdict + closure (split verd | L5 | NULL_PUBLISHED | status=COMPLETE, channel_readiness=NO_PO | exact full, drift  |
| LR-01-LA-RITUAL-CANDIDATE-INVENTORY | LA ritual candidate inventory (packet A, internal-only) | L3 | STRUCTURAL_ONLY | PRIMARY_RITUAL 9 (7 cross-site, 2 single | the tiny independe |
| LR-02-LB-RITUAL-TARGET-INVENTORY | LB ritual/religious target inventory (packet B, LB-only) | L4 | STRUCTURAL_ONLY | 29 targets: 15 EVALUATION religious, 4 D | 15 targets is adeq |
| LR-03-KNOWN-RITUAL-PAIR-LEDGER | Known ritual-pair quarantine ledger (§VII) | L5 | TRIVIAL_RECOVERY | 5 pairs (incl PA-I-TO admin comparison): | removes the only e |
| LR-04-INDEPENDENT-DRIFT-FEASIBILITY | Independent drift-model feasibility audit (D0-D4; D3 admis | L6 | REFUTED | D3 (independent constrained edit, >=2 su | admissible models  |
| LR-05-RITUAL-LEAKAGE-FIREWALL | Ritual leakage firewall proven before any matching interfa | L3 | SUPPORTED | 7/7 (report lists 8 guarantees) pass: LA | NOT_APPLICABLE |
| LR-06-RITUAL-POSITIVE-CONTROLS | Ritual feasibility positive controls PC-R1..R4 (synthetic/ | L5 | SUPPORTED | PC-R1 exact synthetic implant recovered  | confirms exact-con |
| LR-07-RITUAL-NULLS-POWER-SIM | Ritual null families + power simulation (12 families, perm | L5 | NO_POWER | Exact: FP 0.8% (1.6% post-hoc-bounded),  | exact FULL (min 1) |
| LR-08-RITUAL-FINAL-FEASIBILITY-VERDICT | Final ritual feasibility verdict (§XII) | L5 | NO_POWER | status=COMPLETE, ritual_channel_readines | exact full, drift  |

## egyptian (14 instances)

| id | method | layer | outcome | verdict | power |
|---|---|---|---|---|---|
| EGY-01 | Egyptian non-Cretan correspondence corpus source-status +  | L0 | INCOMPLETE | verdict.py: status=INCOMPLETE, egyptian_ | unassessable (no f |
| EGY-02 | Calibration schema + inclusion rules + M0–M9 correspondenc | L0 | NOT_APPLICABLE | status=SPEC_FROZEN_AWAITING_CORPUS (sha  | NOT_APPLICABLE |
| EGY-03 | Hoch-1994 OCR auto-extraction of the calibration corpus (e | L0 | INCOMPLETE | verdict UNCHANGED: INCOMPLETE / NOT_READ | NOT_APPLICABLE (co |
| EGY-04 | Vision-reading of Hoch 1994 page images → hand-verified ca | L0 | SUPPORTED | gate status: INCOMPLETE(no corpus) → COR | adequate to fit (≥ |
| EGY-05 | M2 pooled-probabilistic correspondence model fit + held-ou | L6 | SUPPORTED | acceptance=PASS, beats_baselines=true (v | adequate at n=152; |
| EGY-06 | Matched-scarcity Linear-B positive control (§VII) — recove | L6 | SUPPORTED | control_verdict=PASS; min_detectable_anc | min detectable 2 a |
| EGY-07 | End-to-end null family — random-pairing / permuted-model / | L6 | SUPPORTED | specificity_ok=true; permissive_excessiv | NOT_APPLICABLE |
| EGY-08 | Transcription/sign-value uncertainty sensitivity (§IX) | L6 | SUPPORTED | verdict_reverses_under_uncertainty=false | stays ≫ null even  |
| EGY-09 | Egyptian-channel power envelope (§X) — minimum useful anch | L6 | SUPPORTED | min useful anchors=2; P(NO_POWER at K=3) | this IS the power  |
| EGY-10 | Mechanical gate readiness verdict (§XI) → COMPLETE / READY | L0 | SUPPORTED | status=COMPLETE, egyptian_channel_readin | min detectable 2 a |
| EGY-11 | REQ-01 Aegean-list apparatus determination via Bělohoubkov | L1 | INCOMPLETE | req01_status=ADVANCED_PROXIMATE_ONLY (no | NOT_APPLICABLE |
| EGY-12 | REQ-01 direct collation of Edel & Görg 2005 primary editio | L1 | SUPPORTED | REQ-01=CLOSED_PRIMARY_COLLATED; primary_ | NOT_APPLICABLE |
| EGY-13 | Cretan-anchor one-shot confirmatory preregistration (mint) | L6 | NOT_APPLICABLE | status=FROZEN_MINTED; plan_hash 2eab1536 | endpoint-clearabil |
| EGY-14 | Cretan-anchor one-shot confirmatory RUN — mechanical CONFI | L6 | NULL_PUBLISHED | pre-registered mechanical verdict = CONF | p-value establishe |

