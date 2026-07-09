# EPOCH-094 — Sequence/segmentation morphogenesis (blinded LB)

**Frontier:** F11 TURING_MORPHOGENESIS · **gate:** A · **layer:** L2
**plan_hash:** `d6618319780925724af1bed6cf70e9819e8b52d6a7b69a2b8345e22c45c4b963`
**Verdict:** **SEGMENTATION_MORPHOGENESIS_NULL** · **LA touched:** no · **licence:** none

## Question
Distinct from E091–093 (class recovery): given an unsegmented blinded-LB sign stream, does an RD/morphogenesis
boundary cue recover word boundaries better than generic unsupervised cues?

## Design
- LB words (~3.23 signs) concatenated into 15-word streams; truth = word boundaries. Held-out: stats on 70% train,
  boundary-F1 on 30% test streams (5 seeds). Boundaries predicted at the true rate (top-k) for a fair comparison.
- Cues: random · transition surprisal −log P(s₊₁|s) · forward branching entropy · **morphogenesis** |u(a)−u(b)|
  (RD Schnakenberg activator over the G_POSITION sign-type graph, unsupervised coarsest-mode selection).

## Positive control — PASSED (detects)
Synthetic planted-boundary corpus: transition surprisal 0.870 ≫ random 0.342. Task is detectable. **But even here
the morphogenesis cue reaches only 0.363 (≈ random)** — the failure is intrinsic to a static field, not data.

## Result (blinded LB, boundary-F1 at true rate)
| cue | boundary-F1 |
|---|---|
| transition surprisal | **0.650** |
| forward branching entropy | 0.369 |
| random (floor) | 0.304 |
| **morphogenesis (RD)** | **0.310** |

## Reading
- The RD/morphogenesis boundary cue is **indistinguishable from random** (0.310 vs 0.304), while the generic
  transition-surprisal cue recovers boundaries well (0.650).
- This is **architectural, not data-limited**: a static morphogenetic field is a *type-level* quantity and cannot
  encode a *sequential/transition* property like a word boundary. The PC proves it — surprisal 0.87 but
  morphogenesis 0.363 even where boundaries are trivially detectable.
- Consistent with E091/E092 (morphogenesis ties/loses to generic methods). **Byproduct** (generic, not
  morphogenesis): transition surprisal is a strong unsupervised LB boundary cue.

## F11 family status after E094
| epoch | leg | verdict |
|---|---|---|
| E091 | class recovery (mechanism) | NULL (equal-diffusion ties) |
| E092 | class recovery (specificity) | GENERIC (Turing not needed) |
| E093 | data-scale threshold | ABOVE (LA data-sufficient; weak signal) |
| E094 | segmentation | NULL (static field ≠ sequential boundaries) |
| E095 | geographic/scribal | RESERVED (next) |
| E096 | frozen-LA phonetic | DE_AUTHORIZED |

Morphogenesis provides no advantage for class recovery OR segmentation; LA is not data-limited for the weak generic
signal. **One reserved F11 epoch remains (E095).** Banking E094 advances the F12 launch gate (E094 now terminal;
only E095 blocks E097).

## Successors (5)
1. **E095 — geographic/scribal morphogenesis (queued next).** Last reserved F11 leg; regional structure is a coarser
   signal that may behave differently — but tested with the generic-best method, morphogenesis ablated.
2. **§12 map integration** of the E091–E094 F11 arc (bounded-neg 22→23; qualification 4→5).
3. **F11 closure note** — draft the family summary (mechanism-null + specificity-null + data-sufficiency +
   segmentation-null) for the exhaustion map.
4. **Generic-surprisal segmentation** cross-reference with the published segmentation_extension (0.436 micro-F1) —
   different metric; note the strong 0.650 boundary-precision-at-true-rate for the record.
5. **F12 launch prep** — once E095 is terminal, `launch_gate.py` flips and E097 (ECC/belief-propagation) starts.

Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
