# Cretan-anchor one-shot — result & honest interpretation (2026-07-06)

The minted preregistration (`plan_hash 2eab1536…`, commit `a0b2403`) was run **once**, fail-closed
against the pinned hashes (`cretan_oneshot_verdict.json`, commit `1e5c33b`). Then the positive result was
adversarially stress-tested (`wf_7ddc21a2-027`, 5 agents). **Bottom line: the mechanical pre-registered
verdict is `CONFIRM_GENERALIZES`, but the honest interpretation is `RECOVERED_TRIVIAL` — a NULL in
substance.** The discipline caught a false positive before it propagated.

## Pre-registered mechanical verdict (stands, no retune — invariant 3)

| | value |
|---|---|
| `r1_M2` | **3** / 3 |
| `r1_B_id` (identity edit-distance) | 1 |
| `r1_B_egy` (generic-Egyptian, strict identity) | 1 |
| permutation p (N=10 000) | 0.0014 (null r1 hist `{0:9062,1:881,2:44,3:13}`) |
| verdict | `CONFIRM_GENERALIZES` |

Per anchor: Knossos `k-n-š`→`k-n-s` (M2 1 / B_id 2 / B_egy 10); Amnisos `m-n-š`→`m-n-s` (1 / 2 / 13);
Lyktos `r-k-t`→`r-k-t` (1 / 1 / 1).

## Why the honest interpretation is TRIVIAL / NULL

Adversarial verification (all four lenses returned **ARTIFACT**; adjudication `DOWNGRADE_TO_TRIVIAL`,
`result_stands: false`):

1. **A fair baseline ties M2.** A model-free baseline that folds the single obvious sibilant equivalence
   (Egyptian `š`-group = foreign /s/) also reaches **3/3** top-1 — tying M2 with strictly less information.
   The pre-registered `B_egy` was under-specified as *strict char-identity*, which refuses the one fold
   that decides the test (that is what manufactures M2's ranks of 10 and 13). Against a fair generic-Egyptian
   comparator, the prereg's own `RECOVERED_TRIVIAL` branch (`r1_M2 ≤ max(baselines)`) fires.
2. **The whole edge is one record.** M2's only discriminating correspondence is foreign /s/ → Egyptian `š`,
   learned from **exactly one** training pair (`HV-0234`, `p-s-l` → `ma-p-ši-l-ta`). **Leave-one-out of that
   single record flips the verdict 3→1 (REFUTE)** — Knossos and Amnisos fall to rank 2. Support is n=1 in the
   used direction — below any reasonable information floor (invariant 7) for a load-bearing claim.
3. **Effective evidence ≈ 1, not 3** (invariant 8 / effective-n). Lyktos (`r-k-t`→`r-k-t`) is a pure-identity
   freebie every baseline gets. Knossos and Amnisos both hinge on the *same* terminal `š→s` rule (and even
   share the medial `-n-`). So "3/3" = 1 identity freebie + one rule applied twice. **Do not use the prereg's
   unqualified-3/3 language.**
4. **Mechanism mislabel.** What recurs is an **Egyptian scribal orthography** convention (group-writing of
   foreign sibilants), *not* a Semitic–Aegean phonological or lexical link. Correct scope: "the Egyptian
   rendering convention for foreign /s/ recurs on the Cretan ovals" — never "a Semitic-trained correspondence
   generalizes to Aegean phonology."
5. **Homophony.** Recovering the `k-n-s` *skeleton* over a de-duplicated pool is not uniquely recovering
   "Knossos" (7 DĀMOS wordforms share `k-n-s`; Amnisos 7; Lyktos 12). Top-1 identifies a consonant class; do
   not headline "ranked all 3 Cretan toponyms at top-1."
6. **The p-value tests the wrong thing.** `p=0.0014` / 9.48 bits establishes non-randomness only (M2 beats
   random refitted maps). It does **not** test robustness to M2's own support (LOO flips it) nor M2 vs a fair
   fold baseline (which ties it). It must not be cited as evidence of non-trivial generalization.

## What is NOT wrong (do not over-downgrade)

The harness is honest — **no bug, no leak, no preprocessing cheat**. The Lev ≤1 skeleton-collision holdout is
real and `HV-0234` legitimately survives it (its skeleton `p-s-l` is Lev ≥2 from every target). The `s↔š`
alternation is a genuine Egyptian-orthography phenomenon the model learned unsupervised. Edel read the final
sign as `š` — *different* from the answer `s` — which **mitigates** the §15.6 reading-circularity worry rather
than driving it. The defect is the **triviality/fragility of the CLAIM**, not contamination or fraud.

## The flaw this exposes in the minted prereg (lesson for any v3)

The pre-registered baseline set (`B_id` strict edit-distance, `B_egy` strict identity) omitted a
**fold-tolerant** generic-Egyptian baseline. Because the one correspondence that decides the test is a single
sibilant fold, a fair baseline had to include it — and neither did. The pre-mint verification did not catch
this; the post-run skeptic did. A future v3 (fresh plan_hash) must (a) include a sibilant-fold generic-Egyptian
baseline, (b) require support > n=1 for any load-bearing correspondence (information floor), and (c) use
anchors that exercise *independent* correspondences, not the same rule twice.

## Consequence for the gate chain

The downstream vocalization / Linear A probe (and any sound-JEPA) is **NOT licensed** — the "confirmation" was
trivial, so there is no validated instrument to build on. The ≤0.75 cap bounds propagation but does not rescue
a mislabeled positive: a `RECOVERED_TRIVIAL` dressed as `CONFIRM_GENERALIZES` would authorize further work on a
false premise. **Corrected: this is another honest NULL** — the Egyptian→Aegean channel is not shown to
generalize. That null is the insurance-policy outcome the project exists to produce, not a failure.

*Discipline: the mechanical verdict stands as the pre-registered outcome; nothing was retuned or re-run. This
report corrects the interpretation only. Firewall vs Linear A intact.*
