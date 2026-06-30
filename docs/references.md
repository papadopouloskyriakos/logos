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

## Where logos sits

Empty cell = opportunity *and* warning. Opportunity: no one has wrapped a decipherment
method in the agora discipline/deflation + agentic-LLM + held-out-verdict + JEPA-transfer
frame, openly. Warning: the cell is empty partly because Luo's result shows
unknown-language decipherment is near-intractable without a cognate — logos's realistic
deliverable is the **honest discipline platform** (and a defensible extension of Luo),
not a likely Linear A "crack." State that plainly in every outward-facing doc.
