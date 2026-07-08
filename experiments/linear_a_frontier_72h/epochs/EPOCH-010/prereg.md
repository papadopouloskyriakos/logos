# EPOCH-010 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F3** (substitution-neighborhood bridges v3)
**Epoch question:** CHANNEL-CAPACITY BOUND + ENSEMBLE + HUB ANCHORS — close or reopen the
E003/E006 door definitively. On the KNOWN LB-cog↔Cypriot-cog pair: (1) does ANY
estimator-free capacity bound at b=5 seeds exceed the required Holm-surviving hit rate
(~0.119–0.14 depending on held-out size)? (2) can decorrelated-error fusion of
{M1, EST_GW, EST_OT} cross the bar without new information? (3) do frequency/centrality-
stratified 5-seed draws (LA's real anchors are high-frequency toponyms) beat uniform draws?
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08T04:46Z
**Substantive gates:** A/G.
**Articles triggered:** V (claim layers), VII (search receipt), VIII (effective_n + multiplicity),
IX (info budget), XI/XII (non-circularity), XV (transfer licences: nothing here earns a value),
XXII (stage header).
**Claim layer of ANY result here: L2 (relative/structural), calibrated on KNOWN scripts
(LB, Cypriot) + CTRL identity pair. No Linear A data is touched. No licence can change.**

## Non-circular contract (Art. XI/XII)

Identical to E002/E003/E006: all similarity matrices are MF_A trigram-frame cofill-Jaccard
built from sign IDENTITY + word co-occurrence only; known values are read AFTERWARD to define
GT pairs and GRADE. Alignment operates on opaque per-script sign lists with target order
shuffled (seeded). ORACLE probes deliberately leak ground truth INTO THE DECISION FUNCTION —
they are labelled as bounds, can only make DOOR_CLOSED harder to reach (conservative
direction), and can never REOPEN the door (only honest, realizable Holm-surviving cells can).

## Data / units (frozen; identical to E003/E006, same RNG streams)

- KNOWN pair = LB-cog ↔ Cypriot-cog, full-corpus alignable n=47; CTRL = LB-DĀMOS split-half
  identity pair, n=71 (MIN_SUP=3, `f_bridge_common` loaders, E003 problem construction).
- Corpus subsampling / target-shuffle / uniform seed draws / wrong-seed injection reuse
  E003's exact deterministic streams (`e003_seed_poverty.rng_for` keys
  (pair,"corpus",f,d), (pair,"shuffle",f,d), (pair,"seeds",f,d,b,rep)) so every uniform-seed
  replicate is REPLICATE-PAIRED with E003's M1 and E006's estimator cells.
- New streams (this epoch only): ("cap_null",probe,f,d,rep), ("cap_scramble",f,d,rep),
  ("ens_null",method,f,d,rep), ("hub_seeds",strat,f,d,rep), ("hub_null",strat,est,f,d,rep),
  ("hub_adv_seeds",...)/("hub_adv_null",...), ("ens_adv_seeds",rep)/("ens_adv_null",rep).
- b=5 everywhere (LA's firm seed budget); f ∈ {0.75 (LA operating point, 5 draws × 4 reps),
  1.0 (1 draw × 20 reps)}; R=20 reps/cell; N_PERM=1000; MIN_HELDOUT=10; predictions over ALL
  n target columns (E003 convention). Machinery reused read-only: `e002_motif_common.py`,
  `e003_seed_poverty.py`, `e006_seed_efficient.py` (est_gw, est_ot), `f2_cross_script_bridge.py`.

## Required rate (frozen mechanical definition)

Per replicate: from the SAME 1000-permutation null-count distribution used to grade that
replicate's predictions, c_req = smallest integer c with #(null_counts ≥ c) ≤ 3 (i.e. perm-p
≤ 0.0041667 = 0.05/12, the inherited E002 Holm-12 per-test bar). required_rate_rep =
c_req / n_heldout. E003's headline 5/42 = 0.119 (b=5, f=1.0) is the sanity reference.

## Part 1 — CHANNEL-CAPACITY probes (KNOWN, b=5, f ∈ {0.75, 1.0}, 20 reps each)

Feature span per replicate: X = Ss[:, s_seed] (source profiles restricted to the 5 drawn
seeds), Y = St[:, t_seed] (target profiles restricted to the 5 true counterpart columns).
Held-out rows = non-seed signs; candidates = all n target columns.

Verdict-bearing probes (each → per-rep exact accuracy; margin_rep = acc − c_req/H;
probe **EXCEEDS** iff median(margin) ≥ 0 over valid reps):

