# ADDENDUM-F1B — Exit-B CSA sufficiency sweep, scored under the F1a-frozen rule

**Status: COMPLETE — 2026-07-16 (append-only, Art. XVII). Classification: `NON_COMPARABLE`.**
LOGOS-2 stays CLOSED. F1a remains the binding confirmatory result. No closed conclusion,
the final-report verdicts, the E213 seal, or E208's de-authorization is altered by this addendum.

## What entered (receipt before inspection)
Import gate `import_f1b.py` hashed the bundle at `results/csa/exitB_sweep_20260716/` into
`IMPORT_RECEIPT.json` **before** scoring. Files + sha256:
- `recovery_by_benchmark.json` — `a1889126dbabf38888623b50dc931d16feeb7cfa2515a86bd7effbad24e08fef`
- `cells.tgz` (168 raw cells) — `44b21827801604b2c9eb51a2b0ba1af2029e7d9a118d5c3560e5d61f65d160f5`
- `T0_convergence.json` — `29258bb7305aaa631f9acdb532f3329f032a7a7bde238c1bc2fedd9cae6ba38b`
- `PROVENANCE.json` — `591335060889af344912455acc85acc9a7098073aece03ae64e8cd203713be7d`

Provenance: Exit-B CSA sufficiency sweep, 168/168 cells, completed 2026-07-15 on vast.ai
instance 44534071 (destroyed post-backup); byte-verified backup
`runtime/csa_sweep_vast_backup_20260716/` (173/173 files, tarball sha `b71fa4e9…`).

## Classification = `NON_COMPARABLE` (mechanical; `F1B_SCORED.json`)
The sweep cannot be placed on F1a's axis for **three** frozen-criteria reasons:
1. **Different recovery engine.** F1a scored with frequency-init EM (`scripts/decipher`, LIN-14);
   the sweep uses CSA (Tamburini 2025 `CSA_OptMatcher`). Different algorithms → recovery numbers
   are not interchangeable.
2. **Under-converged → lower bound.** The sweep ran at `steps=2000`. The T0 convergence control
   (verdict **`CONVERGENCE_ARTIFACT`**, Linear B full corpus still climbing to 37.3% at 6,000 steps)
   proves the syllabic recovery numbers are **censored lower bounds**, not converged values. A lower
   bound cannot serve as an independent replication *or* a converged confirmation of F1a's floor.
3. **Alphabetic-control dataset mismatch.** The sweep's alphabetic anchor is `ugaritic-noiseless`;
   F1a's was `uga-heb.no_speNL` (Ugaritic→Hebrew). Different datasets.

## Directional consistency (reported; does not change qualification)
Applying F1a's **frozen** per-dataset thresholds to the sweep's *best* recovery across **all** swept
sizes (an over-generous test):

| shared syllabic dataset | F1a threshold | sweep max @ any size | F1a full (EM) | reaches threshold? |
|---|---|---|---|---|
| Linear B → Greek | 0.50 | **0.106** | 0.000 | **no** |
| Cypriot → Greek | 0.35 | **0.318** | 0.005 | **no** |

**No shared syllabic benchmark reaches its F1a threshold at any swept size → `NOT_PROMOTED`.** The
sweep is therefore *directionally consistent* with F1a's `NOT_QUALIFIED_FOR_LINEAR_A` verdict, though
— being a lower bound under a different engine — it neither confirms nor contradicts it in a
comparable metric.

## Carried F1a context (per BOUNDARY.md)
UGA 0.486 carried a 34.4% dataset-inherent cognate-identity leak (adjudicated; discounted as
partly-trivial retrieval); LB 0.000; CSYL 0.005; false-graduation calibration 0/200, CP95 upper
0.0149 (≤ 0.02, certified). F1a status: `ALPHABETIC_REPLAY_ONLY_NOT_QUALIFIED_FOR_LINEAR_A`.

## Compliance
Art. XVII (append-only; this refines the E201 row, alters no closed verdict). Art. XII (a target is
never graded by the rule that created it — the sweep is the pseudo-decipherment learning-curve
instrument, scored here only against F1a's independent EM harness, not against itself). A recovery
lower bound below threshold neither promotes a claim nor converts the LOGOS-2 null into a positive.
**F1b resolved. LOGOS-2 remains closed.**
