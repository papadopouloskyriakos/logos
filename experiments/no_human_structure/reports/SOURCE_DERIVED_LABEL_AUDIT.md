# Source-derived label audit (Stage 3)

Deterministic Linear B source-label corpus (NO LLM). Categories per the revised Stage-3 ontology.
Corpus: `data/source_labels/linear_b_source_labels.jsonl` (sha in `data/manifests/linear_b_source_labels.sha256`).

| category | count | notes |
|---|---|---|
| **REFERENCE_GOLD_A** | 66 | secure non-trivial content roles from cited indexes (PLACE 43 · HUMAN_OR_INSTITUTION 23) |
| WEAK_SILVER_B | 20 | operators/qualifiers (grammatical, bounded uncertainty) |
| STRUCTURAL_CONTROL_A (forms) | 7 | totalling forms (to-so…) — NOT load-bearing |
| STRUCTURAL_CONTROL_A (notation nodes) | 15,613 | numerals + logograms — NOT load-bearing |
| DISPUTED_OR_EXCLUDED | 0 | (cross-index conflicts resolved by priority) |

## REFERENCE_GOLD_A non-trivial — the load-bearing pool
- **66 form-types · 66 lexical families · 63 morphological families.**
- By role: **PLACE 43, HUMAN_OR_INSTITUTION 23** — only **2 of 4** load-bearing coarse classes;
  **OPERATOR_OR_RELATION and QUALIFIER are structurally absent** (they reach only WEAK_SILVER_B).
- By site: **KN 38 · non-KN 46**. Spread across ~21 document series.
- **Dependency:** every content-role label sits in ONE `SHARED_DECIPHERMENT` cluster (DĀMOS + V–C + DMic
  descend from one decipherment) — recorded as a single evidentiary lineage, not multiple independent votes.

## §II circular-evaluation firewall (enforced)
STRUCTURAL_CONTROL_A labels (numeral/logogram/total) are **excluded from the load-bearing semantic
evaluation** (test `test_source_labels_categories`): they may feed weak supervision + controls only. The
primary future eval uses REFERENCE_GOLD_A, `evidence_basis != STRUCTURAL_ONLY`, non-trivial, grouped by
lexical/morphological family.