1. **CAP_ORACLE_LIN** (oracle-feature probe): per-script column z-scoring of X and Y (no GT);
   ridge map W = (XᵀX + 0.01·n·I)⁻¹XᵀY fit on ALL n true pairs INCLUDING held-out
   (deliberate leakage = upper bound for any linear metric on the seed span);
   cost = ‖x_iW − y_j‖; accuracy = max(argmin-acc, Hungarian-acc) per rep.
2. **CAP_ORACLE_CCA** (oracle-feature probe): CCA fit on all n true pairs (reg 1e-6, all 5
   components, canonical corrs clipped to ≤0.999); cost = ‖diag(ρ)(x_iWx) − diag(ρ)(y_jWy)‖;
   accuracy = max(argmin, Hungarian).
3. **CAP_BEST_BATTERY** (oracle SELECTION, honest rules): 5 metrics {raw-L2, rownorm-L2 (=M1),
   cosine, colz-L2, Spearman} × {argmin, Hungarian} = 10 rules, none uses GT in the decision;
   accuracy = per-rep MAX over the 10 (selection envelope).
4. **CAP_ORACLE_PICK3** (ensemble ceiling): per held-out sign, correct iff ANY of
   {M1, EST_GW, EST_OT} (E006 frozen implementations, same anchors) predicts it correctly —
   the union bound for any selection-fusion of the three.

Report-only (cannot bear the verdict; declared): **CAP_FANO** — Gaussian-CCA mutual
information I = −½Σln(1−ρ_k²) between held-out X rows and their TRUE Y rows; Fano converse
acc ≤ (I + ln2)/lnH. Known to be loose at H≈36–66 (I=0 already gives ≈0.19 > required), so it
can never close the door by itself; recorded because the epoch task names it.

**Capacity verdict (KNOWN, b=5, f=0.75 = LA operating point):**
CAPACITY_EXCEEDS iff ≥1 valid verdict-bearing probe EXCEEDS; else CAPACITY_BELOW_REQUIRED.
f=1.0 reported alongside (descriptive).

### Capacity controls

- **PC_CAP (positive, gating)**: CTRL identity pair, b=5, f=1.0, 20 reps: CAP_ORACLE_LIN and
  CAP_BEST_BATTERY must both EXCEED (realizable M1 already achieves 0.112 there vs required
  ≈0.076–0.09). Either failing → capacity machinery NO_POWER → DOOR_CLOSED unavailable this
  epoch (verdict can then only be REOPENED or MARGINAL).
- **NEG_CAP (overfit control, per-probe validity)**: KNOWN b=5 f=1.0, 20 reps, ground truth
  SCRAMBLED by a seeded permutation (("cap_scramble",f,d,rep)); oracle probes re-fit on the
  scrambled pairs. A probe with median(margin) ≥ 0 on scrambled GT is **OVERFIT_BROKEN**:
  excluded from the verdict-bearing set (reported). If ALL of {LIN, CCA, BATTERY, PICK3} are
  OVERFIT_BROKEN → capacity verdict NO_POWER (DOOR_CLOSED unavailable).

## Part 2 — ENSEMBLE cells (claim-bearing)

KNOWN, b=5, uniform seeds (E003 streams), f ∈ {0.75, 1.0}, 20 reps. Per replicate compute the
three cost matrices {M1, EST_GW, EST_OT}; FIRST report error-structure descriptives: per-method
acc, pairwise error-set Jaccard (wrong-prediction index sets), 3-way overlap, PICK3 union.
Then two frozen fusions, each graded exactly like E003 (exact count on held-out, 1000-perm
null, ("ens_null",method,f,d,rep)):

- **ENS_RANK**: per row, rankdata each method's cost; fused cost = mean rank; argmin.
- **ENS_POE**: per method, row-softmax of −cost/τ_m with τ_m = std of the cost matrix
  (per rep); fused = elementwise product of the three row-distributions; argmax.

Cell verdict = E003 rule: SURVIVES_HOLM iff median p ≤ 0.0041667; NOMINAL ≤ 0.05; else FLOOR;
NO_POWER if > R/2 replicates invalid. **NEG_ENS (gate)**: b=5, f=1.0, k_wrong=5 (full anchor
scramble, E006 adversarial construction): both fusions must be FLOOR, else the ensemble
family is ESTIMATOR_DETECTOR_BROKEN (its cells cannot REOPEN; reported).

## Part 3 — HUB-STRATIFIED anchor cells (claim-bearing)

KNOWN, b=5, f ∈ {0.75, 1.0}, estimators {M1, EST_OT} (profile-family + best global-transform
at the operating point), strategies:

- **HUB_SUP**: candidate pool = top ⌈n/4⌉ alignable pairs by min(support_s, support_t)
  computed on that draw's subsampled corpora; draw 5 seeds uniformly from the pool
  (("hub_seeds","SUP",f,d,rep)).
