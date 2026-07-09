# EPOCH-067 REPORT — How deep is word-initial concentration? Single prefix slot or depth-2?

**Campaign:** Linear A frontier-72h · **Layer:** L3 (morphological typology; L2/L3 anonymous-positional)
**Operator:** logos z.ai research worker (GLM-5.2) · **Discipline:** STRICT LOGOS (proposer/operator; mechanical verdict)

## Verdict (mechanical, frozen rule)

# **CONCENTRATION_DEPTH_2**

A second concentrated word-initial slot exists at position 1, beyond the position-0 prefix slot
established by E064. PC passed; A_0 and A_1 are both significant globally; A_1 replicates in ≥2 sites.

## Question

E064 showed word-INITIAL (position 0) sign entropy is significantly lower (more concentrated) than
word-final — a prefixing signature. **Does the concentration extend to position 1 (a SECOND
concentrated initial slot → depth-2 prefixing / "prefix-stacking"), or stop at position 0 (a SINGLE
prefix slot)?**

## Data (verified)

`corpus/silver/inscriptions_structured.json`, words with `len(signs) >= 3` (so positions 0,1,2 exist):
**n = 752**. Six sites with ≥30 such words: Haghia Triada 353, Zakros 76, Khania 46, Knossos 41,
Palaikastro 39, Phaistos 34. (≥2 testable → not underpowered.)

## Metric & null (frozen)

- `H_k` = Shannon entropy (bits) of the **anonymous** sign distribution at position k ∈ {0,1,2}.
- `A_k = E_null[H] − H_k`; `A_k > 0` ⇔ position k more concentrated than chance.
- **Null:** within each word, uniformly permute its sign order; recompute `H_k`. Positions are
  exchangeable under the null ⇒ `E[A_k] = 0` (controls sign-frequency + word-length + sample size).
- `perm p_k = frac(null A_k ≥ observed A_k)`, one-sided (concentration). 2000 shuffles.

## Positive control (SYNTHETIC — gates the verdict) — **PASSED**

| Condition | Expectation | Result |
|---|---|---|
| DETECT-DEPTH2 (pos0 & pos1 restricted) | A_0 AND A_1 flagged | A_0=3.163 p=0; A_1=3.162 p=0 ✓ |
| DETECT-SINGLE (only pos0 restricted) | A_0 flagged, A_1 NOT | A_0=3.565 p=0; A_1=−0.231 p=1.0 ✓ |
| FALSE-POSITIVE (all positions uniform) | rejection ≤ 0.10 over ≥20 draws | 2/20 = 0.10 ✓ |

Self-check (exchangeable synthetic corpus, 200 reps): mean `A` = [−0.0027, −0.0010, −0.0017] ≈ 0 ✓
The test discriminates depth-2 from single-slot and does not fire on uniform input.

## Global result (n=752, 2000 shuffles)

| Position | H_k (obs) | E_null[H] | A_k (bits) | perm p |
|---|---|---|---|---|
| 0 | 5.2722 | 5.6473 | **+0.3751** | 0.0000 |
| 1 | 5.4166 | 5.6496 | **+0.2331** | 0.0000 |
| 2 | 5.5201 | 5.6479 | **+0.1278** | 0.0005 |

A monotone concentration **gradient**: A_0 > A_1 > A_2, all significant. Concentration is strongest
at the word edge and decays inward — consistent with a prefix *zone* rather than a single isolated slot.

## Cross-site robustness of the pos1 slot (pos0 is E064-established)

| Site | n | A_1 | p_1 | sig |
|---|---|---|---|---|
| Haghia Triada | 353 | +0.0726 | 0.0785 | ns |
| Zakros | 76 | +0.3312 | 0.0015 | **SIG** |
| Khania | 46 | +0.1478 | 0.1710 | ns |
| Knossos | 41 | +0.1071 | 0.2215 | ns |
| Palaikastro | 39 | +0.4813 | 0.0040 | **SIG** |
| Phaistos | 34 | −0.0996 | 0.7770 | ns |

**n_sites_testable = 6, n_sites_A1_sig = 2** (Zakros, Palaikastro) — meets the frozen ≥2-site bar.
The signal is site-heterogeneous: the largest site (Haghia Triada) shows a weak same-direction
effect that does not reach significance, while two smaller sites show strong concentration.

## Honest bottom line

**Depth-2 concentration, not a single prefix slot.** Position 1 is significantly concentrated beyond
the within-word-shuffle null globally (A_1 = 0.233 bits, p = 0.0000) and replicates in 2 of 6 sites.
Combined with the monotone A_0 > A_1 > A_2 gradient, the structure is that of a *prefix zone* of at
least two concentrated slots, not a single isolated prefix position.

## Interpretive caveat (frozen, must be read with the verdict)

A significant pos1 concentration is **structurally ambiguous** between (a) a genuine SECOND prefix
morpheme (true prefix-stacking) and (b) the first prefix's **selectional restriction** on the
following sign (E050 found A- has a weak generic continuation restriction). At L2/L3 we report only
the structural fact — *pos1 is concentrated beyond the shuffle null* — and do **NOT** adjudicate
stacking-vs-selection. That adjudication requires a conditional/marginal transition-structure test
(suggested as E068).

## Non-circularity

Anonymous sign IDs only (no readings, no values, no meaning). Metric = positional Shannon entropy
exclusively; no n-gram models, no sign identities in the statistic. Within-word shuffle holds
sign-frequency + word-length + sample-size fixed, so `E[A_k]=0` by construction (self-check
confirmed). L2/L3-typology only. PC is synthetic and stated as such.

## Outputs

- `prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json` — `epochs/EPOCH-067/`
- `data/epoch_067/` — data dir
- This report — `reports/EPOCH067_REPORT.md`
