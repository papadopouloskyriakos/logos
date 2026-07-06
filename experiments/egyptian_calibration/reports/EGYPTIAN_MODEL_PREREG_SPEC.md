# EGYPTIAN_MODEL_PREREG_SPEC — §V (FROZEN BEFORE FIT)

`configs/egyptian_model_freeze.json` sha `3c56ed71…` (`data/manifests/egyptian_model_freeze.sha256`).
Status: **SPEC_FROZEN_AWAITING_CORPUS** — specified before any data/validation is viewed, so that when a
fittable corpus arrives (REQ-02b) there is no post-hoc design freedom.

## Model families
M0 identity baseline · M1 weighted edit-distance baseline · M2 pooled probabilistic correspondence ·
M3 names+toponyms · M4 toponyms-only (if powered) · M5 period-matched · M6 genre-matched (if powered) ·
M7 high-confidence-only (tier A) · M8 sensitivity incl. tier-C · M9 permissive unconstrained (FP stress
test only). Sparse subgroup → `SUBGROUP_NO_POWER`, never a forced model.

## Frozen: features · L2 regularization (λ grid, CV) · grouped k-fold + leave-one-family/genre/period-out
· seeds (20260706) · acceptance thresholds (must beat M0/M1 on held-out; subgroup min n=30) · fallback
rules · baseline definitions. **No model-family or threshold change after positive-control results are
visible;** any later revision is a separately versioned exploratory design.
