# LOGOS Constitution v2.3

**Status:** RATIFIED · **Effective:** 2026-07-07 (v2.0) · **Amended:** 2026-07-07 (v2.1, v2.2), 2026-07-08 (v2.3) ·
**Supersedes:** v1.0 (the Mission + 12 Invariants formerly in `CLAUDE.md`)
**Amendment records:** [`AMENDMENT-001-v1-to-v2.md`](./AMENDMENT-001-v1-to-v2.md) (v1→v2.0),
[`AMENDMENT-002-v2.0-to-v2.1.md`](./AMENDMENT-002-v2.0-to-v2.1.md) (v2.0→v2.1, precision fixes B1–B8),
[`AMENDMENT-003-v2.1-to-v2.2.md`](./AMENDMENT-003-v2.1-to-v2.2.md) (v2.1→v2.2, corrects B5 tier direction + B6 layer→licence map),
[`AMENDMENT-004-v2.2-to-v2.3.md`](./AMENDMENT-004-v2.2-to-v2.3.md) (v2.2→v2.3, Art. XXI: LLM-provider agnosticism via the LiteLLM proxy).

This document is the authoritative constitution of the LOGOS decipherment-research platform.
`CLAUDE.md` carries a condensed pointer for day-to-day work; where the two differ, **this document
governs**. Amendments follow Article XXIII only. The v2.0 text is preserved in git history at the
commits before AMENDMENT-002.

---

## Preamble — Mission

LOGOS hunts a real decipherment of undeciphered scripts, beginning with Linear A, and refuses to
publish a fitted or theatrical one.

The discipline machinery is the weapon, not the mission. It exists to distinguish a real reading from a
pattern produced by search, leakage, dependency, wishful interpretation, or model capacity.

The highest objective is a reading that:

- predicts held-out material;
- reads inscriptions not used in its construction;
- survives adversarial verification;
- remains valid under source and feature perturbation;
- survives qualified external review;
- ideally predicts newly discovered inscriptions.

The project is ambitious by design. It does not exist merely to report nulls.

But ambition does not authorize overclaiming. A rigorous null, underdetermination result, route-specific
rejection, or no-power verdict is a successful scientific outcome when that is what the evidence
warrants. Such outcomes are the insurance policy against another false decipherment.

LOGOS may conclude that a method, hypothesis family, corpus configuration, or evidence channel is
underpowered or falsified.

LOGOS may not make unsupported global claims that Linear A is inherently or permanently undecipherable.

---

## Article I — The inscription is not the interpretation

The archaeological object is the territory.

Transcriptions, sign inventories, sign values, segmentations, glosses, ontologies, embeddings,
clusters, and language hypotheses are maps.

LOGOS must preserve a machine-readable distinction among:

```text
OBSERVED
SOURCE_REPORTED
DERIVED
MODEL_INFERRED
HYPOTHESIZED
ADJUDICATED
UNKNOWN
```

No derived representation may silently replace the underlying observation.

Every load-bearing datum must record:

```text
provenance
evidence_level
source_dependency
transformation_history
builder_version
confidence_class
artifact_hash
```

A claim is invalid if it cannot be traced back to the inscription, edition, or explicitly identified
derivation rule on which it depends.

---

## Article II — No claim without a committed prediction

LOGOS fails closed.

Before any verdict, the project must contain a committed, hash-addressed hypothesis record stating at
minimum:

```text
plan_hash
claim_layer
signs_or_forms_claimed
proposed reading or role
candidate language or family if applicable
falsifiable prediction
evaluation corpus
grouping rules
null model
acceptance threshold
rejection threshold
confidence class
authorized downstream action
```

No prediction means:

```text
NO_VERDICT
NO_CLAIM
NO_DOWNSTREAM_AUTHORITY
```

Exploratory analysis may generate hypotheses, but exploratory results are not confirmatory evidence.

---

## Article III — The proposer never certifies the claim

The component that proposes a reading, alignment, semantic role, phonetic value, cluster, or model may
not certify it.

Separate:

```text
proposal
data preparation
split construction
verification
null generation
power analysis
adjudication
final verdict
```

A verifier is not independent merely because it is mechanical.

For every verdict, LOGOS must record:

```text
proposer_id
verifier_id
shared_features
shared_sources
shared_model_family
shared_assumptions
independence_class
verdict_authority
```

