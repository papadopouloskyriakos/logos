# I1 — Agnostic value-system search with relative constraints — FROZEN SPEC

**Task:** I1. **Seed:** 20260708. **Constitution:** v2.2. **As-of:** 2026-07-07.
**Claim layer of any output:** capped at L2/L3. No phonetic value is asserted; "values" are *abstract
relabeling-invariant slots*. This is a search *for* recoverable value structure, pre-registered to fail
CLOSED. Pre-registered BEFORE the search was run.

## 0. Question

Is there a **compact syllabic value system** — a factorisation of the Linear A sign inventory into a
consonant×vowel grid — that captures *real* phonotactic structure (i.e. predicts **held-out** Linear A
sign sequences better than a random factorisation of the same size), when the search space is pruned by
the campaign's relative constraints and **no** candidate language is committed to?

Given the standing campaign nulls (position→C/V REFUTED; substitution axis is word-INITIAL not consonantal;
seed-propagation a frequency artifact; cross-script transfer NULL; SEED_A=0; multi-view fusion no recovery),
the pre-registered expectation is **UNDERDETERMINED / NO_RECOVERY**. The value of the test is the *mechanical*
verdict + the *equivalence-class size* that quantifies the underdetermination. NO subjective meaningfulness
enters the objective at any point.

## 1. Value-system formalisation (agnostic, relabeling-invariant)

A **value system** φ = (φC, φV) assigns every *core* Linear A sign an abstract **consonant class**
φC(s) ∈ {0..|C|−1} and **vowel class** φV(s) ∈ {0..|V|−1}. The pair (φC(s),φV(s)) is the sign's *syllabic
value slot*. Classes are **abstract** — they are never mapped to phonemes; the identity of a class is only
its membership. This is what makes the system agnostic (no language) and relabeling-invariant.

- **Core signs:** the 55 Linear A conservative-syllabary signs with corpus frequency ≥ 10
  (`X.load_a()`, freq threshold frozen at 10). The 37 rarer signs are merged into one reserved
  class `RARE` (φC=RARE, φV=RARE) — a data-availability decision, not a hypothesis.
- **Boundary token** `BND` (word start/end) has reserved classes φC=BND, φV=BND.
- **Grid:** primary |C|=15, |V|=5 (matches the Linear B grid the script was borrowed from — the natural
  "cross-script-compatible" prior, itself under test). Sensitivity: |C| ∈ {12, 15, 18}, |V| fixed 5.

## 2. Generative model & the primary objective term (held-out, non-circular)

Each Linear A **word** (GORILA `stream` `t=='word'` unit, 2,462 words) is a string of syllable slots.
The value system induces a **factored bigram** model over slots:

  P(sylᵢ | sylᵢ₋₁) = P(cᵢ | cᵢ₋₁) · P(vᵢ | vᵢ₋₁),   with `^`…`$` boundaries.

If φ captures real phonology (vowel harmony, consonant co-occurrence restrictions), the *factored*
C-model and V-model share statistical strength across signs in the same row/column and therefore predict
**held-out** words better than a random factorisation of identical grid size. The C/V transition tables
are estimated on TRAIN words (add-α = 0.5 smoothing); the score is the mean per-token held-out
log-likelihood (nats):

  **seqLL(φ)** = (1/N_test-tokens) Σ_test-bigrams count[a,b]·( logP_C[φC(a),φC(b)] + logP_V[φV(a),φV(b)] ).

**Non-circularity (Art. XII):** every input to seqLL is a pure distributional statistic over sign
*identities*. Known Linear B values are NEVER a model input — they are used only to GRADE the winner
(§6) and to define the cross-script constraint diagnostic. Held-out words never inform table fits.

**Split (leakage gate, Art. IX):** words grouped by inscription id; fixed grouped 80/20 train/test
(seed 20260708). ALL comparisons (search, nulls, controls) use the identical split. Winner robustness =
5-fold grouped CV of seqLL.

## 3. Relative-constraint terms (SPACE-REDUCING GUIDES, never deciders)

Small additive bonuses with FROZEN weights, each normalised to [0,1], scaled ≪ the natural nats/token
scale of seqLL so they can only break near-ties (Constitution truth-layer cap: structure guides, held-out
prediction decides). All are TRAIN-side / structure-only:

- **relAgree** (C4 substitution graph): over the 12 strong substitution edges, max(sameV-fraction,
  sameC-fraction) — rewards substitution neighbours sharing *some* phonological dimension.
