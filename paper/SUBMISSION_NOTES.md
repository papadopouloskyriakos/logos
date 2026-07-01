# Submission notes — logos preprint (TACL + arXiv)

Paper title: **Falsification-First Decipherment: A Decontaminated Inference Framework
for Testing Undeciphered-Script Claims, with Linear A as a Worked Null**

Two PDFs are built from one shared body (`paper/tacl/body.tex`) via two thin wrappers:

| Target | Wrapper | Options | Output |
|---|---|---|---|
| **A — arXiv (named)** | `paper/tacl/main-arxiv.tex` | `\anonfalse`, `[acceptedWithA]` **(retained deliberately)** | `paper/build/logos-arxiv.pdf` |
| **B — TACL (anonymous)** | `paper/tacl/main-tacl.tex` | `\anontrue`, no `acceptedWithA` | `paper/build/logos-tacl-anon.pdf` |

Build both: `bash paper/tacl/build.sh` (pdfLaTeX + bibtex + 3 more pdfLaTeX passes).

**Why `[acceptedWithA]` is retained on the arXiv wrapper (verified against `tacl2021v1.sty`):** the
style offers exactly two modes — `submission` (anonymous: confidentiality banner, line-number rulers,
"Anonymous TACL submission") and `acceptedWithA` (`\taclpubformattrue`), which *only* (a) shows the
author block instead of the anonymous slot and (b) removes the submission banner/rulers. It emits **no**
masthead, journal name, acceptance line, or Action-Editor text — there is no third "neutral" mode to
switch to, and removing the option would render the arXiv PDF as a confidential anonymous submission.
Trade-dress scan of the rendered Target A: the only "Transactions of the Association" string in the PDF
is the Luo et al. (2021) bibliography entry (a cited venue, not trade dress); p.1 carries the
"Preprint — under review; not peer reviewed." note. The PDF metadata title is the **full** paper title
and `pdfauthor` is Kyriakos Papadopoulos (an earlier "truncated title" report was a display artifact of
the checking command, not the PDF).

---

## (a) TACL "Comments to the Editor" — ONE ready-to-paste block (authors + preprints + keywords)

> **Author:** Kyriakos Papadopoulos. **Affiliation:** Independent Researcher.
> **Country:** Netherlands. **ORCID:** 0009-0003-0995-2518.
> **Contact email:** ____________ (fill in — see the durability note below).
>
> **Preprint declaration.** A non-anonymous preprint of this work is available:
> Zenodo, "Falsification-First Decipherment: A Decontaminated Inference Framework
> for Testing Undeciphered-Script Claims, with Linear A as a Worked Null",
> DOI ____________ (fill in), deposited ____________ (fill in deposit date); and
> arXiv, same title, arXiv:____________ (fill in id), posted ____________ (fill in
> date). The submitted manuscript does not cite these versions, per TACL policy.
>
> **Keywords:** decipherment; Linear A; undeciphered scripts; multiple-testing
> correction; pre-registration; negative controls; contamination; held-out
> evaluation; low-resource historical languages; falsification.

- Email note: the address entered must be **durable and monitored** through a
  multi-month review cycle, and should ideally **match the arXiv account** used for
  the preprint. The address currently on file (rfpsqzau@nuclearlighters.net) — CONFIRM
  it meets both criteria before submitting.

---

## (b) Pre-specification chronology (verified from repo artifacts, 2026-07-02)

| Item | In-repo commit (freeze) | External timestamp | First execution |
|---|---|---|---|
| prereg-morphology | 2026-06-30 20:27 +0200 | Zenodo `date-released` 2026-07-01 | 2026-06-30 21:15 +0200 (pooled-run findings commit) |
| stratification addendum | 2026-06-30 22:55 | Zenodo `date-released` 2026-07-01 | 2026-07-01 00:52 +0200 (stratified-run findings commit) |
| salgarella addendum | 2026-07-01 00:07 | Zenodo `date-released` 2026-07-01 | 2026-07-01 00:52 +0200 (same stratified-run findings commit) |

