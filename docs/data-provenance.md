# Data provenance & licensing

logos is **open by default** (invariant 10), but the underlying epigraphic data is owned by others.
This file documents every external data source, its licence, how to obtain it, and how logos handles
it. **Rule: bulk / licensed raw data is never committed** — it is `.gitignore`d (see `corpus/bronze/*`,
`corpus/silver/*.json`, `runtime/`). Only logos's own code, pre-registrations, and analysis are
redistributed here under the MIT licence. The repository ships placeholder `.gitkeep` files so the
directory skeleton is reproducible without the data.

## Linear A — transliterations, signs, corpus

| source | what it provides | licence / terms | logos handling |
|---|---|---|---|
| **GORILA** — L. Godart & J.-P. Olivier, *Recueil des inscriptions en Linéaire A* (Études crétoises 21, 1976–1985) | the standard critical edition: authoritative transliterations, sign inventory, find-data | print critical edition; © the authors/publisher | reference authority; **not** redistributed |
| **lineara.xyz** (digital Linear A corpus) | machine-readable transliterations that the logos *silver* corpus is normalised from | no open licence stated by the source | derived `corpus/silver/*.json` is **git-ignored**; never redistributed |
| **SigLA** — *The Signs of Linear A* (E. Salgarella & S. Castellan) | sign-level palaeography, sign drawings/inventory | database; see SigLA site for terms | used for sign-image / palaeography work; sign images **git-ignored** |
| **CHIC** — *Corpus Hieroglyphicorum Inscriptionum Cretae* (Olivier & Godart 1996) | Cretan Hieroglyphic, for cross-script context | print critical edition | reference only; not redistributed |

## Linear B — for cross-script comparison

| source | what it provides | licence | logos handling |
|---|---|---|---|
| **DĀMOS** — Database of Mycenaean at Oslo (University of Oslo) | the Linear B corpus (transliterations, metadata) | **CC BY-NC-SA 4.0** | harvested politely (≤1 request/s) into `corpus/bronze/linearb/damos/`, which is **git-ignored**; not redistributed. See `scripts/fetch_damos.py` + `docs/damos-courtesy-email-DRAFT.md`. |

## Fonts & sign images

| source | what it provides | licence | logos handling |
|---|---|---|---|
| **Aegean** font (G. Douros) | Unicode glyphs for Linear A/B + Aegean numerals, used to render sign images for the palaeography/JEPA work | released to the public domain by the author | font + rendered images are tooling inputs; rendered image sets are **git-ignored** |

## Scholarly literature

Papers and monographs (e.g. Braović 2024; Salgarella 2025; Davis 2013; Thomas 2020; Corazza et al.
2021; Schrijver 2014) are **cited**, not redistributed. Short verbatim quotations appear under
fair-use / fair-dealing for criticism and research; rights remain with the authors and publishers.
Full bibliography: `docs/references.md`; per-source digests: `docs/related/`.

## How to reproduce with data

1. Obtain the Linear A transliterations from the source above and place the raw dump under
   `corpus/bronze/` (git-ignored).
2. Run the normalisers in `scripts/` to build `corpus/silver/` (git-ignored).
3. For the Linear B comparison, run `scripts/fetch_damos.py` (respects DĀMOS's rate limit + licence).
4. The discipline harness, pre-registrations, and analysis in `scripts/comparison/` + `docs/` then run
   against the local corpus.

## Affiliation

This work is independent and is **not** affiliated with, endorsed by, or sponsored by any of the
data sources, projects, or authors named above.
