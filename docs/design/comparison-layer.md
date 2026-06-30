---
provenance: operator design spec (provided 2026-06-30); adopted as the design for the
  discipline / comparison layer (task #15) and the predict/verdict schema (tasks #11/#12).
status: adopted, with two maintainer refinements appended (section F). Cross-refs to
  "the brief" point at docs/findings/2026-06-30-expert-redteam-synthesis.md.
---

# logos — lexical-comparison layer: encoding, deflation, decontamination

*Design spec. Extends the logos schema to (A) encode a lexical/cognate-comparison hypothesis with a
falsifiable held-out implication, (B) deflate it against a search-sized null so a Gordon-style match
must clear a meaningful bar, and (C) tell "the embedding found it" from "a model regurgitated Gordon."
Built to fail honestly: the most likely output of this layer is a calibrated **null**, and that null
is the deliverable.*

---

## 0. The one principle everything hangs on

> A sound-match is a **proposer signal (confidence ≤ 0.75)**. It becomes **evidence** only if the
> *sign-values it commits to* predict structure in inscriptions it was not derived from, at a rate
> beating the expected maximum of the number of matches the search could have produced.

Matches are cheap (permissive roots × vowels × languages). Held-out *systematic* consequences of a
match are not. We test the consequence, not the match.

---

## A. Encoding a comparison hypothesis

### A.1 What a hypothesis actually commits to

A lexical-comparison hypothesis is **not** "Minoan word W ≈ root R in language L." That has no teeth.
It is the *partial sign→value map and correspondence system that the match forces*, plus the
held-out implication of applying it blind.

```
hypothesis = {
  plan_hash:        sha256(canonical_body),     # registered BEFORE held-out test
  partial_map:      { *301: /na/, ... },         # the sign values this match COMMITS to
  correspondence:   [ (A-series → L-phoneme rules) ],  # the systematic sound-laws implied
  candidate_lang:   "NW-Semitic" | "Anatolian" | "L_fake_07" | ...,
  anchor_lexeme:    { form: "nawaya", root: "N-W-Y", gloss: "dwell" },
  derivation_set:   [inscription_ids used to FIND the match],   # e.g. Libation Formula @ sites {a,b}
  heldout_set:      [inscription_ids NOT used],                 # e.g. sites {c,d,e} + admin tablets
  free_params:      k,                            # # asserted sign-values + correspondence rules
  provenance:       embedding_nn | llm_proposed | literature_match | human | canary,
  search_log_ref:   id → the instrumented retrieval that emitted this (gives N_eff, see B.2),
}
```

The hash-key registers `partial_map` + `correspondence` + `heldout_set` **before** the verdict runs.
Internal fit on `derivation_set` is recorded but **scores zero**. (Brief §6.3, enforced.)

### A.2 The held-out implication — and why it must be *structural*, not lexical

Naive held-out test = "do the committed values produce more L-lexeme hits in `heldout_set` than
chance?" This is the overfitting-prone version; isolated word-hits are exactly what chance yields.

Stronger, harder-to-fake test = **does the committed map reveal *systematic L-morphology* across
held-out inscriptions?** Truth produces system (recurring real affixes, agreement, regular roots);
coincidence produces scattered hits. Three test statistics, in increasing strength:

- `S_phono` — log-likelihood of held-out word-forms under an **L-phonotactic n-gram model** built
  from L's known lexicon. (Weak: surface plausibility.)
- `S_lex`   — deflated lexeme recall: fraction of held-out forms within regular-correspondence edit
  distance ≤ ε of an L lexeme. (Medium; the Gordon failure mode — must be hammered by the null.)
- `S_morph` — **recurring-morphology score**: do the held-out forms exhibit the *same* L affix /
  template inventory at above-null frequency, consistently, across *independent* inscriptions?
  (Strong: this is Kober's internal-structure logic keyed to a specific language.)

**Primary statistic is `S_morph`.** `S_lex` is reported but never sufficient alone. The Libation
Formula's recurrence across ~5 peak-sanctuary sites is the natural **5-fold held-out CV**: derive on
k sites, predict the verb/morphology on the held-out site(s).

---

## B. Deflation — sizing the bar so `nawaya` has to mean something

### B.1 The null distribution (Packard, scaled)

Build the null by generating control hypotheses with the **same structural freedom** as the real one
but **no genuine correspondence**, and computing the same held-out statistic on each:

- **frequency-banded sign-value permutation** (Packard 1974): shuffle sign→value assignments within
  frequency bands (prevents trivial artifacts), recompute `S_morph` on held-out.
- **random lexeme draw**: keep the map, draw the anchor root randomly from L's lexicon.
- **canary languages** (see C.3): real held-out statistic against fabricated languages.

This yields a null with mean `μ₀`, std `σ₀`, skew `γ₃`, kurtosis `γ₄`.

### B.2 Effective-n: COUNT it, don't estimate it

Last conversation's point, now operational: a vector/RAG search makes the trial count **exact**.
Instrument the retrieval to log every distinct `(sign-value-assignment × lexeme × segmentation)`
candidate it actually scored. **That count is `N_eff`.** No hand-waving.

Sanity upper bound (use only to detect under-logging):
```
N_eff ≲ S_unknown · V̄_branch · R_L · F · G_seg
        (signs free) (values/sign)(roots in L)(families)(segmentations)
```
The honest `N_eff` is the logged count; it will be large, and that is the point — the human-search
version hides this number, the machine version is forced to publish it.

### B.3 The deflated bar (DSR, adapted from Bailey & López de Prado 2014)

The threshold is the **expected maximum of `N_eff` draws from the null**, not the single-trial bar:

```
E[max_Neff] ≈ μ₀ + σ₀ · [ (1−γ)·Φ⁻¹(1 − 1/N_eff) + γ·Φ⁻¹(1 − 1/(N_eff·e)) ]      γ = 0.5772…
```

Then deflate the observed `S*` for skew/kurtosis and **track-record length** `T` (= size of the
held-out evaluation; small `T` ⇒ noisier `S*` ⇒ lower DSR, correctly penalizing thin held-out sets):

```
DSR = Φ( (S* − E[max_Neff]) / σ̂(S*) ),   σ̂(S*) deflated by (γ₃, γ₄, T)
```

**Graduation gate (both clauses, brief §6.4):**
```
GRADUATE(family L)  iff   DSR ≥ 0.95   AND   free_params k ≤ U_floor
```
where `U_floor` is the §3 identifiability budget (MDL: the correspondence may not assert more free
parameters than the corpus can pin). This is the legitimate use of the §3 number — a complexity cap,
not a refutation.

### B.4 Why this kills `*301 → nawaya`

It was derived **on** the Libation Formula (frozen religious language), tested **on nothing**, value
reverse-engineered to fit one root. Under this layer it must instead show that `*301 = /na/`, applied
blind to held-out sites + admin tablets, produces **recurring Semitic morphology** above
`E[max_Neff]` for an `N_eff` counting the whole Semitic-root × vowel-fill search. It won't — and the
verdict says so mechanically. A null on Semitic is then a **publishable result**, not a failure.

---

## C. Decontamination — discovery vs regurgitation

The threat: a frontier model has read Gordon, Best, Di Mino. When the LLM proposer or a RAG-over-
scholarship pipeline emits `*301=na→N-W-Y`, "convergence" with the model is **shared-source
contamination**, not independent evidence. Five mechanisms, ordered by robustness:

### C.1 Literature index + quarantine (necessary, not sufficient)

Index every published Linear A sign-value and correspondence claim (Gordon 1957/66, Best, Davis,
Duhoux, Di Mino's public material, …). Any proposed correspondence matching the index is tagged
`literature_match` and **quarantined**: it may be tested, but it can never count as *discovery* and
its provenance weight is hard-capped. Default assumption for an index hit: regurgitation.

### C.2 Literature-virgin signs (the decisive generalization test)

Partition signs into `L_known` (any published proposal exists) and `L_virgin` (none). A real
correspondence *system* forces values on `L_virgin` signs too. **Discovery claims may rest only on
`L_virgin` held-out success.** Regurgitation can only return what's in the training corpus; it cannot
predict the untouched signs. If the system is right about `*301` (in the literature) but useless on
`L_virgin`, it memorized — it didn't discover.

### C.3 Fabricated-language canary (regurgitation-proof noise floor)

Construct `L_fake`: a phonotactically-plausible lexicon generated from a CV-template grammar with
realistic phoneme frequencies and invented glosses — **never published, never in any training set.**
Run the *full* comparison pipeline against `L_fake` exactly as against Semitic/Anatolian.

- `L_fake` cannot be regurgitated, so any "signal" it produces is **definitionally spurious** → it is
  your empirical false-positive floor.
- **Decision rule:** a real candidate language passes only if its deflated held-out score exceeds the
  `L_fake` score **distribution** (use *many* `L_fake` instances) by the corrected margin.
- If `S_morph(Semitic) ≈ S_morph(L_fake)`: the comparison layer has **no power**; stop and report the
  null. This single diagnostic is the cleanest thing in the whole design — it can't be fooled by
  memorization because there's nothing to memorize.

### C.4 LLM-ablation delta

Run the pipeline (a) with the LLM proposer and (b) with it removed (cognate-aware vector metric +
mechanical verdict only). Correspondences surviving in (a) but not (b), **intersected with the
literature index**, estimate the contamination the LLM is laundering. Large delta on literature hits
⇒ the LLM is a regurgitation engine; demote it to recall-only, never verdict-path.

### C.5 Provenance in the schema

```
verdict = {
  heldout_stat: S*, null_q: E[max_Neff], N_eff, DSR, mdl_k: k, mdl_budget: U_floor,
  provenance, lit_index_hit: bool, virgin_sign_support: float, fake_lang_margin: float,
  verdict: GRADUATE | REJECT | NULL_PUBLISHED,
}
```
`provenance = llm_proposed AND lit_index_hit = true` ⇒ excluded from any discovery claim by
construction. The LLM is **nowhere on the verdict path** — it proposes; it never grades. (Brief §6.2.)

---

## D. Combined plan of action (build sequence)

Ordered so each step produces a usable artifact and the cheap falsifiers come first.

**Phase 0 — inventory + index (philology, no ML).**
1. Clean 259 raw tokens → ~90 syllabograms by *inheriting* SigLA/GORILA typing (Q5); carry
   logograms/numerals as a separate channel.
2. Build the **literature index** (C.1): every published sign-value + correspondence claim.
3. Partition signs → `L_known` / `L_virgin` (C.2).

**Phase 1 — harness credibility (known answer first).**
4. Reproduce **Linear B → Greek** recovery on the existing engine (audit Q2). No comparison-layer
   claim is trusted until the harness recovers a known decipherment.

**Phase 2 — the null machinery, before any real match.**
5. Implement `S_phono / S_lex / S_morph` and the **frequency-banded permutation null** (B.1).
6. Instrument retrieval to **log `N_eff`** (B.2); implement the **DSR + MDL gate** (B.3).
7. Build the **fabricated-language canary** generator and run it — this gives the noise floor
   *before* you're tempted by a real result (C.3). If the floor is high, you've learned the layer is
   underpowered for free.

**Phase 3 — controlled comparison.**
8. Run candidate families (Semitic, Anatolian, Tyrrhenian, IE, isolate-null) through the *same*
   pipeline as the canaries. Everything enters as a registered, hash-keyed, ≤0.75 signal.
9. Apply the decision rules: graduate only on `DSR ≥ 0.95 AND k ≤ U_floor AND beats L_fake margin
   AND `L_virgin` held-out support`.
10. Run the **LLM-ablation delta** (C.4); compute contamination estimate.

**Phase 4 — deliverable (most likely a null).**
11. Publish, per outcome:
    - *Most likely:* "No candidate family clears the deflated, decontaminated bar; here is the
      calibrated null and the `L_fake` floor that sinks Gordon/Di Mino-style matches." ← real,
      useful, publishable; it's the referee artifact the field lacks.
    - *Best case:* graduated **sound-value** imputations for `L_virgin` signs (Etruscan-grade:
      pronunciation, uncertainty-quantified), explicitly **not** a meaning-decipherment.

---

## E. Acceptance gates (copy into `graduation_state`)

A comparison hypothesis is EVIDENCE only if **all** hold:

- [ ] registered (`plan_hash`) before held-out test; `derivation_set` scored zero
- [ ] primary statistic is `S_morph` (recurring held-out morphology), not isolated `S_lex` hits
- [ ] `DSR ≥ 0.95` against a null sized to the **logged** `N_eff`
- [ ] `free_params k ≤ U_floor` (MDL / §3 budget)
- [ ] deflated score beats the **`L_fake` canary** margin
- [ ] support generalizes to **`L_virgin`** signs (not just literature-known ones)
- [ ] not (`llm_proposed` ∧ `lit_index_hit`) for any *discovery* claim
- [ ] survives LLM ablation (or its survival is independent of the literature index)

Fail any → `REJECT` or `NULL_PUBLISHED`. Never `GRADUATE` on internal fit, single hits, or LLM
fluency.


---

## F. Maintainer refinements (2026-06-30)

Adopted as the design for (b) task #15 and the predict/verdict scaffold (#11/#12). Two refinements to resolve before building:

1. **S_morph is not the sole primary for THIS corpus.** Recurring-morphology needs morphological variety; Linear A is short, administrative, heavily formulaic — there may be too little morphology to recur, so S_morph could be near-powerless regardless of truth (a "no power" verdict that reflects the corpus, not the hypothesis). Make **deflated S_lex the pragmatic primary** (it is exactly the Gordon failure mode, so hammering it is the point) and S_morph the gold-standard-if-the-corpus-cooperates. The spec's "if S ~= L_fake, report no power" escape stays.

2. **L_fake must be calibrated to the candidate.** A trilateral-root-rich Semitic would beat a sparse L_fake because of SEARCH ATTRACTIVENESS, not truth. L_fake must be frequency / root-template / lexicon-size-matched to each real candidate so the null is as "matchable." "Realistic phoneme frequencies" (C.3) is necessary but not sufficient.

DSR note: the instrumented-N_eff rehabilitation (B.2) makes the MACHINE-search trial count exact — a sound rebuttal to the red-teams' "unknowable trial count" for that portion. It does NOT count the human/LLM mental search (the garden of forking paths); the L_fake canary is the N_eff-independent backstop for that residual. So DSR is a secondary, mechanical-search-scoped statistic; L_fake is the headline falsifier.
