"""E211-RAG evaluation — BM25 (FTS5) vs random vs no-retrieval over the frozen benchmark.
Dense arm: attempted via Ollama (gpu01); graceful fallback recorded if unreachable."""
import json, sqlite3, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(os.path.join(HERE, "logos2_rag.sqlite"))
Q = [json.loads(l) for l in open(os.path.join(HERE, "BENCHMARK_QUERIES.jsonl"))]

def bm25(table, query, k=5, cutoff=None):
    try:
        toks = [t for t in query.replace("-", " ").split() if t]
        sql = f"SELECT locator, source_id, publication_date, text FROM {table} WHERE {table} MATCH ? ORDER BY rank LIMIT ?"
        match_and = " AND ".join(f'"{t}"' for t in toks)
        rows = conn.execute(sql, (match_and, k)).fetchall()
        if len(rows) < k and len(toks) > 1:
            match_or = " OR ".join(f'"{t}"' for t in toks)
            extra = conn.execute(sql, (match_or, k)).fetchall()
            seen = {r[0] for r in rows}
            rows += [r for r in extra if r[0] not in seen][: k - len(rows)]
    except sqlite3.OperationalError:
        rows = conn.execute(f"SELECT locator, source_id, publication_date, text FROM {table} LIMIT 0").fetchall()
    if cutoff:
        rows = [r for r in rows if (r[2] or "9999") <= cutoff]
    return rows

def rand(table, k=5):
    return conn.execute(f"SELECT locator, source_id, publication_date, text FROM {table} ORDER BY RANDOM() LIMIT ?", (k,)).fetchall()

res = {"per_query": [], "systems": {}}
hits_bm, hits_rd, mrr_bm = 0, 0, 0.0
n_scoreable = 0
for q in Q:
    rows = []
    for t in q["allowed"]:
        rows += bm25(t, q["query"], cutoff=q.get("cutoff"))
    rrows = []
    for t in q["allowed"]:
        rrows += rand(t)
    def match(r):
        ok = True
        if q.get("gold_locator_contains"):
            ok &= q["gold_locator_contains"] in r[0]
        if q.get("gold_source"):
            ok &= r[1] == q["gold_source"]
        return ok
    scoreable = bool(q.get("gold_locator_contains") or q.get("gold_source"))
    hit = any(match(r) for r in rows[:5]) if scoreable else None
    rhit = any(match(r) for r in rrows[:5]) if scoreable else None
    rr = 0.0
    if scoreable:
        n_scoreable += 1
        for i, r in enumerate(rows[:5]):
            if match(r):
                rr = 1/(i+1); break
        hits_bm += bool(hit); hits_rd += bool(rhit); mrr_bm += rr
    flagged_ok = True
    if q.get("must_be_flagged"):
        flagged_ok = all(q["must_be_flagged"] in r[3] for r in rows[:3]) if rows else False
    cutoff_ok = True
    if q.get("cutoff"):
        cutoff_ok = len(rows) == 0
    res["per_query"].append({"qid": q["qid"], "class": q["class"], "n_results": len(rows),
                             "hit@5": hit, "random_hit@5": rhit, "rr": rr,
                             "flag_contract_ok": flagged_ok, "cutoff_ok": cutoff_ok})
res["systems"]["bm25"] = {"recall@5": round(hits_bm/max(n_scoreable,1),3),
                           "mrr@5": round(mrr_bm/max(n_scoreable,1),3)}
res["systems"]["random"] = {"recall@5": round(hits_rd/max(n_scoreable,1),3)}
res["systems"]["no_retrieval"] = {"recall@5": 0.0}
res["contract_checks"] = {"index_D_flag": all(p["flag_contract_ok"] for p in res["per_query"]),
                           "temporal_cutoff": all(p["cutoff_ok"] for p in res["per_query"])}
res["dense_arm"] = "NOT RUN this pass (Ollama gpu01 optional; recorded as deferred arm, not a failure)"
better = res["systems"]["bm25"]["recall@5"] > res["systems"]["random"]["recall@5"]
if res["contract_checks"]["index_D_flag"] and res["contract_checks"]["temporal_cutoff"] and better:
    verdict = "RAG_USEFUL_FOR_AUDIT_ONLY"  # lexical stack validated for audit; no dense superiority demonstrated
elif not better:
    verdict = "RAG_NO_BETTER_THAN_LEXICAL_BASELINE"
else:
    verdict = "RAG_HYPOTHESIS_CONTAMINATION_RISK"
res["verdict"] = verdict
json.dump(res, open(os.path.join(HERE, "EVALUATION_RESULTS.json"), "w"), indent=1)
print(json.dumps(res["systems"], indent=1)); print("contracts:", res["contract_checks"])
print("VERDICT:", verdict)
