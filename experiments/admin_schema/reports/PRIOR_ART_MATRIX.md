# PRIOR-ART MATRIX (§II)

Audit of 20 works (workflow `wf_dcb6a179-216`, 3/4 clusters + synthesis; the novelty-boundary agent failed
StructuredOutput and was backfilled by hand — receipts in `data/prior_art/search_receipts/receipts.md`;
full register `data/prior_art/prior_art_register.csv`). Scored on the four axes that define the point of
novelty. **OVERLAP** requires all four.

| Work | blinded structure-only role/schema | cross-script transfer gate | uncertainty-aware | sealed held-out | distance |
|---|:--:|:--:|:--:|:--:|:--:|
| **Born, Monroe, Kelley & Sarkar 2025** — Disambiguating Numeral Sequences (Proto-Elamite) | ✅(numerals) | ❌ | ✅ | ✅ | **NEAR** |
| Born, Kelley et al. 2019 — Sign Clustering/Topic Extraction (Proto-Elamite) | ✅(sign-clusters) | ❌ | ❌ | ❌ | MODERATE |
| Helena Tomas — Linear A vs Linear B administrative systems | ❌(human, un-blinded) | ~(qualitative) | ❌ | ❌ | MODERATE |
| Corazza et al. 2021 — Linear A fraction values (INSCRIBE/Tamburini) | ❌(numeric, un-blinded) | ~(metrology) | ✅ | ❌ | MODERATE |
| Davis & Valério 2020 — HT 85 / HT 117 names-vs-designations | ❌(uses LB anthroponyms) | ~ | ❌ | ❌ | MODERATE |
| Luo, Cao & Barzilay 2019 — Neural Decipherment (min-cost flow) | ❌(**phonetic**, needs cognate lang) | ~(script→lang) | ~ | ❌ | MODERATE |
| Braović et al. 2024 — systematic review | ❌(survey) | — | — | — | MODERATE |
| Neural Representation Learning for Scribal Hands of Linear B 2021 | ❌(palaeography) | ❌ | ❌ | ✅ | MODERATE |
| "Contextual reconstruction of LA administrative meaning" (2026 coverage) | ❌(human concept) | ❌ | ❌ | ❌ | MODERATE |
| Papavassileiou et al. 2023/2024 — Linear B text restoration | ❌(restoration) | ❌ | ~ | ✅ | FAR |
| Luo et al. 2021 — undersegmented-script decipherment | ❌(phonetic) | ~ | ~ | ❌ | FAR |
| Schoep — Linear A administration | ❌ | ❌ | ❌ | ❌ | FAR |
| Salgarella 2020 — Aegean Linear Scripts / homomorphy | ❌(sign-level) | ~(graphic) | ❌ | ❌ | FAR |
| Salgarella, Bellinato & Ferrara 2025 — spice logograms | ❌(**reading** goal) | ~(graphic) | ❌ | ❌ | FAR |
| SigLA · DĀMOS · LiBER · PA-I-TO | data resources (used by logos) | — | ~(DĀMOS stores rival readings) | — | FAR |
| Sommerschield et al. — ML for Ancient Languages survey | ❌(survey) | — | — | — | FAR |

**Conjunction score across all 20: 0 works satisfy all four axes.**
- Blinding-as-ablation on a *decipherable* script = **0/20** (all use readings openly, or work on a script
  that is merely undeciphered so there are no known glosses to withhold).
- Structure-only admin **role/schema** induction — only Born 2019/2025 come close, but on numerals /
  sign-clusters, not administrative role or document-family schema.
- A **learned cross-script transfer gate** with hidden glosses = **0/20**.

## Method-primitive precedent (honest)

The individual primitives are established *outside* Aegean scripts: heterogeneous-graph document models
(Doc-GCN), factor graphs, CRF role labelling, held-out evaluation, and statistical hypothesis-space pruning
(Corazza 2021, Born 2025) all exist. The contribution is therefore **combinatorial** — a new *conjunction*
and *application*, not a new primitive. See `NOVELTY_BOUNDARY.md`.
