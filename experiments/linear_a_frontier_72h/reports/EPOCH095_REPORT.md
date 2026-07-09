# EPOCH-095 — Geographic/scribal morphogenesis (LA site-community recovery)

**Frontier:** F11 TURING_MORPHOGENESIS (final calibration leg) · **gate:** A/E · **layer:** L2
**plan_hash:** `d04b895422a278bcec2a6196df7347d914b067bd8509a85074a2d0a95a1b7d29`
**Verdict:** **GEOGRAPHIC_MORPHOGENESIS_NULL** · **LA touched:** yes (site labels = structural metadata) · **licence:** none

## Question
Does an RD/morphogenesis process over a document-similarity graph recover LA site/regional community structure
better than generic clustering and a length confound? Truth = inscription site label (opaque signs, no values).

## Design
- LA inscriptions, sites ≥25 docs, **balanced** to 80 docs/site (HT dominates 63%), 5 subsample seeds.
- Document graph = cosine of normalized sign-frequency vectors. Methods: morphogenesis (RD activator communities) ·
  spectral · Louvain · length-only (confound) · random. Metric: site-recovery ARI.
- PC: synthetic planted-site corpus (site-specific Dirichlet distributions).

## Positive control — PASSED (detects)
Generic clustering recovers planted sites: spectral ARI **0.782** (morphogenesis 0.317). Harness has power.

## Result (balanced LA site recovery, ARI)
| method | ARI |
|---|---|
| length-only (confound) | 0.059 |
| Louvain | 0.043 |
| **morphogenesis (RD)** | **0.019** |
| spectral | 0.011 |
| random (floor) | −0.000 |

## Reading
- **No method recovers balanced LA site structure from blinded document sign-content** — all ARI < 0.06 (≈ chance).
  Morphogenesis (0.019) is no exception, and the length-only confound (0.059) is nominally the "best," i.e. what
  little separates balanced sites is document **length**, not sign content.
- LA sites share one syllabary, so document-level sign-content does not cluster by site once the HT-frequency
  imbalance is removed. Consistent with the campaign's **E012 doc→site NO_POWER/confounded**.
- This is **orthogonal to** the real *feature-level* cross-site signals (A-prefix cross-site robust E023; site
  registers E065) — those are specific features, not whole-document community structure.

## F11 morphogenesis family — CLOSED
| epoch | leg | verdict |
|---|---|---|
| E091 | class recovery (mechanism) | NULL — equal-diffusion ties Turing |
| E092 | class recovery (specificity) | GENERIC — Turing not needed |
| E093 | data-scale threshold | ABOVE — LA data-sufficient, weak signal |
| E094 | segmentation | NULL — static field ≠ sequential boundaries |
| E095 | geographic | NULL — no site community from balanced sign-content |
| E096 | frozen-LA phonetic | DE_AUTHORIZED |

**Net F11:** a graph reaction-diffusion / Turing morphogenesis process provides **no decipherment advantage over
generic methods on any tested channel**, and the recoverable structure is thin + generic. The family was built
rigorously (Turing instability verified mechanically throughout; PCs firing 5/5; frequency/degree/length/
permutation guards) and returns an honest, comprehensive negative. LA is **not** data-limited (E093) — the
constraint is signal-weakness + no licensed transfer.

## Successors (5)
1. **F12 E097 — error-correcting-code / belief-propagation (LAUNCHES NOW).** The launch gate is open
   (`MORPH_TERMINAL=True`); the cross-disciplinary family begins.
2. **§12 exhaustion-map integration** of the full F11 arc (bounded-neg 22→24; qualification 4→5; a new
   "morphogenesis channel" subsection).
3. **VERIFICATION_AUDIT** Session-8 table (E091–E095).
4. **F11 closure note** in FRONTIER_MAP (mark the family's central hypothesis refuted, comprehensively).
5. **Feature-vs-community distinction** — record that E095's whole-document site null coexists with real
   feature-level cross-site signals (A-prefix, registers), to prevent misreading E095 as "no site structure exists."

Finalization remains BLOCKED (clock 2026-07-11T03:20Z, not epoch count).
