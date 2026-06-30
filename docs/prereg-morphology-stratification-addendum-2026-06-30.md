# Pre-registration ADDENDUM — corpus stratification for morphology induction (Direction A)

**Registered 2026-06-30, as a NEW dated pre-registration** (the original
`docs/prereg-morphology-2026-06-30.md` is frozen and is never edited; per logos policy any change is
a new dated file). This addendum governs **any second / stratified morphology run** — the first run
(`scripts/comparison/morphology.py`, pooled, reported a NULL) stands as-is under the original pre-reg.

**Motivation.** Two external inputs force a stratification redesign before any morphology claim:
(1) v2 next-actions §P1.6 — pooling ~1,370 inscriptions risks inducing "morphology" that is really a
mix of genres/registers/periods, a confound the within-form permutation null does **not** catch
because it preserves the pooling; (2) the audit of **Salgarella & Judson 2024** ("Signs of the
times?", KO-RO-NO-WE-SA pp. 359–379), the field's own statement on the stratification axis.

## What Salgarella & Judson 2024 establish (the binding constraints)

- **Palaeographic variation does NOT cleanly track chronology** (Conclusions, p. 377): "any
  chronological analyses purely based on palaeography are to be regarded as thoroughly unreliable."
- **Linear A is treated by the experts as ONE chronological unit (LM IA–B)** (pp. 360–361): internal
  chronological resolution "is not reliably available." Variant sign-forms are largely
  *contemporaneous* (p. 360; "persistence of variation," p. 373).
- **The decisive artifact: a scribe-driven "pattern."** The simplified Knossos West Wing forms "may
  reflect the preferences of the two writers who are predominant in this deposit, **Hand 103 and Hand
  115**" (p. 375) — two individuals produce what looks like a trend. Variation is driven by **site and
  scribal hand**, down to the individual writer (p. 376), "as much as chronological."
- **Their own corpus scope** (p. 360): restricted to *administrative tablets* from the prominent
  sites (Haghia Triada, Khania, Zakros, Phaistos, Arkhanes, Malia, Knossos, Tylissos) — **not** the
  libation/votive corpus that anchors the Davis/Di Mino dispute. (So this paper is **orthogonal** to
  the `*301` question — palaeography ≠ morphology; never cite it as support for or against
  i-`*301`="give".)

## The stratification requirement (binding on the stratified run)

1. **KEEP leave-one-SITE-out CV.** Validated by their site-specific-variation finding; site is a real
   stratum. (The original pre-reg already uses leave-one-site-out, not k-fold.)
2. **Stratify by genre/register before inducing morphology.** Define strata explicitly and tag by
   site + document type: **Haghia Triada administrative** (~half the corpus) vs **libation / ritual
   formula** vs **other sites/genres**. Induce morphology *per stratum*, then test **cross-stratum
   stability** of every candidate affix/paradigm. An affix that appears in only one stratum is a
   **register feature**, reported as such — not asserted as language morphology.
3. **ADD a scribal-hand / find-spot robustness control.** No affix or segmentation signal may be
   reducible to a dominant scribe's idiolect (the Hand 103/115 lesson). Where SigLA palaeographic
   grouping or GORILA find-spot data permit a hand/deposit grouping, require any candidate affix to
   recur across **distinct hands / deposits**, not just distinct inscriptions. Where hand-attribution
   is unavailable (see data caveat), fall back to **find-spot/deposit** as the stratum and flag
   inscription-independence as an **unverified assumption**.
4. **DEFLATE effective-n for within-hand and within-site non-independence.** The original H2 gate
   ("each affix must recur on ≥2 distinct stems across **independent inscriptions**") counts
   hand-correlated inscriptions as independent samples — empirically violated here, which inflates
   effective-n and under-deflates the multiplicity correction (logos invariant 8). The stratified run
   must compute effective-n with within-hand/within-site correlation discounted, and report the
   deflated significance. Upgraded gate wording: **"…recur on ≥2 distinct stems across distinct
   scribal hands / deposits where SigLA palaeographic grouping permits; otherwise flag
   inscription-independence as unverified and deflate."**
5. **EXPLICITLY DECLINE chronological-period CV.** Do **not** add temporal stratification or
   LM-subperiod cross-validation. Per pp. 360–361 and 377, any chronological/sub-period dating of
   Linear A palaeography conflicts with the published consensus and would be desk-rejected as
   methodologically unsupported. Cite this paper as the justification for *not* stratifying by time.
6. **Robustness caveat on the segmentation positive.** The word-boundary positive (micro-F1 0.436 >
   0.389 random) rests on the scribe's word-dividers, which are themselves a documented
   scribal/site practice. The stratified run must check boundary-recovery robustness **across
   hands/deposits**, not only across the 52 sites, before the positive counts as held-out-independent.

## Data caveat (records what is and is not available)

Linear A hand-attribution is **far less developed** than Linear B (where Hand 103/115 etc. are
catalogued). logos must first determine whether SigLA palaeographic data or GORILA find-place data
can support a hand/deposit stratum **at all**, or whether **find-spot/deposit must serve as the only
available proxy**. If neither supports a usable hand grouping, requirement #3 degrades to find-spot
stratification + an explicit "inscription-independence unverified, deflated" flag — reported as a
limitation, never silently dropped. The relevant source (Salgarella 2020, site/deposit-specific
palaeographic preferences) is in the acquisition list.

## Acceptance / outcomes

Same four outcomes as the original pre-reg (CONFIRM / EXTEND / REFUTE-NULL / NO-POWER), now evaluated
**per stratum and on cross-stratum stability**. A candidate that confirms in one stratum but fails
cross-stratum stability is reported as a register/idiolect feature, not validated morphology. Counts
are generated, not hand-written. This file is frozen at commit time.
