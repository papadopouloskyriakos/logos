# Finding 2026-06-30 — C.4 LLM-ablation on qwen2.5:72b: harness validated, contamination number NOT YET measurable (honest partial-null)

Ran the §C.4 LLM-ablation (`scripts/comparison/ablation.py`) end-to-end against a frontier-scale open
model — **`qwen2.5:72b`** — on a rented **vast.ai H100 SXM 80 GB** (Ollama; instance torn down after,
~$0.85 spend). 40 seeds × 40 held-out Linear A forms; NW-Semitic candidate; bhsa Hebrew lexicon (7682
skeletons) for the model-free arm; 57-claim seed litindex. **0 LLM errors, 40/40 seeds.** This is the
upper-bound regurgitation probe we went off-box for (a 72B is a far stronger memorizer than the local
gemma3:12b).

## The headline number is an ARTIFACT — reported as such, not as a finding

`contamination_rate = 1.000` in **all 32 seeds where it is defined** (min=max=1.0). This is **not**
evidence that the LLM is a 100% regurgitation engine. Verified mechanically:

- `a_lit_hits ≡ delta_lit_hits` in **40/40** seeds → the mechanical arm **never** shares a
  literature-matching correspondence with the LLM → the rate is **forced to 1.0 by construction**.
- The two arms' value vocabularies overlap in only **10 of 134** values: ARM (a) emits phonetic
  strings (`da`, `dī`, `alm`, `gra`…); ARM (b) emits romanized-Hebrew consonants (`$`, `&`, `<`, `q`,
  `w`…). They live in disjoint value spaces, so ARM (b) is structurally incapable of corroborating a
  literature hit.

Both confounds were flagged as risks at build time. The harness reports them honestly
(`litindex_partial=True`, `seed_nonexhaustive=True`, the value-vocab caveat); the run **confirms** they
dominate. Publishing the 1.0 as a contamination result would be the exact "English-is-Semitic" /
overfitting failure the discipline layer exists to prevent (invariant 8).

## What IS trustworthy — the raw divergence + cross-method agreement

Reported regardless of literature coverage (the meaningful v1 signal):

| metric | mean | range |
|---|---|---|
| LLM correspondences/seed (`n_a`) | 28.3 | 8–46 |
| mechanical correspondences/seed (`n_b`) | 9.9 | 4–16 |
| correspondence-level jaccard (a vs b) | 0.165 | 0–0.36 |
| sign-level overlap (value-agnostic) | 0.231 | 0–0.44 |
| LLM-only correspondences `|a\b|` | 23.2 | 8–46 |

**Cross-method agreement (corroborated signal):** a 72B LLM *and* a model-free edit-distance metric
independently converge on the same sign→consonant for a solid set — `SI→s, NI→n, KA→k, NA→n, TE→t,
MA→m, SA→s, DA→d, DI→d, KI→k, MI→m, PA→p, RE→r, RO→r, TA→t`. Caveat: these are essentially the
conventional GORILA consonant skeletons (CV → C), so for the LLM this is recovering *known* values, not
novel discovery; the agreement validates that both arms are operating sanely, not that anything new was
found.

## Honest verdict

**The C.4 contamination delta is not yet a measurable quantity.** It is gated on two inputs the harness
already names:
1. **Populate the litindex** with NW-Semitic phonetic sign-value proposals (Gordon/Best/Di Mino — the
   `*301→/na/` exemplar is still not quarantined). Today's seed is GORILA-syllabic only, so a_lit_hits
   keys on the wrong vocabulary.
2. **Reconcile the two arms onto a common value vocabulary** (or score contamination on the consonant
   skeleton, not raw value strings), so the mechanical arm *can* corroborate a literature hit.

Until then the contamination number is structurally pinned at 1.0 and means nothing. This is a recorded
**methodological partial-null**: the ablation machinery runs cleanly on a frontier-scale model, and it
tells us — honestly — exactly what it needs before it can decide anything. That is the insurance-policy
deliverable, not a fabricated "100%."

## Provenance / reproducibility

Model `qwen2.5:72b` (Ollama default q4_K_M) on vast.ai H100 SXM 80 GB (ephemeral; not a fixed asset).
Raw result: `runtime/ablation/qwen2.5-72b-nw-semitic.json` (gitignored); per-call log
`runtime/ablation/llm_calls.jsonl` (41 calls incl. 1 smoke). Harness committed at `0582966`.
