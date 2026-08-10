# WATCH: Anetaki II (Kanta ed., forthcoming — INSTAP Academic Press)

**What is awaited:** *Anetaki II: the Neopalatial Room 1 and the Ivory Repository* — the full
edition of KN Zg 57 (ivory Ring, ~119 signs, longest known Linear A inscription) and KN Zg 58
(handle), including the transliterations the 2024 overview defers (~16 sign-groups: six
"perfectly recognizable" on Face B, ≥9 on Face C, the four-sign handle Face-β sequence, the
Face-A syllabograms and ligatures, the six-fraction sequence). Verified unpublished as of
July 2026 (`experiments/crossscript_gate/phase3/anetaki_extraction.md`).

## What to monitor (human, quarterly glance — NO standing agents)

- INSTAP Academic Press catalog / new-titles page.
  SERIES POINTER (from Henkel & Margaritis 2022, Religions 13:81, OA, vault
  `corpus/bronze/anetaki_context/`): the Anetaki editions belong to the INSTAP series *The
  Religious Center of the City of Knossos* — **Vol. 1: The Fetish Shrine** (Kanta ed.,
  forthcoming) is a sibling volume; the KN Zg 57/58 edition ("Anetaki II" = the Neopalatial
  Room 1 / Ivory Repository). Watch INSTAP for BOTH volumes of this series.
- The Ariadne Supplements page (ejournals.lib.uoc.gr) and Kanta's publication listings.
- SigLA (sigla.phis.me) and lineara.xyz for KN Zg 57/58 ingestion (both empty as of
  2026-07-03).
- Corroboration on file: Kentro 24 (Fall 2021, INSTAP newsletter; vault
  `corpus/bronze/kentro_newsletters/`, sha 56a6dfe6…) — the Anetaki archaeobotany report states
  full results appear "as chapters in excavation volumes on Anetaki": the volumes are in
  preparation as of 2021. Kentro is itself a cheap annual signal: each fall issue may carry
  Anetaki/publication-status notes.

## THE TRIGGER — the day KN Zg 57/58 transliterations publish

1. **Acquire + register** per the house pattern (vault + SHA-256 + `_acquisition.md`).
2. **Run the pre-built census re-scan** per
   `experiments/crossscript_gate/phase3/GAP_DELTA.md`: exact/variant matches of the new
   sequences against `anchor_census.csv` `la_signs` → new LOTO legs; editor-identified
   names/toponyms → provenance-graded census candidates. Editor-printed readings only — the
   no-reading-from-photographs rule stands forever.
3. **Grade the two registry entries mechanically** against the official text
   (docs/linear-a-claims-2026.md): Rjabchikov 2025's photograph-derived readings
   (fringe-quarantined; pre-date the edition, so gradable sign-by-sign) and the 2024
   pre-publication prediction paper (greater A/B similarity + Greek-reading support —
   falsifiable, scorable).
4. **Only then** does a Phase-3 discussion become eligible — under a NEW pre-registration and
   a NEW external timestamp. The N=2 ledger is closed; any Phase 3 is a new pre-registered
   family, and its prereg must say so.

## Addendum (2026-07-03): pending-edition items from the corpus-completeness sweep

The sweep (experiments/crossscript_gate/phase3/sweep/) identified **26 class-(c)
pending-edition items** (enumerated in the del Freo rapport 2016–2021 or channel sources but
never transliterated) — full rows in `missing_items.csv` filtered `class=c_pending_edition`;
headline items beyond KN Zg 57/58: the Kommos, Hagia Photini fragments, THE Zg 16's edition,
the ZA 11 + ZA 13 new joins (pending Petrakis). These join THIS watch: same quarterly glance,
same trigger mechanics (acquire → GAP_DELTA/SWEEP re-scan → census update). Also on watch:
the four pre-2016 del Freo rapports (print-only; the human gap list) whose acquisition would
close the 1985–2015 enumeration coverage holes, and PYR Zb 5's pending removal (reattributed
to Cretan Hieroglyphic per Ferrara et al. 2016, endorsed by the rapport — flagged for the next
corpus rebuild, NOT applied to the frozen corpus).

**Reopening-thresholds hook (2026-08-05):** on any trigger firing, also consult the
GENERATED `docs/reopening-thresholds.md` — compare the new-corpus delta against each
route's `reopen at` column (nearest tripwire: alternation grid at +288 docs ≈ 10.5
KN-Zg-57-equivalents). A crossing mandates a NEW preregistration, never an automatic
claim; new-edition readings enter through `corpus/divergences.json`
(`scripts/divergence_register.py`), not ad-hoc adoption.

## Addendum (2026-08-10): pre-2016 rapports acquired; RILA-S1 exists; watch-list deltas

The "four pre-2016 del Freo rapports" line above is RESOLVED — all four received privately
from the author 2026-08-10 (round-2 sweep: `experiments/crossscript_gate/phase3/sweep/
round2_pre2016_rapports/ROUND2_DELTA.md`; verdict UNMOVED, 0 anchor legs; the 1996-2000
rapport was published in *Pasiphae* III (2009) 187-197). Watch-relevant deltas:

- **RILA-S1 IS PUBLISHED**: Del Freo & Zurbach, *Recueil des inscriptions en linéaire A.
  Supplément 1*, Études Crétoises 21.6, EFA/Peeters 2024 (ISBN 9782869586420, not OA) —
  +107 documents / +427 signs (corpus 1,534 docs / 7,574 signs, cutoff end-2023), with a
  dubious-texts section. It is the candidate primary edition for MANY of this watch's
  pending items and for the announced Supplement readings (KN Zb 27 numeral 107, PE Zb 7
  AB 57-54-39). **+107 docs does NOT cross the +288 alternation-grid tripwire on its own.**
  Acquisition = owner decision; on acquisition: round-3 diff + divergence-register pass
  (new witness), THEN the reopening-thresholds comparison per the 2026-08-05 hook.
- KN Zg 57/58 (Anetaki) editio princeps: STILL PENDING as of Rapport 2016-2021 — the
  anchors-route trigger (`new_site_toponym_candidates`) remains the live tripwire.
- New pending-edition stragglers from the pre-2016 windows (round-2 class c, see
  `round2_pre2016_rapports/missing_round2.csv`): KAST Wy 1 (Rethemiotakis, announced
  2001-2005, reading printed in rapport), ZA Zb 39 (announced 1996-2000 as Zb 35),
  ARKH Zb 10, ARM Zg 1, PSE Zb 2, Mochlos Block C fragments — same quarterly glance.
- THE 7-12: definitive Boulotis edition still pending; identity of silver's ad-hoc IDs
  partially resolved (THEtab.4 = THE 7, THEfr.1 = THE 10 CONFIRMED; fr.2/3 and tab.5
  witness-conflicted — register entry R2THE); **THE 8 missing in silver, present in
  SigLA**.
