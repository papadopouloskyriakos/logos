# E206 — Independently gated onomastic record linkage · Stage 1: SLOT FREEZE

**Classification (PRECHECK §4):** EXTENSION with hard gate — the exact-continuity channel is
CLOSED (NULL_PUBLISHED); the genuinely-new element is a drift-tolerant, pre-registered design
with a NEW input freeze. **This prereg covers Stage 1 only** (internal slot definition + freeze).
Stage 2 (external inventories, correspondence models, canaries, multiplicity family) will be a
separate prereg committed only AFTER the Stage-1 freeze is on record. **No external name
inventory, list, lexicon, or database is loaded, read, or consulted at Stage 1.**

## Slot definition (internal structure ONLY; all criteria mechanical)

Inputs: `corpus/silver/inscriptions_structured.json` (hash in data_manifest.sha256). Word = the
editor token; unit of candidacy = the word type (sign-tuple).

Candidate slot classes:
- **S1 ledger-entry heads:** word (len ≥ 2) immediately preceding a numeral token — the
  registered entry-head position (E060 template; E069 name-then-modifiers). Candidate strings =
  entry-head word types with ≥ 2 token occurrences.
- **S2 totals heads:** word types occurring adjacent (±2 tokens) to the KU-RO sequence heading a
  totals line — candidate account/office slots.
- **S3 libation-order slot-2:** word types occupying the second position of the E072 canonical
  libation order on libation-genre documents — the internal candidate dedicant slot.
- **S4 cross-site recurrent non-formula words:** word types (len ≥ 3) attested at ≥ 2 sites,
  excluding S3 formula vocabulary — candidate toponym class.
- **S5 site-local recurrent words:** word types (len ≥ 3) with ≥ 3 tokens all at one site —
  candidate person/official class.

Per candidate the freeze records: sign sequence, class(es), token count, document IDs, sites,
positional rule that admitted it.

## Contamination classification (mechanical, frozen with the set)

A candidate is CONTAMINATED_PRIOR_EXPOSURE if its sign sequence appears in: the five published
toponym equations (PA-I-TO, SE-TO-I-JA, SU-KI-RI-TA, DI-KI-TE-family, I-DA-family), the
cross-script pin derivations (I, RI, SU, TO source words), the canonical libation-formula
vocabulary as published (A-TA-I-*301-WA-JA family), or KU-RO / PO-TO-KU-RO themselves.
Contaminated candidates stay IN the freeze but are flagged and will be scored separately at
Stage 2 (they cannot contribute to a graduation claim).

## Freeze mechanics

Emit `SLOT_FREEZE.json` (candidates + criteria + counts) and `SLOT_FREEZE.sha256`; commit both.
Any Stage-2 change to the candidate set is an amendment with reason. After this commit, external
inventories may be assembled under Stage 2's own prereg (multiplicity family: every candidate
language × name database × transliteration × segmentation × value-transfer rule × edit cost ×
phonetic prior × chronology filter × geography filter × borrowing model).

## Forbidden at Stage 1

Loading any external name data; scoring any candidate against anything; wording any candidate as
a name/place/person (they are SLOT candidates, L2 structural objects, until Stage 2 evidence).
