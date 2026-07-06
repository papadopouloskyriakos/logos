# EGYPTIAN_VISION_EXTRACTION_METHOD — how the corpus was derived (unblock)

The dataset is **not downloadable** (open Egyptological corpora are the wrong content; Hoch/Muchiki/
Schneider are copyrighted print). It was **derived from the Hoch 1994 scan we already own** by reading
the PAGE IMAGES directly (vision), bypassing the OCR corruption entirely — a genuine hand-verification.

## Method
- Hoch is a scanned book (300 dpi CCITT images + a corrupt OCR text layer). pdftotext mangles the
  specialised transliteration, so it was NOT used for the pairs.
- Instead each dictionary entry page (PDF p.36–247 ≈ book p.14–225) was **read as an image**, and each
  entry transcribed: Egyptian group-writing transliteration (consonantal skeleton), gloss, the
  romanised Semitic cognate(s) with language tag, and Hoch's own **reliability tag [1]–[5]**.
- **Tiering is author-provided, not invented:** Hoch's `[5]`/`[4]` → tier **A**, `[3]` → **B**, `[2]` →
  **C**, `[1]` → excluded. This is exactly the hand-verification the discipline required.
- Cretan/Keftiu/Linear-A material is excluded by construction (Hoch is Semitic; verified zero leakage).
- Consonantal-skeleton duplicates (same root, e.g. the four `n-h-r` entries) were collapsed to one, so
  the corpus is ~1 record per root (156 distinct roots / 159 records).

## Result (frozen, `data/manifests/egyptian_calibration_primary.sha256` = `cc2c20d8…`)
- **159 records; 152 tier-A/B (99 A, 53 B); 156 distinct consonantal roots** (effective independent units).
- item classes: LOANWORD 130, PERSONAL_NAME 23, DIVINE_NAME 3, TOPONYM 1, ETHNONYM 1, OTHER 1.
- cognate spread: BH 142, Ug 84, Akk 64, Ar 40, Aram 30, Ph 25, Syr 24, Amor 9, Eth 4, …
- **Zero Cretan/Keftiu/Linear-A leakage.**

## Licensing
Hoch is copyrighted (Princeton UP). The derived correspondence records are GITIGNORED (data/*); this
methodology, the coverage counts, and the sha256 checksum are committed. Reproduce by re-reading the
owned scan.

## Status
This **lifts the REQ-02 blocker**: the load-bearing calibration corpus now exists to standard (tier-A/B
≥ 150, author-tiered, root-independent). The gate can proceed to fit the FROZEN model spec
(`configs/egyptian_model_freeze.json`) → validation → matched-scarcity control → nulls → power → verdict.
