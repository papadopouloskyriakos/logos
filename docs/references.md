# references — the prior-art map for logos

Before claiming any novelty, logos anchors on this map. Grouped by how close each gets to
"agentic + data-science + open + unknown-script decipherment." The honest headline:
**no mature open-source *agentic* decipherment platform exists — the cell is empty — but a
strong methodological foundation (Luo 2019) and engineering references (Ithaca/Pythia) do.**

## 1. Foundational decipherment *methods* (build on, don't reinvent)

- **Luo, Cao & Barzilay (2019), "Neural Decipherment via Minimum-Cost Flow: From Ugaritic
  to Linear B"** — [ACL P19-1303](https://aclanthology.org/P19-1303.pdf) ·
  [arXiv 1906.06718](https://arxiv.org/abs/1906.06718). *The* seminal automatic-decipherment
  result. Auto-deciphered **Ugaritic→Hebrew** (Semitic cousins), **partially Linear B→Greek**,
  and **explicitly did NOT crack Linear A** (unknown language). This is logos's **baseline
  method** — see [luo-2019-neural-decipherment.md](luo-2019-neural-decipherment.md). Code not
  openly released → reimplement from the paper.
- **Luo et al., "Deciphering Undersegmented Ancient Scripts Using Phonetic Prior"** —
  [PDF](https://people.csail.mit.edu/j_luo/assets/publications/DecipherUnsegmented.pdf).
  Follow-up; relevant to scripts without clear word boundaries.
- **Ravi & Knight (2011), "Deciphering Foreign Language"** — the Bayesian/MT-decipherment
  lineage (IBM-model style) that Luo neuralizes. The statistical-decipherment root.
- **Snyder, Barzilay & Knight (2010), "A Statistical Model for Lost Language Decipherment"**
  — Ugaritic via Bayesian cognate matching. Another root.

## 2. Restoration of *known*-language text (engineering references, open code)

These do NOT decipher unknown scripts — they restore damaged text in known languages. Use
them as engineering references for sparse-text transformer pipelines and data discipline.

- **DeepMind Ithaca** — [github](https://github.com/google-deepmind/ithaca). DNN for
  restoration + geographical/chronological attribution of ancient Greek inscriptions
  (Nature). ~62% restoration, 71% attribution.
- **Pythia** (Ithaca's predecessor) — [github](https://github.com/sommerschield/ancient-text-restoration).
- **Aeneas / "Predicting the Past"** — [github](https://github.com/google-deepmind/predictingthepast).
  Generative NN for contextualizing ancient texts.

## 3. Surveys / the literature map (our reading baseline)

- **"Machine Learning for Ancient Languages: A Survey"** (Sommerschield et al., Comp.
  Linguistics 2023) — [github](https://github.com/ancientml/ml-for-ancient-languages) ·
  [ACL](https://aclanthology.org/2023.cl-3.5/). **240+ papers.** Start here; it is the map.
- **"A Systematic Review of Computational Approaches to Bronze Age Aegean and Cypriot
  Scripts"** — [ResearchGate](https://www.researchgate.net/publication/378833808). The
  Aegean-specific slice.

## 4. Open decipherment *attempts* (peers, varying maturity)

- **JamesPiggott/Ancient-Language-Decipherer** — [repo](https://github.com/JamesPiggott/Ancient-Language-Decipherer).
  CV+NLP for detect/recognize/translate ancient scripts. Closest open *attempt*; read as a
  fellow traveller, not a platform.
- **L-Colin/Linear-A-decipherment-programme** — [repo](https://github.com/L-Colin/Linear-A-decipherment-programme).
  Python programme under NTU supervision (Perono Cacciafoco / Duoduo).
- **Frontiers in AI (2025), "On automatic decipherment of lost ancient scripts"** —
  [paper](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1581129/full).
  DL image→string pipeline for the **Indus script**.
- **MDPI "Minoan Cryptanalysis"** — [Information 15(2):73](https://www.mdpi.com/2078-2489/15/2/73).

## 5. Agentic + corpus patterns (architectural cousins)

- **"Agent-Driven Corpus Linguistics" (arXiv 2026)** — [html](https://arxiv.org/html/2604.07189v1).
  LLM agents over a corpus query engine via **MCP**. Not decipherment, but the agentic
  tool-use shape logos's hypothesis layer wants.

## 6. Corpus infrastructure (data foundations)

- **lineara.xyz** — [repo](https://github.com/mwenge/lineara.xyz). Linear A corpus explorer
  (the explorer site Blahah recommended on HN).
- **GORILA** (Godart & Olivier, *Recueil des inscriptions en Linéaire A*) — the canonical
  print/academic corpus; digitized forms circulate.
- **SigLA** (Signs of Linear A) — the sign-level database; the palaeographic inventory.

## Update 2026-06-30 — audit findings (prior art, from the survey §8.1)

Mined from Sommerschield et al. 2023 ("Machine Learning for Ancient Languages: A Survey,"
*Computational Linguistics* 49(3), [DOI 10.1162/coli_a_00481](https://doi.org/10.1162/coli_a_00481)).
The decipherment method lineage — logos implements the combinatorial core (Berg-Kirkpatrick &
Klein 2011), neural variant (Luo 2019) is the upgrade:

- **Rao et al. 2009/2010** — Indus script conditional entropy / Markov; "is it language?"
  Contested by **Sproat 2010/2014** (repetition turn-out → non-linguistic). *Entropy shows
  structure, not languagehood — the caution behind `corpus_info.py`.*
- **Snyder, Barzilay & Knight 2010** — non-parametric Bayesian cognate decipherment
  (Ugaritic→Hebrew). [paper]
- **Berg-Kirkpatrick & Klein 2011** — cognate decipherment as **combinatorial optimization**
  (min edit-distance under char mapping). *logos's numpy/scipy core.*
- **Bouchard-Côté et al. 2013** — probabilistic sound-change / proto-language reconstruction.
- **Luo, Cao & Barzilay 2019 ("NeuroCipher")** — seq2seq + min-cost flow; Ugaritic→Hebrew,
  Linear B→Greek. *the torch upgrade.*
- **Luo et al. 2021** — undersegmented scripts via phonetic conversion; Gothic/Ugaritic/Iberian.

**Cross-script & embedding prior art — MUST cite (NOT our novelty):**
- **Papavassiliou, Owens & Kosmopoulos 2020** — "include related writing systems (Linear B) as
  the key to decipherment." *(the cross-script idea predates us)*
- **Karajgikar, Al-Khulaidy & Berea 2021** — word2vec embeddings for Linear A glyphs + symbol grouping.
- **Corazza et al. 2022 ("Sign2Vec")** — unsupervised sign clustering (ResNet50+k-means) for
  Cypro-Minoan, 2/3 signs correct. *direct prior art for the representation layer.*
- **Daggumati & Revesz 2018** — CNN+SVM script-family trees ("Linear B close to Cretan Hieroglyphic").
- **Papavassileiou, Kosmopoulos & Owens 2023** — Linear B generative LM (BiRNN) for tablet
  infilling, [DOI 10.1145/3593431](https://doi.org/10.1145/3593431). *the known-side asset for
  cross-script transfer.*

**logos's actual novelty:** the agora discipline layer (deflation + held-out verdicts + open
platform) + the cross-script A↔B JEPA joint-embedding formulation. Not "Linear B as key" or
"Linear A embeddings," which exist.

## Philological & statistical prior art (added 2026-06-30 expert audit — LOAD-BEARING)

Missing from the first pass; two external red-teams flagged these as non-optional (the Libation
Formula is our held-out set):

- **Duhoux** — standard analyses of the Linear A **Libation Formula**.
- **Brent Davis** — *Minoan Stone Vessels with Linear A Inscriptions* (2014) + structural /
  word-order analysis of Linear A (the most serious modern structural analyst).
- **Packard (1974)**, *Minoan Linear A* — constructed 9 **fictitious decipherments** as a null
  (Ventris-value transfer beat them only ~2:1). The ancestor of our permutation-null discipline.
- **Barber (1974)**, *Archaeological Decipherment* — the identifiability-without-a-known-target
  threshold our unicity argument must (and currently fails to) engage.
- **Godart & Olivier, GORILA** (1976–85) — the corpus + sign-inventory authority.
- **John G. Younger**, *Linear A Texts* (online) — formula segmentation.
- **CREWS project (P. Steele, Cambridge)** — Aegean writing systems.
- **Robinson**, *Lost Languages* — cautionary framing.
- A **systematic review of computational Aegean & Cypriot scripts** (more targeted than the broad
  ML survey); **Luo et al. 2021** (central — undersegmented scripts, phonetic conversion,
  related-language comparison).
- Cross-lingual embedding alignment (for the §5 reframing): **Mikolov et al. 2013**, **Conneau
  et al. MUSE 2017**, orthogonal Procrustes; **Bouchard-Côté et al. 2013** sound-drift (needs
  candidate cognates first — cannot create them from unlabelled signs).

## Where logos sits

Empty cell = opportunity *and* warning. Opportunity: no one has wrapped a decipherment
method in the agora discipline/deflation + agentic-LLM + held-out-verdict + JEPA-transfer
frame, openly. Warning: the cell is empty partly because Luo's result shows
unknown-language decipherment is near-intractable without a cognate — logos's realistic
deliverable is the **honest discipline platform** (and a defensible extension of Luo),
not a likely Linear A "crack." State that plainly in every outward-facing doc.
