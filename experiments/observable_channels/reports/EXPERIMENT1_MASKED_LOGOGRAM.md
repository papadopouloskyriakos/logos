# Experiment 1 — masked logogram recovery (first result)

Predict an entry's logogram (commodity channel) from its opaque word forms + structure, under **unseen
lexical-family (A12)** + cross-site controls. `results/masked_logogram.json`.

| | value |
|---|---|
| examples / train / **unseen-family test** | 3,711 / 2,312 / **457** |
| distinct logograms | 115 |
| baseline: frequency (majority logogram) | 0.175 |
| baseline: **document-series shortcut** | **0.630** |
| M_struct (structure only, strict A12) | 0.186 |
| M_sign (sub-lexical sign-bag NB, A12) | 0.182 |
| null (label shuffle) | 0.144 |
| min detectable over series (n=457) | 0.69 |
| **cross-site KN→non-KN: M_sign vs baseline** | **0.073 vs 0.115** (negative transfer) |

## Reading (honest)

- **The channel is well-powered** (457 unseen-family units — the pivot fixed the power problem that killed the
  label route).
- **But the predictive signal is a SHORTCUT, not transferable.** The commodity is largely determined by the
  **document series** (0.63) — Mycenaean scribes filed tablets by commodity into series. That is exactly the
  shortcut the gate requires us to remove.
- Under the mandatory controls (A12 unseen-family + **no series**), opaque word-form context barely beats the
  frequency baseline (0.182 vs 0.175), only weakly beats the null (0.144), and **transfers negatively across
  sites** (0.073 < 0.115). So **word-form identity/context does not transferably carry the commodity channel**
  — consistent with LB administration, where a given recipient/place receives different commodities in
  different documents; the *document*, not the *word*, fixes the commodity.

## Status against the gate

`OBSERVABLE_CHANNEL_READY` requires success on ≥2 channels, above baseline, above null, under unseen-family,
in ≥1 KN↔non-KN direction, and no series/site dependence. **Experiment 1 (masked logogram from word context)
does NOT meet this** — it fails the "beat the strongest baseline" and "cross-site" and "no series dependence"
conditions. This is one channel of the planned set; experiments 2–6 (quantity channel, accounting-closure,
template completion, cross-site invariance, O2+D8) remain — but the first result flags the same structural
pattern seen throughout the project: **the observable signal is real but lives in the document/series
structure, not in transferable opaque-word-form context.** To be tested, not assumed, on the other channels.