- **formConsist** (E2 formula grammar): 1 if φC(KU)==φC(KI) (KU-RO/KI-RO paradigm ⇒ shared consonant,
  contrasting vowel), else 0.
- **morphCompat** (A- prefixation / affix paradigm): 1 − normalised entropy of the C-class distribution
  of the PREFIX_EDGE sign set — rewards the productive word-initial affix signs concentrating in few
  consonant classes (coherent morphology).
- **crossCompat** (cross-script): Rand-index agreement, on the 58 CV-parseable AB signs, between φ's
  same-vowel relation and Linear B's TRUE same-vowel relation. This is the cross-script-compatibility
  constraint AND a diagnostic; per the campaign's cross-script NULL it is expected ≈ chance.

**FROZEN objective:**  O(φ) = 1.0·seqLL(φ) + 0.01·relAgree + 0.01·formConsist + 0.01·morphCompat +
0.01·crossCompat. (Anchor-consistency term = 0: SEED_A=0, no secure anchors — recorded, contributes
nothing.) Parameter cost is constant within a grid (assignment map = 55·log2(|C|·|V|) bits) so it does
not affect within-grid ranking; it is charged across grids in the MDL grid selection (§6).

## 4. Search — two methods (Art. VII complete receipt)

- **Method A — best-first / beam coordinate ascent:** 24 random restarts; each does coordinate-ascent
  sweeps (reassign every sign to its objective-argmax cell given the rest) to convergence (≤30 sweeps).
  Track the top-50 distinct optima (beam).
- **Method B — Bayesian / MCMC (simulated annealing Metropolis):** 40 chains × 20,000 single-sign
  reassignment steps, geometric cooling T:1.0→0.02. Record every visited state within ε=0.01 nats of the
  global best (the effective posterior support / equivalence spread).

Total distinct systems evaluated is logged for the multiplicity penalty.

## 5. Nulls & controls (fail-CLOSED)

- **N1 random-φ null (best-of-N):** 20,000 random φ on the SAME grid & split → full seqLL distribution +
  best-of-N ceiling (the false-graduation ceiling, the campaign's gate-calibration logic).
- **N2 permuted-corpus null:** shuffle sign tokens within word positions (preserve word lengths + unigram
  marginals, destroy bigram phonotactics); rerun search + random null. If the real-corpus search gain over
  random-φ is NOT materially larger than the permuted-corpus gain, the "structure" is a marginal artifact.
- **C1 Linear B positive control:** identical pipeline on `X.load_b_damos()` words (|C|=15,|V|=5). The
  detector MUST fire here (Linear B has a true CV grid) and the winner's V-partition should align with the
  true Linear B vowels (AMI, permutation-tested) — proving the search is a live detector, not dead.

## 6. FROZEN mechanical verdict

`VALUE_STRUCTURE_RECOVERED` iff ALL of:
  (a) searched best seqLL > 99th percentile of the N1 random-φ null, AND
  (b) real-corpus gain (best − median null) > 2 × permuted-corpus gain (N2), AND
  (c) winner's V-partition aligns with Linear B vowels on AB signs above its own label-permutation null
      (AMI perm-p < 0.05).
Otherwise `UNDERDETERMINED_NO_RECOVERY`. The LB control (C1) is a detector-liveness gate: if C1 fails to
fire, the whole apparatus is reported NO_POWER instead. Grid selection across |C| is by MDL
(model bits + assignment bits + held-out data bits); the primary grid is |C|=15.

## 7. Equivalence classes (Art. V degeneracy accounting)

seqLL and every objective term are invariant under: (i) permuting C-class labels (|C|!), (ii) permuting
V-class labels (|V|!), (iii) permuting signs that occupy an identical cell (homophones, Π_cell n_cell!),
(iv) synonymous class→phoneme relabelings (subsumed by i,ii). The **symmetry-orbit size** of the winner
is |C|!·|V|!·Π_cell n_cell!. The **empirical** underdetermination = number of *relabeling-distinct*
systems within ε=0.01 nats of the best (MCMC posterior support). Both are reported in
`I_EQUIVALENCE_CLASSES.md`.

## 8. Outputs
`data/I1_agnostic.json` (all numbers), `reports/I_AGNOSTIC_SEARCH_RESULTS.md`,
`reports/I_EQUIVALENCE_CLASSES.md`. No git commit (orchestrator commits centrally).
