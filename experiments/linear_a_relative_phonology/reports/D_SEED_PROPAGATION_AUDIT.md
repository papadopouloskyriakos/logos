# D3 — Seed-Propagation Audit

**Task.** Audit the Foundry WP5(b) claim — *"~3–4 CORRECT C/V seeds → held-out AUC 0.78 (kv=3)
→ 0.82/0.87 (kv=4 pos / pos+sub) on known-truth Linear B … the mechanism is validated: a handful
of correct seeds + internal propagation recovers C/V."* (source
`experiments/linear_a_foundry/scripts/wp5_reduced_seed_bootstrap.py`,
`data/wp5_reduced_seed_bootstrap.json`, `reports/WP4_WP5_CROSSSCRIPT_ANCHORS.md` l.24) — with the
same rigour WP-A used on position→C/V.

**Constitution.** L2/L3 anonymous relative structure; NO phonetic value assigned. Non-circular
(Art. XII): known LB `{A,E,I,O,U}` label seeds and grade held-out AUC only, never a model feature;
`log_freq` dropped from propagation exactly as the Foundry did. Independent reimplementation of the
whole pipeline (features, kNN-RBF affinity, Zhou-2004 closed-form label spreading, Mann-Whitney AUC);
the substitution-graph builder is imported read-only so `pos+sub` reproduces faithfully. Seed 20260708.

Artifacts: `scripts/d3_seed_propagation_audit.py` → `data/D3_seed_audit.json`.

---

## VERDICT: `SEED_PROPAGATION_FREQUENCY_ARTIFACT`

The "0.87" is a **cherry-picked small-sample number sitting on a class-leak, and the recoverable
signal is the frequency artifact WP-A already refuted** — not a propagation mechanism. Four
independent lines converge:

1. **Reconstruction OK, then collapses under an honest CI.** The published numbers reproduce exactly
   on the Foundry's `n_draws=5` sampling. With **all** vowel-seed combinations × 60 consonant draws,
   `pos+sub` kv=4 falls **0.874 → 0.784** (sd 0.190, min **0.015**, max 1.0) and kv=3 falls
   **0.819 → 0.749** (min 0.015). The headline was a lucky 5-draw sample of a distribution that spans
   chance-to-ceiling.
2. **Design leak: kv=4 reveals 80 % of the positive class.** LB has only **5 vowels**. Seeding 4 of
   them leaves exactly **one** held-out vowel, so the "held-out AUC" is a rank percentile on a **single
   positive** vs 65 negatives. The honest recovery metric, recall@k, is **0.057 ≈ 0** — the one
   held-out vowel is essentially never ranked at the top. AUC rises **monotonically with the fraction
   of the answer key revealed** (0.51→0.64→0.75→0.78 at kv=1→4): that is the leakage signature, not
   propagation power.
3. **The missing null: not significant.** The Foundry ran a random-seed null for the freq-prior regime
   (A) but **never for the pivotal clean-seed regime (B)**. Run here (N=500, matched counts): the
   correct-seed observed does **not** beat random-seed labelling — `pos` p=**0.33** (z=0.49),
   `pos+sub` p=**0.13** (z=1.19). The random-seed AUC distribution is mean ≈0.50 with **sd ≈0.18**
   (max 0.94), so a lone "0.87" draw is unremarkable inside it.
4. **Frequency artifact (WP-A carryover) dominates.** Pure **frequency ranking of the signs — no
   seeds, no propagation — gives AUC 0.8725**, *exceeding* the entire label-spreading apparatus
   (0.784 honest / 0.874 cherry-picked). `initial_rate` alone (the exact feature WP-A flagged) gives
   0.759 ≈ the seed-prop AUC; a no-propagation seed-centroid baseline gives 0.742 ≈ seed-prop. The 5
   LB vowels are simply among the most frequent signs; the propagation features are the same
   frequency-confounded position features, and the grading targets are high-frequency. Frequency was
   "dropped from propagation" but re-enters through the position features **and** the target class.

---

## 1. Reconstruction (faithful, Foundry `n_draws=5` sampling)

