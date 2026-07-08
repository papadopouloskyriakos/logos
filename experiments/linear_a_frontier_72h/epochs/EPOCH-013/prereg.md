# EPOCH-013 — Component-decomposition matcher: attack the E009 coverage ceiling (frontier F2/F9, gate A)

**Frozen:** 2026-07-08 (hash = sha256 of this file, recorded in result.json BEFORE the run)
**Seed:** 20260708
**Claim layer:** L1 (sign-form geometry / palaeography) only. No L2+ claims, NO phonetic values
anywhere in any output. No transfer licences touched (Art. XV: none earned, none claimed).
**Articles triggered:** V (layer wording), VII (search receipt: one architecture, frozen
hyper-rules, no post-hoc tuning), VIII (effective n = exhaustive frames, no analyst selection),
IX (info budget: output is a similarity matrix, not a reading), XI/XII (non-circularity: the LB
font gallery and AB value-identity ground truth are Unicode/font-standard, independent of the
extraction pipeline; SigLA labels are used only to LOCATE and GROUP instances, never as a
matching feature; recovery counting uses NO label information in the decomposition rule),
XVIII (assumption register: SigLA traces are expert re-drawings made with knowledge of sign
identity — ALL stability numbers are upper bounds on photograph-level allography; carried on
every output), XXII (this header + compliance line in the report).

## Question

E009's pipeline fails 1,009/4,756 glyph instances (21.2%) as `too_many_components`
(n_components > 8 after despeckle) — yet E008 showed some LA signs (TI, *307, *309B) are
GENUINELY multi-component. Replace the single-graph feature vector with a
**multiset-of-subgraphs matcher**: each glyph = a bag of connected-component stroke-graphs
(each with its own topology + relative-position features), glyph-to-glyph distance via optimal
assignment (Hungarian) with a component-count-aware unmatched penalty. Does this (1) NOT
degrade the E009 LEG1 calibration on already-extractable signs, (2) recover a material share of
the 1,009 failures and raise dark-sign coverage, (3) hold or improve within-script
self-retrieval on the expanded corpus, and (4) yield an upgraded similarity matrix?

## Pre-freeze frame facts (from E009's PUBLISHED artifacts only — `features/instances.json`,
`epochs/EPOCH-009/result.json`; no new pipeline output was computed before this freeze)

- 4,756 instances; 3,744 E009-ok; 1,009 `too_many_components` (median stored n_components 18,
  p90 43, max 132); 3 bbox-density fails.
- The 1,009 failures touch 158 labels, only **14** of them dark (A3xx). **Recovery ceilings
  (arithmetic on E009 counts, computable without any new run):**
  - dark-sign usable coverage: 65/69 now → **69/69 ceiling** (all four missing labels A335,
    A347, A361, A365 have ≥1 failed instance);
  - dark-sign ROBUST (≥3) coverage: 21/69 now → **25/69 ceiling** (only A316, A320, A324, A335
    can cross 3). **The task brief's "target ~50/69 robust" is mathematically unreachable from
    this corpus**; we preregister the honest frame and grade against the ceiling, not the brief.
  - LEG2 frame (labels ≥4 instances): 116 now → 126 ceiling.
- E009 published baselines to beat/hold: LEG1 agg MRR 0.1710 (aspect adversary 0.0987, chance
  0.0663, gallery n=74, frame n=57); LEG2 even/odd self-MRR 0.3993 (n=116, aspect 0.1126,
  chance 0.0459).

## Pipeline (rule-based, deterministic; ALL rules frozen NOW)

Shared front end = E009 frozen pipeline verbatim (bbox mode per doc reused from E009
`doc_meta`; crop; >512 px LANCZOS downscale guard; alpha/Otsu `binarize`; AMENDMENT-A
`despeckle` = remove comps < max(4 px, 2% of largest) + 3×3 closing). Renders are the cached
E009 set (`data/stroke_corpus/renders/`, 802 docs); NO new fetching.

**Component decomposition (new, frozen):**

1. Connected components (8-connectivity) of the despeckled ink mask.
2. Keep components with ink share ≥ 3% of total ink, largest-first, **cap K = 12**.
3. `decomposable(instance)` := total ink fraction ∈ [0.01, 0.6] ∧ 1 ≤ n_kept ≤ 12 ∧ kept ink
   share ≥ 0.70 of total ink ∧ every kept component yields a valid `skeleton_graph` with all
   features finite ∧ component aspect > 0. Fail reasons recorded (`fragmented_beyond_cap`,
   `kept_share_lt_070`, `ink_fraction_out_of_range`, `empty_component_skeleton`).
4. Per-component feature (13-dim): [n_endpoints, n_junctions, n_loops, n_strokes,
   skel_len_norm, orient0..3 (length-weighted 4-bin), rel_cx, rel_cy, ink_share, log(comp
   aspect)] where (rel_cx, rel_cy) = component ink centroid in glyph-bbox coordinates ∈ [0,1]²
   and ink_share = comp px / total kept px. Whole-glyph aspect is kept OUT (adversary feature).
5. z-normalization: pooled mean/sd over ALL kept components of ALL decomposable epigraphic
   instances (one space for queries, gallery, everything).
6. Component pair cost c(a,b) = Euclidean distance of z-vectors. Glyph distance
   D(A,B): pad the m×n cost matrix to s×s (s = max(m,n)) with dummy cost **λ = median cost over
   20,000 seeded random cross-instance component pairs** (unmatched component = as bad as a
   random mismatch); Hungarian optimal assignment; D = total assignment cost / s. This is
   component-count-aware: each surplus component pays λ.
