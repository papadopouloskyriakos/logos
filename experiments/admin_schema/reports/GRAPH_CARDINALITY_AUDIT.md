# Graph cardinality audit (Stage 4.1 Correction 4)

**Semantics (now explicit):**
- **SIGN** = a sign OCCURRENCE (unique node id); its graphic identity is `opaque_id` (a TYPE key).
- **WORD_FORM** = a word OCCURRENCE (unique id); `opaque_id` = the composite form TYPE (repeats share it).
- **ENTRY** = a `/`-delimited administrative segment of a ROW (occurrence).
- **TOKEN** = a residual, unclassified OCCURRENCE (bracket-only / vestigial material not matching
  word/logogram/numeral/measure) — kept explicit rather than dropped, so damage is not silently normalised.
- NUMERAL / LOGOGRAM / MEASURE_MARKER = notation occurrences, **explicitly separate** node types (not TOKEN
  subclasses), so structural notation can be excluded from the non-trivial gate.

**Counts (LB):** WORD_FORM 15,777 occurrences over 4,843 distinct form-types; SIGN 44,974; ENTRY 16,042; ROW
14,841; NUMERAL 8,875; LOGOGRAM 6,738; MEASURE_MARKER 2,699; TOKEN (residual) 10,425.

**Invariants tested** (`test_graph_cardinality_invariants`, `test_no_duplicate_occurrences`):
each SIGN → exactly one WORD_FORM parent ✅; each WORD_FORM → exactly one ENTRY ✅; no orphan nodes ✅; node
ids unique per graph ✅; word-form TYPE (`opaque_id`) never mistaken for an occurrence (occurrences have
distinct ids) ✅. Entries may contain notation-only content (documented, allowed).
