# LOGOS-2 Milestone-2 Control Addendum

**Committed BEFORE reading, scoring, plotting, or summarizing any at-scale CSA, Linear B,
Cypriot, or other confirmatory result.** As of this commit the resumed CSA sweep has completed
zero cells' contents that anyone (human or model) has inspected: only scheduler progress lines
(launch/finish counts) have been read; no cell JSON, no curve, no locator output. Machine-readable
mirror: `MILESTONE2_CONTROL_ADDENDUM.json`; both hashed in `MILESTONE2_CONTROL_ADDENDUM.sha256`.

Standing interpretation discipline (restated, binding): UNSAT_GENERIC is not evidence against a
specific linguistic hypothesis; relational darkness is not proof of undecipherability; Ugaritic
(alphabetic) success does not qualify the machinery for syllabic Linear A; pilot 0/15 is
descriptive only, never a false-positive-rate certificate; Salgarella homomorphy grades are
palaeographic evidence, never phonetic-value identity; A-initial enrichment is not prefixation,
productivity, or morphology.

## 2.1 E201 confirmatory F1 qualification (frozen)

**Split (clarification consistent with the frozen E201 prereg):**
- **F1a — EM qualification + null calibration + process-replay scoring.** Runs on the in-repo
  `.cog` datasets; no dependency on the running CSA sweep; may start once this addendum is
  committed.
- **F1b — sufficiency-curve integration.** Consumes the CSA sweep's at-scale LB/Cypriot cells
  ONLY through a §2.3 import record; no F1b artifact may be read before F1a's plan (this
  section) is frozen — satisfied by this commit ordering.

**Datasets and hashes (from the committed E201 `data_manifest.sha256`):**
`linear_b-greek.cog` (270ff077…), `linear_b-greek.names.cog` (ec09bb5d…), `csyl-greek.cog`
(60fd1818…), `uga-heb.no_speNL.cog` (per manifest), `uga-heb.no_speNoisy.cog`,
`StarlingDB_Ph-Ug.cog`, `RWT2002_Luv-Hit.cog` (per manifest). Source: vendored Tamburini /
NeuroDecipher lineage files, unchanged; any file whose hash differs at run time disqualifies the
arm (fail closed).

**Partitions:** per dataset, a seeded 70/30 fit/holdout split of cognate pairs
(seed = sha256(1336530913 | "E201F1" | dataset | "split")). Anchors and any bilingual seeding are
drawn ONLY from the fit partition. `cognate_accuracy` and all qualification metrics are computed
ONLY on holdout pairs. No dev partition (no tuning is permitted at F1; hyperparameters are the
pilot's frozen defaults: sub_cost=1.0, indel_cost=1.0, max_len_delta=2, iters=25,
frequency-init EM with SOFT anchor warm-start exactly as `harness.py` at commit 26ccd27).

**Preprocessing/transliteration:** the `.cog` files' own romanization, tab-split, char-tuple
words — no edits, no normalization beyond what `harness.load_cog` at 26ccd27 performs.
**Segmentation:** KNOWN (pair lists are pre-segmented); the segmentation-degradation rung remains
NOT_APPLICABLE for these datasets (disclosed in the E201 prereg).

**Qualification rung (single, no search):** R_full = 10 anchor names (first 10 fit-partition
pairs under the seeded order) + 10% bilingual seeding from fit. Qualification is evaluated at
R_full ONLY; the descriptive ladder {0,1,3,5,10 names} × bilingual {0,10%} is reported whole but
carries no qualification weight (no best-rung selection).

**Recovery thresholds (holdout cognate accuracy at R_full):** Linear B→Greek ≥ 0.50 (from the
frozen E201 prereg); Cypriot→Greek ≥ 0.35 (set here, blind); Ugaritic→Hebrew ≥ 0.60 (frozen
E201 prereg; alphabetic — informative but NEVER sufficient for syllabic qualification).

**Syllabic qualification rule:** the machinery may support positive Linear A inference ONLY if
at least one of {Linear B→Greek, Cypriot→Greek} meets ALL of: (1) holdout accuracy ≥ its
threshold at R_full; (2) same pipeline abstains (no graduation) on unrelated-language,
shuffled-anchor(=corrupted anchors at f=1.0 on the anchor set), and synthetic-isolate controls;
(3) no leakage detector fires; (4) survives the two-dataset Bonferroni (the only search in the
family is which of the two syllabic datasets qualifies: report both, correct at α/2 where a
p-value is used); (5) uses no post-hoc segmentation or value mapping (frozen pipeline only).
Otherwise the EM implementation is marked **NOT_QUALIFIED_FOR_LINEAR_A_POSITIVE_INFERENCE**; the
anchor-to-identifiability framework may still be discussed as a framework, but no positive Linear
A conclusion may be generated from this implementation.

**Abstention metric:** char-mapping confidence = fraction of cipher chars whose top-1 vs top-2
co-occurrence counts differ by ≥2; the pipeline ABSTAINS when confidence < 0.5. Abstention
correctness = abstention rate on controls (target ≥ 0.8) and non-abstention on qualifying real
runs. **Calibration minimum:** among confident chars the holdout accuracy must be ≥ overall
holdout accuracy (an inverted reliability ordering disqualifies); full reliability table reported.

