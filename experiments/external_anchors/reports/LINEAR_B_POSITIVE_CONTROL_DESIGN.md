# Linear-B positive control — module design (DESIGN, not executed)

Implements the protocol in `LINEAR_B_MATCHED_SCARCITY_PROTOCOL.md`. Shares the null machinery
(`src/nulls/nulllib.py`) and the same match/score path intended for Linear A.

- `src/positive_control/degrade.py` — the (PROVISIONAL) Egyptian-style distortion layer:
  `degrade(skeleton, params, rng)` applying vowel-loss/merger/epenthesis/omission/substitution/noise.
  Fixed params, never tuned to maximize recovery. Replaced by the frozen Hoch model once fit.
- `src/positive_control/harness.py` — builds matched-scarcity LB conditions (anchor grid 2–6,
  candidate pool, LOSO split), runs the held-out recover-vs-null comparison, emits receipts.
- `experiments/linear_b_positive_control/` — configs + a `run.py` (later, authorized pass only).
- `tests/test_positive_control_*.py` — degradation determinism + structure preservation + that the
  harness refuses to score without a receipt and without a held-out split.

**Gate:** the LA experiment does not proceed unless this control, at matched scarcity under a frozen
mapping, recovers LB→Greek materially above the null. Not executed in this pass.
