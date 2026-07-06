# Linear-B matched-scarcity positive-control protocol (DESIGN — not executed)

A full-corpus Linear B→Greek success proves nothing about a *sparse, uncertain* Linear A experiment.
This control asks: **can the SAME pipeline recover a real relationship when degraded to Linear A
scarcity?** If it can't, the LA test has no interpretive value and stops at `NO_POWER`.

## Source data
Linear B (Knossos) toponyms/anthroponyms with **known Greek referents** (ko-no-so=Knossos,
a-mi-ni-so=Amnisos, pa-i-to=Phaistos, ku-do-ni-ja=Kydonia, tu-ri-so=Tylissos, …) as the "external
anchors"; a set of Linear B administrative word-forms as the internal candidate pool. The relation
(LB sign→Greek value) is the known ground truth the pipeline must recover **without being told it**.

## Matched degradation (each dimension pinned to the prospective LA setup)
n usable anchors (**2–6**) · n internal candidates (≈ tier-B count) · sign inventory · token count ·
genre (administrative) · word-length distribution · **projected-value uncertainty** ·
**transcription uncertainty** · segmentation ambiguity · **external-representation distortion**
(Egyptian-style — provisional layer §below) · number of sites (leave-one-site-out) · train/held-out
split · mapping complexity · optimization budget · restart count. **Same code path + scoring as LA.**

## Egyptian-style degradation (PROVISIONAL — replace with the frozen Hoch model once fit)
Synthetic distortion: vowel loss/uncertainty, consonant merger, epenthesis, cluster simplification,
consonant omission, limited substitution, scribal noise. **Fixed synthetic parameters; NOT tuned to
maximize recovery.** Marked provisional until REQ-02 provides the empirical Egyptian→foreign
correspondence.

## Anchor-count grid
`2, 3, 4, 5, 6` (larger where data allow) — the same grid as the power envelope, so the two align.

## Procedure, metrics, thresholds
- **Held-out** recovery: mapping learned on training anchors must predict held-out-anchor Greek values.
- Metrics: held-out true-positive recovery vs the end-to-end null false-positive (same null families).
- **Success threshold (provisional):** held-out recovery materially exceeds the null at the same
  anchor count (gap and absolute FP to be set with the calibrated model), under a **frozen** mapping.
- **Failure interpretation:** if the pipeline cannot recover LB→Greek at matched scarcity, then a
  positive LA result would be uninterpretable → the LA test is `NO_POWER` / method-rejected, and is
  not run.

## Provisional assumptions awaiting REQ-02
The distortion layer and the mapping-flexibility/tolerance are provisional; the control must be
**re-run with the frozen Hoch correspondence model** before it can gate sensitivity. Until then, no
sensitivity claim is made (the power pilot already shows the *naive* in-sample design is FP≈1.0).

## Compute
Light Monte-Carlo over the grid × null families, local CPU, minutes; **no CSA/fence contention**.
Scaffold: `src/positive_control/` (degradation + harness stubs; shares `nulllib`); executed only in a
later authorized pass.

## Status
**Designed, not executed.** No sensitivity is claimed until the matched control is actually run and
passes under the frozen model. See `LINEAR_B_POSITIVE_CONTROL_DESIGN.md` for the module layout.