**Effect sizes:** every reported accuracy carries (acc − chance) with a 1000-resample bootstrap
95% CI over holdout pairs; minimum effect for qualification: CI lower bound > 2× chance.

**Leakage tests:** the pilot's identical-string detector (threshold 5%) plus a fit/holdout
overlap check (any pair present in both partitions disqualifies).

**False-graduation definition (for §2.2):** a null campaign "graduates" falsely if its holdout
accuracy ≥ the dataset threshold AND ≥ 2× empirical chance AND the pipeline did not abstain AND
no leak detector fired.

**Missing/failed cells:** any failed or timed-out qualification cell fails that dataset's arm
closed (no imputation, no rerun-until-pass; a mechanical infrastructure failure may be rerun once
with the failure logged).

**Seeds:** master 1336530913; per-cell sha256(master | "E201F1" | dataset | cell | replicate).
**Environment:** `research/logos2/.venv` as frozen in the E201 `environment.txt` refreshed at the
F1a start commit; any package drift between freeze and run disqualifies.

**Disqualification conditions:** dataset hash mismatch; partition-overlap leak; env drift; seed
deviation; any post-freeze edit to harness.py semantics before F1a completes (bugfixes require an
amendment file first); any inspection of F1b imports before this addendum's commit (none
occurred).

## 2.2 False-graduation calibration (frozen)

Pilot 0/15 is descriptive only. Confirmatory calibration arm:

- **N_null = 200** independent null campaigns (≥149 required for a zero-failure bound below
  0.02; 200 preferred and adopted).
- Null construction preserves: corpus size, alphabet/syllabary size, character frequency
  profile, segmentation regime (pair lists), anchor-count regime (10 anchors + 10% bilingual
  drawn the same way), and the model-selection procedure (none beyond the frozen pipeline — the
  full pipeline including its abstention rule runs inside every null).
- Null families (declared): synthetic-isolate target (frequency/length-matched), shuffled-
  inventory source, unrelated-target pairing — each 200/3 ≈ 66-67 campaigns, composition frozen
  as 67/67/66.
- **Report the exact one-sided Clopper–Pearson 95% upper bound** on the false-graduation rate;
  the committed target is **upper bound ≤ 0.02**. If ≥1 false graduation occurs, continue to
  N=400 and evaluate the bound; if the bound still exceeds 0.02 the arm FAILS. Never summarize
  by the point estimate alone; MC p-values use the plus-one correction.

## 2.3 Imported CSA artifact boundary (frozen)

Any import of CSA-sweep or other external-worktree outputs emits, BEFORE analysis:
`research/logos2/imports/<import_id>/IMPORT_RECORD.json` (source branch, commit, experiment/epoch,
host, environment, start/completion timestamps, seeds, configuration, completion status, file
list, per-file SHA-256, whether any human/model inspected the files before this addendum's
commit [answer for the CSA sweep: NO — only scheduler launch/finish lines were read], whether any
file was regenerated after freezing), `IMPORT_MANIFEST.sha256`, and `README.md`. Incomplete
provenance ⇒ the import fails closed and the dependent arm is BLOCKED.

## E203 confirmatory extension (scope freeze, per milestone-2 brief §3)

E203-F1 adds, without responding to UNSAT_GENERIC by adding hard pins: minimal-unsat-core
enumeration + core-composition comparison vs matched random pin sets; a transparent weighted
formulation (CP-SAT soft penalties; weights sensitivity-swept over declared bands
w ∈ {0.25, 0.5, 1, 2, 4} × the Salgarella-grade base weights) reporting near-optimal solution
multiplicity, assignment marginals/bounded support, stability under weight perturbation, and
genuinely-contracting sign domains; counting bounds (domain-product + SIS + XOR-hash where
feasible) with CP-SAT/Z3 backbone cross-check validated on synthetic instances; extended matched
nulls (degree-, domain-size-, sign-frequency-, edge-class-, and uncertainty-grade-preserving);
and the E202-recast sequential acquisition policy over the declared hypothetical-observation
family (secure name; toponym; fraction relation; allograph split; new sparse-site inscription;
bilingual fragment; commodity label; palaeographic grade correction) ranked by expected entropy
reduction, model-count reduction, backbone increase, acquisition cost, availability, and
wrong-observation robustness → `VALUE_OF_INFORMATION.csv`, `SEQUENTIAL_ACQUISITION_POLICY.json`,
`EVIDENCE_ACQUISITION_PRIORITIES.md`.

## Standing rules for E204–E208 this milestone

E204: no seal opening (the FRACTION_ORDER_ANETAKI_SEAL's opening rule — Anetaki II publication —
has not occurred); component separation + ablations + selection-aware nulls as briefed; ≤L3.
E205: three conditions (NO_HOMOMORPHY_PRIOR / GRADED_PALAEOGRAPHIC_PRIOR /
HARD_IDENTITY_SENSITIVITY_ONLY — the last never default); palaeographic evidence only; E205C
stays BLOCKED_DATA. E206: internal-only slot freeze committed before ANY external name inventory
is loaded; contamination classified. E207: the six-model battery + matched synthetics; the
restricted conclusion vocabulary (POSITIONAL_ONLY … PARADIGMATIC_MORPHOLOGY_SUPPORTED); banned
words unless the final category is reached. E208: **DE_AUTHORIZED_PENDING_LICENSE_CLEAN_GATE**.
