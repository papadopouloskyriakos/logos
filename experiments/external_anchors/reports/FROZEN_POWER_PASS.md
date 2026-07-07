# Egyptian toponym-anchor — frozen-regime power pass (the unexecuted milestone)

Design/power analysis (Constitution v2.2 Art. VIII/IX). `results/power/frozen_power_envelope.json`. Frozen
result artifacts untouched. **Truth-layer signal only (≤0.75) — a design result, NOT a reading.**

## What was run

Phase A found the committed `toponym_power_envelope.json` reported only the `frozen=False` (mapping-search)
regime, which is uninformative (in-sample FP 0.72–1.00 — the multiple-testing trap relocated into the
sign-value search). The discipline condition is `frozen=True`: a FIXED a-priori correspondence (no search),
justified by the clean CC-BY Kilani-2019 group-writing→sound model (its role is only to license "no search";
no Kilani rule is invented). Measured over realistic Egyptian consonant-skeleton lengths at the real anchor
scarcity (n=3–4 securely-identified Cretan toponyms):

| skeleton La | candidate Lc | FP_frozen | REC (optimistic ceiling) | powered? |
|---|---|---|---|---|
| 3 | 3 | 0.24–0.26 | 0.87–0.97 | **NO** (FP ≫ 0.10) |
| 3 | 4 | 0.41–0.42 | 0.90–0.98 | **NO** |
| **4** | **4** | **0.04** | **0.71–0.91** | **yes** |
| **4** | **5** | **0.07–0.08** | **0.74–0.92** | **yes** |

## Honest reading — design-viable but scarcity-limited (NOT a crack)

1. **The frozen discipline materially helps.** Removing the mapping search drops the false-positive floor from
   ~0.25 (pilot search regime) to ~0.04 **at La=4**. The channel is *not* NO_POWER by design.
2. **But power hinges on skeleton length ≥4.** At La=3 (bare consonant skeleton k-n-s) FP is ~0.24 and it is
   NOT powered; only if the Egyptian group-writing yields ≥4 *distinctive* slots per toponym does the design
   clear a credible FP≤0.10 bar. Whether real renderings give 4 distinctive slots (vs 3 consonants + carriers)
   is uncertain.
3. **REC is an OPTIMISTIC ceiling** — it assumes Kilani gives the EXACT correspondence AND each anchor
   genuinely has an image in the LA corpus. FP uses a random a-priori map; a real Kilani map could match more
   densely. Both are upper-bound-favourable.
4. **Reality is worse — the real attempt was TRIVIAL.** The actual Egyptian confirmatory test this session
   (branch `research/egyptian-calibration-gate`, where Edel & Görg 2005 *was* collated, REQ-01 closed) ran the
   Cretan one-shot and returned **`TRIVIAL_RECOVERY`**: the correspondence rests on a single training record
   (š~s, HV-0234), leave-one-out flips the verdict 3→1. The design's optimistic power is not realized because
   the real anchors are too few and the correspondence too fragile.

## Verdict

**The Egyptian external channel is DESIGN-CONDITIONALLY-POWERED (frozen regime, La≥4) but its one real
confirmatory attempt is `TRIVIAL_RECOVERY`, and a broader confirmatory run stays SOURCE-limited by anchor
scarcity (3–4 secure toponyms, one-training-record correspondence).** It is not dead by design — it is limited
by anchor scarcity + correspondence fragility. The concrete unlock would be **more securely-identified Cretan
toponyms in the Egyptian record with ≥4 distinctive skeleton slots AND an independently-calibrated
correspondence not resting on one record** — neither of which the present sources supply. This converts the
external channel's status from INCOMPLETE to: *design-viable, real-attempt-trivial, unlock = more independent
anchors.* Sensitivity: the result depends on V=20 / n_cand=11 / tol=1 (pilot params) and on La=4 being the
true effective skeleton length; smaller La or larger n_cand removes the power.
