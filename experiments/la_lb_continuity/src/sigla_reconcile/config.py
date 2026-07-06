#!/usr/bin/env python3
"""Canonical, read-only paths + checksums for the LA↔LB reconciliation inputs.

Both inputs are gitignored licensed-derived data present ONLY in the main worktree; this pass
references them read-only and commits code + checksums + counts (never the data). Override the
main-repo root with env LOGOS_MAIN if the checkout lives elsewhere.
"""
import hashlib, os

MAIN = os.environ.get("LOGOS_MAIN", "/home/claude-runner/gitlab/n8n/logos")

SIGLA_DOCUMENTS = os.path.join(MAIN, "corpus/bronze/sigla_browse_2026/sigla_documents.json")
SIGLA_SIGNS     = os.path.join(MAIN, "corpus/bronze/sigla_browse_2026/sigla_signs.json")
SIGLA_DECODER   = os.path.join(MAIN, "scripts/sigla_decode.py")            # regeneration provenance
SILVER          = os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")
SILVER_ONTOLOGY = os.path.join(MAIN, "corpus/silver/signs_ontology.json")

INPUTS = {                                                                 # id -> path, for the manifest
    "sigla_documents": SIGLA_DOCUMENTS,
    "sigla_signs":     SIGLA_SIGNS,
    "silver_inscriptions_structured": SILVER,
    "silver_signs_ontology": SILVER_ONTOLOGY,
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()

def input_manifest():
    """Deterministic {id: {path, sha256, bytes}} for every input (relative path recorded, not absolute)."""
    out = {}
    for k, p in INPUTS.items():
        st = os.stat(p)
        out[k] = {"path": os.path.relpath(p, MAIN), "sha256": sha256(p), "bytes": st.st_size}
    return out