First-execution timestamps are the first commits of the corresponding findings documents (commit
granularity; the freeze-precedes-run ordering is visible above at timestamp granularity for all three
rows). The external deposit **postdates** first execution: the paper therefore states
(§3.1 + Appendix A.1) that pre-specifications were frozen **in-repository before each
run** (commit history), and that the external immutable deposit certifies the *current
state* of the registrations, **not temporal priority**.

---

## (c) Page count + appendix policy conformance (final)

- **Governing policy:** the 2021 formatting-instructions statement that appendices count
  toward the page limit is **superseded** by TACL's **"New TACL Appendices Policy"**
  (transacl.org/index.php/tacl/announcement/view/105, **effective March 1, 2024**):
  main content **10 pages** (references exempt), **plus** appendices after the references,
  unreviewed, in two categories — **Category 1 up to 5 pages** (replication detail:
  preprocessing decisions, model parameters, lengthy proofs/derivations, pseudocode, sample
  inputs/outputs, annotator guidelines, URLs) and **Category 2 up to 3 pages**
  (complementary tables and figures explicitly referred to from the main paper). "No free
  text will be allowed in the appendices unless it specifically adds more details of
  Category #1." Exceeding the limits → rejected/returned.
- **Main content (strict measure — the page on which §9.7's LAST line, "…cited
  projects or their authors.", renders): page 10** on BOTH targets, re-measured after
  the 2026-07-02 p.10-restoration micro-pass (method: `pdftotext -layout` page split,
  locating the literal last-line string; corroborated by Ghostscript ink-bbox — p.10
  is inked to the same bottom edge as a full page). Target A: last text row of p.10
  (100% — zero spare rows); Target B: row 77/79 (~97%). **≤10.0 ✓** and completely
  full — the earlier "90%/88%" figures were measured against a mid-§9.7 string, and
  the combined pass had in fact spilled ~2–6 lines onto p.11 on both targets; the
  micro-pass restored p.10 via five sanctioned duplicate-compression edits.
  **Caveat: zero cushion** — any future body addition of even one line will spill;
  re-verify the page boundary on the exact final compiled upload.
- **Category 1 (Appendices A–D + Software & data note, replication prose):**
  **≈4.9 pp ≤ 5.00 ✓** (both targets; spans mid-p.13 after References to p.18 at ~44%;
  re-measured after the micro-pass — unchanged, as all micro-pass edits were in the
  body pp.1–10; Cat-2 re-measured ≈1.5 pp ≤ 3 ✓, App E p.18@44% → p.19, ~88%-full).
  *Note: the tighter internal target of 4.7–4.8 pp was NOT reached — the remaining
  Cat-1 prose is genuine replication detail (procedures, parameters, derivations,
  the new C.1 generation-settings block) whose removal would harm exact replication;
  per the fallback rule this residual-margin shortfall is reported, not silently cut.*
- **Category 2 (Appendix E, "Complementary tables", 11 tables):**
  **≈1.55–1.74 pp ≤ 3 ✓** (Tables 2–12: morphology strata; sensitivity 2×2;
  morphology-induction quantities; metrology quantities; phonology per-test; cross-script
  alignment + controls; LLM per-item reproduction; abstention asymmetry; corpus
  denominators/unicity; detector+gate calibration; index/canary/ablation quantities).
  **Every Appendix E table is explicitly referenced from the main paper** (§3.2, §3.3, §4,
  §6, §7.1–7.3, §8.1–8.2, §9.1 — verified by grep, 1+ body \ref per table).
- **Total document length:** 19 pp each (10 main + ~2.5 references + ~6.6 appendices).
- **Deleted from appendices (non-Cat-1 free text, per policy):** the MDL/DSR-history
  "removed-from-the-gate" aside; the §9.1 axis-vs-survey recap; the §3.5 self-audit
  anecdote ("caught confounds in our own builds" narration); the §9.5 study-wide-budget
  elaboration; the C.3 learning-curve lineage/ancestors positioning; the A.1
  self-review/docstring-correction narration; the B.2 "first draft failed" narration; the
  "$2.80 GPU rental" trivia; the A-appendix "nothing here is load-bearing" preamble; all
  "(relocated from §X)" meta-tags. Nothing load-bearing was deleted — every deleted
  statement either was narration or remains stated in the reviewed body.
- **Main-content conformance note:** reaching the strict ≤10.0 (the earlier
  References-page−1 measure had hidden a ~0.9-pp spill of §9.6–9.7 onto p.11) required,
  beyond the sanctioned §3.1–§3.4 mechanics relocations, replacing **verbatim within-body
  duplicate sentences with cross-references** to their canonical body location (e.g. the
  §1/§2.1 fifteen-challenges enumeration and Sec-6.3 evaluation-gap quote, each stated
  twice; §9 restatements of §3.4/§4/§5/§7.3 sentences; triple-stated archival URLs now
  canonical in §9.7 + Software & data note). Every claim/number/verdict remains stated and
  defended in the body; no number, result, or verdict changed; §5 and Table 1 untouched;
  the 0.6% / Clopper–Pearson ≈1.54% headlines remain in §3.4; abstract byte-identical
  (185 words).

### Relocation log — FIRST trim pass, 2026-07-01 (historical; uses the earlier
### References-page−1 measure; superseded by the strict measure above)

All moves are pure relocation — only derivations, mechanics, historical lineage, and
appendix-duplicated restatements moved; nothing load-bearing left the reviewed body.

| Stage | Block relocated (from → to) | Target A main pp |
|---|---|---|
| baseline | — | **12** (refs top of p.13) |
| 1 | §3.4 MDL / U_floor "removed-from-gate, now a diagnostic" history → App D | 11 (refs ≈90% p.12) |
| 2 | §3.3 lit-index seed/adversarial/62-entry census + L_fake TV-dist ~0.84→~0.33 → App C.5 | 11 |
| 3 | §3.2 S_morph within-form-shuffle FPR (3.0%, 6/200) + saturated power (50/50) → App A.2 | 11 |
| 4 | §9.3 libation-formula held-out detail → App A.3; §9.5 study-wide-budget elaboration → App D | 11 |
| 5 | §4 sign-count denominators/channels, §9.1 H3 near-miss, §9.4 ~7,400-channel note → App C.4 | 11 (≈58% p.12) |
| 6 | §3.4 explicit E[max] formula + Gaussian/independence assumptions (already verbatim in App D) → App D | 11 (≈50% p.12) |
| 7 | §3.4 baseline-citation aside + §3.5 self-audit anecdote → App D (dropped 1 duplicate archival line) | 11 (≈16% p.12) |
| 8 | §9.2 MDL-history recap trim; §8 redundant registered-extension pointer removed | 11 (≈14% p.12) |
| 9 | §9.1 axis-vs-survey recap → App D | A **11** / B **10** |
| 10 | §9.4 unicity + Salgarella restatements (dup of §4 / §2.2 / C.4) | **A 10 / B 10** |

Blocks 1–4 are the prescribed priority order: they moved References up **within** p.12 but
did not cross the p.12→p.11 boundary (12.0 → ≈11.3 effective pp). Stages 5–10 apply the same
category of relocation (mechanics / derivations / history / appendix-duplicated restatements,
every headline kept) until Target A crossed to 10 pp, then **stopped at first-under-10**.

- **Body stands alone:** every Table 1 row and every probe headline (NO POWER; segmentation
  supported; metrology & phonology nulls; capped circular image demo; contamination
  gradient) is still defended in the reviewed body. The gate's **0.6% false-graduation rate**
  and **Clopper–Pearson ≈1.54%** upper bound remain in §3.4; **U ≈ 204–415** remains in §9.4 (and Table 10); **N ≈ 5,792** and **V = 259** now live in Table 10,
  referenced from §4 and Appendix C.4 (Cat-2 tables are body-referenced, per policy); abstract
  unchanged at **185 words**.
- Frozen-content re-verification (compiled body): Clopper–Pearson ≈1.54% present; **no**
  "1.3%"; **no** "effective-n"/"n_eff"; **no** "trivially satisfied"; **no** "frontier
  model"/"virgin"; **no** operative DSR clause (bailey2014 kept only as selective-inference
  lineage, App D). Build: 0 errors, 0 overfull boxes, 0 undefined references.

