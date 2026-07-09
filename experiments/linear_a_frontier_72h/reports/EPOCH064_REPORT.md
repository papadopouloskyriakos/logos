# EPOCH-064 REPORT — Is word-initial entropy concentration (prefixing morphology) cross-site robust?

**Layer:** L3 (typology of the Linear A writing system). **Anonymous sign IDs; positional entropy only; no phonetic value, reading, or meaning.**

## Question
E027 established GLOBALLY that the word-INITIAL sign position has LOWER entropy than the word-FINAL position (initial slot more concentrated / drawn from a more restricted inventory — the signature of a PREFIXING morphology; the A-prefix E022–E025 is one instance). E027 did NOT test whether this asymmetry generalizes across sites. **Does the initial<final entropy asymmetry hold in EACH site (a cross-site-robust typological property), or is it globally-driven / site-local?**

## Metric & null (frozen)
- **A = H(word-final sign) − H(word-initial sign)** over multi-sign words (len≥2). A>0 ⇔ initial MORE concentrated = prefix-consistent.
- **Null:** within EACH word, uniformly permute its sign order, then recompute A. Preserves each word's sign multiset + word-length distribution + per-site sample size; makes initial/final exchangeable (E[A]=0).
- ≥2000 shuffles; one-sided perm p (initial-concentration) + reversed p (final-concentration).

## Data
10 sites with ≥20 multi-sign words; global pooled n = 1369. (Haghia Triada 694, Zakros 132, Khania 120, Knossos 61, Phaistos 58, Palaikastro 57, Iouktas 34, Arkhalkhori 34, Syme 21, Tylissos 21.)

## Positive control (SYNTHETIC) — PASSED ✅
Gates the verdict.
- **DETECT-PREFIX** (restricted initial inventory + diverse finals): A=+3.25, perm p=0.001 → flagged initial-concentration. ✅
- **DETECT-SUFFIX** (restricted final inventory, direction check): A=−3.25, reversed p=0.001, initial-concentration p=1.0 → correctly flags REVERSED direction, not initial. ✅
- **FALSE-POSITIVE** (symmetric initial/final): rejection rate 0.067 over 30 draws (≤0.10). ✅
- Self-check: within-word-shuffle null mean(A) ≈ 0 on symmetric synthetics. ✅

## Global result
| metric | value |
|---|---|
| n_words | 1369 |
| A_obs | **+0.2227** bits |
| A_null_mean | +0.0015 |
| perm_p (initial-concentration) | **0.0005** |
| reversed_p (final-concentration) | 1.0 |

Global A is significantly positive: the word-initial slot is more concentrated than the word-final slot, replicating E027.

## Cross-site result
| Site | n | A_obs | perm_p | sig (A>0) |
|---|---:|---:|---:|:--|
| Haghia Triada | 694 | +0.2214 | 0.0010 | ✅ |
| Zakros | 132 | +0.0963 | 0.2254 | — |
| Khania | 120 | −0.0045 | 0.5047 | — |
| Knossos | 61 | +0.5191 | 0.0115 | ✅ |
| Phaistos | 58 | +0.3128 | 0.0555 | — |
| Palaikastro | 57 | +0.3094 | 0.0490 | ✅ |
| Iouktas | 34 | +0.8951 | 0.0010 | ✅ |
| Arkhalkhori | 34 | +0.4340 | 0.0450 | ✅ |
| Syme | 21 | −0.0419 | 0.5692 | — |
| Tylissos | 21 | +0.5121 | 0.0380 | ✅ |

- **6 of 10 sites** individually significant in the SAME direction (A>0): Haghia Triada, Knossos, Palaikastro, Iouktas, Arkhalkhori, Tylissos.
- 8 of 10 sites have A≥0; the two negative sites (Khania, Syme) are essentially null (perm p>0.5), not reversed.
- **No site shows a significant REVERSED (suffixing) outcome.**

## Leave-one-site-out (Haghia Triada)
Removing the dominant site HT (~51% of multi-sign words) leaves the asymmetry intact and slightly stronger:
- pooled-minus-HT n=675, A=**+0.3322**, null mean −0.0014, **perm p=0.0005**.
- The global result is NOT an artifact of one site's sample size.

## Frozen mechanical verdict
PC PASSED ∧ global A>0 significant (perm p=0.0005) ∧ ≥2 sites significant same-direction (6 sites, A>0) ∧ survives leave-one-site-out (pooled-minus-HT p=0.0005).

### **VERDICT: INITIAL_CONCENTRATION_CROSS_SITE_ROBUST**

## Bottom line
Yes — the word-initial entropy concentration (the prefix-consistent positional asymmetry of E027) is a **cross-site-robust typological property of the Linear A writing system**, not a globally-driven or site-local artifact. It holds globally (A=+0.22, p=0.0005), in 6 of 10 testable sites individually in the same direction, and survives removal of the dominant Haghia Triada assemblage. The initial sign slot is drawn from a more restricted inventory than the final slot across the Linear A corpus. (Anonymous signs, positional entropy only; no reading.)

## Outputs
- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-064/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-064/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-064/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-064/result.json`
- raw: `experiments/linear_a_frontier_72h/data/epoch_064/raw_results.json`
