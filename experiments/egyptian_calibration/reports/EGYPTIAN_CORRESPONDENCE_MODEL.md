# EGYPTIAN_CORRESPONDENCE_MODEL — §VI (FITTED, FROZEN)

Model `src/calibration/model.py`, fit on the frozen corpus (152 tier-A/B, sha cc2c20d8). M2 = pooled
probabilistic P(egyptian-grapheme | semitic-consonant), add-α smoothed; scores candidate source
skeletons for an Egyptian rendering via best alignment.

## Learned correspondences (the systematic shifts — genuine, known Egyptology)
- **P(egy|l): r 26 / l 4 / n 2** — the well-known Egyptian **l→r** merger (no distinct /l/ grapheme).
- P(egy|ʾ): ꜣ 25 (aleph→ꜣ) · P(egy|h): h 23, ʿ 1 (occasional h→ʿayin) · P(egy|d): d 10, t 1, r 1 ·
  P(egy|ṣ): d 4, s 2 · P(egy|b): b 45, p 1 (occasional devoicing).
The model recovers real, published group-writing correspondences — not noise.