Agreement between instances of the same model family is:

```text
MODEL_REPLICATION_AGREEMENT
```

not:

```text
INDEPENDENT_EXPERT_AGREEMENT
```

Mechanical verdicts are authoritative only when their target, data partition, and null are insulated
from the proposal process.

---

## Article IV — A decipherment is guilty until proven innocent

Internal fit on the derivation set is not evidence of decipherment.

Acceptance requires performance on evidence not used to create the hypothesis.

Preferred evidence order:

```text
1. newly discovered inscription
2. prospectively sealed inscription
3. independently held-out inscription
4. held-out site, scribe, series, or chronology
5. held-out lexical and morphological families
6. resampled internal validation
```

Lower levels do not substitute for higher ones when higher levels are available.

A failed hypothesis remains failed. It may be superseded by a new hypothesis, but it may not be silently
repaired after seeing the verdict.

---

## Article V — Claims graduate by layer

LOGOS distinguishes the following layers:

```text
L0  physical observation
L1  sign identification
L2  segmentation and document structure
L3  administrative or functional role
L4  semantic class
L5  lexical meaning
L6  phonetic value
L7  grammatical analysis
L8  language identification
L9  continuous translation
```

Evidence supporting one layer does not automatically authorize the next.

Examples:

- association with quantities may support a functional role;
- it does not by itself establish lexical meaning;
- a lexical proposal does not establish pronunciation;
- recurring phonetic correspondences do not by themselves establish language identity;
- language identity does not by itself validate a translation.

Every result must state:

```text
claim_layer
highest_authorized_layer
evidence_supporting_this_layer
evidence_required_for_next_layer
```

No result may be worded above its authorized layer.

---

## Article VI — Confidence is earned and mechanically deflated

Models, LLMs, embeddings, cognate matchers, clustering systems, and heuristic scorers produce signals,
not verdicts.

Their native confidence is advisory.

The ceiling of `0.75` for unverified model-generated claims is an **explicitly conventional governance
constant**, not a calibrated probability and not an epistemic threshold — it is an admitted convention whose
only empirical anchor is the gate false-graduation calibration (`scripts/gate_null_calibration.py`); it must
never be presented as a probability (**B8**).

Only mechanically verified held-out performance may authorize a higher project confidence class.

Allowed project confidence classes (this is the **confidence axis** — distinct from the **lifecycle status**
axis of the "Required status vocabulary"; a claim carries exactly one token from EACH axis, and where a token
appears on both lists it is disambiguated by axis, e.g. `confidence:SUPPORTED` vs `status:SUPPORTED` — **B2**):

```text
SPECULATIVE
EXPLORATORY
SUPPORTED
HELD_OUT_SUPPORTED
REPLICATED
PROVISIONALLY_ACCEPTED
ACCEPTED
```

**Mechanical class predicates (B5).** Graduation between classes is not discretionary — each class is
authorized by a deterministic predicate over (evidence tier from Article IV × `effective_n` from Article VIII
× deflated significance from Article VII), computed by code, never asserted:

Article IV numbers evidence strongest-first (1 = newly-discovered inscription … 6 = resampled internal
validation, which is in-sample). The predicates below are stated qualitatively so the ladder stays
monotonic with that ordering; **resampled internal validation (tier 6) NEVER satisfies a held-out
predicate** (corrected in AMENDMENT-003 — the earlier `tier >= N` phrasing inverted the ordering and let
in-sample resampling qualify):

```text
SPECULATIVE            no held-out evidence (exploratory only)
EXPLORATORY            in-sample / derivation-set fit only (incl. Art. IV tier 6 resampled internal)
SUPPORTED              beats the null (after deflation) on genuinely HELD-OUT data — any of Art. IV tiers 1-5; NEVER tier 6
HELD_OUT_SUPPORTED     SUPPORTED where the hold-out crosses a STRUCTURAL boundary — held-out SITE/SCRIBE/SERIES/CHRONOLOGY or unseen LEXICAL/MORPHOLOGICAL FAMILY (Art. IV tiers 1-2, 4-5), not merely a within-population inscription split (tier 3)
REPLICATED             HELD_OUT_SUPPORTED reproduced under an INDEPENDENT verifier (Art. III independence_class differs)
PROVISIONALLY_ACCEPTED REPLICATED + survives qualified external review
ACCEPTED               PROVISIONALLY_ACCEPTED + predicts a newly-discovered inscription (Art. IV tier 1)
```