7. LB font gallery (74 renders) is decomposed with the IDENTICAL rule (binarize → despeckle →
   decompose), z-scored in the same pooled space.

**Recovered instance** := E009 status `too_many_components` ∧ `decomposable` under rule 3.
**Usable corpus (expanded)** := E009-ok ∧ decomposable, PLUS recovered. (E009-ok instances that
fail rule 3 are attrition — counted, reported, and excluded from queries; fail closed.)

## Legs & controls (PC first; fail closed)

- **PC-1 (positive control, run FIRST, synthetic, analytic ground truth):**
  (a) E008's 5 single-component glyphs (+ O T X L) through the decomposition path: each must
  give n_kept = 1 with E008's (endpoints, junctions, loops) ground truth (L-relaxation as in
  E008); ≥4/5 must pass.
  (b) 3 multi-component glyphs with analytic decomposition ground truth: "=" (2 bars → 2 comps,
  each (2,0,0)); "÷" (bar + 2 dots → 3 comps: (2,0,0),(0,0,0),(0,0,0)); "%" (2 rings + bar → 3
  comps: (0,0,1),(0,0,1),(2,0,0)). All 3 must decompose to the exact kept-count with
  per-component topology matching the multiset ground truth.
  (c) Matcher sanity: D(g,g) = 0 for all synthetics ∧ D("=","=") < D("=","%").
  PC-1 PASS := (a) ∧ (b) ∧ (c). FAIL ⇒ verdict DECOMPOSITION_DEGRADES(PC_FAIL), stop.
- **LEG-1 / PC-2 non-degradation (confirmatory #1):** E009's exact LEG1 frame (57 shared
  values, 74-render LB gallery, same truth map). Queries = **E009-ok instances only** (isolates
  the matcher change from the corpus change). Aggregate rank per value = rank of truth by MEAN
  over the value's query instances of D(instance, gallery render). Metrics: agg MRR, top-1,
  top-5, per-instance MRR. NC1: 20,000-draw permutation null (iid uniform ranks, n = realized
  values), one-sided p. NC2 aspect adversary: rank by |Δ mean log whole-glyph aspect| (E009
  protocol). **NC3 count adversary (new): rank by mean |n_kept(query) − n_kept(gallery)|** —
  the matcher must beat pure component counting.
  NONDEGRADE := realized n ≥ 30 ∧ p < 0.01 ∧ MRR_agg ≥ 0.145 (= E009's 0.171 minus a 15%
  relative margin) ∧ MRR_agg > aspect MRR ∧ MRR_agg > count MRR.
  Secondary (descriptive): same leg with queries = expanded corpus (ok + recovered).
- **LEG-R recovery (confirmatory count, no p-value):** n_recovered / 1,009; ok-attrition rate;
  dark usable & robust coverage (69-frame, ceilings above); expanded LEG2 frame size; per-label
  recovery table. RECOVERY_GOOD := recovery_rate ≥ 0.30 ∧ dark usable ≥ 67/69 ∧ dark robust
  ≥ 23/69.
- **LEG-2′ self-retrieval on the expanded corpus (confirmatory #2):** labels with ≥4 usable
  instances (expanded). Even/odd split by sorted (designation, glyph index) [E009 protocol].
  Half representation = up to 6 instances seeded-sampled (rng(SEED+13), per label, sorted
  order); D(half_A_i, half_B_j) = mean cross-pair instance distance; rank of self. Self-MRR,
  20,000-draw permutation p, aspect adversary (mean log aspect per half), count adversary.
  HOLD := n ≥ 15 ∧ p < 0.01 ∧ self-MRR ≥ 0.359 (= 0.9 × E009's 0.3993) ∧ self-MRR > aspect
  self-MRR. Diagnostic (descriptive): identical protocol on E009-ok-only instances and on the
  E009 116-label frame, to decompose matcher effect vs corpus-expansion effect.
- **Output:** upgraded similarity matrix over all usable labels (≥1 usable instance, expanded)
  + the 74 LB font renders as a MARKED block. Label representation = up to 4 seeded instances
  (rng(SEED+14)); entry = mean cross-pair D (self-diagonal 0). Written to
  `data/stroke_corpus/component_matcher/component_similarity_matrix.{json,npz}` + per-instance
  component features `components.json` + `recovery_manifest.json`. NO values, NO readings.

## Mechanical verdict (frozen)

- **DECOMPOSITION_DEGRADES** := PC-1 FAIL ∨ ¬NONDEGRADE.
- **DECOMPOSITION_RECOVERS** := NONDEGRADE ∧ RECOVERY_GOOD ∧ HOLD (report all numbers).
- **DECOMPOSITION_NEUTRAL** := otherwise (PC passes, matcher not worse, but recovery small or
  self-retrieval falls below the hold bar; numbers reported).
- Multiplicity: exactly 2 confirmatory p-values (LEG-1 p, LEG-2′ p); Holm reported alongside
  raw. Everything else is descriptive and worded as such.

## Honest-accounting commitments

- A recovered instance is a GEOMETRY extraction, not a reading; coverage gains are L1 only.
- The 15% non-degradation margin and the 0.9 hold factor are frozen HERE, before any run;
  thresholds are immutable; a pipeline BUG fix (not threshold change) is allowed, logged as a
  deviation, with pre- and post-fix numbers both reported.
- Trace-standardization caveat (Art. XVIII) attaches to every stability number.
- The brief's 50/69 robust target is recorded as unreachable (ceiling 25/69) — grading against
  the brief's number would be theater; grading is against the preregistered thresholds above.
- Compute: local CPU (32 cores), multiprocessing over docs/label pairs; deterministic seeds
  only (SEED, SEED+13, SEED+14, perm rng SEED+9 as E009).
