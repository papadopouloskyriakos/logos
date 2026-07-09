# EPOCH-058 — Unsupervised Document Typology (L2, structural counts only)

**Layer:** L2 (pure document-structure statistics; structural counts only; NO sign values, NO readings, NO phonetics/meaning)
**Question:** Do Linear A inscriptions partition into recoverable structural DOCUMENT TYPES from their structural profile alone (length, numeral-density, divider/line-break density, mean word length)? Is that partition beyond a feature-shuffled null? Is it cross-site stable? Does it merely recover the archaeological 'support' label?

## Verdict (FROZEN, mechanical)

# **DOC_TYPOLOGY_SITE_LOCAL**

Structural document types ARE recoverable globally and beyond the null, and the typology is NOT merely the support label — but the structural partition does NOT transfer across sites. The doc-types are site-local conventions, not a pan-Cretan system.

## Non-circularity

Clustering features are STRUCTURAL COUNTS only: x1 n_content, x2 numeral density, x3 divider density, x4 line-break density, x5 mean word length (log1p then z-score). The 'support' label was NOT a clustering feature; it was used ONLY post-hoc to compute ARI. No sign values, readings, phonetics, or meanings were used. L2 only.

## Data inspection

- Usable inscriptions (>=2 content tokens): **n = 465** (of 1341).
- Feature medians: n_content=5.0, num_dens=0.33, div_dens=0.00, nl_dens=0.54, mean_wlen=1.79.
- Support (usable): Tablet 309, Stone vessel 75, Roundel 22, others small.
- Sites with >=25 usable: Haghia Triada 197, Khania 80, Zakros 39, Phaistos 27, Knossos 25 → **5 sites usable**; site pair for cross-site test = (Haghia Triada, Khania).

## Positive control (gates verdict) — PASSED

| test | result |
|---|---|
| DETECT: 3-type synthetic recovery, silhouette perm p | **0.005** (≤0.05) |
| DETECT: ARI vs planted labels | **1.00** (≥0.6) |
| FALSE-POSITIVE: single-type spurious-structure rate (20 draws) | **0.10** (≤0.10) |
| **pc_verdict** | **PASSED** |

Machinery self-check (recovers planted 3-type; does not split single-type) also passed.

## LA main results

### GLOBAL typology
- chosen **k = 2** (silhouettes: k2=0.345, k3=0.284, k4=0.312)
- **silhouette = 0.345**, **perm p = 0.002** (500 per-column-shuffle perms; null mean=0.204, null max=0.220) → **beyond null**
- cluster sizes: [337, 128]
- cluster profiles (raw centroids):
  - cluster A (n=337): n_content≈9.4, num_dens≈0.40, div_dens≈0.07, nl_dens≈0.71, mean_wlen≈1.7 → longer, numeral-dense, short-word documents
  - cluster B (n=128): n_content≈3.1, num_dens≈0.02, div_dens≈0.34, nl_dens≈0.38, mean_wlen≈2.7 → short, divider/line-break-heavy, longer-word documents

### SUPPORT alignment
- **support-ARI = 0.39** (< 0.5) → the induced typology is NOT merely the archaeological support label.

### CROSS-SITE stability — FAILS
- Train k=2 typology on Haghia Triada (n=197), apply to Khania (n=80), compare to Khania's own induced k=2 labels.
- **trainA→applyB ARI = −0.10**; null (label-permutation) mean=0.002, 95th pct=0.10, max=0.21 → **NOT beyond null** (perm p=1.0).
- The two sites partition differently:
  - HT clusters: long-numeral-heavy (n_content≈14.4, num_dens≈0.42) vs short (n_content≈3.4).
  - Khania clusters: both short; split by numeral density and word length (num_dens 0.38 vs 0.0; mean_wlen 1.4 vs 1.6).

## Mechanical verdict trace

- PC PASSED ✓
- global silhouette perm p = 0.002 ≤ 0.05 ✓ (clustering beyond null)
- cross-site train/apply ARI beyond null? **NO** ✗
- → rule: "DOC_TYPOLOGY_SITE_LOCAL iff clustering beyond null BUT cross-site train/apply ARI NOT beyond null" → **DOC_TYPOLOGY_SITE_LOCAL**

## Bottom line

There IS an intrinsic structural document typology in Linear A — the inscriptions split into two recoverable structural types (long/numeral-dense vs short/divider-heavy) at a level beyond chance, and that split is not just a relabeling of the physical support. But it is **site-local**: the same structural types do not recur across Haghia Triada and Khania. The structural "document types" reflect local scribal/functional conventions at each site rather than a shared pan-Cretan document-type system. This is honestly informative: structure carries real but non-transferable signal.

## Outputs

- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-058/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-058/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-058/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-058/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_058/cluster_assignments.json`, `null_summary.json`
