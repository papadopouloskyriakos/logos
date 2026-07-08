# EPOCH-016 — Simulation-based inference pilot (known-script calibration only)

**Frontier F9 (gate A) · prereg frozen 2026-07-08T12:35:48Z ·
plan_hash `a15faa74…6efe0a77d` (= sha256 of prereg.md) · script sha256
`520bc4e7…d36efe0a77d` matches the frozen hash · seed 20260708 · claim ceiling L2
(relative/structural, gauge-invariant value-CLASS recovery — no absolute value, no language).
**Linear A is never loaded by `scripts/e016_sbi_pilot.py`** (grep-verified: the only LA-derived
quantity anywhere in the script is the scalar `LA_TOKEN_SCALE = 5792`, pre-declared in the
prereg). No LA claim can emerge from this epoch by construction.**

## Question

Can an amortized SBI estimator — a neural pair-posterior trained entirely on a generative
admin-syllabary *simulator* (never on real language) — recover sign VALUE-CLASS structure
(consonant-row / vowel-column membership, scored by ARI, gauge-invariant) on an opaque **known**
script degraded to Linear A's token scale, at the same anchor budgets (0/3/5) where the G-surface
anchor-geometry solvers (E003 seed-poverty surface, E006 GW estimator) hit the floor? This is a
new-architecture pilot (frontier F9), calibration-only: an LA application would need its own
prereg.

## Design (frozen, zero tuning)

Generative simulator over an opaque C×V grid (10–14 consonant rows × 4–5 vowel columns),
parameters drawn from a prior matched to LA/LB measured aggregate statistics (Zipf slopes,
word-length, site imbalance, formula rate — see prereg §1; no sign identities used). Two
sklearn MLP pair-classifiers (P(same row), P(same col)) trained on 200 simulations →
292,352 labeled sign-pairs, feed a spectral-clustering value-class decoder (oracle k, granted
equally to every method). Benchmark = `load_b_damos()` restricted to the 59 core CV-grid signs
(97.7% of tokens), truncated to LA's measured 5,792-token scale, R=20 seeded replicates.
Baselines at matched anchor budgets, same kept signs, same oracle k: **BASE_SPEC** (raw
2nd-order-cosine spectral clustering — the "no-SBI" distributional-geometry stand-in),
**BASE_M1** (b>0 only; anchor-profile k-means, the E003 G-surface estimator analogue),
**BASE_GW** (entropic Gromov–Wasserstein to an idealized grid template, the E006-best estimator
analogue). Primary endpoint: paired per-replicate ARI_C(SBI) − max(baselines), sign-flip
permutation (10,000), Holm over 3 budgets. Full spec: `epochs/EPOCH-016/prereg.md`.

**Reproducibility check:** the frozen script was re-executed end-to-end after the first run;
every number in the two `result.json` files (all controls, all LB cells, all verdicts) is
byte-identical except wall-clock (`167.1s` vs `168.5s`) — the seeded design is fully
deterministic.

## Controls (run first, in the frozen order) — PASS on all three gates

| Control | Result | Bar | Gate |
|---|---|---|---|
| **PC-A** (ample, 5×LA scale, b=0, 20 held-out true-prior sims) | mean ARI_C **0.6846**, ARI_V 0.3362, pair-AUC 0.908 | ≥0.40 | **PASS** |
| PC-B (LA scale, b=0, in-distribution) | mean ARI_C 0.318, ARI_V 0.213, pair-AUC 0.804 | descriptive | reported |
| **NEG** (structure-free painted labels, b=5, 20 sims) | mean ARI_C −0.001, perm p=.852 | \|mean\|<0.05 → PASS | **PASS, no leak** |
| **MISSPEC** (wrong-prior SBI on true-prior LA-scale held-out) | ARI drop **0.074** (0.318→0.244), OOD flag frac 0.05 | drop<0.10 → ROBUST | **ROBUST** |
| Global miscalibration override | — | — | **false** (SBI_MISCALIBRATED = NO) |

Training diagnostics: insample pair-AUC_C 0.838 / AUC_V 0.630 on 292,352 pairs; base rates
same-row 6.5%, same-col 20.6% (heavy class imbalance — the AUCs, not raw accuracy, are the
honest readout).

## Verdict cells — opaque Linear B at LA token scale (R=20 replicates)

