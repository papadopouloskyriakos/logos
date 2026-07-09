# EPOCH-077 REPORT — Does glyph SIZE mark document-INITIAL prominence (a spatial heading marker)?

**Campaign:** Linear A frontier-72h · **Epoch:** 077 · **Layer:** L2 (structural graphic; signs opaque, no reading)
**Task:** Is the document-initial glyph systematically LARGER (spatial prominence/heading marker), or is glyph
size purely a per-sign property (E076)? Spatial modality.

---

## 1. Question & non-circular design

E076 found normalized glyph SIZE is a shared cross-site per-SIGN convention. E077 asks whether size ALSO marks
POSITION — specifically whether the document-**initial** glyph is systematically larger (the visual analog of
the campaign's positional findings: E022 A-prefix heading role, E062 document-peripheral markers, E069
entry-initial word longer) — or whether size is independent of position.

**Non-circular:** glyph size = within-document z-scored log bbox-area (removes per-photo scale); position =
glyph index in transcription order (0 = first). The two are independent measurements. **Null = within-document
position shuffle**: permute each doc's glyph order preserving its size multiset, recompute D_init. Under it
E[D_init] ≈ 0 (verified: null mean = +0.0004). Signs are opaque catalog IDs; no phonetic value, reading, or
meaning. L2 only.

**Metric (frozen):**
- `D_init = mean over docs of (z-size of glyph 0) − (mean z-size of glyphs 1..n-1)`. D_init > 0 ⇔ initial larger.
- `rho = mean within-doc Pearson(z-size, position index)` (secondary, context).

## 2. Data

`data/sigla_glyphs_bbox.json`, dividers excluded, docs with ≥4 non-divider bbox glyphs: **322 docs**.
Sites with ≥15 docs: Haghia Triada (169), Khania (52), Zakros (28), Phaistos (20), Knossos (19).

## 3. Inspection (descriptive, pre-verdict)

Global D_init = **−0.057** (initial glyph slightly *smaller*, not larger). rho = −0.041 (weak negative).
Per-site directions already inconsistent (HT positive; Khania/Phaistos/Knossos negative; Zakros flat).
Coordinator prior (no global initial-prominence) confirmed descriptively.

## 4. Positive control (SYNTHETIC — gates verdict)

| check | result |
|---|---|
| DETECT (plant initial-prominence, effect=0.35 z) | flagged 25/25 replicates → **power_est = 1.0** |
| FALSE-POSITIVE (position-independent size) | rejected 1/25 → **false_pos_rate = 0.04** (≤ 0.10) |
| Null calibration | E[D_init] under shuffle = +0.0004 (≈ 0) ✓ |
| **PC verdict** | **PASSED** (synthetic) |

The machinery reliably detects a real planted prominence and does not fire on position-independent size. The
negative global result below is therefore a **well-powered bounded negative**, not a machinery failure.

## 5. Global result

| quantity | value |
|---|---|
| n_docs | 322 |
| D_init (observed) | **−0.0569** |
| D_init (null mean ± sd) | +0.0004 ± 0.0633 |
| p_init (one-sided initial-larger, 4000 draws) | **0.814** |
| rho(pos, size) | −0.0414 |

Global D_init is **not significant** (p_init = 0.814) and the sign is *negative* — the initial glyph is not
larger globally; if anything marginally smaller.

## 6. Cross-site result

| site | n_docs | D_init | null | p_init | sig | direction |
|---|---|---|---|---|---|---|
| Haghia Triada | 169 | +0.148 | −0.0002 | **0.0478** | **yes** | larger |
| Khania | 52 | −0.395 | −0.0024 | 0.990 | no | smaller |
| Zakros | 28 | −0.039 | −0.0010 | 0.582 | no | smaller |
| Phaistos | 20 | −0.344 | −0.0021 | 0.899 | no | smaller |
| Knossos | 19 | −0.188 | −0.0052 | 0.755 | no | smaller |

Sites significant initial-**larger**: **1 of 5** (Haghia Triada only). Directions are **inconsistent**
(HT larger; the other four smaller or flat).

## 7. Frozen mechanical verdict

PC PASSED (power_est = 1.0). Global D_init NOT significantly > null (p_init = 0.814, and negative). Exactly
**1 site** significant initial-larger (HT), so not ≥2 same-direction sites.

→ **`SPATIAL_SIZE_POSITION_SITE_LOCAL`**

A positional size effect exists but is **site-local and direction-inconsistent**: Haghia Triada alone shows a
significant initial-larger glyph; the other four sites do not, and three trend initial-*smaller*. This is not a
shared cross-site convention.

## 8. Bottom line

Glyph size does **not** mark document-initial prominence as a cross-site spatial convention. Globally the
initial glyph is not larger (D_init = −0.057, p_init = 0.814), and the only significant initial-larger signal
is a **local Haghia Triada habit** — the other four sites are non-significant and mostly trend the opposite way.
So: glyph size is **primarily a per-sign property** (consistent with E076), with at most a **site-local**
positional use at Haghia Triada, not a pan-Cretan heading/prominence marker. This is a well-powered bounded
negative on the cross-site claim (PC power = 1.0), with one honest site-local exception.

## 9. Successors (≥5)

- **E078:** Is HT's initial-larger effect driven by a sign *class* (logogram vs syllabogram) at position 0, not size per se?
- **E079:** Does size mark *line*-initial or *entry/clause*-initial position (via bbox x-coordinate segmentation), finer than document-initial?
- **E080:** Per-sign conditional model: controlling for which sign sits at position 0, does any residual positional size effect remain?
- **E081:** Does size mark document *periphery* (first OR last / margins) bidirectionally, paralleling E062?
- **E082:** Dedicated one-sided null test of the secondary rho (monotonic size-by-position trend).
- **E083:** Is the HT initial glyph larger than its *own sign's* typical size, or just a large sign that happens to sit first?

---
*Opaque sign IDs only (e.g. AB59). Structural size = bbox area. No phonetic value, reading, or meaning. Layer L2.*
