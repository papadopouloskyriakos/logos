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


def _derives_transitive(sid, graph, seen=None):
    """All sources sid derives from, transitively."""
    seen = seen if seen is not None else set()
    for dep in graph["sources"][sid].get("derives_from", []):
        if dep not in seen:
            seen.add(dep)
            _derives_transitive(dep, graph, seen)
    return seen


def _dependent(a, b, graph):
    """Mechanical B4 test (Art. XI): two sources are DEPENDENT unless they have (i) distinct underlying
    edition AND (ii) distinct decipherment lineage AND (iii) no shared upstream lexicon — and neither
    derives from the other without demonstrating independence. Computed from the ATOMIC fields, not the
    hand-authored lineage label alone; `independence_demonstrated` releases the derives_from / shared-edition
    link (e.g. STRUCTURAL_RULES derives from DAMOS but is edition-independent)."""
    sa, sb = graph["sources"][a], graph["sources"][b]
    if a == b:
        return True
    if b in _derives_transitive(a, graph) and not sa.get("independence_demonstrated"):
        return True
    if a in _derives_transitive(b, graph) and not sb.get("independence_demonstrated"):
        return True

    def shared(field):
        va, vb = sa.get(field), sb.get(field)
        return va is not None and va == vb

    if shared("shared_decipherment_tradition"):
        return True
    if shared("upstream_lexicon"):
        return True
    if shared("underlying_edition") and not (sa.get("independence_demonstrated") and sb.get("independence_demonstrated")):
        return True
    if sa.get("lineage") == sb.get("lineage"):
        return True
    return False


def _components(source_ids, graph):
    """Union-find over the mechanical B4 dependency -> list of components (each a sorted list of sources)."""
    ids = list(dict.fromkeys(source_ids))
    for sid in ids:
        if sid not in graph["sources"]:
            raise KeyError(f"unknown source '{sid}' — cannot assess independence (Art. XI/XVI: fail loud)")
    parent = {s: s for s in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if _dependent(ids[i], ids[j], graph):
                parent[find(ids[i])] = find(ids[j])
    comps = {}
    for s in ids:
        comps.setdefault(find(s), []).append(s)
    return [sorted(v) for v in comps.values()]


def component_map(source_ids, graph=None):
    """{source_id -> component representative} — the mechanical evidentiary-unit id (for effective_n folds)."""
    graph = graph or load_graph()
    return {s: comp[0] for comp in _components(source_ids, graph) for s in comp}


def collapse(source_ids, graph=None):
    """Group cited sources into evidentiary components (mechanical B4). Returns {representative: [sources]}."""
    graph = graph or load_graph()
    return {comp[0]: comp for comp in _components(source_ids, graph)}


def effective_sources(source_ids, graph=None):
    """Number of INDEPENDENT evidentiary votes = mechanical B4 components (Art. XI -> Art. VIII effective_n)."""
    graph = graph or load_graph()
    return len(_components(source_ids, graph))


def concordance(source_ids, graph=None):
    """Full independence assessment. `raw_n` sources collapse to `effective_n` independent votes (mechanical
    B4); agreement is independent replication ONLY if effective_n == raw_n."""
    graph = graph or load_graph()
    ids = list(dict.fromkeys(source_ids))
    comps = _components(ids, graph)
    eff = len(comps)
    collapsed = {c[0]: c for c in comps if len(c) > 1}
    # lineage labels appearing in a collapsed (multi-source) component
    collapsed_lineages = {graph["sources"][s]["lineage"] for c in comps if len(c) > 1 for s in c}
    is_indep = eff == len(ids)
    verdict = ("INDEPENDENT_REPLICATION" if is_indep else "SINGLE_LINEAGE" if eff == 1 else "PARTIALLY_DEPENDENT")
    return {"raw_n": len(ids), "effective_n": eff, "independent": is_indep, "verdict": verdict,
            "components": comps, "collapsed": collapsed, "collapsed_lineages": sorted(collapsed_lineages),
            "note": "effective_n independent evidentiary votes (mechanical B4, Art. XI); count agreement as effective_n, never raw_n."}


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
