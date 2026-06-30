# Expert red-team synthesis — 2026-06-30

Two independent external red-teams of the logos audit brief (one Claude Opus, one GPT-5.5)
**converged on the same corrections**. This doc is the authoritative record of what we are
**withdrawing**, what we are **correcting**, and the **revised roadmap**. The brief's
information-theoretic and method claims were overclaimed in places — exactly the failure mode
logos exists to prevent — so these corrections are mission-critical, not cosmetic.

Sources (operator-provided): `20260630_claude_opus_logos_audit_response.md`,
`20260630_openai_gpt55_logos_expert_red_team_audit.md`.

---

## 1. WITHDRAWN claims (the overclaims)

| Claim (brief) | Verdict | Why |
|---|---|---|
| "The corpus is more than large enough to uniquely pin a decipherment" / "refutes the too-little-text argument" | **WITHDRAWN** | Unicity distance assumes a *known plaintext-language oracle*. Measuring D from the ciphertext makes the implicit oracle = Linear A up to relabelling → "unique relative to a language model we don't possess." It conflates *a unique key exists* with *the key is distinguishable from impostors*. |
| "data quantity is not the blocker" | **WITHDRAWN** (as stated) | The binding constraint is *identifiability under an unknown target*, which unicity distance does not address. |
| "a unique consistent map exists in principle" | **WITHDRAWN** | A permutation of sign labels preserves all sequence statistics; many observationally-equivalent maps fit. |
| the engine is "a faithful B-K&K 2011 core" | **WITHDRAWN** | Our EM + `linear_sum_assignment`-over-char-pairs is an alternating nearest-neighbour heuristic. B-K&K jointly optimizes **word-level bipartite matching + a restricted many-to-many alphabet correspondence + edit alignments, with random restarts**. We apply Hungarian to the *wrong variable* (alphabet, not lexicon), force 1-1 cardinality, and omit restarts. |
| the Linear-A "chance-accuracy null" | **ILL-DEFINED** | Linear A has no gold phonetic map → "mapping accuracy" is undefined. Nulls belong on **synthetic / Linear-B / Ugaritic pseudo-decipherments**, not Linear A. |
| JEPA "manufactures a cognate target" | **CATEGORY ERROR** | A↔B gives **phonetic values for A-only signs** (a readout), *not* a cognate language. Linear B's language is Greek, which Linear A is not. A↔B is **script borrowing**, not language cognacy. |
| Deflated-Sharpe over signs×roots×families as the multiple-testing engine | **WEAK / WRONG MECHANISM** | DSR needs a Sharpe-like statistic (no decipherment equivalent) and an honest trial count — impossible with human+LLM proposers (Gelman's garden of forking paths). It's decoration, not the engine. |
| "free params ≤ information floor" graduation gate | **DIMENSIONALLY INVALID** unless both sides are bits | Comparing a parameter count to an entropy budget is apples-to-oranges. Must be **MDL** (bits saved on held-out − bits to describe the map). |

## 2. Corrected claims

- **§3 information floor → a toy-model precondition diagnostic ONLY.** "Under a narrow
  symbol-substitution toy model, the corpus exceeds a plug-in unicity estimate — this shows
  *recurrent structure is measurable*, nothing more." It does NOT establish identifiability.
  - **New open problem (promoted from caveat):** if Linear A **underspells** like Linear B
    (omits codas/l-r/vowel length), the phonology→script channel is **non-injective / lossy**,
    and a lossy channel has **no unicity distance at all** — the destroyed information is
    unrecoverable at *any* corpus size. This is probably where the real ceiling lives.
  - **Redundancy ambiguity:** using log₂(V) gives D=3.687; using empirical H₀ gives D=1.880
    (≈doubles U). State which and why.
  - **Sparse-sample bias:** plug-in conditional entropy on 259 types / 5.8k tokens is
    optimistically biased → U artificially small. Trigram ≠ guaranteed stronger (sparsity).
    Use held-out cross-entropy, inscription-level bootstrap CIs, site/genre-stratified,
    bias-corrected/Bayesian entropy estimators, shuffled + template-preserving nulls.
  - **The real information-sufficiency test = pseudo-decipherment learning curves** (both
    experts): downsample Linear B to Linear-A-like token count, length distribution, genre
    structure, site fragmentation; hide phonetic values; vary anchors; measure held-out
    recovery. *That* answers "can the system recover values under Linear-A-like constraints."

- **§4 baseline → harness validation + a known-answer recovery milestone, NOT a Linear-A method.**
  No cognate method runs on Linear A. The credibility milestone is **Linear B → Greek recovery**
  (reproduce a published number, e.g. Luo's ~67% cognate accuracy; we now HAVE
  `linear_b-greek.cog`). Keep the simplified Hungarian heuristic **renamed** ("simplified
  heuristic baseline"), and either (a) implement faithful B-K&K (word-level bipartite matching
  + many-to-many alphabet + restarts) or (b) clearly label ours as a simplified comparator.

- **§5 → phonetic-value imputation under a script-borrowing model; JEPA is an ablation.**
  Honest ceiling = **Etruscan-grade** (pronounceable, uncertainty-quantified sign values; an
  isolate readable-but-not-understood). Run **simpler, interpretable baselines FIRST** and
  require JEPA to beat them: frequency/positional matching → seeded graph alignment of A/B
  sign-context networks → CCA → **orthogonal Procrustes alignment of distributional embeddings
  (Mikolov 2013 / MUSE)** → optimal-transport with shared signs as soft anchors. Bouchard-Côté
  sound-drift is the principled core **but needs candidate cognate pairs first** (cannot create
  them from unlabelled signs). Critical: **inherited Linear-B values cannot be both the
  training anchors and the independent proof.**

- **§6 discipline → pre-registration + held-out + PIPELINE-LEVEL PERMUTATION NULL; DSR demoted.**
  - Lead with **pre-registration + held-out verification + a permutation null** (Packard 1974
    built 9 *fictitious* Linear A decipherments as a null — Ventris-value transfer beat them
    only ~2:1; foreground Packard as the ancestor of the idea).
  - **Pipeline-level null:** rerun the *entire discovery pipeline* on null corpora that preserve
    nuisance structure (sign frequencies, word/inscription lengths, site structure, formula
    repetition, genre, lexicon size). The best null score calibrates how impressive the real
    best is. Use **FWER/max-statistic** for final claims, **hierarchical FDR** for exploration,
    **MDL** for complexity.
  - **Hashing ≠ sufficient pre-registration:** add trusted timestamps, append-only mirrored
    registry, corpus+code commit hashes, a *declared search budget*, complete retention of
    failed hypotheses, a locked/untouched holdout ("lockbox").
  - **Confidence thresholds (0.75/0.80) are governance, not calibration** — validate with
    reliability diagrams / Brier / ECE, by prediction type and family.
  - **"Sole writer" ≠ independent validation** — add blinded benchmark eval + external
    replication + epigraphic adjudication blind to the generating model.
  - **5 sites ≠ ordinary 5-fold CV** — call it *leave-one-site-out externalization with
    cluster-level uncertainty*; low power, formulaic dependence.

- **§5 inventory → INHERIT, don't cluster; layered ontology; clean BEFORE the floor.**
  GORILA/SigLA already encode AB-series (shared w/ B, values) vs A-only `*`-series, logograms,
  numerals, fractions, ligatures, damaged/uncertain. The `lineara.xyz`/Douros transliterations
  already carry the AB/`*` distinction. So 259→~90 is a **parse + metadata join**, not a
  learning problem. Build a **layered sign ontology**: raw observation → diplomatic token →
  canonical sign id → allograph family → functional class (syllabogram/logogram/numeral/…) →
  value hypothesis. Keep **logograms + numerals as separate channels** (they contaminate both
  H_rate and φ). Maintain **raw / conservative / exploratory** inventories; test every result
  across all three. Represent damaged signs with masks, not deletion.

## 3. Prior art to add (philological gaps, load-bearing)

- **Duhoux** — standard analyses of the **Libation Formula** (our CV set; not citing him is a
  referee magnet).
- **Brent Davis** — *Minoan Stone Vessels with Linear A Inscriptions* (2014) + structural /
  word-order work; the most serious modern structural analyst of Linear A.
- **Packard (1974)**, *Minoan Linear A* — the fictitious-decipherment permutation null
  (ancestor of our deflation idea).
- **Barber (1974)**, *Archaeological Decipherment* — the identifiability threshold §3 must
  engage (and currently fails).
- **Godart & Olivier, GORILA** (1976–85) — corpus authority for the inventory.
- **John G. Younger**, *Linear A Texts* (online) — formula segmentation.
- **CREWS project (P. Steele, Cambridge)** — Aegean writing systems.
- **Robinson**, *Lost Languages* — cautionary framing.
- A **systematic review of computational Aegean/Cypriot scripts** (more targeted than the broad
  ML-for-ancient-languages survey); **Luo et al. 2021** (central, not peripheral — handles
  uncertain segmentation, phonetic conversion, related-language comparison).

## 4. Reframed mission & realistic ceiling

- **New framing:** "A falsifiable, statistically-calibrated inference framework for determining
  which structural, phonetic, and linguistic claims Linear A can support" — ambitious without
  presupposing full decipherment is identifiable.
- **Ceiling = Etruscan-grade** (pronounceable, uncertainty-quantified sign values + a rigorous
  null map). **Full decipherment: <1–3%** (no bilingual, unknown language, short formulaic
  corpus, possible underspelling, many equivalent hypotheses).
- **The product (65–80% credible):** the open, preregistered, null-calibrated benchmark +
  corpus-normalization framework — valuable *even if every proposed reading fails*. Reduce
  trading jargon (DSR / "offensive" / "action cutoff") in expert-facing material in favour of
  preregistration / selective inference / multiplicity correction / locked holdout / MDL /
  posterior predictive checking.

## 5. Revised roadmap (action list)

1. **Withdraw** the strong unicity conclusion (done in this doc + DESIGN); keep as toy-model
   diagnostic; build the **pseudo-decipherment learning-curve** test (downsample Linear B).
2. **Rename** the engine "simplified heuristic baseline"; implement **faithful B-K&K**
   (word-level bipartite + many-to-many alphabet + restarts) OR clearly label ours. Milestone =
   **Linear B → Greek known-answer recovery**.
3. **Replace** the Linear-A chance-null with **synthetic / Linear-B / Ugaritic
   pseudo-decipherment** nulls.
4. **Replace DSR** with pipeline-level permutation selective inference (FWER/FDR) + MDL; keep
   DSR only as one (stated-conservative) instance.
5. **Build the layered sign ontology** + raw/conservative/exploratory inventories; separate
   logogram/numeral channels; recompute the floor on the cleaned ~90-syllabogram stream.
6. **Benchmark simple A↔B alignment first** (frequency → graph alignment → CCA → Procrustes/MUSE
   → OT); JEPA only if it beats them on blinded pseudo-decipherment.
7. **Expand prior art** (§3); **recruit an Aegean epigrapher** before any sign interpretation.
8. **Search-budget accounting** (log every family/lexicon/root/map/segmentation/seed/rerun) +
   **report instability** as a primary result.
9. **Benchmark lockbox** (an untouched held-out set, evaluated sparingly).

---

## 6. Maintainer assessment (2026-06-30) — independent reasoning, not deference

Recorded so the audit trail shows the critiques were *reasoned about*, not rubber-stamped.
Blind deference to two authoritative red-teams would be its own failure mode. Position:
**agree on the substance of every correction; three measured refinements; one bet kept.**

- **Unicity §3 — the computation has narrow diagnostic value, not zero.** As a *precondition
  diagnostic* it does real work: under the substitution model it RULES OUT the "too little text"
  excuse (corpus length is not the binding constraint; identifiability is). The sin was
  presenting that negative result as a positive identifiability proof. "15% defensible"
  conflates "the claim as stated is indefensible" (true) with "the number is useless" (false).
  Opus's "lossy channel → no unicity distance" is technically correct but means the ceiling
  drops to the **orthographic** layer, not that all recoverable information vanishes — the
  pseudo-decipherment curriculum measures that; we don't assert it a priori.
- **Faithful B-K&K is credibility polish, not a blocker.** A clearly-labeled simplified
  heuristic + the known-answer recovery milestone is sufficient standing for logos's purpose;
  faithful B-K&K (word-level bipartite + many-to-many + restarts) is a credibility upgrade,
  pursued next, but it does not gate the framework.
- **JEPA / the A↔B bet — method critique accepted in full; the underlying experiment KEPT.**
  "Manufactures a cognate target" was a category error (A↔B is script borrowing; B's language is
  Greek, A's is not); JEPA-the-architecture is over-engineered for 5.8k signs; the right tools
  are anchored alignment (Procrustes/MUSE/OT/graph); Etruscan-grade is the honest ceiling. BUT
  the A↔B phonetic-imputation experiment STAYS, because (i) it is the **only offensive lever** —
  every other path concedes the missing-target problem entirely; (ii) the red-teams' **own**
  rating (cross-script representation learning 60% plausible as an experiment) supports keeping
  it; (iii) the circularity they flagged is also the validation (hold out shared signs, recover
  their known B-side values). JEPA is demoted to an ablation; the experiment is not dropped.
- **Meta:** the discipline machinery did its job (the red-teams caught real overclaims). The
  test of whether it is working is precisely that we can disagree where the evidence supports it
  while conceding where it doesn't.
