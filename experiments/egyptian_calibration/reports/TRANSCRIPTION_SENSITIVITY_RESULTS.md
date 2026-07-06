# TRANSCRIPTION_SENSITIVITY_RESULTS — §IX

`results/gate.json`. Egyptian-rendering uncertainty perturbs k consonants per anchor:

| tier | perturbation | top-1 | short recovery |
|---|---|---|---|
| LOW | none | 0.691 | 0.685 |
| CENTRAL | ~30% of anchors, 1 consonant | 0.586 | 0.577 |
| HIGH | every anchor, 1 consonant | 0.349 | 0.342 |

Recovery **degrades gracefully** and stays ≈ 50× the null (0.0067) even under HIGH uncertainty.
`verdict_reverses_under_uncertainty = False` — the readiness verdict is robust to plausible
transcription/sign-value uncertainty.
