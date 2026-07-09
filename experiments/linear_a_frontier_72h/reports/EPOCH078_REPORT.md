# EPOCH-078 REPORT — Glyph-Size Economy of Effort (cross-site, class-controlled)

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-078 (third SigLA spatial epoch)
**Layer:** L2 (pure structural graphic property; opaque sign IDs, no reading/meaning)
**Verdict (FROZEN MECHANICAL):** `GLYPH_SIZE_FREQUENCY_ECONOMY_CROSS_SITE`

## Question
Do more FREQUENT signs get drawn systematically SMALLER — a spatial economy-of-effort
compression, the glyph-modality analog of Zipf's law of abbreviation (frequent words are
shorter)? Tested globally, WITHIN a homogeneous sign class (AB syllabary vs class A), and
CROSS-SITE.

## Critical confound (load-bearing)
Rare signs may be pictorial LOGOGRAMS (intrinsically large). A raw size↔frequency slope
could then be the logogram/syllabogram size-complexity difference, not economy. Controlled
by testing the correlation WITHIN a homogeneous sign class. The economy verdict REQUIRES a
significant negative r within the AB syllabary (r_AB), not merely r_all.

## Metric (frozen)
- Per doc (>=4 non-divider glyphs): within-doc z-score of log bbox-area (removes per-photo scale).
- Per sign: mean within-doc z-size + corpus frequency; keep signs with freq>=8.
- r_all = Pearson corr(log freq, mean z-size). r<0 <=> economy.
- Class control: r_AB (AB syllabary), r_A (class A); AB vs A mean-size confound check.
- Null: frequency-label shuffle (permute {sign->log(freq)} over kept signs); one-sided perm p.

## Results

### Global
| n signs | r_all | perm p |
|---|---|---|
| 89 | **-0.351** | **0.0004** |

Significant negative economy globally.

### Class control (the load-bearing test)
| class | n | r | perm p |
|---|---|---|---|
| AB syllabary | 62 | **-0.317** | **0.005** |
| A (Linear-A-only) | 26 | -0.620 | (n/a) |

**Confound check:** mean z-size AB = 0.112 vs A = 0.081 — nearly equal. The size-frequency
slope is therefore NOT a class-level mean-size (logogram-complexity) artifact. The economy
effect SURVIVES within the homogeneous AB syllabary.

### Cross-site (sites with >=15 good docs)
| site | n signs | r | perm p | sig neg |
|---|---|---|---|---|
| Haghia Triada | 90 | **-0.376** | **0.0007** | ✓ |
| Khania | 29 | **-0.480** | **0.0033** | ✓ |
| Zakros | 35 | -0.178 | 0.155 | |
| Phaistos | 12 | -0.240 | 0.235 | |
| Knossos | 8 | +0.065 | 0.615 | |

**2/5 testable sites** significant negative (HT, Khania). Zakros/Phaistos trend negative but
underpowered; Knossos (n=8 signs) non-significant. (Mallia dropped below the >=15 good-doc
threshold after the >=4-non-divider filter.)

### Positive control (SYNTHETIC — gates verdict)
| verdict | detect p (median) | power_est | false-pos rate |
|---|---|---|---|
| **PASSED** | 0.002 | **1.0** | **0.04** (≤0.10) |

Detect power 1.0, false-positive rate 0.04 — machinery calibrated. Self-check: frequency-shuffle
null has E[r]≈0.009 on independent data.

## Frozen mechanical verdict
PC PASSED ✓ · r_all sig negative (p=0.0004) ✓ · r_AB sig negative (p=0.005, survives class control) ✓ · ≥2 sites sig negative (HT, Khania) ✓
→ **`GLYPH_SIZE_FREQUENCY_ECONOMY_CROSS_SITE`**

## Bottom line
There IS a cross-site glyph-size economy of effort in Linear A: more frequent signs are drawn
systematically smaller (r_all=-0.351), and — critically — this SURVIVES the sign-class control
(r_AB=-0.317 within the homogeneous AB syllabary, p=0.005), so it is a genuine within-class
frequency-compression effect, NOT the logogram/syllabogram size-complexity confound (AB and A
mean sizes are nearly equal). It replicates across the two largest sites (Haghia Triada, Khania).
This is the spatial analog of Zipf's law of abbreviation, established as a pure L2 structural
graphic property with no phonetic reading invoked.

## Non-circularity
glyph size = within-doc z-scored log bbox-area; frequency = corpus glyph count; class control
removes the logogram-complexity confound; frequency-label-shuffle null destroys the size↔frequency
association. size ⊥ frequency by construction. L2 only: opaque sign IDs, no reading/meaning.

## Outputs
- prereg.md, plan_hash.txt, machinery.py (with __main__ self-check), result.json — `epochs/EPOCH-078/`
- data dir — `data/epoch_078/`
