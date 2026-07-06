# LINEAR_B_MATCHED_SCARCITY_RESULTS — §VII

`src/calibration/gate.py`; results `results/gate.json`. Tests whether the validated model retains
recovery at the intended Cretan-anchor scarcity (few, short anchors).

Recovery by anchor length (LOO top-1): **len2 0.818 · len3 0.638 · len4 0.864 · len5 1.0**.
Short-form recovery (len ≤ 4, matched to Cretan toponyms): **0.685**; per-anchor null 1/149 ≈ 0.0067.

| K anchors | expected recovered (real) | null P(≥1) | detectable |
|---|---|---|---|
| 2 | 1.37 | 0.013 | ✅ |
| 3 | 2.06 | 0.020 | ✅ |
| 4–6 | 2.7–4.1 | <0.04 | ✅ |

**Minimum detectable anchors = 2.** Even short forms recover ~0.68, far above the ~0.007 null.