| Anchors (b) | SBI | SPEC | M1 | GW | mean diff (SBI−best base) | raw p | Holm p | **Verdict** |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.0710 | **0.0868** | — | 0.0065 | −0.0158 | .177 | .353 | **SBI_MATCHES** |
| 3 | 0.0663 | **0.0734** | 0.0256 | 0.0328 | −0.0135 | .220 | .353 | **SBI_MATCHES** |
| 5 | 0.0557 | **0.0636** | 0.0277 | 0.0381 | −0.0198 | **.010** | **.030** | **SBI_MATCHES*** |

\* At b=5 the underperformance is Holm-significant (p=.030<.05) but its magnitude (−0.0198) does
**not** clear the preregistered ±0.05 material margin — the frozen rule (`d≤−0.05 AND p<.05`
for UNDERPERFORMS) correctly resolves this to MATCHES. Read honestly: at b=5, SBI's shortfall
vs the raw-cosine baseline is statistically detectable but *sub-material*.

**Mechanical verdict (all three budgets, frozen rule): `SBI_MATCHES`. Global miscalibration
override: false.** This is exactly the preregistered modal prediction (p=0.35).

## Reading the numbers honestly (not a verdict, but load-bearing)

1. **BASE_SPEC — plain raw-cosine spectral clustering with no learning at all — is the single
   best method at every anchor budget tested**, including against SBI's trained neural
   pair-posterior. SBI never loses by a material margin, but it never wins either; its learned
   12-feature combination adds nothing measurable over 2nd-order cosine at LA's scale on real
   (degraded) language.
2. **Anchor budgets 0→3→5 do not help — mean ARI_C mildly *declines* for SPEC and SBI as budget
   rises** (0.087→0.073→0.064 for SPEC; 0.071→0.066→0.056 for SBI), confirming sub-prediction
   (ii) but for an unflattering reason: ARI_C is scored on non-anchor signs only, so pulling
   more high-frequency signs out as anchors leaves the harder low-frequency remainder to score.
   Five LA-realistic anchors are not doing constructive work for any method here — consistent
   with E003's "the bottleneck is the anchor-profile *geometry*, not seed count" finding, now
   independently reproduced under a completely different estimator family.
3. **BASE_M1 (the E003 G-surface analogue) is confirmed the weakest baseline** at b=3 (0.0256)
   and b=5 (0.0277) — in the same order of magnitude as E003's own quoted M1 floor (.039,
   different metric/methodology, same qualitative story): anchor-profile geometry is
   structurally the weakest of the four channels tried here, not just under the G-surface's
   own machinery.
4. **The sim-to-real gap is large and this is the epoch's most important honest number.**
   PC-B (in-distribution, true generative process, LA scale) gets ARI_C=0.318 — a working
   pipeline with real power. Real degraded LB at b=0 gets ARI_C=0.071 for SBI (0.087 for the
   best baseline) — a **~4–5× drop** the moment the corpus is genuine language instead of a
   draw from the simulator's own prior. The simulator, however good its aggregate-statistic
   matching, is not capturing whatever structure actually carries consonant-row information in
   real degraded language at this scale.
5. **Sub-prediction (iv) is REFUTED, not confirmed, and that refutation cuts against the
   simulator's honesty, not for it.** Predicted: real LB flagged out-of-distribution in ≥50% of
   replicates (p=.55 — "real language ≠ simulator"). Observed: **0/20 (flag_frac=0.0)** — every
   real-LB replicate's OOD statistic (0.802–0.833) sits below the true-prior threshold (0.848).
   Combined with the misspec control's low flag rate under an *actively wrong* prior (0.05, i.e.
   1/20) even though the wrong-prior training was disjoint from the true prior by design, the
   single-scalar median-|z| OOD detector used here has **low discriminative power overall** —
   it is not simply that the simulator matches real language well; the detector itself may be
   too coarse to catch the mismatches that matter. This is a caveat on the MISSPEC "ROBUST"
   read: a wrong-prior model degrading only mildly *and* being hard to flag as OOD is a weaker
   form of robustness than a model that is provably being stress-tested by a sensitive detector.

## Bearing on frontier F9 (new optimization architectures)

