# EPOCH-020 — DEVIATIONS (append-only, Art. XVII)

- 2026-07-08: caught and fixed a bug in `holm_survives_any` in
  `scripts/e020_allograph_adaptive_null.py` during the first execution attempt (killed before
  `result.json` was ever written, so this is a pre-result bugfix, not a correction to a published
  finding). The original implementation required ALL 60 signs in the family to individually clear
  their Holm-adjusted threshold before returning `True` (an "all survive" check), instead of the
  correct Holm step-down definition ("count ranks, in ascending-p order, that pass `p <= alpha/(n-rank)`
  before the first failure; ≥1 survivor ⇒ True"). This bug would have silently near-zeroed the
  per-sign Holm false-graduation-rate calibration (Step 3 and the Step 4 synthetic calibration), because
  requiring all 60 signs to pass simultaneously is an almost-impossible bar under any null. It did NOT
  affect the main verdict logic (`verdict_INV`), which used a separately (correctly) computed
  `n_inv_signs_surviving` count, not the buggy boolean. Fixed by extracting a single
  `holm_n_survivors()` helper and deriving `holm_survives_any()` from it; both real-data and
  leave-one-out calibration call sites now use the corrected helper. No other prereg deviation.
