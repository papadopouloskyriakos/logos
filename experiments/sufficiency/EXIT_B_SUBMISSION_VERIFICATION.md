# Exit-B submission verification — does the frozen TACL submission carry the clamped numbers?

**Date:** 2026-07-04. **Read-only pass.** Nothing built, edited, deposited, or fetched. The §2 hard
stop remains in force. This grades one gating fact: does the **exact artifact submitted to TACL
(#11385)** contain the clamped Exit-B sentence / numbers / branch verdicts — and did the frozen
invariant *"the paper asserts NO result from the sufficiency curve"* HOLD or BREAK.

## Bottom line

**The submitted TACL manuscript DOES contain the clamped numbers and result assertions.** The
invariant is **BROKEN**. A TACL editor notice (vehicle B1) is therefore owed on the facts. The same
content is in the Zenodo 21119213 deposit and the `body.tex` source (no drift).

---

## 1. Submitted-PDF identity — hash-verified

| Artifact | Role | Recorded (SUBMISSION_NOTES §f/§0) | Recomputed | Match |
|---|---|---|---|---|
| `paper/build/logos-tacl-anon.pdf` | **TACL #11385 submission** (anon) | sha256 `4e4973ec…4b23bc` | `4e4973ec…4b23bc` | **✓** |
| `paper/build/logos-arxiv.pdf` | **Zenodo 21119213** file (named) | sha256 `a2ab89fa…1ea145` | `a2ab89fa…1ea145` | **✓** |
| `paper/build/logos-arxiv.pdf` | (Zenodo md5, §0) | md5 `f83a0815…2806a9` | `f83a0815…2806a9` | **✓** |
| `paper/arxiv-package.tar.gz` | arXiv TeX (never posted) | sha256 `ae2ee2c1…21faf2` | `ae2ee2c1…21faf2` | **✓** |

Identity rests on a **recorded SHA-256, recomputed and matched** — not merely a file record. `pdfinfo`:
tacl-anon = 19 pp, **no Title/Author** (anonymized, metadata-clean); arxiv = 19 pp, Title
"Falsification-First Decipherment…", Author "Kyriakos Papadopoulos" (named). Both built 2026-07-02
01:26 CEST.

## 2. Grep hit table — submitted PDF (`logos-tacl-anon.pdf`)

Page 9 is the **sole locus** of every sufficiency number (searched full 19 pp; `0.462, 0.475,
0.760, 0.805, 0.044, 0.066, n=276, n=346` each appear on **page 9 only**). Two-column line numbers
interleave in the raw dump; sentences below are from the reading-order (column) extraction.

| Page | Matched string | Verbatim context | Exit-B? |
|---|---|---|---|
| 9 | `0.044 ± 0.023, n=276` | "…stays at its chance floor (0.044 ± 0.023, n=276; floor ≈ 0.004)…" | **Y** |
| 9 | `0.066, n=346` | "…while Cypriot→Greek sits marginally above (0.066, n=346)." | **Y** |
| 9 | `completed 2,000-step` | "…decipherability claim. The completed 2,000-step curve (near-converged…)" | **Y** |
| 9 | `Linear-A-scale locator` | "…splits the branches at the sweep's Linear-A-scale locator (600–700 distinct word-forms…)" | **Y** |
| 9 | `600–700` | "(600–700 distinct word-forms, syllabic normalization)" | **Y** |
| 9 | `every recovery a lower bound` | "…Phoenician→Ugaritic 0.760 vs. 0.805; every recovery a lower bound) splits the branches…" | **Y** |
| 9 | `Linear-A-scale` (2nd) | "Is a Linear-A-scale corpus large enough to recover a decipherment…" (section opener) | Y (protocol) |
| 9 | `sufficiency curve` | "…known-answer sufficiency curve" (section title) | Y (protocol) |
| 2 | `sufficiency` | "…contamination and sufficiency signals (§7)" — topic mention, **no number** | Y (protocol) |
| 16 | `C.3 Information-sufficiency CSA sweep (design and deposit)` | design-only; "full per-size report and per-cell artifacts are deposited (`results/csa/`)" | Y (protocol) |
| 3, 4, 7, 8, 13, 14, 17, 18 | `276` / `346` / `600` / `700` | unrelated numerals (line-number artifacts, §-refs, corpus/table values) | **N** |

**No table, figure caption, appendix, or abstract in the submitted PDF prints the per-size CSA
recovery values.** Appendix C.3 describes the sweep and **points out to the deposit**
(`results/csa/`) rather than tabulating numbers. The abstract/intro contains no sufficiency figure.

## 3. Verbatim Exit-B passage + classification

**Passage (submitted PDF, p9 — "Registered extension: a known-answer sufficiency curve"), verbatim:**

> "Is a Linear-A-scale corpus large enough to recover a decipherment if a known cognate existed?
> Because every benchmark is handed a real cognate signal Linear A lacks, any recovery is an
> optimistic benchmark, conditional on a known cognate relationship: at-floor at Linear-A scale ⇒
> information-insufficient even given a cognate; above-chance ⇒ identifiability (cognate-absence,
> uncorrected multiplicity) rather than corpus size would be implicated; neither branch is a
> decipherability claim. **The completed 2,000-step curve (near-converged: Luvian→Hittite 0.462 vs.
> published 0.475, Phoenician→Ugaritic 0.760 vs. 0.805; every recovery a lower bound) splits the
> branches at the sweep's Linear-A-scale locator (600–700 distinct word-forms, syllabic
> normalization): Linear B→Greek, the primary analog, stays at its chance floor (0.044 ± 0.023,
> n=276; floor ≈ 0.004), while Cypriot→Greek sits marginally above (0.066, n=346). Under-convergence
> keeps the at-floor branch non-definitive; full per-size and per-cell artifacts are deposited
> (Appendix C.3).**"

