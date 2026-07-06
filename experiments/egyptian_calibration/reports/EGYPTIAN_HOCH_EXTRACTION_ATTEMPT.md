# EGYPTIAN_HOCH_EXTRACTION_ATTEMPT — deriving the corpus from the owned Hoch scan

After confirming no downloadable open dataset exists (TLA/Ramses = native Egyptian; Trismegistos =
Greco-Roman-period names; Hoch/Muchiki/Schneider = copyrighted print), we attempted to DERIVE the
calibration corpus from the Hoch 1994 scan we already own (`src/calibration/extract_hoch.py`).

## Yield
- **101 entries** parsed from the OCR body; **76 tier-A candidate pairs** (clean romanized headword +
  ≥1 romanized Semitic source form), 25 tier-C.
- Egyptian headwords extract CLEANLY (`abu`, `anak`, `atpata`, `atba`) in the consistent OCR
  normalization (aleph→'3', ayin→'c').

## The irreducible blocker (a clean finding, not a mere OCR gripe)
The **pairing** — which source form is the etymon of which headword — is NOT reliably recoverable from
the OCR: entry-block boundaries bleed, entries cite multiple comparanda, and prose words are caught
(`abu`↔abu ✓, `atpata`↔ispatu ✓, but `aswata`↔usparu ✗ bled from the next entry, `Yamsula`↔all ✗).
Cleaning this requires either:
- **(a) hand-verification** of each headword↔etymon pair against Hoch's actual entry structure, or
- **(b) similarity-based pairing** — which is **FORBIDDEN**: selecting the source form by consonantal
  resemblance to the headword would bias the very correspondence probabilities the model estimates
  (circular; it is exactly the fishing-rod the gate exists to prevent).

So the auto-derived corpus is **noise-limited at ~76 candidates**, below the ≥150 clean-entry threshold,
and cannot be cleaned automatically without circularity.

## Consequence
The gate remains `INCOMPLETE`. To reach a **powered** calibration, one of:
1. a **clean machine-readable Hoch** dataset (pairs already structured), OR
2. **Muchiki 1999** machine-readable, OR
3. an **authorized hand-verification pass** over the ~76 tier-A candidates + more (labour-bounded;
   yields a sensitivity-tier model at best if <150 survive).

The extractor + this finding are the concrete result of the online search: the data is *partially
derivable but not to the standard a non-circular calibration requires* without one of the above.
