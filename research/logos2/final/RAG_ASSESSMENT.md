# RAG assessment (E211) — RAG_USEFUL_FOR_AUDIT_ONLY

## What was built
The smallest reproducible stack: SQLite FTS5 (BM25), no external services, database
gitignored, snapshot pinned by `rag/INDEX_MANIFEST.sha256` (embedded at closure in the E213 seal as
the hard scholarship cutoff). Five epistemically separated indexes, 12,928 chunks total:

| index | content | chunks | contamination handling |
|---|---|---|---|
| A_OBS | silver transcriptions + E204R2 canonical fraction records | 2,726 | observation/restoration labelled per chunk |
| B_SCHOL | primary scholarship paragraphs; SM2017 metadata-only rows | 294 | published equations flagged as prior art |
| C_COMP | comparative .cog corpora | 9,484 | separate table; never merged with A |
| D_CLAIMS | interpretive claims ONLY (e.g. Rjabchikov 2025) | 124 | every chunk contamination-flagged + text-prefixed `INTERPRETIVE_CLAIM_ONLY` |
| E_ADV | seeded adversarial/null canaries | 300 | fabricated, labelled |

## Measured performance (n is small; stated exactly)
The frozen 12-query harness had 7 mechanically scoreable queries. BM25 recall@5 = 5/7
(0.714), MRR@5 0.643; random baseline 4/7 (0.571); no-retrieval 0. The margin over random
is one query on n = 7 — far too weak to ground any performance claim beyond "retrieval
functions." The dense arm (Ollama) was deferred, recorded as a deferred arm, not a failure.

## Answers to the closure questions
- **Did RAG outperform BM25?** Not applicable as posed — BM25 *is* the retrieval arm; no
  dense/hybrid arm ran to compare against it. BM25 beat random by 1/7 queries and
  no-retrieval by 5/7.
- **Did RAG improve contradiction retrieval?** NOT ESTABLISHED. The `contradictory_evidence`
  query class was not mechanically scoreable in the frozen harness (hit@5 = null); no claim
  is made.
- **Did RAG create contamination risk?** The risk exists by construction and was contained,
  not eliminated: both hard contracts pass mechanically (Index-D chunks always carry the
  contamination flag; temporal-cutoff filtering excludes post-`as_of` sources). Interpretive
  sources are indexed claims-only. No RAG output was ever placed on an evidential path.
- **Did RAG produce any candidate anchor worth independent testing?** No.

## Standing rule
RAG is **NOT_A_CHANNEL** (E212): retrieval over the same corpora can surface provenance and
prior art for audit, but cannot constitute evidence, confirm a reading, or count as an
independent channel. Banned framings ("RAG confirmed", "retrieved proof") are enforced by
`verifiers/run_battery.py`.
