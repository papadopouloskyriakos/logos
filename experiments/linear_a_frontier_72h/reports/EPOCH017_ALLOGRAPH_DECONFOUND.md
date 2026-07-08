# EPOCH-017 — Photograph / second-rendering allograph de-confound

**plan_hash** `3b527541f2ed427028fff73c5264394b874150257833c0f5f6cc32b0b48624c9` (frozen 2026-07-08T13:08:35Z,
before any run) · **verdict** `SITE_ALLOGRAPH_REAL` (mechanical, frozen rule) · **claim layer** L1 only
· **deviations** none.

## What this epoch answers

E012 found doc→site allograph structure in the SigLA stroke corpus (LEG1_FIRE, LEG2_FIRE) but flagged
it `ALLOGRAPH_STRUCTURE_CONFOUNDED`: a pure rendering-nuisance embedding (document ink/density/bbox-mode
metadata — no shape information at all) beat the allograph classifier (0.3307 > 0.2797 balanced
accuracy, G3 fail). Because every SigLA glyph is a single modern tracer's vector hand, "site allograph
structure" could be the tracer's session/rendering habits correlating with site, not ancient scribal
variation. E012 named PHOTOGRAPH-LEVEL re-extraction as the decisive de-confound. This epoch runs the
strongest de-confound actually obtainable.

## STEP 0 — source audit (all SOURCE_BLOCKED for pixels; feature-partition run instead)

| Channel | Checked | Finding | Status |
|---|---|---|---|
| (B) Photographs | `corpus/bronze/sigla_browse_2026/*.html`, live `sigla.phis.me/about.html`, live `sigla.phis.me/document/ARKH%207/` | SigLA ships only vector traces ("Dataset and drawings are available under CC BY-NC-SA 4.0"; document page: "Link to tablet drawing"; image files `.png` traces; no photo/drawing toggle; no photograph referenced anywhere) | **SOURCE_BLOCKED** |
| (A) Second rendering | `corpus/bronze/sign_images` (single Aegean/UFAS *font*, one idealized glyph per sign VALUE — not per-instance, not a scholarly hand-copy), `corpus/bronze/younger_lineara` (text only), full `corpus/bronze/` listing | No second independent image rendering of specific inscribed signs exists in-repo; GORILA is SigLA's stated textual basis but no GORILA plate images are shipped | **SOURCE_BLOCKED** |
| Same-scribe attribution (negative control) | `corpus/silver/`, `corpus/bronze/palaeo/`, `corpus/bronze/sigla_browse_2026/`, `corpus/bronze/younger_lineara/` | No GORILA/SigLA same-hand or scribe attribution found anywhere in-repo | **SOURCE_BLOCKED** — substituted by a rendering-shuffle null (needs no attribution data) |

Per the frozen prereg, this triggers **channel (C) FEATURE-PARTITION only** — the pre-registered
fallback, not a stall.

## Feature partition (defined from the extractor's own geometric semantics, pre-existing in the code)

