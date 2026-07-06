# EGYPTIAN_MODEL_BASELINE_COMPARISON — §VI

The frozen primary model (M2) is required to beat simple baselines on held-out non-Cretan data:
- vs **M0 identity** (reward exact Egyptian≈Semitic consonant identity): M2 top-1 0.691 > 0.434 ✓
- vs **M1 uniform edit distance**: M2 MRR 0.753 > 0.562 ✓
The gain comes entirely from the learned systematic correspondences (esp. l→r), which the identity/
edit-distance baselines cannot represent. A model that performed only in-sample, or only after pooling
incompatible item classes, would not pass — this one passes out-of-sample and per-family.
