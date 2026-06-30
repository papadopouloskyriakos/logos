# "English is a Semitic language": the failure mode logos is built to catch

This note explains the single intuition the whole logos discipline is organised against, and points to
the exact machinery that defends against it. It is a *methodological* demonstration, not a claim about
English or Semitic.

## The trick

Pick any two languages. Give yourself (a) a small target corpus, (b) freedom to choose which words to
compare, (c) a large reference — a dictionary or a reconstructed proto-language with hundreds of roots
and permissive sound-correspondence rules — and (d) no held-out test. You can now "prove" almost any
affiliation you like. To "show" that **English is a Semitic language**, you cherry-pick:

- *English* "be" ~ Semitic *b-*… ; "water" ~ a root with *w*…; "mother/mama" ~ a nasal root; and so on,
- accepting near-matches, allowing meanings to drift ("give" ≈ "dwell" if you need it to), and
- counting the hits while quietly ignoring the far larger number of words that did **not** match.

Each individual comparison looks suggestive. The conclusion is nonsense. The error is not in any one
match — it is that the *number of comparisons you were free to try* was never paid for. With enough
candidate roots and a small enough corpus, a pile of individually-plausible matches is the **expected**
outcome under pure chance. This is the mechanism behind a large share of failed decipherments: a tiny
corpus + an unknown language + a thesaurus of candidate readings lets a determined analyst translate
almost anything, and *internal consistency on the cherry-picked set feels like confirmation.*

## Why undeciphered scripts are maximally exposed

Linear A makes every ingredient worse: ~7,400 sign occurrences (a few printed pages of text), short and
formulaic words, no known related language, and a partly lossy corpus. The space of candidate
phonetic/lexical readings dwarfs what that little text can constrain. So a method that "succeeds" on
Linear A has, by default, **not** earned belief — it has to *prove* it is not doing the English-Semitic
trick.

## How logos defends against it (the machinery, not a promise)

logos treats every positive as guilty until proven innocent, with four concrete defences:

1. **The fabricated-language canary (`L_fake`).** Before trusting a method, run it on a *fabricated*
   corpus calibrated to the real sign statistics but carrying **no genuine morphology or language**. If
   the method "finds" the same structure there, the structure is a statistical echo, not a reading. This
   is a hard false-positive floor. *Worked example:* the morphology induction found pre-registered
   affixes that beat a shuffle null — but **not** the `L_fake` bigram floor, so logos reported the null
   instead of a "result" (`docs/findings/2026-06-30-direction-a-morphology.md`,
   `scripts/comparison/lfake.py`).
2. **Multiple-testing deflation.** Every claim is corrected for the number of hypotheses × signs × roots
   that were *free to be tried* (effective-n / deflated significance, after Bailey & López de Prado). A
   match rate without this correction is meaningless — it is exactly the uncounted-comparisons error
   above.
3. **Contamination control (the literature index).** A "discovery" that merely reproduces a
   value already published in the literature is shared-source contamination, not independent evidence.
   logos indexes published readings (`L_known`) and partitions the truly literature-unseen signs
   (`L_virgin`); discovery claims may rest only on held-out success on `L_virgin` signs
   (`scripts/comparison/litindex.py`).
4. **Pre-registration + a held-out gate.** The hypothesis (which signs, which reading, which language
   family, the falsifiable prediction) is hash-keyed and timestamped *before* the test, and the verdict
   is computed mechanically against held-out material. You cannot move the target after seeing the data.

## The takeaway

The English-Semitic demo is not a strawman; it is the precise shape of the most common self-deception in
decipherment. logos's contribution is not a cleverer way to find matches — it is the **discipline that
makes a match cost what it should**, so that a reading which survives has earned the right to be
believed, and a corpus that cannot support one is *shown* to be unable to, rather than overfit anyway.
See also the worked failure case in `docs/linear-a-claims-2026.md`.