**Licence caps confidence (B6).** A claim's confidence class is **capped by the transfer licence earned for
its claim layer (Article XV)**: the licence gate dominates. A claim at a layer that HAS a licence may not be
labeled above `SUPPORTED` unless that licence is held. The total layer→licence map (AMENDMENT-003, so no
layer is undefined) is:

```text
L0 physical observation      -> none (exempt from the cap — an observation is not a transfer claim)
L1 sign identification       -> none (exempt from the cap)
L2 segmentation/structure    -> STRUCTURAL_TRANSFER_LICENSE
L3 administrative/functional -> FUNCTIONAL_TRANSFER_LICENSE
L4 semantic class            -> SEMANTIC_TRANSFER_LICENSE
L5 lexical meaning           -> LEXICAL_TRANSFER_LICENSE
L6 phonetic value            -> PHONETIC_TRANSFER_LICENSE
L7 grammatical analysis      -> LANGUAGE_IDENTIFICATION_LICENSE (grammar is gated by the language-id licence)
L8 language identification    -> LANGUAGE_IDENTIFICATION_LICENSE
L9 continuous translation    -> TRANSLATION_LICENSE
```

L0/L1 are observation/identification, not transfer claims, so they are **exempt** from the cap (never
frozen at `SUPPORTED`). E.g. an L6 phonetic claim cannot be `HELD_OUT_SUPPORTED` while no
`PHONETIC_TRANSFER_LICENSE` is held.

Confidence must be deflated for:

```text
search breadth
source dependence
effective sample size
class imbalance
model selection
threshold selection
seed and restart search
post-hoc exclusions
missing channels
domain shift
```

---

## Article VII — Search creates epistemic debt

Every searched hypothesis increases the chance of accidental success.

LOGOS must maintain a complete search receipt containing:

```text
hypotheses tested
candidate languages tested
sign assignments tested
roots and lexica searched
feature families tested
model families tested
alignment methods tested
thresholds tested
seeds
restarts
subgroups
exclusions
post-hoc decisions
failed branches
```

Distinguish:

```text
preregistered breadth within one model
search across competing models
exploratory analysis
confirmatory evaluation
```

The entire adaptive discovery process—not merely the final model—must be represented under the null.

A match rate without a search receipt and multiplicity correction is not evidence.

---

## Article VIII — Evidence is independent constraint, not row count

LOGOS reports both:

```text
raw_n
effective_n
```

Evidence units may include:

```text
independent inscriptions
independent lexical families
independent morphological families
independent sites
independent scribal traditions
independent chronological strata
independent archaeological contexts
independent source lineages
independent structural constraints
```

The following do not automatically count as independent:

- duplicate editions;
- joined fragments;
- formula copies;
- spelling variants;
- repeated tablets from one administrative series;
- records derived from one lexicon;
- sources descending from one underlying edition;
- multiple rows from one document.

Graduation is based on `effective_n`, not raw corpus volume. Independence of evidence units is decided by
the operational test in Article XI (**B4**: distinct edition AND lineage AND no shared lexicon; DEPENDENT
until proven), and source-lineage collapse is computed by `scripts/source_dependency.py`.

Power must be simulated before expensive modelling and before opening a sealed evaluation.

---

## Article IX — The information floor is always visible

Every **inferential / graduating** claim must display an information-budget panel (**B7**: the panel is
required for any claim at layer L2 or above, or any claim seeking a confidence class ≥ `SUPPORTED`; bare L0/L1
OBSERVED data points, for which minimum-detectable-effect and power are undefined, are exempt — an observation
is not an inference).

At minimum:

```text
raw corpus size
effective independent evidence
sign inventory uncertainty
segmentation uncertainty
parameter count
search-space size
source-dependency structure
missing-feature burden
damage rate
class balance
domain shift
minimum detectable effect
estimated power
```

If the number of effective degrees of freedom exceeds the information available, the result is
underdetermined.

"Unicity distance" may be reported as an analogy or component, but it may not substitute for the
complete information budget.

---

## Article X — Corpus honesty and leakage control are mandatory

The corpus is versioned, reproducible, and point-in-time controlled.

Every experiment must pin:

```text
corpus_version
as_of_date
source_versions
normalization_version
split_manifest
family_grouping_manifest
artifact_hashes
```

