# PROJECT CHARTER — Blinded Cross-Script Administrative Schema Induction

## Decision & scope

The external phonetic-anchor programme is **closed** for the currently available evidence (see the
completed-branch verdicts below). This programme is **structure-first semantic decipherment**:

> Recover administrative **semantic roles** and **document schemas** from script structure alone;
> validate the method under **blinded** ground truth on **Linear B**; only then consider a frozen
> one-shot transfer to Linear A.

**This pass is a Linear B benchmark + transfer-feasibility gate only.** It STOPS before producing
semantic predictions for real Linear A forms. A rigorous negative result is a successful result.

**Valid final outcomes:** `READY_FOR_LINEAR_A_TRANSFER_FREEZE` · `NO_POWER` · `REJECT_ARCHITECTURE`
· `INCOMPLETE`.

## Scientific target (§I)

Model MAY use: raw sign identity + sequence; word/entry/row/document position; numerals + fractions;
logograms; totals/subtotals; document + support type; site/findspot/chronology/scribal hand; recurrence
+ formula structure; damage/joins/allography/transcription uncertainty.

Model MUST NOT use: phonetic transliteration; Greek lexemes; translations/glosses; known personal/place
names; candidate-language data; pretrained natural-language embeddings.

**Target ontology:** PERSON · PLACE · INSTITUTION · TITLE_OR_OFFICE · COMMODITY ·
ANIMAL_OR_HUMAN_CATEGORY · MEASURE_OR_UNIT · QUANTITY · TRANSACTION_OR_ALLOCATION_OPERATOR · QUALIFIER
· TOTAL_OR_SUBTOTAL · HEADER_OR_SECTION_LABEL · FORMULA_OR_BOILERPLATE · UNKNOWN.

**A transfer may support** structural statements ("behaves like a personnel designation", "likely a
destination/institutional slot", "instantiates an allocation schema"). It must **never** support
"this word means X", "this sign is pronounced Y", "Linear A encodes language Z".

## Isolation record (§III)

- **Branch:** `research/blinded-admin-schema-induction` · **Worktree:** `/home/claude-runner/gitlab/n8n/logos-admin-schema`
- **Parent:** `main` @ `f6a5682` (feat(corpus): decode SigLA database.js) — forked 2026-07-06.
- **Completed external-anchor / prior research branches (DO NOT touch, reset, merge, or rewrite):**
  | branch | tip | verdict |
  |---|---|---|
  | `research/egyptian-calibration-gate` | `dfa291e` | external phonetic anchor — Cretan one-shot CONFIRM_GENERALIZES *mechanically* but honest interpretation **TRIVIAL/NULL** |
  | `research/external-minoan-anchors` | `6d2e926` | anchor/SigLA sourcing |
  | `research/la-lb-ritual-feasibility` | `e6ee2b4` | **COMPLETE / NO_POWER** |
  | `research/la-lb-toponym-continuity` | `87b4dea` | CLOSED — split verdict (H_exact NULL / H_drift NO_POWER) |
- **Protected & untouched:** `main`, `paper/`, `runtime/` (CSA sweep), all completed research branches.
  Light local CPU only; no CSA-runtime interference.

## Hard constraints (this pass MUST NOT)

Touch the CSA runtime · modify the paper or its correction workflow · perform real Linear A semantic
inference · perform phonetic or lexical matching · use candidate languages · externally preregister or
publish · assign Linear A meanings/translations/pronunciations/language-families/cognates · reopen
external-anchor matching.

## Gate chain (this programme)

Prior-art/novelty → source audit → canonical document graph → LB role gold ontology → blinding firewall
→ frozen grouped splits + sealed holdout → baselines (B0–B2) → structured models (M1 CRF, M2 factor
graph [primary], M3 MDL templates, M4 graph sensitivity) → frozen acceptance gate → positive controls →
nulls + ablations → **sealed LB benchmark (run once)** → Linear A **structural compatibility dry run
(no semantic output)** → mechanical benchmark verdict.

Load-bearing gates: PC2 (unseen-word-form) + PC3 (cross-site) must generalize; **A6 (remove lexical
identity)** must not collapse — collapse under A6 ⇒ memorization ⇒ blocks transfer.
