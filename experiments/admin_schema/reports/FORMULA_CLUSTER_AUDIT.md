# Formula-cluster audit (Stage 4.1 Correction 5)

**Construction (`formula_clustering.py`):** a formula-cluster id is `FC_<hash16>` of an entry's **opaque
word-form-id sequence** (B_SIGN composites). The clustering function **rejects any non-opaque input**
(transliteration, lemma, gloss, role, label) — blind by construction (`test_formula_cluster_blindness`).

**Distribution:** one FC membership node per entry-with-word-forms (9,432). `test_formula_cluster_fold_safety`
verifies **same id ⇔ same opaque form sequence** (no hash collisions) and reports the singleton rate (most
formulae are unique — clusters are sparse, NOT a dense semantic signal).

**Inputs used:** opaque sign/form sequence + entry structure only. **Never:** transliteration, Greek, lemma,
translation, gloss, semantic role, document interpretation, or any future gold label.

**Classification: `GROUPING_ONLY`** (default). A formula cluster is a **leakage-control fold key** (keep
identical-formula entries together across train/test), **not** a model-visible semantic shortcut. It is not
promoted to a transferable feature unless separately justified in a later stage.
