# E211-RAG evaluation report (v1.1 final for this campaign)

**Verdict: RAG_USEFUL_FOR_AUDIT_ONLY.** Stack: SQLite FTS5 (BM25) over five separated indexes
(A 2726 / B 294 / C 9484 / D 124 / E 300 chunks; subscript-folded text; PIT metadata per chunk).
Benchmark (12 frozen queries): BM25 recall@5 0.714, MRR 0.643 vs random 0.571, no-retrieval 0.
Contracts: Index-D INTERPRETIVE_CLAIM_ONLY flagging PASS; temporal-cutoff refusal PASS
(2016 cutoff correctly returns zero for 2017 scholarship).

Limitations (recorded, binding on any use): benchmark v1 has weak gold labels on single-source
tables (random inflated there); dense/hybrid/rerank arms DEFERRED (Ollama arm not run — recorded
as deferred, not failed); GraphRAG not reproducible in-repo → not attempted. Two harness repairs
(FTS5 token quoting + OR-fallback; subscript folding) were retrieval-infrastructure defects,
documented pre-verdict. RAG output is an audit/provenance layer ONLY: it is never evidence,
never an independent channel, and cannot graduate anything above L2.
