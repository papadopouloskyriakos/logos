# EPOCH-015 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F4** (gate A) — segmentation-marginalized morphology.
**Epoch question:** Prior LA morphology froze ONE segmentation (GORILA words) and then induced affixes.
Does JOINT treatment — word boundaries as LATENT with a calibrated probabilistic boundary distribution,
affix induction by MARGINALIZING over sampled segmentations — beat frozen-single-segmentation induction
where truth is known (opaque LB; synthetic admin syllabary), and does LA's one validated affix
(A- prefixation) become MORE or LESS robust when segmentation uncertainty is integrated? Do any NEW
LA affix candidates survive the frequency-matched null + Holm under marginalization?
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Substantive gate:** A. **Claim ceiling:** L2/L3 (structure/affix-as-functional-slot). No language named;
no phonetic value is an input; sign names (A, JA, …) are GORILA/DĀMOS transliteration labels used as
anonymous identities.
**Articles triggered:** V (wording capped at L2/L3), VII (full candidate/threshold space enumerated here;
nothing selected post hoc), VIII (effective_n = documents; multiplicity = Holm over the frozen LA scan
family; the A- test is a single preregistered confirmatory test), IX (info budget: word/sign token counts
on every claim), XI (source-dependency: boundary model inputs are unsupervised distributional statistics +
physical layout marks; GORILA word units enter ONLY as the frozen comparator arm and the LA mark
positions; DĀMOS gold boundaries enter ONLY as LB calibration/grading labels), XII (the LB gold affix
inventory is derived from GOLD boundaries; candidate inventories are derived from INDUCED boundaries —
the rule is shared but the graded information differs, so no target is graded by the rule that created
it from the same inputs; the wrong-structure null makes this operational), XV (no licence touched),
XVII (append-only; deviations logged in result.json), XVIII (assumptions A1–A6), XXII (this header).

## Prior art cited + differenced (do-not-repeat check)

- **Relphono campaign (CLOSED):** B3 validated unsupervised segmentation families on opaque LB
  (cue TP-min, branching entropy, Bayesian, MDL, FST); B4 proved any LA segmentation is an over-cut
  superset (~0 skill over cut-everywhere); B5 built a probabilistic boundary ensemble for LA; E1 induced
  morphology on FROZEN segmentations and validated A- prefixation (adaptive p .008). **Difference:**
  E015 runs the never-run joint step — affix statistics are EXPECTATIONS over boundary samples, never conditioned
  on one segmentation; nulls are marginalized the same way (paired sample↔null replicates).
- **Methodology inventory:** segmentation-marginalized (latent-boundary) morphology is not among the 214
  catalogued instances; nearest lineage = frozen-segmentation morphology (E1) + boundary ensembles (B5).
- **Segmentation-extension memory:** micro-F1 has an all-boundaries ceiling — cut rates are REPORTED for
  every arm so gains cannot be a cut-everywhere artifact.

## Data (frozen; pre-freeze audit was counts-only)

- **LB (calibration + positive control):** DĀMOS `corpus/bronze/linearb/damos/items.jsonl`, tablets =
  documents with ≥2 syllabic wordforms via `scripts.cross_script.data._damos_wordforms`:
  2,202 tablets / 11,908 words / 39,005 sign tokens. Opaque streams = per-tablet concatenation of
  wordforms in reading order; gold gaps at word ends. 70/30 tablet split, seeded (20260708):
  ensemble statistics + calibration on TRAIN only; affix recovery graded on TEST only.
- **LA (application):** `corpus/silver/inscriptions_structured.json`, docs with ≥2 signs:
  618 docs / 5,069 sign tokens / 2,424 GORILA words (1,806 internal word-word gaps, of which 1,631
  carry a physical mark div/num/nl/other and 175 are unmarked/editorial).
- **Synthetic (control 2):** generated per §Synthetic below; no real-corpus content.

## Boundary-probability model (frozen)

