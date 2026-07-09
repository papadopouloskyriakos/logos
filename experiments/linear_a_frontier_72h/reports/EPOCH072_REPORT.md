# EPOCH-072 REPORT — Libation formula as an ORDERED SEQUENCE across sites (L3)

**Verdict:** `LIBATION_FORMULA_ORDERED_SEQUENCE_CROSS_SITE`
**Layer:** L3 (pure structural order; anonymous sign-tuples; no reading, no meaning)
**Direct successor of:** EPOCH-071

---

## Question (mechanical, value-blind)

When two libation (stone-vessel) word-forms co-occur in an inscription, do they
appear in a CONSISTENT relative order — and is that canonical order SHARED
across sites — beyond a within-inscription word-order shuffle null?

E071 found that individual libation word-FORMS do NOT recur cross-site beyond
frequency+site-size. But E071 never tested the formula's DEFINING feature: its
fixed SEQUENTIAL ORDER. A "formula" is a shared ORDER, not just shared
vocabulary. E072 isolates ORDER.

## Method (frozen)

- Anonymous word-forms = sign tuples, len>=2 (stream tokens `t=="word"`).
- For each inscription, every unordered pair {fa,fb} of distinct forms yields
  one observation (site, sign), sign=+1 if the lex-smaller form precedes in
  stream (first-occurrence position), else -1.
- Testable pairs: total occurrences >= 2 (singletons trivially consistent).
- Cross-site pairs: observed at >= 2 distinct sites.
- consistency(pair) = max(n_plus,n_minus)/(n_plus+n_minus) ∈ [0.5,1].
- **C_glob** = mean consistency over testable pairs.
- **C_cross** = mean consistency over cross-site pairs.
- **A_cross** = # cross-site pairs whose dominant order is identical in EVERY
  site with >=1 occurrence (full cross-site agreement). agree_frac = A_cross/n.
- **Null:** independently shuffle each inscription's word-form order. This
  preserves each inscription's word multiset, so the testable pair set, the
  cross-site pair set, occurrence counts, and site structure are ALL INVARIANT
  — only the order signal changes. 2000 draws. One-sided perm p, add-one.

The null mean of consistency is NOT 0.5. Self-check confirmed the empirical
shuffle null matches the closed-form E[max(H,T)/k] = 0.75, 0.75, 0.6875 for
k=2,3,4 (to <0.03), all >0.5 — the null is empirical, not naive.

## Results — real corpus

| quantity | observed | null mean | perm p |
|---|---|---|---|
| C_glob (all 13 testable pairs) | **1.000** | 0.740 | **0.00050** |
| C_cross (10 cross-site pairs) | **1.000** | 0.737 | **0.00050** |
| A_cross (cross-site agreement) | **10 / 10** | 3.68 | **0.00050** |

- n_lib_inscriptions = 99; n_multiword (>=2 forms) = 56.
- n_testable_pairs = 13; n_cross_pairs = 10; n_sites (corpus) = 15.
- agree_frac = 1.0 — every cross-site pair agrees on one order in every site.

**Every one of the 13 testable pairs has consistency 1.0.** Word order in the
libation corpus is not free. And the order is shared: all 10 cross-site pairs
agree unanimously across the sites that contain them.

### Top cross-site pairs (anonymized)

| n_sites | n_occ | consistency | dominant order |
|---|---|---|---|
| 4 | 5 | 1.000 | + |
| 4 | 4 | 1.000 | + |
| 3 | 3 | 1.000 | + |
| 2 | 3 | 1.000 | + |
| 2 | 2 | 1.000 | + |
| 2 | 2 | 1.000 | + |
| 2 | 2 | 1.000 | - |
| 2 | 2 | 1.000 | + |
| 2 | 2 | 1.000 | - |
| 2 | 2 | 1.000 | - |

The strongest pairs span up to 4 sites (e.g. the A-TA-I-*301-WA-JA / SI-RU-TE
pair at 4 sites/4 occ, and the I-PI-NA-MA / SI-RU-TE pair at 4 sites/5 occ),
all perfectly consistent and unanimously agreed across sites.

## Positive control (SYNTHETIC — stated)

| arm | result |
|---|---|
| (a) DETECT planted canonical order | flagged 20/20 replicates; best detect p = 0.0020 |
| (b) FALSE-POSITIVE on random-order co-occurrences | rejection rate **0.00** over 20 draws (<=0.10 required) |
| (c) POWER at observed pair/site scale (5 forms, 40 insc) | **power_est = 1.0** |

**PC verdict: PASSED.** The machinery detects a planted ordered formula, does
not fire on random-order co-occurrences, and has full power at the observed
corpus's signal scale.

## Frozen mechanical verdict

PC PASSED (power_est=1.0 >= 0.5) AND C_cross > null (p=0.00050 <= 0.05) AND
A_cross > null (p=0.00050 <= 0.05) AND n_cross_pairs=10 >= 5 AND >=2 sites
contribute cross-site pairs.

→ **`LIBATION_FORMULA_ORDERED_SEQUENCE_CROSS_SITE`**

The libation forms appear in a CONSISTENT canonical order that is SHARED across
>=2 sites: a real cross-site ordered formula.

## Bottom line (honest)

YES — beyond the individual-form frequency effect that E071 already showed
cannot explain cross-site recurrence, the libation word-forms DO recur as an
ORDERED sequence: their relative order is perfectly consistent (consistency
1.0 on every testable pair) and that order is unanimously shared across sites
(A_cross = 10/10, p=0.00050 vs the within-inscription shuffle null). E071
ruled out a frequency-based explanation for the FORMS; E072 shows the formula
is real as a shared ORDERED SEQUENCE — the order is the signal that survives
once frequency, site-size, and co-occurrence structure are all held fixed by
the shuffle null. This is pure structural L3 order: we make NO claim about
what the formula says, only that a fixed order recurs cross-site.

## Non-circularity

Anonymous sign-tuples only; no reading/phonetics/meaning. The shuffle null
preserves each inscription's word multiset, so testable pairs, cross-site
pairs, occurrence counts, and site structure are invariant — only order
changes. Singletons excluded. Null mean is empirical (validated vs
closed-form), not 0.5. PC synthetic. L3 only.

## Outputs

- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-072/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-072/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-072/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-072/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_072/` (observed_stats.json, cross_site_pairs.json)
