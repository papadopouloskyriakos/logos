# E204R amendment R1 (implementation defects, pre-gate; committed before rerun)

1. **Parser C hang (misctexts.html):** the source's unclosed <TD>/<TR> tags produce
   pathologically nested trees; C's walker double-traversed nested cells (exponential).
   Repair: standard HTML table recovery in the tree builder (a new <tr> auto-closes an open
   <tr>; a new <td> auto-closes an open <td>), and the row walker no longer re-walks cell
   subtrees. Tree semantics for well-formed tables unchanged.
2. **Designation grammar (both parsers, religioustexts 0 records):** designations may carry a
   support-class token BETWEEN prefix and number ("IO Za 2", "PK Zb 21"). The document
   detector accepts an optional intervening support-code token; the support keyword window is
   otherwise unchanged. Applied independently in C and D.
No gate, schema, exclusion, or classification rule changes. As-run outputs (none had been
produced for C beyond profiling; D never ran) are unaffected; this precedes any comparison.
