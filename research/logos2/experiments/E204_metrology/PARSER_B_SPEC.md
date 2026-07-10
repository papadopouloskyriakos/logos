# Parser B specification (HTML tag-stripping character FSM over .html renderings)

Input: HTtexts.html, misctexts.html, religioustexts.html (independent rendering of the same
source; different whitespace/line structure than the .txt files).
Logic (NO record-level regexes; explicit state machine):
1. Strip tags with a char-scanner (in_tag flag), decode entities (&amp; etc.), normalize
   NBSP; build a token stream with explicit newline tokens from <br>/<p>/<tr> boundaries.
2. FSM states: SEEKING_DOC -> IN_DOC -> IN_LOCUS -> NUMBER_ZONE -> (CONTINUATION|CLOSED).
   Document detection: token pair (SITE-PREFIX, integer) followed within 12 tokens by a
   support keyword token (tablet/nodule/roundel/...) or 'GORILA'.
   Locus detection: token matching side.line shape via character-class walk (letter? digits
   dot digits, dash ranges), not regex.
3. Number zone: scan tokens right-to-left from end of locus segment; classify each token by
   character composition (all-digits -> integer; all-chars in frozen fraction alphabet,
   len<=2 -> fraction letter; else stop).
4. Continuation: after a record, if the next non-empty token-line contains ONLY fraction
   letters, append.
5. Exclusions: implements EXCLUSION_RULES.md via its own word-set sentence detector (>=4
   consecutive lowercase English tokens => prose) and its own decimal-gloss detector
   (digit-dot-digit char walk).
6. KU-RO detection via token equality on the hyphen-joined context word.
Output: schema-conformant CSV, parser="B". Shares ONLY raw files + SCHEMA.json with Parser A.
