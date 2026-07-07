# B — Root-Search Nulls & Search Receipt

**Prereg** DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c) · **Seed** 20260708.

## B2 — Exact search receipt (charge every axis the reading rides)

| axis | count |
|---|---|
| candidate_values | 65 |
| languages | 6 |
| consonant_collapses_incl_hollow | 5 |
| weak_root_transforms | ['y', 'h', "'", 'w', 'hollow'] |
| segmentations | 4 |
| mean_gloss_senses_per_root | 3.63 |
| triconsonantal_roots_searched_per_language_orderOfMag | 1500 |
| **logged root/gloss search cells** (values×collapses×languages×segmentations) | **7,800** |
| author's stated simulations | 100,000 |

logged cells = values x collapses x languages x segmentations (the reading's OWN degrees of freedom); the triconsonantal inventory per language (~1500) and gloss polysemy multiply the true root-search multiplicity far beyond this and beyond the author's stated ~1e5.

## B3 — Matched controls

### (a) L_fake canary + frequency/length-matched real roots + Packard permutation

- held-out probe form: `nwy`; Hebrew lexicon n=2767; NED-eps=0.34.
- s_lex(n-w-y, **real Hebrew**) = **0.000**
- s_lex(n-w-y, **L_fake** invented Semitic) mean = 1.000 (sd 0.000, n=48)
- s_lex(n-w-y, **freq/len-matched random real**) mean = 0.000
- s_lex(n-w-y, **Packard-permuted**) mean = 0.979

The edit-distance 'match exists' channel has NO POWER for this probe: the L_fake INVENTED lexicon already contains a near-match to n-w-y ~100% of the time (floor mean 1.0), i.e. a near-match is essentially guaranteed in any dense Semitic-shaped lexicon; the Packard-permuted (destroyed-correspondence) control also scores ~0.98. The gold cognate WORDLIST returns 0.0 because it is a 2215-entry Ugaritic<->Hebrew cognate list, NOT a root dictionary, so it under-covers bare roots. Because L_fake >= real, this S_lex channel reads search-attractiveness, not cognacy (cf. run_canary docstring; Task A likewise caps S_lex). Root EXISTENCE is therefore established authoritatively by the BDB-cited B1 table (nwh is real), NOT by this edit-distance statistic.

### (b) Random-*301-value null (best-of-value)

- of the 13 admissible C1 phonemes, 54% hit a real root and 8% hit a dwell-tier gloss (weak-collapse regime). /na/ is not distinguished from the field on 'a root exists'.

### (c) best-of-language & dwelling-field prior

- dwell-tier languages ['Hebrew', 'Aramaic', 'Akkadian']; unrelated ['Arabic']; literal-yod languages give {'Ugaritic': ['drive-away', 'expel', 'chase'], 'Arabic': ['intend', 'purpose', 'resolve', 'journey', 'depart', 'be-distant', 'date-stone']}.

### (d) wrong-gloss control

- Assigning the root Arabic's REAL gloss 'intend' scores 0.5/3 on formula features (vs dwell 0.0/3): the gloss is under-constrained by the data (see B_GLOSS_SPECIFICITY).

## B3 — Deflation (E[max] over the search multiplicity)

- per-trial dwell-hit prob (best-of-language) p_language = 0.750; (narrow LA-onset axis) p_onset = 0.077
- P(>=1 dwell hit | logged 7,800 cells) = 1.0000
- P(>=1 dwell hit | author's 100,000 sims) = 1.0000

under weak collapse 3/4 admitted languages gloss the target skeleton habitation-tier (p_language=0.75); across the logged search a dwell-tier hit is CERTAIN (P>=1 = 1.000). A single dwell match is at/below E[max]; not exceptional. (Only the onset n reaches dwell among the 13 LA onsets, but ONLY via a y->h weak collapse AND selecting Hebrew/Aramaic over the yod-matching Arabic/Ugaritic — remove either freedom and 'dwell' evaporates.)

## Verdict input handed to the gate

- **ROOT_AND_GLOSS_ARE_GENERIC_SEARCH_OUTCOME (H2/H3 not exceptional)** — H2 (root) is a deterministic consequence of H1's /na/ under weak-radical freedom; H3 (gloss 'dwell') is a best-of-language/best-of-gloss selection, discarded by the literal-yod languages, and not favoured by observable formula structure. S_lex-style 'match exists' is a floor property. None of this clears E[max]; none is held-out evidence.
