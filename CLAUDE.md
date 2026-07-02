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

**NOW (2026-07-03) — SUBMITTED: Zenodo preprint published + TACL under way; paper stays
byte-frozen through review.**
The harness is built, exercised, calibrated, written up, and out the door:

- **Corpus ingested** (silver: 1,341 inscriptions / 52 sites; DĀMOS Linear B 13,562
  wordforms via `scripts/cross_script/data.py`). Licensed raw data gitignored, never
  redistributed.
- **Probes executed** (all pre-registered, graded from artifacts): morphology NO-POWER
  null + segmentation positive (micro-F1 0.436 vs 0.389, site-clustered gap CI excludes 0);
  metrology null (p = 1.0, J = ½ credited to Bennett); phonology data-limited null;
  cross-script image leg = circular demonstration (capped ≤ 0.75); LLM-ablation
  public-exposure gradient; L_not_indexed abstention asymmetry (`L_virgin` was renamed
  `L_not_indexed` repo-wide, module `l_not_indexed.py`).
- **Gate calibrated**: best-of-100 random-map null → false-graduation 3/500 = 0.6%
  (one-sided exact Clopper–Pearson 95% upper ≈ 1.54%); Linear B morphology positive
  control FIRES (0.562 vs bigram floor ~0.30) — Linear A's null is short-word, not a
  dead detector (`scripts/comparison/linb_morphology_control.py`,
  `scripts/gate_null_calibration.py`).
- **CSA sufficiency sweep DONE** (H100 destroyed; `results/csa/`): at Linear-A scale,
  Linear B→Greek (primary analog) at its chance floor, Cypriot→Greek marginally above;
  2,000-step = lower bound, at-floor branch non-definitive. Serial CSA path (processes=1)
  is BROKEN — always run parallel.
- **Paper**: `paper/tacl/body.tex` is the single source → `paper/build/logos-arxiv.pdf`
  (named) + `paper/build/logos-tacl-anon.pdf` (anonymized, metadata-clean) +
  `paper/arxiv-package.tar.gz` (arXiv TeX upload). Main content exactly 10.0 pp
  (**zero cushion** — one added body line spills to p.11), Cat-1 ≈4.9/5, Cat-2 ≈1.5/3
  per TACL's March-2024 appendices policy. Byte-frozen; sha256s in
  `paper/SUBMISSION_NOTES.md` §(f). **Do not rebuild without re-verifying the p.10
  boundary and re-freezing.**
- **Submitted (2026-07-02, recorded in SUBMISSION_NOTES §(0))**: preprint PUBLISHED on
  Zenodo — DOI 10.5281/zenodo.21119213 (v1.0, CC-BY-4.0; concept DOI 21119212), file =
  the frozen `logos-arxiv.pdf`, md5-verified byte-identical to the local build; TACL
  manuscript **#11385** submitted (authorDashboard/submission/11385). **arXiv was NOT
  used** — the old "Variant A-only" declaration is OBSOLETE; the corrected
  Comments-to-Editor block lives in SUBMISSION_NOTES §(0).
- **Portal metadata DONE (2026-07-03)** — Contributors + Comments-to-Editors completed;
  the submission is fully lodged. **Next: wait for TACL's editorial decision** (track at
  the dashboard). A reviewer-requested revision restarts the freeze discipline (rebuild →
  re-measure p.10 → re-freeze §(f) hashes). The markdown preprint
  (`docs/preprint/…-condensed-v6.md`) is the historical record, kept in sync; the LaTeX
  is authoritative.
