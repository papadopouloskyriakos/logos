# OPERATOR-AFK — autonomous operating charter

**Operator AFK ~2 weeks from 2026-06-30.** Autonomous continuation authorized. This file is the
durable charter for autonomous Claude sessions + the deferred-for-operator queue. Read it FIRST
on every autonomous resumption.

## The contract

**WILL do (engineering — no operator needed):**
- Build the remaining framework pieces via the Workflow tool (implement + adversarial verify),
  verify each myself (re-run the headline number, read the verify pass, confirm no overclaim),
  record a `docs/findings/<date>-<topic>.md`, then **git commit + push to `origin main`**.
- The ordered work queue (below).
- Fix verify-caught issues.
- Keep docs/references.md + the findings as the honest audit trail.

**WILL NOT do (outward / human-dependent / strategic — DEFER, append to §Deferred):**
- The **DĀMOS Linear-B data request** (email to humans at damos@hf.uio.no / the Patras authors).
- **Recruit an Aegean epigrapher** (human contact).
- Any **publish / preprint / public-release** decision.
- Create **new external resources/accounts/repos** beyond `n8n/logos`.
- **Strategic scope changes** beyond the audit-corrected roadmap (no new targets, no pivot away
  from the decontamination-layer contribution without the operator).

## Guardrails (non-negotiable)

1. Honor the logos invariants (`CLAUDE.md`): no claim without hash-keyed held-out verification;
   the LLM never grades itself; honest nulls over claims; open by default; truth-caps ≤0.75.
2. **Verify, don't trust** — every workflow's self-report is re-run/checked before commit.
3. **Honest nulls are deliverables** — record them; never spin a null into a claim.
4. Stick to the audit-corrected roadmap; record the rationale for any judgment call in the finding.
5. If blocked on a decision or external input: record it in §Deferred + move to the next unblocked
   task. Do not stall.
6. **Commit + push often** — GitLab `origin main` is the durable state; the Galera `logos` DB +
   `docs/findings/` + the task list are the resume points.

## Ordered work queue (engineering)

1. **Fix the L_fake MEDIUM caveats** (#22): root-template sampler (candidate empirical
   root-frequency, not independent marginals) + full-Hebrew-lexicon rejection (ETCBC/bhsa) +
   correct the "zero real content" wording + publish residual collision rate.
2. **Adopt CSA_OptMatcher** (#20): clone `github.com/ftamburin/CSA_OptMatcher` (+EditDistanceWild)
   into `corpus/bronze/code/` (gitignored); reproduce Tamburini 2025 Table 3 on the shared
   benchmarks; this is the baseline the discipline layer grades.
3. **predict.py / verdict.py / family_scores.py + DB connector** (#11/#12/#13): agora-pattern
   ports per `docs/design/comparison-layer.md` (§A encoding, §E acceptance gates); wire the
   `hypotheses`/`verdicts`/`family_scores` tables in the `logos` DB.
4. **Finish the decontamination layer** (#15): literature index + `L_known`/`L_virgin` partition
   + LLM-ablation delta; the S_phono/S_morph statistics (S_lex is done); the DSR/MDL graduation
   gate (instrumented N_eff + `k ≤ U_floor`).
5. **Pseudo-decipherment learning curves** (#16): downsample Linear B to Linear-A-like data,
   measure held-out recovery — the real information-sufficiency test (replaces the withdrawn
   unicity claim).
6. **Sign-image I-JEPA** (#21, running) — process when it lands; record honestly (I-JEPA vs
   classical; cross-script image alignment vs the Track B sequence null).

## Deferred for operator (do NOT do autonomously)

- [ ] **DĀMOS Linear-B corpus** (~5,500 tablets) — data request to damos@hf.uio.no / Patras
      authors. **Blocks:** the cross-script A↔B bet (both sequence + image paths) beyond the
      null already recorded.
- [ ] **Aegean epigrapher** — sign-classification / genre review (both audits: largest non-ML
      hazard). Needed before any sign-level interpretation is asserted.
- [ ] **Publish / preprint decision** — the framework + nulls are approaching preprint quality;
      the operator decides when/where.
- [ ] **Any scope pivot** (e.g., add a target script, change the contribution framing).

## How continuation works + its limits

- A **durable recurring cron** (every ~4h) re-invokes a Claude session to run one work-cycle
  (pick next task → Workflow → verify → finding → commit+push). It survives Claude restarts.
- **Limits to know:** (a) recurring jobs **auto-expire after 7 days** — autonomous-me re-arms it
  during active cycles, but if the session is dead at day 7 it stops; (b) the cron fires **only
  while a Claude Code session is alive + idle** — keep it in a persistent terminal/tmux; (c) if
  everything stops, just re-invoke `claude` — state is fully recoverable from GitLab + the DB +
  this file + the task list.
- **Nothing is lost** across stops: all code/results are committed to `origin main`; derived
  data + the DB live on the runner/Galera.

## State snapshot (2026-06-30)

Done + on GitLab: corpus + DB + inventory (V=92) + logos_stats + datasets + simplified engine +
Track B null + L_fake canary (self-validation holds). Running: sign-image I-JEPA. See
`docs/findings/` for every result. Positioning: logos = the decontamination + discipline layer
for the LLM-in-the-loop era (Tamburini owns the baseline; the decipherment is data-gated).
