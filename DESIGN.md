# DESIGN.md — logos architecture & rationale

logos is [finops-agora](../finops-agora)'s epistemic-discipline core, retargeted from
*financial edge* to *linguistic decipherment*. The problem shapes are isomorphic: **rare
signal, sparse data, an adversarial null, and a field drowning in self-deceiving
"positives."** This doc is the architecture; the operating rules are in
[CLAUDE.md](CLAUDE.md); the mission framing is in [README.md](README.md).

## ⚠ Expert-audit corrections (2026-06-30) — supersedes overclaims below

Two independent external red-teams found that several claims in this doc (and in the
information-floor finding) were **overclaimed** — a quieter version of the self-deception
logos exists to prevent. The authoritative correction record is
[docs/findings/2026-06-30-expert-redteam-synthesis.md](docs/findings/2026-06-30-expert-redteam-synthesis.md).
Until revised inline, treat these as **withdrawn/corrected**:

- The unicity-distance result is a **toy-model precondition diagnostic**, NOT proof the corpus
  can pin a decipherment (it assumes a known plaintext-language oracle; lossy underspelling may
  mean no unicity distance at all).
- The decipher engine is a **simplified heuristic baseline**, NOT a faithful Berg-Kirkpatrick &
  Klein 2011 reproduction (B-K&K uses word-level bipartite matching + many-to-many alphabet +
  restarts). The credibility milestone is **Linear B → Greek known-answer recovery**.
- The cross-script A↔B idea yields **phonetic values (a readout)**, not a cognate language; the
  honest ceiling is **Etruscan-grade**. Run simpler alignment baselines (Procrustes/MUSE/OT/graph)
  before JEPA.
- The multiple-testing engine is **pre-registration + held-out + pipeline-level permutation null
  (Packard 1974) + MDL** — DSR is demoted to one weak instance.
- The sign inventory must be **inherited from GORILA/SigLA** (layered ontology), not learned;
  clean to ~90 syllabograms BEFORE computing the floor; logograms/numerals are separate channels.
- Realistic ceiling: **<1–3% full decipherment**; the durable product is the open, null-calibrated
  benchmark/framework.

**Reframed mission:** *"a falsifiable, statistically-calibrated inference framework for
determining which structural/phonetic/linguistic claims Linear A can support."*

## The isomorphism (why agora's patterns transfer)

| agora (trading) | logos (decipherment) |
|---|---|
| a price series | a sign sequence / inscription |
| a strategy family (momentum, value…) | a language-family hypothesis (Semitic, Anatolian, Tyrrenian, IE, isolate) |
| a prediction (direction, horizon, catalyst) | a hypothesis (sign→phone map, lexeme, grammar rule, falsifiable held-out implication) |
| the index benchmark (VWRD) | the **information floor** (unicity-distance / entropy budget) |
| the mechanical `verdict` (match/partial/deviation vs prices) | the mechanical `verdict` (held-out-site / held-out-inscription accuracy) |
| multiple-testing across strategies tried | multiple-testing across signs × roots × families tried |
| a fake edge that costs capital | a fake decipherment that misleads the field |
| G3 = real-money deploy | acceptance = reads held-out text + survives peer review |

The single biggest transfer: **agora's "Deflated-Sharpe over effective-n" is exactly the
cure for the decipherment field's "I matched 408 words" disease.** Matching words across a
thesaurus of Proto-Semitic roots on a 7,500-character corpus is a multiple-testing problem;
without deflation it proves nothing (cf. the "English is a Semitic language" demo). logos
turns that intuition into a number.

## Methodological foundation — the decipherment lineage (don't reinvent)

The decipherment *method* is not invented here; it sits in a well-mapped lineage (per the
Sommerschield et al. 2023 survey §8.1 — `coli_a_00481.pdf`). logos implements the
**combinatorial core** and treats the neural variant as a documented upgrade:

- **Rao et al. 2009/2010** — sign-sequence conditional entropy / Markov ("is it language?") —
  the same statistic `corpus_info.py` computes. **Contested by Sproat 2010/2014** (see §4 caveat).
- **Snyder, Barzilay & Knight 2010** — non-parametric Bayesian cognate decipherment
  (Ugaritic→Hebrew). The cognate-decipherment root.
- **Berg-Kirkpatrick & Klein 2011** — cognate decipherment as **combinatorial optimization**
  (minimize edit-distance between cognate word pairs under a character mapping). **This is
  logos's numpy/scipy core**: the character mapping is a min-cost bipartite assignment
  (`scipy.optimize.linear_sum_assignment` = the bipartite min-cost flow), iterated EM-style
  with weighted edit-distance alignment. Runs on the runner — no torch.
- **Luo, Cao & Barzilay 2019 ("NeuroCipher")** — neuralized the alignment scorer with a
  seq2seq + min-cost-flow objective (Ugaritic→Hebrew, Linear B→Greek 67.3% cognates). **The
  documented torch upgrade path** once GPU training is wired (phase 5).

