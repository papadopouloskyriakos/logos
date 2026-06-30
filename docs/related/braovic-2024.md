# Related-work ingest — Braović, Krstinić, Štula & Ivanda 2024 (the survey spine)

**Citation.** M. Braović, D. Krstinić, M. Štula & A. Ivanda, "A Systematic Review of Computational
Approaches to Deciphering Bronze Age Aegean and Cypriot Scripts," *Computational Linguistics*
50(2):725–779, 2024. DOI [10.1162/coli_a_00514](https://doi.org/10.1162/coli_a_00514). Open access,
CC BY-NC-ND. PDF: <https://aclanthology.org/2024.cl-2.7.pdf>.

**Status: P-BLOCK #1 ingested.** This is the field's flagship computational-decipherment review and
the first one focused specifically on Bronze Age Aegean/Cypriot scripts. A CL reviewer of a logos
paper will know it by heart; *not* engaging its taxonomy reads as not knowing the field. Audited
2026-06-30 (full 55 pp). This file is the related-work spine; the draft's Related Work section is
built from it.

## The single most important finding — logos's headline novelty is an *empty cell* in the canonical taxonomy

Sec. 4 (pp. 735–738) enumerates **15 "major challenges" of computational decipherment**: unknown
writing system / reading direction; unknown punctuation; unknown language; small dataset; incomplete
vocabulary; unknown syntactic/word-order typology; unknown morphological typology; allographs;
scribal penmanship; exonyms; homonyms; unknown context; unavailable parallel data; unavailable
digital data; unavailable hardware/HPC.

**None of the 15 is about overfitting, multiple-testing, false-positive control, contamination, or
telling a *fitted* decipherment from a *real* one.** That entire failure-mode axis — the one logos
exists to police — is absent from the field's canonical challenge list. This is the cleanest, most
citable novelty claim logos has:

> **Draft positioning ("the 16th challenge").** The survey's 15-challenge taxonomy omits the
> false-positive / multiplicity / contamination axis. logos adds it and builds the machinery for it:
> the decontamination-discipline harness — L_fake canary, L_known/L_virgin partition, LLM-ablation,
> Deflated-Sharpe / effective-n deflation, pre-registration, and a held-out graduation gate computed
> mechanically by `verdict.py`.

And Sec. 6.3 (p. 746) hands logos its referee hook by *naming the open problem*:

> "it is just as difficult to evaluate and score the results of their computational analysis since in
> many cases there is nothing to compare them against, and **their evaluation remains an open
> problem.**" (p. 746)

logos's answer is concrete: the libation formula recurs across ~5 peak-sanctuary sites → a natural
leave-one-site-out held-out CV, with verdicts computed mechanically from held-out data. Quote this
sentence in the draft and present the held-out method as the answer to the named open problem.

## Where logos sits in the survey's method taxonomy (Sec. 7.1) — and where it is NOT novel

| logos component | survey bucket | prior work logos must distinguish itself from |
|---|---|---|
| Direction D (metrology/fractions) | 7.1.1 individual symbols / metrology | **Corazza et al. 2021** (already credited; ½=1/2 ⟂ their J=1/2). Survey confirms logos picked the right baseline. |
| Palaeo I-JEPA cross-script image work | 7.1.1 visual similarity | **Daggumati & Revesz 2019/2023** (CNN+SVM; LB↔Cretan-hieroglyphic correlation); **Corazza et al. 2022** Sign2Vec. **Cross-script visual comparison is NOT novel.** |
| Cognate/Semitic grading + deflation | 7.1.2 words / word-parts | **Min Eu, Xu & Cacciafoco 2019**; **Colin & Cacciafoco 2020** ("brute-force attack" on dictionaries); **Luo et al. 2019**. |

**Desk-reject risk (image work).** The git-log phrasing "cross-script IMAGE alignment SUCCEEDS /
first non-null offensive signal" must be reframed. Daggumati & Revesz already did cross-script CNN
visual similarity. logos's *defensible* novelty is narrower and real: **the controlled image-vs-
sequence ASYMMETRY under one harness** (image aligns; sequence/cognate does not), not "cross-script
visual comparison." Drop any "first/novel visual alignment" wording or a reviewer who knows this
survey flags overclaim on exactly logos's named novelty.

## Other load-bearing reconciliations

- **Word-length premise mismatch (must fix).** The Direction-A morphology null leans on "Linear A's
  short, mostly 1–2-sign words." The survey's cited figure (**Fuls 2015**, p. 733) is an **average
  word length of 3.3 signs**. Cite Fuls and report the *actual* word-length distribution from the
  corpus, or a reviewer sees a tension between logos's premise and the survey's headline number.
  → tracked for the Direction-A finding; see `docs/` reconciliation note.
- **Semitic is not crank — quarantine, don't dismiss.** Per **Schoep 2002** (via this survey, p. 734)
  the two *best-founded* language hypotheses are Semitic (non-IE) and Lycian (Anatolian IE). logos's
  stance — index the Di Mino/Gordon Semitic readings to *quarantine* them and grade the family
  head-to-head, never "crank" — is exactly right and now has a citable warrant. Strengthens
  `linear-a-claims-2026.md` and the litindex rationale.
- **The undisciplined search-trap baselines are in-domain.** Min Eu/Cacciafoco 2019 and Colin &
  Cacciafoco 2020 are the *concrete Linear-A instances* of the multiple-testing dictionary-fishing
  trap logos's deflation polices — cite them (alongside Di Mino/Gordon) to make the deflation
  contribution legible rather than abstract.
- **Direction-A targets a gap, not a duplication.** The survey raises word-order (#6) and morphology
  (#7) typology only *generically* (Croft 2003) and **does not cite Davis 2013 or Thomas 2020**. So
  logos's pre-registered test of those specific claims is a contribution the canonical survey leaves
  open. The pre-reg/finding should say this.
- **Corpus-count reconciliation.** Survey (Tan 2022): **97 unique Linear A signs**, 64 carried into
  Linear B; ~1,370 documents; 7,362–7,396 total signs (Schoep 2002). logos's V differs because it
  counts the fuller SigLA inventory (rare/compound/numeral) vs the core phonetic syllabary — document
  this so `corpus_info` numbers are defensible against the canonical figure.

## Desk-reject checklist (engage all of these in the draft)

1. Map logos explicitly into Sec. 7.1 method taxonomy + the 15-challenge frame (the "16th challenge").
2. Cite + distinguish Daggumati & Revesz 2019/2023 and Corazza 2022 on the image claim.
3. Foreground Corazza et al. 2021 as the Direction-D baseline.
4. Cite **Ferrara & Tamburini 2022** — the survey names it as the *only* comparable prior review;
   omitting logos's nearest competitor-review is a standard desk-reject trigger.
5. Quarantine (don't dismiss) the Semitic reading; cite Schoep 2002.
6. Reconcile the 1–2-sign premise against Fuls 2015's 3.3-sign average.

## What this PDF does *not* supply (still needed)

Schoep 2002 (Minos suppl. 17); Daggumati & Revesz 2019/2023 full papers; Colin & Cacciafoco 2020 +
Min Eu et al. 2019; Ferrara & Tamburini 2022 full text; Fuls 2015. The survey does not reproduce
Corazza 2021's solved fraction values, and does not cite Davis 2013 / Thomas 2020 (logos holds those
separately). See `docs/related/_acquisition.md`.
