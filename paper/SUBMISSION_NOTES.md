# Submission notes — logos preprint (TACL + arXiv)

Paper title: **Falsification-First Decipherment: A Decontaminated Inference Framework
for Testing Undeciphered-Script Claims, with Linear A as a Worked Null**

Two PDFs are built from one shared body (`paper/tacl/body.tex`) via two thin wrappers:

| Target | Wrapper | Options | Output |
|---|---|---|---|
| **A — arXiv (named)** | `paper/tacl/main-arxiv.tex` | `\anonfalse`, `[acceptedWithA]` | `paper/build/logos-arxiv.pdf` |
| **B — TACL (anonymous)** | `paper/tacl/main-tacl.tex` | `\anontrue`, no `acceptedWithA` | `paper/build/logos-tacl-anon.pdf` |

Build both: `bash paper/tacl/build.sh` (pdfLaTeX + bibtex + 3 more pdfLaTeX passes).

---

## (a) TACL "Comments to the Editor" — preprint declaration (ready to paste)

> A non-anonymous preprint of this work is available: Zenodo, "Falsification-First
> Decipherment: A Decontaminated Inference Framework for Testing Undeciphered-Script
> Claims, with Linear A as a Worked Null", https://doi.org/10.5281/zenodo.21087572,
> deposited __________ (fill in deposit date); and arXiv ____________ (fill in arXiv id),
> ____________ (fill in date once posted). The submitted manuscript does not reference
> these versions, per TACL policy.

---

## (b) TACL portal — author metadata

- Name: **Kyriakos Papadopoulos**
- Affiliation: **Independent Researcher**
- Country: **Netherlands**
- ORCID: **0009-0003-0995-2518**
- Email: **rfpsqzau@nuclearlighters.net**  *(CONFIRM BEFORE SUBMIT)*

---

## (c) Page count + unicity relocation

- TACL limit is **7–10 content pages** (references excluded; **appendices included**).
- **Main-content page count (through §9 Discussion, excluding References + Appendices):**
  - **Before** the §4 relocation: **~12.5 pp** (Target A: References began ~47% down p.13 → 13 content pages).
  - **After** the §4 relocation: **12 pp** (Target A; §9 fills pp.1–12, References begin at the top of p.13). Target B (anon): also **12 pp** (§9 runs to ~94% of p.12).
- **Unicity relocation applied? YES.** The numeric unicity-distance calculation detail
  (four sign denominators, the ~7,400 vs 5,792 occurrence channels, the U ≈ 204–415
  computation) was moved from §4 into a new appendix subsection **Appendix C.4**; §4 now
  carries only a short qualitative identifiability paragraph plus a pointer. No other
  content was cut.
- **Appendices A–D:** pp.15–20 = **6 pp** (within the ~≤8 pp guideline).
- **⚠️ LENGTH IS STILL OVER THE HARD LIMIT.** Even after the single sanctioned relocation,
  main content is **12 pp** vs the TACL maximum of 10. TACL treats >10 content pages as a
  desk-reject. The relocation was the only reduction authorised for this packaging task
  ("do not cut anything else"), so **the author must trim ~2 pages of content (or move more
  material to appendices, noting appendices count toward the TACL limit) before submitting
  to TACL.** The arXiv target has no length limit and is unaffected.

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

(All four fields empty — no name in Author/Creator/Producer. Metadata stripped via
`\hypersetup{pdfauthor={},pdftitle={},pdfcreator={},pdfproducer={}}` in the `\ifanon` branch;
`exiftool`/`qpdf`/`pdftk` were not available in the build environment.)

Automated leak scan on the anon PDF text (all counts 0): `Kyriakos`, `Papadopoulos`,
`papadopouloskyriakos`, `zenodo`/`Zenodo`, `21087572`, `0009-0003`, `ORCID`.

---

## (e) Submission-order reminder

1. **Post the named arXiv preprint FIRST** (`logos-arxiv.pdf`), category **cs.CL** — this
   needs a **cs.CL endorsement** if the author is not yet endorsed. Record the arXiv id + date.
2. **Then submit the anonymized PDF** (`logos-tacl-anon.pdf`) to TACL and paste the
   declaration from (a), filling in the Zenodo deposit date and the arXiv id/date.
3. **Re-check the current transacl.org anonymity + preprint policy at submit time** (policies
   change); confirm the author metadata in (b); and **resolve the length overage in (c)**
   before uploading to TACL.
