# Revision-queue: CSA corpus-size sufficiency sweep — novelty audit + required rewordings

**Status:** revision / F1b-addendum material ONLY — the paper stays byte-frozen through TACL
review; nothing under `paper/` was read or written here. The sweep enters the record via the
`imports/E201_F1B/` boundary and **cannot alter any frozen conclusion** (see
[[logos2-campaign]] closure). Date: **2026-07-14**.

## TL;DR

Two adversarial research workflows audited whether the CSA cross-script corpus-size sufficiency
sweep is novel. **Verdict: `NOVEL_WITH_CAVEATS`, and it held under a 14-pass scoop-hunt** (7
hunts + 7 independent rechecks; no direct or strong scoop). Two claims take **partial**
preemption and need a **one-sentence reword + citations each** — *not* a retraction. The
story-carrying claims (size is not the lever; syllabary success is anchor-dependent) are intact.

**Total action = rewrite 2 sentences + add ~6 citations, in the addendum only.**

## The four claims and their audited status

- **N1 — integrated instrument** (same unsupervised matcher × graded-N size sweep × abjad-vs-
  syllabary contrast × positive control × calibrated null gate): **core survives intact**; only
  the *"positive-control-then-null protocol" framing* sub-claim is partially preempted (C7).
- **N2 — flat-with-corpus-size negative at Linear-A scale** (size is not the binding constraint):
  **fully intact.** Untested anywhere located; the field only asserts the folk "corpus too
  small" claim (the *opposite* of a demonstration). The 2024 *Computational Linguistics*
  systematic review has no corpus-size ablation.
- **N3 — anchor-dependence collapse** (SOTA matchers hit 86–89% on syllabaries only because fed
  pre-grouped cognate lexica / known target / proper-noun anchors; anchor-free → ~3–16%):
  **intact and corroborated**, not scooped — Tamburini 2025 and Luo 2019 are the very setups the
  claim characterizes.
- **N4 — calibrated random-mapping false-graduation gate** (~0.6% empirical FDR): **application
  survives; the underlying permutation-null *method* is prior art** (C6).

## ACTION 1 — N4 wording (triggered by C6)

Do **not** present the random-permutation / best-of-N null as a *new statistical test*. Claim
only the **application** to an end-to-end decipherment verdict.

- ❌ ~~"we introduce a best-of-100 random-map null gate"~~
- ✅ "we apply a calibrated random-**mapping** false-graduation **gate** — a permutation null in
  the tradition of Kessler (2001) and List's LexStat (2012) — to the end-to-end decipherment
  verdict, reporting an empirical ~0.6% false-graduation rate (Clopper–Pearson 95% upper
  ≈1.54%)."
- Add: Kessler 2001, List 2012, a max-of-N baseline reference. **Contrast** Berg-Kirkpatrick &
  Klein 2013 ("Million Random Restarts" — random restarts *find the true key*, opposite purpose;
  cite to pre-empt reviewer confusion).

## ACTION 2 — N1 protocol framing (triggered by C7)

Frame "positive-control-on-a-known-script THEN calibrated null gate before the target" as
**formalizing/integrating standard sanity-check practice into one named, sequenced instrument** —
not inventing the constituent moves.

- ❌ ~~"our protocol: validate on a known script, then gate"~~ (reads as invention)
- ✅ "Validating a matcher on a decipherable script is standard practice (Knight 1999; Luo 2019;
  Tamburini 2023/2025); our contribution is to **pair** that positive control with an empirical
  best-of-N false-graduation gate as the *disposal rule before* the undeciphered target — as a
  single named, sequenced instrument. No located paper pairs the two this way."
- Add: Luo 2019, Tamburini 2023/2025, Knight 1999, Sproat (writing-system null work). Core N1
  instrument is **not** narrowed — only this framing component.

## Citations to add (BibTeX — VERIFY keys/venues against the actual PDFs before compiling)

