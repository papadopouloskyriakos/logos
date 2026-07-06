# PREREGISTRATION — One-shot Cretan-anchor confirmatory test (v2, hardened)

**Status: DRAFT v2 — NOT MINTABLE YET (preconditions pending, §15).** This document commits a
falsifiable prediction *before* execution (invariant 1, fail-closed). It reports no outcome. The
plan_hash stays **empty** until every §15 precondition is met; only then is the hash minted and the
test run. v1 was withdrawn after an adversarial red-team (`wf_3bfac2b3-fdf`, verdict REVISE_THEN_COMMIT)
found 6 blockers — see `REDTEAM_cretan_prereg_response.md`; v2 closes them.

- **id:** `cretan-anchor-oneshot-v2` · **as_of:** 2026-07-06 · **channel:** Egyptian external-anchor

---

## 0. What v2 changed (why the naive test was invalid)

The Cretan toponyms' Egyptian and Linear B consonant skeletons are **near-identical** (Lyktos `r-k-t` =
`r-k-t` exactly; Knossos `k-n-š`≈`k-n-s`). So the honest danger is **triviality**: a model-free
string-similarity ranker, or a model that only knows *generic Egyptian sign values*, would "recover" the
targets while the **Semitic-trained correspondence does zero work**. v2 therefore (a) adds two model-free
baselines the frozen model must **beat** to claim anything, (b) splits the verdict so a recovery that the
identity baseline also achieves is reported as **trivial, not generalization**, (c) replaces the invalid
i.i.d. binomial with a joint permutation test, (d) fixes skeletonization into one blind function, (e)
selects anchors by a skeleton-blind rule, and (f) confronts the fact that Edel *read the eroded ovals
using the Greek identifications* (a reading-independence leak).

## 1. Question and hypotheses

Does the **frozen** Egyptian→foreign correspondence model (fit **only** on non-Cretan Semitic loanwords)
recover the Linear B forms of the Kom el-Hetan Cretan ovals **AND add discriminating power beyond
model-free string overlap and generic Egyptian orthography**?

- **H1 (generalization):** the frozen M2 recovers the targets at top-1 above the scramble null **and by a
  positive margin over BOTH the identity baseline and the generic-Egyptian-sign-value ablation**.
- **H1′ (recovery-only):** M2 recovers the targets above the scramble null, but **not** above the two
  model-free baselines → recovery is skeleton near-identity, **no generalization is shown**.
- **H0 (assumed true until refuted — invariant 3):** recovery is at the empirical-null rate.

A PASS on H1 is a positive control that the **Semitic-trained** correspondence generalizes to the Aegean.
H1′ is the honest "recovered-but-trivial" outcome. Neither reads any undeciphered script; result capped
≤ 0.75, **non-compounding** (invariant 5).

## 2. Frozen inputs (committed, hashed)

| Input | Artifact | sha256₁₆ | Status |
|---|---|---|---|
| Target set | `frozen/cretan_confirmatory_targets.json` | `6903f5f1` | committed |
| Model spec | `configs/egyptian_model_freeze.json` | `3c56ed71` | committed |
| Calibration corpus (post-holdout) | `data/gold/…handverified.jsonl` → collision-holdout applied (§11) | **TBD** | pending §11 |
| Skeletonizer `f()` | `src/calibration/skeleton.py` | **TBD** | pending §3 |
| Identity baseline `B_id` | in `src/calibration/cretan_test.py` | **TBD** | pending |
| Generic-Egyptian ablation `B_egy` | frozen sign→consonant table | **TBD** | pending |
| Candidate pool | `frozen/lb_toponym_pool.json` | **TBD** | pending §4 |
| Verdict script | `src/calibration/cretan_test.py` | **TBD** | pending |

The model is M2 refit deterministically from the **post-holdout** corpus per spec `3c56ed71`; **zero
parameters fit to Cretan data**.

## 3. Skeletonization `f()` and anchor selection (both blind)

