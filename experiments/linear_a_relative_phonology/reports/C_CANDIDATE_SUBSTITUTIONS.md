# C1 — Substitution / Alternation Candidates in Linear A

**Task C1.** Catalogue Linear A word-forms that stand in a **one-sign contrast** in matched
contexts, separated into philological categories, with a full metadata record and a
non-phonological alternative explanation per candidate. **No phonetic value is assigned to any
sign** — signs are compared as opaque GORILA/SigLA transliteration tokens (Constitution v2.2
Art. V L2/L3 ceiling; Art. XII: the target is never graded by a rule that reads it).

- Engine: `experiments/linear_a_relative_phonology/scripts/c1_substitution_candidates.py`
- Data: `experiments/linear_a_relative_phonology/data/C1_candidates.json` (full records)
- Seed 20260708, deterministic, pure stdlib. All counts below are script-generated (Invariant 12).

## Corpus and method

- **3,147 GORILA word units** (silver `inscriptions_structured.json`), **1,165 distinct word
  types**, of which **984 are length ≥ 2** (a one-sign contrast needs a ≥2-sign shared context),
  across **1,341 documents / 52 sites**.
- **Substitution pair** = two equal-length word types agreeing at every position but one
  (`KI-RO` / `KU-RO`). **INDEL pair** = length differs by one, edit-distance 1 (`KU-RO` / `RO`) —
  reported separately as *affixal*, never a true substitution.
- Each candidate records: the two forms; differing sign(s) + position; token frequency of each;
  documents, sites, chronology (context phase), support; source editions; damage status;
  segmentation note; internal + external (neighbour-word) context similarity; category tags +
  a single primary category; a chronological flag; a **non-phonological alternative explanation**;
  a source **dependency cluster** (all silver signs + word-division descend from the single
  **GORILA/Ventris** homomorphic lineage — nothing here is independently corroborated); a
  **substitution family** id (paradigm cluster); and an A/B/C/D **quality tier**.
- **Edition disagreements** are mined on a separate track: the independent **SigLA** palaeographic
  edition (Salgarella & Castellan; decoded from `database.js`) is aligned to GORILA/silver on the
  **575 shared documents**; single-locus reading differences are flagged.

## Headline counts

| | |
|---|---|
| substitution pairs (equal-length, 1-sign) | **2,794** |
| indel/affixal pairs (length ±1) | **955** |
| total word-pair candidates | **3,749** |
| edition-disagreement loci (GORILA vs SigLA, 575 shared docs) | **253** |
| alternation families (substitution components) | 73 (23 with ≥3 forms) |

## Counts per category

Primary category is **mutually exclusive** (priority: damage → allographic → scribal-correction →
same-document → same-formula → same-site → cross-site). Tag counts are **non-exclusive** (one
candidate can be same-document *and* same-site *and* chronological). Edition-disagreement and
chronological are reported on their own tracks (they cross-cut the spatial primaries).

| Category | primary (exclusive) | tag (non-exclusive) |
|---|---:|---:|
| same-document | 43 | 78 |
| possible scribal-correction | 25 | 28 |
| same-formula (shared neighbour-word slot) | 8 | 10 |
| same-site | 1,283 | 1,569 |
| cross-site | 1,856 | 2,180 |
| possible allographic-variation | 6 | 7 |
| damage-induced | 528 | 528 |
| **chronological** (disjoint dated phases) | — | 254 |
| **edition-disagreement** (separate SigLA track) | 253 | 253 |

The **cross-site** bucket dominates simply because, on a small corpus, most one-sign near-homographs
are two unrelated words attested at different places with **no shared context that licenses a
substitution** — exactly the multiple-testing trap (Invariant 8). They are retained but tiered low.

## Quality-tier distribution

Tier reflects usefulness as a *relative-structure* alternation candidate, **net of confounds**:

- **A** — substitution, ≥2 signs, both differing signs clean identified syllabograms, **both forms
  attested ≥2×**, a **controlled context** (same-document or same-formula), **no** damage/allograph
  confound.
