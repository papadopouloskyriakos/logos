# Checkpoint — power curve + synthetic lab + WP6 (obstacle fully quantified)
- commits: 8be4827 (WP4/5) + _(this)_. experiment families now ~16 (quota 18). null realizations: PC 24×combos,
  synth >=200 ×curves, WP6 >=50 end-to-end (multi-family). sources ~6/60. anchors 115 (>=100).
- new constraints: LA needs ~2-5x corpus + word segmentation for the validated C/V/substitution channels
  (power curve 4.9x wordforms; synthetic 1.88x tokens + segmentation tax); methods validated on synthetic +
  reject wrong-language.
- best candidate: reduced-K value search on LA — AT_END_TO_END_NULL (beats order-shuffle z=8.5 but not
  wrong-language LB or random-prior; FWER 0.71). No value map.
- best null: wrong-language LB scores HIGHER than LA through the identical pipeline (the sharpest control).
- obstacle: quantified LA corpus/segmentation power; NOT value-blindness, NOT anchors, NOT method failure.
- licence: NOT_EARNED. remaining quotas: WP2 (segmentation lever + 2 encodings + shape), 3 candidate-language
  rounds (expected AT_END_TO_END_NULL), 5 sealed challenges (no surviving candidate to seal -> document), more
  sources, >=24 commits. status RUNNING.
