# Finding 2026-06-30 — paper audit: Tamburini 2025 is major prior art; novelty re-assessed

Three-document audit (`wwq22bb6r`: `logos_references.md`, `frai-08-1581129.pdf`,
`2604.17828v1.pdf`). Decisive for the build plan.

## 1. Tamburini 2025 (CSA_OptMatcher) — the B-K&K+Luo comparison layer, ALREADY PUBLISHED

Fabio Tamburini, *On automatic decipherment of lost ancient scripts relying on combinatorial
optimisation and coupled simulated annealing*, **Frontiers in AI 8:1581129 (2025)**.
Code: `github.com/ftamburin/CSA_OptMatcher` + `github.com/ftamburin/EditDistanceWild` — **the
same repo we already pulled the 2,214 Ugaritic-Hebrew cognate pairs from.**

It is a **non-neural** cognate-ID system: **k-permutation** solution encoding with explicit
**null / one-to-many / many-to-one / many-to-many** mappings (+ a permutational-number-system
isomorphism to integers, Patel 2022), a **single joint energy E(σ)** for sign+lexicon matching
(vs Luo's two-step EM), a **#UA+#MA regulariser** against degenerate maps, **EDW** (edit distance
with `?`/`*` wildcards for damaged signs), **Coupled Simulated Annealing** (16 annealers), and
**mean±std over 4 seeds** (Reimers & Gurevych 2017). It **decontaminates Luo** (strips the
expected-cognate-count leak; calls out Luo's max-over-restarts reporting bias) and **beats the
decontaminated NeuroCipher on 6/7 benchmarks** (Ugaritic-Hebrew 95.5 vs 90.4; Linear-B-Greek
89.4 vs 75.8; Luvian-Hittite 47.5 vs 18.2). It also adds 3 new benchmarks (CS/AG, Ph/Ug, Luv/Hit).

**Implication:** the planned "faithful B-K&K with restarts to close our 0.55% gap" is **moot** —
Tamburini published it, better, open-source. **Action: workflow `wvjjldtsy` stopped.** Our
simplified heuristic (0.55%) stays as **internal harness calibration only**, never a contribution.
Phase 1 becomes *"reproduce Tamburini Table 3 on the shared benchmarks, then extend"* — and we
**adopt CSA_OptMatcher** rather than rebuild.

## 2. arXiv:2604.17828 — MISFETCH (Nair 2026, not agent-driven corpus linguistics)

The PDF is **Ashish S. Nair (2026), "How Non-Linguistic Is the Indus Sign System? A
Synthetic-Baseline Scorecard"** — a statistical-epigraphy paper (Indus languagehood via synthetic
heraldic/administrative baselines + a Farmer-Sproat-Witzel 4-metric scorecard + within-inscription
fixed-seed Monte-Carlo null). **NOT** an agentic/MCP/corpus-query paper (grep for agent/MCP/
retrieval/instrument = 0 hits; Claude appears only as a dev assistant with a hard no-inference-time
wall). Cite only for **methodology cousins**: multi-metric simultaneous discrimination; fixed-seed
permutation null; **dedup-rate reporting** (found 24% silent exact duplicates materially biasing
repetition metrics → logos must dedup + publish the rate); and the AI-Assistance-Disclosure that
reaffirms proposer/grader separation (agora invariant 3). **If a genuine agent-driven-corpus
linguistics paper was intended, re-fetch the correct arXiv ID.**

## 3. What is STILL genuinely logos-novel (narrowed, but real)

Untouched by Tamburini (no LLM, no regurgitation concern) AND Nair (non-linguistic generators)
AND not withdrawn by our own red-team:

1. **`L_fake` fabricated-language canary** — a phonotactically-plausible, root-template/lexicon-
   size-**matched invented lexicon** (calibrated per comparison-layer §F), never published, never
   in any training corpus, run through the full pipeline as an **empirical false-positive floor
   for frontier-model pretraining contamination**. Tamburini has no memorization problem; Nair's
   generators test *languagehood*, not *LLM contamination*. **This is the headline logos novelty.**
