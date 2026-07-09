# EPOCH-092 — Turing-specificity vs generic graph clustering (blinded LB)

**Frontier:** F11 TURING_MORPHOGENESIS · **gate:** A · **layer:** L2
**plan_hash:** `16b9f7b4b2007ac2f59f8f05400b50e8fbde95ad3ac49884f4b0ded4550becfd`
**Verdict:** **GENERIC_GRAPH_CLUSTERING (TURING_NOT_NEEDED)** · **LA touched:** no · **licence:** none

## Question
Is a Turing (graph reaction–diffusion) morphogenesis mechanism EVER specifically needed on blinded LB, or does
generic graph clustering do the same or better? E091 showed the *mechanism* (unequal vs equal diffusion) adds
nothing; E092 tests Turing against a full panel of generic baselines.

## Fairness gate (positive control) — all methods PASS 5/5
Planted-Turing block graph (k=3). Turing **and every generic baseline** recover the planted blocks 5/5:

| method | planted-PC recovered |
|---|---|
| turing · spectral · eigenmap-kmeans · eigenmap-GMM · louvain · linear-diffusion | 5/5 each |

This certifies the baselines are genuine strong detectors — so "Turing does not beat them" is a real result, not
a strawman win.

## Blinded-LB recovery (best-of-view macro-F1)
| channel | Turing | spectral | eigenmap-kmeans | eigenmap-GMM | Louvain | linear-diffusion |
|---|---|---|---|---|---|---|
| role | 0.675 | 0.618 | 0.636 | 0.554 | 0.406 | **0.798** |
| vowel | 0.453 | 0.396 | 0.490 | 0.437 | **0.491** | 0.372 |
| consonant | 0.194 | 0.169 | 0.164 | 0.141 | 0.109 | **0.200** |

**A generic baseline matches or beats Turing on every channel.** role: linear-diffusion (0.798) > Turing (0.675);
vowel: Louvain (0.491) > Turing (0.453); consonant: all ~chance (8-class).

## Reading
- Turing morphogenesis confers **no recovery advantage** over generic spectral / community / heat-kernel
  clustering on blinded LB. The diffusion-driven instability is not specifically required.
- The recoverable structure is itself thin: role is largely the trivial syllabogram-vs-other (degree) split,
  vowel tops out at ~0.49, consonant is chance.
- With **E091** (equal-diffusion ties full Turing) this **refutes the F11 central hypothesis** — a Turing
  mechanism does not recover linguistic structure better than generic clustering. Consistent with **EPOCH-016**
  (SBI: raw-cosine spectral ties/beats fancy methods on this corpus).

## Successors (5)
1. **E093 — LB→LA degradation surface (queued next).** Reframed post-E092: use the *generic-best* graph method
   (not Turing) to map how role/vowel recovery degrades from LB toward LA conditions; locate whether LA is
   above/near/below any detection threshold. Distinct, load-bearing (informs the decipherment-threshold question).
2. **E094 — Segmentation morphogenesis.** Different graph (position/boundary) + task (boundary recovery) vs
   DP/Bayesian/MDL — not pre-decided by the class-recovery result; run with generic + Turing side by side.
3. **E095 — Geographic/scribal morphogenesis.** Regional structure is a coarser signal that may behave
   differently; test generic-vs-Turing on site/scribe graphs.
4. **E093b — degradation of the Turing-vs-generic GAP.** Does the (currently zero) Turing advantage ever become
   positive as the graph is degraded? Tests whether Turing helps specifically in the low-data regime.
5. **F11 closure note** — draft the family summary (E091+E092 refute the central hypothesis) for the §12 exhaustion
   map; de-authorize E096 (frozen-LA phonetic application) since its calibration gate failed.

**E096 (frozen LA phonetic-class application) is de-authorized** — it was gated on a Turing-specific positive that
E092 refutes. Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
