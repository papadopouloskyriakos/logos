# Adaptive-choice inventory

Every choice in the discovery procedure that could manufacture an attractive result. The end-to-end
null (`END_TO_END_NULL_SPEC.md`) MUST replay every choice marked *searched* or *estimated*; anything
not replayed is a leak. Columns: **fixed** (set externally, not from LA), **est** (estimated from
independent calibration), **searched** (optimized over alternatives), **#alt** (rough alternative
count), **in-null** (must the null reproduce it?), **conf-ok** (permitted in confirmatory use).

| # | adaptive choice | fixed | est | searched | #alt | in-null | conf-ok |
|---|---|:-:|:-:|:-:|---:|:-:|:-:|
| 1 | external-anchor inclusion/exclusion | ✓ (prereg list) | | | ~2^n | ✓ | ✓ |
| 2 | alternative scholarly identifications (Siteia/Phaistos/Kydonia) | | | ✓ | 2–3/anchor | ✓ | tier-gated |
| 3 | temporal-tier admission (A–D) | ✓ | | | 4 | ✓ | ✓ |
| 4 | LA candidate-slot selection (which class/tier) | ✓ (frozen manifest) | | | — | ✓ | ✓ |
| 5 | confidence-tier threshold (B vs B+C) | | | ✓ | 2 | ✓ | ✓ |
| 6 | segmentation of LA forms | | ✓ | ✓ | few/form | ✓ | ✓ |
| 7 | transcription variant (damaged signs) | | ✓ | ✓ | few/form | ✓ | ✓ |
| 8 | projected sign-value variant | | ✓ | ✓ | per-sign | ✓ | ✓ |
| 9 | candidate mapping (sign→sound) | | | ✓✓ | huge | ✓ (**dominant FP driver**) | only if frozen |
| 10 | correspondence penalties/tolerance | | ✓ | ✓ | grid | ✓ | frozen from Hoch |
| 11 | model family | ✓ | | | small | ✓ | ✓ |
| 12 | hyperparameters | | | ✓ | grid | ✓ | ✓ |
| 13 | restart selection | | | ✓ | budget | ✓ | ✓ |
| 14 | best-score selection (best-of-search) | | | ✓✓ | budget | ✓ (**must be in null**) | held-out only |
| 15 | held-out split | ✓ (LOSO, seed) | | | — | ✓ | ✓ |
| 16 | candidate-language selection (E8) | | | ✓ | many | ✓ | equal-budget only |
| 17 | dictionary/lexicon selection (E8) | | | ✓ | many | ✓ | equal-budget |
| 18 | morphology rules (E8) | | ✓ | ✓ | — | ✓ | — |
| 19 | semantic-class filtering | ✓ (frozen manifest) | | | — | ✓ | ✓ |
| 20 | manual exclusions | **forbidden** outside the receipt | | | — | n/a | logged only |
| 21 | stopping rule | ✓ (prereg) | | | — | ✓ | ✓ |

**Load-bearing:** choices **9** (mapping search) and **14** (best-of-search) are the false-positive
engines — the power pilot shows in-sample best-of-search → FP≈1.0. Confirmatory use requires the
mapping **frozen** (choice 9 not searched; calibrated from Hoch) and evaluation **held-out** (choice
14 measured out-of-sample). No manual exclusion (20) may exist outside the machine-readable search
receipt.
