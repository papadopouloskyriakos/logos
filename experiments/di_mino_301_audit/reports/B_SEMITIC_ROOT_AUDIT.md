# B — Semitic Root Audit (Di Mino H2: A-TA-I-*301-WA-JA contains N-W-Y)

**Prereg** DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c) · **Constitution** v2.2 · **Seed** 20260708 · generator `scripts/B_semitic_root_gloss_audit.py`. All counts script-generated (invariant 12). Non-circular: known Semitic values grade the benchmark only; *301 is the hypothesis.

## Reading under test

`A-TA-I-*301-WA-JA`: 5/6 signs = standard transferred LB values (`literature_match`, score 0). The one free parameter `*301=/na/` makes the last three signs `na-wa-ya` -> strip vowels -> **n-w-y** -> root **N-W-Y** glossed **"dwell"**.

## B1 — Verified root forms + meanings across the six admitted Semitic languages

| language | attested root | final radical | ends in YOD (matches na-wa-ya)? | gloss tier vs 'dwell' | attested gloss | sources |
|---|---|---|---|---|---|---|
| Hebrew | nwh | h | no | **exact** | dwell; abide; abode; habitation; pasture; rest; keep-at-home | Brown-Driver-Briggs; Strong's Hebrew Lexicon (H5115 navah / H5116 naveh); Klein; Koehler-Baumgartner |
| Aramaic | nwh | h | no | **near** | abode; dwelling; resting-place; rest | Sokoloff; Payne Smith; Jastrow |
| Akkadian | nw' | ' | no | **broad** | steppe; pasture; encampment; camp | Chicago Assyrian Dictionary (N/2; von Soden |
| Ugaritic | nwy | y | YES | **unrelated** | drive-away; expel; chase | del Olmo Lete & Sanmartin |
| Arabic | nwy | y | YES | **unrelated** | intend; purpose; resolve; journey; depart; be-distant; date-stone | Lane; Wehr; Quranic Arabic Corpus |
| Phoenician | — | — | no | **none** | (not attested) | Hoftijzer-Jongeling |

### The N-W-H / naveh competitor (the crux)

Hebrew "dwell" is the root **n-w-H** (final HE): the verb *navah* 'rest/dwell, abide' and — carrying most of the attestation — the NOUN *naveh* 'abode, habitation, abode of shepherds/flocks, pasture' (BDB; Strong H5115/H5116; Klein). The claim's `na-wa-ya` yields final **YOD** (n-w-y). So the "dwell" reading requires silently equating III-yod with III-he — a tertiae-infirmae **weak-root collapse** — and then leans on a mainly-NOMINAL 'abode/pasture' sense, not a verb.

The two languages whose *attested* root actually ends in yod give **unrelated** glosses: **Arabic** n-w-y = *nawa* 'to **intend**/resolve; to journey, be distant' (niyya 'intention'); **Ugaritic** n-w-y gloss debated ('drive away', SOURCE_UNCERTAIN). Akkadian *nawum* (n-w-'/m) = 'steppe/pasture/encampment' (broad, and again not -y).

## B (root density) — is "a matching root exists" exceptional?

| collapse regime | C1 values hitting a real root | hitting a dwell-tier gloss | hitting exact/near |
|---|---|---|---|
| strict | 31% | 0% | 0% |
| weak | 54% | 8% | 8% |
| weak+hollow | 77% | 8% | 8% |

Tertiae-infirmae/hollow roots are dense, so a real Semitic root sitting on the target skeleton is unremarkable. **H2 conclusion:** the N-W-Y root is a deterministic consequence of choosing /na/ plus generous weak-radical freedom — not independent held-out evidence.

## Source-dependency / honesty

- The weak-root neighbourhood table is a **curated, citation-tagged sample** (BDB-anchored) — a LOWER BOUND on real weak-root density, so it is conservative for the 'roots are dense' argument.

- Ugaritic n-w-y is flagged **SOURCE_UNCERTAIN** and excluded from load-bearing tier counts. Phoenician 'dwell' via n-w-h/y is **SOURCE_BLOCKED** (uses y-s-b).
