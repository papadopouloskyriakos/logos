# F_RELATIVE_CLASS_COMPATIBILITY — do anonymous C4/C5 classes agree with the value hypotheses?

**Task F4-D** · Constitution v2.2 (Art. VIII multiplicity, Art. XII, Art. XV) · seed 20260708 ·
script `scripts/f4_loso_relative_class.py` → `data/F4_loso.json` · classes from `data/C_la_graph.json`.

## Question

The C4/C5 substitution rel_classes are built **value-free** — from Linear A sign identity, frame
membership and word-final position only. This report asks the constraining question: **do the anonymous
classes agree with the cross-script value hypotheses?** If the signs a class groups together *also*
share a vowel or a consonant series under the LB-value hypothesis — **more than a size- and frequency-
matched random LA sign set would** — that is a genuine relative-structure constraint (a "same-vowel"
or "same-consonant" class) that would hold *without* assigning any absolute value. The class stays
anonymous; only its internal *coherence* is graded.

This is the honest, load-bearing test for the campaign's surviving candidate: it is exactly where a
real relative phonology would show up, and exactly where WP-A warned the signal might be only a
frequency prior.

## Grading and nulls (non-circular)

- **Statistic:** within a class, the *modal fraction* on an axis = (count of the most common vowel /
  consonant) / (valued members). 1.0 = the class is phonologically uniform on that axis.
- **Unconditioned null:** random same-size subset of the LA valued-syllabogram universe (20,000 draws).
- **Frequency-matched null:** draw one sign per class member from that member's own LA frequency band
  (20,000 draws) — removes the "high-frequency signs cluster on the `a` vowel" confound that sank the
  WP-A position→C/V result (A4: 4/5 vowels in the top frequency quartile).
- **Multiplicity (Art. VIII):** 5 classes × 2 axes = **10 tests** → Bonferroni factor 10.
- LB values grade only; class construction never saw them (Art. XII).

## Result — per class

| class | signs (values) | axis | modal | frac | p (uncond) | p (freq-matched) |
|---|---|---|---|---|---|---|
| REL_CLASS_01 | A DA JA KA MI RU SI TA (a,da,ja,ka,mi,ru,si,ta) | vowel | **A** | 0.625 (5/8) | 0.050 | 0.117 |
| | | cons | D | 0.125 | 1.00 | 1.00 |
| REL_CLASS_02 | KU MA SA (ku,ma,sa) | vowel | A | 0.667 (2/3) | 0.526 | 0.603 |
| | | cons | K | 0.333 | 1.00 | 1.00 |
| REL_CLASS_03 | RA RE (ra,re) | vowel | A | 0.500 | 1.00 | 1.00 |
| | | cons | **R** | 1.000 (2/2) | 0.058 | 0.063 |
| REL_CLASS_04 | PA TE (pa,te) | vowel | A | 0.500 | 1.00 | 1.00 |
| | | cons | P | 0.500 | 0.992 | 0.996 |
| REL_CLASS_05 | KI WA (ki,wa) | vowel | I | 0.500 | 1.00 | 1.00 |
| | | cons | K | 0.500 | 0.994 | 0.996 |

**Bonferroni survivors (p × 10 < 0.05): NONE — unconditioned or frequency-matched.**

## Reading

1. **The two tantalizing signals are exactly the two the campaign already knows to distrust.**
   - **REL_CLASS_01 as a "same-`a`-vowel" class** (5/8 of A DA JA KA MI RU SI TA carry vowel `a`) reaches
     p = 0.050 against the *unconditioned* null — but **dissolves to p = 0.117 under the frequency-
     matched null** and fails Bonferroni ×10 either way. This is the same signal, and the same
     dissolution, as WP-A: the `a`-vowel signs are the high-frequency signs, so a value-free substitution
     graph that favours frequent signs will *look* `a`-enriched without any phonological cause. C4 had
     already flagged this class as {same_vowel:3, cross:4}; F4 shows the enrichment is frequency, not
     phonology.
   - **REL_CLASS_03 {RA,RE} as a "same-`R`-consonant" class** is uniform on the consonant (modal frac
     1.0) at p = 0.058 (uncond) / 0.063 (freq) — but it is a **single edge (n = 2)** and dies under
     Bonferroni. It is the C3/C5 `same_consonant` candidate seen once more, still underpowered: one
     RA/RE alternation is not a recovered vocalic-alternation series.

2. **No class is compatible with a coherent value-family beyond chance.** Every other class sits at the
   null (p ≥ 0.5). After honest correction for frequency *and* the 10 tests tried, **zero** of the five
   anonymous classes agree with the cross-script value hypotheses more than a random LA sign set would.
   The anonymous relative structure and the LB-value hypothesis are **statistically independent** at
   this corpus scale.

3. **This constrains nothing — which is itself the finding.** A real relative phonology would show at
   least one class surviving as same-vowel or same-consonant, letting us fix a *relative* class label
   without an absolute value. None survives. So the substitution classes cannot be promoted to value-
   family classes, and cross-script correspondences cannot be used to name them. Consistent with the
   whole campaign: internal relative structure is real (L2) but value-blind — the LB-value overlay adds
   no reproducible agreement.

## Verdict

```
RELATIVE_CLASS_x_VALUE_COMPATIBILITY: NULL — 0/5 anonymous C4/C5 classes agree with the LB-value
    hypotheses beyond a size-and-frequency-matched null after Bonferroni x10. The one marginal vowel
    signal (REL_CLASS_01 'a', p_uncond 0.050) is a FREQUENCY PRIOR (p_freqmatched 0.117), reproducing
    the WP-A dissolution; the one marginal consonant signal (REL_CLASS_03 R, p 0.058) is a single
    underpowered edge. No class earns a same-vowel or same-consonant label.
```

The anonymous relative classes do **not** become value-family classes under any evidence-graded cross-
script correspondence; the agreement that exists is frequency, not phonology. Highest earned layer L2.
**Licence unchanged: NONE (Art. XV); no absolute value assigned to any anonymous class.**

**Compliance:** class construction value-free (Art. XII honoured); multiplicity corrected (Art. VIII);
frequency-matched null applied; append-only. No licence bypass.