Per inter-sign gap g in a stream, three parameter-free unsupervised cue features (B3-validated
families, re-implemented self-contained):
  f1 = forward branching-entropy increase at g (Tanaka-Ishii rule, forward side, context depth ≤ 5,
       min context support 3), f2 = backward branching-entropy increase, f3 = forward transitional-
       probability local minimum (Saffran/Harris).
Feature cell c(g) ∈ {0,1}³ (8 cells). **Calibration:** P(boundary | cell) estimated on LB TRAIN gold
gaps with add-1 smoothing. Boundary distribution = independent Bernoulli per gap at the cell probability.
- **LA transfer (assumption A2):** LA gap probabilities use the LB-calibrated cell map, with cue
  statistics (entropy tries, TP) re-estimated unsupervised on ALL LA streams.
- **Layout marks (LA only, assumption A3):** any gap that is a GORILA word-word gap whose intervening
  stream material contains div/num/nl/other gets p(g) := max(p_cell, P_MARK), **P_MARK = 0.9**;
  sensitivity re-run at P_MARK ∈ {0.7, 1.0} (reported, non-gating). Unmarked GORILA boundaries get NO
  boost (they are editorial, not physical).
- **Frozen-single baseline (the comparator):** two deterministic thresholdings, FROZEN_MAP (cut iff
  p > 0.5) and FROZEN_MEAN (cut iff p > mean of p over all gaps of that corpus); the comparator arm is
  whichever has higher gold-boundary F1 on LB TRAIN (chosen on TRAIN, frozen before TEST; strengthens
  the baseline). The SAME chosen rule is used on synthetic and LA.
- **Marginalization:** K = 20 seeded boundary samples; statistic = mean over samples; nulls paired
  (below). Marginalized inventory replicated with 3 sampling seeds (20260708/+1/+2) for stability.

## Affix induction + inventory rule R (frozen; identical in every arm)

Words = segments of a segmentation. Only words with ≥2 signs count. For sign s:
prefix productivity = #distinct RECURRENT stems t with (s)+t attested (recurrent = t is a free word or
the single-sign-affix residual of ≥2 words — the relphono E1 paradigm criterion); suffix symmetric.
- **Candidate universe U (per corpus):** signs with ≥ MIN_ATT = 10 attestations word-initially
  (prefix candidates) / word-finally (suffix candidates) on the REFERENCE word list (LB: gold TEST
  words; synthetic: gold words; LA: GORILA words — frozen so U cannot drift with the segmentation).
