# Finding 2026-06-30 — cleaned sign inventory (the keystone, done + verified)

The GORILA/SigLA sign ontology, built by **inheritance (parse + metadata join), not
clustering** — exactly as the expert audit mandated (Q5). Independently verified (not just the
workflow's self-report): ontology class counts, the cleaned floor, and 35/35 tests (+4
documented xfails) all reproduce. Builder `scripts/inventory/build_ontology.py`; floor
`scripts/inventory/floor_cleaned.py`.

## The cleaned inventory

259 raw transliteration tokens → **166 canonical sign ids**, classified by functional class:

| class | count |
|---|---|
| syllabogram-AB (shared with Linear B, known values) | 59 |
| syllabogram-Aonly (`*`-series, undeciphered) | 72 |
| logogram (commodity ideograms: GRA/VIN/VIR/HIDE/OLE…; sexed `*F`/`*M`) | 20 |
| fraction (`*800`–`*929` Aegean fraction series) | 10 |
| numeral (Aegean number glyphs) | 2 |
| uncertain (honestly marked, not forced: `None`, `QA2`, 1 PUA glyph) | 3 |

Three syllabogram inventories (logograms/numerals/fractions kept as **separate channels** —
verified zero leaks into the syllabogram stream):
- **conservative (PRIMARY): V=92, N=5171** (AB + clearly-A-only; ligatures decomposed;
  letter-suffix allographs merged to base; subscripted RA2/PA3/TA2/PU2 kept distinct).
- exploratory: V=88 (conservative + subscripted-AB collapse — an aggressive graphic-allograph
  bound, not a phonetic claim).
- raw syllabogram: V=131 (ligatures as single symbols, no merges).

**AB vs A-only is read straight off the token** (verified against
`/tmp/lineara/.../syllables.txt`): bare CV/V matching the Linear-B syllabary → AB; a literal
`*`-prefix + GORILA catalogue number → A-only. This is the GORILA/SigLA editorial convention,
not a learned guess.

## Floor on the cleaned stream (still a toy-model precondition)

| stream | N | V | H0 | H_rate | D | U(P=30) |
|---|---|---|---|---|---|---|
| **conservative (PRIMARY)** | 5171 | **92** | 5.590 | 4.467 | 2.057 | **219** |
| exploratory | 5171 | 88 | 5.510 | 4.467 | 1.992 | 217 |
| raw syllabogram | 5117 | 131 | 5.669 | 4.432 | 2.602 | 247 |
| raw silver V=259 (old) | 5792 | 259 | 6.210 | 4.330 | 3.687 | 345 |

- Cleaning **lowers** V (259→92) and **raises** H_rate slightly (4.330→4.467) — i.e. removing
  low-entropy logograms/numerals makes the syllabogram stream *less* redundant, modestly
  *raising* U — but **U ≪ N holds on every stream**. (U(P=30) ranges 217–345 vs N≈5.1–5.8k.)
- The raw-259 row **reproduces the original finding exactly** → validates that `floor_cleaned`
  reuses `corpus_info`'s formula (the test asserts the functions are identical objects).
- **STILL a toy-model precondition only** — the unicity-as-identifiability claim is withdrawn
  (red-team synthesis §1). U≤N shows measurable recurrent structure, not that a decipherment is
  identifiable. The real test is pseudo-decipherment learning curves (#16).

## Caveats (honest)

- **One bounded classification bug** (verify-flagged): star-**prefixed** logograms whose tail is
  neither a pure number nor an `F`/`M` suffix (`*OLIV`, `*406VAS`) fall through to
  syllabogram-Aonly in the RAW stream + ontology. The confidence filter keeps them out of the
  conservative PRIMARY, so the headline V=92 and the floor PRIMARY are clean. Fix is a one-line
  classifier tightening.
- **Numerals under-represented** (only 2 bare Aegean glyphs): the silver `signs` array came from
  `transliteratedWords` only; most numeric content lives in `parsedInscription`, which
  `corpus_io` did not carry. A complete numeral/fraction channel needs a re-ingest of
  `parsedInscription`.
- ~41 hapax/ligature-only A-only signs are excluded from conservative by a stated frequency
  threshold; an epigrapher's sign-by-sign review could move several (conservative V=92 ≈ ±5).

## What this unblocks

- **Track B (A↔B phonetic imputation):** the 59 AB signs (shared, known Linear-B values) are the
  anchors; the 72 A-only signs are the imputation targets.
- **Pseudo-decipherment curriculum (#16):** a clean V≈92 syllabogram stream to downsample Linear
  B against.