| channel | kv | published | recomputed AUC | recall | held-out vowels |
|---|---|---|---|---|---|
| pos | 3 | 0.78 | **0.7803** | 0.10 | 2 |
| pos | 4 | 0.82 | **0.8215** | **0.00** | 1 |
| pos+sub | 3 | — | **0.8189** | 0.10 | 2 |
| pos+sub | 4 | **0.87** | **0.8738** | **0.00** | 1 |

Reproduced to ±0.001 → the audit targets the real pipeline, not a config drift.

## 2. Honest CI — all vowel combos × 60 consonant draws (`pos+sub`)

| kv | frac class revealed | held-out vowels | AUC mean | sd | min | max | recall |
|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 4 | 0.506 | 0.153 | 0.129 | 0.852 | 0.095 |
| 2 | 0.4 | 3 | 0.639 | 0.173 | 0.061 | 0.934 | 0.086 |
| 3 | 0.6 | 2 | **0.749** | 0.193 | 0.015 | 0.985 | 0.090 |
| 4 | 0.8 | 1 | **0.784** | 0.190 | 0.015 | 1.000 | **0.057** |

AUC tracks the *fraction of the positive class handed to the model as seeds*, while recall stays
pinned near zero. This is class leakage, not recovery.

## 3. Random-seed null for regime B (Foundry never ran it)

| channel | correct-seed AUC | random-seed null mean±sd | z | p |
|---|---|---|---|---|
| pos | 0.587 | 0.499 ± 0.181 | 0.49 | **0.33** |
| pos+sub | 0.701 | 0.497 ± 0.172 | 1.19 | **0.13** |

Neither clears p<0.05. The pivotal claim has no significance test that survives.

## 4. Leave-one-seed-out (kv=4 vowel set {E,A,O,U}, `pos+sub`, base 0.815)

| drop | AUC without | Δ |
|---|---|---|
| E | 0.946 | **+0.131** |
| A | 0.862 | +0.046 |
| O | 0.638 | **−0.177** |
| U | 0.469 | **−0.346** |

Removing one seed swings the "result" from **0.47 (below chance) to 0.95**. A single seed choice
dominates — the mechanism is not stable across its own inputs.

## 5. Adversarial wrong seeds (true consonants→vowel, true vowels→consonant)

`pos` AUC 0.345, `pos+sub` 0.180 (both <0.5). Seeds *do* drive the score (so it is not seed-inert),
but combined with §3–§4 that only means the score reports **whether you happened to label the
high-frequency signs correctly** — and the vowels are the high-frequency signs (the artifact).

## 6. Frequency-artifact test (the WP-A carryover)

| probe | AUC | seeds? | propagation? |
|---|---|---|---|
| **F1 pure frequency ranking of all signs** | **0.8725** | no | no |
| F2 `initial_rate` ranking (WP-A artifact feature) | 0.759 | no | no |
| F4 no-propagation seed-centroid | 0.742 | yes | no |
| seed-prop kv=4 pos+sub (honest CI) | 0.784 | yes | yes |
| F3 freq-matched random seeds | 0.599 | yes | yes |

F1 **exceeds** the full apparatus with zero seeds and zero propagation. F2/F4 match it without
propagation. F3 (0.599) shows high-frequency *seeds* alone are not enough — but that does not rescue
the claim, because F1 shows you need no seeds at all: the frequency signal lives in the **targets**
(vowels are high-freq) and in the frequency-confounded position features, exactly as WP-A found.

---

## Interpretation

The Foundry framed WP5(b) as *"a handful of correct seeds + internal propagation recovers C/V — the
mechanism is validated."* Audited, the "validation" is: a 5-draw cherry-pick (honest CI 0.78, spanning
0.02–1.0); computed on a design that reveals 80 % of the 5-item positive class and grades the ranking
of the **one** vowel left over (recall ≈ 0); with no regime-B null (and the one run here is
non-significant, p=0.13–0.33); and entirely matched or beaten by **pure frequency ranking (0.872)**,
the very artifact WP-A refuted. The propagation graph contributes nothing over frequency ordering or a
plain seed centroid.

This is consistent with, and reinforces, the wave-1/2 finding: the LB C/V "signal" that supposedly
transfers is a frequency artifact. The seed-propagation "0.87" is **not** an independent validation of
a recovery mechanism — it is the same artifact re-expressed, plus small-sample and class-leak inflation.
No phonetic value is assigned; no licence earned.
