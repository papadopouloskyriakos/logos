# CLAUDE.md — working in logos

Operational constitution for Claude Code sessions in the **logos** decipherment-research
platform. The *why* and architecture live in [DESIGN.md](./DESIGN.md); this file is the
*how* and the rules that keep logos honest. Patterns are inherited from
[../finops-agora/CLAUDE.md](../finops-agora/CLAUDE.md) and
[../claude-gateway/CLAUDE.md](../claude-gateway/CLAUDE.md) — read them for the lineage.

## Mission

**logos hunts a real decipherment of undeciphered scripts (Linear A first) and refuses to
publish a fake one.** The discipline machinery is the weapon, not the mission — it exists to
tell a *real* decipherment from a *fitted* one. Edge (here: a true phonetic/lexical reading)
is rare and must be earned against held-out data; the alternative is the self-deception that
defines ~95% of historical decipherment claims.

**The goal is acceptance: a reading that reads held-out text, survives expert review, and
ideally predicts newly-uncovered inscriptions — the standard by which Linear B (1952) was
accepted.** Open-and-honest-first is *sequencing, not cowardice*: you don't publish a
"cracked" claim on an unproven reading. If, after honest work, nothing survives the gate,
that null result — rigorously mapping what the corpus can and cannot support — is the
**insurance policy** (it saved the field another false decipherment) — the *fallback, never
the aim.* Do NOT write defeatist "Linear A is uncrackable" framing into any doc, prompt, or
UI copy.

## Invariants — do not break these

1. **No claim without a committed prediction (fail CLOSED).** Before any verdict, a
   hypothesis row keyed by `plan_hash` must exist: the sign(s) or sign-sequence claimed, the
   proposed reading, the language family, the falsifiable prediction (what held-out evidence
   it implies), and a confidence. No prediction → no verdict → no claim.
2. **The LLM / model never grades its own outcome.** Verdicts are computed mechanically from
   held-out corpus data by `scripts/verdict.py`. A hypothesis that fails never auto-resolves.
   (Inherited from agora invariant 3.)
3. **A decipherment is guilty until proven innocent.** Internal consistency on the
   derivation set is **not** evidence (overfitting). Acceptance requires held-out
   verification — held-out-site or held-out-inscription accuracy, ideally a newly-uncovered
   inscription. This is the Linear-B-new-tablet standard.
4. **Deterministic risk/honesty rules, never the LLM.** Phonetic assignments, family tests,
   sizing of evidence — all arithmetic. The LLM proposes; the gate disposes.
5. **Truth-layer caps.** Forecasts/assignments from any model (LLM theses, JEPA embeddings,
   cognate-matchers) enter as signals with confidence ≤ 0.75 — structurally unable to *decide*.
   Only mechanically-verified held-out reads rank higher.
6. **Dedup is deterministic.** A hypothesis/reading's identity is a content hash; inserts are
   idempotent. Replays and crashed retries are no-ops.
7. **The information floor is always on screen.** Every claim shows its deflated significance
   next to the corpus's unicity-distance / entropy budget. Parameters > information ⇒ the
   reading is underdetermined; say so.
8. **Multiple-testing discipline is mandatory.** The "English is a Semitic language" failure
   mode (cherry-picking roots across a thesaurus on a tiny corpus) is THE enemy. Every claim
   is deflated for n_hypotheses × n_signs × n_roots tried (Deflated-Sharpe / effective-n, the
   agora machinery). A match-rate is meaningless without it.
9. **Corpus honesty (PIT / leakage gates).** Use only evidence available up to a discovery's
   `as_of`; held-out partitions never inform hypothesis formation. The silver/gold corpus is
   versioned and reproducible.
10. **Open by default.** Corpus tooling, verdict methodology, lexicon tables: PUBLIC in this
    repo. Licensed raw vendor data is the only exception (gitignored).
11. **LLM via the Claude Code subscription only** — `claude -p …`. Never set
    `ANTHROPIC_API_KEY`. Local models via Ollama on the gpu host.
12. **Counts are generated, not hand-written.** Any "N inscriptions / N signs / N hypotheses"
    figure comes from a script, not a hand-edit.

## Conventions

- Commits end with the standard `Co-Authored-By` trailer. Default branch `main`.
- Silver corpus = normalized JSON/Parquet under `corpus/silver/`; gold = the queryable store.
- Receivers/scanners emit canonical signal rows; the verdict pipeline consumes them.
- Where to add content (so this file doesn't regrow — the agora lesson):
  dated claim analysis → `docs/`; a runbook → `docs/runbooks/`; a stable invariant → here.
- **When stuck, grep the siblings FIRST:** `../finops-agora` (the predict/verdict/score
  pipeline, agora_stats, the JEPA harness) and `../claude-gateway` (agent control).

## Current status

**NOW (2026-06-30) — v0 scaffold.** No corpus ingested, no JEPA trained, no hypotheses
graded. Founding docs + directory skeleton + `scripts/corpus_info.py` (corpus stats +
unicity-distance estimate, runnable via `--demo`). Next: ingest the public GORILA/SigLA
corpus (see `docs/`), stand up the predict→verdict scaffold, compute the real
unicity-distance number on the true Linear A corpus.
