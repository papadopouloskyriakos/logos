# F_CYPRO_MINOAN_SENSITIVITY — does Cypro-Minoan add information or multiply shape matches?

**Task F4-C** · Constitution v2.2 (Art. XI source-dependency, Art. XII, Art. XV) · seed 20260708 ·
script `scripts/f4_loso_relative_class.py` → `data/F4_loso.json`.

## Question

Ten of the 59 correspondences carry a Cypro-Minoan (CM) sign number in their Cypriot detail
(`cypriot_detail`, from Steele & Meissner 2017 Table 6.2). The field routinely treats a three-way
LA↔CM↔Cypriot pedigree as *stronger* evidence for a sign's value. F4-C asks the honest question: does
the CM leg supply an **independent evidence axis**, or does it merely **re-flag signs the shape and
Cypriot-stability channels already select** — inflating apparent corroboration without adding
information?

## The CM-attested set

```
CM (10): A DA I NA PA RO SA SE TI TO
         (CM sign: A=102, DA=004, I=104, NA=013, PA=006, RO=005, SA=082, SE=044, TI=021, TO=008)
```

## Contingency against the other channels (2×2 Fisher, two-sided)

| channel | CM ∧ channel | CM ∧ ¬channel | ¬CM ∧ channel | neither | Fisher p | CM ⊆ channel? |
|---|---|---|---|---|---|---|
| shape = homophone | 10 | **0** | 15 | 34 | 5.2e-05 | **YES** |
| shape ≥ homomorphic | 10 | **0** | 47 | 2 | 1.00 | **YES** |
| Cypriot-stable = true | 10 | **0** | 1 | 48 | ~0.0 | **YES** |

`CM ∧ ¬channel = 0` in every row: **the CM set is a strict subset of each channel.** Every CM sign is
already flagged homophone by shape AND already flagged Cypriot-stable. The Cypriot-stable set adds
exactly one sign CM does not (**PO**); shape-homophone adds 15.

## Independent-information probe (LOSO)

Vowel-family recovery (F4-B) on the CM subset vs the Cypriot-stable subset it lives inside:

| subset | n | dist top-1 | dist centroid | frequency | chance (modal) |
|---|---|---|---|---|---|
| cypro_minoan | 10 | 0.300 | 0.100 | 0.200 | 0.500 |
| paleography_high (Cypriot-stable) | 11 | 0.273 | 0.091 | 0.182 | 0.500 |

Restricting to CM does not move value recovery off the same at/below-chance null that governs every
subset (F4-B). There is no CM-specific lift to be had — because there is no CM-specific *sign*.

## Interpretation

1. **CM multiplies, it does not add.** With `CM ∧ ¬channel = 0` against shape-homophone *and* Cypriot-
   stability, the CM leg introduces **no new sign and no orthogonal axis**. It re-attests a value on
   signs whose value was already asserted by two other channels drawn from the same Ventris/GORILA
   lineage (Art. XI cluster `L_GORILA_VENTRIS`). Counting CM as a third independent witness would be
   **double-counting a single latent identity fact** — precisely the multiplicity failure Art. VIII/XII
   guard against.

2. **The tiny Fisher p-values are the symptom, not a result.** p = 5.2e-05 (shape) / ~0 (Cypriot) mean
   CM co-occurs with those flags *far more than chance* — i.e. maximal redundancy. A genuinely
   independent channel would show CM signs *outside* the existing flags (`CM ∧ ¬channel > 0`); there are
   none.

3. **No independent value power.** Since CM ⊂ Cypriot-stable ⊂ (shape-adjacent), and all three are
   value-judgments on the same transliterated identity (F1: shape and scholarly channels CIRCULAR,
   admin channel NULL, 0/59 primary value witnesses), the CM channel inherits the same status: it
   cannot break the circularity or supply a held-out witness. F4-B confirms it recovers nothing beyond
   chance distributionally.

## Verdict

```
CYPRO_MINOAN_INDEPENDENCE: NONE — CM (10) is a STRICT SUBSET of shape-homophone AND Cypriot-stable
                           (CM & not-channel = 0 in both; Fisher p 5.2e-05 / ~0). CM MULTIPLIES already-
                           flagged signs; it adds no orthogonal evidence axis and no new sign (only PO
                           is Cypriot-stable-but-not-CM). LOSO on CM = same at/below-chance null.
```

The Cypro-Minoan leg does **not** add independent information; it inflates apparent corroboration by
re-flagging signs the shape and Cypriot channels already select. Treat LA↔CM↔Cypriot as **one**
correlated witness, not three. **Licence unchanged: NONE (Art. XV).**

**Compliance:** contingency and LOSO use channel/identity fields only; LB/CM values grade, never input
(Art. XII); source-dependency redundancy recorded (Art. XI).