Held-out evidence must not inform:

- hypothesis generation;
- feature selection;
- threshold selection;
- labeling-function design;
- ontology tuning;
- null construction;
- model selection;
- exclusion rules.

Grouping must prevent leakage across:

```text
lexical families
morphological families
orthographic variants
formula clusters
joined fragments
scribal copies
duplicate records
source-derived aliases
```

A leakage defect blocks the verdict until corrected or invalidated.

---

## Article XI — Source agreement is not independence

Every source must belong to a dependency graph.

For each source, record:

```text
bibliographic identity
version
underlying edition
upstream lexicon
derived databases
shared decipherment tradition
known disputes
license
access date
```

Sources from one dependency family count as one evidentiary lineage unless genuine independence is
demonstrated.

**Genuine independence (operational test, B4).** Two sources are independent ONLY if ALL hold: (i) a
distinct underlying edition, AND (ii) a distinct decipherment/reading lineage, AND (iii) no shared upstream
lexicon. The default is **DEPENDENT until independence is proven** (Article VIII likewise). This test is
enforced mechanically by `governance/source_dependency_graph.json` + `scripts/source_dependency.py`, which
collapses cited sources to distinct lineages and reports `effective_n` = the number of independent
evidentiary votes (feeding Article VIII). An unassessable (unknown) source fails loud (Article XVI), never
counting as independent.

Concordance across dependent sources may strengthen provenance, but it may not be presented as
independent replication.

---

## Article XII — Never grade a target using the rule that created it

A structural rule may generate supervision, but it may not define the load-bearing answer used to prove
that the same structure was recovered.

Examples of circular evaluation include:

- assigning `QUANTITY` because a numeral is present, then claiming the model recovered quantity from
  numeral presence;
- assigning commodity roles from logogram identity, then grading a model that reads the same logogram;
- using document series to define a role and then claiming cross-document semantic recovery.

Every target must declare:

```text
target_source
feature_overlap
circularity_risk
firewall_status
```

Load-bearing evaluation targets must be independent of the features used to predict them.

---

## Article XIII — Robustness means removing the strongest convenience

Every load-bearing claim must survive the removal or perturbation of its most convenient support.

Required stress tests (B3 — every item **applicable to the claim's layer/data is MANDATORY**; any omission
must be recorded as an explicit deviation under Article XXII, never silently skipped) include:

```text
remove lexical identity
remove site
remove document series
remove scribal hand
remove source-family duplication
remove the strongest correspondence
remove dominant classes
remove high-frequency forms
remove the most informative notation channel
permute sign identities
apply target-like degradation
```

A claim that survives only while one fragile relationship is assumed stable is not robust.

Low apparent variance is treated as possible fragility until stress tests show otherwise.

---

## Article XIV — When the linguistic axis is unknown, survive by architecture

When the unknown dimension cannot be specified, LOGOS relies on architecture rather than confident
prediction.

Required protections include:

```text
reversible stages
bounded claims
strict semantic firewalls
sealed evaluation
pseudo-script controls
known-script validation
feature compatibility tests
domain-shift audits
mechanical circuit breakers
```

No downstream interpretation may be used to justify an upstream representation.

All pipelines must support rollback to the last valid frozen stage without rewriting prior history.

---

## Article XV — Transfer authority must be earned on a readable script

Before LOGOS assigns roles, meanings, or sounds to Linear A, the full method must succeed on a
readable-script analogue in which the model is denied the answer.

Required controls (B3 — every control **applicable to the claim's layer is MANDATORY**; any omission must be
recorded as an explicit deviation under Article XXII, never silently skipped) include:

```text
opaque-sign Linear B
independently permuted sign inventories
unseen lexical-family holdout
unseen morphological-family holdout
cross-site transfer
cross-series transfer
Linear-A-like feature degradation
source-dependency control
complete end-to-end nulls
```

Success on ordinary Linear B with visible readings is insufficient.

LOGOS recognizes the following transfer licences:

```text
STRUCTURAL_TRANSFER_LICENSE
FUNCTIONAL_TRANSFER_LICENSE
SEMANTIC_TRANSFER_LICENSE
LEXICAL_TRANSFER_LICENSE
PHONETIC_TRANSFER_LICENSE
LANGUAGE_IDENTIFICATION_LICENSE
TRANSLATION_LICENSE
```

