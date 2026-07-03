# Published-record checklist — merge notes (2026-07-03)

Merge of channel fragments in `fragments/` into `published_record_checklist.csv`.
Dedupe key = normalized designation (HTML-unescape; strip spaces/dots/backticks/angle-brackets;
uppercase; trailing `(?)` uncertainty markers and `(-> …)` reattribution arrows dropped;
parenthesized gap/unassigned designations keyed on their full string). Provenance rank on
collision: **delfreo-rapport > younger-pointer > sigla**; the losing row's publication, notes,
and divergent translit/accessibility values are folded into the winner's notes as
`[channel] …`; the `sources` column lists every channel that attested the item
(semicolon-separated).

## Merge statistics

| | count |
|---|---|
| Input rows — delfreo-rapport | 33 |
| Input rows — younger-pointer | 43 |
| Input rows — sigla | 225 |
| **Total input** | **301** |
| **Checklist rows out** | **294** |
| **Deduped (multi-channel merges)** | **7** (6 merged keys; PE 6 attested by all 3 channels) |

Multi-source rows: `PE 6` (all three channels), `KN Zg 57` (delfreo + younger, via same-object
alias), `(Zominthos libation table)` (delfreo + younger, via same-object alias), `SA We 4`
(delfreo + younger), `KH 96` (younger + sigla), `MY Zf 2` (younger + sigla).

Two **manual same-object aliases** were applied (evidence recorded in the merged rows' notes):

1. Younger's unnumbered **"KN Zh"** ivory sceptre (Kanta 2018 exh. cat. no. 280, D. 13.7 cm)
   = rapport's **KN Zg 57** (ivory ring, diam. ~13.7 cm, Kanta 2019 cat. 280, Anetaki plot).
   Designation-letter discrepancy (Zg vs Zh) unresolved until the Kanta et al. editio princeps
   appears.
2. Younger's **ZO Za 1** (3-tier stone libation table, Zominthos 2013, news reports)
   = rapport's **Zominthos libation table** (Sapouna-Sakellaraki 2013, Central Building
   Room 53). Open dispute: the rapport's verdict is masons' marks (NOT Linear A); Younger
   lists it as LA. Inventory item `ZO1` is possibly the same object — verify before treating
   as either a gap or a removal.

Deliberately **NOT merged** (side-level vs unsided IDs, kept as separate rows with
cross-references in notes): younger `KE 6` vs sigla `KE 6a`/`KE 6b`; younger `KH 93` vs sigla
`KH 93a`/`KH 93b`. Whether the unsided and sided IDs denote the same physical documents must
be verified against GORILA / the first editions — not assumed.

## Channel coverage statements (as returned by the channels)

### CHANNEL A (delfreo-rapport) — COMPLETE

Output CSV: `fragments/delfreo.csv` (33 rows, header exact per spec; committed + pushed, 6e6a627)

ACQUIRED (1 rapport):
- Rapport 2016-2021 (Del Freo), KO-RO-NO-WE-SA / Ariadne Suppl. 5, Rethymno 2024, pp. 87-124,
  DOI 10.26248/ariadne.vi.1843, CC BY-NC-SA from the journal's own OA platform (article 1843 of
  issue 178, same issue as the already-acquired Kanta et al. 1841). Archived:
  `corpus/bronze/delfreo_rapport_koronowesa/delfreo_rapport_2016-2021.pdf`, SHA-256
  404862427dd9faa01855ff6520b6c29da175a236a5dce2878ae7be2ca517deba, PROVENANCE.md alongside;
  entry appended to `docs/related/_acquisition.md`. Stated coverage: finds/editions 2016-2021
  plus older items resolved in that window; Linear A = its §2, pp. 96-108.

GAP-LISTED (4 rapports, one gap row each; none honestly OA):
- Rapport 2011-2015: Aegean Scripts (14th colloquium, Copenhagen 2015), Incunabula Graeca 105,
  CNR Edizioni, Rome 2017, vol. 1 (exact pages unverified). Access: print ~120 EUR via
  ispc.cnr.it order form; Academia.edu author copy is login-gated (403), no green-OA repository
  copy found despite CNR's 12-month-embargo policy.
- Rapport 2006-2010: Etudes myceniennes 2010 (13th colloquium), Bibl. di Pasiphae 10, Serra
  2012, pp. 3-21 (per BMCR 2013.01.36), ISBN 9788862274722, ~280 EUR. NOTE: the 13th colloquium
  was Sevres/Paris/Nanterre 2010, NOT Austin — Austin was the 11th (2000); correction recorded
  in the gap row.