**Classification: RESULT-ASSERTING (not protocol-only).** The bolded sentence prints two numeric
recovery values (`0.044 ± 0.023`; `0.066`) and two branch verdicts (Linear B→Greek "stays at its
chance floor"; Cypriot→Greek "sits marginally above"). Trigger clauses: *"stays at its chance floor
(0.044 ± 0.023, n=276)"* and *"sits marginally above (0.066, n=346)."* Per the no-charity rule, the
surrounding hedges — "optimistic benchmark", "every recovery a lower bound", "Under-convergence keeps
the at-floor branch non-definitive", "neither branch is a decipherability claim" — do **not**
downgrade a sentence that still states the numbers and the floor/above-floor verdicts. Moreover
those hedges address **under-convergence** (the 2,000-step budget), not the **size clamp**: the text
represents the values as measured "at the sweep's Linear-A-scale locator (600–700 distinct
word-forms)" and calls the curve "completed", both of which the integrity audit shows are false —
the values are the size-276 / size-346 endpoints, and the 600–700 points were unrun.

**Invariant verdict: BROKEN.** The submitted manuscript asserts numeric results and branch verdicts
from the sufficiency curve; it does not merely describe a protocol.

## 4. Source cross-check (`paper/tacl/body.tex`) — diagnostic, no drift

`body.tex` lines 709–727 carry the **identical** passage. No post-submission drift on any target
string:
- l.720 `The completed 2{,}000-step curve (near-converged:`
- l.723 `branches at the sweep's Linear-A-scale locator (600--700 distinct`
- l.725 `analog, stays at its chance floor ($0.044\pm0.023$, $n{=}276$; floor`
- l.726 `$\approx0.004$), while Cypriot$\to$Greek sits marginally above`
- l.727 `($0.066$, $n{=}346$). Under-convergence keeps the at-floor branch`

(The submitted PDF is authoritative for the B1 question; the source is reported only to show the
frozen text has not moved. Source == submitted PDF on every hit.)

## 5. Target A — `logos-arxiv.pdf` (named build; also the Zenodo file)

**Present, identical passage.** All sufficiency numbers appear on **page 9** of the named PDF too
(`0.044`, `n=276`, `0.066`, `n=346`, `completed 2,000-step`, `Linear-A-scale locator`,
`marginally above`, `non-definitive` — verified by reading-order extraction). Target A is **not yet
on arXiv** (SUBMISSION_NOTES §0/§e); it matters only if arXiv is ever posted — that upload would
carry the clamped content and must be corrected first.

