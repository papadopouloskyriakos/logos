"""E211-RAG index builder — smallest reproducible stack (SQLite FTS5). Five separated
indexes as tables (A_OBS, B_SCHOL, C_COMP, D_CLAIMS, E_ADV) with the frozen chunk schema.
No production-KB mixing; no unlicensed full text (SM2017 = metadata rows only)."""
import csv
import hashlib
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "logos2_rag.sqlite")
MAIN = "/home/claude-runner/gitlab/n8n/logos"
L2 = "/home/claude-runner/gitlab/n8n/logos-logos2"

FIELDS = json.load(open(os.path.join(HERE, "CHUNK_SCHEMA.json")))["fields"]


def h(x):
    return hashlib.sha256(x.encode() if isinstance(x, str) else x).hexdigest()


def mk(conn, table):
    conn.execute(f"CREATE VIRTUAL TABLE IF NOT EXISTS {table} USING fts5("
                 + ",".join(FIELDS) + ")")


def fold(t):
    for u, a in zip("\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089", "0123456789"):
        t = t.replace(u, a)
    return t


def add(conn, table, **kw):
    kw["text"] = fold(str(kw.get("text", "")))
    row = {f: str(kw.get(f, "")) for f in FIELDS}
    row["chunk_id"] = h(table + row["source_id"] + row["locator"] + row["text"])[:24]
    row["content_hash"] = h(row["text"])
    conn.execute(f"INSERT INTO {table} VALUES ({','.join('?' * len(FIELDS))})",
                 [row[f] for f in FIELDS])