> These were surfaced by web-research subagents; treat details as provisional until checked
> against the paper (constitution: don't present unverified as verified). Items flagged
> **[VERIFY]** need a look at the source before use.

```bibtex
@book{kessler2001significance,
  author={Kessler, Brett},
  title={The Significance of Word Lists: Statistical Tests for Investigating Historical Connections Between Languages},
  year={2001}, publisher={CSLI Publications}, address={Stanford, CA}}

@inproceedings{list2012lexstat,
  author={List, Johann-Mattis},
  title={LexStat: Automatic Detection of Cognates in Multilingual Wordlists},
  booktitle={Proc. EACL 2012 Joint Workshop of LINGVIS \& UNCLH}, year={2012},
  url={https://aclanthology.org/W12-0216/}}

@inproceedings{bergkirkpatrick2013restarts,
  author={Berg-Kirkpatrick, Taylor and Klein, Dan},
  title={Decipherment with a Million Random Restarts},
  booktitle={Proc. EMNLP 2013}, year={2013},
  url={https://aclanthology.org/D13-1087/}}

@inproceedings{luo2019neural,
  author={Luo, Jiaming and Cao, Yuan and Barzilay, Regina},
  title={Neural Decipherment via Minimum-Cost Flow: From Ugaritic to Linear B},
  booktitle={Proc. ACL 2019}, pages={3146--3155}, year={2019},
  url={https://aclanthology.org/P19-1303/}}

@article{tamburini2025csa,
  author={Tamburini, Fabio},
  title={On automatic decipherment of lost ancient scripts relying on combinatorial optimisation and coupled simulated annealing},
  journal={Frontiers in Artificial Intelligence}, volume={8}, pages={1581129}, year={2025},
  doi={10.3389/frai.2025.1581129}}

@inproceedings{tamburini2023cawl,   % [VERIFY exact title]
  author={Tamburini, Fabio}, title={<verify>},
  booktitle={Proc. Workshop on Computation and Written Language (CAWL) 2023}, year={2023},
  url={https://aclanthology.org/2023.cawl-1.10/}}

@inproceedings{sogaard2018limitations,
  author={S{\o}gaard, Anders and Ruder, Sebastian and Vuli{\'c}, Ivan},
  title={On the Limitations of Unsupervised Bilingual Dictionary Induction},
  booktitle={Proc. ACL 2018}, year={2018}, url={https://aclanthology.org/P18-1072/}}

@article{corazza2024review,          % [VERIFY full author list + page range]
  author={Corazza, Michele and others and Ferrara, Silvia},
  title={A Systematic Review of Computational Approaches to Deciphering Bronze Age Aegean and Cypriot Scripts},
  journal={Computational Linguistics}, volume={50}, number={2}, year={2024},
  url={https://aclanthology.org/2024.cl-2.7/}}

@book{barber1974decipherment,
  author={Barber, E. J. W.},
  title={Archaeological Decipherment: A Handbook},
  year={1974}, publisher={Princeton University Press}, address={Princeton}}

@inproceedings{knight1999deciphering,  % [VERIFY — "Knight 1999"; likely Knight & Yamada 1999]
  author={Knight, Kevin and Yamada, Kenji},
  title={A Computational Approach to Deciphering Unknown Scripts},
  booktitle={ACL Workshop on Unsupervised Learning in NLP}, year={1999}}

% [VERIFY] Sproat writing-system null-measure reference — adjudicator cited "W99-0906",
% but the apt one may be Sproat 2014 (Language) or the Rao–Sproat entropy exchange. Check
% before citing.

% [VERIFY] max-of-N random-baseline technique reference, e.g.
% "Stronger Random Baselines for In-Context Learning", arXiv:2404.13020 (2024).
```

## What NOT to touch

N1 core instrument, **N2**, **N3** survive intact and carry the paper's message ("text isn't the
lever, anchors are"). No edits there beyond adding the corroborating cites (Luo 2019, Tamburini
2025 for N3; Corazza/Ferrara 2024 + Barber 1974 for N1/N2 "no prior controlled size sweep").

## Honesty caveats (state these in the addendum, don't hide them)

- This is a **search-based** negative, not a proof. Phrase as *"we found no prior work that…"*,
  never *"no prior work exists."*
- C5/C6 confidence is **medium**: the null-methods / cryptanalytic-baseline space is large and
  negative evidence over it is incomplete; the empirical-null idea is "in the air" across fields
  (cryptanalytic wrong-key randomization; proteomics decoy-FDR; LLM-watermark nulls). The N4
  narrowing (Action 1) handles this.
