# RITUAL_NULL_RESULTS — §X

Results `data/results/ritual_nulls_power.json`.

| family | FP(≥1) / note |
|---|---|
| 1 random pairing | 0.005 |
| 2 freq-matched synthetic ritual | 0.008 |
| 3 length-matched synthetic targets | 0.010 |
| 4/5/6 formula/site/object-class shuffle | degenerate (not match features) → 0 |
| 7 matched non-ritual controls | 0.010 |
| 8 perturbed equivalence | 0.007 |
| 9 independently-constrained drift null | **none exists** (D3 inadmissible, §VIII) |
| **10 permissive best-of-edit (≤2)** | **0.9962** — 13 spurious matches/run |
| 11 known-pair selection penalty | 2 exact-representable known / 3 drift (unrecoverable) |
| 12 post-hoc selection penalty | nominal 0.008 → **bounded 0.016** (×2 channels tried) |
| **combined best-of-search** | **0.9963** (dominated by the permissive-edit family) |

**The wall:** exact matching is specific (~0.8–1.6% FP), but the edit tolerance required to span genuine
drift makes false positives essentially certain (99.6%). There is no admissible independent drift null.
