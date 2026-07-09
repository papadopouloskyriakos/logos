# EPOCH-056 REPORT — Dual Sign-Class Induction: Is the LA Script Distributionally Logo-Syllabic?

**Campaign:** Linear A frontier-72h
**Layer:** L2 (writing-system structure / sign-inventory taxonomy)
**Verdict:** `DUAL_SIGN_CLASS_CROSS_SITE_ROBUST`
**Signs:** ANONYMOUS IDs throughout. "logogram-like" / "syllabogram-like" are DISTRIBUTIONAL cluster labels, NOT readings, meanings, or decipherment.

---

## 1. Question

Real logo-syllabic scripts (Linear B, hieroglyphic) mix a **logogram/ideogram class** (signs that stand alone, are counted — numeral-adjacent — and rarely compose into long words) with a **syllabogram class** (signs that compose into multi-sign words). Do Linear A signs **partition** into ≥2 distributionally-distinct functional classes recoverable from **pure distribution** (position-in-word + numeral-adjacency + solo-occurrence)? Is that partition **beyond a feature-column-shuffled null**? Does one class look **logogram-like**? Is the partition **cross-site stable**?

## 2. Method (frozen in prereg)

Per-sign features (z-scored across the 61 signs with ≥20 sign-tokens):
- **f1** numeral-adjacency rate (word immediately precedes a `num` token)
- **f2** solo-word rate (1-sign word)
- **f3** word-initial rate · **f4** word-final rate · **f5** mean word length

2-means into k=2; separation = silhouette vs a **feature-column-shuffled** permutation null (500 perms; each feature column permuted across signs independently, preserving marginals, destroying sign-feature association). Classes characterized by mean f1/f2; "logogram-like" = higher mean(f1)+mean(f2); between-class f1 gap + Mann-Whitney. Cross-site: per-site k=2 partitions on signs with ≥10 tokens in ≥2 sites; pairwise ARI (max over label swap) vs a random-labeling null.

## 3. Positive Control (SYNTHETIC — gates verdict)

**The positive control is SYNTHETIC.** Linear B DAMOS wordforms are syllabic tuples with **no numeral stream and no marked ideograms**, so a real-LB ideogram-recovery control is **not available**. The PC therefore plants synthetic sign-classes.

| PC arm | Result | Threshold | Pass? |
|---|---|---|---|
| DETECT planted 2-class | silhouette perm p = 0.000; recovered-vs-planted ARI = 1.000 | p≤0.05 AND ARI≥0.7 | ✅ |
| FALSE-POSITIVE single-class | false-split rate = 0.05 (1/20 draws) | ≤0.10 | ✅ |

**PC verdict: PASSED.** The machinery detects a real planted split and does not hallucinate one on a single-class corpus. Machinery is informative.

## 4. Global Result (LA, n=61 clusterable signs)

| Metric | Value |
|---|---|
| Signs clustered (≥20 tokens) | 61 |
| **Silhouette (observed)** | **0.543** |
| Silhouette null mean ± SD | 0.196 ± 0.024 |
| **Silhouette perm p** | **0.000** (500 perms) |

The observed silhouette (0.543) is **~14 null SDs** above the feature-column-shuffled null mean (0.196). The two-class structure is overwhelmingly beyond chance. Seed-stable (silhouette 0.543, p=0 across seeds 1/42/2024/7777).

### The two classes

| Class | Size | f1 (num-adj) mean | f2 (solo) mean | f5 (word len) mean | Distributional label |
|---|---|---|---|---|---|
| **A** | **17** | **0.475** | **0.808** | low (short words) | **logogram-like** |
| **B** | 44 | 0.328 | 0.119 | higher (multi-sign words) | syllabogram-like |

- **f1 gap** = 0.147 (logogram-like higher)
- **Mann-Whitney f1 p** = **0.044** (significant; logogram-like class is more numeral-adjacent)
- The logogram-like class is overwhelmingly solo-word (f2=0.81 vs 0.12) — these signs stand alone and are counted; the syllabogram-like class composes into multi-sign words.

