# Grouping & leakage rules — DRAFT (NOT FROZEN / NOT COMMITTED)

Related forms must stay in the SAME fold. Grouping key hierarchy (most-specific wins); a form inherits the
first cluster it belongs to, else falls back to its own singleton.

```
1. joined_fragment_cluster       (heading '+' joins — from Stage-4 lb_reference.json; 1,162 clusters)
2. same_underlying_record_cluster (duplicate/copy documents of one record)
3. scribal_copy_cluster          (same scribe + near-identical content)   [scribe channel empty in this dump — see decision #B]
4. formula_cluster               (identical opaque word-form sequence — Stage-4 FORMULA_CLUSTER; 9,432)
5. lemma_family                  (EVAL-ONLY key: same lemma)              [used to GROUP folds, never as a feature]
6. morphological_family          (inflectional siblings — EVAL-ONLY key)
7. orthographic_variant_cluster  (spelling variants of one form)
8. word_form_family              (same opaque form-id — Stage-4 REPEATS_FORM; 1,606 repeated across ≥2 docs)
9. document_series               (23 series — must not leak via trivially-unique templates)
```

Rules (binding for the future split, §VIII):
- Inflectional siblings and spelling variants **must not** straddle train/test when their relation is known.
- Joined fragments count as **one** document (never independent).
- Copied / formulaically duplicated entries stay grouped.
- A repeated lexical form across tablets is **one** lexical family (no seen-form leakage into the unseen-form
  test).
- Document-series identity must not leak through templates unique to one series.
- **`lemma_family` / `morphological_family` use the EVALUATION-ONLY key ONLY to define fold boundaries; they
  are never exposed to model code** (grouping is a leakage-control, not a feature).
