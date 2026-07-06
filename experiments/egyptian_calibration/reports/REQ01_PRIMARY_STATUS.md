# REQ01_PRIMARY_STATUS — §III

`REQ-01-secondary`: Cline & Stannish 2011 (present) — provides Aegean-list identifications + caveats.
`REQ-01-primary-edition`: Edel & Görg 2005 (Kom el-Hetan) / Kitchen full collation — **NOT directly
audited** (Kitchen local copy is an 8-page discussion, not the edition).

Therefore for any future Cretan toponym anchors:
```
primary_edition_verified = TRUE    # 2026-07-06: Edel & Görg 2005 (ÄAT 50) in hand + directly collated
confirmatory_eligible    = TRUE    # frozen target set: frozen/cretan_confirmatory_targets.json
req01_status             = CLOSED_PRIMARY_COLLATED   # was ADVANCED_PROXIMATE_ONLY / NOT_AUDITED
```
**→ SUPERSEDED by the 2026-07-06 (evening) closure below.** The block-quoted `false/false` history
and the `ADVANCED_PROXIMATE_ONLY` update are kept for the audit trail; the operative status is CLOSED.
REQ-01 does **not** block this non-Cretan calibration gate, but it WILL block a later confirmatory Cretan
toponym target freeze until the primary edition is directly collated.

## Update 2026-07-06 — online sourcing + apparatus extraction

- **Primary edition still not obtainable free** (Edel & Görg 2005 / Edel 1966 not on archive.org/Propylaeum;
  the only free "Kitchen" item = the 8-page discussion, sha `b1a6c8fa`, re-verified identical). Full online
  search in `REQ01_ONLINE_SOURCING_RESEARCH.md`.
- **User delivered** Bělohoubková 2014 BA thesis (secondary compilation, sha `91a0035b`). It **reproduces
  Edel & Görg's own facsimile plates** (Obr. 5 = Tf. 13; Obr. 7 = Taf. 14) but at non-collatable resolution
  → REQ-01 advances to `ADVANCED_PROXIMATE_ONLY`, **not closed**.
- **Candidate (not confirmatory) target set** frozen where ≥2 independent sources agree:
  **Knossos `k-n-š` (E_N10), Amnisos `m-n-š` (E_N1, doubled E_N11), Lyktos `r-k-t` (E_N12).**
  Phaistos and Kydonia are **NOT** freezable (single-authority / Pisaia-vs-Phaistos discrepancy).
- Full determination + apparatus table: `REQ01_APPARATUS_DETERMINATION.md`.
- **Residual gap:** direct collation of Edel & Görg 2005 (ÄAT 50) plates+apparatus at usable resolution,
  or Kitchen's full hieroglyphic collation. Acquire a high-res copy for personal collation.

## Update 2026-07-06 (evening) — REQ-01 CLOSED_PRIMARY_COLLATED

**User delivered the actual primary edition** (Edel & Görg 2005, ÄAT 50, Harrassowitz, ISBN
3-447-05219-8; 135-pp OCR scan, sha `2a6f7f19`, gitignored). Verified + **directly collated**
(workflow `wf_2a50f935-9c4`, 6 agents). REQ-01 → **CLOSED_PRIMARY_COLLATED**;
`primary_edition_verified = TRUE`; Cretan targets **confirmatory-eligible**.

- **Frozen target set:** `frozen/cretan_confirmatory_targets.json` (freeze-identity `sha256:6903f5f1`,
  5 targets): Knossos `knš`/li10, Amnisos `ʾmnš`/li11, Lyktos `rkt`/li12 (all **FROZEN**); Phaistos
  `byšt`/li2, Kydonia `ktny`/li3 (**FROZEN_WITH_ALTERNATIVES**, palimpsest). Secondary: Kythera `ktr`.
- **Corrected** the secondary-source verdict: Phaistos IS Phaistos on the visible stone (Pisaia/Pisatis
  is the erased undertext); Kydonia is a secure Edel reading. Set strengthened 3 → 5.
- **Residual (non-blocking):** Falttafeln 13/14 facsimiles absent from the scan → photographic sign-level
  plate verification still to source; freeze rests on Edel's edition text + line-drawings.
- **Full apparatus + table:** `REQ01_EN_COLLATION_FROZEN_TARGETS.md`.
- **Next (unblocked, not done here):** preregister the one-shot Cretan-anchor test. Firewall: these
  targets never enter Linear A hypothesis formation.
