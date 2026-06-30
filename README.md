# logos — an agentic decipherment-research platform

<!-- DOI badge: after you enable this repo on Zenodo and cut the first GitHub Release, replace the line
     below with the badge markdown Zenodo gives you (https://zenodo.org/account/settings/github/). -->
[![DOI](https://img.shields.io/badge/DOI-pending%20Zenodo%20release-blue)](https://github.com/papadopouloskyriakos/logos)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> *logos* (λόγος): word, reason, account, meaning.

**logos's job is to find, test, and honestly validate linguistic hypotheses about
undeciphered scripts — starting with Linear A — and to NEVER publish a self-deceiving
decipherment.** It is an *offensive* research system: it hunts a real decipherment, but
the discipline machinery below (predict-before-claim, mechanical held-out verdicts, the
LLM never grading its own hypothesis, multiple-testing deflation, the unicity-distance
gate) is **the weapon that separates a real decipherment from a fitted one.** A positive
decipherment is guilty until proven innocent.

The history of failed decipherments is ~95% self-deception: a tiny corpus, an unknown
language, and a thesaurus of candidate roots let you "translate" almost anything (see the
"English is a Semitic language" demo). logos is the **difference-detector**: when a
hypothesis here claims an edge, the machinery has *earned* the right to believe it. When
nothing survives, the rigorous null — *exactly what the corpus can and cannot support* — is
the honest, publishable deliverable. The aim is the decipherment; the null result is the
insurance policy.

## Lineage

logos inherits its discipline DNA from two private sibling research repos:

- **claude-gateway** — the agent-control patterns: predict-before-act gates, mechanical
  verification (grader ≠ proposer), human-as-circuit-breaker, fail-closed kill-switches,
  survive-abandonment→safe decay.
- **finops-agora** — the rare-signal-under-noise core: hash-keyed predictions, a mechanical
  `verdict` writer, the López de Prado honesty layer (Deflated-Sharpe, PBO/CPCV, effective-n),
  truth-layer caps, the PIT/survivorship data discipline, and the **TS-JEPA encoder**
  (repurposed here as a sign-sequence / cross-script representation layer).

The trigger for this repo was the June 2026 "Linear A cracked" claim (Tom Di Mino /
Claude Code): a capable conjecture, but **not public, not peer-reviewed, not reproducible**,
with a live contradiction at its anchor and no held-out verification. logos is built to be
its exact opposite: **open by default, mechanically verdicted, deflated for multiple
testing.** See [docs/linear-a-claims-2026.md](docs/linear-a-claims-2026.md).

## The non-negotiables

1. **No claim without a committed, falsifiable prediction.** A phonetic/lexical/grammatical
   hypothesis is hash-keyed and registered *before* it is tested. No prediction → no verdict.
2. **The proposer never grades itself.** LLM-assigned phonetics, JEPA embeddings, and any
   model output enter as **truth ≤ 0.75** signals; the verdict is mechanical, computed
   against held-out corpus. (The Di Mino anchor that grades its own root-match is the
   anti-pattern.)
3. **A decipherment is guilty until proven innocent.** Nothing is "cracked" without
   held-out verification (the Linear-B-new-tablet standard, operationalized as held-out-site
   / held-out-inscription verdicts). Internal consistency on the training set is **not**
   evidence — it is curve-fitting by another name.
4. **The information floor is always on screen.** Every claim is shown next to its
   deflated significance **and** the corpus's unicity-distance / entropy budget. A
   decipherment whose free parameters exceed the bits the corpus constrains is
   underdetermined by construction.
5. **Open by default.** The corpus tooling, the verdict methodology, and any lexicon table
   are PUBLIC. (Licensed raw data is the only exception.) The deliberate contrast to
   non-publication claims.

Full operating rules: [CLAUDE.md](CLAUDE.md). Architecture & rationale: [DESIGN.md](DESIGN.md).

## Status (2026-07): the discipline harness + a body of pre-registered nulls

The harness is built and exercised; a preprint is in preparation. What exists:

- **The decontamination / falsification harness** — a literature index with an
  `L_known`/`L_virgin` partition + an `L_fake` fabricated-corpus canary, LLM-ablation,
  multiple-testing deflation, and pre-registration, all graded mechanically from persisted
  artifacts (`scripts/comparison/`).
- **A worked failure case** — a three-part, primary-sourced refutation of the June-2026
  "Linear A cracked" (`*301`) claim, including that its own morphological table contradicts the
  Semitic family it assigns (`docs/linear-a-claims-2026.md`, `scripts/comparison/litindex.py`).
- **A body of rigorous, pre-registered nulls**, each with its borderline cases named: Direction-A
  morphology (pooled + genre-stratified), Direction-D metrology (parse-coverage), a
  distributional-phonology pilot with a power analysis, the cross-script *image-vs-sequence*
  asymmetry, and an LLM regurgitation / `L_virgin` probe (`docs/findings/`).
- **Literature engaged at the primary-source level** — Braović 2024, Salgarella 2025, Davis 2013,
  Corazza 2021, Schrijver 2014, et al. (`docs/related/`, `docs/references.md`).

The honest framing is unchanged: the aim is a real decipherment; the rigorous null — *exactly what
the corpus can and cannot support* — is the insurance policy. Architecture & rationale:
[DESIGN.md](DESIGN.md); operating rules: [CLAUDE.md](CLAUDE.md).

> **Reproducibility note.** The licensed Linear A corpus (GORILA / SigLA-derived) is **not**
> redistributed here (it is gitignored — see invariant 10). The code, the discipline harness, the
> pre-registrations, and all analysis/findings are open.
