# C_AUDIT — the load-bearing audit of the substitution consonant-axis channel

**Verdict (mechanical, `scripts/c_audit.py` → `data/C_audit.json`):
`SUBSTITUTION_CONSONANT_AXIS_VALIDATED`.**

The C3 substitution result — "substitution neighbours share a CONSONANT and differ in vowel (the
vocalic-alternation axis, = Greek inflection)" — is subjected to the EXACT battery that refuted the
Foundry position channel (`A_SYNTHESIS_AND_ERRATUM.md`: independent replication, frequency-band-
disjoint split, multiplicity, oriented adaptive nulls). Unlike position, **it survives every leg.**
The decisive difference: position was a frequency prior that collapsed to chance once frequency was
held fixed; the substitution consonant-axis is real relative structure that survives a
frequency-matched null (p=0.0033) and a degree-preserving null (lift 2.4×, p=0.0033).

Non-circular throughout: generation + all four scorers use sign IDENTITY only; Linear B (C,V) values
are used ONLY to grade. Seed 20260708, N_null/N_perm = 300, DĀMOS 13,562 wordforms / 4,946 types /
73 scorable signs / 2,628 graded sign-pairs / 20,311 graded word-minimal-pairs.

---

## Scope of the claim (read before quoting "VALIDATED")

VALIDATED means: **on a KNOWN script, the substitution channel is a genuine relative-phonology
detector** — it recovers the consonant-held/vocalic-alternation axis and that recovery is not an
artifact of frequency, degree, implementation, site, or the number of relation types tried. This is a
*detector-calibration* claim (roughly L2 structural), and it establishes the asymmetry the WP-A
erratum flagged: the substitution channel is load-bearing where the position channel was not.

VALIDATED does **NOT** mean: (i) the detector recovers anything on Linear A; (ii) value-blindness /
relabeling-invariance is defeated (the constraint-expansion campaign proved LA *internal* evidence is
relabeling-invariant, and this LB calibration does not touch that — on LB the grading uses TRUE
values, so a real Greek-inflection axis is *expected* to surface); (iii) any phonetic or transfer
licence is earned. **All LA transfer licences remain NOT_EARNED; highest earned layer unchanged.**

---

## The battery, leg by leg (position's fate in brackets)

### Leg 1 — Independent replication  ✅  [position: 2 of 3 unsupervised models FAILED]
Four genuinely distinct implementations of "substitution neighbours share a consonant," graded as
same_consonant-vs-cross AUC over sign-pairs:

| implementation | same_consonant AUC | same_vowel AUC | axis = consonant? |
|---|---|---|---|
| A · slot-fill substitution weight (raw frame count; the C3 method) | 0.643 | 0.544 | ✅ |
| B · distributional neighbour-embedding cosine | 0.676 | 0.568 | ✅ |
| C · frequency-normalized co-fill **Jaccard** (set overlap of substitution environments) | **0.703** | 0.566 | ✅ |
| D · co-fill **PPMI** (pointwise mutual information over the sign×slot bipartite graph) | 0.692 | 0.569 | ✅ |

**All 4/4 agree** the axis is the consonant (differ in vowel), each with same_consonant > same_vowel
and > 0.55. Critically, C and D are frequency/degree-normalized by construction (a raw-count bug in A
cannot reproduce itself in a set-overlap or PMI statistic), and the strongest signal comes from the
frequency-normalized Jaccard — the opposite of a frequency artifact.

### Leg 2 — Grouped CV  ✅  [position: frequency-band split COLLAPSED to 0.481 = chance]
- **Frequency-band-disjoint** (the exact killer of position): pooled within-band same_consonant AUC
  (both signs in the same log-freq quartile, so frequency cannot rank them) = **0.657** (method A),
  **0.725** (Jaccard). The frequency baseline within-band is near chance (per-band 0.42/0.52/0.39/0.60,
  pooled 0.584). Position collapsed here; substitution does not. *(Caveat: per-band positive counts
  are small — 5/7/10/11 same_consonant pairs — and the within-band signal is strongest in the
  high-frequency stratum, AUC 0.945 in the top quartile vs 0.558 in the bottom; the pooled estimate
  and the frequency-matched null in Leg 4 are the load-bearing frequency controls.)*
- **Leave-one-site-out** (rebuild the graph on the complement corpus): same_consonant AUC 0.633–0.646
  across all 6 sites incl. dropping KN (4,146 docs); all folds keep the consonant axis.
