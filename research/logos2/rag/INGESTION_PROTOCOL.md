# E211-RAG ingestion protocol (frozen)

1. Register + licence-check + sha256 every source BEFORE parsing.
2. Chunking: observational records = one record per chunk (doc/locus-anchored); scholarship
   = paragraph chunks with page locators; corpora = one entry per chunk.
3. Observation vs restoration vs inference flags carried from source flags; no OCR (all
   sources are digital text; OCR prohibited here).
4. Duplicates: content-hash dedup within an index; cross-index duplicates allowed (indexes
   are separated by EPISTEMIC CLASS, not content).
5. PIT: every chunk carries publication_date + availability_ts; queries declare cutoffs;
   the engine refuses chunks newer than the cutoff.
6. Index D ingestion marks contamination_flag=1 on any chunk containing a proposed LA value
   or reading; E213 sealing applies a hard index snapshot cutoff.
