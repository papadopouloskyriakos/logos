# Power-analysis assumptions (PROVISIONAL)

The envelope in `TOPONYM_POWER_ENVELOPE.md` rests on the following, all flagged provisional and to be
replaced with calibrated values before any go/no-go.

## Fixed from real evidence
- **Candidate count `n_cand ≈ 11`** — the tier-B `TOPONYM_LIKE` count from the frozen Task-A manifest
  (44 including tier-C). Real, internal-only.
- **Anchor count grid `2–6`** — bounded above by the securely-identified Egyptian toponyms actually
  available (Knossos, Amnisos, Lyktos, tentatively Siteia): realistically **3–4**.

## PROVISIONAL (awaiting REQ-02 / edition detail)
- **Distortion model** — modelled here as Hamming tol 1 over abstract sound-slots with mapping
  flexibility 3 and a random per-sign mapping search (budget 300). The REAL model must be the
  **frozen Hoch-calibrated Egyptian→foreign correspondence** (consonant substitution/omission/merger,
  vowel-indicator reliability, group-writing), estimated on independent non-Cretan names and **frozen
  before matching** (REQ-02 satisfied → not yet fit). Freezing removes the mapping *search*, which is
  the dominant false-positive driver.
- **Skeleton length `La=3`** — pessimistic; real toponym group-writings are ~4–5 elements
  (`kA-n-yw-SA`), which reduces coincidental matches.
- **Sign-value uncertainty / segmentation ambiguity** — folded into the flexibility+tol proxy; to be
  parameterized from the projected-value reliability per sign (blocked in part by GORILA palaeographic
  variants).
- **Slot-classifier precision/recall** — the envelope uses the manifest as ground truth; a sensitivity
  sweep over classifier error (tier-B vs tier-C target sets) is required.

## Re-run trigger
Re-run the envelope with: (1) the **frozen** Hoch correspondence model (no search, `frozen=True`),
(2) real skeleton lengths, (3) the tier-B-only vs tier-B+C candidate sets, (4) transcription-variant
draws. Only the **held-out FP under the frozen model** is admissible as the design's operating
false-positive rate. If held-out FP stays ≳ 0.1 even under the frozen model, the verdict is
`NO_POWER` and no confirmatory run is warranted.
