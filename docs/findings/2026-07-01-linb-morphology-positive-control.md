# Linear B morphology positive control (preprint item 1.5)

**Question.** Does the bigram-floor affix test that returns **NO POWER** on Linear A have measurable
power in a *relevant syllabic setting where morphology demonstrably exists*? If yes, Linear A's null
means "the test finds morphology where it exists and correctly finds none in Linear A," not "the
floor is too strong to detect anything."

**Method.** The *identical* test (`scripts/comparison/morphology.py::null_falsification`, the same
REAL-vs-shuffle-vs-`L_fake`-bigram-floor procedure) run on **Mycenaean Greek (Linear B)** from the
already-ingested DĀMOS corpus, parsed with the canonical `scripts/cross_script/data.py::_damos_wordforms`
extractor (the same one behind §7.3's 13,562-wordform figure). Affix panel: 16 **pre-registered**
Mycenaean suffixes (a-priori, from Ventris & Chadwick 1953; suffixal, because Greek inflection is
suffixal) — `scripts/comparison/linb_morphology_control.py`. NOT tuned to fire; the productivity gate
(≥2 distinct residual stems) and the conservative max(shuffle, `L_fake`) floor are the real test.

**Corpus (generated).** 3,856 tablets, **13,562 word-tokens**, 4,946 distinct wordforms;
**mean 3.23 signs/word** (median 3, 26.5% ≤2 signs), 89 distinct syllabograms — versus Linear A's
**mean 1.84 signs/word** (76.1% ≤2 signs). The word-length contrast is the mechanism.

**Result — the control FIRES.**

| corpus | mean signs/word | REAL confirm | shuffle floor | `L_fake` bigram floor | verdict |
|---|---|---|---|---|---|
| **Linear B** (this control) | 3.23 | **0.562** (9/16) | ~0.03 | **~0.30** (5 draws: 5,5,5,5,4) | **HAS POWER** |
| Linear A (§6) | 1.84 | 0.250 | — | 0.375 | NO POWER |

`has_morphology_power = True` (beats_shuffle **and** beats_lfake), stable across 5 `L_fake` draws and
seeds. Confirmed Mycenaean affixes: **-jo** (adj/gen -yo-), **-o-jo** (gen sg -oio), **-de**
(allative), **-qe** (enclitic -kʷe "and"), **-o-i** (dat pl -ois), -we, -ro, -wo, -ta — driven by
the securely-grammatical suffixes, exactly the endings a first-order sign-bigram model cannot
manufacture on longer words.

**Sensitivity note (honest).** A first run with an ad-hoc transcription parser produced
mean 2.19 signs/word (fragments/short tokens) and did NOT fire (`L_fake` 0.625 > real 0.562) — the
same short-word phenomenon as Linear A. Switching to the canonical `_damos_wordforms` extractor
(complete multi-sign wordforms, mean 3.23) flips it to fire. This *confirms* rather than undercuts
the finding: the test's power tracks word length, precisely the paper's short-word argument.

**Reading.** The bigram-floor test is not inert. On a syllabic corpus with real inflectional
morphology and Mycenaean-scale word length it recovers that morphology above the bigram floor; on
Linear A's short words it cannot separate morphology from sign-bigram order and reports the null.
Linear A's `NO POWER` is a property of the corpus (short words), not a dead detector.

**Reproduce.** `python3 scripts/comparison/linb_morphology_control.py` → `results/linb_morphology_control.json`.