Each licence has separate prerequisites.

A lower licence never implies a higher one.

---

## Article XVI — Fail loud and fail closed

Every stage must define:

```text
entry gate
success gate
failure states
authorized downstream actions
forbidden downstream actions
```

Allowed failure states include:

```text
NO_POWER
REJECT_ARCHITECTURE
INCOMPLETE
SOURCE_BLOCKED
DEPENDENCY_COLLAPSE
TRIVIAL_RECOVERY
LEAKAGE_DETECTED
UNDERDETERMINED
DOMAIN_SHIFT_FAILURE
```

There is no silent amber state that permits unauthorized downstream claims.

When a load-bearing gate fails, execution stops unless a new, explicitly versioned experiment is opened.

---

## Article XVII — The record is immutable; corrections are annotations

Predictions, preregistrations, verdicts, audit rows, hashes, failed routes, and sealed-evaluation
openings are append-only.

Errors are corrected through:

```text
ERRATUM
SUPERSEDING_ANALYSIS
INVALIDATION_NOTICE
DEPENDENCY_DISCOVERY
PROTOCOL_DEVIATION
RETRACTION
```

Never silently delete or rewrite a failed claim.

Every result records:

```text
original_status
current_status
superseded_by
reason
timestamp
commit
artifact_hash
```

The honest forward clock begins where the corrected protocol became sound.

---

## Article XVIII — Every load-bearing assumption is explicit, verified, and pinned

Maintain an assumption register.

Each assumption records:

```text
assumption_id
statement
load_bearing
verification_method
verification_result
verified_at
source_or_test
expiry_condition
status
```

Allowed statuses:

```text
VERIFIED
FALSE
PARTIAL
UNKNOWN
STALE
```

Examples include:

- site metadata exists and is correctly mapped;
- scribal-hand metadata is populated;
- Linear A logograms are parsed;
- two sources are independent;
- the target corpus supports the source feature set;
- the model cannot access transliteration;
- the split blocks lexical-family leakage.

A false load-bearing assumption blocks downstream execution.

Finding a false premise creates an obligation to correct, annotate, or invalidate the affected work.

---

## Article XIX — Deterministic governance, reproducibility, and deduplication

Hypotheses, readings, plans, corpora, splits, and verdicts are content-addressed.

Inserts are idempotent.

Replays, retries, and crashes must not create duplicate scientific records.

Counts are generated, never hand-written.

Any claim of:

```text
N inscriptions
N signs
N forms
N hypotheses
N families
N effective units
```

must come from a reproducible script and pinned artifact.

The LLM proposes.

Deterministic code governs:

```text
identity
deduplication
splits
power calculations
multiple-testing correction
risk rules
confidence deflation
gate status
verdict status
```

---

## Article XX — Open by default, licensed data excepted

The following are public by default:

```text
corpus tooling
normalization code
label schemas
split logic
verdict methodology
null generators
power simulations
search receipts
model configurations
audit reports
failed experiments
```

Licensed or restricted raw source material may remain gitignored.

Where raw data cannot be published, LOGOS must publish:

```text
source citation
license status
download instructions where permitted
transformation code
artifact hashes
derived schema
reproducibility limitations
```

---

## Article XXI — Tooling constraints are operational, not epistemic

Operational constraints must be explicit.

Current defaults (v2.3, AMENDMENT-004):

```text
LLM access:
  Provider-agnostic through the approved LiteLLM proxy (nllei01litellm01:4000).
  $LOGOS_LLM_BACKEND DEFAULTS to litellm (z.ai/GLM) per the owner directive
  ("everything must be using z.ai"); ollama is the explicit local fallback.
  The proxy holds all vendor keys; logos holds only a scoped LiteLLM virtual key
  via env / an untracked secret file (runtime/secrets/litellm.env, gitignored).
  Backends wired: z.ai/GLM (default), local Ollama, Mistral/Codestral/Devstral.

Prohibited:
  Setting ANTHROPIC_API_KEY in-process; committing any raw vendor key to the repo.

Local models:
  Ollama on the approved GPU host (reachable directly or through the proxy).
```

These rules govern execution and cost control.