2. **Literature-virgin-signs decontamination** (`L_known`/`L_virgin`) — discovery claims may rest
   only on `L_virgin` held-out success; regurgitation cannot predict untouched signs. No analog.
3. **LLM-ablation delta × literature-index contamination estimator** (comparison-layer §C.4).
4. **The integrated finance-derived discipline stack as a decipherment-claim graduation gate**
   (prereg + exact-logged `N_eff` + deflated bar + MDL `k≤U_floor` + held-out structural test).
   Each component borrowed (DSR=LdP; permutation null=Packard/Sproat; MDL=standard); the specific
   *transfer + single enforced gate onto decipherment* is logos.

**Secondary / distinguishing axes** (defensible, narrower): **sign-mapping-accuracy as a metric**
(Tamburini reports cognate-ID only — the 29/30 figure is Snyder's background); **exhaustive
permutational exact-bounds** via Patel 2022 vs Tamburini's CSA metaheuristic (if tractable);
broader **script coverage** (Linear A target; Cypro-Minoan test — Tamburini leaves these future).

## 4. NO LONGER NOVEL — cite / retract

- B-K&K+Luo comparison layer on Ugaritic-Hebrew → **Tamburini Table 3**.
- Permutation encoding w/ null/one-to-many/many-to-one → **Tamburini k-permutations**.
- Unified joint energy vs EM → **Tamburini E(σ)**.
- Decontaminating SOTA by stripping gold-standard inputs → **Tamburini (for Luo)**.
- mean±std over seeds → **Reimers & Gurevych 2017**; non-neural beats neural SOTA on small data →
  **Tamburini 6/7**; DSR as headline → already internally demoted; "unique consistent map" +
  "faithful B-K&K core" → already withdrawn.

## 5. Plan corrections (to fold into comparison-layer.md + references + roadmap)

- **Adopt CSA_OptMatcher** as the non-neural baseline (clone the open repo); Phase 1 = reproduce
  its Table 3, then extend. Drop the faithful-B-K&K rebuild.
- **Adopt EDW** (wildcard edit distance) for `S_lex` so damaged inscriptions are first-class.
- **Add `sign_map_accuracy`** to the verdict schema, reported ONLY on synthetic/Linear-B/Ugaritic
  pseudo-decipherments (Linear A mapping accuracy is ill-defined — no gold).
- **Exhaustive permutational-fragment-enumeration exact-bounds baseline** (Patel 2022) — defensible
  novelty IF tractable; else degenerates to CSA+fragments ≈ Tamburini.
- **Strengthen §C decontamination** with the Tamburini citation (generalize: train/test leakage,
  held-out-language generalisation, LLM-corpus contamination via literature index + L_fake + L_virgin).
- **Multi-seed reporting** in acceptance gates (≥4 seeds, fixed-seed logging; max-over-restarts =
  contaminated reporting).
- **Phase-0 dedup + dedup-rate reporting** (Nair's 24% lesson).
- **References fixes:** add **CREWS (Steele 2017/2019)**, **Ferrara 2012** (Cypro-Minoan corpus),
  **Valerio 2016**, the computational Aegean/Cypriot review set (Corazza/Karajgikar/Daggumati/
  Papavassiliou); fix the authorless **arXiv:2604.17828 → Nair, A. (2026)**; resolve a precise
  **Duhoux** libation-formula citation; add GORILA's commercial imprint (Geuthner, Paris); soften
  "Tamburini supersedes B-K&K" → "SOTA along the combinatorial-optimisation axis; complementary
  to B-K&K's generative/Bayesian lens."

## 6. Net positioning

logos's defensible contribution is no longer "a decipherment baseline" (Tamburini owns that) — it
is **the decontamination + discipline layer for the LLM-in-the-loop era** (`L_fake` + `L_virgin` +
LLM-ablation + the integrated graduation gate), with the calibrated null as the publishable
field-referee artifact. The offensive A↔B phonetic-imputation bet (Track B, still running) remains
distinct (distributional embedding alignment + held-out-anchor recovery), not anticipated by
Tamburini's combinatorial cognate-ID.