- **Null:** frequency-matched i.i.d. null (E1): synthetic corpora matched to the word-length profile +
  sign-unigram of the word list under test; one-sided p = (1 + #{null ≥ obs}) / (1 + n_null).
- **Inventory rule R:** (s, POS) ∈ inventory iff p ≤ 0.01 with n_null = 200 (gold/frozen arms).
- **Marginalized R:** obs = mean_k productivity on sample k; null replicate j = mean_k productivity on
  a fresh matched synthetic corpus for sample k (n_null = 200 replicates × K = 20 samples).
- If a sign has <2 qualifying attestations in an induced arm, its decision is "not affix" (no skip).

## Controls (run FIRST, in this order)

- **PC-LB (positive control, gates the verdict):** on LB TEST opaque streams: gold inventory
  G = R(gold TEST words). Arms: FROZEN (chosen rule) and MARG (K=20). Recovery scored on U:
  precision/recall/F1 of predicted inventory vs G.
- **Wrong-structure null (must collapse):** signs shuffled WITHIN each gold word (seeded), streams
  rebuilt, FULL pipeline re-run (cues re-estimated on shuffled TRAIN, calibration re-fit, both arms
  induced on shuffled TEST), scored against the REAL G. Machinery is informative iff
  F1_frozen(real) > F1_frozen(wrong) AND F1_marg(real) > F1_marg(wrong).
- **Synthetic control (graceful-degradation):** admin syllabary V = 60 CV signs; stem types Zipf(1.1),
  stem length 2–4; affixes = 4 reserved-but-reusable signs: prefix P1 attach .25; suffixes S1 .30,
  S2 .15, S3 .08 (exclusive draws); documents of 2–8 words; token budget 1,200 words per corpus;
  hapax regimes via stem-type inventory N_stem ∈ {150, 600, 2400}; 5 seeds per regime; 70/30 split,
  calibration on synthetic TRAIN gold. Gold affix set = the 4 planted (sign, POS) pairs; F1 on the
  synthetic U. **Graceful iff** mean ΔF1(MARG − FROZEN) ≥ 0 at the most hapax-heavy regime (N_stem=2400).

## LA tests (frozen)

1. **A- confirmatory (single preregistered test, no Holm):** A word-initial prefix productivity + its
   freq-matched null p (n_null = 2,000) under three arms: (a) GORILA-frozen words (replication anchor),
   (b) FROZEN induced segmentation, (c) MARGINALIZED (K=20, paired nulls, n_null = 2,000).
   **A- is ROBUST_UNDER_MARGINALIZATION iff p_c ≤ 0.05.** Direction: IMPROVES if p_c ≤ p_b,
   DEGRADES if p_c > p_b (reported with productivities and null means).
2. **Exploratory scan (Holm):** candidates = U(LA GORILA): word-initial signs ≥10 attestations
   (32, minus A → 31) + word-final ≥10 (40) → **family of 71 tests**, marginalized statistic,
   n_null = 2,000, Holm at α = 0.05. Survivors = NEW affix candidates (reported with frozen-GORILA
   p for comparison; a survivor is only claimed L2/L3 "productive positional slot").

## Mechanical verdict (frozen rule)

Primary (from PC-LB, gated by the wrong-structure control):
- **MARGINALIZATION_IMPROVES** iff ΔF1 = F1_marg − F1_frozen > 0 AND exact two-sided McNemar
  (binomial on discordant candidate classifications vs G over U) p ≤ 0.05 AND all 3 sampling-seed
  replicates give ΔF1 > 0.
- **MARGINALIZATION_DEGRADES** iff the mirrored conditions hold (ΔF1 < 0, McNemar p ≤ 0.05, all
  replicates < 0).
- **MARGINALIZATION_NEUTRAL** otherwise.
If the wrong-structure control fails to collapse (either arm's real F1 ≤ its wrong-structure F1),
verdict = MACHINERY_UNINFORMATIVE and no LA interpretation is made (LA numbers still reported).
Secondary (reported, not the primary verdict): synthetic graceful/not; A- robust/not + direction;
scan survivors with null stats. Cut rates reported for every arm (all-boundaries-ceiling guard).

## Assumptions (register)

- **A1** DĀMOS wordform extraction (`_damos_wordforms`) yields reading-order streams; word-internal
  sign order faithful. (Inherited from B3/E1; unchanged.)
- **A2** LB→LA calibration transfer: the cell→probability map estimated on LB gold transfers to LA
  cue statistics. Untestable on LA (no gold); mitigated by the P_MARK mark channel + sensitivity runs.
- **A3** Physical layout marks (div/num/nl/other) are boundary evidence with reliability P_MARK = 0.9.
- **A4** Independent-Bernoulli gap sampling (no boundary–boundary interaction). Known simplification;
  the synthetic control measures its cost where truth is known.
- **A5** Frequency-matched i.i.d. null is the correct chance model for recurrent-stem productivity
  (inherited from relphono E1, where it was adaptive-null-validated for A-).
- **A6** MIN_ATT = 10, p ≤ 0.01 inventory rule, K = 20, n_null as stated — all frozen here; no
  post-hoc retuning. Any deviation → logged in result.json deviations[].

## Outputs

`epochs/EPOCH-015/{prereg.md,plan_hash.txt,result.json}`,
`reports/EPOCH015_MARGINALIZED_MORPHOLOGY.md`, `data/marginalized_morph/*` (all arms' inventories,
per-candidate stats, calibration table, synthetic curves), scripts `scripts/e015_*.py`.
