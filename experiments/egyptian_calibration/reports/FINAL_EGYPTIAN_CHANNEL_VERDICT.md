# FINAL_EGYPTIAN_CHANNEL_VERDICT — §XI

Mechanically derived by `src/calibration/verdict.py`; results `results/final_verdict.json`.

## Verdict
```
status                     = INCOMPLETE
egyptian_channel_readiness = NOT_READY
```

## Why INCOMPLETE (and explicitly NOT a disguised NO_POWER)
The gate cannot be scored past its **load-bearing input**: the non-Cretan Egyptian→foreign correspondence
calibration corpus **cannot be populated to standard** (§III/§IV). Hoch 1994's group-writing
transliteration is OCR-corrupt; Kilani 2019 is clean but the wrong layer (native vocalization); Kitchen
is discussion-only; Muchiki 1999 is unavailable. No fittable paired records exist, so **no model can be
fit, validated, or positive-controlled — power is not assessable.** `NO_POWER` presupposes a
fittable-but-weak corpus whose recovery/FP can be measured; none exists, so the honest verdict is a
source/extraction blocker (`INCOMPLETE`), not a negative dressed up to avoid the source problem.

## Milestone items (§XV)
1. **Isolation** — worktree `research/egyptian-calibration-gate` from `external-minoan-anchors@6d2e926`;
   main/paper/runtime/CSA sweep/closed LA↔LB channels untouched; light local CPU only.
2. **Source status** — REQ-01-secondary present (Cline&Stannish); REQ-01-primary NOT audited →
   Cretan toponyms confirmatory-ineligible. REQ-02: Hoch OCR-corrupt, Kilani wrong-layer, Muchiki absent.
3. **Calibration corpus** — 0 records (buildable=False); schema/tiers/rules frozen; coverage gap = entire corpus.
4. **Correspondence model** — spec frozen (M0–M9, sha `3c56ed71`), **not fitted** (no corpus).
5. **Positive control** — not executed (no frozen model).
6. **End-to-end null** — not executed.
7. **Uncertainty** — LOW/CENTRAL/HIGH tiers specified; not exercised.
8. **Power** — not assessable.
9. **Final verdict** — INCOMPLETE / NOT_READY.
10. **Recommendation** — **RESOLVE ONE EXACT SOURCE BLOCKER (REQ-02b)**: a machine-readable Hoch 1994
    dataset, OR a transliteration-aware hand-verified Hoch subset of ≥~150 entries, OR Muchiki 1999
    machine-readable. The frozen schema + model spec will then execute fit→control→null→power with no
    post-hoc freedom. No real Cretan/LA matching, preregistration, or sign-value claim was made.

## What is NOT claimed
No Linear A phonetic/lexical/language-family/decipherment verdict; no Cretan name correspondence; the
design is frozen and preserved, awaiting the one missing dataset.
