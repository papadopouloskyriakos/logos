# EPOCH-010 — Channel-capacity bound + ensemble + hub anchors (the E003/E006 door)

**Verdict: `DOOR_MARGINAL` — by one razor-thin quantity.** The seed-span metric class is
**formally exhausted** (oracle probes WITH full ground-truth leakage stay below the required
rate), ensembles and hub anchors are FLOOR everywhere, and the only bound above the bar is
the three-expert union ceiling, which sits **exactly at** the requirement (median margin
+0.000 at the LA operating point).

Frontier F3 · gates A/G · plan_hash `0380e6c327b72fa1a0e65d9d95dff93572de95b783fb70e2c4de9783daa878fe`
(prereg frozen 2026-07-08T04:47:58Z before any corpus run) · seed 20260708 · claim layer **L2**
(KNOWN-script calibration only; no LA data touched; licences unchanged).
Articles: V, VII, VIII, IX, XI, XII, XV, XXII.

## Question

E003: at LA's budget (b=5 seeds) the Holm bar needs hit rate ≈0.119–0.122; M1 delivers 0.039.
E006: better estimator geometry recovers half the gap (→0.071) then saturates; suspect =
channel SNR. E010 asks the terminal question three ways, all on the KNOWN LB-cog↔Cypriot-cog
pair (E003 discipline, replicate-paired RNG streams, 20 reps, 1000-perm nulls, frozen bar
0.05/12 = 0.0041667):

