# EPOCH-002 — Higher-order substitution motifs (frontier F3)

**Campaign** linear-a-frontier-72h · branch `research/linear-a-frontier-72h` · seed 20260708
**Prereg** `epochs/EPOCH-002/prereg.md`, plan_hash `09c55c9e42406393d278299569007d085e1bc9c558ca388ca4715f76b34cadae`, frozen 2026-07-08T03:27Z **before** any analysis ran.
**Articles** V, VII, VIII, IX, XI/XII, XV, XXII. **Claim layer: L2 relative/structural.** No value
is proposed; no transfer licence is earned.

## Question

The flat substitution-neighborhood bridge was `NO_POWER` even on known LB↔Cypriot
(anchor-lattice F2: best exact 0.064, zero Holm survivors), while the within-script flat channel
is real (same-C AUC 0.700 full / 0.750 freq-disjoint). Do HIGHER-ORDER motifs do better —
tested on the known script first?

Three preregistered families, all built from sign identity + document metadata only (values
grade only): **MF_A** trigram frames (joint prev/next 2-sign contexts, boundary-padded),
**MF_B** formula(series)-controlled substitution slots, **MF_C** site-stratified mean Jaccard.

## Positive control (gated first)

Flat full-corpus same-C AUC = **0.6999**, inside the frozen [0.68, 0.72] window → detector intact.

## Leg 1 — within-script (opaque LB, 72 signs, 2,556 graded pairs): `MOTIF_WITHIN_EQUIVALENT`

| family | same-C AUC fd | label-null Holm p | Δ vs flat (boot 95% CI, fd) | LOSO wins | verdict |
|---|---|---|---|---|---|
| FLAT | 0.750 | (0.001, outside Holm set) | — | — | baseline |
| MF_A trigram | 0.682 | 0.006 | [−0.171, +0.031] (full: [−0.133, −0.016]) | 0/6 | EQUIVALENT |
| MF_B formula | 0.753 | 0.006 | [−0.100, +0.117] | 0/6 | EQUIVALENT |
| MF_C site | 0.761 | 0.006 | [−0.078, +0.115] | 0/6 | EQUIVALENT |

All three families carry the C-axis (all 6 family×axis tests survive Holm against the
frequency-matched label null; degree-preserving nulls all pass at p = 0.005), but **none beats
flat**: 0/6 LOSO wins each, bootstrap CIs straddle 0 (MF_A is significantly *worse* on the full
corpus). Point estimates MF_B/MF_C ≥ flat on freq-disjoint are within noise.

**Adversarial discovery — the wrong-language control FAILED for every family *including flat*:**
on a within-word-shuffled corpus the same-C AUC stays at 0.60–0.64 full / 0.65–0.70 fd
(prereg pass bar: < 0.55). Two honest readings, jointly: (i) a large share of the C-axis signal
is **order-free** — carried by word-level sign composition (paradigm words differing in one sign
share the rest of their bag), not by sequential substitution structure specifically; (ii) the
shuffle is only weakly destructive for short words (18% of LB types are 2-sign, 35% 3-sign).
Either way, **the mechanistic attribution "substitution structure" in F1/C_AUDIT is now
constrained**: their label-null significance stands, but "substitution" vs "co-occurrence
composition" is not separated by that machinery. (F1 itself never ran this control.)

## Leg 2 — cross-script on KNOWN scripts (MF_A only; MF_B/MF_C SOURCE_BLOCKED — cog lexical lists carry no series/site metadata): `MOTIF_CROSS_SUPERIOR`

| pair | n | best motif exact | flat exact | Holm-12 exact survivors (motif) | flat survivors |
|---|---|---|---|---|---|
| CTRL LB split-half (identity) | 71 | **M1 0.775** (all 4 methods survive) | 0.408 | M1,M2,M3,M4 | M1,M3,M4 |
| KNOWN LB-cog↔Cypriot-cog | 47 | **M1 0.149**, p=0.001 | 0.064 | **M1:exact** (+M1:conC) | **none** |

The trigram-frame geometry nearly doubles the identity ceiling (0.408→0.775) and produces the
**first Holm-surviving exact recovery on the genuine cross-script pair** where the flat bridge
had zero survivors. M1 hits: A, E, KE, TE, KA, O, MA.

Post-hoc diagnostics (declared; verdict-neutral):
- **Frequency-rank adversary**: matching purely by support rank gets 3/47 (p = 0.085), overlap
  with M1 = {KE} only → not a frequency artifact.