## 6. Zenodo record 10.5281/zenodo.21119213 — manifest + hash check

- **Deposited file (per SUBMISSION_NOTES §0): `logos-arxiv.pdf`** — one file, resource type Preprint,
  CC-BY-4.0, Version 1.0 (concept DOI 21119212). Recorded md5 `f83a0815…2806a9` **and** sha256
  `a2ab89fa…1ea145`; both **recomputed = MATCH** (§1). So the deposited Zenodo file is byte-identical
  to the local `logos-arxiv.pdf`, which **carries the clamped page-9 passage**.
- The in-repo markdown mirror `docs/preprint/logos-preprint-2026-07-01-condensed-v6.md` (**line 147**)
  also carries the identical clamped sentence — but it is the **repo historical record, NOT a file
  deposited on Zenodo 21119213**. The file on Zenodo that carries the clamp is the **PDF**.
- No local copy missing; no hash mismatch; **Zenodo was not fetched** (local records only).

## 7. Bottom line

**The submitted TACL manuscript (#11385, `logos-tacl-anon.pdf`, sha256 `4e4973ec…4b23bc`) DOES
contain the clamped numbers and result assertions** ("completed 2,000-step curve … at the
Linear-A-scale locator (600–700 …): Linear B→Greek … stays at its chance floor (0.044 ± 0.023,
n=276) … Cypriot→Greek sits marginally above (0.066, n=346)"), all on **page 9**. The frozen
invariant "the paper asserts NO result from the sufficiency curve" is **BROKEN**. The identical
content is in the Zenodo 21119213 deposit and the `body.tex` source. On these facts a **TACL editor
notice (B1) is owed**; correction of the Zenodo record (B2/B3) and Target A applies to the same
passage. (Correction wording/timing is a later prompt — this pass is findings only.)

---

### Adversarial verification (3-lens workflow `wf_5ff49b5a-a4b`, 4 agents, 0 errors)

Three independent lenses over the full page-marked submitted-PDF text, then a synthesizer.
**Unanimous, no verdict-level disagreement.**

- **Lens A (classify):** RESULT-ASSERTING; invariant **BROKEN**. Trigger clause: *"Linear B→Greek …
  stays at its chance floor (0.044 ± 0.023, n=276 …), while Cypriot→Greek sits marginally above
  (0.066, n=346)."*
- **Lens B (exhaustive 20-page sweep):** page 9 is the **SOLE locus**; `missed_anything=false`.
  Independently confirmed: **Table 1 has no CSA/sufficiency row**; no table/caption/abstract/figure
  amplifies the numbers; Appendix C.3 prints zero curve values and defers to `results/csa/`. The
  abstract/§9.4 *"identifiability, rather than corpus size"* thesis is **not** a curve
  result-assertion (prints no number; rests on the independent identifiability + unicity argument;
  points the opposite direction to the at-floor CSA reading).
- **Lens C (argue-the-opposite):** `can_sustain_no_result_reading=false`. The strongest no-result
  defense — that §9.4 "explicitly withdrew" the sufficiency claim — **fails**: that withdrawal
  covers a **different quantity** (the unicity toy-model U≈204–415 signs, §4/Table 10/App C.4), not
  the CSA curve, so **it does not retract the page-9 numbers**. "Neither branch is a decipherability
  claim" disclaims only a Linear-A decipherment conclusion, not the numeric benchmark or the two
  branch verdicts. Concession: the manuscript prints the numbers and asserts both branch verdicts.
- **Synthesizer:** `invariant=BROKEN`, `submitted_contains_clamped_content=true`,
  `editor_notice_owed=true`, `loci_pages=[9]`. Also notes the defect is **visible on the face of the
  text** — printed `n=276`/`n=346` fall *below* the stated "600–700 distinct word-forms" locator, so
  the paper presents endpoint clamps as if measured at the locator.

**Convergent verdict: the submitted, hash-frozen TACL artifact itself carries the clamped values and
branch verdicts — the defect is not confined to internal artifacts — so a B1 editor notice is owed.**
One new point for the correction decision: **no existing sentence in the paper retracts the page-9
CSA numbers** (the §9.4 withdrawal is about unicity, not the curve).
