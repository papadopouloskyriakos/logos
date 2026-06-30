# Finding 2026-06-30 — Linear A's information floor: unicity is MET

**Headline: by Shannon's unicity-distance criterion, the Linear A corpus is more than large
enough to uniquely pin a decipherment. U ≈ 204–415 signs ≪ N ≈ 5,792. The "too little text"
excuse is false — and this corrects our own earlier prior and the common HN/forum claim.**

Computed by `scripts/corpus_info.py` on the real normalized corpus (1341 inscriptions,
5792 syllable-signs parsed from the lineara.xyz transliterations; V=259 raw-transliteration
tokens). Reproduce: `python3 scripts/corpus_io.py && python3 scripts/corpus_info.py`.

## The numbers (measured)

```
inscriptions        : 1341
total signs N       : 5792
unique inventory V  : 259            (raw transliteration: syllabograms + subscripts + logograms)
unigram entropy H0  : 6.210 bits/sign
entropy rate H_rate : 4.330 bits/sign   (bigram conditional; an UPPER bound on true rate)
redundancy D        : log2(V) - H_rate
```

Unicity distance `U = H(K) / D`, where `H(K) = V · log2(P)` is the entropy of the sign→sound
map (P = the value set each sign maps onto). Sensitivity over the plausible (V, P) space:

| V (inventory) | P (value set) | H(K) bits | U (signs) | vs N=5792 |
|---|---|---|---|---|
| 90 (clean syllabary)  | 30 (phonemes) | 442  | **204** | U ≪ N |
| 90  | 60 (syllables) | 532  | **246** | U ≪ N |
| 180 | 60 | 1063 | **336** | U ≪ N |
| 259 (raw) | 30 | 1271 | **345** | U ≪ N |
| 259 | 60 | 1530 | **415** | U ≪ N |

These are bigram-based **upper bounds** on U — trigram conditional entropy is lower, which
raises D and *lowers* U further. The verdict is robust: in no plausible scenario does U
approach N. **There is enough ciphertext.**

## Why this is sound (and where it isn't)

Unicity distance for a *substitution cipher* measures the plaintext language's redundancy D
from the ciphertext itself — valid because substitution preserves n-gram structure. Linear A
as a syllabic substitution fits this model, so measuring D from the sign sequences is the
standard approach. The script's own redundancy is a legitimate proxy here.

**Caveat that could raise difficulty (does not flip the verdict):** if Linear A is not a clean
substitution — logosyllabic with heavy logograms, underspelling (omitting sounds, like Linear
B), or abbreviation-heavy — the effective key is larger than V·log2(P) and the simple model
understates difficulty. But the margin (U is ~14× below N at the worst point) is wide; it
would take a script *very* far from substitution to flip "determinable" to "underdetermined."

## What this changes (the honest correction)

- **Refuted:** "Linear A has too little surviving text to be deciphered" / "unicity distance
  is not met" — a claim made on HN and in our own `docs/linear-a-claims-2026.md`. The data
  says otherwise. Data quantity is **not** the blocker.
- **The real obstacles** (now sharpened): 
  1. **No known cognate language to map to** — Luo 2019's limit; the map has a target-space
     but no target. *This is what the cross-script A↔B JEPA is meant to attack* (manufacture a
     cognate-like target from the 60 shared signs).
  2. **The multiple-testing / search trap** — U<N says a unique consistent map *exists* in
     principle; it does NOT say an algorithm finds it, and it does NOT stop a Di Mino-style
     root-match cherry-pick from producing a false positive. The Deflated-Sharpe / effective-n
     discipline is the cure, not more text.
  3. **A mixed inventory** (syllabograms + logograms + numerals conflated in V=259) that a
     real decipherment must separate.

## Implication for the roadmap

Don't chase corpus size. Attack (1) the cognate-absence via cross-script JEPA transfer and (2)
the search via DSR deflation + held-out verdicts. The Luo-baseline null ("no cognate ⇒ can't
pin a map") now reads more precisely as an *algorithmic* null, not an *information-theoretic*
one — which makes the JEPA "manufacture a target" bet the highest-leverage idea in the plan.