- **Leave-one-series-out**: min same_consonant AUC 0.635; all folds keep the consonant axis.

### Leg 3 — Multiplicity over the relation family  ✅  [position: survived NO correction; not even the best channel]
Word-minimal-pair method AUC (class vs cross), Holm/BH over the 5 relation types tried:

| relation | AUC | Holm-adj p | note |
|---|---|---|---|
| morphophono (same_C, word-final) | 0.744 | 0.017 | case/gender endings |
| same_consonant (all) | 0.704 | 0.017 | the axis |
| same_consonant (word-internal) | 0.665 | 0.017 | axis holds off word-final too |
| same_vowel | 0.612 | 0.017 | weaker sister axis |
| spelling_variant | 0.363 | 0.017 | allographs *anti*-recovered (low raw count) |

same_consonant and morphophono both survive Holm at α=0.05. (All raw two-sided permutation p hit the
resolution floor 1/301 → identical Holm 0.017; the substantive point — same_consonant clears the
family-wise correction and is one of the two strongest channels, not a runner-up — holds.)

### Leg 4 — Oriented (two-sided) adaptive nulls  ✅  [position: two-sided p 0.146; best-of-model 0.129]
- **Degree-preserving (Maslov–Sneppen), two-sided**: same_consonant strong-edge lift 2.43× (top-20)
  down to 1.39× (top-320), **p_two-sided = 0.0033 at every cutoff**. The sister axis same_vowel is
  NOT significant at the strong-edge cutoffs (lift 1.15×, p_two-sided 0.52 at top-20) — confirming the
  axis is specifically the consonant, not generic phonetic relatedness.
- **Frequency-matched label null** (permute same_C/cross labels within freq(a)·freq(b) strata): obs
  0.643 vs null mean 0.494, **p_two-sided = 0.0033**. This is the exact control position failed; the
  substitution axis passes decisively — the enrichment is NOT frequency.
- **Best-of-relation selection null** (max AUC over the 5-type family vs null max): obs max 0.744 vs
  null max 0.561, p = 0.0033.

### Leg 5 — Explicit frequency-artifact test  ✅
- Frequency alone (freq[a]·freq[b]) recovers same_consonant only weakly (AUC 0.570) and near-chance
  within band (0.584); the method beats it both overall and within-band.
- Residualizing the edge weight on log(freq[a]·freq[b]) (regress frequency out) leaves same_consonant
  AUC = **0.634** — essentially undiminished. The signal is not carried by frequency.

---

## Decision rule and outcome

VALIDATED requires ALL of: ≥2 independent implementations agree · the frequency-band-disjoint split
survives (≥0.55; position collapsed to 0.481) · multiplicity (Holm) survives · oriented adaptive
nulls (degree-preserving two-sided, frequency-matched, best-of-relation) all p<0.05 · leave-one-
site/series-out all folds keep the consonant axis. Miss the freq-band OR the core nulls/multiplicity →
REFUTED; core intact but a robustness leg weak → EXPLORATORY_ONLY.

| component | result | pass |
|---|---|---|
| independent replications agreeing (≥2) | 4/4 | ✅ |
| frequency-band-disjoint pooled AUC | 0.657 | ✅ |
| multiplicity (Holm, same_C / morphophono) | 0.017 | ✅ |
| degree-preserving two-sided p | 0.0033 | ✅ |
| frequency-matched null two-sided p | 0.0033 | ✅ |
| best-of-relation selection p | 0.0033 | ✅ |
| LOSO site + series, all folds axis=consonant | yes | ✅ |

→ **`SUBSTITUTION_CONSONANT_AXIS_VALIDATED`.**

## Why substitution survives where position died
Position's "signal" was frequency rank (vowels are frequent); every passing grouping preserved
frequency rank, and the moment frequency was held fixed (within-band, frequency-matched permutation)
it fell to chance. The substitution consonant-axis is orthogonal to frequency: it survives a
degree-preserving null (which fixes each sign's substitution participation), a frequency-matched
label null, within-band evaluation, and frequency residualization — and it is reproduced by four
independent scorers including two that are frequency-normalized by construction. The channel earned
its status against the same brutal bar that the position channel failed.

## Append-only note (Art. XVII)
This audit CONFIRMS and does not amend C3. The surviving load-bearing candidate for "internal LB
methods detect real relative phonology" is now the substitution consonant-axis, *validated as a
detector on a known script*. Transfer to Linear A and the value-blindness question remain open and
separate; no LA licence is created here.
