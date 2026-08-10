# A machine-readable index of the Linear A entries in the CH/LA/LB rapport series, 1996-2021

Prepared by Kyriakos Papadopoulos (independent researcher, Netherlands; ORCID
0009-0003-0995-2518), 2026-08-10, and shared with Maurizio Del Freo at his request.
It extends the index of the Rapport 2016-2021 (built July 2026 from the open-access
Ariadne Supplement 5 edition) across the four earlier rapports which Dr. Del Freo
kindly provided in August 2026.

## Files

- `rapport_la_index_1996-2021.csv` — the index: **125 rows**, one row per entry/mention in
  the Linear A section of one rapport (so an object treated in several rapports appears in
  several rows — deliberately: the rows trace each item's reporting history).
- `index_counts.json` — machine-generated row counts (all counts quoted below come from it).

## Coverage

| rapport_window | source | LA section | rows |
|---|---|---|---|
| 1996-2000 | Olivier, *Pasiphae* III (2009) 187-197 | pp. 189-193 | 23 |
| 2001-2005 | Del Freo, *Colloquium Romanum* (Pasiphae I, 2008) 199-222 | pp. 202-213 | 36 |
| 2006-2010 | Del Freo, *Etudes myceniennes 2010* (Bibl. Pasiphae 10, 2012) 3-21 | pp. 7-15 | 18 |
| 2011-2015 | Del Freo, *Aegean Scripts* (Incunabula Graeca 105, 2017) I 3-29 | pp. 10-18 | 19 |
| 2016-2021 | Del Freo, *KO-RO-NO-WE-SA* (Ariadne Suppl. 5, 2024) 87-124 | pp. 96-108 | 29 |

## Columns

- **designation** — as the rapport gives it, including uncertainty markers `(?)`,
  renumbering arrows `(-> ...)`, and `(parenthesized)` labels for undesignated finds and
  for bookkeeping/negative-verdict entries (which are indexed too, for completeness).
- **description** — object, find data, and the readings *as reported in that rapport*
  (AB-numbering; editorial under-dots are described in words — "dotted" — rather than
  typeset; `[[ ]]` = erasure, `[` = break).
- **publication / year / pages** — the editio princeps or operative citation given by the
  rapport, plus the rapport's own printed page(s).
- **translit_printed_in_rapport** — yes / partial / no: whether the rapport itself prints a
  transliteration.
- **accessibility** — of the cited edition at the rapport's date: open / paywalled /
  pending_edition.
- **corpus_status** — a mechanical cross-reference against the digital research corpus we
  use (the 1,341-document dataset derived from the public lineara.xyz corpus, plus our
  small documented additions layer). `in corpus (as X)` gives the ID under which the item
  appears there when it differs from the rapport's designation. This column describes the
  *state of the public digital corpus*, never an editorial judgement of ours.
- **notes** — cross-links across rapport generations (announced -> published -> revised),
  numbering disputes, later corrections, and divergence flags.

## Conventions and caveats

- Diacritics are stripped throughout the CSV for encoding robustness (sign readings use
  GORILA/AB numeric codes, so nothing is lost where it matters).
- Only the Linear A sections (§2 of each rapport) are indexed, plus explicitly LA-relevant
  crossovers from the CH sections (e.g. the Samothrace noduli).
- The index is an independent working tool, not a critical edition; all errors are ours
  and corrections are very welcome. The rapports remain the authority for every entry.

## Observations that may be of interest (from the mechanical cross-reference)

1. **Thera:** the lineara.xyz-derived dataset carries the six Delta 18a tablet fragments
   under ad-hoc IDs; the cross-reference identifies `THEtab.4` = THE 7 (its numerals 7
   and 46 match the Boulotis 2008 face-a readings exactly) and `THEfr.1` = THE 10
   (isolated AB 67 — silver, SigLA and the rapport agree). The remaining pairings are
   witness-conflicted and left open (`THEfr.2/3` read A 302 as Boulotis suggests for
   THE 11/12, but SigLA reads A614 and AB22 there; `THEtab.5` vs THE 9 rests on
   elimination only). **THE 8 (the TELA+SE >= 200 fragment) is absent from that dataset**
   (SigLA does carry THE 7-12, including THE 8). The dataset's Zb-numbering is mixed: it
   follows the rapport for THE Zb 13 but the editors (Zb 15) for the Akrotiri lamp — and
   its lamp reading differs from the editio princeps (RE-SA 2 vs AB 09-A 332 2).
2. **Khania:** the digital corpus follows the rapport's numbering throughout (KH Zb 98,
   KH 99, KH 100 — not the ed.pr.'s KH Zb 1, 98, 99).
3. **Readings that later moved:** the digital corpus is impressively current in most
   places (it carries the 2008 Syme revisions including the AB 48 attestation on SY Za 4,
   the post-restoration PE Zb 7 reading AB 57-54-39, the 2015 Miletus renumbering, and the
   2015 Vrysinas re-readings), but it retains the superseded numeral 17 on KN Zb 27
   (autopsy 2012: 107) and the superseded AB 54 on KH Wc 2124 (ed.pr. 2018: variant of
   AB 61), and it still brackets KN Zb <27> as unlocated although the pithos was
   rediscovered.
4. **Site labels:** the digital corpus labels the whole Arkhanes series (ARKH 1-6, Zc 8,
   Zf 9) with the site "Arkhalkhori" (= Arkalochori), and places LACH Za 1 at "Larani";
   both appear to be data defects of the digital corpus, now documented on our side.
5. **Zominthos:** the digital corpus's `ZO1` (vase logogram + numeral 217) is *not* the
   2013 stepped libation table discussed in Rapport 2011-2015 (and judged masons' marks in
   Rapport 2016-2021) — a distinction easy to miss.
6. **Doubted items included:** the digital corpus includes, with committed readings, several
   items where the rapport series suspends judgement or objects (KN Ze 56, LACH Za 1,
   DRA Zg 1, IN Zb 1, the Phylakopi handle as MI Zb 3, the HM 767 gold disc as LA) — worth
   knowing when using it quantitatively.

## Method and reproducibility

The entries were extracted by close reading of the five rapports' LA sections; the
cross-reference column and all counts are computed mechanically by open scripts
(`build_deliverable.py`, `round2_scan.py`) in the public repository
<https://github.com/papadopouloskyriakos/logos> (directory
`experiments/crossscript_gate/phase3/sweep/`). The four pre-2016 rapport PDFs are *not*
in the repository and are not redistributed.

## Licence

The index itself (structure and annotations): CC BY 4.0, Kyriakos Papadopoulos 2026.
Bibliographic facts and brief quoted readings remain attributable to the rapports and
editiones principes cited in each row; nothing here substitutes for them.

Contact: kyriakos@papadopoulos.tech
