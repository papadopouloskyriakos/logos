# logos — a falsification-first platform for undeciphered-script research

[![DOI](https://zenodo.org/badge/1285556812.svg)](https://zenodo.org/badge/latestdoi/1285556812)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> *logos* (λόγος): word, reason, account.

**logos tests linguistic hypotheses about undeciphered scripts — starting with Linear A —
under a discipline designed to tell a real signal apart from a fitted one, and to report an
honest null when nothing survives.**

The history of failed decipherments is, in large part, a history of self-deception: a tiny
corpus, an unknown language, and a large space of candidate readings let a determined analyst
"translate" almost anything. (The classic intuition: with a permissive enough target you can
"prove" that *English is a Semitic language* — see [docs/english-is-semitic-demo.md](docs/english-is-semitic-demo.md).) logos is
built as a difference-detector. A proposed reading only counts as evidence once it survives
pre-registered, held-out, multiple-comparison-corrected validation. When nothing survives, the
calibrated null — *what the corpus can and cannot support* — is itself the deliverable.

This is a methodological contribution first. If a Linear A decipherment is attainable on the
present evidence, this framework is built to recognize it. The working conclusion, on current
data, is that the binding constraint is **identifiability** (no known related language, a small
and partly lossy corpus), not effort — and the rigorous demonstration of *that* is the result
the field can use.

## Why now

A high-profile AI-assisted Linear A claim circulated in June 2026 — a capable conjecture, but
not public, not peer-reviewed, and not reproducible, with no held-out verification. logos is
built to be its methodological opposite: open by default, mechanically graded, and corrected for
multiple testing. The claim is treated as a *worked example* of the failure modes the framework
is designed to catch ([docs/linear-a-claims-2026.md](docs/linear-a-claims-2026.md)) — analysed on its public evidence, as a
claim, not a person.

## The non-negotiables

1. **No claim without a committed, falsifiable prediction.** A phonetic, lexical, or grammatical
   hypothesis is registered (hash-keyed, timestamped) *before* it is tested. No prediction → no
   verdict.
2. **The proposer never grades itself.** Model-assigned phonetic values and learned embeddings
   enter only as *candidate signals* with capped weight; the verdict is computed mechanically
   against held-out material. A hypothesis that grades its own match is the anti-pattern.
3. **A reading is guilty until proven innocent.** Nothing counts as deciphered without held-out
   verification (operationalized as held-out-site / held-out-inscription tests, in the spirit of
   the new-tablet check that confirmed Linear B). Internal consistency on the training set is
   curve-fitting, not evidence.
4. **The information floor is always on screen.** Every claim is shown beside its
   multiple-comparison-corrected significance and the corpus's entropy / identifiability budget.
   A reading whose free parameters exceed what the corpus can constrain is underdetermined by
   construction.
5. **Open by default.** The corpus tooling, the validation methodology, and any results table are
   public. Licensed raw data is the only exception.

Operating rules: [CLAUDE.md](CLAUDE.md). Architecture & rationale: [DESIGN.md](DESIGN.md).

## Status (2026-07): the harness, a body of pre-registered nulls, and a published preprint

The discipline harness is built, exercised, and calibrated; the preprint is **published on
Zenodo** ([DOI 10.5281/zenodo.21119213](https://doi.org/10.5281/zenodo.21119213), 2026-07-02)
and **under review at TACL** (submitted 2026-07-02) — LaTeX single source under `paper/tacl/`,
built PDFs under `paper/build/`, submission record in `paper/SUBMISSION_NOTES.md`.
Headline calibrations: the graduation gate's realized false-graduation rate under a
best-of-100 cherry-picked null is **0.6% (3/500; Clopper–Pearson 95% upper ≈ 1.54%)**, and
the identical morphology test that returns no-power on Linear A **recovers Mycenaean
(Linear B) inflection** (9/16 affixes above the bigram floor) — the null is a property of
Linear A's short forms, not a dead detector. A known-answer CSA sufficiency sweep
(`results/csa/`) finds the primary syllabic analog (Linear B→Greek) at its chance floor at
Linear-A scale even when handed a real cognate signal (2,000-step lower bound; Cypriot→Greek
marginally above). What exists:

- **A decontamination / falsification harness** — a literature index with a known-reading vs.
  literature-unseen partition, a fabricated-language control corpus, model-ablation contamination
  checks, multiple-comparison correction, and pre-registration — all graded mechanically from
  persisted artifacts (`scripts/comparison/`).
- **A qualitative audit** — a three-part, primary-sourced refutation of the June-2026 `*301`
  claim, including that its own morphological segmentation (a prefixing, agglutinative verb) finds
  no support in the primary descriptions of the form (Davis 2013: no Afroasiatic signature;
  Salgarella 2025: agglutinative isolate) — resting on those descriptions, not on any a-priori
  typological contradiction ([docs/linear-a-claims-2026.md](docs/linear-a-claims-2026.md)).
- **A body of pre-registered nulls**, each with its borderline cases named: morphology induction
  (pooled and genre-stratified), metrological/accounting analysis, a distributional-phonology
  pilot with a power analysis, a cross-script image-vs-sequence asymmetry, and a model-
  regurgitation probe on literature-unseen signs (`docs/findings/`).
- **Literature engaged at the primary-source level** — Braović 2024, Salgarella 2025, Davis 2013,
  Thomas 2020, Corazza 2021, Schrijver 2014, and others (`docs/related/`, `docs/references.md`).

## Reproducibility & data

The licensed Linear A corpus (GORILA- and SigLA-derived) and the DĀMOS Linear B data are **not**
redistributed here — they carry CC BY-NC-SA / all-rights-reserved terms and are git-ignored. The
code, the discipline harness, the pre-registrations, and all analysis and findings are open under
the MIT license. Each source's license and how to obtain it is documented in
[docs/data-provenance.md](docs/data-provenance.md).

This work is independent and not affiliated with or endorsed by any of the cited projects or
their authors.

## Citation

To cite the **paper** (Zenodo preprint; under review at TACL):

> Papadopoulos, K. (2026). *Falsification-First Decipherment: A Decontaminated Inference
> Framework for Testing Undeciphered-Script Claims, with Linear A as a Worked Null* (1.0).
> Zenodo. https://doi.org/10.5281/zenodo.21119213

The software is archived on Zenodo separately. To cite the software in general, use the
**concept DOI** (always resolves to the latest version):

> Papadopoulos, Kyriakos. *logos: a falsifiable, decontaminated inference framework for testing
> undeciphered-script decipherment claims.* Zenodo. https://doi.org/10.5281/zenodo.21087572

To cite a specific snapshot, use that version's DOI (v0.1.0 → `10.5281/zenodo.21087573`).
Machine-readable metadata is in [`CITATION.cff`](CITATION.cff) (GitHub's "Cite this repository")
and [`.zenodo.json`](.zenodo.json).
