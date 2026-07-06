# REQ-01 CLOSED — direct collation of Edel & Görg 2005, Liste EN (2026-07-06)

The REQ-01 **primary edition** — Edel († ) & Görg, *Die Ortsnamenlisten im nördlichen Säulenhof
des Totentempels Amenophis' III.* (ÄAT 50, Harrassowitz 2005, ISBN 3-447-05219-8) — was **delivered
by the user** (scp, 20 MB, 135-pp OCR scan, sha `2a6f7f19…`, gitignored) and **directly collated**.
Verified front matter + TOC (Liste AN/BN/CN/DN/**EN 161**/Fragmente/Register + Fototafeln 1-12 +
Falttafeln 1-14). Collation by workflow `wf_2a50f935-9c4` (6 agents, 0 errors), reading Edel's own
oval transliterations, apparatus, certainty qualifiers, Görg `(MG:)` revisions, and line-drawings.

## Status: `REQ-01 = CLOSED_PRIMARY_COLLATED`  ·  `primary_edition_verified = true`  ·  `confirmatory_eligible = true`

The frozen Cretan confirmatory target set is the machine-readable artifact
`frozen/cretan_confirmatory_targets.json` (freeze-identity `sha256:6903f5f1…`, 5 targets).

| Toponym | EN row | Edel transliteration | Egy skeleton | Linear B | Certainty | Freeze |
|---|---|---|---|---|---|---|
| **Knossos** | li 10 | `kꜣ-jn-jw-šꜣ` | knš | ko-no-so | *sicher* | **FROZEN** |
| **Amnisos** | li 11 (+li 1 palimpsest) | `[j]ʿ-m-n-i-šꜣ` | ʾmnš | a-mi-ni-so | *sicher / sehr gut* (Osing autopsy) | **FROZEN** |
| **Lyktos** | li 12 | `rj-kꜣ-tj` | rkt | ru-ki-to | undisputed reading (Kitchen 1965) | **FROZEN** |
| **Phaistos** | li 2 (front palimpsest) | `bꜣ-y-šꜣ-tj` | byšt | pa-i-to | visible name *sicher* (Osing); undertext fraglich | **FROZEN_WITH_ALTERNATIVES** |
| **Kydonia** | li 3 (front palimpsest) | `Kꜣ-tw-nꜣ-y` | ktny | ku-do-ni-ja | *sicher* (visible name) | **FROZEN_WITH_ALTERNATIVES** |

*Secondary robustness anchor:* **Kythera** li 8 `kꜣ-tj-i-rꜥ`=ktr → ku-te-ra (*sicher*, "schlechthin
perfekte Wiedergabe") — the bridge island, not strictly Cretan.

## What the primary edition CORRECTED versus the secondary sources

The Bělohoubková-thesis / Cline-&-Stannish pass had marked **Phaistos** and **Kydonia** *not freezable*.
The editio maior overturns that:
- **Phaistos** is the *visible/recut* name on li 2 (Osing-confirmed by on-block autopsy). "Pisaia/Pisatis"
  is only the **erased undertext** — not the oval's reading. So Phaistos is freezable (palimpsest caveat).
- **Kydonia** is a *secure Edel reading* ("verblüffend genau"), not the "single-authority" the secondary
  sources implied. Freezable (palimpsest caveat).

So the primary edition **strengthened** the set from 3 → 5 anchors. It also confirmed the three
unconditional readings, and — notably — Lyktos's Greek **L rendered by Egyptian r** matches the l→r
correspondence the frozen calibration model independently learned (`P(egy|l): r`).

## Residual caveats (honest, non-blocking)

- **Plate verification outstanding.** Tafel 12 (the only photo) is too eroded to read the ovals at sign
  level; the **Falttafeln 13/14 hand-copy facsimiles are absent** from this 135-pp scan. The freeze rests
  on Edel's *edition text + his own line-drawings* (Fig. 1-4, reconstruction table p.191) — authoritative,
  but not independently-legible photographic confirmation. **Next:** source the fold-out Falttafeln
  separately for sign-level plate verification.
- **Palimpsest dependency.** Phaistos/Kydonia are freezable only via the surviving Vorderseite palimpsests
  li 2 / li 3; their original Cretan-side ovals (li 14 / li 15) are physically lost.
- **Diacritic legibility.** Edel prints aleph and ayin identically (apostrophe) → Amnisos's leading a-sign
  (ꜣ vs ꜥ) is not confidently distinguishable at scan resolution (rendered ꜣ by convention).

## Discipline & next step

This pass is a **FREEZE ONLY** (invariants 3, 8): no Linear A matching, no sign-value claim, no external
preregistration. The Cretan targets are externally fixed by the ancient list — not tuned to fit anything —
and competing readings are carried as alternatives, not collapsed to a cherry-picked choice.

**The one-shot Cretan-anchor preregistration is now UNBLOCKED.** Recommended next artifact: a preregistration
(fresh timestamp/DOI) anchoring on the three FROZEN targets (Knossos/Amnisos/Lyktos), with the two
FROZEN_WITH_ALTERNATIVES (Phaistos/Kydonia) and optional Kythera as robustness anchors, stating the
falsifiable prediction (apply the frozen correspondence model to each Egyptian oval → recover the Linear B
skeleton) and the multiple-testing deflation up front. **Do not run the test until it is preregistered.**
**Firewall:** these Cretan targets must never enter Linear A hypothesis formation or scoring.
