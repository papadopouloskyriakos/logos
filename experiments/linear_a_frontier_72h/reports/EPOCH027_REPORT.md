# EPOCH027 REPORT — INITIAL-vs-FINAL Cross-Site Generalization Asymmetry (LA)

**Layer:** L2/L3 (positional/structural only — no phonetic / meaning / reading inference)
**Task:** Synthesis of E023 (word-INITIAL A- generalizes across 9/10 sites) + E026 (word-FINAL RO concentrated at 1 site). Question: do word-INITIAL positional preferences generalize across independent LA sites MORE than word-FINAL ones, across the whole sign inventory?

## VERDICT (mechanical, from frozen rule): `MACHINERY_UNINFORMATIVE`

**No LA claim is made.** The frozen positive-control gate fired before any LA inference was permitted.

---

## 1. Setup (frozen at inspection)
- Qualifying signs: **42** signs with >=30 total occurrences across >=2-sign LA words.
- Qualifying sites: **10** sites with >=20 qualifying words (Haghia Triada, Zakros, Khania, Knossos, Phaistos, Palaikastro, Iouktas, Arkhalkhori, Syme, Tylissos).
- Power: NOT underpowered (>=6 signs, >=5 sites).
- Null: within-word uniform permutation (E024 machinery), extended symmetrically to the FINAL slot — P(last==S) = count_S_in_word / L, identical in distribution to the INITIAL null.
- Prereg + plan_hash frozen BEFORE any LA computation. `plan_hash.txt = 6acd1f16...  prereg.md`.

## 2. Positive Control — ran FIRST, FAILED (frozen gate)
The SAME per-sign init-vs-final cross-partition procedure was run on LB (DĀMOS >=2-sign wordforms) under a **seeded balanced 5-way partition (seed=7)**. LB is KNOWN to carry strong grammatical WORD-FINAL structure (inflectional endings). The frozen PC requirement: the machinery must report `mean(n_final_sig_parts) >= mean(n_init_sig_parts)` on LB.

| metric | value |
|---|---|
| LB signs tested (>=30 occ) | 69 |
| `lb_mean_init` | **1.565** |
| `lb_mean_final` | **1.246** |
| direction | **init > final** |
| `lb_diff(final − init)` | −0.319 |
| **PC verdict** | **FAILED** |

**Stability:** init>final holds for base seeds {0, 11, 99} and partition seeds {7, 42, 123}. Not a seed artifact.

**Honest mechanism of failure.** The within-word permutation null flags ANY positional concentration, not specifically grammatical-ending structure. LB has many highly position-specialized word-INITIAL syllabograms (e.g. A, DA, DI, KA, KU, ME clear all 5 folds at the initial slot with final=0) that clear the null in more folds than the final-specialized signs do (A2, DE, JA, JO, QE, RO, TA, TO, ... clear all 5 folds at the final slot with init=0). Both ends are strongly structured; the inventory-wide mean tilts slightly initial. Per the frozen rule, a method that reports initial-dominance on a final-dominated benchmark is biased → `MACHINERY_UNINFORMATIVE`.

## 3. LA asymmetry test — computed for transparency, NOT a valid claim
Because the PC gate fired, the LA numbers below are reported for the record only and carry **no inferential weight** under this protocol.

| metric | value |
|---|---|
| `mean_init` | 0.714 |
| `mean_final` | 0.619 |
| `diff (init − final)` | +0.095 |
| label-swap p (5000 draws, two-sided) | **0.836** |
| Wilcoxon signed-rank p | 0.599 |
| signs init>final | 14 |
| signs final>init | 16 |
| ties | 12 |

Even setting the failed PC aside, there is **no detectable positional asymmetry** in LA (p=0.84, near-symmetric sign counts). The per-sign table reproduces E023's A-initial signal (A: init_sig_sites=9, final_sig_sites=0) but that single sign does not generalize to an inventory-wide initial-vs-final asymmetry.

## 4. Bottom line (honest)
The disciplined answer to the EPOCH-027 question is: **we cannot tell, because the method failed its own positive control.** The within-word permutation null, applied uniformly across the whole sign inventory, manufactures slight initial-dominance even on Linear B — where word-final structure is known to dominate — so any LA initial-vs-final contrast it produces is uninterpretable. The LA raw numbers happen to show essentially no asymmetry (p=0.84), but that is not a valid claim under this protocol. The E023/E026 init-generalizes / final-local contrast should be re-examined under a position-symmetric null before any synthesis is attempted.

## 5. Outputs (exact PATH CONTRACT paths)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-027/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-027/plan_hash.txt` (6acd1f16...)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-027/machinery.py` (imports E024 permutation_null; __main__ self-check passes)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-027/result.json`
- `experiments/linear_a_frontier_72h/reports/EPOCH027_REPORT.md` (this file)
- `experiments/linear_a_frontier_72h/data/epoch_027/la_per_sign_persite.csv`, `lb_per_sign_perfold.csv`, `la_per_sign_summary.csv`

## 6. Non-circularity
Sign names reported as opaque tokens; no phonetic / sound / meaning / language / reading inference drawn. LB used as positive-control benchmark only (no reading transferred to LA). Verdict is mechanical from the frozen PC gate; the operator did not adjudicate. The PC fired honestly and the LA claim was suppressed accordingly.