- **B** — substitution, clean syllabograms, ≥1 form ≥2×, controlled or same-site, no confound.
- **C** — cross-site only, or hapax+hapax, or a differing sign is a logogram/ligature, or an
  allographic (orthographic) confound.
- **D** — damage-induced (`*NNN`/measure sign), edition-disagreement, or an indel with no context.

| Tier | word-pairs | + edition | total |
|---|---:|---:|---:|
| A | 7 | 0 | **7** |
| B | 459 | 0 | **459** |
| C | 1,927 | 12 | **1,939** |
| D | 1,356 | 241 | **1,597** |

By kind: **SUB** = A7 / B459 / C1,872 / D456; **INDEL** = C55 / D900 (indels never reach A/B — a
length change is affixation/segmentation, not substitution). 2,338 of 2,794 SUB pairs have both
differing signs = clean syllabograms.

Primary × tier (word-pairs):

| primary | A | B | C | D |
|---|---:|---:|---:|---:|
| same-document | 3 | 6 | 34 | 0 |
| scribal-correction | 4 | 3 | 18 | 0 |
| same-formula | 0 | 0 | 8 | 0 |
| same-site | 0 | 450 | 330 | 503 |
| cross-site | 0 | 0 | 1,531 | 325 |
| damage-induced | 0 | 0 | 0 | 528 |
| allographic | 0 | 0 | 6 | 0 |

## Tier-A candidates (all 7)

The strongest relative-alternation candidates — clean syllabic minimal pairs, both forms repeated,
sharing a document (many share the *same slot* of an administrative ledger):

| forms | freq | shared docs | primary |
|---|---|---|---|
| **KI-RO / KU-RO** | 16 / 37 | HT88, HT94b, HT117a, HT123+124a/b | scribal-correction |
| **KU-RO / KU-RE** | 37 / 2 | HT39 | scribal-correction |
| **KU-RO / KU-PA** | 37 / 4 | HT110a | scribal-correction |
| **TE-TU / TE-KI** | 3 / 2 | HT13 | scribal-correction |
| **SA-RO / KU-RO** | 4 / 37 | HT9a | same-document |
| **A-RA / A-PA** | 3 / 2 | ARKH1a | same-document |
| **SA-RA₂ / PU-RA₂** | 20 / 2 | HT28b | same-document |

