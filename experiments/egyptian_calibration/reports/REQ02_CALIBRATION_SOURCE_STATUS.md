# REQ02_CALIBRATION_SOURCE_STATUS — §III

The load-bearing input. A fittable model needs paired records: **(Egyptian group-writing spelling ↔
independently-known foreign source form)** with segment alignment, `egyptian_reading_confidence`, and
`source_form_confidence`.

- **Hoch 1994** — the correct corpus (~500 Semitic loanwords/names in group writing). Local scan sha
  `4df9bc09…`, 594 pp. Prose clean; **group-writing transliteration OCR-corrupt** → cannot extract the
  segment-aligned pairs to standard. Auto-parsing would bake OCR noise into the very false-positive
  calibration the gate depends on (forbidden).
- **Kilani 2019** — CC-BY, clean, sha `4ecff477…`. But calibrates the group-writing→**sound** layer from
  **native** Egyptian words via Coptic — NOT the Egyptian→**foreign** correspondence. Wrong layer.
- **Muchiki 1999** — the foreign-consonant-approximation layer for names/toponyms; **not acquired**.
- **TLA Late-Egyptian v19** (HF, CC-BY-SA) — Egyptian lexical corpus (native), not a foreign-correspondence
  paired set; not fetched; would not supply the foreign layer regardless.

**Status: the primary calibration manifest CANNOT be populated to standard.** Smallest sufficient unblock
(any ONE): a machine-readable Hoch dataset; OR a transliteration-aware, hand-verified Hoch subset of
≥~150 entries (a smaller subset is itself NO_POWER for calibration); OR Muchiki 1999 in machine-readable
form. See MATERIAL_REQUESTS.md.
