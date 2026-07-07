# Retrieved primary source — AI Clambake "AI Engineer Claims to Have Cracked Linear A"
URL: https://aiclambake.com/clamtakes/linear-a/  (friend-authored, dated 2026-06-16)
Retrieved: 2026-07-08 via WebFetch (page->markdown). Author of claim: Tom Di Mino.

## Core public claim (adjudicable)
- Inscription IOZa2 (Iouktas) line 1: "A-TA-I-*301-WA-JA · JA-DI-KI-TU · JA-SA-SA-RA-ME ..."
- Sign *301 assigned value "na" (a Linear-A-only sign).
- Root "nawaya" = "to dwell"; N-W-Y triconsonantal ("to dwell or inhabit" in Hebrew, Akkadian, and other Semitic).
- The word is a verb root appearing in regional forms across five peak-sanctuary sites on Crete.
- Figure 1: "A summary of the symbols in line 1 of the Minoan prayer inscription" (the only published table fragment).
- Tooling: Claude Code-built Python scripts querying GORILA + SigLA. Started January 2026; key pattern 2026-05-22.
- Semitic hypothesis: Linear A is an extinct Semitic precursor to biblical Hebrew (reviving Gordon 1957).

## Claimed extended results (NO published artifact)
- 40 signs with proposed readings (incl. 13 previously-unknown LA signs; 5 Linear B signs resolved).
- 408 Linear A terms translated to English (no table published).
- 9-page draft "Ya Diktu: Grammar of the Minoan Peak Sanctuary Libation Formula" (not public).
- No links to code repository, preprint, sign table, or word list in the article.

## Availability audit (2026-07-08)
- github.com/tdimino: 41 public repos; NONE contain decipherment code/sign-table/lexicon/manuscript
  (only "claude-code-minoan" = a ~/.claude config, unrelated).
- minoanmystery.org: consulting site; NO sign table, lexicon, manuscript, *301 value, or code.
- Secondary coverage (hyper.ai, follownews, braindetox) repeats the same facts; no primary artifacts.
=> EXTENDED_ARTIFACT_STATUS = SOURCE_BLOCKED for the 40-sign table, 408-lexicon, Ya Diktu manuscript,
   the 5 LB corrections, the logogram analysis, and the ~100k-simulation methodology.

## Figure 1 (minoan-fig1.png, sha256 651e50d9…) — EXACT transcription of "§3.1 Position 1: The Invocation Verb"
| Sign | AB Number | Linear B | Value | Morphological Function |
|---|---|---|---|---|
| A   | AB08 | B 08 | /ʾa/ | 1cs person prefix ("I") |
| TA  | AB59 | B 59 | /ta/ | tG reflexive-causative stem morpheme |
| I   | AB28 | B 28 | /i/  | Stem vowel (invariant across 14 attestations) |
| 301 | —    | (none) | /na/ | Root C₁ of √n-w-y "to dwell" (proposed) |
| WA  | AB54 | B 54 | /wa/ | Root C₂ |
| JA  | AB57 | B 57 | /ya/ | Root C₃ |

MECHANICAL CRUX (read off the table): 5/6 signs (A,TA,I,WA,JA = AB08/59/28/54/57) carry STANDARD transferred
Linear B values (/a/,/ta/,/i/,/wa/,/ya/) — conventional GORILA readings, NOT discoveries -> literature_match,
barred from counting as discovery. The ONLY novel value is *301=/na/, marked "(proposed)", with AB "—" and
Linear B "(none)" = NO cross-script anchor. The root √n-w-y = the last three signs *301-WA-JA read as CV
syllables na-wa-ya, vowels stripped -> n-w-y. So the entire word-decipherment pivots on ONE free parameter.
Di Mino's morphology labels (1cs prefix ʾa-, tG stem, stem vowel) are Semitic-styled but the surface structure
is prefix+stem+contiguous-root; whether that is "Semitic prefix-conjugation" or "agglutinative" is exactly what
the mechanical morphology audit (family C) adjudicates on held-out data rather than by assertion.
