# EPOCH-001 — Anetaki source acquisition: the contradiction was verbal, the corpus supply is real but sequence-free

**Verdict: `RESOLVED_PUBLISHED_PARTIAL`** · plan_hash `357337e5…70db` · 2026-07-08 ·
Constitution v2.2 · claim layer L0/L1 (supply only) · `SEAL_SCOREABLE_CONTENT_ACQUIRED=false`

## 1. The precise resolution

The anchor-lattice K finding ("published, not in silver") and the J1/M finding ("no
transliteration public") were **both correct on different axes**:

- **Published:** Kanta, Nakassis, Palaima & Perna, in *KO-RO-NO-WE-SA* (Ariadne Suppl. 5),
  Rethymno **2024**, pp. 27–43, DOI 10.26248/ariadne.vi.1841, CC BY-NC-SA 4.0 — already on
  disk since 2026-07-03. The "Ariadne Supplements **2025**" dating in the K note is the
  March–April 2025 online/media wave of the same edition; **no separate 2025 publication
  exists** (Ariadne issue-178 TOC read in full: no other Anetaki article).
- **No transliteration:** verified directly against the PDF this epoch — the article
  prints **zero transliterated sign sequences**. All sequence content (6 Face-B groups,
  ≥9 Face-C groups, the Face-β 4-sign sequence, the ≥16 Face-A metope signs, the 6
  fraction-sign identities: ~119 signs total) is deferred to **Kanta (ed.), *Anetaki II***
  — INSTAP Academic Press, **still unpublished as of 2026-07-08** (instappress.org checked;
  no Kadmos edition ever appeared; no Zenodo/arXiv/academia preprint).
- **"Not in silver" was imprecise:** silver already carries **KNZg57a** — a 5-token
  preliminary reading (*401+RU, *401+RU, *418+L2, NI, VAS + lacunae) inherited from
  lineara.xyz with **no identifiable published source** (recorded at confidence ≤ 0.5).
  It coheres with the editors' prose (vas+RU ligature; rhyton A664 ↔ *418+L2 alias,
  mechanically supported via PH8a.3).

## 2. Carrier identities (task list corrected)

| id | object | status |
|---|---|---|
| KN Zg 57 | ivory Ring, ~119 signs (with 58) | preliminary overview published; ed.pr. forthcoming; partial 5-token preliminary reading in silver |
| KN Zg 58 | ivory bar/handle (accounting face δ with 6-fraction sequence) | same; **numbering collision** with Younger's old steatite "KN Zg 58" (HM 843, Hieroglyphic) recorded |
| KN Zg 55 | steatite disk seal, JA-SA-JA | in silver; **chance find, NOT from the Anetaki deposit** |
| KN Zg 56 | — | **NOT_ESTABLISHED anywhere** (GORILA holdings, Younger, Del Freo rapport, Civitillo 2024, 14 search routes): the task's "55, 56, 57, 58" enumeration is unsupported for 56 |

## 3. What was acquired (all quarantined under `data/anetaki_2025/`, silver untouched)

- `editions.json` — 7 deduplicated editions/witnesses with licensing + accessibility
  (1 scholarly edition with epigraphic content; 1 numbering authority; 1 unpublished
  ed.pr. = SOURCE_BLOCKED; 1 unsourced preliminary; 1 fringe + 1 prediction registry
  object; media echoes).
- `sign_candidates.json` — **40 machine-readable rows**, each row page-cited with witness +
  confidence: 35 editor-grade/placeholder rows (Kanta et al. 2024), 1 preliminary
  (KNZg57a), 3 fringe-quarantined (Rjabchikov photo-readings), 1 prediction-registry
  (Chiapello). Negative control: **0 fringe leaks** into evidence rows (mechanical).
- `CONTAMINATION_BOUNDARY.md` — both frozen seals (`ANETAKI_FINAL_EDITION_DELTA_SEAL`,
  `M_ANETAKI_LATTICE_DELTA_SEAL`) remain **SEALED_PROSPECTIVE and uncontaminated**: this
  epoch touched only material the seals pre-declared J1-public/excluded; their scoring
  targets (the transliterations) remain 100 % unobserved. Trigger protocol restated.

## 4. Genuinely-new information vs silver (mechanical, `scripts/anetaki_delta.py`)

- **+2 countable new-to-LA sign types**: Cretan Hieroglyphic **\*180** and **\*181** used
  in a Linear A text (handle face α) — absent from the silver sign universe.
- **+1 probable NEW Linear A sign** (face α) — shape unpublished, not countable yet.
- A664 (rhyton) = **UNCERTAIN_ALIAS** of silver's *418+L2 (present in PH8a.3 AND KNZg57a).
- New *301 contexts: **0**. Verifiable new A-only occurrences: **0**. New formula slots:
  **0**. New transliterated sequences: **0**.
- Held-out inventory awaiting *Anetaki II*: 6 + ≥9 + 4 sign-groups, ≥16 metope signs,
  6 fraction identities — the campaign's single best future test bed (numeral-free ritual
  genre + accounting handle from a NEW genre/site context for the L2/L3 positives).

## 5. Controls and receipts

- **Positive control:** 15/15 phase3-extraction load-bearing items reproduced from the
  PDF (4 initial regex fails were hyphenation/case artifacts, each verified verbatim).
- **Search receipt (Art. VII):** 14 routes, all logged in `result.json`, negatives
  included. Notable honest negative: the search-engine-synthesized citation
  "Kanta, Nakassis, Palaima, Perna **and Weingarten**, 'Two Linear A Inscriptions on
  Ivory…'" could NOT be verified on any fetched primary page (Nakassis CV lists only the
  2024 article) — recorded as an UNVERIFIED possible ed.pr. title, not evidence.
- SigLA re-checked: no Zg 57/58 (802 docs unchanged).

## 6. What this buys the campaign

Zero value-bearing bits (as the K epoch predicted: 0-anchor row). The commodity acquired
is **held-out test power** — now machine-readable, quarantined, and with a written
contamination boundary so it stays spendable. The only lever that changes anything is the
*Anetaki II* publication event; everything needed to score it mechanically on day one is
now in place.