def main():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    for t in ("A_OBS", "B_SCHOL", "C_COMP", "D_CLAIMS", "E_ADV"):
        mk(conn, t)

    # ---- Index A: silver transcriptions (one inscription per chunk) ----
    silver = json.load(open(f"{MAIN}/corpus/silver/inscriptions_structured.json"))
    sf = h(open(f"{MAIN}/corpus/silver/inscriptions_structured.json", "rb").read())
    for ins in silver:
        words = [" -".join([]) or "-".join(w) for w in ins.get("words", [])]
        add(conn, "A_OBS", index_class="OBSERVATIONAL_EVIDENCE", source_id="SILVER_LA",
            title=ins["id"], locator=ins["id"], source_file_hash=sf,
            publication_date="pre-2026", availability_ts="2026-07-10",
            licence="in-repo derivative", source_class="observation",
            obs_restoration_inference="observation", language_script="Linear A",
            site=ins.get("site", ""), chronology=ins.get("context", ""),
            doc_type=ins.get("support", ""),
            text=" ".join(words))
    # canonical fraction apparatus
    cf = f"{L2}/research/logos2/experiments/E204R2_residual_canonicalization/CANONICAL_FRACTION_DATASET.csv"
    cfh = h(open(cf, "rb").read())
    for r in csv.DictReader(open(cf)):
        add(conn, "A_OBS", index_class="OBSERVATIONAL_EVIDENCE", source_id="E204R2_CANON",
            title=r["doc_id"], locator=f"{r['doc_id']} {r['locus']}",
            source_file_hash=cfh, availability_ts="2026-07-10",
            licence="campaign-derived", source_class="observation",
            obs_restoration_inference="observation" if r["restored"] == "0" else "restoration",
            language_script="Linear A", doc_type="fraction-record",
            text=f"{r['context_word']} {r['logogram']} {r['integer']} {r['fraction_seq']}")

    # ---- Index B: Younger paragraphs (licence: internal factual use) + SM2017 metadata ----
    for fn in ("lineara-main.txt", "lexicon.txt"):
        p = f"{MAIN}/corpus/bronze/younger_lineara/{fn}"
        raw = open(p, encoding="utf-8", errors="replace").read()
        fh = h(open(p, "rb").read())
        for i, para in enumerate(x for x in raw.split("\n\n") if len(x.split()) > 20):
            add(conn, "B_SCHOL", index_class="PRIMARY_SCHOLARSHIP", source_id="YOUNGER_WEB",
                title=fn, locator=f"{fn}#p{i}", source_file_hash=fh,
                publication_date="2023-08", availability_ts="2026-07-03",
                licence="internal factual use; no redistribution",
                source_class="scholarly_inference",
                obs_restoration_inference="inference", language_script="Linear A",
                text=" ".join(para.split())[:1200])
    for r in csv.DictReader(open(f"{MAIN}/experiments/crossscript_gate/toponym_anchors.csv")):
        add(conn, "B_SCHOL", index_class="PRIMARY_SCHOLARSHIP", source_id="SM2017_META",
            title="Steele-Meissner 2017 toponym equation", locator=r.get("page", ""),
            publication_date="2017", availability_ts="2026-07-01",
            licence="copyright; metadata-only", source_class="scholarly_inference",
            obs_restoration_inference="inference",
            contamination_flag="1",  # published equations = prior art for onomastics
            text=f"toponym equation {r['la_signs']} ~ LB {r['lb_form']} ({r['citation'][:80]})")

    # ---- Index C: comparative corpora (cog entries) ----
    D = f"{MAIN}/corpus/bronze/code/CSA_OptMatcher/data"
    for fn in os.listdir(D):
        if not fn.endswith(".cog"):
            continue
        fh = h(open(f"{D}/{fn}", "rb").read())
        with open(f"{D}/{fn}", encoding="utf-8") as f:
            next(f)
            for i, ln in enumerate(f):
                parts = ln.rstrip("\n").split("\t")
                if len(parts) == 2 and parts[0]:
                    add(conn, "C_COMP", index_class="COMPARATIVE_CORPORA",
                        source_id="COG_CORPORA", title=fn, locator=f"{fn}#{i}",
                        source_file_hash=fh, availability_ts="2026-07-10",
                        licence="research-use", source_class="observation",
                        obs_restoration_inference="observation",
                        language_script=fn.split(".")[0],
                        text=f"{parts[0]} = {parts[1]}")

    # ---- Index D: interpretive claims (claims-only; contamination-flagged) ----
    rj = f"{MAIN}/corpus/bronze/rjabchikov_2025_sceptre"
    if os.path.isdir(rj):
        for fn in os.listdir(rj):
            p = f"{rj}/{fn}"
            if not os.path.isfile(p) or os.path.getsize(p) > 2_000_000:
                continue
            try:
                raw = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for i, para in enumerate(x for x in raw.split("\n\n") if len(x.split()) > 15):
                add(conn, "D_CLAIMS", index_class="INTERPRETIVE_CLAIMS_NOT_EVIDENCE",
                    source_id="RJAB2025", title=fn, locator=f"{fn}#p{i}",
                    publication_date="2025", availability_ts="2026-07-03",
                    licence="claims-only indexing", source_class="interpretive_claim",
                    obs_restoration_inference="inference", contamination_flag="1",
                    text="INTERPRETIVE_CLAIM_ONLY " + " ".join(para.split())[:1000])

    # ---- Index E: adversarial/null (seeded synthetic entries) ----
    import numpy as np
    rng = np.random.default_rng(1336530913)
    silver_signs = sorted({s for ins in silver for w in ins.get("words", []) for s in w})
    for i in range(300):
        L = int(rng.integers(2, 6))
        fake = "-".join(rng.choice(silver_signs, L))
        add(conn, "E_ADV", index_class="ADVERSARIAL_AND_NULL", source_id="E206_CANARIES",
            title=f"fabricated-{i}", locator=f"fab#{i}", availability_ts="2026-07-10",
            licence="campaign-derived", source_class="adversarial",
            obs_restoration_inference="adversarial", contamination_flag="0",
            text=f"fabricated candidate {fake}")

    conn.commit()
    counts = {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
              for t in ("A_OBS", "B_SCHOL", "C_COMP", "D_CLAIMS", "E_ADV")}
    conn.close()
    manifest = {"db": "logos2_rag.sqlite", "db_sha256": h(open(DB, "rb").read()),
                "counts": counts, "built": "2026-07-10",
                "stack": "SQLite FTS5 (BM25); dense arm optional via Ollama gpu01"}
    json.dump(manifest, open(os.path.join(HERE, "INDEX_MANIFEST.json"), "w"), indent=1)
    with open(os.path.join(HERE, "INDEX_MANIFEST.sha256"), "w") as f:
        f.write(manifest["db_sha256"] + "  logos2_rag.sqlite\n")
    print("indexes built:", counts)


if __name__ == "__main__":
    main()
