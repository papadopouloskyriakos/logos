#!/usr/bin/env python3
"""Source-dependency lineage-collapse checker (Constitution v2.0 Art. XI).

Art. XI: sources in ONE evidentiary lineage count as ONE vote — their concordance is NOT independent
replication. This module loads governance/source_dependency_graph.json and answers, mechanically:

  * given a set of cited sources, how many INDEPENDENT evidentiary votes do they actually represent?
    (= number of distinct lineages) — the effective source count that feeds effective_n (Art. VIII) and
    the information-budget panel's source-dependency field (Art. IX);
  * are these sources genuinely independent, or is their agreement one decipherment replicated?

Fail-loud (Art. XVI): an UNKNOWN source cannot be assessed for independence, so it raises rather than
silently counting as an independent vote. Deterministic; no DB.

CLI:
    python3 scripts/source_dependency.py --validate
    python3 scripts/source_dependency.py SRC-DAMOS SRC-VC-DOCS2 SRC-DMIC   # -> 1 effective vote
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_PATH = os.path.join(_REPO, "governance", "source_dependency_graph.json")


def load_graph(path=GRAPH_PATH):
    with open(path) as f:
        return json.load(f)


def _sources(graph):
    return graph["sources"]


def lineage_of(source_id, graph):
    """The evidentiary lineage of a source. Raises KeyError (fail loud) on an unknown source."""
    src = _sources(graph).get(source_id)
    if src is None:
        raise KeyError(f"unknown source '{source_id}' — cannot assess independence (Art. XI/XVI: fail loud)")
    return src["lineage"]


def collapse(source_ids, graph=None):
    """Group cited sources by evidentiary lineage. Returns {lineage_id: [source_ids...]} (sorted)."""
    graph = graph or load_graph()
    out = {}
    for sid in source_ids:
        out.setdefault(lineage_of(sid, graph), []).append(sid)
    return {k: sorted(v) for k, v in sorted(out.items())}


def effective_sources(source_ids, graph=None):
    """The number of INDEPENDENT evidentiary votes = distinct lineages (Art. XI -> Art. VIII effective_n)."""
    graph = graph or load_graph()
    return len(collapse(source_ids, graph))


def concordance(source_ids, graph=None):
    """Full independence assessment of a set of 'agreeing' sources. `raw_n` sources collapse to
    `effective_n` independent votes; agreement is independent replication ONLY if effective_n == raw_n."""
    graph = graph or load_graph()
    ids = list(dict.fromkeys(source_ids))                  # dedup, preserve order
    by_lineage = collapse(ids, graph)
    eff = len(by_lineage)
    collapsed = {lin: sids for lin, sids in by_lineage.items() if len(sids) > 1}
    is_indep = eff == len(ids)
    if is_indep:
        verdict = "INDEPENDENT_REPLICATION"
    elif eff == 1:
        verdict = "SINGLE_LINEAGE"                          # all one evidentiary vote (e.g. SHARED_DECIPHERMENT)
    else:
        verdict = "PARTIALLY_DEPENDENT"
    return {"raw_n": len(ids), "effective_n": eff, "independent": is_indep, "verdict": verdict,
            "by_lineage": by_lineage, "collapsed_lineages": collapsed,
            "note": "effective_n independent evidentiary votes (Art. XI); count agreement as effective_n, never raw_n."}


def validate(graph=None):
    """Self-consistency of the graph (Art. XIX): every lineage root + every derives_from target exists,
    every source's lineage is defined. Returns a list of problems (empty = OK)."""
    graph = graph or load_graph()
    srcs = _sources(graph); lineages = graph["lineages"]; problems = []
    for lid, lin in lineages.items():
        root = lin.get("root")
        if root and root not in srcs:
            problems.append(f"lineage {lid} root '{root}' is not a source")
    for sid, s in srcs.items():
        if s["lineage"] not in lineages:
            problems.append(f"source {sid} has undefined lineage '{s['lineage']}'")
        for dep in s.get("derives_from", []):
            if dep not in srcs:
                problems.append(f"source {sid} derives_from unknown source '{dep}'")
    return problems


def main():
    args = sys.argv[1:]
    graph = load_graph()
    if not args or args[0] == "--validate":
        problems = validate(graph)
        print("source_dependency_graph:", len(_sources(graph)), "sources,",
              len(graph["lineages"]), "lineages")
        print("VALIDATION:", "OK" if not problems else "\n  - " + "\n  - ".join(problems))
        return
    print(json.dumps(concordance(args, graph), indent=1))


if __name__ == "__main__":
    main()
