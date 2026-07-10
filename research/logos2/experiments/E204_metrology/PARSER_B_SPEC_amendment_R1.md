# Parser B spec amendment R1 (defect repair; committed before amended rerun)

First-contact finding: the HTML renders records as TABLE ROWS — <TR> with <TD> cells in the
author's own column layout ("side.line | statement | logogram | number | fraction"), matching
his printed column-header line. Parser B's original line-reconstruction model (tags->newlines)
shattered each record across cells (coverage 25 records vs A's 1362).

Repair: Parser B becomes a TABLE-ROW parser: one <TR> = one candidate record; cell texts map
positionally to schema fields (first cell must be a locus token; last two non-empty cells are
number and fraction zones; middle cells are statement/logogram). Document detection unchanged
(FSM over inter-table flattened text). Exclusion rules unchanged. This INCREASES independence
from Parser A (author-table semantics vs whitespace heuristics) and shares no code with A.
The original parser_b output is preserved as parser_b_output_R0_invalid.csv.