**Why this fails on Linear A (the null):** every method above needs a *known cognate
language* to map onto. Linear A's language is unknown → the optimization has no target → the
map can't be pinned. That null confirms §4's information floor empirically. The cross-script
A↔B JEPA is the one bet that tries to *manufacture* a cognate-like target.

**Sharpened novelty (post-audit):** "use Linear B as a key" (Papavassiliou, Owens &
Kosmopoulos 2020) and "embeddings for Linear A glyphs" (Karajgikar et al. 2021; Sign2Vec /
Corazza et al. 2022 for Cypro-Minoan) are **prior art, not ours**. logos's defensible
contributions: (a) the **agora discipline layer** (Deflated-Sharpe over signs×roots×families +
mechanical held-out verdicts + open platform) — absent from all prior work; (b) the specific
**cross-script A↔B joint-embedding (JEPA)** formulation of the transfer; (c) using the
Papavassileiou et al. 2023 Linear B generative LM as the known-side representation.

**Scope (operator-approved 2026-06-30):** Linear A is the **primary target** (the only Aegean
script whose corpus meets unicity, §4). The rest of the Aegean undeciphered family — Cretan
Hieroglyphic, Cypro-Minoan, the Phaistos Disc — enter **only as cross-script probes / extra
embedding context** for the A↔B transfer, never as decipherment targets (the Phaistos Disc is
a single ~241-token document; unicity is hopeless there).

## The layers

```
   CORPUS / INGESTION          REPRESENTATION (≤0.75)        HYPOTHESIS + RIGOR
 ┌──────────────────┐        ┌──────────────────────┐     ┌──────────────────────┐
 │ GORILA + SigLA + │        │ JEPA (LeCun):        │     │ predict (hash-keyed  │
 │ lineara.xyz →    │───────▶│  • sign-image I-JEPA │────▶│  hypothesis, falsifi- │
 │ bronze (raw) →   │        │  • sequence TS-JEPA  │     │  able, confidence)    │
 │ silver (norm) →  │        │  • cross-script A↔B  │     │   ↓                   │
 │ gold (DuckDB)    │        │   joint embedding    │     │ verdict (held-out,    │
 └──────────────────┘        └──────────────────────┘     │  MECHANICAL)          │
        │                              │                   │   ↓                   │
        └──────────────────────────────┴──────────────────▶│ score (win-rate vs    │
                                                           │  held-out, Brier,     │
                                                           │  calibration)         │
                                                           │   ↓                   │
                                                           │ graduate (win-rate +  │
                                                           │  order-stat E[max])   │
                                                           └──────────────────────┘
```

### 1. Corpus / ingestion (bronze → silver → gold)

