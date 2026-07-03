# Literature acquisition list (from the 2026-06-30 audit)

Tracks what logos holds, what is open-access (pull directly), and what is paywalled / operator-supplied.
Drafting (Track 1) does **not** start until the two P-BLOCK items are ingested + summarized (Braović:
done; Salgarella 2025 body: pending operator). "Confirm URL" = open-access likely but not yet verified.

## In hand (audited 2026-06-30)
- **Salgarella 2020** *Aegean Linear Script(s): Rethinking the Relationship between Linear A
  and Linear B* (CUP; DOI 10.1017/9781108783477; ISBN 978-1-108-47938-7 Hardback) — ✅
  **ACQUIRED 2026-07-03** (operator's Cambridge Core personal download; complete per-chapter
  PDFs with text layers; zip SHA-256 `256c70c8f16ae09f8a77119e6e0f05f0cf2bfef981e21b081ce3ab9a0dbd9856`)
  → `corpus/bronze/salgarella_2020/` (gitignored, non-redistributable; PROVENANCE.md +
  SHA256SUMS alongside). THE standing acquisition item — now closed. Settles: homomorphy
  grades (anchors.csv), the historiography AUDIT's Salgarella rows, her A↔B taxonomy
  (docs/related/salgarella-2020-taxonomy.md).
- **Kanta, Nakassis, Palaima & Perna 2024** "An archaeological and epigraphical overview…
  (Anetaki plot)", *KO-RO-NO-WE-SA* (Ariadne Suppl. 5), 27–43 — ✅ **ACQUIRED 2026-07-03**, OA
  (CC BY-NC-SA 4.0), DOI 10.26248/ariadne.vi.1841 →
  `corpus/bronze/kanta_etal_2024_anetaki/kanta_etal_2024_anetaki.pdf` (gitignored; 3,104,974 B,
  SHA-256 `87dad27b79ee3ef4539b844d7ed30a0069ac14acdd2ff75eed160f9baadf57d2`; PROVENANCE.md
  alongside). KN Zg 57 (ivory Ring, ~119 signs, longest known LA inscription) + KN Zg 58
  (handle, accounting + six-fraction sequence). **Prints NO transliterated sequences** — full
  edition = Kanta (ed.) forthcoming, *Anetaki II* (THE standing supply acquisition for any
  Phase-3). Extraction: `experiments/crossscript_gate/phase3/anetaki_extraction.md`.
- **Rjabchikov 2025** "The Decipherment of two Records of Linear A on the Ivory Mirror from
  Knossos, Crete", in *Tendentsii i problemy razvitiya sovremennoy nauki* (IV conf.,
  Petrozavodsk 2025-08-18), MTsNP "Novaya Nauka", pp. 100–106 — ✅ **ACQUIRED 2026-07-03** as
  a **REGISTRY OBJECT (fringe), never evidence**: full proceedings volume from the
  publisher's own open archive
  <https://sciencen.org/assets/Kontent/Konferencii/Arhiv-konferencij/KOF-1370.pdf> →
  `corpus/bronze/rjabchikov_2025_sceptre/KOF-1370_novaya_nauka_2025_proceedings.pdf`
  (gitignored; 2,001,176 B, SHA-256
  `b4ce36798ad0271c86509a2c8ff54cefe52194131f0a51ee2fd2e06864c40437`; PROVENANCE.md
  alongside, plus the Wayback copy of his Academia.edu record, SHA-256
  `f733c2e607ebb416d112ac18e0a8418ef449eaee1aa98a8eb0b4a2ab4930067a`). Fringe
  "decipherment" of the Anetaki sceptre **KN Zg 57/58 from photographs, before any official
  transliteration**; all 15 printed readings quarantined in `litindex.py`
  (`fringe_sceptre_reading`); registry entry in `linear-a-claims-2026.md` (fringe_flag=true).
