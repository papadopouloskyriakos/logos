# Finding 2026-07-01 — distributional-phonology pilot (Track-2): a DATA-LIMITED null, validated by a power curve

A pre-registered Track-2 (offensive, non-blocking) pilot
(`scripts/comparison/phono_distributional.py`) asking: does a sign's **distributional context** (which
signs it sits beside) carry information about its **phonetic value** — measured on the known `AB` signs
whose Linear B sound value we can borrow? A positive on the knowns would be the prerequisite for
imputing sound values to the un-anchored `A`-only signs (the offensive goal, reading the silent signs).
Truth-layer-capped (invariant 5): a positive only *proposes*; no sound value is asserted for any sign.
Graded from `runtime/phono-distributional.json`; imports no `verdict.py`.

## Method (pre-registered before running)

- **Features = raw co-occurrence** (left+right neighbour bigram counts over the sign vocabulary,
  PPMI-weighted, L2-normalised). **Labels = the LB-transferred (C, V)** parsed from the GORILA name
  (`DA`→d/a, `A`→∅/a, `NWA`→nw/a). This is the *non-circular* version: features never see the labels.
- **Test:** leave-one-out 1-NN — does a sign's nearest distributional neighbour share its consonant
  class / its vowel — vs a **label-permutation null** (geometry fixed, labels shuffled). Šidák-deflated
  over the 2 tests (C, V). 50 of ~55 AB signs met the ≥3-occurrence threshold.

## Result — DATA-LIMITED NULL (no bridge detectable), and why that phrasing is exact

| test | LOO-1NN acc | null mean | perm p | Šidák p |
|---|---|---|---|---|
| consonant (13 classes) | 0.080 | 0.065 | 0.40 | 0.64 |
| vowel (5 classes) | 0.140 | 0.201 | 0.86 | 0.98 |

Neither clears chance — distributional context does **not** predict the phonetic class of the known
signs. **But the honest verdict is "data-limited," not "no bridge exists,"** because of the positive
control below.

## The positive control caught an over-claim (the third the discipline has caught)

A first draft reported a flat "NULL: no bridge." The **positive control** — plant context vectors that
*are* informative about the label (one-hot class + noise) and check the test detects them — **failed to
fire at planted strength 1.0**. So the test could not even see a *planted* signal there, which would
make a null uninterpretable. Replacing it with a **power curve** over planted strengths resolves it:

```
planted strength:   1     2     3     5     8    13
test fires (p<.05): no   YES   YES   YES   YES  YES     -> min firing strength = 2.0
```

So the test **works** (it detects a moderately-strong planted signal on these 50 signs) but is **not
infinitely sensitive** at n=50 / 13 consonant classes. Therefore we **cannot distinguish** "no
distribution→phonetics bridge" from "too few signs/contexts to detect a *weak* one." Both point the
same way:

> **The sound path is not recoverable from Linear A alone — it needs the larger Linear B corpus
> (DĀMOS).** No sound value is imputed for any sign.

## Why this belongs in the preprint

It pre-empts the predictable referee question — *"couldn't you just use ML to recover the sounds?"* —
with a measured answer and a **power analysis**, not hand-waving: the distributional-phonetics bridge is
below the detectability floor at this corpus size, and the minimum corpus to detect even a strong signal
is quantified (the test needs planted strength ≥2 at n=50). It is on-theme for the paper's spine (a body
of rigorous, pre-registered nulls bounded by the information floor) and it is honest about being
*data-limited* rather than negative. It also sharpens the strategic map: the **image** leg of the
cross-script bet works now; the **sound/sequence** leg is data-blocked, exactly as this pilot shows.

## Verified

+4 pilot tests (C/V parsing; the positive control has power; the real result is the data-limited null;
no verdict import). Raw artifact `runtime/phono-distributional.json` (gitignored). The grade is computed
mechanically from the permutation tests + the power curve, never from narration.
