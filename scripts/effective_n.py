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


def effective_n(items, dims, source_key="source_id"):
    """Report raw_n + per-dimension independent-unit counts + the bottleneck effective_n.

    `dims` are the grouping dimensions the claim must be independent along (e.g. ['lexical_family',
    'site', 'document_id']). effective_n = the MINIMUM distinct count across those dims — the tightest
    independence constraint. If items carry `source_key`, the Art. XI source-lineage count is folded in as
    another dimension (dependent editions/lexica collapse to one lineage)."""
    dims = list(dims)
    by_dim = {d: distinct_units(items, d) for d in dims}
    # Art. XI: collapse cited sources to independent lineages
    src_ids = [s for s in (_val(it, source_key) for it in items) if s is not None]
    if src_ids:
        try:
            from scripts import source_dependency
            by_dim["source_lineage"] = source_dependency.effective_sources(sorted(set(src_ids)))
        except Exception as e:                                  # unknown source fails loud upstream
            raise
    if not by_dim:
        return {"raw_n": len(items), "by_dim": {}, "effective_n": len(items),
                "bottleneck_dim": None, "note": "no dimensions given — effective_n defaults to raw_n"}
    bottleneck_dim = min(by_dim, key=by_dim.get)
    return {"raw_n": len(items), "by_dim": by_dim, "effective_n": by_dim[bottleneck_dim],
            "bottleneck_dim": bottleneck_dim,
            "note": "effective_n = min independent-unit count across the claim's required-independence dims (Art. VIII); graduation keys off this, never raw_n."}


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