**One deterministic, hash-pinned function `f(transliteration) → consonant tuple`**, applied *identically*
to (i) every Egyptian oval, (ii) every target LB form, (iii) every pool member. `f()` pins the
conventions **inside** it so no answer-aware preprocessing leaks in: **aleph (ꜣ/ʾ) and ayin (ʿ) are
vowel-carriers → dropped on both sides; glides j/w/y as vowel-carriers → dropped; š and s are kept
distinct** (any š≡s equivalence must be *earned by the model*, not preprocessed). Assertion enforced at
run start: `f(target_LB)` is byte-identical to that target's entry in the frozen pool. This resolves the
v1 Amnisos discrepancy: `f`(a-mi-ni-so)=`m-n-s`, `f`(ʾ-m-n-š)=`m-n-š` (leading aleph dropped as a
vowel-carrier on both sides). *(The frozen target file's parenthetical "(ʾ)" is a vowel-carrier `f` drops.)*

**Anchor set by a skeleton-blind, model-blind mechanical rule** (evaluated on properties knowable without
the match): a primary anchor is every En-list oval that is (a) identified as a **Cretan** toponym,
(b) **non-palimpsest**, (c) a **surviving** oval (not a lost/reconstructed li 14/15), and (d) **not marked
*fraglich*** by Edel. This rule *deterministically* yields **{Knossos li 10, Amnisos li 11, Lyktos li 12}**
— the reduction from the 6 collated Cretan/near-Cretan ovals is by these answer-blind criteria, **not** by
match cleanliness. Phaistos/Kydonia are excluded because they are palimpsest + reconstructed-original;
Kythera because it is not Cretan. All model-behaviour annotations (e.g. the v1 "l→r correspondence the
model learned" note) are **struck** from the frozen file (they encode outcome knowledge).

## 4. Candidate pool (one source, blind, confusability-floored)

Built once, before any scoring, frozen to `frozen/lb_toponym_pool.json`:
1. **One committed source** (no fork): all Linear B **place-names** in DĀMOS at a pinned version/query
   (`scripts/cross_script/data.py`); inclusion/exclusion of ethnica/derivatives/restorations/compounds
   stated as an explicit predicate. Every target LB skeleton must be present and **unique** in the pool.
2. **Confusability floor:** each target must have **≥3 distractors within edit-distance ≤1** of its
   skeleton, else `NO_POWER` (an isolated target is recoverable by raw overlap with the model doing no
   work). Record `M = |pool|` and the per-target confusable-set sizes.

## 5. Procedure (mechanical — the model never grades itself, invariant 2)

Committed, hash-pinned `src/calibration/cretan_test.py` refits M2 (post-holdout corpus, spec `3c56ed71`),
then for each anchor ranks all pool skeletons by four scorers — **M2**, **`B_id`** (edit-distance /
consonant-multiset overlap, no parameters), **`B_egy`** (generic Egyptian sign→consonant values, no
Semitic fitting), and the **scramble** family — recording the true skeleton's rank under each. **Ties at
rank 1 = not recovered**, applied bit-identically across all scorers. Emits the verdict JSON.

## 6. Statistics — joint permutation test (replaces the invalid binomial)

Let `r1(scorer)` = number of primary anchors with the true skeleton at rank 1 under that scorer.
- **Null distribution:** a **joint Monte-Carlo permutation** — draw `N ≥ 10,000` scrambled correspondence
  maps; for each, score **all** anchors against the **same** pool and record `r1`. This carries the
  shared-pool / shared-map correlation and skeleton overlap with **no i.i.d. assumption**.
- **p-value:** `p = (1 + #{replicates with r1 ≥ r1(M2)}) / (1 + N)` (never 0).
- Report the full null distribution of `r1`, and `r1(B_id)`, `r1(B_egy)` computed on the same pool.

## 7. Decision rule (locked, two-tier)

- **NO_POWER** iff `M < 30` **or** any target fails the §4 confusability floor. Reported, never a PASS.
- **REFUTE** iff `r1(M2) ≤ 1` **or** `p ≥ 0.05`.
- **RECOVERED_TRIVIAL** iff `p < 0.05` and `r1(M2) ≥ 2` **but** `r1(M2) ≤ max(r1(B_id), r1(B_egy))`
  → recovery is skeleton near-identity / generic orthography; **generalization NOT shown**.
- **CONFIRM_GENERALIZES** iff `p < 0.05` **and** `r1(M2) ≥ 2` **and** `r1(M2) > r1(B_id)` **and**
  `r1(M2) > r1(B_egy)` → the Semitic-trained correspondence adds discriminating power.

The strong claim (§13) attaches **only** to `CONFIRM_GENERALIZES`. `2/3` reads as "null excluded,
provisional"; `3/3` is required for unqualified language.

## 8. Multiple-testing discipline (invariant 8)

The primary set is chosen by the §3 mechanical rule, not by match quality; the reduction 6→3 is deflated
for as a choose-rule (report what the rule *could* have admitted). Phaistos/Kydonia/Kythera + the full
6-oval list are a **symmetric** secondary analysis with a pre-committed interpretation (a secondary FAIL
counts against, not merely "sensitivity"). Skeletonizer, pool source, baseline definitions, `N`, and the
tie rule are all pinned before freeze — no post-hoc scorer/threshold selection.

## 9. Information floor (invariant 7)

Zero free parameters fit to Cretan data. Surprisal is reported as `−log₂(p_empirical)` and per-target
confusable-set size (**not** `log₂ M`, which would overstate it). The `B_id`/`B_egy` increments quantify
how much of any recovery is *not* attributable to string identity or generic orthography.

## 10. Power

Gate estimates (matched short-anchor scarcity): recovery ≈ 0.685, min detectable = 2 anchors,
`P(NO_POWER at K=3)=0.031`. Additionally, `NO_POWER` unless the empirical null admits a clearable
endpoint (the realistic `r1=2` must reach `p<0.05` under the §6 permutation null); otherwise the pool is
declared underpowered rather than run.

## 11. Leakage / PIT (invariant 9)

- **Corpus exclusion is by SKELETON, not label.** State the exact exclusion predicate; then remove from
  training every pair whose Egyptian **or** foreign skeleton equals any target skeleton (within
  Levenshtein 1); report the count removed and the resulting corpus sha. This upgrades "zero Cretan data"
  to **"zero target-skeleton information."**
- **Reading independence (the deepest issue).** Edel read the eroded ovals **using** the Greek/LB
  identifications, so the Egyptian skeleton is **not** cleanly independent of the answer. Precondition:
  source the fold-out **Falttafeln 13/14** for sign-level oval readings independent of the toponym ID;
  drop any anchor whose skeleton is reconstructed from the identification. Until then, the test scores
  against **Edel's ID-informed readings**, and the claim is scoped to "recovers Edel's readings" with this
  leak stated — **not** "independently known."
- Pool built blind to scores; `as_of` of every input strictly precedes the run (enforced by freeze-commit
  timestamp; fail-closed unless the run clock postdates it).

## 12. One-shot, no-pilot, deviations

- Runs **once**. A REFUTE / RECOVERED_TRIVIAL is a real, publishable result — never a prompt to retune.
- **No-pilot attestation** (required at freeze): "M2 (spec `3c56ed71`, post-holdout corpus) has never been
  scored against these ovals or any candidate pool prior to this freeze." Freeze and run are separate,
  ordered, timestamped git events.
- Any deviation voids the plan_hash and requires a fresh preregistration.

## 13. Interpretation (scaled, capped, non-compounding)

- **CONFIRM_GENERALIZES (3/3):** the Semitic-trained correspondence demonstrably generalizes to real
  Aegean toponyms, beating identity + generic-Egyptian + scramble baselines — provisional pending
  Falttafeln sign-level confirmation (§11). Signal ≤ 0.75, **non-compounding** (a chain of capped signals
  may not launder to >0.75). "Licenses" means **permits PROPOSING** a separately pre-registered, separately
  power/leakage-gated downstream probe (vocalization / Linear A place-names → then, only then, a
  sound-JEPA) — it is **not** auto-authorization, and the §14 firewall stands.
- **CONFIRM_GENERALIZES (2/3):** "null excluded, provisional"; one primary missed — weaker language only.
- **RECOVERED_TRIVIAL:** the Egyptian and Aegean skeletons are near-identical; the test says nothing about
  generalization. Report as such; do **not** brand a "validated instrument."
- **REFUTE:** the correspondence does not generalize to the Aegean; the anchor route is closed.
- **NO_POWER:** pool cannot support the test; stop (do not weaken the pool to force power).

## 14. Firewall (non-negotiable)

These Cretan targets are confirmatory targets for the **Egyptian** channel only and must **never** enter
Linear A hypothesis formation or scoring.

## 15. Preconditions before the plan_hash is minted (all required)

1. `f()` (`src/calibration/skeleton.py`) written, hash-pinned; the `f(target_LB)==pool_entry` assertion passes.
2. Identity baseline `B_id` and generic-Egyptian ablation `B_egy` implemented + hash-pinned.
3. Corpus skeleton-collision hold-out applied; exclusion predicate stated; new corpus sha recorded.
4. Pool frozen from one committed source with the confusability floor + uniqueness checks; sha recorded.
5. `src/calibration/cretan_test.py` (joint permutation, `N≥10,000`) written, reviewed, hash-pinned.
6. Falttafeln 13/14 sourced for sign-level reading independence — **or** the claim explicitly scoped to
   "recovers Edel's ID-informed readings" with the leak documented per anchor.
7. No-pilot attestation recorded; freeze committed with a timestamp preceding any run.
8. plan_hash = sha256 of the canonical hypothesis row **including** all the above hashes; then, and only
   then, run once.

*Companion machine-readable row: `prereg/prereg_cretan_anchor_test.json` (plan_hash empty until §15 done).*
