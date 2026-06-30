# Pre-registration ADDENDUM — Salgarella-2025 affix inventory + Davis positional grammar (Direction A)

**Registered 2026-06-30, as a NEW dated pre-registration** (the original
`docs/prereg-morphology-2026-06-30.md` is frozen and never edited; this is a second dated addendum,
alongside `prereg-morphology-stratification-addendum-2026-06-30.md`). Governs any **stratified
morphology re-run**; the first pooled run stands under the original pre-reg.

**Motivation.** The body of **Salgarella 2025** (*Writing in Bronze Age Crete*), now acquired and
analyzed (`docs/related/salgarella-2025.md`, §7/§8 claims adversarially verified against the source),
**confirms** the registered Davis 2013 inventory (so the frozen pre-reg is **not** stale) but supplies
structures the frozen pre-reg does not encode, and the current synthesis **does not adopt** Thomas
2020's segmentation. This addendum registers those additions BEFORE the stratified run, so the model
cannot be tuned to them after the fact (invariant 8).

## H4 — Davis six-position Libation-Formula positional grammar (Salgarella 2025 §7.2 / Davis 2013)

**Primary source now in hand (Davis 2013, Kadmos 52:35–52) — and the two templates differ; register
both.** The "give/gift" gloss is **Duhoux's (1992, 80)**, adopted by Davis 2013 as his working gloss;
`*301` keeps **no phonetic value**. The slot assignments are NOT identical across the two sources:
- **Davis 2013 (p.41):** seq1 = V "gives" · seq2 = **S, the dedicant's name** · seq3 = **O,
  `ja-sa-sa-ra-me` "offering"** · seq4 "requesting" · seq5 "(a) favour" · seq6 "divine". Sequences 1–3
  form a clause that can stand alone; 4–6 a dependent clause that "never occurs on its own."
- **Salgarella 2025 §7.2:** seq1 verb · seq2 **place-name** · seq3 **dedicant** · seq4 `A/JA-SA-SA-RA-ME`
  object · seq5 subordinate verb · seq6 `-TE` "from" phrase (a refined/expanded template).
- *Test:* on held-out libation inscriptions, recover the **positional slot assignment** (sequence →
  slot) above a permutation null that shuffles slot labels, and report **which template the data
  supports** (the seq2/seq3 dedicant-vs-place-name divergence is the discriminating cell). This is a
  *positional-grammar* prediction the frozen pre-reg (affixes only) does not encode. **No phonetic
  value** is assigned to `*301`. (Frozen-pre-reg correction: H1a's "OSV <1% of languages" framing is
  imprecise — Davis 2013 argues SVO is "unattested in the ancient eastern Mediterranean," so SOV/VSO
  are likeliest, and of 7 ancient VSO languages **none allow OSV** (p.36, p.48–49 n.64); use that.)

## H5 — Davis whole-unit vs Thomas morpheme segmentation, HEAD-TO-HEAD (do not assume Thomas)

Salgarella/Davis segment the verb's prefixal material as **whole units `A-TA-` / `TA-NA-`**; Thomas
2020 cuts `a-/ta-/na-/t-`. The frozen pre-reg registered Thomas's cuts; the current synthesis does not
adopt them.
- *Test:* register **both** analyses and let the segmenter adjudicate mechanically — does the induced
  boundary on the `i-*301` verb fall at the whole-unit edge (`A-TA-|`, `TA-NA-|`) or at Thomas's
  morpheme cuts, on held-out forms, above null? Report which analysis the data supports; **neither is
  assumed**. Multi-attestation forms that constrain the segmentation: **`ta-na-i-*301-u-ti-nu`**
  (IO Za 6), **`a-ta-i-*301-de-ka`** (ZA Zb 3).

## H6 — Benchmark-blessed §8 affix set (Salgarella 2025 §8, with primary attributions)

Each must recur on ≥2 distinct stems across distinct hands/deposits (per the stratification addendum)
above the within-form permutation null + the DSR-deflated bar:
- `-TE / -TI` = "from" / "of" (Valério 2007) — **confirms registered H3 `-te/-ti`**.
- `I- / J-` = "to" / "at" (Duhoux 1997) — the locative/allative prefix (registered H3 `i-`).
  **Triple convergence:** Davis 2013 (p.50, Greenberg Universal 3) independently *predicts* Minoan
  should have "prepositions or adpositional **prefixes**" (VSO ⇒ prepositional, 52/57 of Dryer's VSO
  languages), so a prepositional `I-/J-` prefix is exactly what his typology predicts — Duhoux 1997 +
  Salgarella §8 + Davis 2013 all agree.
- `-JA` = adjective-forming suffix (Younger 2024, *Linear A Texts: Introduction* §13) — relates to
  registered Thomas `-ja`.
- `-RU / -RE` = likely the Minoan counterpart of Greek masculine `-os` (Steele & Meissner 2017, via
  personal-name comparison) — the v2-flagged candidate case-markers, now sourced.
- `-A` = feminine ending on personal (women's) names (Godart 1984 / Schoep 2002 / Younger 2024) — a
  **nominal** morphology claim tested on administrative (non-libation) words, extending H3's domain.
- `A/JA-SA-SA-RA-ME` = invariant direct-object lexeme (slot 4) + the `A- ~ JA-` word-initial
  alternation (Karetsou, Godart & Olivier 1985) registered as a testable sandhi/contextual rule.
- `KI-RI-TA2 ~ KI-RO` = a `-TA2` deverbal/derivational relation tested on administrative vocabulary.

## H7 — Typology priors (deterministic penalties, not the LLM)

The benchmark typology is **agglutinative** (multisyllabic prefixing; Duhoux 1978, endorsed Salgarella
2025 §8) with **provisional VSO** order (Davis 2013, hedged "may be"). Register as deterministic
priors: any induced analysis implying **non-concatenative root-and-pattern (Semitic) or fusional-IE
inflection** is penalized as contra-benchmark. (This is also the structural refutation of the
Di Mino `*301`/Semitic claim — his own table draws a concatenative prefix-stacked verb, which is the
*opposite* of Semitic morphology; see `litindex.py` CITATION_DIMINO + `linear-a-claims-2026.md`.)

## Mandatory channel exclusion — abbreviations (field intel 2026-06-30)

Short list-headers (1–3 signs) and seal-signs are likely **abbreviations**, not morphological forms;
they masquerade as affix variants and pollute affix statistics. Before affix induction, **segregate an
abbreviation channel** (heuristic: ≤3-sign tokens in heading/seal positions) and **exclude it from
affix induction**, reporting it separately. This sits alongside the stratification requirement
(`prereg-morphology-stratification-addendum-2026-06-30.md`).

## Falsification + acceptance (unchanged discipline)

- Null models the model must FAIL on: within-inscription sign-order shuffle; the **L_fake** corpus.
  A candidate that "confirms" on L_fake or beats the bigram floor is void.
- Multiplicity: H4–H7 affixes/structures tested jointly; Deflated-Sharpe / effective-n correction,
  deflated for within-hand/within-site non-independence (stratification addendum).
- **No phonetic claim.** Confirmed affixes/slots are structural objects; sign values are never imputed
  from cross-script phonetics.
- Outcomes per the original pre-reg (CONFIRM / EXTEND / REFUTE-NULL / NO-POWER), per stratum and on
  cross-stratum stability. Counts are generated, not hand-written. Frozen at commit time.