- Rapport 2001-2005: Colloquium Romanum (12th, Rome 2006), Pasiphae 1-2, Serra 2008 (pages
  unverified). Cited repeatedly by the 2016-2021 rapport.
- Rapport 1991-1995: by J.-P. OLIVIER (pre-Del Freo), Floreat Studia Mycenaea (10th, Salzburg
  1995), Vienna 1999 (pages unverified). Rapport 1996-2000 (Austin 2000, 11th) is a further
  uncited hole of unclear publication status — flagged in that row's notes.

LA ITEMS EXTRACTED FROM THE 2016-2021 RAPPORT: 28 rows —
- 21 find/edition rows: KKH Zb 1; KN Zb 36a-d; KN Zg 57; KN Zg 58; Kommos frag (unassigned);
  KH Wc 2124; KH 102; KH 104; KH 105; KH Zc 106 (?); PK Za 27; PK Za 28; PE 6 (reclassified
  from PE <6>); Phaistos Hagia Photini frag (unassigned); Phaistos Chalara frag (unassigned);
  THE Zb 14; THE Zg 15 (?); THE Zg 16; VRY Zb 2 (?); VRY Zb 3 (?); VRY Za 4 (?)
- 3 re-reading/join/dispute rows: KH Wc 2123 (A 373 vs tripod-variant), PK Zb 25 (Hopkins
  re-reading), ZA 11 + ZA 13 new joins (2 rows, pending Petrakis)
- 1 REMOVAL candidate: PYR Zb 5 reattributed to Cretan Hieroglyphic as PYR Yb 01 (?)
  (Ferrara et al. 2016, endorsed by rapport)
- 2 attribution-ambiguity rows: KN S (4/4) 01 (Archanes formula, CH vs LA unresolved),
  SA We 4 (footnote-level LA attribution)
- 1 NEGATIVE verdict: Zominthos libation table judged masons' marks, not LA

Translit printed in rapport itself: yes=14, partial=4, no=10 (of item rows). Pending editio
princeps at rapport date: KN Zg 57/58, Kommos frag, Hagia Photini frag, THE Zg 16, ZA 11/13
joins — all flagged pending_edition (post-2021 appearance should be re-checked).

