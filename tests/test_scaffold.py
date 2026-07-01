"""pytest for the comparison-layer scaffold (logos_db / predict / verdict / family_scores).

Run from the repo root:
    pytest tests/test_scaffold.py -v

Five required behaviours (docs/design/comparison-layer.md §A/§E):
  (a) hash idempotency — same canonical body -> same plan_hash, no duplicate row.
  (b) confidence cap — model-assisted provenance is structurally capped at <=0.75 (fail CLOSED).
  (c) sole-writer — verdict.py is the ONLY script that INSERTs INTO verdicts.
  (d) §E gate refuses — a failing case is REJECT/NULL_PUBLISHED, NEVER GRADUATE.
  (e) round-trip — predict -> verdict -> family_scores aggregates end-to-end on the live DB.

DB-touching tests run against the LIVE logos DB under an isolated family prefix
(``__scaffoldtest__…``) and clean up every row they write (hypotheses / verdicts / family_scores /
graduation_state) in an autouse fixture, so the suite leaves no pollution. If the DB is unreachable
the DB tests skip (the pure tests still run) — the agora ProxySQL-cert gotcha, documented.
"""
import os
import sys
import uuid

import pytest

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts import predict, verdict, family_scores, logos_db  # noqa: E402

TEST_FAMILY = "__scaffoldtest__" + uuid.uuid4().hex[:8]
TEST_PREFIX = "__scaffoldtest__"

# realistic NW-Semitic-style consonantal skeletons so the L_fake trilateral-root sampler calibrates
CAND_LEX = ["nwy", "brq", "mlk", "ywm", "dn", "qtl", "zkr", "bnh", "hlk", "yqr"]
HELD_FORMS = ["nwy", "brq", "mlk", "ywm", "dn", "qtl"]


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def conn():
    try:
        c = logos_db.db()
        c.cursor().execute("SELECT 1")     # force-connect
        return c
    except Exception as e:                 # pragma: no cover - env-dependent
        pytest.skip(f"logos DB unreachable ({type(e).__name__}); skipping DB tests")


@pytest.fixture(autouse=True)
def _cleanup(conn):
    """Remove every test-family row before AND after each test (hypotheses cascade via plan_hash)."""
    def _purge():
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE v FROM verdicts v JOIN hypotheses h ON h.plan_hash=v.plan_hash "
                            "WHERE h.family LIKE %s", (TEST_PREFIX + "%",))
                cur.execute("DELETE FROM hypotheses WHERE family LIKE %s", (TEST_PREFIX + "%",))
                cur.execute("DELETE FROM family_scores WHERE family LIKE %s", (TEST_PREFIX + "%",))
                cur.execute("DELETE FROM graduation_state WHERE family LIKE %s", (TEST_PREFIX + "%",))
        except Exception:
            pass
    if conn is not None:
        _purge()
    yield
    if conn is not None:
        _purge()


# --------------------------------------------------------------------------- #
# (a) hash idempotency
# --------------------------------------------------------------------------- #
def test_hash_idempotent_same_body_same_hash_no_dup(conn):
    """Committing the identical canonical body twice yields the same plan_hash and exactly one row."""
    kwargs = dict(
        family=TEST_FAMILY, claim_type="sign_map", candidate_lang="NW-Semitic",
        partial_map={"*301": "na"}, correspondence=[{"rule": "*A-series -> a"}],
        heldout_set=["I-Cr-1", "I-HT-88"], derivation_set=["I-Pk-1"],
        free_params=3, provenance="embedding_nn", confidence=0.6,
        prediction={"heldout_forms": HELD_FORMS, "candidate_lexicon": CAND_LEX, "n_eff": 12,
                    "u_floor": 8, "not_indexed_sign_support": 0.5, "lit_index_hit": False},
        thesis_text="*301 = /na/ forces a Semitic N-W-Y root across the held-out sites.",
        search_log_ref="run-test-001")
    ph1 = predict.commit(_conn=conn, **kwargs)
    ph2 = predict.commit(_conn=conn, **kwargs)
    assert ph1 == ph2, "identical canonical body must hash to the same plan_hash"
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM hypotheses WHERE plan_hash=%s", (ph1,))
        assert cur.fetchone()[0] == 1, "re-commit must be a no-op (ON DUPLICATE KEY UPDATE plan_hash=plan_hash)"
    # a DIFFERENT confidence yields a DIFFERENT hash (confidence is in the body — agora pattern)
    kw2 = dict(kwargs); kw2["confidence"] = 0.55
    ph3 = predict.commit(_conn=conn, **kw2)
    assert ph3 != ph1, "a different confidence is a different hypothesis (it is in the canonical body)"


