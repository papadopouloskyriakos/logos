# I1 — Equivalence classes of the searched value systems

Seed 20260708 · Constitution v2.2 (Art. V degeneracy accounting). Numbers from `data/I1_agnostic.json`.
This report quantifies **why** an agnostic value-system search on Linear A is underdetermined: any candidate
system sits inside an astronomically large orbit of systems that the honest objective cannot tell apart, and
on top of that the objective landscape is (per the permuted-corpus control) statistically flat.

## 1. Symmetries the objective is invariant under

The seqLL objective and every reported grade are unchanged by:

1. **Consonant-class relabeling** — permuting the |C| abstract consonant labels: factor **|C|!**.
2. **Vowel-class relabeling** — permuting the |V|=5 abstract vowel labels: factor **|V|! = 120**.
3. **Homophone (within-cell) sign permutation** — two signs sharing an identical (c,v) cell are
   interchangeable under the model: factor **Π_cell (n_cell!)**.
4. **Synonymous class→phoneme mapping** — any bijection from abstract classes to actual phonemes; this is
   exactly symmetries 1–2 and adds nothing beyond them (there is no privileged phoneme labelling — the whole
   point of an *agnostic* search).

Because the search never touches a known value (SEED_A = 0, no anchors), **no symmetry is broken by data**:
the orbit is realised in full. This is the formal statement of "internal evidence is value-blind /
relabeling-invariant" that the campaign established.

## 2. Orbit size of the best system (per grid)

Orbit = |C|! · |V|! · Π_cell n_cell!  (log₁₀):

| grid | occupied cells | log₁₀ |C|! | log₁₀ |V|! | log₁₀ Π cell! | **log₁₀ orbit** | orbit |
|---|---|---|---|---|---|---|---|
| C12 | 25 | 8.68 | 2.08 | 12.56 | **23.3** | ~10²³ |
| **C15 (primary)** | 23 | 12.12 | 2.08 | 13.02 | **27.2** | **~10²⁷** |
| C18 | 31 | 15.81 | 2.08 | 8.93 | **26.8** | ~10²⁷ |

The primary (C15) winner — C-class sizes [4×10, 3×5], V-class sizes [11,11,11,11,11] — has **≥ 10²⁷**
relabeling-equivalent twins that are *literally indistinguishable* under the objective and under every grade
in this study. For comparison, the freely-optimised collapse system (4 cells) has an even larger orbit,
log₁₀ ≈ 82, because its few huge cells contribute enormous within-cell permutation factors.

## 3. Empirical landscape flatness (the orbit is a lower bound on ambiguity)

The symmetry orbit counts systems that are *exactly* equal. The permuted-corpus control shows the objective
is additionally **statistically flat** across genuinely different systems:

- real-corpus seqLL gain over random-φ median = **0.469 nats/token**; permuted-corpus gain = **0.462**;
  **ratio 1.014**. The objective's advantage over chance survives destruction of all phonotactics ⇒ it does
  not separate the "true" value structure from marginal-fitting noise.
- Consequently the set of systems within measurement noise of the best is effectively the **entire balanced
  partition space modulo symmetry**, not a small identifiable neighbourhood. (The MCMC ε=0.01-nat near-optimal
  counter returned 0 distinct extra systems only because it rarely reaches the greedy optimum's seqLL within
  0.01 nats — a reach limitation, not evidence of a sharp peak; the analytic orbit and the permuted-corpus
  flatness are the load-bearing evidence.)

## 4. What would break the degeneracy (and why the corpus cannot)

Each symmetry is broken only by an **external, value-bearing** constraint:

- symmetries 1–2 (class relabeling) ⇒ need **secure phonetic anchors** (a bilingual, or independently-read
  signs). Current state: SEED_A = 0. None available.
- symmetry 3 (homophones) ⇒ need evidence that two co-celled signs carry *different* values (again external).

No amount of additional *monodirectional* Linear A corpus removes these — they are removed only by an anchor
or a bilingual, exactly as recorded in the campaign memory ("only a bilingual or ≥3 independent held-out
anchors can crack it; more corpus cannot"). The 10²⁷ orbit is the precise cost of that missing external
information.

## 5. Bottom line

Every candidate value system the agnostic search can propose is one representative of a ≥10²⁷-member
symmetry orbit, drawn from a landscape the honest objective cannot distinguish from chance (permuted ratio
1.01). This is the structural reason the verdict is `UNDERDETERMINED_NO_RECOVERY` and no phonetic value is
assignable — not a failure of search effort, but an information-theoretic property of a monodirectional,
anchor-free corpus.
