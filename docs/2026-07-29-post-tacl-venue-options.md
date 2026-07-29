# Post-TACL venue options — 2026-07-29

**Context:** TACL #11385 was desk-rejected 2026-07-29 (decision "(d)"; no external
reviews; TACL barred until 2027-07-29). Full record: `paper/SUBMISSION_NOTES.md` §(g).
**This document is analysis for an owner decision — nothing has been submitted anywhere.**

**Provenance:** produced 2026-07-29 by an 8-agent analysis pass (1 manuscript-critique
reader of `paper/tacl/body.tex`, 1 governance reader of `governance/CONSTITUTION.md`,
5 venue scouts with live web verification against official venue pages — all 5 reported
successful web access — and 1 synthesis judge). Deadlines/policies below were checked
2026-07-29 and **must be re-verified at execution time**.

Articles consulted: I (decision = SOURCE_REPORTED), XVII (append-only), XXII (stage
citation), XXIII (no re-narration of outcomes). The desk rejection is an **editorial
event, not a scientific verdict** — no claim, number, or verdict changed status; the
paper remains COMPLIANT at L2 (`governance/RETROACTIVE_COMPLIANCE.md`); no ERRATUM /
INVALIDATION class applies.

---

## 1. Honest read of the rejection (from the manuscript itself)

**What the critique got right (about half of it the paper invited):**

- "Largely applies existing statistical methods" matches the paper's own explicit
  deferrals: E[max] bar credited to Bailey et al. 2014, permutation nulls "after
  Packard 1974", Tamburini's CSA matcher used "not a reimplementation", Clopper–Pearson
  and DP segmentation textbook. No new algorithm or theorem is claimed anywhere.
- "The primary contribution appears to be the organizational framework itself" is nearly
  a quote of §9.1 ("The discipline is the contribution … The deliverable … is not a
  reading of Linear A. It is a harness."). A desk editor took the paper at its word.
- The systems register is real and sits in the main body: "logos" as agent,
  `scripts/verdict.py`, SearchLog, repo invariants by number, grep-clean audit language.
  Engineering-artifact signals, not CL-paper signals — partly an artifact of the
  zero-cushion 10-pp compression.

**What the critique undersold (real, citable, and none of it needs a number to change):**

- The **calibrated graduation gate**: a claim-acceptance procedure with a *measured*
  Type-I error under an adversarial best-of-100 random-map null (3/500 = 0.6%, CP95
  upper ≈1.54%) **paired with** a firing Linear B positive control (0.562 vs ~0.30
  floor). A detector calibrated in both directions is a methodological instrument, not
  "applying existing statistics"; no prior decipherment work reports a calibrated
  false-graduation rate.
- The **LLM-era decontamination constructs**: post-model-release L_fake fabricated-language
  canary ("nothing to memorise"), the L_indexed/L_not_indexed partition, and the
  `generalizes_to_not_indexed` graduation clause — new experimental designs, not
  reorganized statistics.
- The paper directly answers the open evaluation problem named in the field's own
  flagship survey (Braović et al. 2024, *Computational Linguistics* 50(2) §6.3), on
  canonical CL tasks in the Snyder/Berg-Kirkpatrick/Luo lineage.

**Bottom line:** a venue-fit judgment, not a quality judgment. The rational path is not
to contest TACL but to pick the contribution class the work actually belongs to and
rewrite frame, register, and lead — the governance-frozen results pass through untouched.

**Three viable reframings (framing/ordering/register only; no claim changes):**

1. **Evaluation-methodology paper** (→ *Computational Linguistics* journal): lead with
   the calibrated-gate experiment + differentiated-verdict Table 1; systems vocabulary
   demoted to a reproducibility appendix. Addresses both stated reasons.
2. **Pre-registered empirical study / rigorous-null framing** (→ RSOS / PLOS ONE /
   JCA-CHR-class): the harness becomes Methods; the frozen verdicts become Findings;
   venues that judge pre-registration and calibration on their own terms.
3. **Applied selective-inference case study** (→ AOAS / JRSS-A / HDSR-class): the
   finance→decipherment transfer of multiplicity control, with the instrumented
   SearchLog and Monte-Carlo gate calibration promoted to the core.

---

## 2. Governance constraints on any resubmission (condensed)

- **§(f) hashes and the Zenodo v1.0 record are permanent** — never edited or re-pointed.
  The operational "no edits to paper/" bar lapses; an *archival* freeze of the v1.0
  artifacts replaces it (Art. XVII, XIV).
- **New venue = new build**: rebuild → re-measure against *that venue's* limits (the
  p.10 / Cat-1 ≤5 / Cat-2 ≤3 measures were TACL-specific) → re-run the §(d)
  anonymization checklist if the venue is anonymous → **append** a fresh dated sha256
  section to SUBMISSION_NOTES (never touching §(f)).
- **If content changes, the preprint updates as a NEW Zenodo version** under concept DOI
  10.5281/zenodo.21119212; v1.0 stays immutable; verify byte-identity deposit↔local.
