# Finding 2026-07-01 — hostile-referee simulation of the preprint (revision roadmap)

A fresh-eyes adversarial referee pass (verdict: **major revisions**) on
`docs/preprint/logos-preprint-2026-07-01.md`. The 8 acceptance-threatening issues, triaged by
whether they are fixable autonomously (prose/reframe), runnable with existing machinery, or need the
operator / a human. This is the pre-submission revision roadmap.

## The 8 issues (severity order)

1. **[BLOCKER · runnable] The graduation gate is never run on a real claim — not even the \*301 one it refutes.** §5 refutes Di Mino/Gordon with a literature argument, not mechanically; the L_fake canary (built to deflate exactly Gordon-style Semitic matches) is never pointed at the Di Mino lexicon. *Fix:* run the five Gordon equations + `a-sa-sa-ra-me` through the canary + deflation + order-statistic gate; report where they land vs the false-positive floor. Machinery exists.
2. **[BLOCKER · runnable] The flagship morphology null (§6) has no positive control**, unlike metrology (§7.1) and phonology (§7.2). On 1.84-sign words a bigram floor *must* absorb short-range affixation, so "bigram-reproducible" is indistinguishable from "no power / over-strong floor." *Fix:* run the identical bigram-floor test on Mycenaean Greek (Linear B — **already ingested**, 13,562 DĀMOS wordforms). If it nulls-out real Greek morphology ⇒ report strictly NO POWER; if it spares it ⇒ the Linear A null is interpretable.
3. **[BLOCKER · operator] §5's target "Di Mino 2026" is uncitable** († pending; "own table" exists only as the authors' archived reproduction). Can't refute a source a referee can't read; naming a person against it is an ethics problem. *Fix:* archive the primary claim at an independent timestamped location (Wayback + Zenodo) OR de-personalize §5 into a generic "Gordon-revival Semitic reading." Also: Davis 2013 p.38 n.13 is a hedged footnote being over-read as "ruled out Semitic" — soften to "found no Afroasiatic morphological signature."
4. **[fixable] Battery-level multiplicity is unpaid** (§9.5 admits it) — the exact sin the paper prosecutes. *Fix:* apply Bonferroni/FDR across the probe p-values now; it only strengthens the nulls.
5. **[fixable] §8.3 sufficiency sweep is un-run / zero-information** and is miscounted as one of "six reported probes." *Fix:* demote to appendix/future-work; re-describe the battery as **five executed probes** + sufficiency as protocol-only.
6. **[fixable] "Sixteenth challenge" overclaims novelty** its own citations undercut (Bailey & López de Prado imported wholesale; Packard 1974's fictitious controls are prior in-field false-positive work). *Fix:* reframe as "consolidate and operationalize an under-instrumented axis anticipated by Packard," drop/mark the ordinal as rhetorical, quote Braović's 15 challenge titles verbatim.
7. **[fixable] The image leg (§7.3) is conceded circular yet gets a full Results subsection**, and its I-JEPA figure matched the impl's *narration* not the artifact (a self-inflicted "grade-from-artifacts" violation). *Fix:* compress §7.3 to a negative-control paragraph; reconcile the I-JEPA seed count/number between the artifact and the stale finding-doc note.
8. **[operator] Venue fit:** §5's primary-source philology is unvetted by an epigrapher (the paper's own scope-freeze requires one), wrapped in finance jargon that alienates Aegean-scripts readers. *Fix:* secure an epigrapher reviewer for §5; translate finance terms (DSR → look-elsewhere/family-wise error).

**Referee also credited** (fairness): the L_fake canary is validated on a known-answer surrogate; DĀMOS ingestion converted a hedge into a tested null; metrology/phonology carry positive controls; self-caught confounds show the discipline bites; nulls are honest, borderline cases named.

## Disposition this session
- Applying now (prose/reframe): #5, #6, #7, #4 (demotion + honest multiplicity note), #3 (Davis softening).
- Attempting (runnable): **#2** Linear-B morphology positive control (highest-value tractable analysis).
- Deferred to operator: **#1** (canary-on-Gordon — runnable but a real analysis; scoped), **#3** archival, **#8** epigrapher. Flagged as explicit next steps.
