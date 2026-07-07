# L — SOURCE WATCH (evidence that would materially move the value layer)

**Campaign:** `research/linear-a-relative-phonology-seals` · **Constitution:** v2.2 · **WP-L.**
**Prospective clock frozen:** 2026-07-07 (every future-source prediction below is timestamped to this date).
**Web search performed:** 2026-07-07 (WebSearch/WebFetch available). Sources checked live; results dated in `data/source_watch/watch.json` per candidate.
**Machine-readable companion:** `data/source_watch/watch.json` · **Parsers:** `scripts/l_ingest_parsers.py` · **Tests:** `tests/test_l_ingest_readiness.py` (6/6 pass) · **Baseline generator:** `scripts/l_source_watch_build.py`.

## Purpose

Stand up a monitor for external evidence that could *materially* move Linear A above its current earned
layer (L2 structure; SEMANTIC+ NOT_AUTHORIZED per `governance/transfer_licences.json`). Each candidate is
scored for constraints added, equivalence classes broken, expected power gain, claim layer affected,
availability, licence, and automation feasibility, then ranked. This is the "insurance + offence" instrument:
it tells us the moment a real anchor becomes acquirable, and it refuses to score dependency-contaminated
sources as if they were independent.

## The honest ceiling (governs every EIG below)

Prior campaigns (memory: *linear-a-constraint-expansion*) established that **internal evidence is
relabeling-invariant**: no amount of *monolingual* corpus growth can, by itself, lift value-layer
underdetermination — only a bilingual or **≥3 independent held-out anchors** can. So the watch scores two
distinct things and never conflates them:

1. **Falsification power** — a new held-out text grades pre-frozen predictions (Invariant 3, the
   Linear-B-new-tablet standard). *Anetaki II sits here.*
2. **Value recovery / licence lift** — requires independence from the GORILA→Ventris homomorphic lineage.
   *No registered candidate delivers this alone.*

A source can be top-ranked for (1) and still authorize **no** SEMANTIC+ licence. We say so explicitly rather
than let "longest inscription ever" read as "decipherment fuel."

## Ranked watch (by expected information gain)

| # | Source | EIG | Layers | Avail. (2026-07-07) | License | Auto |
|---|--------|-----|--------|---------------------|---------|------|
| 1 | **Anetaki II** — editio princeps of KN Zg 57/58 (ivory scepter, ~119 signs) | **HIGH** | L2–L4ctx,L7 | UNAVAILABLE (forthcoming) | copyright (INSTAP) | LOW |
| 2 | **New LA inscriptions + joins** (Del Freo rapport stream) | MED-HIGH | L1–L3 | PARTIAL | per-pub | MED |
| 3 | **Sign catalogues / rationalized sign-lists** (Salgarella 2022, Ferrara repertoires) | MED | L1 + info-budget denom. | AVAILABLE | CC BY-NC-ND | MED |
| 4 | **Re-editions / GORILA corrigenda** | MED | L1 | PARTIAL | per-pub | MED |
| 5 | **SigLA version bumps** | MED | L1–L2 | AVAILABLE | CC BY-NC-SA | HIGH |
| 6 | **Cretan Hieroglyphic** (Civitillo/Ferrara/Meissner 2024; new seals) | MED-LOW | L2, L6-comparandum | AVAILABLE | copyright | LOW |
| 7 | **Museum image / autopsy releases** | LOW-MED | L0–L1 | SPORADIC | museum terms | MED |
| 8 | **Cypro-Minoan updates** | LOW | L2 | PARTIAL | per-pub | LOW |
| 9 | **Onomastic / toponym indexes** (Younger lexicon) | LOW (capped) | L5,L8 | ARCHIVED-ONLY | web-archived | HIGH but capped |

Full per-candidate rationale, web-status strings, and monitoring triggers are in `watch.json`.

## Web-verified status of the two decisive candidates

- **Anetaki II — STILL UNPUBLISHED as of 2026-07-07.** The only edition-bearing publication remains the 2024
  *Ariadne* Suppl. 5 overview (Kanta/Nakassis/Palaima/Perna), which prints archaeological context and **no
  transliteration**. March-2026 popular coverage of the "Minoan ivory scepter" still frames the inscription
  as unpublished/undeciphered. No 2026 critical edition located. → the genuine prospective held-out gold is
  **not yet acquirable**; the campaign's Anetaki predictions stay sealed and ungraded.
- **Younger's online LA / Cretan-Hieroglyphic corpora went OFFLINE** (University of Kansas withdrew hosting;
  confirmed in the postscript to *Cretan Hieroglyphic*, CUP 2024, reviewed BMCR 2026.01.17). **Ingestion
  consequence:** treat the Younger lexicon/texts as *archived-only* — ingest from the held Wayback captures
  (`SRC-YOUNGER-*`), never assume a live URL. Flagged in `L_INGESTION_READINESS.md`.

New this cycle (context, not corpus): *Cretan Hieroglyphic* (Civitillo, Ferrara & Meissner eds, CUP 2024) is a
synthesis, **not** a new corpus/sign-list; a new hieroglyphic seal analysis (KN S(4/4) 01) circulated in 2025;
DBAS-CHS (Florence) continues to catalogue 300+ hieroglyphic seals/nodules.

## Monitoring triggers (what to poll, and the fire condition)

- **Anetaki II:** INSTAP Academic Press catalogue + WorldCat new-monograph alert + Kanta/Nakassis/Palaima
  feeds. **FIRE:** any listing with a transliteration/plates → open the sealed Anetaki predictions, grade,
  never re-seal.
- **New finds / joins:** Del Freo rapport cycle, BCH *Chronique des fouilles*, SMEA/Kadmos, INSTAP *Kentro*.
  **FIRE:** any editio princeps with signs → run `parse_editio_princeps` → append to
  `post_gorila_additions` (Art. XVII append-only), re-measure held-out supply.
- **Palaeography (SigLA / sign-lists):** `sigla.phis.me` `database.js` hash change; Salgarella/Ferrara output.
  **FIRE on hash change:** re-run `scripts/sigla_decode.py`; on a sign-count change, re-run the
  information-budget denominator (Invariant 7) before any significance figure is quoted.
- **Sister scripts:** CUP/CHIC catalogue, DBAS-CHS, Ferrara/HoChyMin. **FIRE:** a new *corpus edition*
  (not a synthesis) only.

## Compliance line

WP-L SOURCE-WATCH: articles_triggered {VII search-receipt, IX info-budget, XI source-dependency, XII
no-self-grading, XV licences}; gates {no dependency-contaminated source scored as independent; no monolingual
source scored as a licence-lift; counts machine-generated (Invariant 12)}; assumptions {EIG is ordinal and
pre-acquisition; real syllabary ≈92 for the denominator}. Status: **INVENTORY_BUILT**; no verdict altered; no
prediction opened (Anetaki II unavailable). Prospective predictions frozen 2026-07-07.
