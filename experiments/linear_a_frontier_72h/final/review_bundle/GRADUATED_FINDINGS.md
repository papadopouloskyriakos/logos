# Graduated Findings (§12.4)

Machine-readable: `GRADUATED_FINDINGS.json` (count = 1). Reflects the terminal audit remediation
(E103R corrected joint null; verdict class unchanged).

## FINDING-1 — Recurrent A-initial positional enrichment in Linear A administrative units

- **Exact claim:** In Linear A administrative units of ≥2 signs, the sign **A** occupies initial position far
  more often than its within-unit multiset expectation, corpus-wide — a recurrent **A-initial positional
  enrichment** (an anonymous initial slot; relative constraint only).
- **Claim layer:** L2/L3 (structural / functional-positional). **Highest licence:** none.
- **Supporting evidence (4 orthogonal held-out axes):**
  - **Adaptive null (E022):** within-word permutation, PERMUTE p = **0.0002**; best-of-72-candidate maxT p = 0.0002
    (z 5.63 > null max-z 5.19); PC power 25/25, calibration false-graduation 0/300.
  - **Cross-site held-out (E023):** significant (raw + Holm) in **9/10 sites**; survives leave-one-site-out
    (drop Haghia Triada → p .001 on the remaining 675 words); clears 9 sites vs comparator median 2.
  - **Multi-axis held-out (E024):** significant in **5/6 support types** (Nodule = 0, A-initial absent on
    sealings) + **4/4 chronological phases**; survives support leave-one-out.
  - **Segmentation robustness (E103, corrected E103R):** rank-1 best-of-universe maxT survivor at p ≤ .01 under
    **three overlapping segmentation/selection variants derived from a single corpus lineage** (editor /
    divider-strict / numeral-anchored ledger-heads), z ≈ 17 (editor & divider) / 7.5 (numeral), dominating the
    next sign KU by ~2.4× in the editor baseline (2.2× divider, 1.1× numeral-anchored); PC power+calibration clean; leave-one-method-out evaluated mechanically from
    the frozen E022/E023/E024 artifacts and invariant. **Variant overlap quantified:** B_divider_strict shares
    87.6% of unit realizations with A_editor (1199/1369 identical; 170 editor units participate in merges
    yielding 166 divider-bounded units), and C_numeral_anchored is a function-restricted **subset** of A_editor
    (467/467 of its units are A_editor units) — so the materially distinct variants are two (editor-family,
    numeral-anchored). This axis is segmentation **robustness**, never independent replication.
- **Independent channels:** 1 (positional profile). **Effect size:** z ≈ 17 (baseline variant).
- **Held-out:** yes (site, support, chronology, segmentation). **Null:** yes (matched adaptive; campaign-wide
  pilot E104 and bound-based certification E104R: 1/400 false graduation, CP95 upper 1.18%).
- **Limitations:** single method-channel; a single corpus lineage (GORILA/silver); an alternate *sign inventory*
  (SigLA) cross-check was scoped but not run (SigLA is a different edition of the same inscriptions, not an
  independent lineage). "A-initial absent on sealings/nodules" is a genuine support-type boundary, not a failure.
- **Authorized interpretation:** a real, held-out-robust, cross-site, cross-period **A-initial positional
  enrichment** — a structural regularity of the LA administrative writing system. It is compatible with a
  recurrent initial functional or morphological slot; prefixhood, productivity, sound, and meaning are not
  established.
- **FORBIDDEN stronger interpretations:** any phonetic value for A (e.g. /a/), any morpheme meaning, any word
  reading, any language-family inference, and **morphological prefixhood** (or productivity) as an assertion.
  The absolute-value gate (E102) fails; **no value is licensed.**
- **Append-only note (corrected under E103R):** QUALIFICATION of E022's "sole survivor" wording (Art. XVII) — A
  remains the dominant, rank-1 initial-enriched sign in every variant; the corrected p ≤ .01 survivor sets are
  exactly: editor {A, KU, U, I, QA, *411, *306} · divider-strict {A, KU, I, U, QA, *411, *306} · numeral-anchored
  {A, KU, PA, DA}. Secondary survivor union (excl. A): **{*306, *411, DA, I, KU, PA, QA, U}** — stated as
  measured; the earlier note's {KU, U, I, QA} phrasing omitted the starred signs and predates the corrected null.

---
No other finding graduated. The vowel-class signal (E099) is real but single-channel and LA-untestable — see
`STRONG_LEADS_AND_FAILED_REPLICATIONS.md`.