`KU-RO` is the recurrent administrative "total" word; `KI-RO` its well-known ledger companion. That
the machine surfaces the ***-RO** ledger set as the top cluster is a sanity check, **not** a reading:
these are candidate contrasts of *unknown* value. (Note: because `KU-RO`/`KI-RO`/`KU-RE` differ by one
sign and co-occur, an editor's first explanation is **paradigmatic administrative vocabulary**, not a
phonological alternation — recorded in each record's `alternative_explanation`.)

## Alternation families (substitution paradigm clusters)

Connected components over substitution edges = the `substitution_family` per candidate.
**73 families; 23 with ≥3 forms.** The single largest component (**361 forms, 2,601 edges**) is a
**length-2 hairball**: on a small corpus nearly every 2-sign word links to another through a shared
sign, so *membership* in it is uninformative (the same near-completeness caveat as WP3.2). The
**informative** families are the smaller 3+-sign paradigms:

| family | size | example forms |
|---|---:|---|
| A-TA-* / *-TA-* / *-TA-RE | 20 | A-TA-NA, A-TA-RE, A-TA-DE, DA-TA-RA, DA-TA-RE, KA-TA-RE, PI-TA-RA |
| *-DA-* medial | 18 | SI-DA-RE, SI-DA-RO, SI-DA-TE, A-DA-RA, A-DA-RO, KI-DA-TA, MI-DA-RA, PA-DA-NI |
| **libation formula** A/JA-SA-SA-RA-ME | 4 | JA-SA-SA-RA-ME, A-SA-SA-RA-ME, JA-SA-SA-RA-MA, A-SA-SA-*802-ME |
| *4xx-VS transaction series | 8 | *403/404/406/408/409/410/411/417 + VS |
| A-RI-* / A-SE-* / A-SU-* | 8 | A-RI-JA, A-RI-PA, A-RI-SU, A-SE-JA, A-SU-JA, PA-SE-JA, NU-RI-JA |
| KU-PA-* | 5 | KU-PA-JA, KU-PA-RI, KU-PA-ZU, DI-PA-JA, TU-PA-RI |

The A/JA-SA-SA-RA-ME family is the recognised Minoan **libation formula** and its A-/JA- alternation
is the single most-cited Linear A variation — recovered here purely from one-sign contrasts.

## Allographic-variation candidates (all 7)

Differing signs are numbered/lettered variants of one base — an **orthographic**, not phonological,
alternation (dominant alternative explanation; capped at Tier C/D):

`SA-RA₂ / SA-RA`, `KU-PA₃ / KU-PA`, `A-PA / A-PA₃`, `PU-RA₂ / PU-RA`, `PU-RA₂ / PU₂-RA₂`,
`*312-TA / *312-TA₂`, and `*309-RI-JU / *309B-RI-JU` (same document TY2; also damage-flagged as
`*309` is an unidentified sign).

## Chronological candidates (254 tagged)

Forms whose attestations fall in **disjoint, time-ordered** phases (e.g. MMII vs LMIB). Almost all
are *also* cross-site or same-site with only 1–2 datable attestations each, so the chronological
signal is confounded with find-spot and hapax status. Example cluster: the `*-DI` family splits
`JA-DI` (MMII, Phaistos) against LMIB `-DI` forms (`MA-DI`, `RU-DI`, `DE-DI`, `SA-DI`) at Haghia
Triada — but each MMII form is a **hapax**, so this is a candidate to watch, not evidence.

## Edition-disagreement candidates (253 loci; 12 phonologically usable)

GORILA/silver vs the independent SigLA edition, single-locus, on 575 shared documents:

- **221** are *representational* (logogram vs A-code, or `*NNN` vs value) — excluded from any
  phonological use.
- **20** are allograph/star-series reading differences (`*21F`↔`*21M`, `*131B`↔`*131C`).
- **12** are **clean syllabogram-vs-syllabogram** disagreements — where the two best editions
  literally read a *different value-bearing sign* at the same spot:

| doc | GORILA | SigLA |
|---|---|---|
| HT6b | DA | DU |
| HT52a | KI | TU |
| HT88 | NI | SA |
| HT95b | ME | ZA |
| HT115a | JA | PA₃ |
| HT117a | JA | PA₃ |
| HT122a | TA | RI |
| HT128a | NU | PA₃ |
| HT154ja | TE | RE |
| HTWa1032 | RO | DA |
| KNZc7 | ZA | ZE |
| PHWa32 | RI | RA |

These are **editorial reading disagreements, not in-language alternations** — but they bound how much
of the apparent "substitution" signal is really palaeographic uncertainty.

## Dependency, non-circularity, and honest limits

- **Source dependency (Art. XI).** Every word-pair rides on **one lineage**: GORILA transliteration
  (sign identity) + GORILA word-division (segmentation), both descending from Ventris-1953 Linear B.
  No candidate is independently corroborated; SigLA (independent palaeography) is used **only** to
  *contradict* (edition track), never to confirm.
- **Non-phonetic (Art. V).** Signs are opaque tokens throughout. Nothing here reads, values, or
  transfers. The output is **relative structure** — which forms contrast in one slot in a shared
  context — at claim-layer **L2/L3**.
- **Multiple testing (Invariant 8).** 3,749 word-pairs from 984 types on a 3,147-unit corpus: the
  base rate of coincidental one-sign near-homography is high. The tiering exists to isolate the few
  (7 Tier-A, 459 Tier-B) pairs with a controlled context from the ~3,500 that are near-homograph
  noise. **No pair is asserted to be a phonological alternation.**
- **Segmentation-fragile.** All forms are whole GORILA word units; a different word division would
  dissolve or create pairs. The affixal/indel pairs are especially segmentation-dependent.

**Verdict: CANDIDATES_CATALOGUED.** A ranked, fully-attributed catalogue of one-sign contrasts with
non-phonological explanations for each — the raw material for a *later* relative-phonology test, not
a result. Guilty-until-proven-innocent: none of these is evidence of anything until a contrast
survives a held-out, non-GORILA-dependent check.
