# CONTINUITY_MODEL_SPEC — §III (ADMINISTRATIVE_TOPONYM_CONTINUITY)

_Model `src/continuity/model.py`, analysis `admin-toponym-continuity-v1-2026-07-06`. A1–A5 results in
`data/results/ablations.json` (gitignored). Frozen input hashes verified before scoring._

## Match definition (no free mapping search)
A **match** between an LA candidate and an LB target is **exact sign-sequence identity** under a fixed
representation — no learned mapping, no best-of-many reassignment, no manual exceptions, no
target-specific edit, no post-result threshold change. Signs compare in **GORILA-number** space
(LA `AB##` and LB `*##` share the number). Layers:

| layer | representation | note |
|---|---|---|
| **A1** | exact raw sign-sequence identity (GORILA numbers) | primary |
| **A2** | via the frozen 77-sign tier-A A↔B equivalence map | ≡ A1 here (allographs not yet clustered) |
| **A3** | A2 + ≤1 wildcard **at** a damaged/composite-flagged position (same length) | prespecified tolerance |
| **A4** | projected LB **base** phonetic values (subscripts merged; homophone-tolerant) | LEVEL_3 ablation |
| **A5** | A4 with a **permuted/wrong** value map | phonetic-specificity control |

Interpretation hierarchy: `A1 ≥ A2 ≥ A3-only ≥ A4-only`. If `A4 ≈ A5` → no phonetic specificity. If
signal appears **only** under A4 → circularity risk high and the orthographic channel does not graduate.

## Engine validation (PC4 face-validity, DEVELOPMENT_FACE_VALIDITY_ONLY)
The one administrative known pair, **PA-I-TO ≡ pa-i-to**, matches under **A1–A4** and is broken by
**A5** (wrong values) — confirming (a) the pipeline can represent a real administrative continuity and
(b) the phonetic-specificity control is live. A true non-pair (PA-I-TO vs ku-ta-to) does not match.
PA-I-TO sets no threshold and counts toward no confirmatory total.

## Observed primary result (mechanical)
**PRIMARY_B (11) × EVALUATION (16): 0 matched pairs at every layer A1–A5.** Same for
PRIMARY_PLUS_SENSITIVITY (44) × EVALUATION: **0**. The internally-selected administrative TOPONYM_LIKE
LA forms are simply different strings from the independently-selected LB Cretan toponyms (e.g.
`AB08-AB51`, `AB01-AB27` vs `da-wo *01-*42`, `ku-ta-to *81-*59-*05`). No orthographic, equivalence-class,
tolerance, or phonetic layer produces a single continuity match.

This is the point estimate; whether **0** is *distinguishable from* or *consistent with* matched
end-to-end nulls — and whether the design has any power to detect implanted continuity at this
scarcity — is decided in §XI (nulls) and §XIII (power), not here.