- **HUB_CEN**: pool = top ⌈n/4⌉ by source motif-graph degree (Ss row-sum, diag excluded);
  same draw rule (("hub_seeds","CEN",f,d,rep)).

2 strategies × 2 estimators × 2 fractions = 8 cells, 20 reps each, graded exactly like E003
(("hub_null",strat,est,f,d,rep)). Reference cells for comparison: E003 M1 uniform (.034/.039)
and E006 EST_OT uniform (.071/.071(b5 f1: .071)). **NEG_HUB (gate)**: HUB_SUP × M1, f=1.0,
k_wrong=5 → must be FLOOR, else hub family ESTIMATOR_DETECTOR_BROKEN.

## Multiplicity (Art. VIII)

Claim-bearing significance tests: 2 fusions × 2 fractions + 8 hub cells = **12 tests**;
per-test bar 0.05/12 = 0.0041667 — identical to the inherited E002/E003/E006 bar, so Holm-12's
entry bar is exactly met; the bar is frozen. Capacity probes are BOUNDS, not significance
tests: they act only in the CLOSED direction, where adding probes is conservative (any probe
exceeding blocks CLOSED), and they can never produce REOPENED.

## Mechanical epoch verdict (frozen order)

0. **PC0** (harness identity, run FIRST): E003 `positive_control()` must PASS
   (KNOWN M1-LOO 7/47, CTRL 55/71, code paths prediction-identical) → else DETECTOR_BROKEN,
   abort, no verdict.
1. Family NEG gates evaluated (NEG_ENS, NEG_HUB); broken families' cells are excluded from
   REOPENED eligibility (reported).
2. **DOOR_REOPENED** iff ≥1 valid claim-bearing cell = SURVIVES_HOLM.
3. else **DOOR_CLOSED** iff PC_CAP PASSED AND capacity verdict = CAPACITY_BELOW_REQUIRED
   (no valid probe EXCEEDS at KNOWN b=5 f=0.75) AND no valid claim-bearing cell ≥ NOMINAL.
   → the cross-script motif channel is formally exhausted at LA's seed budget for the probed
   estimator space + its oracle envelope; write the exhaustion argument; per the
   non-termination rule name ≥2 non-equivalent successor frontiers.
4. else **DOOR_MARGINAL** (report exactly which bound/cell blocks closure).

## Search receipt (Art. VII)

Runs: PC0; capacity = {PC_CAP CTRL 20 reps + NEG_CAP 20 + KNOWN f0.75 20 + KNOWN f1.0 20} ×
5 probes (4 verdict + Fano); ensemble = 2 fractions × 20 reps × 3 base estimators + 2 fusions
+ NEG_ENS 20; hub = 8 cells × 20 reps + NEG_HUB 20. ONE endpoint (held-out exact count;
capacity probes graded as bounds against c_req). All hyperparameters frozen here (ridge
λ=0.01, CCA reg 1e-6, ρ-clip 0.999, τ_m = cost std, pool = top ⌈n/4⌉, battery = the 10 rules
listed); NO tuning, no alternative kernels/fractions/budgets/endpoints will be tried; any
deviation = new preregistration. Pre-freeze work: read prior E002/E003/E006 artifacts only;
no corpus computation was run before this freeze.

## Falsifiable prediction (committed)

E006 pinned the suspect as channel SNR; all three base estimators share the same motif graph,
so their errors should be strongly CORRELATED and fusion should not manufacture information.
Committed: **P(DOOR_CLOSED) = 0.40, P(DOOR_MARGINAL) = 0.45, P(DOOR_REOPENED) = 0.15.**
Sub-predictions: (a) mean pairwise error-Jaccard ≥ 0.5 at the verdict cell, P=0.75;
(b) neither ensemble fusion SURVIVES_HOLM at f=0.75, P=0.90; (c) hub stratification raises
accuracy vs uniform in ≥5/8 cells, P=0.70, but P(any hub cell SURVIVES_HOLM)=0.12;
(d) CAP_ORACLE_PICK3 EXCEEDS at f=0.75, P=0.45 (the decisive uncertain number);
(e) CAP_FANO vacuous (bound ≥ required), P=0.90; (f) NEG_CAP catches ≥0 and ≤2 probes as
OVERFIT_BROKEN, with CAP_ORACLE_CCA the most likely to break, P(CCA broken)=0.35.

If CLOSED: F3's seeded-bridge family is formally exhausted at LA's budget; ≥2 non-equivalent
successor frontiers will be named in the report (committed: they will NOT be re-parameterized
seeded bridges).
