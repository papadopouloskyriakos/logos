# logos-jepa (service scaffold — phase 5, not yet deployed)

The GPU representation layer. **Not trained or deployed in v0** — gated behind the corpus +
symbolic verdict layer (DESIGN.md §2, roadmap phase 5), because Linear A (~7.5k signs) is too
small to pretrain a good latent on A alone.

## Plan (port from agora-jepa, don't rewrite)

Reuse the proven harness in the sibling repo:
`../finops-agora/services/agora-jepa` + `../finops-agora/scripts/jepa_{train,infer,validate}.py`
+ `../finops-agora/docs/jepa-market-encoder.md`.

| agora (market) | logos (script) |
|---|---|
| a return series | a sign sequence |
| latent of future market state | latent of next sign-cluster |
| TS-JEPA encoder | sequence TS-JEPA encoder |
| + (new) sign-image I-JEPA | palaeographic representations (closes the CV gap) |
| + (new) cross-script A↔B joint embedding | the novel transfer bet |

## Host

`nllei01gpu01` (RTX 3090 Ti, 24 GB), alongside agora-jepa / agora-forecast / Ollama (:11434).
Ollama provides the local judge (gemma3) and RAG embeddings (bge-m3), as in agora.

## When to build

After: (1) corpus ingest + the real unicity number, (2) the Luo baseline reproduced, (3) the
predict→verdict scaffold. Then train sign-image + sequence JEPAs on the Linear B corpus (larger,
known phonetics) for cross-script transfer to Linear A. Measure against an n-gram baseline; a
null (JEPA doesn't beat n-grams on the tiny A corpus) is an honest, publishable result.
