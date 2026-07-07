# WP1 — formal identifiability & symmetry theorem

**Verdict: `PRIOR_THEOREM_OVERSTATED`.** Articles: IV, VII, XII, XVII, XXII. The prior campaign's
sign-relabeling result is valid **only within a narrow scope** and does not license the global stopping claim.

## 1. Model

A decipherment hypothesis is a map `φ : S → V` from the sign inventory `S` (|S| ≈ 92 syllabograms) to a
**structured** value space `V` — phonemes carrying features (vowel/consonant, place, manner), organized into
syllables. Let `G = Sym(S)` be the group of sign relabelings and `H ≤ Sym(V)` the value-structure-preserving
permutations (those respecting the C/V partition and phonological features).

## 2. What the prior result actually proves (scope)

Let `O_id` be any objective that is a function of **sign-identity co-occurrence counts alone** (e.g. held-out
bigram/n-gram likelihood over sign IDs). Then for any relabeling `g ∈ G`, the counts of `g(w)` equal the
counts of `w` up to renaming, so **`O_id(φ∘g) = O_id(φ)`** — `O_id` is `G`-invariant. This is the prior
result, and it is correct: an identity-co-occurrence objective cannot distinguish relabeled maps.

**But this is a property of `O_id`, not of "all internal methods".** `O_id` is `G`-invariant *by
construction*. Demonstrating its invariance empirically (30 random maps, identical likelihood) proves nothing
about objectives outside the class `O_id`.

## 3. What it does NOT prove — the symmetry is broken by relative structure

Consider an objective `O_rel` with a term coupling an **internal relation** on signs to a **value-space
relation**:
- **word position:** `Pos(s)` = a sign's word-initial/final/position profile; couple "high-initial signs → vowel
  values". `O_rel` is invariant only under permutations *within* the vowel class and *within* the consonant
  class → the symmetry group drops from `Sym(S)` (order 92!) to `S_v × S_(92−v)` (order 5!·87!, a factor of
  ~10^9 smaller).
- **scribal substitution:** if signs `x,y` interchange in matched contexts, they are phonologically similar;
  couple "substitutable → nearby values". Invariant only under permutations preserving the substitution graph.
- **morphological alternation:** paradigm/suffix-class signs occupy a value-subspace.

Each such term further reduces the residual symmetry. **Internal evidence therefore reduces the value
equivalence classes** — it constrains the *partition and metric* on `V`, even though it cannot name absolute
phonemes without an external anchor to fix one representative per class.

## 4. Theorem (corrected)

> Under corpus representation `R` and an identity-co-occurrence objective `O_id`, all maps in a `Sym(S)`-orbit
> are observationally equivalent. This equivalence does **NOT** hold for objectives coupling internal
> relational structure (position, substitution, morphology) to value-space structure: those are invariant only
> under the subgroup `Sym(S)_R ≤ Sym(S)` preserving that structure. Internal evidence reduces `|Sym(S)_R|`;
> external anchors are required only to select a representative within the residual orbit (absolute values),
> not to establish the partition.

## 5. Empirical confirmation (WP1 counterexample)

On known-truth Linear B, the word-initial-rate statistic separates the 5 vowel signs from consonants at
**AUC 0.744, permutation p=0.035** (`data/wp1_symmetry_break.json`) — a *significant*, relabeling-variant
signal. Applied to Linear A, the top internal-position signs include **A, I, U** (independently vowel-
corresponding), a non-circular reduction of the value classes. The effect is modest with one feature and is
strengthened by the multi-feature C/V + substitution + morphology programme in WP3.

**Consequence for the campaign:** the value layer is **not** provably closed to internal methods. The correct
target is: (i) recover the C/V partition and phonological-similarity classes internally (WP3), (ii) reduce
equivalence-class size, (iii) require far fewer external anchors to fix absolute values (WP5). The prior
"only a bilingual or 3 anchors" claim is superseded.
