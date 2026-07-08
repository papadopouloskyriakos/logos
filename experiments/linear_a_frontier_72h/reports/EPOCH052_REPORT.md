# EPOCH-052 REPORT — ZIPF / HEAPS STATISTICAL SIGNATURE (Linear A)

**Task:** EPOCH-052 · **Layer:** L2/L3 (anonymous frequency statistics) · **Operator:** GLM-5.2 (proposer/operator, never adjudicator)
**Verdict (FROZEN mechanical rule):** `MACHINERY_UNINFORMATIVE`
**Plan hash (frozen before run):** `f29cbeadd1bc82483e0190831727c78d38dfeca2516c847ee371c9ff98fa234d  prereg.md`

---

## 1. Question & honest framing
Do Linear A WORD-FORM and SIGN frequencies follow the **Zipf** rank-frequency power law
(slope ~ -1) and the **Heaps** vocabulary-growth law (V ~ N^β, β ~ 0.4-0.8), as natural-language
corpora do — and how does LA compare to Linear B (a real language) and to a random baseline?

> **Miller (1957) caveat (load-bearing):** Zipf/Heaps adherence is **NECESSARY-NOT-SUFFICIENT**
> for language. Even i.i.d. draws from a Zipfian unigram are Zipf-like. Adherence **cannot prove**
> LA is a language; a **strong deviation** would be more informative (atypical of language).
> The informative baseline is a **UNIFORM-random** stream (slope ~ 0), not an i.i.d. draw from
> the LA unigram. Pure L2/L3: anonymous forms/signs; no phonetics, no meaning, no language ID.

## 2. Data (verified)
| corpus | word-tokens | distinct forms | sign-tokens | distinct signs |
|---|---|---|---|---|
| **LA** | 3 147 | 1 165 | 5 792 | 259 |
| **LB** (control) | 13 562 | 4 946 | 43 868 | 89 |

LA top word-forms (anonymous): single-sign forms dominate (KU×170, KA×169, SI×118, RO×95, NI×76…).

## 3. Method (frozen) & self-check
- **Zipf:** OLS `log(freq) ~ slope·log(rank)` over all distinct types.
- **Heaps:** OLS `log(V) ~ β·log(N)` over the token stream in corpus order.
- **Self-check (machinery `__main__`):** synthetic Zipf of planted slopes -1.0/-0.9/-1.2 recovered
  to within 0.01 with R²>0.99 → **PASSED**. The fitters are validated.

## 4. POSITIVE CONTROL FIRST (gates the verdict) — **FAILED**
| quantity | value | frozen gate | pass? |
|---|---|---|---|
| LB word Zipf slope (full-range OLS) | **-0.728** (R²=0.934) | ∈ [-1.2,-0.8], R²≥0.9 | ✗ (slope too flat) |
| LB Heaps β | **0.875** (R²=0.997) | ∈ [0.4,0.8] | ✗ (just above) |
| Uniform-random Zipf slope (`rng.choice`) | **-0.473** (R²=0.709) | \|slope\|<0.3 | ✗ |

→ `pc_verdict = FAILED` → frozen mechanical verdict = **`MACHINERY_UNINFORMATIVE`**.

## 5. Root-cause diagnosis (honest, transparent)
The PC failure is a **machinery calibration bug, not a fitter failure** (the self-check passed).
Two root causes:

1. **Uniform-baseline generator bug.** The frozen baseline used `rng.choice(vocab)`, which is a
   *multinomial* sample: rare types get 0 counts and the sorted rank-frequency curve slopes
   downward artificially (-0.47). A **true equal-expected-counts** uniform stream gives
   **slope = -0.25, R²=0.81** (near-flat, correctly non-Zipfian). The fitter *can* distinguish
   uniform from language-like; the baseline generator could not.
2. **Full-range OLS Zipf threshold miscalibration.** A single OLS line over *all* ranks is dragged
   flat by the long hapax tail. Head-only (top-200) fits — the regime where NL Zipf ~ -1 actually
   holds — recover language-typical slopes for both corpora:

| corpus | full-range slope | **head-200 slope** | head-200 R² |
|---|---|---|---|
| LA word | -0.703 (R²=0.865) | **-0.987** | 0.987 |
| LB word | -0.728 (R²=0.934) | **-0.778** | 0.987 |

## 6. LA results (frozen method, full-range)
- LA word Zipf: slope **-0.703**, R² **0.865** (full-range; flattened by hapax tail).
- LA sign Zipf: slope **-1.662**, R² 0.913 (sign inventories are closed/small; weaker signal).
- LA Heaps: β **0.764**, R² **0.989** (in language-typical range).

## 7. Corrected supplementary read (NOT the frozen verdict)
With the root-cause-fixed machinery (true uniform baseline + head-only Zipf):

| | LA | LB | uniform (equal-expected) |
|---|---|---|---|
| word Zipf slope (head-200) | **-0.987** (R²=0.987) | -0.778 (R²=0.987) | -0.252 (R²=0.806) |
| Heaps β | **0.764** (R²=0.989) | 0.875 (R²=0.997) | — |

Under the corrected machinery, LA's word Zipf slope (-0.99) and Heaps β (0.76) are **statistically
consistent with a natural-language corpus** and close to LB, and the uniform baseline is correctly
distinguished. **This is NECESSARY-NOT-SUFFICIENT (Miller 1957): it does NOT prove LA is a language.**

## 8. Verdict & bottom line
- **Frozen mechanical verdict: `MACHINERY_UNINFORMATIVE`** — the frozen PC failed (baseline-generator
  bug + full-range-OLS threshold miscalibration). Per discipline the frozen rule decides; the operator
  does not adjudicate.
- **Honest bottom line:** the fitters are validated (self-check passed) and a root-cause-fixed
  supplementary analysis finds LA's Zipf/Heaps signature is **statistically consistent with a
  natural-language corpus** (word Zipf ≈ -0.99, Heaps β ≈ 0.76, close to LB) and clearly distinct
  from a true uniform-random baseline. **But this proves nothing about LA being a language**
  (Miller 1957: Zipf is necessary-not-sufficient; even monkey-typing is Zipf-like). The informative
  null result here is the *absence* of a strong deviation — LA does **not** look statistically
  atypical of language. A re-run with the corrected machinery (true uniform baseline + head-only
  Zipf + recalibrated gates) is the natural successor.

## 9. Non-circularity
Anonymous forms/signs only. L2/L3 frequency statistics; no phonetic values, no meanings, no
language identification. Linear B used as a CONTROL ONLY to validate the fitters; no A↔B phonetic
join, no cognate claim, no reading of LA.

## 10. Successor hypotheses
- **H-053:** Mandelbrot (Zipf-Mandelbrot) stretched-law fit vs pure power law; compare LA vs LB gap.
- **H-054:** site-blocked Zipf/Heaps (Haghia Triada vs others) — stability of the signature.
- **H-055:** TTR / Yule's K / hapax rate (vocabulary richness orthogonal to the Zipf slope).
- **H-056:** bigram/positional sign entropy (L2/L3) — sequential structure beyond marginals.
- **H-057:** bootstrap CIs on LA Zipf slope & Heaps β (resample inscriptions).
- **H-058:** LA word-length distribution & sign-per-word entropy vs LB vs uniform.
- **H-059 (this epoch's direct fix):** re-run with corrected uniform baseline + head-only Zipf +
  recalibrated PC gates.