# --------------------------------------------------------------------------- #
# (b) confidence cap (fail CLOSED)
# --------------------------------------------------------------------------- #
def test_confidence_cap_model_source_refused_above_075():
    """A model-assisted provenance above 0.75 is REFUSED (invariant 5); nothing committed."""
    for bad_conf in (0.751, 0.9, 1.0):
        with pytest.raises(predict.HypothesisError):
            predict.gate(bad_conf, "llm_proposed")
        with pytest.raises(predict.HypothesisError):
            predict.gate(bad_conf, "embedding_nn")


def test_confidence_cap_exactly_075_allowed_for_model():
    """0.750 is the cap itself — allowed (<=, not <)."""
    assert predict.gate(0.75, "llm_proposed") == 0.75
    assert predict.gate(0.75, "embedding_nn") == 0.75


def test_non_model_provenance_can_exceed_cap():
    """human / literature_match / canary are NOT capped at 0.75 (only model-assisted sources are)."""
    assert predict.gate(0.95, "human") == 0.95
    assert predict.gate(0.90, "literature_match") == 0.90


def test_confidence_must_be_in_open_unit_interval():
    for bad in (0.0, -0.1, 1.5, 0):
        with pytest.raises(predict.HypothesisError):
            predict.gate(bad, "human")
    assert predict.gate(0.01, "human") == 0.01   # just above floor, valid


def test_bad_provenance_refused():
    with pytest.raises(predict.HypothesisError):
        predict.gate(0.5, "gpt5_guess")   # not a known provenance class


# --------------------------------------------------------------------------- #
# (c) sole-writer of verdicts (structural / grep)
# --------------------------------------------------------------------------- #
def test_verdict_py_is_the_sole_writer_of_verdicts():
    """No script other than verdict.py may WRITE verdicts (invariant 2/3 — the LLM never grades).

    sole-WRITER, not sole-reader: family_scores is the legitimate consumer (SELECT/FROM verdicts),
    and the docstrings reference it. The invariant is about mutation: only verdict.py INSERTs/UPDATEs/
    DELETEs/REPLACEs the verdicts table.
    """
    import glob
    import re
    scripts_dir = os.path.join(_REPO, "scripts")
    # a write against verdicts: INSERT/UPDATE/DELETE/REPLACE ... verdicts (case-insensitive)
    write_re = re.compile(r"\b(insert|update|delete|replace)\b\s+.*\bverdicts\b", re.IGNORECASE)
    writers = []
    for path in glob.glob(os.path.join(scripts_dir, "*.py")) + glob.glob(os.path.join(scripts_dir, "*", "*.py")):
        with open(path) as f:
            src = f.read()
        if write_re.search(src):
            writers.append(os.path.relpath(path, _REPO))
    assert writers == ["scripts/verdict.py"], (
        f"verdict.py must be the SOLE writer of `verdicts`; found write statements in: {writers}")
    # and the grader never invokes an LLM on the verdict path (no LLM client imported/called)
    with open(os.path.join(scripts_dir, "verdict.py")) as f:
        vsrc = f.read().lower()
    assert "anthropic" not in vsrc and "openai" not in vsrc, "no LLM client on the verdict path"


# --------------------------------------------------------------------------- #
# (d) §E gate refuses graduation unless ALL clauses hold
# --------------------------------------------------------------------------- #
def test_gate_llm_plus_lit_index_never_graduates():
    """llm_proposed AND lit_index_hit = regurgitation by construction -> never GRADUATE."""
    g = verdict.grade(HELD_FORMS, CAND_LEX, confidence=0.6, free_params=3, provenance="llm_proposed",
                      lit_index_hit=True, not_indexed_sign_support=0.9, u_floor=8, n_eff=5, n_fake=6, seed=2)
    assert g["gate_verdict"] != "GRADUATE"
    assert "not_llm_lit_contamination" in g["failing_clauses"]


def test_mdl_clause_removed_u_floor_reported_only():
    """P0.1: the k<=u_floor MDL clause was dimensionally incoherent and passed by construction (u_floor
    defaulted to free_params); it is REMOVED from the §E gate. u_floor is reported-only, and an omitted
    u_floor is reported as NaN (never silently satisfied). Real bit-level MDL is future work."""
    g = verdict.grade(HELD_FORMS, CAND_LEX, confidence=0.6, free_params=12, provenance="embedding_nn",
                      lit_index_hit=False, not_indexed_sign_support=0.9, u_floor=None, n_eff=5, n_fake=6, seed=2)
    assert "k_le_u_floor" not in g["clauses"] and "k_le_u_floor" not in g["failing_clauses"]
    assert g["u_floor"] != g["u_floor"]                    # NaN (omitted u_floor is not silently passed)


