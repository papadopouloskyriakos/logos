# Audit of `0202.zip` — 3 delivered PDFs (2026-07-06)

User-delivered `0202.zip` (sha `af4b1fc15ee6ce18`, 3 PDFs). Question posed: *"are these related?
please audit them extensively."* Audited by workflow `wf_5a8719de-1c0` (4 agents, 0 errors):
one relevance-audit per PDF + a synthesis, each judged against the logos Egyptian external-anchor
needs (REQ-01 Aegean-list primary edition; REQ-02 Egyptian→foreign calibration corpus;
topographical-list methodology; Aegean/Anatolian toponym content).

## Verdict: are they related?

**To each other — LOOSELY.** A co-retrieval bundle, not a coherent source cluster. The only common
thread is *how non-Egyptian toponyms/peoples surface in Egyptian New Kingdom records*. They share no
dataset, no common corpus, no citation dependency; each rests on different primary editions.

**To the logos work — WEAKLY and unevenly, and NONE supplies ingestible REQ-01 or REQ-02 data.**
None is the Kom el-Hetan Aegean-list primary edition (so none closes REQ-01), and none yields clean
calibration anchor pairs (so none touches the frozen REQ-02 gate). Their real value is one methodology
citation (James) plus bibliographic signposting to the sources we actually need (Edel & Görg 2005 etc.).
Notably, **none contains any Aegean/Cretan En-list toponym** (no Knossos/Amnisos/Lyktos/Phaistos/
Kydonia/Keftiu/Tanaju anywhere).

## Per-document dispositions

| # | Document | Tier | Disposition | Why |
|---|---|---|---|---|
| 1 | **Peter James 2017**, "The Levantine War-Records of Ramesses III," *Antiguo Oriente* 15:57–148 (91 pp; sha `d6a534ff`) | **TANGENTIAL** | **CITE_ONLY** (methodology) | On-genre (Medinet Habu "Great Asiatic List" XXVII). But identifications are contested (northernist vs southernist), secondhand (Simons 1937), and **redundant with Hoch 1994** — which the paper itself cites, and which is the source of our frozen corpus. ~6–12 secure pairs, all already in standard onomastica. No En-list content. |
| 2 | **Emad Abdel Azeem 2024**, "From Marriage to Capture: Egypt & Arzawa in the NK," *SHEDET* 12:19–38 (20 pp; sha `63f33147`) | **PERIPHERAL** | **CONTEXT_ONLY** | Diplomatic-history narrative, not an edition. 0 secure new pairs (only trivial `ḫ-t-tA`=Ḫatti). Value = signpost to REQ-01 editions (Edel & Görg 2005, Gander 2015, Cline & Stannish 2011) and the Anatolian Asia/Assuwa/Isuwa/Arzawa debate flanking the Aegean question. |
| 3 | **Gotthard Reinhold 2016**, *The Rise and Fall of the Aramaeans* (Peter Lang; 178 pp; sha `668eb6c7`) | **PERIPHERAL** | **CONTEXT_ONLY** | Aramaic epigraphy / Aramaean political history. Only Egyptian datum = `pȝ-ʾrm`=ʾrm (already known, disputed early-Aramaean claim). Copyright-encumbered **unauthorized dokumen.pub scan — PDF/text NOT committed, NOT redistributed.** |

## The one genuinely useful takeaway (James, methodology — non-copyrightable facts)

NK group-writing oval-transcription conventions, stated explicitly and consistent with our model:
Egyptian **r** renders Semitic **n/l**; Egyptian **t** renders W-Semitic **s/z**; **final -n** is
commonly elided; defective spellings are frequent. (These corroborate the l→r merger and d→t/r shifts
already in the fitted correspondence model.)

## Actions taken / not taken

- **Registered** all three in `SOURCE_REGISTER.csv` as reference/context sources — `*_NOT_INGESTED`.
- **Did NOT ingest** any into the calibration corpus. Rationale: the frozen/passed REQ-02 gate must not
  be re-opened for redundant, contested data; and their "foreign form" is often *inferred from* the
  Egyptian spelling plus a biblical/onomastic guess — exactly the multiple-testing / cherry-picking
  failure mode **invariant 8** exists to stop.
- **Did NOT commit** the PDFs (audited from scratchpad; the Reinhold scan is copyrighted/unauthorized).

## Corpus-honesty guardrails (restated)

- The REQ-02 calibration gate is **FROZEN and PASSED** (~152 tier-A/B Hoch-derived pairs). Adding even
  one anchor mechanically re-opens it → full gate re-run + re-freeze + PIT/leakage compliance
  (invariant 9). Not warranted by any of these three.
- If REQ-02 expansion is ever pursued, source it from **primary onomastica with independently-secure
  foreign forms** (Simons 1937, Aḥituv 1984, Kitchen RITANC) — never from secondary re-analyses.
- **Firewall:** Aegean/Cretan En-list toponyms are *confirmatory targets* for a downstream reading and
  must never leak into Linear A hypothesis formation/scoring. (None of these three carries such forms;
  no immediate leakage vector — firewall kept explicit anyway.)

## Bottom line for REQ-01

All three merely **cite** the real target. The REQ-01 next step is unchanged: acquire and directly
collate **Edel & Görg 2005** (ÄAT 50) — plus Edel 1966 (BBB 25) for the statue-pedestal lists and
Gander 2015 (Klio 97/2:443–502) for the Anatolian-vs-Aegean reading debate.