- **Chiapello 2024** "Deductions on an unknown find surrounded by mystery: the Linear A
  inscribed ivory circle found at Knossos", self-posted Academia.edu 2024-02-07
  (<https://www.academia.edu/114586901/>) — ✅ **PAGE ARCHIVED 2026-07-03** as a **REGISTRY
  OBJECT (pre-publication prediction)**: the public page (author + date + abstract with the
  two hypotheses: greater A/B similarity than assumed; reappraisal of a Greek reading of
  Linear A) via Wayback snapshot 20260703173735 →
  `corpus/bronze/prepub_prediction_2024_ivory_circle/academia_page_wayback_20260703.html`
  (gitignored; 199,054 B, SHA-256
  `e52e31f9be01290d241f837e9acace8ce9048a61322f1bff242f255503cf92b5`; PROVENANCE.md
  alongside). **GAP: the PDF is Academia.edu login-gated and was NOT acquired** (no mirrors
  used; operator with an account can supply it). Registry entry in
  `linear-a-claims-2026.md` (prediction only, no fringe judgment); scorable when
  *Anetaki II* lands.
- **Braović, Krstinić, Štula & Ivanda 2024**, *Comput. Linguistics* 50(2):725–779 — `docs/related/braovic-2024.md`. Open: <https://aclanthology.org/2024.cl-2.7.pdf>.
- **Salgarella 2025** *Writing in Bronze Age Crete* — **BODY ACQUIRED + ANALYZED 2026-07-01** (operator supplied the purchased EPUB; §7/§8 verified). No longer blocking. `docs/related/salgarella-2025.md`.
- **Salgarella & Judson 2024** "Signs of the times?" (KO-RO-NO-WE-SA pp. 359–379) — drove `prereg-morphology-stratification-addendum-2026-06-30.md`.
- **Salgarella, Bellinato & Ferrara 2025** "On Aegean spices," *Kadmos* 64(1/2):29–44 — folded into `litindex.py` (quarantined L_known) + `linear-a-claims-2026.md`.
- **Dickinson review of Steele 2024** (JGA) — pp. 473–474. **No `*301` content** (it is a book review; neutral on the dwell-vs-give crux). Need the **JGA volume/issue/year** before any citation.
- **Davis 2013** (*Kadmos* 52:35–52) — the `*301`="give" / VSO PRIMARY source (audited 2026-07-01); resolves the "still needed: primary Davis text with the `ta-na-i-*301-u-ti-nu` parallel + pages." The "give" gloss is Duhoux's (1992).
- **Salgarella 2019** (*Kadmos* 58:61–92) — palaeography; resolves the hand-stratum question (#19). This IS the site/deposit material the list had pending under "Salgarella 2020 forthcoming."
- **Corazza et al. 2021** (*JAS* 125:105214) + **Schrijver 2014** (*Kadmos* 53:1–44) — the two independent Direction-D fraction systems (audited 2026-07-01).
- **Ferrara, Montecchi & Valério**, "Archanes Formula" — cross-script / `a-sa-sa-ra-me` continuity (refuted).
- **SigLA browse snapshot** (sigla.phis.me, Salgarella & Castellan, dataset+drawings CC
  BY-NC-SA 4.0) — ✅ **ACQUIRED 2026-07-03** (Channel B of the corpus-completeness audit;
  landing + about + browse list "802 documents" + site `database.js` + 2 sample document
  pages only — no bulk per-document scraping) → `corpus/bronze/sigla_browse_2026/`
  (gitignored; PROVENANCE.md + SHA256SUMS alongside; browse.html SHA-256
  `c1d25f91dccf334c3cf24b52c1e4a279970cebd3f5c6f377569de076360170cd`). Stated basis: GORILA
  complete (2021-08-24 changelog) + post-GORILA additions 2026-05-21 (HT Zb 161, KN Za
  10(a/b)/17/18) and 2026-06-26 (PE 1–2, PK 1, GO 2, KE 6, KH 93, KH 101–105, KN 49/54,
  PH 54, THE 7–12). Diff vs `corpus_inventory.csv` (1,341): 577 exact-matched, 78
  side/face-level gaps, 147 wholly absent →
  `experiments/crossscript_gate/phase3/sweep/fragments/sigla.csv` (225 rows).

## Open-access — pull directly (URLs verified 2026-06-30 unless marked *confirm*)
- **Salgarella 2022** "Mix and match: a combinatory (re-)classification of Linear A signs," *TALANTA*
  54:31–52 — **OA accepted version, CC BY-NC-ND**, Cambridge repository:
  PDF <https://www.repository.cam.ac.uk/bitstreams/70a9babb-6286-4a27-a52f-44f2f04bd389/download> ·
  record <https://www.repository.cam.ac.uk/items/d1c8c2dd-ee5b-4e61-9524-2c0eb5280eff>. ✅ verified.
- **Loh & Perono Cacciafoco 2020** "A new approach to the decipherment of Linear A, stage 2 … a 'brute
  force attack'," *Grapholinguistics in the 21st Century 2020* (Fluxus), pp. 927–943, DOI
  10.36824/2020-graf-cacc — **OA PDF** <https://www.fluxus-editions.fr/gla5-cacc.pdf>. ✅ verified.
  **Citation note:** Braović cites this as "Colin & Cacciafoco 2020" — that mis-reads the first name
  *Colin* (Colin Jia Sheng Loh) as a surname. Correct form: **Loh, C. J. S. & Perono Cacciafoco, F.**
  Use the correct form in the draft and flag the survey's slip.
- **Daggumati & Revesz 2023**, *Information* (MDPI, OA) — cross-script CNN visual prior art. The audit's
  "14(4):227" may be one of two Revesz papers; cf. "Convolutional Neural Networks … Three Possible
  Sources of Bronze Age Writings between Greece and India" (ResearchGate 369916621). MDPI is OA:
  <https://www.mdpi.com/2078-2489/14/4/227> *(confirm exact article)*.
- **Steele & Meissner 2017** "From Linear B to Linear A: the problem of the backward projection of
  sound values" (in *Understanding Relations Between Scripts*, pp. 93–110) — ✅ **ACQUIRED 2026-07-03**:
  authors' own CREWS self-archive (Oxbow offprint licence permits web posting after the 3-year embargo,
  July 2020 — stated on the offprint's own licence page):
  <https://crewsproject.wordpress.com/wp-content/uploads/2020/07/chapter-6.pdf> →
  `corpus/bronze/steele_meissner_2017/chapter-6.pdf` (gitignored, not redistributed; 978,536 bytes,
  SHA-256 `a80810e419eae8492e63ed7971e9e65d9f78d3506770a750b9e467f126d34553`; PROVENANCE.md alongside).
  Settles: Table 6.2 Cypriot-stable eleven (p. 98), si "good contender" (p. 98), Table 6.4 place-name
  equations (p. 102), §5 internal-variation series (p. 103), tier grids Tables 6.5/6.6/6.11
  (pp. 102/104/108). Consumed by `experiments/crossscript_gate/steele_meissner_2017.py`.
  (The earlier note — Cambridge repository record all-rights-reserved; companion OA chapter Meißner &
  Steele "Structural and Contextual Concerns" — remains true but is superseded for acquisition purposes.)
- **Younger, John G. — "Linear A Texts & Inscriptions in phonetic transcription" website** —
  ✅ **ACQUIRED 2026-07-03** (archive.org; the KU host `people.ku.edu` was decommissioned early
  2024 and no longer resolves; Younger's successor home is Academia.edu, but there the material
  is reorganized as login-gated PDFs, so the latest Wayback snapshots of the canonical KU pages
  were archived instead — raw `id_` captures). Main page (incl. §10c Place Names; Younger's
  last update 2023-07-03): snapshot 20231222205430 of `people.ku.edu/~jyounger/LinearA/`,
  SHA-256 `4fc646614a37909fe7d50844fa76d4b0c9dc3eec0792c8fabcc069527715ada4`; Lexicon (last
  update 2023-08-07): snapshot 20231203062200 of `…/LinearA/lexicon.html`, SHA-256
  `463778cc7d7262a57adab53c75c33261554af9be69a70a1857bf34079e6c5b94` →
  `corpus/bronze/younger_lineara/` (gitignored, not redistributed; PROVENANCE.md alongside).
  Authorship stated on-page (jyounger@ku.edu). Settles: Younger's place-name identifications
  (PA-I-TO = Phaistos, SU-KI-RI-TA = Sybrita, TU-RI-SA/TU-RU-SA = Tylissos, DI-KI-TE = Mt
  Dikte, SE-TO-I-JA = Archanes?/Ioukhtas?, KU-*79-NI perhaps ku-do-ni-ja, I-DA = Ida?,
  I-TI-NI-SA = Itanos, DA-U-*49 =? da-wo, KU-NI-SU place not "grain", SA-RA2 = Ayia Triada?,
  WI-NA-DU listed only as a name in a list at KH 5.3, not identified as a toponym).
- **Min Eu, Xu & Cacciafoco 2019** — Linear A vs lexical lists *(confirm venue + OA)*.
- **KO-RO-NO-WE-SA proceedings** (Ariadne Suppl. 5) — University of Crete repository may host the OA
  volume *(confirm; the Salgarella & Judson chapter is already in hand)*.
- **Del Freo 2024** "Rapport 2016-2021 sur les textes en écriture hiéroglyphique crétoise, en
  linéaire A et en linéaire B", in Bennet, Karnava & Meißner (eds), *KO-RO-NO-WE-SA* (Ariadne
  Suppl. 5), Rethymno 2024, pp. 87-124, DOI 10.26248/ariadne.vi.1843 — ✅ **ACQUIRED 2026-07-03**
  from the journal's own OA platform (CC BY-NC-SA 4.0):
  <https://ejournals.lib.uoc.gr/Ariadne/article/download/1843/1753> →
  `corpus/bronze/delfreo_rapport_koronowesa/delfreo_rapport_2016-2021.pdf` (gitignored, not
  redistributed; 869,596 bytes, SHA-256
  `404862427dd9faa01855ff6520b6c29da175a236a5dce2878ae7be2ca517deba`; PROVENANCE.md alongside).
  The backbone find-report for LA finds 2016-2021 (§2, pp. 96-108); feeds
  `experiments/crossscript_gate/phase3/sweep/fragments/delfreo.csv`. **Predecessor rapports NOT
  OA** (gap rows in the fragment): Rapport 2011-2015 in *Aegean Scripts* (Incunabula Graeca 105,
  CNR Edizioni 2017, print 120€; author copy on Academia is login-gated); Rapport 2006-2010 in
  *Études mycéniennes 2010* (Bibl. di Pasiphae 10, Serra 2012, pp. 3-21, €280); Rapport 2001-2005
  in *Colloquium Romanum* (Pasiphae 1-2, Serra 2008); Rapport 1991-1995 (Olivier) in *Floreat
  Studia Mycenaea* (Vienna 1999).

## Paywalled / print — operator supplies
- **Salgarella 2025 body** (esp. §7 reading p.35–45, §8 language p.46–53; §4 palaeography p.17–21) + the online appendix (<https://www.cambridge.org/salgarella>). **BLOCKING for any 2nd morphology run.**
- **Salgarella 2019** "Drawing lines," *Kadmos* 58:61–92 (de Gruyter) — synchronic variation.
- **Schoep 2002** *The administration of neopalatial Crete*, Minos suppl. 17 — the Semitic/Lycian best-founded ranking + 7,362–7,396 sign count.
- **Ferrara & Tamburini 2022** "Advanced techniques…," *Lingue e Linguaggio* 2/2022:239–259 (il Mulino) — the only comparable prior review; cite or be desk-rejected.
- **Fuls 2015** "Classifying undeciphered writing systems," *Hist. Sprachforschung* 128(1):42–58 — the 3.3-sign word-length figure (reconcile against the Direction-A premise).
- **Daggumati & Revesz 2019** (DASFAA/DEXA, Springer) — earlier cross-script CNN paper.
- **Judson 2020** *The Undeciphered Signs of Linear B* (CUP) — LB scribal-practice framing + *127/*157 inventory.
- **Sacconi 1972** "The monogram KAPO," *Kadmos* 11(1):22–26 (de Gruyter) + **Foster 1974** (Duke diss.) — the KA+PO=cinnamon/fenugreek origins.
- **Davis 2013** "Syntax in Linear A," *Kadmos* 52 + **Davis 2014** *Minoan Stone Vessels*, Aegaeum 36 — the primary i-`*301`="give"/V-S-O source (quote the `ta-na-i-*301-u-ti-nu` parallel with page numbers).
- **Duhoux** libation-formula analyses — primary source for the formula segmentation / verb slot.
- **Steele 2024** *Exploring Writing Systems and Practices in the LBA Aegean* (Oxbow/CREWS) — only if a sign/formula-level structural claim is wanted (the review notes the book has no index).
