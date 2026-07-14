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

**SCHEDULE REFINEMENT 2026-07-14 (append-only; predictions/rules above UNCHANGED — Art. XVII).**
Verified: none of T1/T2/T3 depends on the CSA size-sweep completing (sz2214 irrelevant); T1/T2
use the gate machinery only, T3 uses the already-completed small syllabic benchmarks
(linearb-greek n_gold=919, cypriot-greek 693). Compute profile measured, not assumed:

- **T1 + T2 — LIGHT, run LOCALLY, now.** They exercise `scripts/gate_null_calibration.py`
  (imports `verdict` + `scripts.comparison.lexstat`; `nulls.py` has `random_lexeme_null` already)
  — pure-Python null simulation, **no CSA annealer / no CUDA**. Measured: B=50 → 7.1 s, RAM Δ≈1 MB;
  full B=500 ≈ 70 s. Zero LXC-freeze risk. **Outputs MUST go to NEW paths** (e.g.
  `results/ablation_T1.json`, `results/null_compare_T2.json`) — **never overwrite the canonical
  `results/gate_null_calibration.json`** (B=500/3/0.006; a probe clobbered + git-restored it once,
  do not repeat).
- **T3 — MODERATE, run on the RENTAL (44534071), concurrently with the sz2214 finishers** (3 cells
  on 64 cores/180 GB = ample headroom; do NOT run the CSA matcher on the LXC). Independent of the
  sweep result. Still gated on scoping the ANCHORED condition against the matcher's cognate-pair
  config (`scripts/baselines/csa_sweep.py:run_cell`, the `cog`/`N`/`M`/`penf` inputs) — a code read,
  not compute. If the anchored mode needs a small extension, do it, else `DEFERRED-INFEASIBLE`.
- **Order:** T1 → T2a → T2b (local, today) ; T3 scoping in parallel → T3 on rental before destroy.
- **Outputs:** append a `## RESULTS (post-run)` section with per-test verdict + script + artifact
  paths; **an amendment may not turn a REFUTE/NARROW into a SUPPORT** (Art. XVII).
- **Nothing here gates or delays** `vastai destroy 44534071` beyond the small T3 window; if the
  anchored mode isn't ready by sweep-end, destroy on schedule and defer T3 to a fresh run.

---

## T0 — CONVERGENCE CONTROL (prerequisite; gates N2/N3 and the published chart) — FROZEN 2026-07-14

**Why this exists (honest note):** the whole sweep is pinned at **`steps=2000`** to byte-match the
92 original cells. Ugaritic (alphabet) *converges* within 2000 steps (0.93, ≈ Tamburini's published
0.955), but Tamburini reaches his Table-3 syllabary numbers (**Linear B 89.4%**) only by **~4000
steps** (runs 100k). Linear B at 2000 steps = **2.4%**, and with only 2 chunks the plateau detector
**cannot have fired** — so it is **not known to be converged**. The N2 ("size is not the lever"),
N3 ("anchor-dependence collapse"), and the "syllabary wall" artifact all treated 2.4% as a real
floor and compared it to a *converged* 89%. **That comparison is confounded by convergence (and by
held-out-vs-in-sample metric).** T0 resolves it BEFORE N2/N3/T3 may be asserted.

**The run (committed):** `linearb-greek` at **full size** (size = n_gold = 919), **seed 0**,
**`steps=6000` cap**, chunk=1000, processes=4, device=cpu, **plateau early-stop** (eps=0.05,
patience=3), on rental 44534071, concurrent with the sz2214 finishers. Baseline to beat: the
2000-step full-919 cells = acc {0.065, 0.007, 0.008, 0.016}, mean **0.024**, seed0 = **0.065**.
Output to `runtime/csa_sweep/T0_convergence/` — **never** the sweep `cells/` dir.

**Committed decision rule (mechanical, fail-closed):**
- **CONVERGENCE_ARTIFACT** → endpoint acc **≥ 0.20**. Consequence: the 2000-step syllabary "floor"
  is substantially a step artifact. **N3 is REFUTED** (the 89%→3% gap is compute, not anchoring);
  **N2 is narrowed** to "at a fixed 2000-step budget"; **the published chart must be corrected or
  retracted** (its headline overreaches).
- **REAL_FLOOR** → plateau early-stop **fires** (converged) **AND** acc **≤ 0.10**. Consequence: the
  syllabary floor is real at convergence; N2/N3 stand *stronger* (now a converged result, not a
  lower bound); the chart is vindicated (with wording tightened to "converged").
- **AMBIGUOUS/ESCALATE** → 0.10 < acc < 0.20, OR runs the full 6000 steps without the plateau
  firing (still improving). Consequence: escalate (higher steps and/or seed 1) before concluding;
  do NOT resolve N2/N3 on an under-converged run.

**Cost/ETA (honest):** linearb-full = 14.3 h/seed at 2000 steps → ~43 h at 6000 (less if
early-stop fires); ≈ **$25–35**, pushing the rental total to ≈ **$90–105** and destroy to ~July 16.
This extra spend is justified: a wrong headline costs far more than $35. An amendment may not turn
ARTIFACT into FLOOR (Art. XVII).

**SCOPING OUTCOME 2026-07-14 (post-`run_one` read):**
- **T3 DROPPED — ill-posed.** `run_tamburini.run_one` always builds `module.Problem(cog, …, N, M,
  penf)` with the cognate `.cog` present and Tamburini's FIXED `N/M/penf` (his rule: N=1,M=2 if
  |L_s|>|K_s| else N=2,M=1; linearb = N=2,M=1,penf=4.0). There is **no anchored-vs-anchor-free
  toggle** — the 89%-vs-3% gap maps entirely onto STEPS, i.e. **T0**. "Anchor-dependence" (N3) was a
  mischaracterization; **N3 is subsumed by T0** and T3 is removed from the slate.
- **T0 upgraded to capture the TRAJECTORY** at zero extra compute: `run_one(checkpoint=1000)`
  computes acc every 1000 steps (line 241), which `run_cell` discarded. Driver now calls `run_one`
  directly → `runtime/csa_sweep/T0_convergence/traj_seed0.jsonl` (acc @1k,2k,…,6k) + heartbeat.
  Relaunched (old endpoint-only run killed at ~22 min). Lets us watch acc climb/flatten and
  early-kill once decisive.
- **T1 + T2 run LOCALLY** (pure-Python gate machinery `gate_null_calibration.py`; measured 7 s /
  ~1 MB) — they do **not** need the rental. So the instance is required only for **T0 (+ a possible
  T0 escalation if AMBIGUOUS)** and the sz2214 sweep tail. Balance 2026-07-14: **$80.53 ≈ 4 days**
  (owner added $45); destroy after T0 is resolved + merged (T1/T2 run local, no instance needed).
