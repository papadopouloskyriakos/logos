# DĀMOS courtesy email — DRAFT for the operator to send

**Action: operator-only** (outward human contact; the autonomous agent does not send email). Cheap
insurance on a relationship the project's credibility will route through. Send after, or alongside, the
harvest.

**To:** Federico Aurora — `federico.aurora@ub.uio.no` (DĀMOS maintainer, University of Oslo Library)
**Subject:** DĀMOS Linear B — non-commercial research use + a question on bulk access

---

Dear Dr Aurora,

I'm using DĀMOS (https://damos.hf.uio.no/) for a non-commercial computational-research project on
Aegean scripts (using the deciphered Linear B corpus as a known-answer control for Linear A work). I
wanted to flag, as a courtesy, that I've been harvesting the public document endpoint
(`/ajaxitem/<id>/`) politely — single-threaded, ~1 request/second, with a descriptive User-Agent —
and that everything is stored locally with provenance and the requested citation attached:

> Aurora, F. (2015). *DĀMOS (Database of Mycenaean at Oslo): Annotating a fragmentarily attested
> language.* Procedia – Social and Behavioral Sciences 198, 21–31.

I'm treating the content under its stated **CC BY-NC-SA 4.0** licence (non-commercial, attribution,
share-alike). If you'd prefer a different access method — or can share a bulk export / dump — I'd much
rather use that than crawl the site, and I'm happy to adjust the rate or stop entirely on request.

I should also note the **ShareAlike** implication for my side: should any *derived* corpus be released
publicly, it would inherit CC BY-NC-SA 4.0 with full attribution to DĀMOS.

Thank you for building and maintaining such a valuable resource.

Best regards,
[name / affiliation]

---

*Notes for the operator:* harvest is `scripts/fetch_damos.py` (gitignored data under
`corpus/bronze/linearb/damos/`, PROVENANCE included). The SA clause only bites if a derived corpus is
*published*; private research use is unencumbered.
