# EPOCH-012 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F6** (gates A/E) — scribal/site allograph structure,
first productive use of the E009 stroke channel.
**Epoch question:** Does per-sign allograph variation in the SigLA stroke corpus carry SITE structure
(and, if so, chronology-proxy structure), beyond document-length / sign-inventory / rendering nulls?
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Claim layer:** L1 ONLY (sign-form geometry / palaeographic variation). No L2+ claim can emerge; no
phonetic values anywhere in any output; no transfer licence touched (Art. XV).
**Articles triggered:** V (L1 wording cap), VII (search receipt: all tests and thresholds enumerated
here; nothing selected post hoc), VIII (effective_n: the permutation unit is the DOCUMENT, never the
instance — instances within a doc share one tracing session and one physical object; doc-level
permutation is the anti-pseudo-replication rule), IX (info budget: a site classifier output is
palaeographic metadata, not a reading), XI/XII (non-circularity: site/support/context labels come from
SigLA designations + corpus/silver — independent of the E009 extraction pipeline; sign labels are used
only to CONDITION comparisons, never graded against themselves; the PC grades sign identity, the legs
grade site — disjoint truths), XVII (append-only; deviations logged in result.json), XVIII
(assumptions below, incl. the standing SigLA trace-standardization caveat), XXII (this header).

## Prior art cited + differenced

- **EPOCH-009 (STROKE_CHANNEL_CALIBRATED_USEFUL):** built the channel; leg2 split-half sign
  self-retrieval MRR 0.399 (chance 0.046, aspect 0.113). E009 never asked about sites. Difference:
  this epoch holds sign identity FIXED and asks whether the residual (allograph) variation is
  site-structured.
- **E009/E008 standing assumption (Art. XVIII):** SigLA traces are expert re-drawings by a team that
  knew sign identities; any stability/structure result is an upper bound on photograph-level claims
  and could be contaminated by tracing style. Carried here as an explicit adversarial leg (G-gates),
  plus the mechanical caveat that ONE trace per document makes tracer-vs-scribe INSEPARABLE at the
  document level — only site-level aggregation with doc-level permutation + the G-gates below can
  partially decontaminate.
- Prior campaigns' palaeography: none ran an instance-level allograph→site test (methodology
  inventory checked: stroke channel is new as of E008/E009).

## Data / units (frozen; pre-freeze DESCRIPTIVE inventory only — counts, no test statistic peeked)

- Input: `data/stroke_corpus/features/instances.json` (E009 output): 4,756 instances, 3,744 ok
  (`ok==true`), 10-dim stroke feature `feat` (5 topology counts, skel_len/√area, 4-bin orientation
  histogram) + `aspect` (adversary channel, kept OUT of primary features, as in E009) +
  `ink_fraction`; `doc_meta` per document (bbox mode, density, global_ink).
