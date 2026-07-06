# MATERIAL REQUESTS

Precise, actionable requests for material that is paywalled, image-only, or requires a specialist
edition. **Non-blocked work continues** while these are pending. Priority: `BLOCKING` > `HIGH` >
`USEFUL` > `OPTIONAL`. Do not redistribute copyrighted full scans where licensing forbids; metadata,
derived factual records, transliterations, and checksums are stored as legally appropriate.

## RESOLUTION LOG (2026-07-06 — 7 PDFs supplied; see `bibliography/source_notes/2026-07-06_pdf_acquisition_audit.md`)
- **REQ-02 — SATISFIED.** Hoch, *Semitic Words in Egyptian Texts* (594 pp) → the Egyptian
  foreign-name/group-writing **calibration corpus**. RQ2/RQ3 pacing item cleared.
- **REQ-01 — SUBSTANTIALLY SATISFIED → BLOCKING downgraded to USEFUL.** Cline & Stannish 2011 (×2)
  reproduces the toponym group-writing transliterations (`kA-n-yw-SA`=Knossos, `i-m-n-y-SA`=Amnisos,
  `ry-kA-ti`=Lyktos) + IDs + LB comparanda + Edel/Görg caveats (bronze v2 records written). Full
  Edel & Görg 2005 apparatus still ideal (all variants; Siteia/Phaistos/Kydonia ovals) but no longer gating.
- **REQ-04 — still open (partial).** `Mari_and_the_Minoans.pdf` is a 1-page **image-only** scan
  (needs OCR; likely a fragment). Still need the actual ARM Kaptara texts.
- Set aside (not sources): 2× "The Map Is Not the Territory" (author's own essay), "Ο ΚΑΘΡΕΠΤΗΣ"
  (Greek, 75 pp).

---

### REQ-01 — Kom el-Hetan Aegean toponym list (primary edition) — `BLOCKING` (RQ2, E1–E3)
- **Source:** Edel, E. & Görg, M. (2005), *Die Ortsnamenlisten im nördlichen Säulenhof des
  Totentempels Amenophis' III.* (Harrassowitz). `SRC-KOMELHETAN-EDEL`.
- **Need:** the hieroglyphic spellings + editorial alternative readings for the securely-identified
  Aegean toponyms (Knossos, Amnisos, Lyktos, and the tentative Siteia/Phaistos/Kydonia), with the
  row/line numbers and any noted recarving.
- **Why:** these are the **frozen target set** for the toponym-anchor confirmatory test (E3); without
  the primary spellings + variants there is no defensible target list.
- **Acceptable form:** transcription/transliteration table (CSV/text) or scanned pages of the
  relevant list rows + apparatus; a photograph of the statue-base rows is also acceptable.
- **Fallback:** Cline & Stannish 2011 (`SRC-KOMELHETAN-CLINE`, open) gives identifications and
  caveats but **not** the full editorial apparatus — usable for a provisional target list flagged
  low-confidence, not for the confirmatory freeze.

### REQ-02 — Egyptian foreign-name calibration editions — `BLOCKING` (RQ2/RQ3, Section VII)
- **Source:** standard editions of 18th-Dynasty Egyptian renderings of **known** foreign names —
  e.g. the Semitic/Anatolian/Hurrian names in the Amarna-adjacent, topographical, and execration
  material; a corpus where the *external* form is independently known.
- **Need:** paired (Egyptian spelling ↔ independently-attested source-language form) records with
  date and scribal context, for **languages other than the Cretan targets**.
- **Why:** the Egyptian→foreign phonological-correspondence model **must** be estimated on this
  independent set and frozen before touching the Cretan anchors (else the model becomes the fishing
  rod — Section VII). This is the pacing item for RQ2/RQ3.
- **Acceptable form:** any machine-readable or scanned paired list (Hoch, *Semitic Words in Egyptian
  Texts*; the Amarna onomastica; topographical-list editions). A pointer to a suitable existing
  dataset is enough.
- **Fallback:** none that preserves independence; without it, E3/E4 stay `INCOMPLETE`.

### REQ-03 — EA5647 writing-board primary edition — `HIGH` (RQ3, E4)
- **Source:** the primary publication of BM `Y_EA5647` (hieratic + transliteration + editorial
  alternatives). BM catalogue metadata is already obtainable.
- **Need:** the hieratic name-forms, their transliterations, editorial variants, and the current
  scholarly view of each name's linguistic identity (Minoan vs Greek) and date.
- **Why:** the personal-name channel (E4) target set; also feeds `minoan_vs_greek_confidence`.
- **Acceptable form:** edition pages / transliteration table.
- **Fallback:** treat as exploratory-only (tier D) until the edition is in hand.

### REQ-04 — Mari (ARM) Kaptara texts — `HIGH` (RQ1/RQ5, E5)
- **Source:** the specific *Archives royales de Mari* texts attesting Kaptara — the tin-route
  text(s), the interpreter/targum payment, and Kaptarite-goods records (`SRC-MARI-ARM-KAPTARA`).
- **Need:** exact text IDs (ARM volume/number), transliteration, translation, and the commodity/role
  vocabulary in context.
- **Why:** builds the administrative trade/commodity ontology (E5), mapped against the LA schema.
- **Acceptable form:** CDLI exports or edition pages; a verified list of the relevant ARM numbers is
  a useful first step.
- **Fallback:** proceed with the ontology from secondary summaries, flagged provisional.

### REQ-05 — London Medical Papyrus Keftiu spells — `USEFUL` (RQ4, E6)
- **Source:** Leitz, *Magical and Medical Papyri of the New Kingdom* (HPBM VII) for BM `Y_EA10059`.
- **Need:** the two Keftiu-language spells in transliteration with editorial notes.
- **Why:** exploratory phonological-inventory constraints only.
- **Fallback:** skip; E6 is exploratory and non-gating.

### REQ-06 — aDNA supplementary tables — `USEFUL` (RQ6, E7)
- **Source:** Lazaridis et al. 2017 (`10.1038/nature23310`) + Skourtanioti et al. 2023 supplements.
- **Need:** per-sample date/site/ancestry-model tables (the supplements, which are usually open).
- **Why:** weak population-prior tiers only.
- **Fallback:** use published summary ancestry proportions; prior tiers are coarse regardless.

---

**Nothing here blocks Stages 0–2 scaffolding, the schema-derived slot audit, the Linear-B positive
control design, or the null framework.** The blockers (REQ-01, REQ-02) gate only the *confirmatory*
toponym test and its power analysis freeze.