1. **Capacity**: does ANY estimator-free bound at b=5 exceed the required rate?
2. **Ensemble**: can decorrelated errors of {M1, EST_GW, EST_OT} be fused across the bar?
3. **Hub anchors**: do high-frequency/high-centrality seeds (LA's real anchor profile) beat
   uniform draws?

Required rate, measured mechanically per replicate (c_req from the same 1000-perm null):
median 0.122 at f=0.75 (H≈41), 0.119 at f=1.0 (H=42) — E003's headline confirmed.

## Gates (all behaved)

- **PC0** harness identity: PASS (KNOWN M1-LOO 7/47, CTRL 55/71, paths identical).
- **PC_CAP** (capacity power, CTRL identity, b=5): all probes exceed (LIN .227, CCA .235,
  BATTERY .242, PICK3 .530 vs required ≈.076) — the probes can see a real signal at 5 seeds.
- **NEG_CAP** (scrambled GT): no probe OVERFIT_BROKEN (margins −.048 to −.071) — the oracle
  leakage does NOT manufacture capacity; the clean numbers are channel, not overfit.
- **NEG_ENS / NEG_HUB** (5-wrong-anchor scramble): FLOOR — detectors intact.

## Part 1 — Capacity at b=5 (KNOWN; f=0.75 = LA operating point)

| probe | leaks GT? | acc median | required | margin | exceeds |
|---|---|---|---|---|---|
| CAP_ORACLE_LIN (ridge fit on ALL pairs) | yes | .073 | .122 | −.048 | no |
| CAP_ORACLE_CCA (CCA fit on ALL pairs) | yes | .096 | .122 | −.036 | no |
| CAP_BEST_BATTERY (max of 10 honest rules) | selection only | .073 | .122 | −.049 | no |
| **CAP_ORACLE_PICK3** (per-sign best of M1/GW/OT) | selection per sign | **.143** (mean .136) | .122 | **+.000** | **yes** |
| CAP_FANO (Gaussian-CCA MI, report-only) | — | bound .333 | .122 | vacuous | (declared) |

f=1.0 is the same picture (LIN .083, CCA .095, BATTERY .083 below .119; PICK3 .143, +.024).

**The exhaustion result inside the marginal verdict:** even an oracle that fits the metric on
the complete ground truth cannot push 5-seed-span profile features past the bar. Every
estimator of the E002/E003/E006 lineage — and any future linear/metric variant on b=5 anchor
profiles — is now formally bounded below the requirement. That family is closed, with a
leakage-validated proof (NEG_CAP clean).

**The one surviving quantity:** the union of the three experts' correct predictions touches
the required rate exactly (post-hoc: margin median +0.000, mean +0.007; 45% of reps strictly
above, 60% at-or-above; at f=1.0: +0.024, 60% strictly above). This ceiling is unrealizable
by construction unless a selector knows, per sign, which expert to trust.

## Part 2 — Ensemble (the selector does not exist)

Error-set overlap FIRST, as preregistered: pairwise error-Jaccard **.894–.930** — the three
estimators share ~90% of their errors; sub-prediction (a) confirmed. Unique correct
contributions are spread across ALL three experts (OT 49 / GW 30 / M1 19 sign-hits at f=0.75)
and across 32 distinct signs — no concentrated structure a realizable selector could key on.

| cell (b=5) | f=0.75 | f=1.0 |
|---|---|---|
| ENS_RANK (fused rank) | FLOOR .068 (med_p .081) | FLOOR .080 (med_p .052) |
| ENS_POE (product of experts) | FLOOR .051 (.262) | FLOOR .070 (.096) |

Fusion lands between the best single expert (EST_OT .071) and the union ceiling (.136),
recovering ~0 of the +.052 selection headroom. No new information: confirmed.

## Part 3 — Hub-stratified anchors (LA's anchor profile buys nothing)

Top-quartile-support and top-quartile-centrality 5-seed draws vs uniform references
(E003 M1 .034/.039; E006 EST_OT .071/.071): all 8 cells FLOOR; hub beats uniform in only
**3/8** cells (best: HUB_CEN M1 f=1.0 .048 vs .039). Committed sub-prediction (c)
(≥5/8 better, P=.70) is **REFUTED** — the fact that LA's five firm anchors are high-frequency
toponyms does NOT mitigate the seed-poverty wall; if anything HUB_SUP hurts M1 (.021 vs .034,
plausibly because top-support seeds have redundant, mutually similar profiles).

## Mechanical verdict

No claim-bearing cell ≥ NOMINAL (12 cells, all FLOOR; families' NEG gates ok) → not REOPENED.
PC_CAP passed and CAP_ORACLE_PICK3 (valid, NEG_CAP-clean) EXCEEDS at f=0.75 → CLOSED
unavailable by the frozen rule → **DOOR_MARGINAL**. Committed distribution had MARGINAL modal
(.45): landed. Sub-predictions: a,b,e,f confirmed; c refuted; d occurred (the declared
decisive uncertainty, P=.45).

## Reading — what "marginal" now means (much sharper than E003's)

The door is no longer "estimator geometry might fix it" (E006 killed that) nor "the channel
rate exceeds the requirement" (that was estimator-relative). After E010 the ENTIRE remaining
opening is: *a per-sign expert-selection oracle worth +.05 accuracy whose ceiling coincides
with the bar to the third decimal, with zero realizable selector signal found.* Practically:
- any Holm-surviving 5-seed bridge on this channel would need a selector carrying genuinely
  NEW information (outside the motif graph — e.g., stroke/epigraphic or document-context
  features), not a recombination of existing costs;
- and even a perfect selector would sit AT the bar, not above it — one lost sign breaks it.

For LA planning: the honest requirement stays E003's — grow the anchor set toward ~46, or
change channels. The seeded-bridge family on trigram-motif geometry is exhausted for every
metric/linear estimator class (proved), and effectively exhausted for fusion (measured);
it is NOT formally exhausted only because of the zero-margin union ceiling.

**LA application stays BLOCKED** (nothing here earns anything; Art. XV unchanged).
Effective-n: 12 preregistered cells × 20 reps + 4 capacity cells × 20 reps + controls; one
endpoint; zero tuning (all hyperparameters frozen in prereg). Runtime 4.6 s + posthoc.

## Successors (non-termination rule; ≥2 non-equivalent since F3 is *de facto* spent)

1. **F3-terminal micro-epoch — selector-information test**: preregister ONE cell asking
   whether E008 stroke-graph features (per-sign epigraphic MRR 0.273 channel) can act as the
   per-sign expert selector; if not, F3 is closed outright (the union ceiling is provably
   unreachable).
2. **New frontier — paleographic bridge (out of F3)**: use SigLA stroke anatomy as the
   PRIMARY cross-script similarity (not a selector), calibrated LB↔Cypriot signary shapes
   first; independent of the motif graph whose SNR is the proven binding constraint.
3. **New frontier — anchor growth, not estimator growth**: the measured requirement is ~46
   anchors; a prereg'd pipeline for candidate LA↔LB toponym equations (Anetaki II prospective
   gold, seal co-occurrence, fraction-system joins) with the E003 anchor-integrity gate,
   targeting the seed axis directly.
4. **Document-context channel**: E010 showed word-graph SNR is the wall; per-DOCUMENT
   co-occurrence graphs (tablet-level, series-stratified) are a different generative process —
   run the same b=5 calibration once, KNOWN pair, before any further estimator work.
5. **Requirement-relaxation study (formal)**: the bar 0.119 assumes exact top-1 recovery;
   preregister the top-3/consonant-class requirement curve at b=5 — if class-level recovery
   Holm-survives where exact fails, the useful L2 deliverable changes shape.

Artifacts: `data/motifs/capacity/{E010_result.json, E010_pc0.json, E010_posthoc.json}` ·
`scripts/{e010_channel_capacity.py, e010_posthoc.py}` ·
`epochs/EPOCH-010/{prereg.md, plan_hash.txt, result.json}`.

*Compliance (Art. XXII): stage opened with articles + gates + frozen plan; PC first; NEG/ADV
controls behaved; verdict mechanical per frozen rule; oracle leakage declared as
bound-machinery and validated against scrambled GT; append-only record; no LA data touched.*
