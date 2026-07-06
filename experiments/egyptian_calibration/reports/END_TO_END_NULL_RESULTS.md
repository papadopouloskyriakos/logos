# END_TO_END_NULL_RESULTS — §VIII

`results/gate.json`. Recovery under broken procedures vs the real model (LOO top-1):

| family | recovery |
|---|---|
| real M2 correspondence | **0.691** |
| 1 random pairing (score vs a random source) | 0.000 |
| 2 permuted model (egy↔sem link shuffled, refit) | 0.118 |
| 3 permissive M9 (all-substitutions-free) | 0.007 |

**Specificity confirmed:** the signal lives in the real correspondences (0.691) — a shuffled map recovers
only 0.118, a permissive all-match model only 0.007 (≈ chance). `specificity_ok = True`;
`permissive_excessive_fp = False` → the search architecture is NOT rejected. Model/threshold/family
choices are prespecified (frozen spec `3c56ed71`); best-of-model selection is covered by the permissive
null. No load-bearing adaptive choice sits outside the null.
