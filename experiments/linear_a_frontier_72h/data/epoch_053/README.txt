EPOCH-053 data artifacts (anonymous form tuples; L2/L3 distributional only).

Files:
- entry_words.json    : list of anonymous entry-word form tuples (word whose next stream token is 'num')
- nonentry_words.json : list of anonymous non-entry-word form tuples
- site_entry.json     : {site: [form tuples]} entry-words per site
- site_nonentry.json  : {site: [form tuples]} non-entry-words per site
- global_metrics.json : size-matched global TTR/entropy gap + permutation p
- cross_site.json     : per-site size-matched restriction test
- loo.json            : leave-one-site-out (drop Haghia Triada)
- positive_control.json : PC detect + false-positive results

All forms are sign tuples; no decoding, no phonetics, no semantics, no values.
