# EPOCH-050 REPORT — A-PREFIX CONTINUATION SELECTIVITY

**Campaign:** Linear A frontier-72h · **Epoch:** 050 · **Layer:** L2/L3
**Verdict (mechanical, frozen rule):** `A_PREFIX_SELECTIONAL_CROSS_SITE`
**Plan hash:** `8dbbaed0ee07e7b2416e5afa5360a463fefe07e7fc46d7778fe11b5738ab7d9c`

---

## 1. Question (discipline)

Is the word-initial sign token **`A`** SELECTIONAL over its continuation — i.e. is the entropy of
the 2nd-sign distribution among A-initial words (len≥2) significantly LOWER than a frequency-matched
null — or does `A` attach freely (no selection)?

**Non-circularity:** signs are ANONYMOUS. `A` denotes the word-initial sign token 'A' ONLY — no
phonetic value, no morpheme, no meaning. The metric is pure continuation-distribution structure
(L2/L3). LB is control-only. The verdict is a distributional statement, NOT a claim that `A` is a
morpheme or carries meaning.

## 2. Data (verified)

- Corpus: `corpus/silver/inscriptions_structured.json`; word tokens = `stream` entries with
  `t=='word'` and a `signs` list. A-initial word = `signs[0]=='A'` AND `len(signs)>=2`.
- **n A-initial words (len≥2) = 155.** Global 2nd-position pool n = 1369.
- Per-site A-initial (len≥2) counts ≥15: **Haghia Triada 41, Khania 20, Zakros 19** (3 testable).

## 3. Metric (frozen)

selectivity = observed **H_after_A** significantly LOWER than a bootstrap null (2nd-signs drawn from
the global 2nd-position distribution, same N=155, B=2000). One-sided p = P(null_H ≤ obs_H).
Cross-site: per site, null drawn from that site's own 2nd-position distribution. LOO on HT.

## 4. Positive Control (gates verdict) — PASSED

| Check | Result |
|---|---|
| DETECT (synthetic restricted-continuation prefix, K=5 signs) | obs_H=2.26 vs null_H=4.10, **p=0.0** → flagged selectional ✓ |
| False-positive rate (300 free-continuation synthetics) | **0.063** (≤ 0.10 threshold) ✓ |
| FP-rate stability across 6 seeds | 0.020, 0.057, 0.033, 0.073, 0.037, 0.053 — all ≤ 0.10 ✓ |
| LB sanity (LB 'A'-initial 2nd-sign entropy vs LB null) | H=5.15 vs null 5.56, p=0.0 (control-only; large-N positional structure) |

**PC verdict: PASSED.** The machinery detects restricted continuations and does not fire on free ones.

## 5. Global result

| Quantity | Value |
|---|---|
| n A-initial (len≥2) | 155 |
| **H_after_A** | **4.762 bits** |
| **null H (bootstrap)** | **5.312 bits** |
| **H_p (one-sided)** | **0.0** |
| distinct 2nd signs after A | 40 |
| top-10 continuation share | 58.7% |

**Top continuations after A (anonymous):** TA 20 (12.9%), DU 14 (9.0%), RA 10 (6.5%), RI 8, SI/SE/SA 7 each, KA/RE/PA 6 each.

→ A- does NOT attach freely: its 2nd-sign entropy is significantly below the frequency-matched null
(p=0.0). But the restriction is **moderate** — 40 distinct continuations, top-10 only 58.7%. This is
a distributional skew, not a closed-class stem paradigm.

## 6. Comparator initial signs

| Initial | n (len≥2) | H_2nd (bits) |
|---|---|---|
| KU | 89 | **3.064** |
| SI | 47 | 3.916 |
| I | 80 | 4.313 |
| KA | 46 | 4.436 |
| **A** | **155** | **4.762** |

**A- has the HIGHEST 2nd-sign entropy among common initials.** In absolute terms A- is the LEAST
restrictive common initial sign; its selectivity is visible only against the frequency-matched null,
not against other initials. KU is far more strongly selectional. A-'s "selection" is real but weak.

## 7. Cross-site (held-out)

| Site | n | H_after_A | null_H | p | restricted? |
|---|---|---|---|---|---|
| Haghia Triada | 41 | 3.759 | 4.471 | **0.0** | **yes (robust)** |
| Khania | 20 | 3.546 | 3.444 | 0.632 | **no** |
| Zakros | 19 | 3.366 | 3.743 | **0.0435** | **yes (borderline)** |

- **n sites testable = 3; n sites restricted = 2** (HT, Zakros).
- **Leave-one-site-out (exclude HT):** n=114, H_after_A=4.625 vs null 5.080, **p=0.0** → the global
  effect does NOT depend on HT alone.
- **Khania actively contradicts restriction** (p=0.632; its H_after_A is if anything ABOVE its site null).

## 8. Mechanical verdict (frozen rule)

- PC PASSED ✓
- Global H_after_A (4.762) significantly < null (5.312), p=0.0 ✓
- ≥2 sites significantly restricted (HT p=0.0, Zakros p=0.0435) ✓
- Survives leave-one-site-out (p=0.0) ✓

→ **`A_PREFIX_SELECTIONAL_CROSS_SITE`**

## 9. Honest bottom line / caveats

1. **The verdict is correct under the frozen rule but rests on a fragile leg.** Zakros sits at
   p≈0.039–0.0505 across alternative seeds — right at the 0.05 boundary. The cross-site claim is
   HT (rock-solid) + Zakros (borderline); Khania (n=20) is a genuine null.
2. **A-'s restriction is WEAK in absolute terms and the verdict label is narrow.** A- is the LEAST restrictive common initial sign: its 2nd-sign entropy (4.762 bits) is HIGHER than KU (3.064), SI (3.916), I (4.313), and KA (4.436). The frozen verdict label `A_PREFIX_SELECTIONAL_CROSS_SITE` is strictly a statement that A-'s 2nd-sign entropy is significantly below its FREQUENCY-MATCHED NULL only; it is NOT a claim that A- is strongly or tightly restrictive, and it does not rank A- against other initials. In absolute terms A- is weakly skewed, not paradigmatic; KU is far more strongly restricted.
3. **Only 3 sites are testable** (≥15 A-initial words). The cross-site bar is met at the lower edge
   of the preregistered power floor.
4. **This is a distributional (L2/L3) finding.** `A` is an anonymous positional token; continuation
   entropy is structure, NOT a morpheme/meaning claim. Whether the restricted continuation set
   reflects a grammatical prefix+stems, a lexical collocation routine, or a corpus-frequency artefact
   is not decided here.

## 10. Outputs

- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-050/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-050/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-050/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-050/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_050/` (distributions, per-site, bootstrap)
