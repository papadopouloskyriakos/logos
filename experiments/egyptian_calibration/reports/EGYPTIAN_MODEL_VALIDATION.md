# EGYPTIAN_MODEL_VALIDATION — §VI

`src/calibration/validation.py`; results `data/results/model_validation.json`. Leave-one-out recovery
of the source skeleton from the Egyptian rendering (candidate pool 149 distinct roots).

| model | top-1 | top-5 | MRR |
|---|---|---|---|
| **M2 correspondence** | **0.691** | **0.855** | **0.753** |
| M0 identity | 0.434 | 0.750 | 0.562 |
| M1 edit-distance | 0.434 | 0.750 | 0.562 |

**M2 materially beats both baselines** (+0.26 top-1) — it recovers the systematic-shift cases (l→r etc.)
that identity/edit-distance penalise. Leave-one-family-out (train on other families, test held-out):
NW Semitic 0.767, South Semitic 0.667, cross-Semitic 0.602; East Semitic too sparse → SUBGROUP_NO_POWER
(correctly flagged, not forced). **Acceptance gate: PASS** (beats baselines on held-out; top-1 > 0.3).