- The "2024 CL review is silent ⇒ no prior size sweep" step is an **argument from absence** —
  strong (two disjoint-query passes found nothing) but not positive confirmation.
- N3's *demonstration* novelty (not its correctness) would narrow if an overlooked Tamburini/Luo
  supplementary ran an anchor-strip experiment; current evidence: Tamburini 2025 ships code only,
  no such supplement.

## Provenance (reproduce / re-audit)

- Prior-art workflow: run `wf_f523535c-805` (9 papers, discover→adversarial-verify→synthesize);
  verdict `NOVEL_WITH_CAVEATS`. Transcript:
  `subagents/workflows/wf_f523535c-805/journal.jsonl`.
- Scoop-hunt workflow: run `wf_28fa900b-487` (7 checks × 2 independent passes + adjudication);
  5/7 `no_scoop`, C6/C7 `partial_preemption`; verdict unchanged. Transcript:
  `subagents/workflows/wf_28fa900b-487/journal.jsonl`.
- Sweep data: `runtime/csa_sweep/cells/*.json`; accuracy-vs-size figure data in
  `scratchpad/plot_data.json` (published artifact "The syllabary wall").
- Scripts: `workflows/scripts/csa-sweep-prior-art-*.js`,
  `workflows/scripts/csa-sweep-scoop-hunt-*.js`.

---

# PRE-REGISTRATION — instrument-ablation tests T1 / T2 / T3 (FROZEN BEFORE RUN)

**Frozen:** 2026-07-14. **`plan_hash` = the git commit that adds this section** (this file's
commit SHA); no test below may be run against a working tree that predates that commit, and
results are recorded append-only under a `## RESULTS` heading that this section does not yet
contain. **Scope/layer:** these are **L0 methodological / instrument-property** tests. They test
the *novelty and load-bearingness of the gate*, NOT the decipherment verdict. **They cannot
raise the earned claim layer, cannot change the frozen paper, and cannot turn the null
decipherment result into a positive one** (Art. XII: a target is never graded by the rule that
created it; Art. XVII: append-only). Articles triggered: I (committed falsifiable prediction,
fail-closed), VII (search receipt — the two prior-art workflows), XII, XVII, XVIII (assumptions
below). Compliance line to emit at close: each test resolves to exactly one of
`SUPPORT / REFUTE / NARROW / NO_POWER` by the frozen rule, no free-text upgrade.

**Shared assumptions (Art. XVIII):** (A1) the five known-answer analogs already in
`runtime/csa_sweep/cells` are a fair stand-in for the instrument's behaviour; (A2) "recovery
accuracy" = `found/total` word-mapping match vs the held-back true reading, as already logged;
(A3) 4 seeds/condition, reusing the sweep's seed protocol `[0,1,2,3]`; (A4) all verdicts computed
by a committed script, never by eye. **If an assumption fails, the affected test returns
`NO_POWER`, not a soft pass.**

## T1 — Component ablation (defends N1: the composition is load-bearing)

- **Purpose:** show the paired instrument (positive control **AND** calibrated null gate)
  rejects false graduations that each component **alone** admits.
- **Conditions** (same benchmarks, same candidate readings):
  - **A · positive-control-only:** trust a candidate's derivation-set score because the pipeline
    demonstrably recovers a *known* analog (no per-claim null).
  - **B · null-gate-only:** gate a candidate on the best-of-100 random-map null, with **no**
    positive-control step establishing the pipeline has power at all.
  - **C · paired (our instrument):** positive control **and** null gate **and** held-out.
- **Inputs:** the syllabic benchmarks' observed best scores (near-chance "signals") as
  candidate-false cases that should be **rejected**, plus ≥20 planted-true maps (real key) that
  should be **accepted**.
- **Committed prediction:** there exist cases (specifically the syllabic near-chance "signal")
  that **A admits** (because the alphabet positive control says "pipeline works," so a 10–16%
  syllabic score is taken as real) and that **C rejects** (the null shows 10–16% is inside the
  random-map distribution). B alone is uninformative where the pipeline has no power.
