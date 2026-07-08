# Search protocol

1. Enumerated all refs (`git for-each-ref` heads+remotes), tags, worktrees (§BRANCH_AND_WORKTREE_MAP).
2. Enumerated every experiment dir per worktree; mapped each UNIQUE campaign dir to its authoritative worktree
   (owning/latest branch) to avoid double-counting inherited foundation dirs.
3. Generated data/ARTIFACT_INDEX.csv = 923 artifacts (reports/data/scripts/prereg across all unique dirs +
   docs/findings paper methods).
4. Fan-out forensic extraction: one agent per campaign lineage reads its committed reports/data/STATUS/
   decision-logs/prereg/verdict rows, extracts METHOD_INSTANCE records (canonical fields + status/outcome enums),
   traces load-bearing numbers to artifacts, flags contradictions, lists artifacts covered.
5. Synthesis: merge instances -> METHOD_INSTANCES + METHOD_LINEAGES + RESULT_NUMBERS + STATUS_CONTRADICTIONS;
   compute UNMAPPED_ARTIFACTS = ARTIFACT_INDEX minus covered; write master + supporting reports.
6. Completeness proof: every ARTIFACT_INDEX row mapped or classified (irrelevant/duplicate/inaccessible).

NON-DESTRUCTIVE: no new experiments; no prior verdict/paper edits; read-only over research branches.
