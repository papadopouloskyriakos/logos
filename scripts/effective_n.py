#!/usr/bin/env python3
"""Evidence-unit effective sample size (Constitution v2.0/2.1 Art. VIII).

`raw_n` counts rows; `effective_n` counts INDEPENDENT evidence units. Two records are NOT independent if
they share a dependency (a joined fragment, a formula cluster, a lexical/morphological family, a scribe, a
document series, a source lineage, a document). This module groups evidence by the dimensions a claim must
be independent along and reports the BOTTLENECK — a claim's evidence is at most as independent as its most
collapsed grouping. Distinct from `logos_stats.effective_n` (a finance time-overlap uniqueness — wrong
primitive for corpus evidence) and `searchlog` N_eff (a trial count). Composes the Art. XI source-lineage
collapse. Deterministic; no DB.

CLI:
    python3 scripts/effective_n.py   # runs the doctest-style demo
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)


def _val(item, key):
    v = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
    return v


def distinct_units(items, by):
    """Number of distinct non-null group values/tuples on dimension(s) `by` (str or list)."""
    keys = [by] if isinstance(by, str) else list(by)
    seen = set()
    for it in items:
        vals = tuple(_val(it, k) for k in keys)
        if all(v is not None for v in vals):
            seen.add(vals)
    return len(seen)


def effective_n(items, dims, source_key="source_id", require_source=False):
    """Report raw_n + per-dimension marginals (UPPER bounds) + the JOINT effective_n.

    `dims` are the grouping dimensions the claim must be independent along (e.g. ['lexical_family',
    'site', 'document_id']). Two records are dependent if they SHARE a value on ANY of those dims (or the
    Art. XI source lineage), so the honest independent-evidence count is the number of connected components
    under union-find over all of them — which is <= the min of the per-dimension marginals (the min
    OVERSTATES independence when the claim must be independent along several dims simultaneously). The
    conservative joint count is the headline `effective_n`; graduation keys off it (guilty-until-proven).

    If items carry `source_key`, dependent editions/lexica are collapsed to one Art. XI lineage and folded
    into the union-find. `require_source=True` (for graduating calls) raises if no source provenance is
    present, so the lineage collapse cannot be silently skipped."""
    dims = list(dims)
    by_dim = {d: distinct_units(items, d) for d in dims}
    proj = [{d: _val(it, d) for d in dims} for it in items]              # projection for the union-find
    link_keys = list(dims)
    src_ids = [_val(it, source_key) for it in items]
    if any(s is not None for s in src_ids):
        from scripts import source_dependency
        graph = source_dependency.load_graph()
        for p, s in zip(proj, src_ids):
            p["_lineage"] = source_dependency.lineage_of(s, graph) if s is not None else None
        link_keys.append("_lineage")
        by_dim["source_lineage"] = source_dependency.effective_sources(
            sorted({s for s in src_ids if s is not None}))
    elif require_source:
        raise ValueError("no source provenance (source_key absent) — a graduating effective_n call must "
                         "provide source ids so the Art. XI lineage collapse cannot be silently skipped")
    joint = dependency_components(proj, link_keys) if (link_keys and items) else len(items)
    marginal_min = min(by_dim.values()) if by_dim else len(items)
    return {"raw_n": len(items), "by_dim": by_dim, "marginal_min_upper_bound": marginal_min,
            "effective_n": joint,
            "note": "effective_n = JOINT connected-components over all required dims + Art. XI source lineage "
                    "(the conservative count; by_dim are per-dimension marginal UPPER bounds). Graduation "
                    "keys off effective_n, never raw_n or the marginal min."}


def dependency_components(items, link_keys):
    """Conservative union-find: two items are DEPENDENT if they share a non-null value on ANY link_key;
    returns the number of connected components (the most conservative effective_n when a claim must be
    independent along all listed dependencies simultaneously)."""
    parent = list(range(len(items)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    for key in link_keys:
        buckets = {}
        for i, it in enumerate(items):
            v = _val(it, key)
            if v is not None:
                buckets.setdefault((key, v), []).append(i)
        for members in buckets.values():
            for j in members[1:]:
                union(members[0], j)
    return len({find(i) for i in range(len(items))})


def _demo():
    items = [
        {"id": "a", "lexical_family": "F1", "site": "KN", "source_id": "SRC-DAMOS"},
        {"id": "b", "lexical_family": "F1", "site": "KN", "source_id": "SRC-VC-DOCS2"},
        {"id": "c", "lexical_family": "F2", "site": "PY", "source_id": "SRC-DMIC"},
    ]
    import json
    print(json.dumps(effective_n(items, ["lexical_family", "site"]), indent=1))
    print("dependency_components(lexical_family):", dependency_components(items, ["lexical_family"]))


if __name__ == "__main__":
    _demo()
