# EPOCH-005 — KNZg57a provenance trace (frontier F8, gate H)

**Campaign:** research/linear-a-frontier-72h · **Date frozen:** 2026-07-08 · **Seed:** 20260708
**Constitution:** v2.2 · **Articles triggered:** VII (search receipt), IX (info budget: this epoch adds
ZERO scoring information — provenance metadata only), XI (source-dependency), XII (non-circularity: the
seals' exclusion lists are the TARGET of the audit, not an input to it), XVII (append-only; possible
ERRATUM output), XVIII (assumption A-3 from EPOCH-001 under test), XXII (this header).

## Claim layer

**L0 (physical/documentary provenance only).** No sign-value, structural, or semantic claim. The epoch
grades a METADATA question: where did the 5-token silver reading of KNZg57a (*401+RU, *401+RU, *418+L2,
NI, VAS) come from, and does its existence breach the Anetaki seal exclusion assumptions?

## Hypotheses (frozen before any trace step runs)

- **H-P1:** The reading has an identifiable published/public source (lineara.xyz's own upstream:
  GORILA, Younger, SigLA, Del Freo rapports, Kanta et al. 2024, a commit-documented editor act, or a
  cited edition). Prediction: the source names the same 5 tokens (or a superset) for KN Zg 57.
- **H-P2:** The reading is an editorial reconstruction by the lineara.xyz maintainer (e.g. from
  published photographs or the editors' prose 'vas+RU' statement), with no independent published
  transliteration. Prediction: git history / commentary shows the tokens appear without a cited edition,
  and no candidate source prints them.
- **H-P3 (adversarial):** The reading is a fabrication/placeholder with no defensible basis.
  Prediction: tokens contradict every physical description (sign count, ligatures) in Kanta et al. 2024
  / Del Freo.

## Derivation vs held-out

Not a statistical claim; units = source records. Derivation set: the in-repo chain (silver builder,
bronze snapshots, /tmp/lineara clone + git log). "Held-out" check: the candidate published sources
(audited independently) must corroborate or fail to corroborate whatever the in-repo chain asserts.

## Controls

- **Positive control (runs FIRST):** trace a KNOWN-provenance silver record (KNZg55, JA-SA-JA — Younger
  misctexts + Civitillo 2024 + CMS II.2 213) through the identical pipeline; the trace must recover its
  published source. If the method cannot source KNZg55, it has no power on KNZg57a.
- **Negative control:** query the same candidate-source set for the NONEXISTENT "KN Zg 56" reading
  (EPOCH-001 established it has no public identity); the trace must return zero sources. A method that
  "finds" sources for Zg 56 is confabulating.

## Search breadth / audit floor

≥ 20 distinct candidate source records OR the complete enumerable narrow corpus, drawn from: lineara.xyz
git history + commentary + site pages; GORILA vol. coverage (via Younger's GORILA-derived files);
Younger misctexts/HTtexts captures; Del Freo Rapport 2016-2021 (on disk); Kanta et al. 2024 PDF (on
disk); SigLA database (on-disk decode); Civitillo 2024; Rjabchikov 2025 (quarantined — checked only for
token overlap, never as evidence); Chiapello 2024 archive; media echoes; web (lineara.xyz live,
github.com/mwenge, archive.org captures). Every record → SOURCE_REGISTER-style row in result.json.

## Kanta-2024 'vas+RU' sub-question (frozen)

Grade mechanically: does the PDF text state a reading that *entails* the silver 5-token sequence?
Entailment rule: the statement must (a) name the same sign identities, (b) the same count/order, on
(c) the same face. Anything less = DOES_NOT_LICENSE (it may still be *consistent*).

## Verdict rule (mechanical, frozen)

- **PROVENANCE_ESTABLISHED** iff ≥1 audited public record prints the 5-token sequence (≥4/5 tokens,
  same order) for KN Zg 57 with a citable locus, AND the record predates or equals the silver ingest.
  Then: if that record is public and outside the seals' declared exclusions → **ERRATUM_REQUIRED** flag.
- **FABRICATION_SUSPECTED** iff H-P3's prediction holds (tokens contradict the physical descriptions)
  AND no chain step shows a defensible editorial basis.
- **PROVENANCE_UNRESOLVED** otherwise (including the H-P2 outcome: editorial reconstruction with a
  traceable in-chain act but no published transliteration). Then: recommend quarantining KNZg57a from
  all future seal scoring + record disposition in the campaign assumption register.

Multiplicity: 3 hypotheses, 1 target, no tunable thresholds → no deflation needed beyond reporting all
three outcomes. LLM grades nothing; the verdict is the rule above applied to the audit table.
