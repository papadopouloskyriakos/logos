# PROJECT CHARTER — No-Human Structural Decipherment Programme

## Decision & scope

The project owner **will not recruit or commission human annotators**. Recorded as a **constraint, not a
scientific failure**:

```
HUMAN_EXPERT_GOLD_PATH: status = CLOSED_BY_OWNER_CONSTRAINT · reason = NO_EXTERNAL_HUMAN_ANNOTATION · scientific_verdict = UNTESTED
```

The completed human-expert package and the automated pilot are **preserved unchanged** (in the parent branch
`research/blinded-admin-schema-induction`). This programme uses ONLY: existing published scholarly
annotations/databases · deterministic source-derived labels · programmatic weak supervision · self-supervised
learning · synthetic & pseudo-script controls · internally-falsifiable structural tests.

**Objective:** test whether a **no-human system** can recover transferable administrative **roles** and
**document schemas** under conditions that *simulate an unread script* (pseudo-scripts), and justify a frozen
one-shot transfer architecture for Linear A. **Not** pronunciation or translation.

**Valid final outcomes:** `READY_FOR_LINEAR_A_NO_HUMAN_TRANSFER_FREEZE` · `NO_POWER` · `REJECT_ARCHITECTURE`
· `INCOMPLETE`. **A negative verdict is a successful scientific result.**

## Isolation (§I)

- **Branch:** `research/no-human-structural-decipherment` · **Worktree:** `/home/claude-runner/gitlab/n8n/logos-no-human-structure`
- **Parent:** `research/blinded-admin-schema-induction @ dd98f1a` (inherits the canonical document graph,
  frozen ontology `781902c0`, feature sets, LA notation resolution). Forked 2026-07-07.
- **Protected & untouched:** `main@f6a5682`, `paper/`, `runtime/`(CSA), all completed research branches, the
  parent branch's closed human-expert package + automated pilot.

## Hard constraints (do NOT)

Fabricate expert annotations · use LLM agents as substitutes for human experts · lower the frozen agreement
thresholds · reinterpret the automated pilot as human validation · delete/rewrite the human-expert package ·
reopen phonetic-anchor searches · run candidate-language matching · infer phonetic values · claim lexical
translations · assign semantic roles to real Linear A forms (until `LINEAR_A_NO_HUMAN_TRANSFER_FREEZE_APPROVED`).

## The core idea — pseudo-script benchmark (§VI)

Simulate the Linear A problem using **Linear B** (which has source-derived evaluation labels) but with the
model-visible sign system made **unreadable**: replace every LB sign ID with a domain-specific random opaque
ID, **independent permutations** per site/split (no cross-domain sign bridge), withhold transliteration/
lemma/Greek, keep only frozen structural channels, and **degrade** the target to match real Linear A coverage.
The load-bearing simulation is **`O2 + D8`** (independent source/target permutations + combined LA-like
degradation). The model never receives the permutation key.

## Load-bearing gates

`NONTRIVIAL_UNSEEN_FORM_SCORE` (excl. numerals/fractions/logograms/totals/dividers/DOCUMENT_STRUCTURE/seen
lexical families/close morphological siblings/source-disputed) · **A12 (remove lexical identity) must not
collapse** · `O2` above transferable baselines · `O2+D8` above null · KN↔non-KN transfer · result outside
end-to-end nulls · source-label dependencies explicitly modeled (no false "independent consensus").

## Gate chain

human-path closure → source-label dependency audit → deterministic SILVER labels → weak-supervision LFs →
pseudo-script freeze (O0–O5 × D0–D8) → self-supervised baselines (SSL0–5) → template induction (T0–4) →
transfer models (B0–B5, M1–M5) → frozen splits + sealed pseudo-script holdout → positive controls (PC1–7) →
nulls + ablations → **sealed pseudo-script eval (once)** → Linear A unsupervised dry-run (no semantic output)
→ mechanical no-human readiness verdict.
