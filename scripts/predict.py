#!/usr/bin/env python3
"""logos predict — commit a comparison-layer hypothesis to the ledger (the fail-CLOSED gate's currency).

Mirrors `../finops-agora/scripts/predict.py` (canonical body -> plan_hash = sha256, idempotent
ON DUPLICATE KEY INSERT) but encodes the comparison-hypothesis schema of
docs/design/comparison-layer.md §A:

  canonical body (the hashed content) =
    { family, claim_type, candidate_lang, partial_map, correspondence,
      derivation_set, heldout_set, free_params, provenance, anchor_lexeme,
      confidence, thesis_sha, search_log_ref }

  plan_hash = sha256(json.dumps(body, sort_keys=True))
    * created_at is OUT of the hash (idempotent same-content re-commits — the agora pattern).
    * thesis is IN as `thesis_sha` (sha256 of the free-text thesis) so the claim's reasoning is
      bound to the identity without storing prose in the key.

A hypothesis is a PROPOSER SIGNAL, never evidence (design §0). model-assisted provenances
(`embedding_nn`, `llm_proposed`) are structurally capped at confidence <= 0.75 (invariant 5) so
they can never *decide* a graduation. The fail-CLOSED gate refuses to commit anything outside
(0,1] or above the model cap — no silent clamp (the LLM proposes; the gate disposes).

This script WRITES A HYPOTHESIS AND NOTHING ELSE. The held-out verdict is scripts/verdict.py.
Idempotent: committing the identical body twice returns the same plan_hash and no-ops.

CLI:
  predict.py --family semitic --claim-type sign_map --candidate-lang NW-Semitic \\
             --partial-map '{"*301":"na"}' --correspondence '[]' \\
             --derivation-set '[]' --heldout-set '["I-1","I-2"]' --free-params 3 \\
             --provenance llm_proposed --confidence 0.55 --thesis-file thesis.md \\
             --search-log-ref run-001
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts import logos_db  # noqa: E402

# provenance classes (design §A / §C.5). MODEL_SOURCES are structurally capped at 0.75.
PROVENANCES = ("embedding_nn", "llm_proposed", "literature_match", "human", "canary")
MODEL_SOURCES = frozenset({"embedding_nn", "llm_proposed"})
CLAIM_TYPES = ("sign_map", "lexeme", "grammar", "reading")
CONF_CAP_MODEL = 0.75   # invariant 5 — a model-assisted claim can never clear the action cutoff
CONF_FLOOR = 0.0        # confidence must be in (0, 1]


class HypothesisError(ValueError):
    """Raised when a hypothesis violates a fail-CLOSED gate (no row committed)."""


def _sha(text):
    return hashlib.sha256((text or "").encode()).hexdigest()


def canonical_body(family, claim_type, partial_map, correspondence, heldout_set,
                   derivation_set, free_params, provenance, confidence, thesis_sha,
                   search_log_ref, candidate_lang="", anchor_lexeme=None):
    """Build the canonical, hash-stable body (dict). Field order is irrelevant — sort_keys at hash."""
    body = {
        "family": family,
        "claim_type": claim_type,
        "candidate_lang": candidate_lang,
        "partial_map": dict(partial_map or {}),
        "correspondence": list(correspondence or []),
        "derivation_set": list(derivation_set or []),
        "heldout_set": list(heldout_set or []),
        "free_params": int(free_params),
        "provenance": provenance,
        "anchor_lexeme": dict(anchor_lexeme or {}),
        "confidence": round(float(confidence), 3),   # IN the hash (agora pattern)
        "thesis_sha": thesis_sha,                    # thesis IN as thesis_sha
        "search_log_ref": search_log_ref or "",
    }
    return body


def plan_hash_for(body):
    """sha256 of the canonical JSON (sort_keys, created_at OUT). Deterministic across replays."""
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def gate(confidence, provenance):
    """The fail-CLOSED hypothesis gate. Returns the (possibly cleaned) confidence or raises.

    (1) confidence must be a real number in (0, 1].
    (2) model-assisted provenance (embedding_nn / llm_proposed) is capped at 0.75 — REFUSED above
        the cap, never silently clamped (the LLM proposes; the gate disposes; the operator sees the
        rejection). This is invariant 5 made mechanical.
    """
    try:
        c = float(confidence)
    except (TypeError, ValueError):
        raise HypothesisError(f"confidence must be numeric in (0,1]; got {confidence!r}")
    if not (CONF_FLOOR < c <= 1.0):
        raise HypothesisError(f"confidence must be in (0,1]; got {c}")
    if provenance not in PROVENANCES:
        raise HypothesisError(f"provenance must be one of {PROVENANCES}; got {provenance!r}")
    if provenance in MODEL_SOURCES and c > CONF_CAP_MODEL:
        raise HypothesisError(
            f"model-assisted provenance '{provenance}' is structurally capped at "
            f"{CONF_CAP_MODEL} (invariant 5); got {c}. Lower the confidence or change provenance.")
    return round(c, 3)


def commit(family, claim_type, partial_map, correspondence, heldout_set, derivation_set,
           free_params, provenance, confidence, prediction=None, thesis_text=None,
           search_log_ref="", candidate_lang="", anchor_lexeme=None, as_of=None, _conn=None):
    """Commit a hypothesis. Returns plan_hash. Idempotent: same canonical body -> same row, no dup.

    `prediction` is the falsifiable held-out implication (the concrete evaluation set registered
    BEFORE the verdict — held-out forms, the candidate lexicon, instrumented N_eff, lit_index_hit,
    not_indexed_sign_support, u_floor). Stored in the `prediction` JSON column; not in the plan_hash
    (the hash commits the structural claim — partial_map/correspondence/heldout_set IDS — per §A).
    """
    conf = gate(confidence, provenance)   # fail CLOSED — raises, commits nothing on violation
    thesis_sha = _sha(thesis_text or "")
    body = canonical_body(
        family, claim_type, partial_map, correspondence, heldout_set, derivation_set,
        free_params, provenance, conf, thesis_sha, search_log_ref, candidate_lang, anchor_lexeme)
    ph = plan_hash_for(body)
    now = datetime.datetime.now()
    pred_json = json.dumps(prediction or {}, sort_keys=True)

    owns_conn = _conn is None
    conn = _conn or logos_db.db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO hypotheses (plan_hash, family, claim_type, body, prediction,
                                           confidence, as_of, created_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE plan_hash=plan_hash""",   # re-commit no-ops (first-freeze)
                (ph, family, claim_type, json.dumps(body, sort_keys=True), pred_json,
                 conf, as_of or now.date(), now))
    finally:
        if owns_conn:
            conn.close()
    return ph


