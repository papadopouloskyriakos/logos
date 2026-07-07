# B1 — Linear A Segmentation Representations

**Constitution v2.2** · seed `20260708` · deterministic, read-only corpus
**Builder:** `experiments/linear_a_relative_phonology/scripts/b1_build_segmentations.py`
**Outputs:** `experiments/linear_a_relative_phonology/data/segmentations/<name>.json` (+ `_SUMMARY.json`)

## Source & scope

Single source of truth: `corpus/silver/inscriptions_structured.json` — **1,341
inscriptions / 52 sites**, stream-tokenized as `word` (3,147) · `nl` (2,114) ·
`num` (1,276) · `div` (463) · `other/raw` (1,056). Total syllabic signs carried in
`word` tokens = **5,792**.

Every representation preserves **source provenance** (each unit carries
`inscription_id`, `site`, `support`, `period`) and **reversibility** (each unit
carries the stream span it came from — a `word_index` range and/or sign-position
range — so any sign traces back to `(inscription_id, word_index, position)`).
Reversibility was spot-checked for `SEG_GORILA_WORD`, `SEG_ENTRY`, and
`SEG_PROBABILISTIC_BOUNDARY` (reconstruction matches the source exactly).

**Non-circularity (Art. XII):** no phonetic value is ever a model input. The GORILA
word boundaries are used **only to grade** the unsupervised boundary detector, never
to train it.

## Results — unit counts + mean length (all REAL, measured)

| Representation | Units | Mean length (signs) | Total signs |
|---|---:|---:|---:|
| SEG_DIPLOMATIC | 1,341 | 4.3192 | 5,792 |
| SEG_GORILA_WORD | 3,147 | 1.8405 | 5,792 |
| SEG_INSCRIPTION_CONTEXT | 1,341 | 4.3192 | 5,792 |
| SEG_ROW | 2,697 | 2.1476 | 5,792 |
| SEG_ENTRY | 1,068 | 2.2491 | 2,402 |
| SEG_FORMULA | 1,642 | 2.0646 | 3,390 |
| SEG_PROBABILISTIC_BOUNDARY | 3,526 | 1.4376 | 5,069 |
| SEG_MULTI_SCALE | 1,341 | 4.3192 | 5,792 |

`SEG_GORILA_WORD` reproduces the campaign spec exactly (3,147 units, mean 1.84).

## Representation definitions

- **SEG_DIPLOMATIC** — raw inscription sign stream; one unit per inscription
  (`rec.signs`, subscripts preserved as transcribed). The faithful diplomatic edition.
- **SEG_GORILA_WORD** — GORILA word units = the stream `word` tokens. The natural
  short unit (mean 1.84 signs); provenance `word_index` + `stream_index`.
- **SEG_INSCRIPTION_CONTEXT** — whole inscription as one co-occurrence context unit.
  Same sign membership as DIPLOMATIC but role differs: it attaches document context
  (`n_words`, `n_numerals`, numeral list, `n_rows`) for whole-document analysis.
- **SEG_ROW** — line/row units split at `nl` tokens; each row records its word signs
  and any numerals. 2,697 rows across 1,341 inscriptions (mean 2.01 rows/inscription).
- **SEG_ENTRY** — administrative entry = a run of word signs **closed by a numeral**
  (commodity/personnel + quantity). 1,068 entries carrying the recorded numeral value.
- **SEG_FORMULA** — formula-carrier segments = **numeral-free word runs** (the
  non-accounting text: libation formulas, labels, headings). Mechanical complement of
  ENTRY. **ENTRY (2,402) + FORMULA (3,390) = 5,792**, an exact partition of the
  word-signs. 1,080 / 1,642 formula units recur across ≥2 inscriptions (annotated,
  not used in the definition).
- **SEG_PROBABILISTIC_BOUNDARY** — per-position boundary probability from an
  unsupervised **order-1 branching-entropy** model (Jin & Tanaka-Ishii style): score
  at each inter-sign gap = mean of right-branching entropy after the left sign and
  left-branching entropy before the right sign, min-max normalized to [0,1]. Segments
  are induced by cutting where prob > the corpus-mean threshold (0.42706 normalized).
  Each inscription stores its full `boundary_prob` vector (length = signs − 1) for
  reversibility. Domain = 618 inscriptions with ≥2 signs (5,069 signs); the 723 signs
  in single-sign inscriptions have no gap to score and are excluded.
- **SEG_MULTI_SCALE** — nested word / entry / inscription hierarchy per inscription.
  Levels: 1,341 inscriptions ⊃ {1,068 entries + 1,642 formula runs} ⊃ 3,147 words ⊃
  5,792 signs; mean 1.187 words/entry.

## Unsupervised boundary detector — graded vs GORILA words (grading only)

The branching-entropy model's induced cuts, scored against GORILA word boundaries
(**used only to grade**):

| metric | value |
|---|---:|
| boundary precision | 0.3532 |
| boundary recall | 0.5687 |
| boundary F1 | 0.4357 |
| tp / fp / fn | 1027 / 1881 / 779 |

Reported as a descriptive property of the representation, not a claim — the detector
over-cuts (recall > precision), consistent with the campaign's known short-word
segmentation regime.

## Integrity checks (all pass)

- Sign conservation: DIPLOMATIC = INSCRIPTION_CONTEXT = GORILA_WORD = ROW =
  MULTI_SCALE = 5,792 signs.
- ENTRY + FORMULA = 5,792 (exact, disjoint partition of word-signs).
- PROB_BOUNDARY: each `boundary_prob` vector has length signs − 1; induced-segment
  signs (5,069) = signs in inscriptions with ≥2 signs.
- Reversibility reconstruction verified for GORILA_WORD, ENTRY, PROB_BOUNDARY.

## Files written

`data/segmentations/`: `SEG_DIPLOMATIC.json`, `SEG_GORILA_WORD.json`,
`SEG_INSCRIPTION_CONTEXT.json`, `SEG_ROW.json`, `SEG_ENTRY.json`, `SEG_FORMULA.json`,
`SEG_PROBABILISTIC_BOUNDARY.json`, `SEG_MULTI_SCALE.json`, `_SUMMARY.json`.