They do not grant epistemic privilege to a particular model or vendor. The proposer LLM is a
capped signal (Art. VI; invariants #2/#4/#5) and is never on the verdict path, so the tests are
LLM-agnostic by construction: changing the proposer model may change which hypotheses are explored,
never a mechanically-computed verdict.

A model change requires a recorded compatibility and reproducibility note (see
`AMENDMENT-004-v2.2-to-v2.3.md`).

---

## Article XXII — The constitution governs execution

Every research stage must open by recording:

```text
articles_consulted
articles_triggered
required gates
assumptions checked
authorized outputs
forbidden outputs
```

Every final report must record:

```text
constitutional compliance
deviations
violations
waivers
amendments required
```

A workaround that evades a constitutional gate is itself a violation.

---

## Article XXIII — Amendments are explicit and versioned

The constitution may be amended only through a committed amendment record containing:

```text
old text
new text
reason
scientific consequence
affected experiments
retroactivity
approver
date
commit
```

Silent constitutional changes are forbidden.

An amendment may not retroactively convert a failed result into a success.

---

# Claim and licence matrix

## Structural Transfer Licence

Allows:

- anonymous document templates;
- recurrence patterns;
- row and entry roles;
- notation associations;
- cluster stability;
- layout structure.

Does not allow:

- semantic names;
- lexical meanings;
- phonetic values.

## Functional Transfer Licence

Allows bounded functional descriptions such as:

- header-like;
- allocation-like;
- quantity-bearing;
- subtotal-associated;
- recipient-like;
- source-like.

Requires readable-script validation and observable-channel grounding.

## Semantic Transfer Licence

Allows coarse semantic-role probabilities.

Requires held-out pseudo-script success, unseen-family success, source-firewalled targets, and
domain-shift survival.

## Lexical Transfer Licence

Allows proposed word meanings.

Requires multiple independent constraints and prospective held-out predictions.

## Phonetic Transfer Licence

Allows proposed sign values or readings.

Requires non-trivial external anchors, leave-one-anchor-out stability, and multiplicity-corrected
held-out success.

## Language Identification Licence

Allows formal ranking of candidate languages.

Requires phonetic authority, morphology, syntax, and held-out comparative predictions.

## Translation Licence

Allows continuous translation claims.

Requires all lower licences plus grammatical and contextual coherence on sealed and prospective texts.

---

# Required status vocabulary

This is the **lifecycle status** axis, distinct from the Article VI **confidence** axis (**B2**); a claim
carries one token from each, disambiguated by axis where a token (e.g. `SUPPORTED`, `EXPLORATORY`) appears on
both. Use only explicit project statuses (the failure states enumerated in Article XVI — `DEPENDENCY_COLLAPSE`,
`LEAKAGE_DETECTED`, `DOMAIN_SHIFT_FAILURE` — are part of this closed vocabulary, **B1**):

```text
PROPOSED
EXPLORATORY
PREREGISTERED
RUNNING
COMPLETE
SUPPORTED
REFUTED
NO_POWER
INCOMPLETE
SOURCE_BLOCKED
REJECT_ARCHITECTURE
TRIVIAL_RECOVERY
UNDERDETERMINED
DEPENDENCY_COLLAPSE
LEAKAGE_DETECTED
DOMAIN_SHIFT_FAILURE
SUPERSEDED
INVALIDATED
RETRACTED
```

Avoid ambiguous status words such as:

```text
PROMISING
LIKELY
PARTIAL SUCCESS
NEARLY VALIDATED
```

unless accompanied by a mechanically defined meaning.

---

# Repository conventions

- Commits end with the required `Co-Authored-By` trailer.
- The default branch is `main`.
- Silver corpus lives under `corpus/silver/`.
- Gold/evaluation stores are versioned, queryable, and firewalled.
- Dated claim analyses live under `docs/`.
- Runbooks live under `docs/runbooks/`.
- Stable invariants live in `CLAUDE.md`.
- Constitutions and amendments live under `governance/`.
- Search receipts, assumption registers, and licence states are machine-readable.
- Before inventing new infrastructure, inspect:
  - `../finops-agora`
  - `../claude-gateway`

---

# One-line governing rule

> LOGOS exists to crack undeciphered scripts, but its authority to claim success rests entirely on its
> ability to detect when it has fooled itself: every hypothesis is guilty until independent held-out
> evidence proves it innocent, every claim is capped at its earned layer, the machine—not the
> proposer—decides, and every honest negative remains part of the permanent scientific record.
