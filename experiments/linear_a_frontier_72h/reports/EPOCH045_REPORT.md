# EPOCH-045 REPORT — Accounting-Intensity: Numeral-Density as a Document-Class Discriminant

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-045 · **Layer:** L2/L3
**Operator:** logos z.ai research worker (GLM-5.2)
**Verdict (mechanical):** `ACCOUNTING_UNDERPOWERED`

---

## 1. Question

Do Linear A **document classes** (the `support` field) differ in **accounting intensity**,
operationalized as **numeral density** = (#num tokens) / (#word + #num tokens) per inscription
(content tokens only; `nl`/`div`/`other` ignored)? And does any difference **survive controlling
for SITE** (i.e. is it not a pure site artifact)?

Discipline (hard): token-composition structure only — no phonetics, no numeral-value arithmetic
(the token `v` field is never read; only the token TYPE `num` is counted), no meaning/reading.

## 2. Data

- Source: `corpus/silver/inscriptions_structured.json` (1341 inscriptions).
- **Qualifying** inscriptions (≥2 content tokens): **465 / 1341**.
- Support classes with ≥20 qualifying inscriptions: **Tablet (309), Stone vessel (75), Roundel (22)**.
- Sites with ≥2 support classes each ≥10 qualifying inscriptions: **1** (Haghia Triada: Tablet=178, Roundel=12).

The corpus is heavily site-skewed (Haghia Triada = 845/1341) and most sites are dominated by a
single support class — this drives the underpowered verdict.

## 3. Global result (pooled across sites)

| Support | n | mean density | median density |
|---|---:|---:|---:|
| Tablet | 309 | 0.360 | 0.400 |
| Stone vessel | 75 | 0.177 | 0.000 |
| Roundel | 22 | 0.061 | 0.000 |

**Kruskal-Wallis across the 3 supports: H = 64.36, p = 1.06 × 10⁻¹⁴.**

Document classes differ dramatically in accounting intensity in the pooled corpus. The ordering
(Tablet > Stone vessel > Roundel) is consistent with the accounting-vs-dedicatory intuition:
tablets are the most numeral-dense, roundels and stone vessels are numeral-sparse.

## 4. Positive Control (gates the verdict) — PASSED

- **DETECT** (planted density difference): p = 1.0 × 10⁻⁵⁰ ≪ 0.05. ✓
- **FALSE-POSITIVE** (two classes from the same distribution, 25 random splits): rejection rate = **0.040 ≤ 0.10**. ✓

The test is well-calibrated: it detects a real planted gap and does not over-reject under the null.
PC verdict: **PASSED**. (Stable across alternative seeds; the frozen seed 20240545 gives fp = 0.040.)

> Note on LB control: Linear B DAMOS lacks per-inscription `support`/doc-class metadata, so the
> planted/random doc-class density positive control was constructed on the LA corpus itself, as
> pre-registered.

## 5. Site-controlled test (the key held-out move)

The frozen rule requires **≥2 sites** each having ≥2 support classes with ≥10 qualifying
inscriptions, to claim a ROBUST site-controlled effect.

**Only 1 site qualifies:** Haghia Triada (Tablet = 178, Roundel = 12).

Within Haghia Triada:
- Mann-Whitney Tablet vs Roundel: **p = 3.4 × 10⁻⁸** (Tablet denser).
- Pooled within-site permutation (stratified by site, 2000 perms): **p = 5.0 × 10⁻⁴**.
- Direction: Tablet denser than Roundel — **consistent** with the global pattern.

This is strongly suggestive, but a single site cannot establish that the support effect is not a
site artifact. The frozen rule therefore returns **ACCOUNTING_UNDERPOWERED**.

## 6. Mechanical verdict

Applying the frozen decision tree:

1. PC PASSED? **Yes.**
2. Global Kruskal p ≤ 0.05? **Yes** (1.06e-14).
3. ≥2 testable sites (≥2 supports × ≥10 inscriptions)? **No — only 1.**

→ **`ACCOUNTING_UNDERPOWERED`**

The global signal is real and large, and the one testable site agrees with it, but the
site-controlled design lacks the statistical leverage (≥2 sites) required to rule out a site
confound under the pre-registered rule.

## 7. Honest bottom line

Document classes **do** differ in accounting intensity in the pooled Linear A corpus — tablets are
numeral-dense, roundels and stone vessels are numeral-sparse — and this is not a machinery artifact
(PC passed). But the corpus's extreme site-skew (Haghia Triada dominates) leaves only a single site
where a within-site support comparison is possible, so we **cannot** mechanically certify that the
effect survives controlling for site. The verdict is **ACCOUNTING_UNDERPOWERED**: the result is
suggestive and directionally consistent, not robust. A relaxed within-site threshold or a
hierarchical model (successor epochs E046–E048) is needed to settle the site-confound question.

## 8. Non-circularity

No phonetic, sound, meaning, or reading claims. No numeral-value arithmetic (the `v` field was
never read; only the token TYPE `num` was counted). Pure L2/L3 token-composition structure.
Linear B used only as a control reference. Verdict decided mechanically by the frozen rule.

## 9. Outputs

- `prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json` (epoch dir)
- `data/epoch_045/per_inscription_density.json`, `support_x_site.json`
- `reports/EPOCH045_REPORT.md` (this file)