E009's 10-dim stroke feature = `[n_endpoints, n_junctions, n_loops, n_components, n_strokes,
skel_len_norm, orient_0..3]`.

- **INV** (rendering-invariant) = indices 0–4: integer topology counts of the skeleton's
  critical-point graph. Skeletonization collapses stroke width and Otsu-binarization collapses
  anti-aliasing *before* these counts are taken — a single tracer's sub-pixel vectorization choices
  (curve smoothing, bezier resolution, digitization angle) should not be able to manufacture them.
  This is exactly `COUNT_IDX = [0,1,2,3,4]`, already defined in `scripts/epoch009_stroke_corpus.py:26`
  (used there for an unrelated LB-font similarity split, written before EPOCH-017 existed — not
  invented post hoc for this test).
- **SEN** (rendering-sensitive) = indices 5–9: `skel_len_norm` + the 4-bin orientation histogram —
  continuous curve/shape descriptors, directly susceptible to a tracer's habitual rendering style.
  Matches the pre-existing `ORIENT_IDX = [6,7,8,9]` plus `skel_len_norm`.

## Positive control (synthetic, known ground truth) — PASS

Reused the real doc/site/sign pairing structure; replaced feature values with synthetic
`N(0,1)` + planted per-site offsets (Cohen's-d≈1.2), confined to INV only (S1), SEN only (S2, models
a site-correlated tracer-session nuisance), or both (S3):

| Scenario | INV fires (p) | SEN fires (p) |
|---|---|---|
| S1 site-signal-only | **yes** (p=0.0005) | no (p=0.106) |
| S2 nuisance-only (site-correlated) | no (p=0.400) | **yes** (p=0.0005) |
| S3 mixed | **yes** (p=0.0005) | **yes** (p=0.0005) |

All three required sub-conditions held → `PC_PASS=true`. The partition method cleanly separates a
planted real (topology-confined) site signal from a planted rendering (curve-confined) nuisance when
they are cleanly separated by construction, and correctly recovers the real signal even when a
site-correlated nuisance co-occurs (S3).

## Main analysis — E012's legs restricted to each partition, real data

**Leg 1' (per-sign within<cross-site pairwise-distance spread, 60 signs, doc-level permutation,
N=10,000):**

| Partition | T_obs | p_raw | Holm (4-family) |
|---|---|---|---|
| INV | 0.1767 | <0.0001 | 0.0004 |
| SEN | 0.1445 | <0.0001 | 0.0004 |

**Leg 2' (doc-embedding → site, LOO balanced accuracy, 258 docs / 5 sites):**

| Partition | balanced_acc | p_raw | N2b p95 | beats N2b | Holm |
|---|---|---|---|---|---|
| INV | 0.2811 | 0.0086 | 0.2512 | yes | 0.0172 (fails <0.01 bar) |
| SEN | 0.2227 | 0.187 | 0.2576 | no | 0.187 |
| nuisance (metadata only, no shape) | **0.3307** | — | — | — | — |

**leg2' does not resolve E012's core confound in either partition**: both INV-restricted (0.2811) and
SEN-restricted (0.2227) doc classifiers stay *below* the pure-metadata nuisance embedding (0.3307) —
identical to E012's original finding. The `FIRE_INV`/`FIRE_SEN` calls below are carried entirely by
**leg1'** (the pairwise spread test), not leg2'.

`FIRE_INV = true` (leg1'_INV Holm p=0.0004<0.01). `FIRE_SEN = true` (leg1'_SEN Holm p=0.0004<0.01,
also).

## Rendering-shuffle null (adversarial; substitutes for the SOURCE_BLOCKED same-scribe control)

Shuffling SEN-partition feature values across all instances (breaking any true per-instance
correspondence, INV dims and labels untouched), 30 reps: leg1'_SEN collapse rate 0.967, leg2'_SEN
collapse rate 0.933 — both ≥0.90 → `COLLAPSES=true`. This confirms the SEN-partition significance on
real (unshuffled) data reflects genuine per-instance/per-document structure, not an artifact of the
permutation-test machinery.

**Honest limit of this null:** it shows SEN's signal is *real structure*, not test noise — it does
**not** by itself distinguish whether that structure is ancient allograph or a tracer-session artifact
(both would collapse identically under shuffling). Its diagnostic role in the frozen verdict rule is
narrower than "prove artifact vs real": it is an apparatus sanity check, exactly as flagged in the
prereg's own honest-accounting section.

## Mechanical verdict

Frozen rule: `SITE_ALLOGRAPH_REAL := FIRE_INV ∧ (rendering-shuffle null on SEN collapses)`, independent
of `FIRE_SEN`. `FIRE_INV=true`, `COLLAPSES=true` → **`SITE_ALLOGRAPH_REAL`**.

## What this verdict does and does not license (read before citing)

- **What changed vs E012:** the per-sign within<cross-site spread (leg1) — the stronger of E012's two
  confirmatory legs — survives when restricted to *pure topology counts* (endpoints/junctions/loops/
  components/strokes), a feature family that should not be manufacturable by a single tracer's curve-
  rendering choices, by the design argument in the "Feature partition" section above and validated by
  the synthetic PC.
- **What did NOT change:** the doc-level site *classifier* (leg2, E012's other confirmatory leg, and
  the one G3 flagged) is **still beaten by a pure-metadata nuisance embedding in both partitions**
  (0.2811 and 0.2227 vs 0.3307). This half of E012's confound is **not resolved** by this de-confound —
  it remains open.
- **Real data ≠ either clean PC scenario.** The PC's clean separations (S1: INV-only; S2: SEN-only)
  were designed to validate the *method*. Real data instead resembles PC's **S3 (mixed)**: both INV and
  SEN fire on leg1'. The frozen verdict rule (by design, stated in the prereg before running) grades
  `SITE_ALLOGRAPH_REAL` on `FIRE_INV` alone once the SEN-shuffle apparatus check passes — but the
  honest characterization is that this is the **weaker, mixed case**, not the unambiguous "signal lives
  only in topology" case. SEN also carrying real (non-artifactual, per the shuffle null) site-correlated
  structure is consistent with — but does not prove — genuine tracer-session-by-site confounding
  persisting alongside a topology-level signal.
- **Layer and licence:** still L1 palaeographic only (sign-form geometry). Still bounded by "one trace
  per document" (tracer-vs-scribe inseparable at the document level, per E012) — this epoch removes the
  *specific* continuous-curve/orientation rendering confound G3 caught; it cannot and does not certify
  photograph-level truth, because no photograph channel is obtainable (STEP 0). No transfer licence is
  touched either way (Art. XV `transfer_licences.json` unchanged).
- **Correct one-line summary:** *E012's pairwise-spread allograph signal survives restriction to a
  rendering-invariant topology-count feature family (validated by a synthetic ground-truth
  positive control and a rendering-shuffle null), but E012's doc-classification confound is
  unresolved and the real data show a mixed rather than a clean pattern — this downgrades, but does
  not fully dissolve, the CONFOUNDED reading, and does not amount to a photograph-verified ancient
  allograph claim.*

## Artifacts

- `epochs/EPOCH-017/{prereg.md,plan_hash.txt,result.json,DEVIATIONS.md}`
- `data/allograph_deconfound/leg_details.json`
- `scripts/e017_allograph_deconfound.py`
