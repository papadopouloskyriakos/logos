# Parser A specification (line-regex strategy over .txt renderings)

Input: HTtexts.txt, misctexts.txt, religioustexts.txt (raw bytes, latin-1-tolerant read).
Logic (regex-based, line-oriented):
1. Document scope opens at /^ ?(HT|ZA|KH|PH|KN|ARKH|PE|PK|MA|TY|GO|IO|KO|PL|PS|SA|SY|VRY|KAM|APO|ARM|KE|MI|POP|PR|SI|SKO|THE|TRA|WA|ZOU?)[A-Z]* ?[0-9]+[a-z]?\b.*(tablet|nodule|roundel|sealing|vessel|bar|lame|Za|Wc|Wa|Wb|Zb|GORILA)/ ;
   doc_id = the designation token(s).
2. Locus lines match /^ ?[ab]?[iv]*\.?([0-9]+(-[0-9]+)?|supra|infra)\b/ or /^ ?(side|edge|lat)\./.
3. Within a locus line, tokenize by whitespace and bullets; the NUMBER ZONE is the maximal
   suffix of tokens matching integers or fraction letters; preceding hyphen-joined uppercase
   groups = context word; +/logogram tokens (X+Y, {\*nnn}) = logogram field.
4. CONTINUATION: a following line consisting ONLY of fraction letters/whitespace appends to
   the previous record's fraction_seq.
5. Exclusions per EXCLUSION_RULES.md implemented with parser-A's own regexes.
6. KU-RO / PO-TO-KU-RO context words set is_kuro.
Output: schema-conformant CSV, parser="A". No code shared with Parser B beyond SCHEMA.json.
