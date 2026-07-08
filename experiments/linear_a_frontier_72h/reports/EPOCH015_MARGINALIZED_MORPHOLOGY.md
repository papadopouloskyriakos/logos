# EPOCH-015 — Segmentation-marginalized morphology (frontier F4, gate A)

**Prereg frozen** 2026-07-08T12:29:36Z · plan_hash `d35828be…c32024` (= sha256 of `prereg.md`) ·
seed 20260708 · claim ceiling **L2/L3** · LA touched (numbers reported, not gate-licensed) ·
no transfer licence changed. Constitution v2.2; Articles V/VII/VIII/IX/XI/XII/XV/XVII/XVIII/XXII.

## Question

Prior LA morphology (relphono E1) froze **one** segmentation (GORILA words) and then induced affixes.
This epoch runs the never-run **joint** step: word boundaries are **latent** with a calibrated
probabilistic boundary distribution, and affix statistics are **expectations over sampled
segmentations** (K=20) rather than conditioned on one. Does marginalization beat frozen-single
segmentation where truth is known (opaque LB; synthetic admin syllabary), and does LA's one validated
affix (**A- prefixation**) become more or less robust when segmentation uncertainty is integrated?

## Primary verdict (frozen rule) — `MACHINERY_UNINFORMATIVE`

The preregistered primary verdict is read from **PC-LB** (opaque Linear B TEST streams, gated by the
wrong-structure control). At the frozen inventory rule R (p ≤ 0.01, n_null = 200) the **LB-TEST gold
target is empty** (best gold candidate JO|SUF p = 0.0149) → the marginalize-vs-frozen recovery
comparison is **vacuous** → `MACHINERY_UNINFORMATIVE`. Under the D1 posthoc relaxation (p ≤ 0.05) the
target is populated (3 gold) but the **frozen** arm's wrong-structure control does not collapse
(real F1 0.00 ≤ shuffled F1 0.105), so `machinery_informative` stays False at the gate.

**Per the frozen rule, no LA interpretation is licensed from PC-LB.** LA numbers are reported below but
are **not** claimed as gate-validated. This is an under-powered-**target** artifact of the small 30 %
LB TEST split, **not** a dead detector — the controls below demonstrate the machinery works where the
target is populated.

## Where truth is known, marginalization wins (synthetic control — decisive)

Admin syllabary with 4 planted affixes; stem inventory swept from mild to hapax-heavy. Truth fully
known; target populated.

| N_stem regime | frozen F1 | marg F1 | ΔF1 (marg−frozen) | seeds ΔF1 ≥ 0 |
|---|---|---|---|---|
| 150 (mild) | 0.690 | 0.898 | **+0.209** | 5/5 |
| 600 | 0.438 | 0.860 | **+0.422** | 5/5 |
| 2400 (most hapax-heavy) | 0.133 | 0.823 | **+0.690** | 5/5 |

**GRACEFUL confirmed.** Frozen-single-segmentation morphology *collapses* as the corpus turns
hapax-heavy; marginalized morphology *holds*. The gap widens exactly where LA lives (hapax regime).

## Posthoc well-powered LB target (Gfull, all 11,908 words) — corroborates

`POSTHOC_CHARACTERIZATION` (D1; never the preregistered verdict). On a well-powered LB gold target
{A3|PRE, JO|SUF}: marginalization recovers **2/2 (F1 0.80)** where the frozen segmentation recovers
**0/2 (F1 0.00)**; the marg wrong-structure control collapses to 0. Consistent with
`MARGINALIZATION_IMPROVES` — but posthoc, so not the primary verdict.

## LA application (reported per prereg; **not** gate-licensed)

618 docs / 2,424 GORILA words / 2,530 frozen-induced words (P_MARK = 0.9).

**A- confirmatory (single preregistered LA test, n_null = 2000):**

| arm | obs (A-initial productive stems) | null mean | p |
|---|---|---|---|
| GORILA anchor (replication) | 47 | 24.9 | **0.0005** |
| frozen induced | 40 | 26.4 | 0.0020 |
| marginalized (K=20) | 39.6 | 26.4 | **0.0005** |

→ **ROBUST_UNDER_MARGINALIZATION = True** (marg p 0.0005 ≤ 0.05); **direction = IMPROVES** (marg p
0.0005 ≤ frozen p 0.0020). The one relphono-validated LA affix survives integrating boundary
uncertainty, and marginalization *sharpens* it back to the gold-anchor significance. Robust across
P_MARK ∈ {0.7, 0.9, 1.0} (GORILA-agreement F1 0.82 / 0.89 / 0.92).

**Exploratory scan (71 candidates, Holm α = 0.05): 0 survivors.** Best raw p TI|SUF 0.0145
(Holm 1.0), RA|SUF 0.017, QA|PRE 0.021 — none survive multiplicity. **No new LA affix candidate**
emerges under marginalization; A- remains the sole validated LA affix.

## Deviations (Art. XVII, append-only — prereg hash unchanged)

- **D1** — the frozen p ≤ 0.01 rule gives an empty LB-TEST gold target; added a posthoc p ≤ 0.05
  scoring pass + a better-powered Gfull target (all 11,908 words). `POSTHOC_CHARACTERIZATION`, never
  the verdict.
- **D2 (SUPERSEDING)** — the preregistered fresh-synthetic-per-sample marginalized null is mechanically
  anti-conservative (shrinks null variance ~1/K while the K segmentation samples share one real
  stream). Replaced uniformly, before any LA run, by a **stream-level** null that preserves cross-sample
  correlation and reduces exactly to the E1 word-level null for a single segmentation. Original-null
  outputs retained in `data/marginalized_morph/pc_lb.json`.

## Honest bottom line

Marginalizing over segmentation uncertainty **helps morphology exactly where the frozen approach
fails** — decisively on the synthetic hapax-heavy regime (ΔF1 up to +0.69, 5/5 seeds) and on a
well-powered LB target (F1 0.80 vs 0.00). But the **preregistered PC-LB gate came back vacuous** (empty
target at the 30 % split), so the `MARGINALIZATION_IMPROVES` direction is **characterized, not
licensed**. On Linear A itself: **A- prefixation is robust under marginalization and marginalization
sharpens it** (reported, not gate-validated), and **no new LA affix survives multiplicity** (0/71). No
LA reading of any layer; ceiling L2/L3; no transfer licence touched. The successor queue re-runs PC-LB
with a non-vacuous target (50/50 or LOO split / partial pooling) to adjudicate the direction at the
preregistered bar.
