# Information Gain and Bottleneck Analysis (§8.2 / §8.3 / §12.7)

## What the 105 epochs collectively learned

### Durable uncertainty reductions (survive dependency collapse)
1. **A- is a real positional prefix slot** (E103) — reduces the space of admissible LA morphological structures:
   any correct account of LA administrative words must place a productive, cross-site, cross-period initial A- slot.
   *Absolute reduction* (held-out, segmentation-robust). Constrains ~155 word-initial-A word types.
2. **The LA vowel signal is frequency-invariant** (E099) — reduces uncertainty about the *nature* of the weak signal
   (structural, not a frequency artifact). *Conditional* reduction: established on LB, LA-untestable.
3. **LA is data-sufficient for the weak signal** (E093) — reduces the hypothesis "more corpus will crack it": at
   ~4245 tokens the binding constraint is signal-weakness + no-transfer, not corpus size. *Absolute.*
4. **The value-assignment space is a single independent channel** (E102) — the sharpest reduction: rules out the
   entire class of "multi-method corroboration" arguments for any absolute value. *Absolute, dependency-adjusted.*
5. **The discipline machinery is load-bearing** (E104) — quantifies that the graduation gate suppresses false
   positives 60× (30.5%→0.5%) while retaining power. *Methodological certainty.*

### False routes eliminated (the insurance value)
Position→C/V and reduced-seed (frequency artifacts, refuted); cross-script substitution bridge at LA scale;
morphogenesis as a mechanism; BP/Potts/TDA/network-flow transfer; SBI as an architecture upgrade; register-strata
phonotactics; word-context→administrative-channel. ~a hundred pre-registered opportunities to publish a fitted
reading, all refused.

## The bottleneck (§8.3) — measured, not asserted

**Dominant limitation = ANCHOR INDEPENDENCE.** The accessible LA data supports exactly **one** independent
linguistic channel (context co-occurrence). A decipherment needs a second independent channel *and/or* an external
multi-slot anchor lattice; neither exists in the accessible corpus.

Ruled OUT as the dominant limitation, each with evidence:
- **Corpus size** — E093: LA is data-sufficient for the signal it has.
- **Algorithmic power** — E016/E092/E101: new architectures match but never beat simple baselines; the ceiling is
  informational, not computational.
- **Detector power** — E104 + every epoch's positive control: gates fire, planted signals recover.
- **Segmentation uncertainty** — E103: the graduated finding is segmentation-robust (3/3 schemes).

Ruled IN as *contributing* (but downstream of anchor independence):
- **Source access / palaeographic resolution** — the one candidate 2nd channel (stroke contours) and the external
  anchor source (Ariadne-2025 Anetaki full edition) are `SOURCE_BLOCKED`.

## Implication
Intensive computation has reached its information ceiling. The next bit of information must come from **new
evidence** (a second independent channel or an external anchor), not from a new model on the same corpus.
