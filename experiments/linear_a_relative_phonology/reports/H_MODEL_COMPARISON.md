# H_MODEL_COMPARISON — the three candidate rounds compared

**Task H (rounds 1–3) synthesis** · Constitution v2.2 · seed `20260708` · as_of `2026-07-07`.
Sources: `data/H1_round1.json`, `data/H2_round2.json`, `data/H3_round3.json`;
reports `H_ROUND_1.md`, `H_ROUND_2.md`, `H_ROUND_3.md`.

## Bottom line

Three orthogonal ways of constraining a value-bearing decipherment were each preregistered, run
against the **same** held-out Linear A word target and the **same** multi-family end-to-end null
battery (S order-shuffle, W wrong-language opaque LB, R random-prior + Holm + leave-one-lexeme-out +
random-lexicon calibration + agnostic control). **All three land at the null.** The design space is
exhausted along its three natural axes — *candidate language* (R1), *external anchors* (R2), and
*inference paradigm over internal morphology* (R3) — and H3 supplies the mechanical reason the other
two could not have succeeded: the internal structure is **value-blind (relabeling-invariant)**.

| round | what varies (the "families") | constraint added | verdict |
|---|---|---|---|
| **R1** `H1` | candidate **languages** (SEM/ANA/TYR + FIN neg-ctrl + CTRL) | relative-class (D5) admission | `AT_END_TO_END_NULL` |
| **R2** `H2` | same 5 languages | + 6 WP-G SEED_B toponym **anchors** | `AT_ANCHOR_CONSTRAINED_NULL` |
| **R3** `H3` | **inference paradigms** (Bayes-joint / MDL / CSP-IP) | morphology-first joint (A-prefix + formula) | `AT_JOINT_INFERENCE_NULL` |

## Head-to-head (verdict-relevant numbers)

Best serious model per round on the identical decisive bar (`max(p_W,p_R)`, Holm across that round's
families) + the random-lexicon calibration percentile:

| round | serious model | real match | decisive | **Holm** | **LOO worst** | cal percentile p | GENUINE? |
|---|---|---|---|---|---|---|---|
| R1 | SEM (KU-RO lexeme) | 0.0382 | **0.0149** | 0.0745 | **1.000** | 0.0066 | no (single-lexeme) |
| R1 | TYR (highest raw) | **0.0726** | 0.1592 | 0.478 | 0.443 | **0.213** | no (shape band) |
| R2 | SEM (anchored) | 0.0384 | **0.0149** | 0.0745 | **1.000** | 0.0066 | no (Δanchor = 0) |
| R2 | TYR (anchored) | 0.0731 | 0.1542 | 0.617 | 0.443 | **0.219** | no (shape band) |
| R3 | CSP-IP / BAYES | **0.0822** | 0.0597–0.070 | 0.179 | 0.199–0.229 | **0.076 / 0.093** | no (shape band) |
| R3 | MDL | 0.0000 | 1.000 | 1.000 | 1.000 | 1.000 | no (reads 0 held-out) |

Controls, all three rounds: agnostic CTRL never clears (decisive 0.53 / 0.53 / 1.0); the
chronogeographically-impossible negative control FIN sits at the null (decisive 0.915, LOO 1.0).

## The three recurring failure modes (each round hits at least one)

1. **The single famous lexeme (`KU-RO` "total").** The one thing that raw-clears the decisive nulls in
   every round is the administrative equation `kull`→`KU-RO`. It dies at Holm (0.0745) and LOO (1.000)
   in R1/R2, and in R3 it is the MDL optimum whose 40-bit gain is *entirely on the excluded derivation
   words* (0 held-out reads). A total-term shortcut shared by any accounting tradition — never
   language-specific evidence.
2. **Word-shape typicality (`A-`initial + `-na`/`-si`).** The highest raw match in every round (TYR
   0.073 in R1/R2; CSP/BAYES 0.082 in R3) is reproduced by same-structure random lexicons
   (percentile p 0.21 / 0.22 / 0.076–0.093, all inside the band). Short open-CV words with a frequent
   `A-` onset match Linear A regardless of the specific lexemes.
3. **One-deep anchors / value-blind structure.** External toponym anchors add **Δ = 0** held-out reads
   (R2, `SEED_A = 0`), and the internal morphology is **relabeling-invariant** (R3: read-count std 0
   over 200 relabelings; Bayesian posterior flat at 3.585 bits / 12 assignments). Neither external
   pins nor internal structure carry recoverable phonetic value.

## Why R3 is the decisive round, not just a third null

R1 and R2 could in principle have failed for *contingent* reasons (wrong candidate languages; wrong
anchors). R3 removes that escape: it does **not** bet on a language — it lets three standard inference
paradigms extract whatever a value assignment the internal morphology/formula backbone can support,
and measures the identifiability directly. The answer is mechanical and language-independent:

- **relabeling-invariance** — consistent relabeling of the value map leaves the entire reading
  unchanged (read-count std 0), so any objective computed on internal structure is invariant to the
  values; **0 bits** of value information exist to be inferred;
- **flat Bayesian posterior** — 3.585 bits / 12 equally-probable assignments; the only concentration
  (`kull`) is dictionary feasibility of an *external* spelling, not LA evidence;
- **CSP feasible set of 1 pinning 2 signs by external-lexeme choice**, covering 0 held-out words.

So the R1/R2 nulls are not bad luck: **no inference paradigm operating on the internal structure can
recover a value**, because the structure is value-blind. This is the campaign's relabeling-invariance
result (internal evidence is value-blind) promoted from a diagnostic to the governing constraint on
the whole candidate-model programme.

## Paradigm comparison within R3 (methodological, for the record)

| paradigm | committed size | held-out reach | characteristic failure |
|---|---|---|---|
| **MDL** | minimal (1 lexeme) | 0.000 | parsimony collapses to the single excluded `KU-RO`; DL gain is all on fitted data |
| **Bayesian-joint** | posterior>0.5 (19) | 0.082 | flat value-posterior; raw match is shape typicality inside the band |
| **CSP / IP** | max-coverage (19) | 0.082 | feasible set of 1 pins 2 signs by lexeme choice; raw match is shape typicality |

MDL under-commits (into the single-lexeme trap), CSP/Bayes over-commit (into the shape-typicality
band); there is **no middle setting** that clears the bar, because the identifiability ceiling is 0
bits of value regardless of committed size — the two errors are the two sides of a null.

## Consequence for the campaign

The value layer is closed from three independent directions. Consistent with the durable positives —
anonymous L2/L3 structure (A- prefixation control-validated cross-site; ledger KU-RO/KI-RO
arithmetic; libation rigid order) is **real but value-blind**. No transfer licence is earned; SEMANTIC+
remains `NOT_AUTHORIZED` (Art. XV). Cracking the value layer requires evidence the corpus does not
contain — a bilingual or ≥3 independent held-out value anchors — not another internal model.
**Next: I1 (constraint-reduced agnostic value search)**, which the R3 relabeling-invariance predicts
will collapse into relabeling/permutation/synonym equivalence classes.
