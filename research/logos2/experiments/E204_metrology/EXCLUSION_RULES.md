# E204 extraction exclusion rules (frozen; both parsers implement independently)

HARD EXCLUSIONS (a record or line is dropped when):
1. The line contains a MODERN DECIMAL GLOSS (digits '.' digits, e.g. "8.50") — Younger's
   interpreted values. Whole line excluded.
2. The line is editorial/commentary prose: contains any of the (case-insensitive) markers
   {according, perhaps, sometimes, found, distribute, gave, record, note, cf., see, comments,
   update, bibliography, "="} outside a transcription locus, or lacks a locus anchor.
3. Translated/derived summaries (lines after "TOTAL" glosses or English sentences).
4. Records without a traceable source location (no document id in scope, or no locus).
5. Duplicated derived summaries (Younger repeats some documents in lexicon.txt: ONLY
   HTtexts/misctexts/religioustexts are extraction sources; lexicon/biblio/main are excluded
   files entirely).

FLAGS (kept, not excluded): '?' -> uncertain=1; '[' ']' -> restored=1; '{ }' editorial sigla
kept as logogram-field annotations; '<' '>' joins; '*' sign numbers are ordinary tokens.
Fraction letters ONLY from the frozen alphabet {J,E,F,K,L,B,H,D,W,X,Y} as isolated capitals
(or juxtaposed sequences) in the number zone; any other capital letter there -> record kept
with fraction_seq='' and anomaly flag (never guessed).
NO ARITHMETIC INFERENCE at extraction: fraction letters are opaque tokens; no values assigned.
Document identity: Younger designation (e.g. "HT 9", "ZA 4 a"); site from designation prefix
via the frozen prefix table in SCHEMA.json; duplicates (same doc in two files) resolved by
precedence HTtexts > misctexts > religioustexts, logged.
