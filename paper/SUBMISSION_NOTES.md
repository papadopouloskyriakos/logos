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

## (c) Page count + relocation to appendices (main content trimmed 12 → 10 pp)

- **Measure (this packaging pass):** main content = everything through §9 Discussion
  (the "Registered extension" section counts; Appendices A–D do **not**), **excluding
  References + Appendices**. Measured on **Target A** as (page on which the References
  section begins) − 1.
- **Final main-content page count: 10 pp** — identical on both targets.
  - Target A `logos-arxiv.pdf`: References begins on **p.11** (≈85% down) → **10 pp**.
  - Target B `logos-tacl-anon.pdf`: References begins on **p.11** (≈74% down) → **10 pp**.
  - No overshoot: main content fills ≈9.8 pp (aim was 9.5–10).
- **Total document length:** 20 pp each (main content + References + Appendices A–D).
- **⚠️ Appendix-counting caveat.** This pass trimmed **main content** to ≤10 pp by
  relocating derivations/mechanics/history to appendices, per the "content ≤10 pp,
  appendices excluded" reading. **If TACL counts appendices toward the 10-page cap**
  (re-confirm current transacl.org policy at submit time), the ~10 pp of appendices must be
  reconsidered separately. arXiv (Target A) has no length limit.

### Relocation log (measured on Target A; every headline/claim/number/verdict kept in the body)

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
  and **Clopper–Pearson ≈1.54%** upper bound remain in §3.4; **U ≈ 204–415, N ≈ 5,792,
  V = 259** remain in §4/§9.4; abstract unchanged at **185 words**.
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
Line-number rulers present on all 20 pages of Target B (absent on Target A); confidentiality
header on all 20 Target-B pages.

---

## (e) Submission-order reminder

1. **Post the named arXiv preprint FIRST** (`logos-arxiv.pdf`), category **cs.CL** — this
   needs a **cs.CL endorsement** if the author is not yet endorsed. Record the arXiv id + date.
2. **Then submit the anonymized PDF** (`logos-tacl-anon.pdf`) to TACL and paste the
   declaration from (a), filling in the Zenodo deposit date and the arXiv id/date.
3. **Re-check the current transacl.org anonymity + preprint policy at submit time** (policies
   change); confirm the author metadata in (b); and **resolve the length overage in (c)**
   before uploading to TACL.
