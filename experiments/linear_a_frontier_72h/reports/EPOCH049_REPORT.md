# EPOCH-049 REPORT — INSCRIPTION-LEVEL SIGN CO-OCCURRENCE (document-topic; L2/L3)

**Verdict (mechanical, frozen rule): `DOCUMENT_TOPIC_COOCCURRENCE_CROSS_SITE`**

Signs ANONYMOUS throughout. Co-occurrence is a distributional claim, NOT a topic/meaning/reading claim.

---

## 1. Question

Do certain signs co-occur *within the same inscription (document)* more than chance — evidence of
document-topic structure (e.g. related entries clustering in one account) — beyond within-word
adjacency (E029) and word-form identity (E032)? And is that structure robust across sites?

## 2. Data & discipline

- Source: `corpus/silver/inscriptions_structured.json`.
- Sign set of an inscription = set of distinct signs in its word tokens (`t=='word'`).
- Restricted to inscriptions with **≥2 distinct signs**: **614 inscriptions**, **253 distinct signs**.
- Sign-set size: mean 6.80, median 4, range 2–29.
- Sites with ≥30 such inscriptions (testable): **5** — Haghia Triada (229), Khania (107),
  Knossos (40), Phaistos (39), Zakros (37).
- Discipline: signs anonymous; L2/L3 only; LB control-only; prereg + plan_hash frozen before run;
  positive control first; mechanical verdict.

## 3. Frozen metric & null

- **cooc_score** = number of sign pairs (s,t) with co-occurrence count ≥ **5** AND hypergeometric
  **z ≥ 3** under an independent-placement per-pair null (E = df_s·df_t / N; hypergeometric variance).
- **Global null** = degree-preserving **curveball** bipartite shuffle of the sign × inscription
  incidence matrix — preserves each inscription's sign-set size and each sign's document frequency
  *exactly*. **600 draws**; one-sided p for "more structure than chance".

## 4. Positive control (gates verdict) — **PASSED**

| Test | Result | Gate |
|---|---|---|
| DETECT (planted topic blocks) | obs 46 vs null mean 23.48, **p = 0.0017** | ≤0.05 ✓ |
| FALSE-POSITIVE (degree-matched random matrices, 25 sets) | rate **0.08** | ≤0.10 ✓ |

Machinery is informative and not inflated by the degree-preserving null.

## 5. Global result

| | value |
|---|---|
| n inscriptions (≥2 signs) | 614 |
| cooc_score (observed) | **504** |
| null mean (degree-preserving) | **292.80** |
| one-sided p | **0.0017** |

Document-level sign co-occurrence structure is real and strong **after** controlling for sign
frequency and document size. The naive top pairs are dominated by high-frequency signs, but the
degree-preserving null already removes pure-frequency inflation; the residual over-representation
is genuine document-level clustering.

## 6. Cross-site (held-out)

| Site | n | cooc_score | null mean | p | sig |
|---|---|---|---|---|---|
| Haghia Triada | 229 | 181 | 75.12 | 0.0017 | ✓ |
| Khania | 107 | 10 | 2.29 | 0.0033 | ✓ |
| Knossos | 40 | 0 | 0.48 | 1.00 | — |
| Phaistos | 39 | 0 | 0.08 | 1.00 | — |
| Zakros | 37 | 5 | 6.69 | 0.78 | — |

- **Sites significant: 2 / 5** (HT, Khania).
- The three smaller sites show no significant structure — consistent with n-driven under-powering
  (cooc_score 0/0/5) rather than absence.
- **Held-out pair replication: 0.05** — the *specific* top pairs of the largest site (HT) do **not**
  replicate in pooled other sites; pair identities are largely HT-local.
- **Leave-one-site-out (drop HT): pooled-rest p = 0.0017** — the aggregate structure **survives**
  removing the dominant site, so document-level co-occurrence is a cross-site phenomenon even though
  exact pair identities differ by site.

## 7. Mechanical verdict

Rule: `DOCUMENT_TOPIC_COOCCURRENCE_CROSS_SITE` iff PC passed AND global sig AND ≥2 sites sig AND
(top-pairs replicate held-out OR survives LOO).

- PC passed ✓
- global cooc_score significant (p=0.0017) ✓
- ≥2 sites significant (HT, Khania) ✓
- held-out replication frac 0.05 (fails) **BUT** survives LOO (p=0.0017) ✓

→ **`DOCUMENT_TOPIC_COOCCURRENCE_CROSS_SITE`**.

## 8. Honest bottom line

There is genuine, frequency-controlled document-level sign co-occurrence structure in Linear A
(cooc_score 504 vs 292.8 expected, p=0.0017), it is detectable in the two largest sites, and the
aggregate signal survives dropping the dominant site. **However**, the *specific* co-occurring pairs
are largely site-local (held-out replication only 0.05), and three of five testable sites are
under-powered nulls. So: cross-site *structure* yes, cross-site *shared topic palette* — not
demonstrated at the pair level. This is a distributional finding about anonymous signs; it is NOT a
claim about topics, commodities, or meanings.

## 9. Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-049/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-049/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-049/machinery.py`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-049/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_049/global_null_distribution.json`
- `experiments/linear_a_frontier_72h/data/epoch_049/top_pairs_anonymous.json`