**No support gained for SBI as an architecture upgrade over the existing G-surface machinery at
LA's operating scale.** The pilot's own positive control shows the estimator has real power
in-distribution (0.68 at ample scale, 0.32 at LA scale) — this is not a dead pipeline — but on
the actual benchmark (real, if opaque, language) it ties the simplest possible baseline
(raw cosine + spectral clustering) at every anchor budget and never exceeds it by a material
margin. Given BASE_SPEC needs no simulator, no training, and no generative-model design
assumptions at all, **SBI buys nothing here that plain distributional geometry didn't already
have**, while adding a large new assumption surface (the simulator's parametric form) whose
sim-to-real gap (finding 4) is exactly the kind of hidden fragility Article XI/XII exist to
catch before it reaches Linear A. F9 stays ACTIVE but this specific architecture is not a
promising next investment at current corpus scale; see successors below for what might change
that.

## Multiplicity / effective_n (Art. VIII)

3 verdict comparisons (anchor budgets) × 1 primary endpoint (ARI_C), Holm-corrected, 20 paired
replicates each; exactly the preregistered space, zero post-hoc threshold or metric selection
entered the verdict. Vowel-column ARI is reported (mean_diff_V column, always positive and
small — SBI mildly *ahead* on the never-verdict-bearing secondary axis, consistent with vowel
columns being the easier 5-way vs 13-way discrimination) but is explicitly non-verdict-bearing
per the frozen prereg. Search receipt: 1 configuration, zero hyperparameter search.

## Compliance

Art. V (claim layer L2 throughout; no value, no language, no LA touched — grep-verified). VII
(search receipt: exactly the preregistered metric/budget/method space; the b=5 Holm-significant
sub-material shortfall is reported, not suppressed). VIII (Holm over 3 budgets; 20 paired
replicates; effective_n = replicates). IX (compute: 168.5s wall, well under the 30-min budget;
token/sim budgets frozen in prereg). XI/XII (simulator built from aggregate statistics only, no
LB sign identity or LA data in its design; ground truth read only by the scorer; oracle k
granted equally; nothing graded here was produced by the rule that grades it — LA is provably
absent from the script). XV (no transfer licence earned or touched; SEMANTIC+ remains
NOT_AUTHORIZED). XVII (append-only; this epoch neither supersedes nor is contradicted by any
prior epoch — it independently reproduces the E003 anchor-geometry-is-the-bottleneck finding
under a disjoint estimator family, which strengthens rather than revises it). XVIII (no formal
A1–A5 assumption set declared beyond the non-circular contract in the prereg — none of the
epoch's numbers depend on an unstated assumption). XXII (this line). Verdict computed by the
frozen rule in `scripts/e016_sbi_pilot.py`; run reproduced byte-identically
(`epochs/EPOCH-016/run.log`, `data/sbi_pilot/E016_result.json` = `epochs/EPOCH-016/result.json`).

## Successors

1. **Diagnose the sim-to-real gap directly** (finding 4): ablate the simulator's plantable
   signals (harmony, paradigm alternants, formula headers) one at a time against real LB to find
   which real-language structure the simulator is failing to reproduce — the 0.32→0.07 collapse
   is the single most informative number this pilot produced and it is currently unexplained.
2. **Feature-importance audit of the trained MLP** (permutation importance on the 12 pairwise
   features) to see whether SBI is *only* re-deriving 2nd-order cosine internally (which would
   fully explain why it ties BASE_SPEC) or whether the minimal-pair / position features carry
   independent weight that the LB benchmark simply can't exploit at this token scale.
3. **Sharpen the OOD detector** (finding 5): the current single-scalar median-|z| statistic
   flags neither real LB nor an actively-misspecified prior at a useful rate; a multivariate or
   per-feature OOD test is needed before any OOD gate here can be trusted as a safety net for a
   future LA application.
4. **Scale-up power curve for BASE_SPEC specifically** (not SBI): given raw cosine is the
   pilot's actual best performer, cheaply sweep corpus scale 1×–10×LA to see whether it, unlike
   the G-surface estimators (E003: no finite budget helps below LOO(46)), has a viable
   corpus-scale path — this reframes "does more data help" around the winning method, not SBI.
5. **Re-run with a richer feature set exploiting formula-position structure** (E002's
   substitution-motif geometry, which DID Holm-survive on KNOWN LB↔Cypriot) as SBI training
   features instead of/alongside the 12 generic ones — the current features are largely what
   BASE_SPEC already computes; motif-context features are the one channel in this campaign that
   has beaten a flat/raw baseline before.
6. **Joint C+V decoding** instead of two independent classifiers — the current pipeline trains
   row and column posteriors separately; a joint (row,col) cell classifier might recover
   structure the marginal decomposition discards, and would also make the secondary vowel-column
   endpoint verdict-bearing in a future prereg.
7. **Any LA application of SBI requires its own prereg AND a resolved finding-4 diagnosis
   first** — running this exact pipeline on LA today would only certify a method that ties a
   trivial baseline on real language it was calibrated against; that is not a result worth
   spending LA's one-shot search receipt on.
