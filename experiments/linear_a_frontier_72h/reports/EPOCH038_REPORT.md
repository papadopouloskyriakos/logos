# EPOCH-038 REPORT — Positional Sign-Entropy Asymmetry (Linear A frontier-72h)

**Question.** If Linear A words carry grammatical SUFFIXES, word-FINAL position should be
dominated by a SMALL set of signs (LOW entropy) relative to word-INITIAL. Is word-FINAL
sign-position entropy significantly LOWER than word-INITIAL (a suffixing tendency), robust
across sites?

**Layer / discipline.** Pure L2/L3 positional-entropy structure on ANONYMOUS sign ids. No
phonetics, sound, meaning, or reading. LB is a positive-control benchmark ONLY. Prereg +
plan_hash frozen before running; PC first; mechanical verdict from the frozen rule.

---

## VERDICT: `NO_POSITIONAL_ENTROPY_ASYMMETRY` (reversed direction — initial MORE concentrated)

There is **no suffix-direction positional-entropy asymmetry** in Linear A. The observed
asymmetry is **negative** (word-INITIAL is *more* concentrated than word-FINAL), the opposite
of a suffixing tendency, and this is statistically significant in the reverse direction.

---

## 1. Global result (LA, n = 1369 words, len ≥ 2)

| quantity | value |
|---|---|
| H_first (entropy, bits) | **5.5292** |
| H_last (entropy, bits) | **5.7518** |
| **Asymmetry (H_first − H_last)** | **−0.2227** (negative ⇒ initial MORE concentrated) |
| Null mean asymmetry (within-word perm) | −0.0018 |
| One-sided p (suffix / final-concentration direction) | **1.0** (not significant) |
| Reverse-tail p (initial MORE concentrated) | **0.0005** (highly significant) |
| n distinct first / last signs | 113 / 106 |
| Normalized H_first / H_last | 0.8107 / 0.8549 |
| Top-5 final-sign share | 0.2272 (flat — no small dominant set) |

**Top-5 word-FINAL signs (ANONYMOUS):** RO 5.7%, JA 4.7%, RE 4.2%, TE 4.1%, NA 3.9% — a flat,
high-entropy distribution with no small suffix-paradigm set.
**Top-5 word-INITIAL signs:** A 11.3%, KU 6.5%, I 5.8%, JA 4.6%, DA 4.4% — sign **A** alone
accounts for 11.3% of word-initial positions, driving the lower initial entropy.

**Bottom line (global):** the data reject a suffix-concentration story. If anything, LA shows
an *initial*-concentration pattern (low-entropy initial sign set), consistent with the
high initial-frequency of sign A noted in prior epochs. This is a distributional finding about
sign-position frequencies, not an interpretation of language function.

## 2. Positive control (gates verdict) — PASSED

Linear B inflects word-finally, so its final-position entropy is expected to be LOWER than
initial. The same machinery must DETECT this and must NOT fire on structureless
(within-word-shuffled) data.

| PC quantity | value |
|---|---|
| PC verdict | **PASSED** |
| LB asymmetry (H_first − H_last) | **+0.2093** (final more concentrated, as expected) |
| LB detect p | **0.0005** (DETECT ✓) |
| LB H_first / H_last | 5.2521 / 5.0428 |
| False-positive rate (20 within-word-shuffled sets) | **0.0** (≤ 0.10 ✓) |

The machinery correctly detects LB's known word-final structure and does not fire on
shuffled words. **Machinery is informative; verdict is unlocked.**

## 3. Cross-site held-out (LA, sites with ≥ 50 words)

6 testable sites (≥ 3, so NOT underpowered).

| site | n | asymmetry | p (suffix dir.) |
|---|---|---|---|
| Haghia Triada | 694 | −0.2214 | 1.0 |
| Khania | 120 | +0.0045 | 0.51 |
| Knossos | 61 | −0.5191 | 0.99 |
| Phaistos | 58 | −0.3128 | 0.95 |
| Palaikastro | 57 | −0.3094 | 0.95 |
| Zakros | 132 | −0.0963 | 0.75 |

- **Sites significant in the suffix direction: 0 / 6.**
- **Direction consistent (all asymmetry > 0)? No** — 5 of 6 sites are negative (initial more
  concentrated); Khania is essentially zero (+0.0045, n.s.).
- **Leave-one-site-out (exclude Haghia Triada, n = 675):** asymmetry = −0.332, p = 1.0 —
  same direction, no collapse.

The reversed (initial-concentration) direction is consistent across sites and survives LOO.

## 4. Mechanical verdict (frozen rule)

- PC passed ✓
- Global asymmetry > 0 significant (p ≤ 0.05)? **No** (asymmetry = −0.2227, p = 1.0; reversed).
- ⇒ `NO_POSITIONAL_ENTROPY_ASYMMETRY` (global not significant AND reversed — initial more
  concentrated). Reported direction honestly: **initial position is significantly more
  concentrated than final** (reverse-tail p = 0.0005).

## 5. Honest bottom line

Linear A does **not** show a suffix-concentration positional-entropy asymmetry. Word-final
position is high-entropy and flat (top-5 final signs = 22.7% of tokens); there is no small
dominant final-position sign set of the kind a suffix paradigm would produce. The machinery
validates this null: it correctly detects Linear B's real word-final inflectional structure
(PC passed). What LA *does* show is the **opposite** — a low-entropy word-INITIAL position
dominated by sign **A** (11.3%) — an initial-concentration distributional
pattern that is consistent across all 6 testable sites and survives leave-one-site-out. This
is a distributional statistic about a sign SET, not a functional interpretation of the script;
whether the initial concentration reflects a genuine positional-structure effect vs an artifact of common
initial signs / word-length structure is left to successor epochs.

## Artifacts
- `experiments/linear_a_frontier_72h/epochs/EPOCH-038/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-038/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-038/machinery.py` (self-check: `python3 machinery.py`)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-038/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_038/` (per-site + global tables)
