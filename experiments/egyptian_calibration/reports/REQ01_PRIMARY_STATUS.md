# REQ01_PRIMARY_STATUS — §III

`REQ-01-secondary`: Cline & Stannish 2011 (present) — provides Aegean-list identifications + caveats.
`REQ-01-primary-edition`: Edel & Görg 2005 (Kom el-Hetan) / Kitchen full collation — **NOT directly
audited** (Kitchen local copy is an 8-page discussion, not the edition).

Therefore for any future Cretan toponym anchors:
```
primary_edition_verified = false
confirmatory_eligible    = false
req01_status             = ADVANCED_PROXIMATE_ONLY   # was NOT_AUDITED
```
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
