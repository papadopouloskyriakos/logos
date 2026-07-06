# PROJECT CHARTER — LA↔LB Ritual-Continuity FEASIBILITY Audit

```
channel_origin = POSTHOC_GENRE_REDIRECT
channel_class  = EXPLORATORY_POSTHOC_CHANNEL
```
**Branch:** `research/la-lb-ritual-feasibility` · **Worktree:** `/home/claude-runner/gitlab/n8n/logos-la-lb-ritual-feasibility`
**Forked from:** `research/la-lb-toponym-continuity` @ `87b4dea` (administrative channel CLOSED + archived).

## Why post-hoc (non-negotiable label)
The ritual channel was proposed **after** observing that most previously discussed LA↔LB continuities
were ritual/localized rather than administrative. Consequences: the known examples cannot serve as
untouched confirmation; thresholds cannot be tuned to recover them; the candidate universe cannot be
built to include them; any future real-data scan needs a **separately reviewed input freeze**; success
would still need independent held-out/prospective evidence. This channel is **never** described as
preregistered, confirmatory, or prospective.

## This pass is FEASIBILITY + POWER ONLY
It MUST NOT: perform real LA↔LB ritual matching; compute any similarity/score; run a prospective scan;
externally preregister; change the manuscript; claim any sign value / lexical continuity / decipherment;
initiate candidate-language testing; resume the Egyptian channel; or modify the archived administrative
results. No similarity function is imported or called in this pass.

## Research question (feasibility)
> Is there enough **independent** ritual-context evidence in Linear A and Linear B to design a future
> falsifiable continuity test that can distinguish genuine lexical/orthographic persistence from chance
> after accounting for post-hoc channel selection, short sequences, transcription uncertainty, and drift?

Secondary: counts of independent LA ritual forms / LB ritual terms; independence after dedup by form,
site, formula, document cluster; whether lengths support discrimination; whether any held-out evidence
remains after quarantining the known examples; whether a drift model can be specified **independently
of** the known pairs; whether false positives can be controlled; power under exact / Tier-A equivalence
/ independently-constrained drift; whether a future one-shot input freeze is justified.

**This pass must NOT answer** which LA ritual form corresponds to which LB form, what any form means,
what any sign sounds like, or whether any known pair is genuine.

## Verdict ontology (mechanical)
```
status                   ∈ {INCOMPLETE, COMPLETE}
ritual_channel_readiness ∈ {NOT_READY, READY_FOR_INPUT_FREEZE_REVIEW, NO_POWER}
```
`INCOMPLETE` may NOT be used to dodge a warranted `NO_POWER`.

## Firewall
LA ritual candidates (internal-only) and LB ritual targets (independent) are built and reviewed in
SEPARATE packets, never side by side; the known-pair ledger is quarantined from both and from the drift
model. Unit of analysis = unique ritual word/formula form (attestations are supporting evidence, not
independent discoveries).

## Deliverables & commits — see §XIV/§XV of the task; all hashes logged in DECISION_LOG.md.
