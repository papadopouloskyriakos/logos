# FINAL_CHANNEL_VERDICT — §X (ADMINISTRATIVE_TOPONYM_CONTINUITY)

_Mechanically derived by `src/continuity/verdict.py` from the committed result files; the model does
not decide the outcome. Results `data/results/final_verdict.json`._

## Verdict
```
status            = COMPLETE
channel_readiness = NO_POWER
circularity       = CIRCULARITY_LOW
```

## Why NO_POWER (triggers, from the numbers)
1. **The matched positive control for the realistic phenomenon cannot be recovered.** Genuine
   orthographic drift (e.g. LA `tu-ru-sa` → LB `tu-ri-so`) is unrecoverable under the no-free-mapping
   constraint (A1/A2/A3 all fail; A3 tolerates only *flagged transcription* uncertainty, not drift).
2. **Held-out administrative evaluation does not exceed the null** — 0 matches at every layer.
3. **Recovery of realistic continuity would require the forbidden flexible mapping search** (min
   detectable pairs: exact = 1, drifted = none).
4. **Insufficient independent administrative candidates** — 11 PRIMARY forms, 8 of them only 2 signs.
`P(NO_POWER)` for the realistic phenomenon ≈ **0.60** (3/5 known continuities drift/derive/vanish).

## The crucial nuance (not a bare null)
The design is **fully powered for EXACT administrative continuity** (min detectable = 1 pair; null FP
≈ 1.25%; positive controls PC1/PC3 recover implanted/true persistence at 100% with ~0 false positives)
— and it returned a **clean 0**. So: *there is no exact administrative Linear A ↔ Linear B toponym
continuity above the null.* What the channel **cannot** evaluate is the drift-inclusive hypothesis,
because spanning drift needs the free mapping the design forbids.

## Required final-report items (§XIII)
1. **Isolation/resources** — isolated worktree `research/la-lb-toponym-continuity`; `main`, the Egyptian
   branch, `paper/`, `runtime/`, the CSA sweep all untouched; light local CPU only (Monte-Carlo).
2. **Frozen input hashes** — LA packet `eb2bb293…`, LB packet `29e25d49…`, A↔B map `77de6684…`,
   ledger `9e832800…`; verified before scoring (anti-drift).
3. **Partition counts** — PRIMARY_B 11 / SENSITIVITY_C_ADDITIONAL 33 / NEGATIVE_CONTROL 21 /
   QUARANTINED 1 = 66 (mutually exclusive); B+C union 44; 16 EVALUATION targets.
4. **ARKH & duplicate dependence** — 3 ARKH → `AMBIGUOUS_ARKH`, reported separately (0 matches); unit =
   unique form (66 effective units, 254 raw attestations; 32 single-site clusters flagged).
5. **A1–A5** — PRIMARY×EVALUATION = 0 at every layer; B+C = 0. PA-I-TO face-validity: A1–A4 match, A5 breaks.
6. **PC1–PC4** — PC1 exact implant 100% recovery / 0 incidental FP; PC2 degraded recovered only by A3;
   PC3 LB-internal 11/11 self-persistence, 0 cross-FP; PC4 face-validity confirmed.
7. **Null FP** — 1.25% (freq-matched), 0.6–0.7% (others), real-data controls 0; combined best-of-search 3.21%.
8. **Held-out administrative** — 0 above null; ran once after freezes.
9. **Effective independent units** — 66 unique forms (no tablet multiplication).
10. **Power envelope** — exact: full power, min detectable 1; genuine drift: zero power.
11. **Genre-mismatch** — primary channel is administrative; known continuities are mostly ritual →
    the primary test evaluates a distinct hypothesis; ritual channel deferred (`EXPLORATORY_POSTHOC`).
12. **Circularity** — CIRCULARITY_LOW (all load-bearing components blind/independent; known-pair use and
    human exposure MANAGED, non-load-bearing).
13. **Status / readiness** — COMPLETE / NO_POWER.
14. **Single recommended next action** — **STOP the LA↔LB administrative channel as NO_POWER**; record
    the exact-continuity negative as the insurance-policy result; do **not** launch a prospective
    confirmatory scan. A drift-tolerant redesign (pre-registered, null-calibrated edit operations) or
    the ritual channel would each be a materially different design requiring a **new input-freeze review**.

## What is NOT claimed
No decipherment, no absolute phonetic sign value, no language-family claim, and **no** claim that the
five known continuities were independently rediscovered (they were used only as development diagnostics).