ID NORMALIZATION NOTES for diffing vs `corpus_inventory.csv` compact IDs: strip
spaces/parentheses -> KKHZb1, KNZb36a-d (inventory may still carry KNZb36/KNZb37 separately),
KNZg57, KNZg58, KHWc2123/2124, KH102/104/105, KHZc106, PKZb25, PKZa27/28, PE6 (may be PE<6> or
absent), THEZb14 (editors' numbering THE Zb 15 — collision risk), THEZg15/16, VRYZb2/3, VRYZa4,
ZA11, ZA13, PYRZb5 (removal), SAWe4 (site sigla SA = Samothrace; inventory may use SAM). Three
finds have NO designation (Kommos, Hagia Photini, Chalara) and cannot match any inventory ID.
Renumbering side-notes: KH Wc 1025 -> KH Wc 2125; possible anepigraphic KH Wc 2126.

### CHANNEL B (SigLA) — RESULT

SIGLA TOTALS
- SigLA exposes 802 Linear A documents ("There are 802 documents in the corpus." on the browse
  page), grouped into 22 site groups: Haghia Triada 372, Khania 220, Phaistos 64, Zakros 44,
  Knossos 37, Mallia 20, Arkhanes 10, Kea 7, Thera 7, Petras 3, Tylissos 3, Gournia 2 +
  "GOURNIA" 2 (site-label quirk, same site), Palaiokastro 2, Pyrgos 2, and 1 each for Haghios
  Stephanos, Kythera, Melos, Mycenae, Papoura, Psykhro, Syme.

DIFF vs corpus_inventory.csv (1,341 rows; normalization = HTML-unescape, strip
spaces/dots/backticks/angle-brackets, case-insensitive)
- Exact-matched: 577 / 802
- Side/face-level gaps: 78 — SigLA sides/faces of documents the inventory DOES hold under a
  base or sibling ID (e.g. HT 41b vs inventory HT41a; HT Wa 1019α/γ vs HTWa1019;
  HT Wc 3004a/b vs HTWc3004; KN Za 10a/b vs KNZa10; GO 2a/b vs GO2r/GO2v recto-verso naming).
  Likely inventory omits sides with no parsed signs — flagged as ambiguity, not assumed.
- Wholly absent: 147 — no match under any side/base normalization. Big clusters:
  KH Wc 2026–2113 roundels (~40), HT Wa 1623–1854 hanging nodules (~30), KH page tablets
  42–97 (16), Phaistos tablets/Wb/Wc (17), HT Wc/Zd stragglers, THE 7–12 (Thera, added to
  SigLA 2026-06-26), KE 6a/b + KE Wc 2a/b, PE 6, PYR 2, MY Zf 2, MA 9, ARKH 7, HT 123a/b,
  HT 142, ZA 25/30/33, KN Wc <24a/24b/25>, KN Zg <21> (angle-bracketed = lost/older-
  documentation items).
- Total gap rows written: 225 (78 side-level + 147 absent, distinguished in notes) →
  `fragments/sigla.csv` (channel='sigla'; publication='SigLA database entry' — sampled
  document pages show "Link to corpus: —", no external citation; translit_printed='partial'
  except the two spot-verified pages, since SigLA stores sign-by-sign editorial transcriptions
  but per-document pages were not bulk-fetched).

SIGLA'S STATED BASIS & TERMS (about.html changelog)
- Basis: GORILA (Godart & Olivier) — "all tablets from GORILA are now present in SigLA"
  (2021-08-24); post-GORILA additions 2026-05-21 (HT Zb 161, KN Za 10(a/b), KN Za 17,
  KN Za 18) and 2026-06-26 (PE 1, PE 2, PK 1, GO 2, KE 6, KH 93, KH 101–105, KN 49, KN 54,
  PH 54, THE 7–12). Aim self-described as "systematic, exhaustive... open access database of
  all Linear A inscriptions" — but the 802 count vs GORILA's ~1,400+ items means
  W-series/minor pieces are still being added; do NOT read SigLA absence as non-existence.
- Terms: dataset and drawings CC BY-NC-SA 4.0 (© 2020– Ester Salgarella & Simon Castellan).

ARCHIVE
- `corpus/bronze/sigla_browse_2026/` (gitignored): landing.html, about.html, browse.html
  (SHA-256 c1d25f91dccf334c3cf24b52c1e4a279970cebd3f5c6f377569de076360170cd), database.js,
  2 sample doc pages, doc_list_extracted.json, PROVENANCE.md, SHA256SUMS. Entry appended to
  `docs/related/_acquisition.md`. Committed+pushed (7c32c79).

CAVEATS
- 24 of the "wholly absent" carry inventory-side suffix mismatches (e.g. HT 123a/b, KH 93a/b,
  PH 17a/b) — they may exist in source layers under unsided IDs that were dropped when no
  signs parsed; each row's notes say to verify against GORILA before treating as a true gap.
- database.js is an encoded binary blob; SigLA counts here come from the server-rendered
  browse.html, not from parsing it.

### CHANNEL C (younger-pointer) — COMPLETE

- Post-GORILA pointers found in Younger: 149 (items flagged by non-GORILA primary citation,
  "not in GORILA"/"NO GORILA", Del Freo & Zurbach 2011 supplement listing, or unpublished
  status, across misctexts/HTtexts/religioustexts/main/lexicon pages)
- Already in inventory (skipped): 106 — includes 6 sigla-normalization matches that a naive
  string diff would miss: HAR Zb 1 = TELZb1 (Tel Haror), SA Wa 1 = SAMWa1, POR Zc 1 = POZc1
  (orig. PO Zg 1), KY Zc 2 = KY Za 2, GO 2 = GO2r/GO2v, PE Zc = PEZc4
- New rows written: 43 → `fragments/younger.csv` (channel='younger-pointer', exact column
  schema as specified)
- Notable among the 43: KN Zh ivory "sceptre" (Kanta 2018 cat.; Kadmos edition announced for
  2023 — merged with KN Zg 57 in this checklist, see aliases above).
- *(NOTE: the channel's return statement was truncated in transmission after "Kanta 2018 cat.;
  Kad…"; the counts above are verbatim, the remainder of its coverage claims is reconstructed
  from `fragments/younger.csv` itself: 43 rows spanning Arkhanes, Armenoi, Gournia, Haghia
  Triada, Kastelli, Kea, Khania, Knossos, Malia, Mochlos, Mycenae, Petras, Petsophas,
  Phaistos, Palaikastro, Pseira, Samothrace, Thera, Zakros, Zominthos; 9 pending_edition
  unpublished pointers; several rows flagged AMBIGUOUS where Younger's citation practice
  leaves GORILA coverage unclear — MY Zf 2, HT Zf 166/167, KN Zb unnumbered = Brice KN Z 36,
  KH Wn 1501-1557 range, ZO Za 1.)*

## Cross-channel ambiguities (do not assume completeness)

- **Side/face vs document identity**: 78 sigla rows are sides/faces of inventoried documents;
  the inventory appears to omit sides with no parsed signs, but this was verified nowhere —
  each row says to check GORILA.
- **Unsided vs sided ID pairs across channels**: KE 6 (younger) vs KE 6a/b (sigla); KH 93
  (younger) vs KH 93a/b (sigla). Kept as separate rows.
- **Script-attribution disputes** carried as rows, not resolved: PYR Zb 5 (→ CH PYR Yb 01,
  removal candidate), KN S (4/4) 01 (Archanes formula CH vs LA), KN Zb 36a-d (LA vs Linear B),
  VRY Zb 3 (LA vs CH), KH Zc 106, SA We 4/Wc 1/Wc 2, Zominthos table (masons' marks per
  rapport vs LA per Younger), ARM Zg 1 (likely not an inscription at all).
- **Numbering collisions**: THE Zb 14 (rapport) vs THE Zb 15 (editors) — one object, two
  numbers; KN Zg 58 designation used both for the Anetaki ivory bar (rapport) and, via CMS
  II 3 no. 23, tangled with Younger's unnumbered Little Palace steatite seal (reclassified
  Hieroglyphic by Younger) — flagged in that row.
