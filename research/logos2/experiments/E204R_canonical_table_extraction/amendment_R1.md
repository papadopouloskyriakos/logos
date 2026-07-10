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

3. **Parser C empty-string trap (latent, surfaced by fix 2):** `s[:1] in "iv"` is True for
   empty s (substring semantics) → infinite loop in is_locus on tokens like "i". Guard added.
   (Parser D's independent implementation already guarded — an incidental demonstration of
   why two parsers.)

# Amendment R2 (spec under-specification; committed before rerun)
Dual-parse comparison localized 154 statement disagreements to two spec gaps:
(a) **Divider bullets:** Younger's transcription divider "•" is punctuation, not statement
    content. Amended spec: standalone bullet tokens and leading/trailing bullets are stripped
    from statement and logogram fields (word-internal sign text unaffected).
(b) **Entity map completion:** numeric bullet references (&#149; &#183; &#8226;) map to "•".
    Parser C's stdlib charref decoding already conformed; Parser D's manual map now includes
    the numeric forms (implemented independently).
Numeric/flag fields were already at 100% agreement; this amendment touches text-normalization
semantics only. Gate thresholds unchanged. If residual disagreement remains after R2, it is a
representation result, not grounds for further rewriting.
