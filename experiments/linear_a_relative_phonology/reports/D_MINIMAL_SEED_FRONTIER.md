# D4 — Minimal-seed frontier: how much external information recovers the relative classes?

**Question.** Seeded label-spreading (D3 harness) can attach the relative vowel/consonant partition to
values *if* you supply some correctly-labelled seed signs. How many seeds, and of what **type**, do you
need before the recovery is real (beats the matched random-seed null)? We build the frontier on the
**Linear B known-truth control** (the V/C partition is gradable there) and then locate Linear A on it.

**Constitution.** L2/L3 relative-structure census; earns NO transfer licence. NON-CIRCULAR (Art. XII):
known LB `{A,E,I,O,U}` seed and grade held-out recovery **only** — never a model feature; `log_freq`
dropped from propagation. Harness = the audited D3 pipeline (kNN-RBF position affinity + substitution
affinity → Zhou-2004 label spreading → held-out AUC/recall), imported read-only. Seed `20260708`.
Artifacts: `scripts/d4_minimal_seed_frontier.py` → `data/D4_frontier.json`.

Control geometry: `n_signs=74` at freq≥20, `n_vowels=5` (A,E,I,O,U), base-rate 0.068.

---

## 1. Seed types (the "type" axis)

| type | selection rule (on the LB control) | LA analogue |
|---|---|---|
| `random` | k signs, labels carry **no** true info | unlimited but value-blind |
| `shape_selected` | value-blind draw (shape ⊥ value: WP-F circular/≤0.75, G3 "shape alone can never be SEED_A") | SigLA shapes; value-blind |
| `secure_shared` | k **TRUE** vowels + k **TRUE** consonants (a bilingual / secure shared-sign value) | **0** (no bilingual; relabeling-invariant) |
| `anchor_derived` | correct seeds drawn ONLY from the SEED_B toponym-anchor pool; true vowels there are just **{A,I}** ⇒ caps at k=2 | ≤2 on paper, **0** after LOTO |
| `incorrect` | k true consonants mislabelled vowel + k true vowels mislabelled cons | the risk of trusting disputed anchors |

k = number of correct vowel-class seeds (matched k consonant seeds), k∈0..5. **The vowel class has only 5
members, so k=5 seeds all of them (no held-out vowel): the V/C frontier SATURATES at k=4.** "k=5+" is
degenerate on this axis, not a higher-power regime.

Honest signal = **lift over the random-seed null at matched k**. The null shares the identical
graph+frequency structure, so `type − random` nets out the D3 frequency leak and isolates the
information carried by the seed **values**.

---

## 2. The frontier on the LB control (channel pos+sub, primary)

Random-null held-out AUC ≈ **0.50** at every k (mean), but its **95% CI upper is wide (0.79–0.84)** —
with only ~1–4 held-out positives, a rank-stat AUC lets random seeds recover by chance surprisingly often.
That wide null is the whole difficulty.

| type | k=1 | k=2 | k=3 | k=4 | recall@k (k=4) | beats null CI95-upper? |
|---|---|---|---|---|---|---|
| random (floor) | 0.496 | 0.503 | 0.488 | 0.488 | 0.05 | — |
| shape_selected | 0.504 | 0.507 | 0.507 | 0.486 | 0.06 | never |
| **secure_shared** | 0.698 | 0.744 | 0.750 | **0.805** | 0.11 | **only at k=4** |
| anchor_derived | 0.624 | 0.723 | *n/a* | *n/a* | — | never (exhausted at k=2) |
| incorrect | 0.322 | 0.251 | 0.223 | 0.214 | 0.00 | never (actively harmful) |

`lift(secure_shared)` over the null mean is real and monotone: **+0.18 / +0.25 / +0.25 / +0.31** for
k=1..4. But statistical separation from the *matched* null (AUC > null CI95-upper ≈ 0.79) is reached
**only at k=4** — four of the five vowels already correctly known.

**Channel dependence.** On the position-only channel (`pos`) secure_shared climbs 0.608→0.684→0.690→0.759
but **never** clears its null CI95-upper (0.80–0.85): even k=4 is not separable. So the single marginal
"pass" at k=4 exists **only** when the substitution channel is added, and even then it is marginal
(0.805 vs 0.793).

**Frontier k\*** (min k where AUC beats null CI95-upper / where recall≥0.5):

| type | pos+sub | pos |
|---|---|---|
| secure_shared | **k=4** (recall≥0.5: never) | never |
| anchor_derived | never | never |
| shape_selected / random / incorrect | never | never |

---

## 3. Reading the frontier honestly

1. **Value-blind seeds recover nothing.** `random` and `shape_selected` sit flat on the 0.50 floor at
   every k. This is the measured price of relabeling-invariance: selecting seeds by shape (the only
   externally-cheap channel LA actually has) carries zero value information. Confirms G3's hard rule
   "a shape match alone can never be SEED_A."
2. **Correct seeds DO carry information — but the minimal count is nearly the whole class.** secure_shared
   lift is real, yet you need **k≈4 of 5** correct vowel identifications before recovery is even
   marginally separable from random seeding, and only with the substitution channel. At that point
   propagation is recovering essentially one held-out vowel (recall ~0.11) — the D3 leak observation
   restated: the "recovery" is a rank stat on ~1 positive, not genuine class induction.
3. **Anchor-quality seeds top out at k=2 and never separate.** The toponym-anchor pool contributes only
   two true vowels {A, I}; the channel is *exhausted* at k=2 (AUC 0.723, still inside the null band) and
   cannot reach k=3. Even those two collapse to one under the cited frozen LOTO gate.
4. **Wrong seeds are worse than none.** `incorrect` drives held-out AUC monotonically to 0.21 and recall
   to 0 — trusting a disputed anchor is actively harmful, not merely uninformative.

**Net frontier:** on a *readable* analogue with a gradable partition, the seed-propagation lever needs
**≈4 secure, correctly-valued seeds (of a 5-member class), plus the substitution channel, to clear the
matched null — and even then marginally, with trivial recall.** It is not a low-external-information lever.

---

## 4. Where Linear A sits

**LA has 0 secure value seeds (`SEED_A = 0`, WP-G).** Mapping availability by type:

| type | LA availability | frontier consequence |
|---|---|---|
| random | unlimited, value-blind | null floor — no recovery |
| shape_selected | available (SigLA) but shape ⊥ value | null floor — no recovery |
| secure_shared | **0** (no bilingual; values relabeling-invariant) | cannot enter the only curve that ever separates |
| anchor_derived | ≤2 on paper (toponym vowels), **0** after LOTO (survivor {I}, 1-deep) | short of even the k=2 anchor cap, which itself never separates |
| incorrect | the outcome if disputed anchors are trusted | actively harmful |

**Linear A is at the pre-frontier origin (k=0 secure).** The only seed channels LA actually possesses
(random, shape) are the two the LB control measures at the null floor; its anchor channel caps below
where the LB control first shows *any* marginal separation (k=4) and collapses to 1 under held-out
testing. The frontier confirms the WAVE-2 conclusion from the seed side: **the missing ingredient is not
more corpus or a better propagator — it is ≈4 independent, secure, correctly-valued seeds (a bilingual or
≥3–4 genuinely held-out-survivable anchors), of which LA currently has zero.**

**Verdict: `SEED_FRONTIER_MAPPED — LA_BELOW_MINIMAL_SEED_THRESHOLD`.** Highest layer L2/L3; no licence earned.

*Generated by `scripts/d4_minimal_seed_frontier.py`; all counts echoed from `data/D4_frontier.json` (invariant 12).*
