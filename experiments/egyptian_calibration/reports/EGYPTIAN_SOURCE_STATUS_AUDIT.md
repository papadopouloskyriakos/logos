# EGYPTIAN_SOURCE_STATUS_AUDIT — §III

Audit of every locally-available Egyptian source for its fitness to populate a **non-Cretan
Egyptian→foreign correspondence** calibration corpus (paired: Egyptian group-writing spelling ↔
independently-known foreign source form, with segment alignment + confidences).

| source | sha256 | pages | fitness for the calibration corpus |
|---|---|---|---|
| Hoch 1994, *Semitic Words in Egyptian Texts* | `4df9bc09…` | 594 | **RIGHT source, UNUSABLE**: entry *prose* extracts cleanly (Semitic forms + meanings) but the specialized **group-writing transliteration is OCR-corrupt** (aleph/ayin/emphatics mangled) → the segment-level Egyptian-spelling ↔ Semitic-consonant alignment the model needs is not recoverable to standard |
| Kilani 2019, *Vocalisation in Group Writing* (CC-BY) | `4ecff477…` | 161 | **CLEAN but WRONG LAYER**: models group-writing→**vowel** reliability from **native** Egyptian words via Coptic; its Appendix A corpus is native lexemes, **not** Egyptian renderings of independently-known foreign forms. Cannot populate a foreign-consonant-correspondence calibration |
| Kitchen, *NK Topographical Lists* | `b1a6c8fa…` | 8 | **discussion only** — an 8-page methodological chapter; contains **no** extractable Egyptian-spelling ↔ identification data tables |
| Muchiki 1999, *Egyptian Proper Names & Loanwords in NW Semitic* | — | — | **NOT AVAILABLE** (the ideal foreign-proper-name source; paywalled, never acquired) |
| Cline & Stannish 2011; EA5647; Kom el-Hetan | — | — | **EXCLUDED by rule** — Cretan/Keftiu TARGET material |

## Decisive finding
There is **no machine-readable, provenance-complete, non-Cretan Egyptian→foreign correspondence corpus
buildable to the required standard** from available sources: the correct source (Hoch) is OCR-corrupt at
the transliteration layer; the only clean corpus (Kilani) is the wrong layer (native vocalization); the
one topographic source (Kitchen) is discussion-only; the ideal foreign-name source (Muchiki) is absent.
This is a **source-access + extraction-defect blocker at the load-bearing input**, not a power question
(there is no fittable-but-weak corpus to assess). → the gate is `INCOMPLETE` (see FINAL verdict).