- **Bronze:** raw sign drawings/photos + raw GORILA/SigLA exports, gitignored where
  licensed. Public foundations: [lineara.xyz](https://github.com/mwenge/lineara.xyz)
  (explorer), GORILA, SigLA, the [NTU programme](https://github.com/L-Colin/Linear-A-decipherment-programme).
- **Silver:** normalized `corpus/silver/*.json` — one record per inscription:
  `{id, site, object_type, dating, signs:[...], logograms:[...], numerals, provenance, as_of}`.
  The schema is defined in `scripts/corpus_io.py` (TODO).
- **Gold:** a DuckDB/Parquet lake over silver for fast statistical scans (the agora
  `lake_build.py` pattern, single-writer, capped). Read-only analytical queries only.

### 2. Representation — JEPA (truth ≤ 0.75, never the decipherer)

JEPA's value is *representation learning without labels, in latent space* — it captures
predictive structure without reconstructing observations and without knowing the language.
It slots into the exact role `agora-jepa` already fills (produce a latent, emit a capped
feature). Three applications, in order of novelty:

1. **Sign-image I-JEPA** — palaeographic representations; clusters same-sign / variant /
   damaged-form with no labels. Closes the portfolio's CV gap.
2. **Sequence TS-JEPA** (direct repurpose of agora's market encoder) — predict the latent of
   the next sign-cluster from context → learns word boundaries and distributional grammar
   with **zero phonetic knowledge** (the Kober/Ventris positional signal, latent & unsupervised).
3. **Cross-script joint embedding (Linear A ↔ Linear B)** — the novel bet. Two related
   scripts sharing ~60 signs are JEPA's "two views into one latent space"; the 60 known
   Linear-B phonetic anchors transfer structure to Linear-A-only signs (`*301` etc.).

**Honest headwind:** Linear A (~7,500 chars) is too small to pretrain a good latent on A
alone. JEPA likely underperforms plain n-gram/entropy stats on A's text and shines instead on
the larger Linear B corpus (for transfer) and on sign-image augmentation. Whether JEPA beats
simpler stats here is itself a publishable research question — we answer it empirically, and a
null is fine. **Decision: v0 ships JEPA as scaffold-only; light it up after the corpus + the
symbolic verdict layer + the unicity number exist.** Reuse agora's harness
(`services/agora-jepa`, `scripts/jepa_*.py`, `docs/jepa-market-encoder.md`).

### 3. Hypothesis → verdict → score → graduate (the agora pipeline, retargeted)

- **predict** (`predict.py`, TODO): canonical JSON body → `plan_hash = sha256(body)`; idempotent.
  A hypothesis carries the sign(s), the proposed reading, the family, a falsifiable held-out
  implication, and confidence ≤ 0.75 if model-assisted.
- **verdict** (`verdict.py`, TODO — the *sole* writer of `verdicts`): mechanical held-out-site
  / held-out-inscription accuracy; cross-corpus consistency; Brier vs the predicted
  implication. The proposer never grades itself.
- **score** (`family_scores.py`): per-family held-out **GRADUATE win-rate** (a win is a §E-gate
  `GRADUATE`, never the intermediate `result=='match'`), calibration gap, and the reported DSR
  diagnostic (effective-n, n_trials) — DSR is computed but is **not** a gate input.
- **graduate** (`family_scores.py` graduation gate): a family graduates only if it has a real
  held-out **GRADUATE win-rate AND enough verdicts** (`MIN_VERDICTS`), with the per-hypothesis §E
  gate requiring the held-out statistic to clear the **order-statistic E[max] bar** over the counted
  multiplicity and to fail closed on un-instrumented search. **DSR and the MDL / information-floor
  check are REPORTED diagnostics, removed from the operative gate after review** (§B.3); a family
  whose readings are underdetermined does not graduate, but that is enforced by the order-statistic
  bar, not by an MDL hard clause.

### 4. The information floor (the benchmark)

`scripts/corpus_info.py` computes the corpus's entropy budget and a unicity-distance
estimate: **bits the corpus constrains vs free parameters of a hypothesized phonetic map.**
If parameters ≫ information, no amount of cleverness can confirm a decipherment — the
honest, decisive number for any Linear A claim. Every graded hypothesis is shown next to it.

**Caveat (the Rao↔Sproat debate):** entropy / conditional-entropy statistics show the sign
sequences carry structure — they do **not** prove the script encodes language. Sproat
(2010, 2014) used exactly this gap to argue the Indus symbols are non-linguistic.
`corpus_info.py` reports structure and an information budget; it renders no verdict on
languagehood.

## Roadmap (honest — built on Luo 2019, not next to it)

0. **Corpus ingest + information floor** — GORILA/SigLA → silver schema → DuckDB gold;
   compute the real unicity-distance number (`scripts/corpus_info.py`) on the true Linear A
   corpus. *(the decisive first number; reproduces the floor argument)* — `corpus_info.py`
   is runnable today on `--demo`.
1. **Reproduce the Luo baseline** ([docs/methods/luo-2019.md](docs/methods/luo-2019.md)) —
   reimplement seq2seq + min-cost flow; reproduce the **Ugaritic→Hebrew success** (proves the
   pipeline) and the **Linear-A null** (proves the floor: no cognate ⇒ the method cannot pin
   a map). *Both publishable; the null is the honest milestone.* This is the non-NIH foundation.
2. **predict → verdict scaffold (the agora layer)** — hash-keyed hypotheses; the LLM never
   grades itself; mechanical held-out-site / held-out-inscription verdicts (`verdict.py`,
   sole writer). Libation Formula × 5 sites = a natural 5-fold CV. Reuse `agora_stats`
   deflation (DSR / effective-n over signs × roots × families).
3. **Multi-family head-to-head** — Semitic (Gordon/Di Mino, one capped prior ≤0.75) vs
   Anatolian vs Tyrrenian vs IE vs isolate, each graded, DSR-deflated for n_families.
   *(the experiment nobody has run)*
4. **Agentic generation** — Claude-in-the-loop cognate/sound-law hypothesis generation as
   ≤0.75 signals (the layer Luo lacks entirely; Luo is pure optimization). `claude -p`, no
   API key; evidence-audit clamps unevidenced confidence.
5. **JEPA layer** — sign-image I-JEPA + sequence TS-JEPA + cross-script A↔B joint embedding;
   test vs n-gram baseline. Gated behind phases 0–1 (too little data to pretrain on A alone).
6. **Rosetta desk (cockpit)** — later; the agora-ui pattern.

## Resolved decisions — FULL SCALE (operator, 2026-06-30)

The operator authorized full-scale resource use. Resolved:

- **Gold store: BOTH.** A `logos` MariaDB database on the Galera cluster via ProxySQL :6033
  (concurrent reads, the cockpit, portfolio conventions — every table has a PK) AND a
  DuckDB/Parquet analytical lake over silver for fast scans. Mirror agora's 3-tier.
- **GPU/host: full.** A `logos-jepa` service on nllei01gpu01 (docker, reusing the agora-jepa
  harness + Ollama) for the representation layer; the runner hosts cron + the predict/verdict
  pipeline. (The GPU also hosts Kronos/Chronos-style forecasters if a sequence model is wanted.)
- **Corpus: open-data ingest + licensed-fetcher.** Open corpus data (lineara.xyz) is ingested
  into silver and committed where its license permits; GORILA/SigLA raw academic exports are
  bronze-only + a `scripts/fetch-*.sh` (invariants 10/12 — bulk licensed data never enters
  git). Each source's license is verified before any commit.
