# DECISION LOG — foundry

## 2026-07-08
- Campaign opened from main@6fd4f20 (v2.2). Isolation + append-only ledger verified; test baseline 411 passed.
  Motivated by the correct critique that the prior stopping theorem was overstated.
- **WP1 `PRIOR_THEOREM_OVERSTATED`.** Formal theorem: relabeling invariance holds only for identity-
  co-occurrence objectives O_id; objectives coupling internal relational structure (position/substitution/
  morphology) to value-space structure are invariant only under the subgroup preserving it (S_v x S_(n-v) for
  C/V), so internal evidence REDUCES the value equivalence classes. Empirical counterexample: word-initial-rate
  separates the 5 LB vowels AUC 0.744 p=0.035 (perm null, known truth); LA top-initial signs A(0.43)/I/U =
  vowel-corresponding, non-circular. Atlas of 13 channels (data/symmetry_breaking_atlas.json). Reframed target:
  WP3 recovers relative C/V+similarity+morphology to shrink equivalence classes; WP5 external anchors then
  fix fewer absolute values. Commit: _(this)_.
- **WP3.1 `CV_PARTITION_RECOVERED` (LB), with honest ablation.** Multi-feature C/V classifier: LB 7-fold CV AUC
  0.835 (perm p=0.01, 200 nulls). ABLATION: log_freq-only AUC 0.838 (a TYPOLOGICAL prior, not corpus
  structure); position-only AUC 0.67 (the genuine relabeling-variant corpus signal, modest+significant). So
  internal corpus structure breaks C/V symmetry weakly-but-significantly; the strong signal is the standard
  frequency prior. LA: ranks A/I top (vowel-corresponding) but LB probs don't calibrate (domain shift) -> LA
  ranking not partition. WP3 continues: LA-internal unsupervised clustering + substitutions (WP3.2) + morphology
  (WP3.4). No reading; no licence. Commit: _(this)_.
- **WP3 core complete (wf_cb02597a).** WP3.2 scribal substitution SIGNAL_VALIDATED on LB (same-C/V recovery
  1.39x null, z=7.07, AUC 0.714 — independent relational channel; signal in edge WEIGHT); LA underpowered
  (max weight 105 vs 303). WP3.1b unsupervised C/V clustering NULL (dominant axis != C/V; needs labels;
  fail-closed). WP3.4 morphology NULL (detector validated on LB 0.731 bits/word; LA gain = recurrence artifact).
  WP3.3 orthographic method validated on LB (p=0.0033) but NO_POWER on LA (unsegmented, 1 pair support>=3).
  SECOND CORRECTION: prior 'more corpus can't help (value-blind)' is REFUTED — the relative channels are
  validated on LB and would reach power on a larger/segmented LA corpus; C/V needs only a few seed labels
  (reduced anchor requirement). Obstacle = LA corpus power for relative channels, not a symmetry theorem.
  Commit: _(this)_.
