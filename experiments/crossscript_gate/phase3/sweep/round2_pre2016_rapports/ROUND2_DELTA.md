# ROUND2_DELTA — corpus-completeness sweep, round 2 (the pre-2016 rapports)

**Date:** 2026-08-10 · **Trigger:** M. Del Freo (CNR) privately sent the four print-locked
rapports that round 1 (2026-07-03, `../SWEEP_DELTA.md`) could only gap-list, in reply to the
owner's 2026-07-03 index-offer email. **Stage header (Art. XXII):** articles_triggered =
VII (search receipt: provenance + alias table printed in `diff_round2.json`), XI
(source-dependency: rapport PDFs → fragment CSVs → mechanical diff/verify → this doc), XVII
(append-only: round-1 artifacts untouched except one declared SUPERSEDING field-add,
`the_zb_14.json`), XVIII (assumptions: the ALIASES map in `round2_scan.py` is the complete
list of identity assumptions). Gates: none on the verdict path — this is corpus/bibliographic
work at L0/L1; no claim above L1 is made; no model run; no held-out label read.

**Verdict: `UNMOVED` for the anchor supply — and the 1996–2015 enumeration is now AUDITED
FACT instead of assumption.** Zero new anchor legs. The two named unknowns of round 1
(1996–2000 publication status; 1986–1990 venue) are resolved. The real yield is
identity/divergence intelligence: 12 flagged silver items, 5 Thera ad-hoc IDs identified,
2 round-1 errata, 1 new systematic silver defect (Arkhanes site labels).

## What arrived (bronze: `corpus/bronze/delfreo_rapports_pre2016/`, gitignored, never redistributed)

| Window | Work | LA section | SHA-256 (prefix) |
|---|---|---|---|
| 1996–2000 | Olivier, *Pasiphae* III (2009) 187–197 | §2, pp. 189–193 | `702973c6` |
| 2001–2005 | Del Freo, *Colloquium Romanum* (Pasiphae I), 2008, 199–222 | §2, pp. 202–213 | `7ebba45a` |
| 2006–2010 | Del Freo, *Études mycéniennes 2010* (Bibl. Pasiphae 10), 2012, 3–21 | §2, pp. 7–15 | `e7167504` |
| 2011–2015 | Del Freo, *Aegean Scripts* (Incunabula Graeca 105), 2017, vol. 1, 3–29 | §2, pp. 10–18 | `60c3eb25` |

**Round-1 unknowns resolved:** (a) the 1996–2000 rapport WAS formally published — *Pasiphae*
III (2009) 187–197, the text of the communication read at Austin in May 2000 (so the
"1996–2000 hole of unclear status" row closes as ACQUIRED); (b) Rapport 1986–1990 =
Olivier, in *Mykenaïka* (BCH Suppl. 25, 1992), pp. 443–456 (per the 2006–2010 abbreviation
list) — the coverage map's UNASSESSED row now has an exact citation (Persée hosts BCH
supplements; possibly honest-OA, unverified). (c) Rapport 1991–1995 pages sharpened to
*Floreant Studia Mycenaea* pp. 419–436. Only 1986–1990 and 1991–1995 remain un-acquired.

## Headline numbers (generated: `diff_round2.json`, `scan_round2.json`)

| quantity | value |
|---|---|
| Fragment rows (4 CSVs, `fragments/`) | 96 (23 + 36 + 18 + 19) |
| Present in the frozen inventory (after declared aliases) | 70 |
| — of which flagged (doubt/divergence/superseded-reading) | 12 |
| Missing, a_ingestible (reading in hand via held rapport) | 3 → **all 3 ingested** to `corpus/derived/post_gorila_additions/` (PSE Zb 1 `]*188̣-54̣-28̣[`; SA We 3 `TE+A708`; SA We 4 `Ạ+TE` ligature) |
| Missing, b_acquisition_gap | 4 (PK Wy 22; THE 7/8/Z 9 + THE 7-12 identity rows; GO Wc 3) |
| Missing, c_pending_edition | 7 (ARKH Zb 10; ARM Zg 1; PSE Zb 2; ZA Zb 35→39 ×2 rows; KAST Wy 1; Mochlos frr.) |
| Missing, d_correctly_absent (absence is the endorsed state) | 12 (negatives, deletions, anepigraphic, bookkeeping) |
| Census-word scan of the 3 new additions | **0 anchor legs** (sign delta: *188, WA, I ×1 each) |
| Frozen corpus SHA-256 before == after | `aaee1aeb…`, `4717a7e3…`, `8a2a8928…`, `246f63f1…` — all four IDENTICAL to round-1 pins (recomputed 2026-08-10) |

