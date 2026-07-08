# EPOCH-005 — KNZg57a provenance trace: PROVENANCE_ESTABLISHED, ERRATUM_REQUIRED

**Campaign:** research/linear-a-frontier-72h · 2026-07-08 · Constitution v2.2 ·
Articles VII, IX, XI, XII, XVII, XVIII, XXII · plan_hash `0f96100a…0754` (frozen before any trace step) ·
mechanical checks 13/13 PASS (`epochs/EPOCH-005/audit_checks.json`, re-runnable via
`scripts/epoch005_knzg57a_trace.py --web`).

## Question

EPOCH-001 found silver already contains **KNZg57a** (`*401+RU, *401+RU, *418+L2, NI, VAS`) inherited
from lineara.xyz with no identifiable published source (assumption A-3, conf ≤ 0.5). If a preliminary
transliteration is *public*, the Anetaki seals' exposure records are wrong and need an ERRATUM before
any scoring.

## Answer — the full chain, every link verified

1. **Kanta et al. 2024** (Ariadne Suppl. 5, 27–43; DOI 10.26248/ariadne.vi.1841) publishes
   **photographs** (Fig. 7, "Photo Ph. Sapirstein") and the prose "*vas+PA, vas+RU, etc.*" (p. 38) —
   but **prints no transliterated sequence** (re-verified on the on-disk PDF).
2. **2025-03-23 10:31 UTC** — github.com/mwenge/lineara.xyz commit `9e426baa` "Add KNZg57 KNZg58":
   both records created **EMPTY**, sourced to the Ariadne article URL, credit "Ph Saperstein" [sic].
3. **2025-03-23 17:22 UTC (same day)** — commit `5facf29c` "Add missing images": KNZg57→KNZg57a, the
   **17-slot reading appears**: `*401+RU, *652, *653, *401+RU, *418+L2, 𐝫×4, NI, 𐝫×4, VAS, 𐝫×2`, plus
   KNZg57b (empty transliteration) and images cropped from the article. The site's local
   `papers/KNZg57.pdf` is **byte-identical** (sha256 `87dad27b…57d2`) to our bronze Kanta 2024 PDF.
   ⇒ **The reading is Robert Hogan's (mwenge) own photo-reading of the published Fig. 7 — authored the
   day the article hit the March-2025 media wave. No scholarly transliteration exists** (Del Freo
   Rapport 2016-2021: both carriers "inédit").
4. `scripts/corpus_io.py` deterministically filters the 7 identified tokens to silver's 5
   (`is_sign_token` requires a latin letter → `*652`,`*653` dropped; KNZg57b dropped as empty).
5. The page is **live today** (lineara.xyz/items/KNZg57a.html, HTTP 200).

**Controls:** positive — the same pipeline recovers KNZg55 = JA-SA-JA in Younger misctexts (method has
power); negative — zero sources for the nonexistent "KN Zg 56" (no confabulation). 25 distinct source
records audited (GORILA categorically excluded — closed 1985, object found 2016; SigLA 0 hits;
Civitillo = Zg 55 only; Rjabchikov 2025: 0 token overlap AND postdates the commit — cannot be the
source).

## Verdict

**PROVENANCE_ESTABLISHED** (per the pre-frozen rule: a public, citable record — lineara.xyz commit
`5facf29c`, 2025-03-23 — prints 5/5 silver tokens in order and predates silver ingest), with the
qualifier that the source is an **editorial photo-reading, not an edition**; reading reliability stays
≤ 0.5 (A-3 *updated*, not removed). H-P3 (fabrication) REJECTED.

**ERRATUM_REQUIRED = true (Art. XVII), before any seal scoring:**

- `J1_exposure.json` (seal branch): its central finding — "No public source … carries a transliterated
  sign-group sequence from KN Zg 57 or KN Zg 58" — is **factually false for Zg 57 since 2025-03-23**
  (still true for Zg 58). Add lineara.xyz as a SRC row; correct the finding.
- Both seals' `"in_current_corpus": false` — misstated; silver holds the 5-token fragment.
- **M seal MP1**: 5–7 of the ~119 target sign slots are publicly known; A-only-count contamination ~0
  (NI = AB; the ligatures are not A-only syllabogram types), but the publicly-known slots must be
  excluded from prediction credit; note the (<0.1%) base-rate self-inclusion.
- **Scoring targets remain unexposed** — no Face-B group, no handle numeral, no libation anchor, no
  value-bearing anchor, no substitution pair is derivable from the 7 public tokens. The seals stay
  SEALED_PROSPECTIVE and scoreable *after* the erratum lands.

**Quarantine:** exclude KNZg57a from any future prediction credit or held-out unit; when *Anetaki II*
publishes, grade lineara.xyz's 7 tokens as a committed external hypothesis (like Rjabchikov/Chiapello).

**Kanta 'vas+RU' sub-question:** DOES_NOT_LICENSE the silver reading (names ligature *types* only,
includes vas+PA which silver lacks; no count/order/face) — the silver sequence is *consistent* with the
prose but not derivable from it.

*Art. IX: zero decipherment information added; L0 metadata only; no licence change.*
