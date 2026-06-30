# logos — an agentic decipherment-research platform

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

logos inherits its discipline DNA from two sibling repos under `n8n/`:

- **[claude-gateway](../claude-gateway)** — the agent-control patterns: predict-before-act
  gates (Infragraph), mechanical verification (grader ≠ proposer), human-as-circuit-breaker,
  fail-closed kill-switches, survive-abandonment→safe decay.
- **[finops-agora](../finops-agora)** — the rare-signal-under-noise core: hash-keyed
  predictions, a mechanical `verdict` writer, the López de Prado honesty layer
  (Deflated-Sharpe, PBO/CPCV, effective-n), truth-layer caps, the PIT/survivorship data
  discipline, and the **TS-JEPA market encoder** (repurposed here as a sign-sequence /
  cross-script representation layer).

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

## Status — v0 (just scaffolded, 2026-06-30)

Nothing ingested yet; no JEPA trained; no hypotheses graded. The repo currently holds:
the founding docs, the directory skeleton, and `scripts/corpus_info.py` — the first
computational artifact, which computes corpus statistics and the **unicity-distance /
information-budget estimate** (the single most decisive number for any Linear A claim).
Run it on its built-in demo: `python3 scripts/corpus_info.py --demo`.

The honest roadmap lives in [DESIGN.md §Roadmap](DESIGN.md).