Classifier deltas vs round 1 (declared in `round2_scan.py` docstring): a_ingestible no longer
requires open accessibility (the held rapport itself prints the reading — the round-1 OA
situation generalized); new class d_correctly_absent so that endorsed absences stop counting
as gaps. Round-1 classes otherwise unchanged.

## Identity resolutions (the alias table's yield)

1. **THEtab.4 = THE 7** (near-certain): silver's numerals [7, 46] + two livestock logogram
   tokens match Boulotis 2008's THE 7 face a exactly ("sign traces + 7"; "AB 21f + 46").
   Silver renders the logogram CAP — Boulotis/Del Freo print AB 21f (= OVISf): these tokens
   sit inside the KNOWN AB21/AB22 inversion family (D4; `corpus/divergences.json` already
   lists THEtab.4 in its livestock-token entry — the register entry can now carry the
   rapport identity).
2. **THEfr.1 ≈ THE 10** (silver: isolated KI = AB 67 — Boulotis: "THE 10 = isolated AB 67").
   **THEfr.2/3 ≈ THE 11/12** (silver: OLE = A 302 — Boulotis: "traces maybe A 302").
   **THEtab.5 ≈ THE 9** (weakest — by elimination: syllabic line, no logograms, which is
   exactly Boulotis's description of the one fragment he does not discuss).
3. **THE 8 is the genuinely missing Thera tablet** (the TELA+SE ≥200-units fragment reported
   since 1996–2000) — no silver candidate carries `54+09 200[`.
4. **Silver ZO1 ≠ the 2013 Zominthos libation table.** ZO1 = vase logogram *409+VS with
   numeral 217 (tablet-like record; earlier Sakellarakis-excavation find; source to verify).
   The 2013 table (Younger's ZO Za 1) is ABSENT from silver — which is the CORRECT state
   given Rapport 2016–2021's masons'-marks verdict. Round-1's "ZO1 possibly the same object —
   verify" is hereby resolved.
5. **PE 6 = silver PEZg6** (Hallager's classification). **ERRATUM to round 1:** the round-1
   `missing_items.csv` lists PE 6 as a b-class acquisition gap; it was present all along
   under the Zg 6 alias. No round-1 verdict is affected (the row drove no analysis).
6. **THE Zb 14 (round-1 additions layer) duplicates silver THEZb15** (the Akrotiri lamp;
   object identity clinched by the shared trailing numeral 2 + lamp support). **ERRATUM to
   round 1:** the addition was ingested because the plain diff missed the editors'-numbering
   alias. A SUPERSEDING `duplicate_of_silver` field was added to
   `corpus/derived/post_gorila_additions/the_zb_14.json` (2026-08-10); nothing deleted.
   Note the readings also differ (silver RE-SA 2 vs ed.pr./rapport SE-*332̣ 2) — same object,
   divergent sign identifications.
7. **KH numbering: silver follows Del Freo** (KHZb98/KH99/KH100 present; Hallager's
   KH Zb 1/98/99 aliases absent) — consistent across the whole KH 97–105 run. The Thera
   series is the opposite story: silver mixes Del Freo's Zb 13 with the editors' Zb 15 and
   carries THEZb5/THEZb7 whose identities this round could NOT establish (neither scheme
   predicts their silver content: Zb 5 = JE; Zb 7 = A-JE).

## Reading verification vs silver (mechanical dump: `silver_verify_dump.json`)

Legend: ✓ = silver matches the rapport-reported reading (AB numbers ↔ silver's LB-value
transcription); Δ = divergence.

**Exact matches (silver is current, incl. post-rapport revisions):** ARKH Zf 9 (JA-KI-SI-KI-NU /
MI-DA-MA-RA₂ = Olivier's 57-67-41-67-55 / 73-01-80̣-76̣) · KN Zb 52 (ZU-RI-NI-MA = 79-53-30-80)
· SY Za 3 join text · SY Za 4 (incl. **NWA = the AB 48 first-attestation**) · SY Za 6 (carries
the REVISED 2008 reading DA-SE-RA-TE = 01-09-60-04, not 1996–2000's 01-28-60-04) · SY Za 8–12
(all five; Za 11 = the rapport's primary alternative RO-QA) · SY Zb 7 (traces dropped) ·
PE Zg 6 (both hapax lines) · **PE Zb 7 (JA-WA-PI = the Del Freo & Zurbach post-restoration
revision AB 57-54-39, not Hallager's A 100/102)** · PH 54 (I-SA-RI-KE = 28-31-53-44) ·
POR Zf 2 (TU-PI-TA = 69-39-59 — the unpublished ring's reading circulated) · PK Zb 21
(KI-TA-NI-TE = the autopsy-confirmed Davis reading) · PK Zb 25 (MI-DA-RA = ed.pr., Hopkins
re-reading not adopted) · MIL Zb 1–4 (all = the 2015 Kadmos edition incl. the Zb 7→Zb 4
renumbering and *86) · CR Zg 4 (I-DA-DA / A-RO-TE = 28-01-01 / 08-02-04) · HT Zb 162
(DI 3 TI-DU) · ZA Zg 35 (ME-MI-JA-RU / SE-WA-AU-DE) · KH 102 (A-MI = 08-73̣) · KH 104
(GRA / DA-RE / GRA) · KH 105 (DE-KI-TI = 45-67-37) · VRY Zb 2 (PO-SA = the 2015 re-reading,
2001–2005's ]73̣[ superseded) · THE Zb 6 (A-TA-NA-JE = Boulotis's 08-59-06-46) · MA Zb 15
(*405+VS + fraction) · ARKH Zc 8 (silver adopts Sakellarakis's A 306-59-46 among the three
printed alternatives) · DRA Zg 1 (silver = Fol & Schmitt's certain first three signs
DA-DU-*301; Del Freo's doubt does not touch content, only attribution).

**Divergences (Δ — register candidates, NOT applied to `corpus/divergences.json`, which is a
generated instrument; a follow-up register run should absorb these):**

| # | Item | Silver | Rapport-series state | Severity |
|---|---|---|---|---|
| Δ1 | KN Zb ⟨27⟩ | numeral **17** + brackets ⟨ ⟩ | 17̣ (GORILA) → 117 (Olivier 1992) → **107** (DF&Z autopsy 2012); pithos REDISCOVERED (brackets obsolete) | reading + status, superseded twice |
| Δ2 | KH Wc 2124 | **WA** (= AB 54) | AB 54 report (2006–2010) was CORRECTED by the 2018 ed.pr. + Rapport 2016–2021 to a **variant of AB 61** | superseded reading |
| Δ3 | THE Zb 15 (lamp) | **RE-SA** 2 | ed.pr./rapport: SE-*332̣ 2 (alt ]73̣[) | divergent identification |
| Δ4 | HT Wc 3024 | A-RA-TU-ME / ***22F**, no numeral | rapport: **06**-60-69-13̣ (NA-…) / **AB 21f 6** | first sign 08 vs 06; 21f→22F = AB21/22-family instance (NOT yet in the D4 register); numeral 6 absent |
| Δ5 | PK Zb 26 | TO-PA₃-**DI** (= 05-56-**07**) | ]AB 05-56-**08** (= …-A) | last sign 07 vs 08 |
| Δ6 | SKO Zc 1 (small frag) | QA-KI-**TI** (16-67-**37**) | ]AB 16̣-67̣-**79̣**[ (…-ZU) | third sign 37 vs 79 (both dotted sources) |
| Δ7 | PK Zb 23 | **KA** (= 77) | Olivier: rather a chariot sketch than AB 87; no 77 on offer | silver commits a sign the series doubts is writing |
| Δ8 | KN Ze 56 | reading **O-DA** | Olivier: three signs, "aucun n'est vraiment lisible", plough-marks not excluded | silver hardens a doubted non-reading |
| Δ9 | LACH Za 1 | site **"Larani"** + full 6-sign reading | Olivier: designation premature (LA/LB/CM/Cypriot all possible; early-12th-c. BCE date) | site DEFECT (Lachish ≠ Larani, a Cretan site) + over-commitment |
| Δ10 | **ARKH 1–6, Zc 8, Zf 9 + ARG Zg 1: site "Arkhalkhori"** | all Arkhanes items (and the Argos item) carry the Arkalochori site label | Arkhanes ≠ Arkalochori | **NEW systematic defect, 11 docs** — merges two sites; touches any site-clustered analysis (direction: coarser clusters = conservative for the published site-clustered CIs; no published verdict re-graded; re-check before site-sensitive reuse, same policy as D1/D4) |
| Δ11 | IN Zb 1, MI Zb 3, HT Zf(HM 767) | included, committed readings (NU-RO; RE-TI; TI-MA) | rapport: reading/attribution "pour le moins incertaine" (IN); "discutable" (MI Zb 3); script deliberately undecided (HM 767) | inclusion-policy divergence |
| Δ12 | IO Za 16, PK Za 27, SY Za 8 | restored formula text WITHOUT brackets (U-NA-RU-KA-NA-SI etc.) | rapport prints breaks (…-77[ ) | D1-family instance (damage/lacuna stripping — known defect, more witnesses) |
| Δ13 | PE Zb 8 | included | GORILA Supplement will EXCLUDE (isolated sign of unsure logographic value) | inclusion-criteria divergence |

**Materiality:** all Δs are metadata/token-level; none touches a published verdict (the
frozen paper's analyses consumed syllabogram sequences in bulk; single-token reading deltas
and two site labels cannot flip any reported null, and the site-label merge coarsens —
i.e. makes more conservative — the site-clustered bootstrap). Policy identical to D1/D4:
recorded, not rebuilt; re-check before any reuse that keys on the affected tokens/sites.

## The audited coverage map (supersedes the round-1 table's gap rows; append-only)

| Window | Rapport | Status 2026-08-10 |
|---|---|---|
| 1986–1990 | Olivier, *Mykenaïka* (BCH Suppl. 25, 1992) 443–456 | citation resolved; NOT acquired (Persée candidate) |
| 1991–1995 | Olivier, *Floreant Studia Mycenaea* (1999) 419–436 | NOT acquired (print) |
| 1996–2000 | Olivier, *Pasiphae* III (2009) 187–197 | **ACQUIRED** (author PDF, private) |
| 2001–2005 | Del Freo, *Colloquium Romanum* (2008) 199–222 | **ACQUIRED** (author PDF, private) |
| 2006–2010 | Del Freo, *Ét. myc. 2010* (2012) 3–21 | **ACQUIRED** (author PDF, private) |
| 2011–2015 | Del Freo, *Aegean Scripts* (2017) I 3–29 | **ACQUIRED** (author PDF, private) |
| 2016–2021 | Del Freo, *KO-RO-NO-WE-SA* (2024) 87–124 | ACQUIRED (OA, round 1) |

The anchor-supply sentence of round 1 stands unchanged, now resting on primary rapports for
1996–2021: every accessible rapport-period item is in the corpus, adds no anchor attestation,
or awaits its editio princeps; the enumeration levers left are the 1986–1995 windows (low
expected yield: their finds are recapped in the acquired rapports) and future editions.

## Compliance

No held-out label read; no recovery model run; frozen corpus byte-identical (four SHA-256
pins recomputed above); additions live only under `corpus/derived/post_gorila_additions/`;
round-1 artifacts untouched except the declared SUPERSEDING field-add in `the_zb_14.json`;
all counts in this document are script-generated (`round2_scan.py` diff/verify/scan);
the four rapport PDFs are gitignored and never redistributed; readings quoted are facts
with page-cited attribution (fair dealing). Claim ceiling: L1 (sign-identity bookkeeping);
nothing here is worded above it.