- **Decision rule:** **SUPPORT N1-composition** iff C's false-graduation rate is lower than
  `max(A,B)` by ≥ a pre-set margin (C ≤ 1% while the worse single component ≥ 5%), **and** C still
  accepts ≥ 90% of planted-true maps. **NARROW/DROP** the N1 protocol-novelty iff C gives **no**
  reduction over the better single component. (Fail-closed: no reduction ⇒ we drop the claim.)

## T2 — Null appropriateness + robustness (defends N4: the *application*, not the method)

- **T2a — right null:** on ≥1 syllabic + 1 alphabet benchmark, compute two null distributions:
  (i) our **random-mapping** null (permute the sign→value key, run the full pipeline, best-of-100)
  and (ii) a **Kessler/LexStat-style wordlist-*pairing*** permutation null (permute target-word
  pairings, key held). **Committed prediction:** the two are **not** equivalent (two-sample
  KS rejects equality at α=0.01) and the random-mapping null is the stricter/appropriate reference
  because it randomizes the object we actually claim (the key). **Decision rule:** **SUPPORT** the
  N4 "distinct application" claim iff the nulls differ **and** the random-mapping FDR ≥ the
  pairing FDR (ours is not laxer). **NARROW** N4 to "we reuse a standard permutation null" iff the
  two are statistically indistinguishable.
- **T2b — where it matters:** report the best-of-100 false-graduation rate **per syllabic
  benchmark** (linearb-greek, cypriot-greek) with Clopper–Pearson 95% CI. **Committed
  prediction / rule:** gate valid iff syllabic false-graduation ≤ 2% (upper CI ≤ ~3%); else the
  gate is reported as mis-calibrated for the regime that matters (fail-closed).

## T3 — Within-harness anchor flip (defends N3: anchor-dependence, the highest-value test)

- **Purpose:** reproduce the SOTA anchored score **and** the anchor-free collapse **in one
  controlled comparison inside our own pipeline**, isolating anchors from corpus size.
- **Conditions** on Linear B → Greek and Cypriot → Greek, **corpus size held FIXED at full**
  (so only anchoring varies, not N):
  - **ANCHORED** (Tamburini-style): CSA fed the pre-grouped enumerated candidate cognate-pair
    lexicon `K_lex` / known related target.
  - **ANCHOR-FREE** (ours): no pre-grouping, subsampled-style matching.
  - **PARTIAL** (optional, Luo-style): proper-noun anchor set only, to trace the gradient.
- **Committed prediction:** ANCHORED ≥ 80% recovery; ANCHOR-FREE ≤ 20%; gap ≥ 50 points at
  fixed N; the alphabet positive control unaffected across conditions.
- **Decision rule:** **SUPPORT N3** iff (anchored − anchor-free) ≥ 50 points at fixed corpus size
  on ≥1 syllabic benchmark, alphabet control unchanged. **REFUTE N3** iff anchor-free *also*
  recovers well (collapse isn't anchor-driven). **NO_POWER / DEFER N3** iff we **cannot reproduce
  ≥ ~80% in the ANCHORED condition** — then "their success is anchor-dependent" is unproven and
  we must say so and NOT claim N3.
- **Implementation dependency (honest risk):** T3 requires an ANCHORED input mode
  (`K_lex` pre-grouping) in the harness. Confirm this exists / is a small extension **before**
  freezing the run; if infeasible this cycle, T3 is recorded `DEFERRED-INFEASIBLE` (not skipped
  silently).

## Run plan

- **Compute:** run on the rental (instance 44534071) in the window **after** the main sweep
  completes and **before** destroy — T1/T2 are cheap; T3 is a few cells per condition. Fallback:
  local, post-sweep.
- **Order:** T1, T2a, T2b (cheap, no new harness) → T3 (after the anchored-mode check).
- **Outputs:** append a `## RESULTS (post-run)` section with per-test verdict + the script +
  artifact paths; **an amendment may not turn a REFUTE/NARROW into a SUPPORT** (Art. XVII).
- **Nothing here gates or delays** `vastai destroy 44534071` beyond the small T-test window; if
  the anchored mode isn't ready, destroy on schedule and defer T3 to a fresh run.