- **Site** := first whitespace token of the SigLA designation after stripping a leading backtick
  (`` `KE Wc 2a`` → KE). Pre-freeze inventory: 722 docs with ≥1 ok instance; ok instances by site:
  HT 2287, KH 475, ZA 325, PH 162, KN 154, ARKH 74, …
- **Support / context** := from `corpus/silver/inscriptions_structured.json` matched by
  `designation.replace(' ','')` (543/722 docs match); unmatched docs with a GORILA series token
  `W[a-z]` get support class `SERIES_<Wx>`; else `UNKNOWN`. Context only from silver-matched docs.
- **z-space:** per-feature mean/SD z-scoring over ALL 3,744 ok instances (frozen, site-blind).
- **Robust label** := ≥3 ok instances corpus-wide (E009 definition; pre-freeze: 133 labels).
- **Deviation** (leg 2 embedding unit): dev(i) = z(feat_i) − mean z(feat) over ALL ok instances of
  label(i) (label mean is corpus-wide, site-blind → non-circular w.r.t. site).
- **Distance:** Euclidean in the 10-dim z-space (primary); aspect-only |Δ z(aspect)| (adversary).

## Frames (frozen from pre-freeze inventory)

- **F-SIGN (leg 1):** signs with ≥2 sites each having ≥3 ok instances → 60 signs (list emitted in
  result.json). Same-doc instance pairs are EXCLUDED from all within/cross comparisons (they share a
  tracing session; Art. VIII).
- **F-DOC (leg 2):** docs with ≥3 ok robust-label instances; sites with ≥10 such docs. Pre-freeze
  inventory says this yields HT/KH/ZA/KN/PH, ≈267 docs (exact realized numbers in result.json).
- **F-MANYDOC (gate G1):** F-SIGN ∩ signs attested in ≥20 distinct docs (pre-freeze: 47 signs corpus-
  wide have ≥20 docs).
- **F-TABLET (gate G2):** F-DOC docs with support == Tablet; sites keeping ≥10 tablet docs
  (pre-freeze inventory: HT ≈142, KH ≈36 → a 2-site test).
- **F-CHRON (legs 3–4):** support proxy within HT: Tablet vs {Roundel, SERIES_Wc} pooled (minority
  pre-freeze ≈16 docs); context: classes with ≥8 non-blank eligible docs each — pre-freeze inventory
  shows LMIB ≈182 vs all others ≤2 → the context leg is expected NO_POWER and will be declared so
  mechanically if <2 classes qualify.

## Positive control (run FIRST; fail ⇒ STOP)

**PC — sign separation, instance level.** On ok instances of robust labels: leave-one-out 1-NN sign
identification in the 10-dim z-space (nearest other instance, same-doc neighbours ALLOWED here — this
is a channel-power check, not a site claim). Null: 1,000 label permutations over the fixed NN graph.
Adversary: aspect-only 1-NN accuracy.
**PC_PASS := top1_acc ≥ 0.15 ∧ p_perm < 0.001 ∧ top1_acc > aspect_top1_acc.** (Known truth: E009
sign-level split-half MRR 0.399; instance-level top-1 must clear 0.15, ≈4× the largest-class share
0.034.) PC fail ⇒ verdict `CHANNEL_PC_FAIL`, stop.

## Leg 1 — per-sign within-site vs cross-site allograph spread (confirmatory)

For each sign s ∈ F-SIGN, over its ok instances' pairwise distances (same-doc pairs excluded):
D_s = mean(cross-site pair dist) − mean(within-site, different-doc pair dist); scale σ_s = SD of all
included pairwise distances of s (permutation-invariant). **Global statistic T = mean over F-SIGN of
D_s/σ_s.**
**Null N1 (doc-level site permutation):** permute the doc→site map over the 722-doc universe
(preserving site doc-counts), 10,000 draws, seed 20260708; instances inherit their doc's permuted
site. Signs with no within or no cross pair in a draw are dropped from that draw's mean. One-sided
p1 = P(T_perm ≥ T_obs).
**Localization (secondary, non-gating):** per-sign one-sided p from the same draws, Holm over the 60
signs; report the count significant at Holm-0.05.
**LEG1_FIRE := Holm-adjusted p1 < 0.01 (family = {p1, p2}).**

## Leg 2 — document embedding → site (confirmatory)

Doc embedding = mean of dev(i) over the doc's ok robust-label instances (F-DOC). Metric: leave-one-
out 1-NN **balanced accuracy** (macro recall over sites).
**Null N2a (doc-level site permutation):** 10,000 permutations of site labels over F-DOC docs on the
fixed NN graph → one-sided p2.
**Null N2b (inventory-resample, confound-preserving):** 1,000 draws; each instance's dev is replaced
by the dev of a uniformly-drawn OTHER instance of the same label (any site), embeddings + NN graph
rebuilt per draw. Preserves doc length and sign inventory exactly; destroys site-coherent allography.
**LEG2_FIRE := Holm-adjusted p2 < 0.01 ∧ balanced_acc > p95(N2b).**
**Nuisance comparator (feeds G3):** embedding = [global_ink, density_xywh, density_xyxy,
mode==xywh, n_ok_instances, mean ink_fraction, mean z(aspect)] per doc, z-scored over F-DOC; same
LOO 1-NN balanced accuracy.
Lattice output: doc embeddings, LOO predicted site, and average-linkage agglomerative clusters at
k = n_sites with ARI vs site (descriptive) → `data/stroke_corpus/allograph_structure/`.

## Legs 3–4 — chronology proxies (conditional; run only if LEG1_FIRE ∨ LEG2_FIRE; else descriptive-skipped)

- **Leg 3 (support proxy, within HT):** leg-1-style global test, grouping = Tablet vs
  {Roundel, SERIES_Wc}, signs with ≥3 ok instances in each class, doc-level permutation (10,000).
  Frame gate: ≥5 qualifying signs ∧ minority class ≥10 docs, else `SUPPORT_NO_POWER`. Raw p3
  (single conditional test, own family).
- **Leg 4 (context):** frame gate ≥2 context classes with ≥8 non-blank eligible docs; pre-freeze
  inventory says this FAILS → declare `CHRONOLOGY_CONTEXT_NO_POWER` mechanically (no test run).

## Adversarial / confound gates (run whenever a leg fires)

- **G1 (tracing-session spread):** rerun leg-1 global test on F-MANYDOC (signs spread over ≥20 docs
  ⇒ many tracing sessions). Survive := p1' < 0.05 (power drops; weaker bar frozen now).
- **G2 (medium, site≈support de-confound):** rerun leg 2 on F-TABLET (2-site HT-vs-KH expected).
  Survive := balanced_acc' > p95 of its own 10,000-draw doc-level permutation null.
- **G3 (rendering nuisance):** allograph balanced_acc (leg 2) > nuisance-comparator balanced_acc.
- **G4 (residualization, reported, non-gating):** OLS-residualize each dev dimension on
  [global_ink, density_xywh, mode] and re-run leg 2 accuracy; report the drop.
- Doc-level coherence (descriptive): same-doc vs different-doc within-site mean distance per F-SIGN
  sign — quantifies the tracer/scribe entanglement; reported, never gated.

## Mechanical verdict (frozen; PC fail overrides all → CHANNEL_PC_FAIL)

- **ALLOGRAPH_STRUCTURE_CONFOUNDED** := (LEG1_FIRE ∨ LEG2_FIRE) ∧ ¬(G1 ∧ G2 ∧ G3), where G1 is
  required only if LEG1_FIRE, and G2∧G3 only if LEG2_FIRE.
- **ALLOGRAPH_STRUCTURE_SITE_LEVEL_DETECTED** := LEG1_FIRE ∧ LEG2_FIRE ∧ G1 ∧ G2 ∧ G3.
- **ALLOGRAPH_STRUCTURE_WEAK** := exactly one of LEG1_FIRE/LEG2_FIRE ∧ its required G-gates pass.
- **ALLOGRAPH_STRUCTURE_ABSENT** := ¬LEG1_FIRE ∧ ¬LEG2_FIRE.
- Multiplicity: confirmatory family = {p1, p2}, Holm. Leg 3 conditional single test (raw p3 < 0.01
  to claim `SUPPORT_STRUCTURE_DETECTED`, else `SUPPORT_STRUCTURE_ABSENT`/`SUPPORT_NO_POWER`).
  Everything else is descriptive and worded as such.

## Honest-accounting commitments

- Any positive is an **L1 palaeographic** result about TRACE geometry: SigLA traces are expert
  re-drawings; one trace per document ⇒ tracer style and scribal hand are inseparable at doc level.
  A SITE_LEVEL_DETECTED verdict therefore reads: "site-coherent allograph structure in the traced
  corpus, robust to tracing-session spread (G1), medium (G2) and rendering nuisance (G3) checks —
  scribal-hand interpretation plausible but not proven without photograph-level replication." This
  sentence (or the corresponding negative) appears verbatim in the report.
- HT dominates (2,287/3,744 ok instances): balanced accuracy + doc-level permutation keep HT from
  buying the verdict; per-site recalls reported.
- effective_n: docs, not instances (Art. VIII); realized doc counts per frame in result.json.
- Nothing is dropped silently: every frame's realized n and every excluded doc/sign category is
  counted in result.json.
- If the run reveals a pipeline BUG (not a threshold choice), the fix is applied, logged as a
  deviation, and pre-fix + post-fix numbers are both reported; thresholds are immutable.