- **May change:** framing, format, exposition, venue wrapper, preprint-declaration text;
  `docs/revision-queue/` material becomes eligible (CSA sweep only with the T0
  CONVERGENCE_ARTIFACT framing and N1/N4 rewordings).
- **May never change:** any frozen verdict/number/result (corrections only via recorded
  ERRATUM/SUPERSEDING/INVALIDATION); wording above L2; the 0.75 signal cap;
  effective-n / search-receipt / info-budget reporting; script-generated counts.
- **Prior-submission honesty:** where a venue asks, disclose the Zenodo DOI and the
  closed TACL #11385 desk-reject.
- The resubmission effort is itself a stage: Art. XXII header
  (`scripts/stage_header.py`) + compliance close.

---

## 3. Ranked venues (21 assessed; judge synthesis over 5 web-verified scout reports)

| # | Venue | Fit | One-line rationale |
|---|-------|-----|--------------------|
| 1 | **Computational Linguistics (MIT Press)** | HIGH | Both TACL reasons invert: Long-Paper criterion *is* "methodological or conceptual innovation"; short-paper track names "well-analyzed negative results"; home of the Sproat–Rao decipherment-rigor debate; answers Braović CL 50(2) §6.3 in its own pages; named review ⇒ preprint zero-friction; rolling; ~16.5-day avg first decision incl. desk |
| 2 | EACL 2027 (ARR Aug 3 cycle) | HIGH | Best conference fit (Resources & Eval / Interpretability; Findings safety net; notify Nov 12) — but the only feeding cycle closes **Aug 3 (5 days away)**, forcing a rushed 8-pp compression that pushes *against* the "systems framing" critique |
| 3 | Findings of *ACL | HIGH | Exists precisely for "sound but below the novelty bar" — TACL reason 1 verbatim; rides any ARR commitment, no separate submission |
| 4 | ACL Rolling Review (platform) | HIGH | Vehicle, not destination. TACL's 1-year bar does **not** extend to ARR. Cycles: Aug 3 → EACL; Oct 12 → NAACL/COLING 2027 (commit Dec 20); Jan 2027 → ACL 2027. No anonymity period since Feb 2024; do NOT tick the binding no-preprint pledge |
| 5 | Cryptologia (T&F) | HIGH | Best fit for the paper *as it stands*: statistical debunking of claimed decipherments is the genre, unicity distance native vocabulary; 20-day avg first decision; costs: no CL-community visibility, 11% acceptance, Chicago-style restyle |
| 6 | Royal Society Open Science | HIGH | Objective review — novelty is *definitionally* not a rejection ground; nulls are regular research articles; format-free initial submission (lowest delta of the general venues); ~GBP 1,700 APC |
| 7 | JDMDH (Episciences overlay) | HIGH | The Zenodo preprint **is the submission object** (overlay journal requires it); diamond OA; frozen PDF submits as-is; lowest prestige of the HIGH tier |
| 8 | PLOS ONE | MED-HIGH | Soundness-only review, no length limits, preprints explicitly fine; $2,477 APC; weak selectivity signal |
| 9 | HSS Communications (Nature) | MED-HIGH | Strong subject fit; ~8,000-word cap = light trim; double-anon default with preprint tolerated (blinding = one-search fiction); APC ~£1,390 |
| 10 | NAACL 2027 / COLING 2027 (ARR Oct 12) | MED | The *unhurried* ARR cycle — 2.5 months to reframe; correct landing spot if CL desk-rejects; COLING selectable at commitment |
| 11 | J. Quantitative Linguistics | MED | Statistical substance fits, but "simple application of existing theory unlikely to be published" re-runs the TACL fight; ~8k words *inclusive* = hardest honest compression |
| 12 | DSH (Oxford) | MED | Canonical DSH shape; 6–12+ month timelines, 9k-word cap, generalist exposition burden |
| 13 | LRE (Springer) | MED | Evaluation-protocol half fits; resource half hobbled by GORILA/SigLA redistribution limits |
| 14 | ACL 2027 (ARR Jan cycle) | MED | Highest prestige, highest recurrence risk of reason 1; third shot carrying ARR review history, not first |
| 15 | J. Language Modelling | MED-LOW | 25–50-pp envelope would undo the compression, but scope-gamble ("quantitative philology"?) + strict anonymity + no stated preprint policy (pre-query the editor) |
| 16 | Science Advances | MED-LOW | 15k-word limit fits everything; significance gatekeeping re-runs the "is a disciplined null big enough" gamble; ~$4,500 APC |
| 17 | ACM JOCCH | MED-LOW | Only venue with real preprint tension (double-anon, "immediate rejection" language; ACM grandfathers the deposit but blinding is trivially broken); community skews 3D/museums |
| 18 | DHQ | MED-LOW | Right audience, worst pipeline: no LaTeX path (TEI/Word re-set of all math), Oct 15 intake, long backlog |
| 19 | PNAS | LOW-MED | ~4k-word body = cutting the paper in half into SI; null is a hard "discovery" sell; only rational after the framing proves itself elsewhere |
| 20 | Kadmos | LOW as-is | The mission's expert community, but a statistics paper is out-of-genre — correct role is a **later epigraphy-first companion article**, same frozen results, inverted framing |
| 21 | EMNLP 2026 | CLOSED | Feeding ARR cycle (May 25) passed; listed so nothing is dropped silently |