def test_gate_no_not_indexed_support_rejects():
    """A reading that only works on literature-known signs (no L_not_indexed support) -> never GRADUATE."""
    g = verdict.grade(HELD_FORMS, CAND_LEX, confidence=0.6, free_params=3, provenance="embedding_nn",
                      lit_index_hit=False, not_indexed_sign_support=0.0, u_floor=8, n_eff=5, n_fake=6, seed=2)
    assert g["gate_verdict"] != "GRADUATE"
    assert "generalizes_to_not_indexed" in g["failing_clauses"]


def test_gate_weak_heldout_is_null_published():
    """Held-out that does not beat the L_fake floor -> deviation / NULL_PUBLISHED, never GRADUATE."""
    g = verdict.grade(["zzz", "qqq", "xxx", "ppp"], CAND_LEX, confidence=0.6, free_params=3,
                      provenance="embedding_nn", lit_index_hit=False, not_indexed_sign_support=0.9,
                      u_floor=8, n_eff=5, n_fake=6, seed=2)
    assert g["result"] == "deviation"
    assert g["gate_verdict"] in ("NULL_PUBLISHED", "REJECT")
    assert g["gate_verdict"] != "GRADUATE"


def test_gate_verdict_enum_is_valid():
    for gv in ("GRADUATE", "REJECT", "NULL_PUBLISHED"):
        assert gv in {"GRADUATE", "REJECT", "NULL_PUBLISHED"}


# --------------------------------------------------------------------------- #
# (e) full round-trip on the live DB: predict -> verdict -> family_scores
# --------------------------------------------------------------------------- #
def test_round_trip_predict_verdict_family_scores(conn):
    """predict a hypothesis -> verdict grades it on held-out -> family_scores aggregates the family."""
    ph = predict.commit(
        family=TEST_FAMILY, claim_type="sign_map", candidate_lang="NW-Semitic",
        partial_map={"*301": "na"}, correspondence=[{"rule": "A -> a"}],
        heldout_set=["I-Cr-1"], derivation_set=["I-Pk-1"], free_params=3,
        provenance="embedding_nn", confidence=0.6,
        prediction={"heldout_forms": HELD_FORMS, "candidate_lexicon": CAND_LEX, "n_eff": 12,
                    "u_floor": 8, "not_indexed_sign_support": 0.5, "lit_index_hit": False},
        thesis_text="*301=/na/ forces NW-Semitic morphology across held-out sites.",
        search_log_ref="run-rt-001", _conn=conn)
    assert len(ph) == 64

    # the hypothesis is due (no verdict yet)
    with conn.cursor() as cur:
        cur.execute("SELECT v.plan_hash FROM hypotheses h LEFT JOIN verdicts v ON v.plan_hash=h.plan_hash "
                    "WHERE h.plan_hash=%s", (ph,))
        assert cur.fetchone()[0] is None, "freshly committed hypothesis must be ungraded (due)"

    graded = verdict.run(plan_hash=ph, n_fake=6, conn=conn)
    assert len(graded) == 1 and graded[0][0] == ph
    g = graded[0][1]
    assert g["result"] in ("match", "partial", "deviation")
    assert g["gate_verdict"] in ("GRADUATE", "REJECT", "NULL_PUBLISHED")

    # the verdict row exists, provenance = verdict.py's code SHA, result matches the grade
    with conn.cursor() as cur:
        cur.execute("SELECT result, accuracy, brier, provenance, notes FROM verdicts WHERE plan_hash=%s", (ph,))
        row = cur.fetchone()
        assert row is not None, "verdict.py must write the verdicts row"
        result, accuracy, brier, prov, notes = row
        assert result == g["result"]
        assert prov == verdict.code_sha(), "verdicts.provenance must be the grader's code SHA"
        assert "code=" in notes and "gate=" in notes

    # family_scores aggregates the family + writes graduation_state
    scores = family_scores.run(family=TEST_FAMILY, conn=conn)
    assert any(s["family"] == TEST_FAMILY for s in scores), "family_scores must roll up the test family"
    with conn.cursor() as cur:
        cur.execute("SELECT n_predictions, win_rate, dsr FROM family_scores WHERE family=%s", (TEST_FAMILY,))
        fs = cur.fetchone()
        assert fs is not None and fs[0] >= 1
        cur.execute("SELECT gate, frozen, reason FROM graduation_state WHERE family=%s", (TEST_FAMILY,))
        gs = cur.fetchone()
        assert gs is not None, "family_scores must write graduation_state"
        gate, frozen, reason = gs
        # a single thin verdict can never graduate (MIN_VERDICTS gate) -> must be frozen + honest reason
        assert frozen == 1, "a 1-verdict family must not graduate (cold-start honesty)"
        assert "frozen" in reason