- **Order destruction**: within-word shuffle of both scripts collapses M1 to 0.043 (p = 0.25)
  → the KNOWN cross-script signal **is genuinely sequential** motif geometry.
- Caveat: only the anchor-seeded M1 (LOO over 46 seeds) survives; unsupervised M2/M3 stay at
  the floor. The bridge works in **seeded** mode only.

## Leg 3 — conditional LA application (triggered per prereg): `LA_MOTIF_GEOMETRY_CONSISTENT_WITH_AB_HOMOMORPHY_L2`

REAL LA-silver ↔ LB-DĀMOS, graded against the **AB shape-homomorphic PROPOSAL** (51 signs;
this is a hypothesis, not ground truth). M1-LOO exact **0.157 (8/51), p = 0.001, Holm-12
survivor**; consonant-class 0.255 (p = 0.001, survivor). Flat baseline: 0.078, zero survivors.
Hits: SI, MI, SA, DI, QE, PU, TO, AU — spread across ranks 6–50, zero overlap with the
frequency-rank adversary (2/51, p = 0.25).

**Caps (read before quoting):**
1. This is a **consistency** test: M1 seeds on the other 50 *proposed* homomorphic pairs, so a
   survivor says the LA motif/co-occurrence geometry coheres with the homomorphic system above
   chance — it does **not** independently recover values, and 43/51 signs misalign.
2. Order destruction only reduces it to 0.118 (p = 0.001): unlike KNOWN, the LA↔LB coupling is
   **substantially composition-driven** (order-free co-occurrence), with a smaller sequential
   component. The composition flavor is adjacent to the historically NULL raw-distribution
   channel (those NULLs were unsupervised/differently graded — no formal contradiction, but
   interpretive weight shifts).
3. L2 only; capped ≤ 0.75 as a signal; **no licence change** (`SEMANTIC+ NOT_AUTHORIZED`
   unchanged; STRUCTURAL licence still not earned — that requires the full analogue protocol).

## Epoch verdict

**Within-script: `MOTIF_WITHIN_EQUIVALENT`. Cross-script: `MOTIF_CROSS_SUPERIOR`.**
Higher-order motif geometry does not improve same-script class recovery, but it restores
cross-script power the flat bridge lacked — the first Holm survivors on both the KNOWN pair
(order-dependent, frequency-clean) and the LA↔LB homomorphy-consistency pair (largely
composition-driven). Plus one new negative constraint: the within-script consonant axis is
substantially order-free, which weakens the "substitution structure" mechanism story attached
to F1/C_AUDIT.

## Artifacts

`data/motifs/E002_{within_script,cross_script,la_leg,posthoc_audit,posthoc_shuffle_cross}.json`;
scripts `scripts/e002_*.py`; prereg + result at `epochs/EPOCH-002/`.

## Successor tasks (ranked)

1. **Seed-poverty curve for the motif bridge (KNOWN pair):** M1 works with 46 seeds; LA offers
   ~5 firm toponym equations at best. Sweep n_seeds ∈ {3,5,10,20,46} on LB↔Cypriot; find the
   minimum seed budget at which the motif bridge still fires. Decides whether the LA
   application can ever run in an honestly-seeded mode.
2. **Composition vs order decomposition as a first-class channel:** build an explicitly
   order-free bag-composition similarity + an explicitly order-only (composition-controlled)
   motif similarity; re-run both legs; assign each prior finding (F1 C-axis, LA↔LB coupling)
   to its true channel; file the F1 mechanism constraint as a notes-level ERRATUM candidate on
   the anchor-lattice F report.
3. **Frame-ablation on the KNOWN hits:** which trigram frames (word-boundary frames?) carry
   the transportable signal for A,E,KE,TE,KA,O,MA; derive a typology of transport-stable
   contexts; test whether those frame types exist with usable support in LA.
4. **Cross-script MF_B on LA↔LB:** formula-controlled frames were SOURCE_BLOCKED only on the
   cog lists — LA and LB both have document/series structure; run the formula-slot bridge
   LA↔LB (and site-stratified MF_C: HT/ZA/KH vs KN/PY/TH) under a new prereg.
5. **Power curve via corpus scaling:** subsample DĀMOS to Cypriot-cog size and below; map M1
   motif-bridge exact accuracy vs corpus size on the KNOWN pair; locates LA (539 packed words)
   on the curve — an honest expected-power statement before any further LA claims.
6. **Ensemble within-script channel:** MF_C site-replication (0.761) + flat (0.750) + MF_B
   (0.753) ensemble under the same holdouts — the only remaining within-script headroom.