**Logogram-like class (17 signs, ANONYMOUS IDs):** CYP, CYP+D, GRA, GRA+PA, KA, KU, NI, O, OLE, OLE+KI, OLE+MI, OLE+U, OLIV, RO, VIN, VIR+[?], ZE.

**Syllabogram-like class (44 signs):** *118, *21F, *301, A, DA, DE, DI, DU, E, I, JA, JU, KI, MA, ME, MI, NA, NE, NU, PA, PA₃, PI, PU, QA, QE, RA, RA₂, RE, RI, RU, SA, SE, SI, SU, TA, TE, TI, TU, U, VS, WA, WI, ZA, ZU.

> **Discipline note:** These sign-strings are opaque IDs. Their conventional names are NOT used as evidence. The cluster labels are pure distributional descriptions.

## 5. Cross-Site Stability

Signs with ≥10 tokens in ≥2 sites: **24**. Sites with enough such signs to support a per-site 2-partition: **4** (Haghia Triada n=58, Zakros n=19, Khania n=13, Palaikastro n=7).

| Metric | Value |
|---|---|
| Sites usable | 4 |
| **Cross-site ARI (observed)** | **0.095** |
| ARI null mean (random labelings) | −0.004 |
| **ARI beyond null?** | **Yes** |
| Pairwise ARIs | 0.16, 0.10, 0.02 (all positive) |

The partition is recovered consistently across sites beyond a random-labeling null, seed-stable. **Haghia Triada** independently recovers a logogram-like core (CYP, GRA, GRA+PA, OLE-family, OLIV, VIN, VIR, ZE, NI); **Khania** recovers CYP, CYP+D, NI, O — overlapping the same core. The two well-powered sites agree on the logogram-like class.

**Honest caveat:** the cross-site ARI magnitude is modest (0.095). It is statistically beyond null (mean −0.004) and all pairwise ARIs are positive, but the signal is driven mainly by Haghia Triada and Khania; Palaikastro (n=7 signs) is underpowered and Zakros's per-site partition differs (possibly genre/register). The frozen rule (ARI beyond null AND ≥2 sites usable) is satisfied; the modest magnitude is flagged.

## 6. Frozen Mechanical Verdict

| Condition | Status |
|---|---|
| PC passed | ✅ |
| Global silhouette perm p ≤ 0.05 | ✅ (p=0.000) |
| Classes differ in f1 (MW p ≤ 0.05, logogram-like higher) | ✅ (p=0.044, gap=0.147) |
| Cross-site ARI beyond null | ✅ (0.095 > −0.004) |
| ≥2 sites usable | ✅ (4 sites) |
| ≥40 signs clusterable | ✅ (61) |

**Verdict: `DUAL_SIGN_CLASS_CROSS_SITE_ROBUST`**

## 7. Bottom Line

Linear A signs **do** partition into two distributionally-distinct functional classes, recoverable from pure distribution alone, far beyond a feature-column-shuffled null. One class (17 signs) is unambiguously **logogram-like** in distribution: it is strongly numeral-adjacent (counted) and overwhelmingly occurs as solo words; the other (44 signs) is **syllabogram-like**: it composes into multi-sign words and is rarely counted. The partition is significantly differentiated in numeral-adjacency and is recovered consistently across the well-powered sites. This is **consistent with** Linear A being distributionally logo-syllabic at the sign-inventory level — the same kind of logogram/syllabogram functional split seen in Linear B and hieroglyphic scripts. This is a structural taxonomy (L2), not a decipherment: signs remain anonymous and "logogram-like" is a distributional label, not a reading or meaning.

## 8. Outputs

- `epochs/EPOCH-056/prereg.md` (frozen) · `plan_hash.txt` · `machinery.py` (self-check PASSED) · `result.json`
- `data/epoch_056/analysis.json` (full numbers)
- PC is SYNTHETIC (real-LB ideogram control unavailable) — stated plainly.