---

## (d) Anonymization checklist — Target B (`logos-tacl-anon.pdf`)

All verified on the compiled anonymous PDF:

- [x] **No author name** in body or author block (renders "Anonymous TACL submission").
- [x] **No GitHub repo** `github.com/papadopouloskyriakos/logos` (masked to "an anonymized
      artifact (code and pre-registrations released on acceptance)"). *(The only `github.com`
      string remaining is the cited third-party baseline `github.com/ftamburin/CSA_OptMatcher`,
      i.e. Tamburini 2025's code — not author-identifying.)*
- [x] **No Zenodo DOI** `10.5281/zenodo.21087572` (masked to "[artifact DOI withheld for
      review]" / "an anonymized artifact").
- [x] **No ORCID** (author block suppressed).
- [x] **Self-references third-person / neutral** ("the logos artifact (v0.1.0)" → "the
      artifact"; method name **logos** retained — it is not identifying). No "(Anonymous)"
      self-citations.
- [x] **Confidentiality header + line-number rulers** present on all pages (submission mode).
- [x] **Clean PDF metadata** — `pdfinfo paper/build/logos-tacl-anon.pdf`:

```
Title:
Author:
Creator:
Producer:
```

(All four fields empty — no name in Author/Creator/Producer/Title. Metadata stripped via
`\hypersetup{pdfauthor={},pdftitle={},pdfsubject={},pdfkeywords={},pdfcreator={},pdfproducer={}}`
in the `\ifanon` branch; `exiftool`/`qpdf`/`pdftk` were not available in the build environment.)
For contrast, Target A `logos-arxiv.pdf` carries `Title: Falsification-First Decipherment`,
`Author: Kyriakos Papadopoulos` (named build, as intended).

Automated leak scan on the anon PDF text (all counts 0): `Kyriakos`, `Papadopoulos`,
`papadopouloskyriakos`, `zenodo`/`Zenodo`, `21087572`, `0009-0003`, `ORCID`, `logos v0.1.0`.
Line-number rulers present on all 19 pages of Target B (absent on Target A); confidentiality
header on all 19 Target-B pages. "Tom Di Mino" appears in Target B only as the cited
claimant of the analysed public claim — not author-identifying.

---

## (e) Submission-order reminder

1. **Upload the named TeX SOURCE package FIRST** (`paper/arxiv-package/`, tarball
   `paper/arxiv-package.tar.gz`: named wrapper + shared body + `.bbl` + `refs.bib` +
   `tacl2021v1.sty` + `acl_natbib.bst`; arXiv declines TeX-generated PDF-only uploads),
   category **cs.CL** — this needs a **cs.CL endorsement** if the author is not yet
   endorsed. Record the arXiv id + date. The wrapper renders the author block with NO
   acceptance trade dress and a first-page "Preprint — under review; not peer reviewed."
   note (verified on rendered p.1).
2. **Then submit the anonymized PDF** (`logos-tacl-anon.pdf`) to TACL and paste the
   combined block from (a), filling in the Zenodo DOI/date and the arXiv id/date.
   **Check the TACL portal's upload-filename instructions at submission time.**
3. **Re-check the current transacl.org anonymity + preprint policy at submit time**
   (policies change); confirm the author metadata in (a). Length is **provisionally
   conformant — re-verify on the exact final compiled upload**: main content ends on
   p.10, Cat-1 ≈4.97 pp ≤5, Cat-2 ≈1.55–1.74 pp ≤3 (March-2024 appendices policy).