**Preprint check:** at **no** scouted venue is the public non-anonymous Zenodo preprint
strictly disqualifying; it is an *asset* at JDMDH (required) and frictionless at CL,
RSOS, PLOS ONE, LRE, DSH, PNAS, Science Advances, Kadmos. Genuine tension only at JOCCH.

---

## 4. Recommended path (judge synthesis; owner decides)

**Primary: *Computational Linguistics* (MIT Press), Long Paper, named review.**
Rolling submission (submissions.cljournal.org), diamond OA, ~16.5-day average first
decision including desk — a cheap, fast test of the structurally best-fit venue, and it
keeps the ARR Oct 12 fallback fully alive.

1. ~~Record the decision append-only (SUBMISSION_NOTES §(g)) + update pointers~~ —
   **DONE 2026-07-29** (commit 86fb433).
2. Open the resubmission stage per Art. XXII (`scripts/stage_header.py`; articles I, V,
   VI, VII, VIII, IX, XV, XVII, XIX, XXII, XXIII).
3. **Reframe rewrite** of `paper/tacl/body.tex` per §1-option-1: retitle around "how
   should decipherment claims be evaluated"; lead with the calibrated gate (0.6% /
   CP95 ≈1.54% / LB positive control 0.562) and Table 1; open related-work on Braović
   CL 50(2) §6.3 + Sproat–Rao; foreground the decontamination constructs; demote systems
   vocabulary to a reproducibility appendix. Framing only; every frozen number/verdict
   unchanged.
4. **Convert format**: TACL two-column → `clv2025.cls` single-column + compling bib;
   names on p.1 (no anonymization pass); 150–250-word abstract; Long-Paper target
   30–40 pp (fold Appendices C/D into the body); PDF + separate title/abstract file.
5. **Re-freeze**: fresh sha256s appended as a new dated SUBMISSION_NOTES section (§(f)
   untouched); new Zenodo **version** under concept DOI 10.5281/zenodo.21119212,
   byte-verified.
6. **Submit** with a cover letter disclosing the Zenodo DOI and the closed TACL
   desk-reject; Art. XXII compliance close; commit + push.
7. **Sequenced fallback** (no concurrent submission — CL bars it): if CL desk-rejects
   (~2–3 weeks), pivot to **ARR Oct 12 → NAACL/COLING 2027** with the Findings tier as
   safety net (8-pp ACL style + mandatory Limitations section + anonymized PDF + RNLP
   checklist; do not tick the binding no-preprint pledge). **Deliberately skip the
   Aug 3 EACL cycle** — a 5-day rushed compression aggravates the exact defect TACL
   named and burns an ARR history.

**Low-effort parallel-safe alternates** (not refereed-concurrent with CL; pick instead
of, not alongside): RSOS or JDMDH submit nearly as-is; JDMDH uses the existing Zenodo
record directly. **Later, regardless of venue:** a Kadmos epigraphy-first companion
article to reach the expert community the mission actually targets.

---

*Compliance: this document records an editorial event (SOURCE_REPORTED) and venue
analysis; no scientific status changed; no claim worded above L2; no submission made.
Arts. I, XVII, XXII consulted. Deadlines re-verify at execution time.*

---

## 5. Addendum — owner feedback and revised recommendation (2026-07-29, same day)

**Accountability finding (owner-raised, record-verified):** the original TACL venue
choice was made with **no pre-submission fit analysis and no committed prediction** —
`docs/scope-freeze-2026-06-30.md` listed the venue decision as an open item, and this
document is the first venue analysis in the repo, written *after* the rejection. The
assistant chose the venue, wrote the paper to it, and stated no desk-pass confidence
the owner could hold it to; the owner's name carried the risk. This process failure is
now closed by binding rules in `paper/SUBMISSION_NOTES.md` §(h) (owner's informed go
required; committed gradeable prediction before any submission; no certainty claims;
"stop at the preprint" always on the table).

**Revised recommendation.** §4's CL-first path optimized for field visibility. The
owner has made the objective function explicit: **not getting burned again ranks above
visibility.** Under that objective the ranking changes:

1. **Royal Society Open Science** (or **PLOS ONE**) first — novelty is definitionally
   not a review criterion, so the §(g) failure mode *cannot recur* at the desk;
   judgment ranges (label: judgment, not mechanical): ~90% desk pass, ~75–85%
   eventual acceptance after a revision round.
2. **JDMDH** as the near-zero-cost alternative — the existing Zenodo deposit is
   itself the submission object.
3. **CL and the ARR/*ACL paths are demoted** — they re-enter the taste of the same
   community that produced the desk reject; ~60–70% desk / ~40–55% acceptance
   (judgment).
4. **"Stop at the preprint" is a standing option, not a fallback of shame** — the
   work is published, citable, and permanent under the owner's DOI.

Nothing moves — no formatting, no editor emails, no submission — without the owner's
explicit decision. There is no deadline pressure; the only near-term deadline (ARR
Aug 3) was already deliberately declined in §4.
