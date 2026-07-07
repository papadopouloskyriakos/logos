# C2 — Paradigm prediction (Di Mino H5/H6) · PARADIGM slot → **REJECT**

**Prereg** DI_MINO_EXACT_CLAIM_V1 (sha `8b098a4c`) · **Constitution** v2.2 · **Seed** 20260708
**Generator** `scripts/C_morphology_audit.py` → `data/results/morphology.json` (§C2). Non-circular, sign-level.

## Method

Di Mino's paradigm is **derived from the target subset** `A-TA-I-*301-WA-JA` (11 copies) and stated as a
fixed morpheme template:

> **`[1cs A-] [tG TA-] [stem-V I-] [root *301-WA-JA]`**

We then apply that template **blind** to the 6 held-out, non-target, distinct position-1 invocation forms
and score, per form, whether each predicted constituent is present — affix order, the "invariant" stem
vowel, and the "invariant" root. A genuine paradigm holds its lexical core (the root) constant while the
affixes inflect; the template must therefore predict the omitted forms, not just re-describe the training
word.

## Per-form template compliance (held-out, leave-target-out)

| held-out form | 1cs `A-` | `TA` slot-2 | stem-V `I` | root `*301-WA-JA` | `A-TA-I` intact |
|---|:--:|:--:|:--:|:--:|:--:|
| A-TA-I-*301-WA-JA *(target, derivation)* | ✓ | ✓ | ✓ | ✓ | ✓ |
| A-TA-I-*301-WA-E | ✓ | ✓ | ✓ | **✗** | ✓ |
| A-TA-I-*301-DE-KA | ✓ | ✓ | ✓ | **✗** | ✓ |
| A-NA-TI-*301-WA-JA | ✓ | **✗** | **✗** | ✓ | **✗** |
| TA-NA-I-*301-U-TI-NU | **✗** | **✗** | ✓ | **✗** | **✗** |
| TA-NA-I-*301-TI | **✗** | **✗** | ✓ | **✗** | **✗** |
| JA-TA-I-*301-U-JA | **✗** | ✓* | ✓ | **✗** | **✗** |

*(`JA-TA-…` places `TA` in slot-2 by accident of the `JA-` onset; the claimed 1cs `A-` is absent.)*

## Held-out prediction rates (fraction of the 6 non-target forms)

| predicted-invariant constituent | held-out compliance |
|---|---|
| 1cs `A-` prefix present | **0.50** (3/6) |
| `TA` in slot-2 | 0.50 (3/6) |
| stem-vowel `I` before `*301` | 0.83 (5/6) |
| **root `*301-WA-JA` present** | **0.17 (1/6)** |
| whole `A-TA-I` prefix complex intact | 0.33 (2/6) |

## Reading — the template's "invariant" is its most variable part

The paradigm is **inverted relative to the claim**. In a real root-and-pattern paradigm the **root** is the
constant and the affixes vary; here the affixes (`A-` 50%, `A-TA-I` 33%) are *more* stable than the thing
labelled "root": **`*301-WA-JA` is present in only 1 of 6 held-out forms (0.17)** — the **least** invariant
constituent of the paradigm. The element that *does* recur across the paradigm is the stem juncture
**`I-*301` (0.83)** — which belongs to the following sign, i.e. Davis's `I-*301` stem, not to Di Mino's
`A-`/`TA-`/`I` affixes nor to his `*301-WA-JA` root.

## Affix-order / allowed–forbidden alternations

Di Mino's template asserts a rigid morpheme order `A > TA > I > root`. The held-out forms violate it three
ways the template forbids:

- **Prefix alternation** `A- ~ JA- ~ ∅`: `A-TA-I-…` (Iouktas etc.) vs `JA-TA-I-…` (Apodoulou) vs
  `TA-NA-I-…` (Psykhro, Iouktas). A fixed 1cs `A-` cannot alternate with `JA-` and then disappear.
- **Slot-2/3 reordering** `TA-I ~ NA-TI ~ NA-I`: `A-**TA-I**-*301` vs `A-**NA-TI**-*301` vs
  `TA-**NA-I**-*301`. The "tG stem + stem-vowel" pair is not a fixed ordered pair.
- **Root final radical unstable** `-WA-JA ~ -WA-E ~ -DE-KA ~ -U-JA ~ -U-TI-NU ~ -TI`: the material after
  `*301` — the claimed C₂C₃ — takes six different shapes. The triconsonantal skeleton is not conserved.

These are exactly the **regional/paradigmatic variants** H6 says the template should PREDICT; instead the
template mis-predicts every one of them below chance for its load-bearing root slot.

## Verdict

**PARADIGM = REJECT.** Derived from the target and applied to held-out forms, Di Mino's fixed template
predicts its own "invariant root" in only **1/6** omitted forms and cannot generate the observed
prefix/stem alternations. A minimal rival that treats `A-…-JA/-E` as edge inflection around an `I-*301`
stem (Davis/Thomas; C_ALTERNATIVE_ANALYSES) predicts the paradigm **5/6**. The paradigm evidence is
**against** the morpheme analysis, not for it — consistent with the segmentation (04) and circularity (02)
findings.
