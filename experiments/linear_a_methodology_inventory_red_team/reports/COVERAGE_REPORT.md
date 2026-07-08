# Coverage report (independent denominator)

Denominator from the INDEPENDENT content-hash enumeration (986 distinct-content artifacts across 12 worktrees),
NOT Prompt 1's index.

| metric | value |
|---|---|
| independent distinct-content artifacts | **986** |
| Prompt 1 index | 923 (undercount 63: 41 .pyc + 11 reference + ~11 branch STATUS/ledger + material misses) |
| method instances (P1 → verified) | 214 → **215** (+EA-13) |
| rows verified | 215 |
| VERIFIED / MINOR / MATERIAL_ERROR | **203 / 12 / 0** |
| UNSUPPORTED / MISSING_ARTIFACT / DUPLICATE / WRONG_LINEAGE | 0 / 0 / 0 / 0 |
| load-bearing numbers checked | ~60 — all REPRODUCED / ARTIFACT_VERIFIED (0 MISMATCH, 0 MISSING) |
| **method coverage** | **214/215 = 99.5%** (1 omission found + added) |
| **artifact coverage** | **986/986** mapped or excluded-with-reason (41 .pyc + 11 reference excluded) |
| new unresolved contradictions | 0 (P1's 48 stand; CSA-clamp ERRATUM confirmed accurate) |

**Exhaustive coverage is claimable:** every distinct-content artifact is mapped to a method instance or excluded
with a stated reason; the single method omission (EA-13) is found and added.
