# E204 metrology — stack freeze (runs ONLY because E204R2 passed; seal remains closed)

**Data (frozen):** `../E204R2_residual_canonicalization/CANONICAL_FRACTION_DATASET.csv`
(sha256 f97fc7e4…, 1385 dual-agreed records). Arithmetic docs: documents with ≥2 unflagged
integer-bearing entry records and one unflagged KU-RO total (uncertain/restored/damaged/anomaly
records excluded from constraints; sensitivity arms re-include restored-only).

**Variables:** one value v_s ∈ (0,1) per fraction letter observed in the dataset. Scaled-integer
encoding: v_s = k_s / B for base B; k_s ∈ 1..B-1. **Bases (frozen alternatives):**
B ∈ {60, 120, 240} (covers duodecimal/sexagesimal families and 1/16 at 240).

**Compositional rule (frozen base + alternative):** a fraction sequence is the SUM of its
letters (JE = v_J + v_E); alternative arm treats multi-letter sequences as ATOMIC values.
**Entry value:** integer + fraction value. **Arithmetic constraint:** per arithmetic doc,
Σ entries == KU-RO total (exact, integer-scaled). Soft arm: maximize #satisfied docs.

**Evidence components (kept separate; never merged silently):**
C_ARITH (constraints above) · C_OCC (occurrence statistics: frequency-rank prior — larger
values rarer; PRIOR only) · C_PALEO (compound-sign composition consistency) · C_TYPO
(unit-fraction preference prior) · C_OPT (simplicity/optimality objective: minimize Σ
denominators) · C_LBCONT (LB fraction-value import — UNLICENSED, off by default, conditional
arm only).

**Computations:** exact CP-SAT enumeration of feasible k-vectors per base (cap 10^6; else
bounds); component factorization; backbone + ROBUST RELATIONS (order relations v_a>v_b and
ratio relations v_a = m·v_b holding in ALL feasible solutions); ablations: LOO-doc, LOO-site,
LOO-sign(rare), LOO-constraint, compositional-alternative, base-alternative, +C_OCC/+C_TYPO/
+C_OPT arms, restored-inclusion arm. **Selection-aware null:** 200 matched artificial
notations (per-doc structure, letter frequencies, entry counts and totals preserved; letters
reassigned by seeded permutation of the letter→slot mapping within each doc set) run through
the ENTIRE pipeline; report how often a null notation yields (a) any feasible system, (b) as
many robust relations as observed; plus exact CP95 bounds. Multiplicity: relation family
Holm-corrected; MC p-values plus-one.

**Statuses:** L3_METROLOGICAL_CLASS_SUPPORTED (≥1 robust relation family survives ALL
ablations AND beats the null battery) | METROLOGICAL_RELATIONS_PARTIAL |
UNDERDETERMINED_AFTER_ABLATION | NULL_NOT_DISTINCTIVE | E204_INVALID. No phonetic value can
graduate from E204 under any outcome. Seeds: master 1336530913, prefix "E204M".