- **Undesignated finds** (cannot match any inventory ID): Kommos vase frag 2019, Phaistos
  Hagia Photini frag 2017, Phaistos Chalara frag 2017.
- **SigLA absence ≠ non-existence** (still adding W-series), and **Younger's citation
  practice ≠ proof of GORILA absence** (verify HT Zf 166/167, MY Zf 2 against GORILA IV).

## Rapport-period coverage map (finds/editions by report window)

| Window | Rapport | Status |
|---|---|---|
| ≤1985 | — (GORILA I–V era, 1976–1985) | Base corpus; covered via GORILA/SigLA channel, not the rapport series |
| 1986–1990 | Olivier (Mykenaïka, 11th? colloquium era) | **UNASSESSED** — not cited by the 2016-2021 rapport and not searched by any channel; existence/venue unverified |
| 1991–1995 | Olivier, Floreat Studia Mycenaea (Vienna 1999) | **GAP** (paywalled print; gap row in checklist) |
| 1996–2000 | unknown (11th colloquium, Austin 2000) | **HOLE of unclear status** — uncited by the 2016-2021 rapport; publication status unverified; flagged inside the 1991-1995 gap row |
| 2001–2005 | Del Freo, Colloquium Romanum (Pasiphae 1-2, 2008) | **GAP** (paywalled print; gap row) |
| 2006–2010 | Del Freo, Etudes myceniennes 2010 (Bibl. Pasiphae 10, 2012), pp. 3-21 | **GAP** (paywalled print ~280 EUR; gap row) |
| 2011–2015 | Del Freo, Aegean Scripts (Incunabula Graeca 105, 2017) | **GAP** (paywalled print ~120 EUR; no honest OA copy found; gap row) |
| 2016–2021 | Del Freo, KO-RO-NO-WE-SA (Ariadne Suppl. 5, 2024), pp. 87-124 | **ACQUIRED** (OA, CC BY-NC-SA; archived in corpus/bronze) |
| 2022– | none yet | Post-rapport window: covered only piecemeal (SigLA 2026 additions, Younger's 2023-state pages, pending_edition flags); next rapport not yet published as far as the channels could see |

Bottom line: of the six rapport windows 1991–2021, exactly **one (2016–2021) is acquired**;
four are honest paywalled gaps with exact citations; 1996–2000 is a hole of unclear
publication status; 1986–1990 was never assessed. Coverage claims for those windows in this
checklist therefore rest on secondary attestation (Younger, SigLA, DF&Z 2011 pointers), not
on the primary rapports.