def _parse_json(s, default):
    if s is None or s == "":
        return default
    return json.loads(s)


def main():
    ap = argparse.ArgumentParser(description="commit a comparison-layer hypothesis (fail-CLOSED)")
    ap.add_argument("--family", required=True)
    ap.add_argument("--claim-type", choices=CLAIM_TYPES, required=True)
    ap.add_argument("--candidate-lang", default="")
    ap.add_argument("--partial-map", default="{}", help="JSON {sign: value}")
    ap.add_argument("--correspondence", default="[]", help="JSON list of sound-law rules")
    ap.add_argument("--derivation-set", default="[]", help="JSON list of inscription ids (derivation)")
    ap.add_argument("--heldout-set", default="[]", help="JSON list of inscription ids (held-out)")
    ap.add_argument("--free-params", type=int, required=True, help="k: asserted values + rules")
    ap.add_argument("--provenance", choices=PROVENANCES, required=True)
    ap.add_argument("--confidence", type=float, required=True)
    ap.add_argument("--thesis-file", help="free-text thesis (hashed into thesis_sha, NOT stored)")
    ap.add_argument("--search-log-ref", default="")
    ap.add_argument("--anchor-lexeme", default="{}", help='JSON {form,root,gloss}')
    a = ap.parse_args()

    thesis_text = None
    if a.thesis_file:
        with open(a.thesis_file) as f:
            thesis_text = f.read()

    ph = commit(
        family=a.family, claim_type=a.claim_type, candidate_lang=a.candidate_lang,
        partial_map=_parse_json(a.partial_map, {}), correspondence=_parse_json(a.correspondence, []),
        heldout_set=_parse_json(a.heldout_set, []), derivation_set=_parse_json(a.derivation_set, []),
        free_params=a.free_params, provenance=a.provenance, confidence=a.confidence,
        prediction={}, thesis_text=thesis_text, search_log_ref=a.search_log_ref,
        anchor_lexeme=_parse_json(a.anchor_lexeme, {}))
    print(f"committed hypothesis {ph}")


if __name__ == "__main__":
    main()
